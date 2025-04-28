# ISTÜN - DentAI: Gömülü Diş Analiz Asistanı

Bu proje, İstanbul Sağlık ve Teknoloji Üniversitesi (İSTÜN) bünyesinde geliştirilmiş, diş hekimlerine panoramik diş röntgenleri üzerinde gömülü diş tespiti ve analizi konusunda yardımcı olmak amacıyla tasarlanmış yapay zeka destekli bir web uygulamasıdır. Uygulama, doktorların hasta bilgilerini girmesine, röntgen görüntülerini yüklemesine ve LandingAI platformu üzerinden eğitilmiş özel bir model aracılığıyla analiz sonuçları almasına olanak tanır.

## Kullanılan Teknolojiler

*   **Backend:** Python, Flask
*   **Veritabanı:** PostgreSQL
*   **ORM:** SQLAlchemy
*   **Yapay Zeka Analizi:** LandingAI Platformu
*   **Frontend:** HTML, CSS, JavaScript (Temel)
*   **Kimlik Doğrulama (Şifre Sıfırlama):** Google OAuth 2.0 (Gmail API)
*   **Ortam Değişkenleri:** python-dotenv
*   **Şifreleme:** Werkzeug

## Özellikler

*   **Kullanıcı Yönetimi:**
    *   Doktorlar için güvenli kayıt ve giriş sistemi.
    *   Şifre hashleme ile güvenli şifre saklama.
    *   E-posta ile şifre sıfırlama (Google OAuth ve Gmail API entegrasyonu).
    *   Oturum yönetimi ve yetkilendirme (`@login_required` decorator).
*   **Hasta Yönetimi:**
    *   Yeni hasta bilgilerini (TC No, Ad Soyad, Yaş, Doğum Tarihi, Cinsiyet) kaydetme formu.
    *   Mevcut hastaların otomatik olarak tanınması.
*   **X-Ray Analizi:**
    *   Panoramik röntgen görüntüsü yükleme.
    *   Yüklenen orijinal görüntünün saklanması (`uploads/original`).
    *   LandingAI servisi üzerinden eğitilmiş model ile görüntü analizi.
    *   Analiz sonucunda gömülü dişlerin türü, adeti ve konumunun (sağ/sol) belirlenmesi.
    *   Analiz edilmiş, üzerine işaretlemeler yapılmış sonucun görsel olarak oluşturulması ve saklanması (`uploads/results`).
*   **Sonuç Gösterimi:**
    *   Hasta bilgileri, yüklenen orijinal röntgen ve analiz edilmiş (işaretlenmiş) röntgenin yan yana gösterimi.
    *   Tespit edilen diş sayısı, türleri ve konumlarının açıkça belirtilmesi.
    *   Detaylı analiz sonuçlarının listelenmesi.
*   **Kayıt Geçmişi:**
    *   Giriş yapmış doktora ait tüm hastaların geçmiş analiz kayıtlarının listelenmesi.
    *   Kayıtların tarih sırasına göre (en yeni üstte) gösterimi.
    *   İstenilen kaydın (veritabanı kaydı ve ilgili dosyalar) güvenli bir şekilde silinmesi.
*   **Diğer:**
    *   Proje ve ekip hakkında bilgi veren "Hakkımızda" sayfası.
    *   Duyarlı (Responsive) tasarım (temel düzeyde).

## Proje Yapısı

```
.
├── app.py                  # Ana Flask uygulaması (Routes, View Fonksiyonları, AI Entegrasyonu)
├── database.py             # SQLAlchemy modelleri ve veritabanı bağlantı ayarları
├── setup_db.py             # Veritabanını ve tabloları ilk kez oluşturma betiği (Manuel Çalıştırılır)
├── requirements.txt        # Gerekli Python kütüphaneleri
├── .env                    # Ortam değişkenleri (Veritabanı, Mail/OAuth bilgileri - GİZLİ)
├── README.md               # Bu dosya
├── static/                 # Statik dosyalar (CSS, JavaScript, Resimler)
│   ├── css/                # CSS stil dosyaları (main.css, login.css vb.)
│   ├── js/                 # JavaScript dosyaları (varsa)
│   └── images/             # Arayüzde kullanılan resimler (logo, arka plan vb.)
├── templates/              # HTML şablonları (Jinja2)
│   ├── base.html           # Ana şablon (Header, Footer, Flash mesajlar)
│   ├── index.html          # Giriş (Login) sayfası
│   ├── register.html       # Doktor kayıt sayfası
│   ├── forgot_password.html # Şifremi unuttum sayfası
│   ├── reset_password.html  # Şifre sıfırlama sayfası
│   ├── patient_form.html   # Hasta bilgi giriş ve röntgen yükleme formu
│   ├── results.html        # Analiz sonuçlarının gösterildiği sayfa
│   ├── previous_records.html # Geçmiş kayıtların listelendiği sayfa
│   └── about.html          # Hakkımızda sayfası
└── uploads/                # Kullanıcı tarafından yüklenen dosyaların saklandığı yer (Geçici)
    ├── original/           # Yüklenen orijinal röntgen görüntüleri
    └── results/            # Analiz sonucu oluşturulan işaretlenmiş görüntüler
```

## Kurulum

1.  **Depoyu Klonlayın:**
    ```bash
    git clone <repository_url>
    cd BitirmeProjesiWEB
    ```
2.  **Sanal Ortam Oluşturun ve Aktifleştirin (Önerilir):**
    ```bash
    python3 -m venv venv
    source venv/bin/activate  # macOS/Linux için
    # venv\Scripts\activate  # Windows için
    ```
3.  **Gerekli Paketleri Yükleyin:**
    ```bash
    python3 -m pip install -r requirements.txt
    ```
4.  **PostgreSQL Kurulumu:**
    *   Sisteminizde PostgreSQL veritabanı sunucusunun kurulu ve çalışır olduğundan emin olun.
5.  **.env Dosyasını Yapılandırın:**
    *   Proje ana dizininde `.env` adında bir dosya oluşturun.
    *   Aşağıdaki değişkenleri kendi PostgreSQL ve Google OAuth 2.0 bilgilerinizle doldurun:
        ```dotenv
        DB_USER=postgres_kullanici_adiniz
        DB_PASSWORD=postgres_sifreniz
        DB_HOST=localhost # veya veritabanı sunucu adresiniz
        DB_PORT=5432
        DB_NAME=dentai_db # veya istediğiniz bir veritabanı adı

        # Gmail API için Google Cloud Console'dan alınan OAuth bilgileri
        GOOGLE_CLIENT_ID=xxxxxxxxxxxx.apps.googleusercontent.com
        GOOGLE_CLIENT_SECRET=xxxxxxxxxxxxxxxxxxxx
        GOOGLE_REFRESH_TOKEN=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
        MAIL_USERNAME=sizin_gmail_adresiniz@gmail.com # E-postaların gönderileceği adres
        ```
    *   **Önemli:** Google OAuth bilgilerini almak için Google Cloud Console'da bir proje oluşturmalı, Gmail API'yi etkinleştirmeli ve bir OAuth 2.0 İstemci Kimliği (Web uygulaması türünde) oluşturmalısınız. Yetkilendirilmiş yönlendirme URI'si olarak `https://developers.google.com/oauthplayground` eklemeyi unutmayın. Refresh Token'ı Google OAuth Playground kullanarak alabilirsiniz. `MAIL_USERNAME`'in OAuth iznini aldığınız hesapla aynı olması gerekir.
6.  **Veritabanını ve Tabloları Oluşturun:**
    *   Aşağıdaki komutu çalıştırarak `.env` dosyasındaki `DB_NAME` ile belirtilen veritabanını ve `database.py` içindeki tabloları oluşturun:
    ```bash
    python setup_db.py
    ```
    *   Eğer veritabanı zaten varsa, betik size silip yeniden oluşturmayı soracaktır.

## Uygulamayı Çalıştırma

1.  Proje ana dizinindeyken ve sanal ortam aktifken aşağıdaki komutu çalıştırın:
    ```bash
    python app.py
    ```
2.  Uygulama varsayılan olarak `http://127.0.0.1:5001` adresinde çalışacaktır. Tarayıcınızda bu adrese gidin.

## Kullanım Akışı

1.  İlk kullanımda "KAYIT OL" bağlantısı ile bir doktor hesabı oluşturun.
2.  Oluşturduğunuz kullanıcı adı ve şifre ile giriş yapın (`index.html`).
3.  Giriş yaptıktan sonra hasta bilgi formuna (`patient_form.html`) yönlendirilirsiniz.
4.  Hastanın bilgilerini girin ve panoramik röntgen dosyasını seçin.
5.  "Analiz Et" (veya benzeri) butonuna tıklayarak görüntüyü yükleyin ve analizi başlatın.
6.  Analiz tamamlandığında sonuç sayfasına (`results.html`) yönlendirilirsiniz. Burada hasta bilgileri, orijinal ve işaretlenmiş röntgen ile analiz detaylarını (diş sayısı, türü, konumu) görürsünüz.
7.  Navigasyon menüsündeki "Geçmiş Kayıtlar" linki ile daha önceki analizlerinizi (`previous_records.html`) listeleyebilir ve istemediklerinizi silebilirsiniz.
8.  Şifrenizi unutursanız, giriş sayfasındaki "ŞİFREMİ UNUTTUM" bağlantısını kullanabilirsiniz.
9.  İşiniz bittiğinde "Çıkış Yap" linki ile oturumu sonlandırabilirsiniz.

## Notlar

*   Bu uygulama, analiz için harici bir servis olan **LandingAI**'ye bağımlıdır. LandingAI API anahtarınızın (`API_KEY`) ve Endpoint ID'nizin (`ENDPOINT_ID`) `app.py` içinde doğru şekilde tanımlanmış olması gerekir.
*   Şifre sıfırlama özelliği **Google OAuth 2.0** ve **Gmail API** kullanır. `.env` dosyasındaki ilgili kimlik bilgilerinin doğru ve geçerli olması şarttır.

