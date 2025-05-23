from flask import Flask, render_template, request, redirect, url_for, session, flash, make_response
import os
import secrets
from PIL import Image
from landingai.predict import Predictor
from landingai.visualize import overlay_predictions
import io
import base64
import contextlib
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.orm import Session
from database import Doctor, Patient, XRay, XRayResult, init_db, get_db, engine
import datetime
# Flask-Mail importları kaldırıldı
# from flask_mail import Mail, Message
import uuid
from dotenv import load_dotenv
from functools import wraps

# Google API İstemci Kütüphaneleri
import google.oauth2.credentials
import google.auth.transport.requests
import googleapiclient.discovery
from email.message import EmailMessage # E-posta oluşturmak için

load_dotenv()

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)
app.config['UPLOAD_FOLDER'] = 'uploads'

# Mail ayarları kaldırıldı
# app.config['MAIL_SERVER'] = os.getenv('MAIL_SERVER', 'smtp.gmail.com')
# app.config['MAIL_PORT'] = int(os.getenv('MAIL_PORT', 587))
# app.config['MAIL_USE_TLS'] = True
# app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')
# app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')
# app.config['MAIL_DEFAULT_SENDER'] = os.getenv('MAIL_DEFAULT_SENDER', app.config['MAIL_USERNAME'])

# mail = Mail(app) # Mail nesnesi kaldırıldı

# Şifre sıfırlama jetonlarını saklamak için sözlük (Bu hala bellekte, ideal değil ama şimdilik kalabilir)
password_reset_tokens = {}

# Ensure the upload folder exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(os.path.join(app.config['UPLOAD_FOLDER'], 'original'), exist_ok=True)
os.makedirs(os.path.join(app.config['UPLOAD_FOLDER'], 'results'), exist_ok=True)

# API Anahtarı ve Endpoint ID
ENDPOINT_ID = "c4e981db-70c4-4178-b04b-d967dccdfb96"
API_KEY = "land_sk_1q3qjHgulUP75mihloCvRaDUuj8GFe7R6BaqRVO2ph4Fd8ICc2"

# Veritabanını başlat
init_db()

# Yardımcı fonksiyon: veritabanı bağlantısını elde et
@contextlib.contextmanager
def get_db_session():
    with contextlib.closing(Session(engine)) as session:
        yield session

# Gmail API Servisini Almak İçin Yardımcı Fonksiyon
def get_gmail_service():
    """OAuth 2.0 kimlik bilgilerini kullanarak Gmail API servisini oluşturur ve döndürür."""
    creds = None
    client_id = os.getenv('GOOGLE_CLIENT_ID')
    client_secret = os.getenv('GOOGLE_CLIENT_SECRET')
    refresh_token = os.getenv('GOOGLE_REFRESH_TOKEN')
    token_uri = 'https://oauth2.googleapis.com/token' # Google token endpoint

    # Ekstra loglama:
    app.logger.info("get_gmail_service fonksiyonu çağrıldı.")
    app.logger.info(f"  Client ID .env'den yüklendi mi? {client_id is not None}")
    app.logger.info(f"  Client Secret .env'den yüklendi mi? {client_secret is not None}")
    app.logger.info(f"  Refresh Token .env'den yüklendi mi? {refresh_token is not None}")
    if refresh_token:
        app.logger.info(f"  Yüklenen Refresh Token başlangıcı: {refresh_token[:10]}...")
    # --- Bitiş: Ekstra loglama

    if not all([client_id, client_secret, refresh_token]):
        app.logger.error("Google OAuth kimlik bilgileri .env dosyasında eksik.")
        return None

    try:
        creds = google.oauth2.credentials.Credentials(
            None, # Access token başlangıçta yok
            refresh_token=refresh_token,
            token_uri=token_uri,
            client_id=client_id,
            client_secret=client_secret,
            scopes=['https://www.googleapis.com/auth/gmail.send'] # Kapsamı belirt
        )
        app.logger.info("Credentials nesnesi başarıyla oluşturuldu.") # Log eklendi

        # Ekstra loglama:
        app.logger.info(f"  Credentials nesnesi geçerli mi (valid)? {creds.valid}")
        app.logger.info(f"  Credentials nesnesinin süresi dolmuş mu (expired)? {creds.expired}")
        app.logger.info(f"  Credentials nesnesinde refresh_token var mı? {creds.refresh_token is not None}")
        # --- Bitiş: Ekstra loglama

        # Token'ın geçerli olup olmadığını kontrol et, gerekirse yenile
        if not creds.valid:
            app.logger.warning("Credentials nesnesi geçerli değil (not valid). Yenileme deneniyor...") # Log eklendi
            if creds.refresh_token: # Yeni koşul: Geçerli değilse ve refresh token varsa yenilemeyi dene.
                try:
                    # Token'ı yenilemek için istek gönder
                    request = google.auth.transport.requests.Request()
                    creds.refresh(request)
                    app.logger.info("Google OAuth token başarıyla yenilendi.")
                except Exception as e:
                    app.logger.error(f"Google OAuth token yenilenirken hata: {str(e)}")
                    return None # Yenileme başarısız olursa None dön
            else:
                # Geçerli refresh token yoksa veya başka bir sorun varsa
                app.logger.error("Geçerli Google OAuth refresh token bulunamadı veya token geçersiz.")
                # Ekstra loglama:
                if not creds.refresh_token:
                    app.logger.error("  Detay: Credentials nesnesi içindeki refresh_token None.")
                elif not creds.expired:
                     app.logger.error("  Detay: Credentials nesnesi geçerli değil (valid=False) AMA süresi dolmamış (expired=False).")
                # --- Bitiş: Ekstra loglama
                return None

        # Gmail API servisini oluştur
        app.logger.info("Gmail API servisi oluşturuluyor...") # Log eklendi
        service = googleapiclient.discovery.build('gmail', 'v1', credentials=creds)
        app.logger.info("Gmail API servisi başarıyla oluşturuldu.") # Log eklendi
        return service

    except Exception as e:
        app.logger.error(f"Gmail servisi oluşturulurken hata: {str(e)}")
        return None

# Login Required Decorator
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'doctor_id' not in session:
            flash('Bu sayfayı görüntülemek için giriş yapmanız gerekmektedir.', 'warning')
            return redirect(url_for('index')) # Redirect to login page (index)
        response = make_response(f(*args, **kwargs))
        # Add headers to prevent caching - ensure no-store is present
        response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '0'
        return response
    return decorated_function

@app.route('/')
def index():
    # If user is already logged in, redirect to patient_form - REMOVING THIS CHECK
    # if 'doctor_id' in session:
    #     return redirect(url_for('patient_form'))
    return render_template('index.html') # Restore template rendering
    # return "Ana Sayfa Testi Başarılı!" # Remove the simple string return

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/login', methods=['POST'])
def login():
    doctor_id = request.form.get('doctor_id')
    doctor_password = request.form.get('doctor_password')
    
    with get_db_session() as db:
        doctor = db.query(Doctor).filter(Doctor.username == doctor_id).first()
        
        if doctor and check_password_hash(doctor.password_hash, doctor_password):
            session['doctor_id'] = doctor.id
            session['doctor_username'] = doctor.username
            session['doctor_fullname'] = doctor.full_name
            return redirect(url_for('patient_form'))
        else:
            flash('Hatalı kullanıcı adı veya şifre!')
            return redirect(url_for('index'))

@app.route('/logout')
def logout():
    session.clear()
    # flash('Başarıyla çıkış yaptınız.', 'success') # Remove the flash message
    return redirect(url_for('index'))

@app.route('/patient_form')
@login_required
def patient_form():
    return render_template('patient_form.html')

@app.route('/analyze', methods=['POST'])
@login_required
def analyze():
    # Get patient information
    patient_info = {
        'name': request.form.get('name', ''),
        'tc_no': request.form.get('tc_no', ''),
        'age': request.form.get('age', ''),
        'birth_date': request.form.get('birth_date', ''),
        'gender': request.form.get('gender', '')
    }
    
    # Check if X-ray file was uploaded
    if 'xray_image' not in request.files:
        flash('X-ray resmi yüklenmedi!')
        return redirect(url_for('patient_form'))
    
    file = request.files['xray_image']
    
    if file.filename == '':
        flash('Dosya seçilmedi!')
        return redirect(url_for('patient_form'))
    
    # Save the uploaded file
    original_dir = os.path.join(app.config['UPLOAD_FOLDER'], 'original')
    results_dir = os.path.join(app.config['UPLOAD_FOLDER'], 'results')
    
    # Dosya adını benzersiz yap
    timestamp = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
    unique_filename = f"{timestamp}_{file.filename}"
    
    file_path = os.path.join(original_dir, unique_filename)
    file.save(file_path)
    
    # Process the image with LandingAI
    try:
        image = Image.open(file_path)
        
        # Perform inference
        predictor = Predictor(ENDPOINT_ID, api_key=API_KEY)
        results = predictor.predict(image)
        
        # Create annotated image
        frame_with_preds = overlay_predictions(results, image=image)
        
        # Save annotated image
        result_image_name = f"result_{unique_filename}"
        result_image_path = os.path.join(results_dir, result_image_name)
        frame_with_preds.save(result_image_path)
        
        # Convert the PIL image to base64 for display in HTML
        buffered = io.BytesIO()
        frame_with_preds.save(buffered, format="JPEG")
        img_str = base64.b64encode(buffered.getvalue()).decode('utf-8')
        
        # Extract results
        detected_teeth = []
        tooth_locations = []
        tooth_types = []
        tooth_count = 0
        
        if results:
            for result in results:
                if hasattr(result, 'label_name') and hasattr(result, 'score'):
                    # Diş tipini ekle
                    tooth_type = result.label_name.upper() if result.label_name else "UNIDENTIFIED"
                    if tooth_type not in tooth_types:
                        tooth_types.append(tooth_type)
                    
                    # Determine position
                    tooth_location = "UNIDENTIFIED"
                    if hasattr(result, 'bboxes'):
                        bbox = result.bboxes
                        if bbox:
                            # Determine if the tooth is on the right or left side
                            # Assuming the image has the patient facing the viewer
                            image_width = image.width
                            bbox_center_x = (bbox[0] + bbox[2]) / 2
                            
                            if bbox_center_x < image_width / 2:
                                tooth_location = "SOL"
                            else:
                                tooth_location = "SAĞ"
                    
                    # Konumu ekle (eğer henüz eklenmemişse)
                    if tooth_location not in tooth_locations:
                        tooth_locations.append(tooth_location)
                    
                    detected_teeth.append({
                        'label': tooth_type,
                        'confidence': result.score,
                        'location': tooth_location,
                        'bbox': result.bboxes if hasattr(result, 'bboxes') else None
                    })
                    
                    tooth_count += 1
        
        # Diş türlerini ve konumları formatla
        formatted_tooth_types = ", ".join(tooth_types) if tooth_types else "UNIDENTIFIED"
        formatted_tooth_locations = ", ".join(tooth_locations) if tooth_locations else "UNIDENTIFIED"
        
        # Prepare information for the results page
        analysis_results = {
            'image_base64': img_str,
            'tooth_types': tooth_types,
            'tooth_type': formatted_tooth_types,
            'tooth_count': tooth_count,
            'tooth_locations': tooth_locations,
            'tooth_location': formatted_tooth_locations,
            'detected_teeth': detected_teeth,
            'raw_results': str(results)
        }
        
        # Veritabanına kaydet
        with get_db_session() as db:
            # Önce hastayı bul veya oluştur
            patient = db.query(Patient).filter(Patient.tc_no == patient_info['tc_no']).first()
            
            if not patient:
                patient = Patient(
                    tc_no=patient_info['tc_no'],
                    full_name=patient_info['name'],
                    age=int(patient_info['age']) if patient_info['age'].isdigit() else None,
                    birth_date=patient_info['birth_date'],
                    gender=patient_info['gender'],
                    doctor_id=session['doctor_id']
                )
                db.add(patient)
                db.flush()  # ID'yi oluşturmak için flush yapıyoruz
            
            # X-ray kaydını oluştur
            xray = XRay(
                file_path=file_path,
                file_name=file.filename,
                patient_id=patient.id
            )
            db.add(xray)
            db.flush()
            
            # X-ray sonucunu oluştur
            xray_result = XRayResult(
                tooth_types=formatted_tooth_types,
                tooth_count=tooth_count,
                tooth_locations=formatted_tooth_locations,
                result_image_path=result_image_path,
                raw_result=analysis_results['raw_results'],
                xray_id=xray.id
            )
            db.add(xray_result)
            db.commit()
        
        return render_template('results.html', 
                              patient_info=patient_info, 
                              results=analysis_results)
    
    except Exception as e:
        flash(f'Hata oluştu: {str(e)}')
        return redirect(url_for('patient_form'))

@app.route('/forgot_password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = request.form.get('email')
        sender_email = os.getenv('MAIL_USERNAME') # Gönderen e-postayı .env'den al

        if not sender_email:
             flash('Gönderen e-posta adresi yapılandırılmamış.')
             return redirect(url_for('index'))

        with get_db_session() as db:
            doctor = db.query(Doctor).filter(Doctor.email == email).first()

            if doctor:
                # Benzersiz bir jeton oluştur
                reset_token = str(uuid.uuid4())
                # Jetonu sakla (hala bellekte, ideal değil)
                password_reset_tokens[reset_token] = {'doctor_id': doctor.id, 'expiry': datetime.datetime.now() + datetime.timedelta(hours=1)}

                # Şifre sıfırlama e-postası gönder (Gmail API ile)
                reset_url = url_for('reset_password', token=reset_token, _external=True)

                try:
                    service = get_gmail_service()
                    if not service:
                        flash('E-posta gönderme servisi başlatılamadı. Lütfen sistem yöneticisiyle iletişime geçin.')
                        return redirect(url_for('index'))

                    message = EmailMessage()
                    message['To'] = email
                    message['From'] = sender_email
                    message['Subject'] = 'DentAI - Şifre Sıfırlama İsteği'

                    email_body = f'''Merhaba {doctor.full_name},

Şifrenizi sıfırlamak için aşağıdaki bağlantıyı kullanın:

{reset_url}

Bu bağlantı 1 saat içinde geçerliliğini yitirecektir.

Eğer bu isteği siz yapmadıysanız, lütfen bu e-postayı dikkate almayın.

Saygılarımızla,
DentAI Ekibi
'''
                    message.set_content(email_body)

                    # Mesajı base64 formatına kodla
                    encoded_message = base64.urlsafe_b64encode(message.as_bytes()).decode()

                    create_message = {
                        'raw': encoded_message
                    }

                    # Gmail API kullanarak mesajı gönder
                    send_message = (service.users().messages().send(userId='me', body=create_message).execute())
                    app.logger.info(f'Şifre sıfırlama e-postası {email} adresine gönderildi. Mesaj ID: {send_message["id"]}')
                    flash('Şifre sıfırlama bağlantısı e-posta adresinize gönderildi.')

                except Exception as e:
                    app.logger.error(f"E-posta gönderilirken Gmail API hatası: {str(e)}")
                    flash(f'E-posta gönderilirken bir hata oluştu. Lütfen daha sonra tekrar deneyin.') # Genel hata mesajı

            else:
                # Güvenlik için aynı mesajı göster (e-posta sistemde olmasa bile)
                app.logger.warning(f"Şifre sıfırlama isteği başarısız: {email} adresi bulunamadı.")
                flash('Şifre sıfırlama bağlantısı e-posta adresinize gönderildi.')

        return redirect(url_for('index'))

    return render_template('forgot_password.html')

@app.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    # Jetonun geçerliliğini kontrol et
    if token not in password_reset_tokens or password_reset_tokens[token]['expiry'] < datetime.datetime.now():
        flash('Geçersiz veya süresi dolmuş şifre sıfırlama bağlantısı.')
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        new_password = request.form.get('new_password')
        confirm_password = request.form.get('confirm_password')
        
        if not new_password or not confirm_password:
            flash('Lütfen tüm alanları doldurun.')
            return render_template('reset_password.html', token=token)
        
        if new_password != confirm_password:
            flash('Şifreler eşleşmiyor.')
            return render_template('reset_password.html', token=token)
        
        # Şifreyi güncelle
        with get_db_session() as db:
            doctor_id = password_reset_tokens[token]['doctor_id']
            doctor = db.query(Doctor).filter(Doctor.id == doctor_id).first()
            
            if doctor:
                doctor.password_hash = generate_password_hash(new_password)
                db.commit()
                
                # Jetonu kaldır
                del password_reset_tokens[token]
                
                flash('Şifreniz başarıyla değiştirildi. Yeni şifrenizle giriş yapabilirsiniz.')
                return redirect(url_for('index'))
            else:
                flash('Bir hata oluştu. Lütfen tekrar deneyin.')
        
    return render_template('reset_password.html', token=token)

@app.route('/previous_records')
@login_required
def previous_records():
    doctor_id = session['doctor_id']
    records = []
    with get_db_session() as db:
        # Doktora ait tüm hastaları bul
        patients = db.query(Patient).filter(Patient.doctor_id == doctor_id).all()
        
        # Tüm x-ray kayıtlarını ve sonuçları getir
        for patient in patients:
            xrays = db.query(XRay).filter(XRay.patient_id == patient.id).all()
            
            for xray in xrays:
                result = db.query(XRayResult).filter(XRayResult.xray_id == xray.id).first()
                
                if result:
                    # Base64 formatında görüntüyü elde et
                    try:
                        with open(result.result_image_path, "rb") as img_file:
                            img_data = base64.b64encode(img_file.read()).decode('utf-8')
                            
                        records.append({
                            'id': result.id,
                            'patient_id': patient.id,
                            'xray_id': xray.id,
                            'patient_name': patient.full_name,
                            'patient_tc': patient.tc_no,
                            'xray_date': xray.upload_date,
                            'xray_date_str': xray.upload_date.strftime('%d.%m.%Y %H:%M'),
                            'tooth_type': result.tooth_types,
                            'tooth_count': result.tooth_count,
                            'tooth_location': result.tooth_locations,
                            'image_base64': img_data
                        })
                    except Exception as e:
                        print(f"Görüntü yüklenirken hata: {str(e)}")
        
        # Kayıtları tarihe göre ters sırala (en yeni en üstte)
        records.sort(key=lambda x: x['xray_date'], reverse=True)
                    
        return render_template('previous_records.html', records=records)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        # Get form data
        doctor_name = request.form.get('doctor_name')
        doctor_email = request.form.get('doctor_email')
        doctor_password = request.form.get('doctor_password')
        doctor_password_confirm = request.form.get('doctor_password_confirm')
        
        # Validate form data
        if not all([doctor_name, doctor_email, doctor_password, doctor_password_confirm]):
            flash('Lütfen tüm alanları doldurunuz.')
            return redirect(url_for('register'))
            
        if doctor_password != doctor_password_confirm:
            flash('Şifreler eşleşmiyor.')
            return redirect(url_for('register'))
        
        # Veritabanına kaydedelim
        try:
            with get_db_session() as db:
                # Kullanıcı adı ve e-postanın benzersiz olduğunu kontrol et
                existing_user = db.query(Doctor).filter(
                    (Doctor.username == doctor_name) | (Doctor.email == doctor_email)
                ).first()
                
                if existing_user:
                    flash('Bu kullanıcı adı veya e-posta zaten kullanılıyor.')
                    return redirect(url_for('register'))
                
                # Yeni doktoru oluştur
                new_doctor = Doctor(
                    username=doctor_name,
                    email=doctor_email,
                    password_hash=generate_password_hash(doctor_password),
                    full_name=doctor_name
                )
                
                db.add(new_doctor)
                db.commit()
                
                flash('Kaydınız başarıyla tamamlandı. Giriş yapabilirsiniz.')
                return redirect(url_for('index'))
        except Exception as e:
            flash(f'Kayıt sırasında bir hata oluştu: {str(e)}')
            return redirect(url_for('register'))
            
    return render_template('register.html')

@app.route('/delete_record/<int:result_id>', methods=['POST'])
@login_required
def delete_record(result_id):
    doctor_id = session['doctor_id']
    try:
        with get_db_session() as db:
            # İlgili sonucu bul
            result = db.query(XRayResult).filter(XRayResult.id == result_id).first()
            
            if not result:
                flash('Kayıt bulunamadı.')
                return redirect(url_for('previous_records'))
            
            # X-ray kaydını bul
            xray = db.query(XRay).filter(XRay.id == result.xray_id).first()
            
            if not xray:
                flash('X-ray kaydı bulunamadı.')
                return redirect(url_for('previous_records'))
            
            # Hasta kaydını bul
            patient = db.query(Patient).filter(Patient.id == xray.patient_id).first()
            
            # Doktorun yetkisini kontrol et
            if patient and patient.doctor_id != doctor_id:
                flash('Bu kaydı silme yetkiniz yok.')
                return redirect(url_for('previous_records'))
            
            # Dosyaları sil
            if os.path.exists(result.result_image_path):
                os.remove(result.result_image_path)
            
            if xray and os.path.exists(xray.file_path):
                os.remove(xray.file_path)
            
            # Veritabanından kayıtları sil
            db.delete(result)
            
            if xray:
                db.delete(xray)
            
            db.commit()
            
            flash('Kayıt başarıyla silindi.')
    except Exception as e:
        flash(f'Kayıt silinirken bir hata oluştu: {str(e)}')
    
    return redirect(url_for('previous_records'))

if __name__ == '__main__':
    app.run(debug=True, port=5001)
