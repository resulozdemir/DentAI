from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, Text, DateTime, LargeBinary, Float, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
import datetime
import os
from dotenv import load_dotenv

# .env dosyasından veritabanı bilgilerini yükle
load_dotenv()

# Veritabanı bağlantı bilgileri
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "postgres")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "dentai_db")

# Veritabanı bağlantı URL'si
DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# SQLAlchemy ORM bağlantısını oluştur
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Veritabanı modellerini tanımla
class Doctor(Base):
    __tablename__ = "doctors"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    full_name = Column(String(100), nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    is_active = Column(Boolean, default=True)
    
    # İlişkiler
    patients = relationship("Patient", back_populates="doctor")

class Patient(Base):
    __tablename__ = "patients"

    id = Column(Integer, primary_key=True, index=True)
    tc_no = Column(String(11), unique=True, index=True, nullable=False)
    full_name = Column(String(100), nullable=False)
    age = Column(Integer, nullable=True)
    birth_date = Column(String(10), nullable=True)
    gender = Column(String(10), nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    doctor_id = Column(Integer, ForeignKey("doctors.id"), nullable=True)
    
    # İlişkiler
    doctor = relationship("Doctor", back_populates="patients")
    xrays = relationship("XRay", back_populates="patient", cascade="all, delete-orphan")

class XRay(Base):
    __tablename__ = "xrays"

    id = Column(Integer, primary_key=True, index=True)
    file_path = Column(String(255), nullable=False)
    file_name = Column(String(255), nullable=False)
    upload_date = Column(DateTime, default=datetime.datetime.utcnow)
    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=False)
    
    # İlişkiler
    patient = relationship("Patient", back_populates="xrays")
    result = relationship("XRayResult", back_populates="xray", uselist=False, cascade="all, delete-orphan")

class XRayResult(Base):
    __tablename__ = "xray_results"

    id = Column(Integer, primary_key=True, index=True)
    tooth_types = Column(String(255), nullable=True)
    tooth_count = Column(Integer, nullable=True)
    tooth_locations = Column(String(255), nullable=True)
    result_image_path = Column(String(255), nullable=True)
    raw_result = Column(Text, nullable=True)
    processed_date = Column(DateTime, default=datetime.datetime.utcnow)
    xray_id = Column(Integer, ForeignKey("xrays.id"), nullable=False, unique=True)
    
    # İlişkiler
    xray = relationship("XRay", back_populates="result")

# Veritabanını oluşturma fonksiyonu
def init_db():
    Base.metadata.create_all(bind=engine)

# Veritabanı oturumu oluşturma işlevi
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close() 