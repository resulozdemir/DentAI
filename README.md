# ISTUN - DentAI: Embedded Tooth Analysis Assistant

This project is an AI-powered web application developed at **Istanbul Health and Technology University (ISTÜN)** to help dentists detect and analyse impacted teeth on panoramic X-ray images.

The application allows doctors to enter patient information, upload X-ray images and receive analysis results from a custom model trained on the **LandingAI** platform.

---

## Tech Stack 🛠️

* **Backend:** Python, Flask  
* **Database:** PostgreSQL  
* **ORM:** SQLAlchemy  
* **AI Inference:** LandingAI platform  
* **Frontend:** HTML, CSS, Vanilla JS  
* **Auth / Password Reset:** Google OAuth 2.0 (Gmail API)  
* **Environment Variables:** python-dotenv  
* **Password Hashing:** Werkzeug

---

## Features

### 👤 User Management
* Secure sign-up & login for dentists.  
* Passwords stored with hashing.  
* Password-reset via e-mail (Google OAuth + Gmail API).  
* Session management & route protection (`@login_required`).

### 🧑‍⚕️ Patient Management
* Form to register new patients (ID No, name, age, birth date, gender).  
* Automatic recognition of existing patients.

### 🦷 X-Ray Analysis
* Upload panoramic X-ray.  
* Original image stored under `uploads/original`.  
* Image sent to LandingAI endpoint for inference.  
* Model returns tooth type, count and position (left/right).  
* Result image with bounding boxes generated and saved under `uploads/results`.

### 📊 Result Display
* Side-by-side view of patient data, original X-ray and annotated X-ray.  
* Clear listing of detected teeth (type, count, position).  
* Detailed analysis table.

### 🗂️ Record History
* Logged-in doctor can view all previous analyses.  
* Sorted by newest first.  
* Secure deletion of a record (DB row + files).

### ℹ️ Other Pages
* "About Us" page describing project & team.

---

## Project Structure

```
.
├── app.py                  # Main Flask app (routes, AI integration)
├── database.py             # SQLAlchemy models & DB config
├── setup_db.py             # Script to create DB/tables (run once)
├── requirements.txt        # Python dependencies
├── .env                    # Environment variables (DB, mail/OAuth) – SECRET
├── static/                 # CSS, JS, images
│   ├── css/
│   ├── js/
│   └── images/
├── templates/              # Jinja2 HTML templates
│   ├── base.html
│   ├── index.html           # Login
│   ├── register.html        # Doctor sign-up
│   ├── forgot_password.html
│   ├── reset_password.html
│   ├── patient_form.html    # Patient details + X-ray upload
│   ├── results.html         # Analysis results page
│   ├── previous_records.html
│   └── about.html
└── uploads/
    ├── original/           # Raw uploaded images
    └── results/            # Annotated result images
```

---

## Setup 🚀

1. **Clone the repo**
   ```bash
   git clone <repository_url>
   cd DentAI
   ```
2. **(Optional) Create & activate a virtualenv**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # macOS/Linux
   # venv\Scripts\activate  # Windows
   ```
3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```
4. **Install PostgreSQL** and make sure the server is running.
5. **Configure `.env`**
   ```dotenv
   DB_USER=your_pg_user
   DB_PASSWORD=your_pg_password
   DB_HOST=localhost
   DB_PORT=5432
   DB_NAME=dentai_db

   # Gmail API (Google Cloud Console)
   GOOGLE_CLIENT_ID=xxxxxxxx.apps.googleusercontent.com
   GOOGLE_CLIENT_SECRET=xxxxxxxxxxxxxxxx
   GOOGLE_REFRESH_TOKEN=xxxxxxxxxxxxxxxxxxxxxxxx
   MAIL_USERNAME=your_gmail@gmail.com
   ```
   *Create a Google Cloud project, enable Gmail API, generate OAuth credentials and obtain a refresh token via OAuth Playground.*
6. **Initialise the DB**
   ```bash
   python setup_db.py
   ```

---

## Running the App

```bash
python app.py
```
The server runs at `http://127.0.0.1:5001` by default.

---

## Typical Workflow

1. Sign up a doctor account → log in.  
2. Fill patient form & upload X-ray.  
3. Click **Analyse** → wait for results.  
4. View annotated image & details.  
5. Browse **Previous Records** for history.  
6. Use **Forgot Password** if needed.  
7. Log out when done.

---

## Notes

* Analysis relies on an external **LandingAI** endpoint – ensure `API_KEY` and `ENDPOINT_ID` are set inside `app.py` or `.env`.
* Password reset uses Gmail OAuth 2.0 – credentials must be valid.

---

## License

This project is for academic purposes at ISTÜN. All rights reserved.

