import os
import sys
import psycopg2
from dotenv import load_dotenv
from database import init_db

def setup_database():
    """
    PostgreSQL veritabanı oluşturma işlemini gerçekleştirir.
    Önce database.py dosyasındaki tablolarla aynı isimde veritabanını oluşturur,
    daha sonra tabloları oluşturur.
    """
    # .env dosyasından yapılandırmaları yükle
    load_dotenv()
    
    # Veritabanı bağlantı parametreleri
    db_params = {
        'user': os.getenv("DB_USER", "postgres"),
        'password': os.getenv("DB_PASSWORD", "postgres"),
        'host': os.getenv("DB_HOST", "localhost"),
        'port': os.getenv("DB_PORT", "5432"),
    }
    
    db_name = os.getenv("DB_NAME", "dentai_db")
    
    # Önce postgres veritabanına bağlan
    conn = None
    try:
        # Postgres veritabanına bağlan
        conn = psycopg2.connect(
            dbname="postgres",
            **db_params
        )
        conn.autocommit = True
        cursor = conn.cursor()
        
        # Veritabanını listele
        cursor.execute("SELECT datname FROM pg_database;")
        databases = [record[0] for record in cursor.fetchall()]
        
        # Veritabanı zaten varsa silme sorgusu
        if db_name in databases:
            print(f"Veritabanı {db_name} zaten mevcut.")
            
            # Kullanıcıya sorma
            user_input = input(f"Mevcut '{db_name}' veritabanını silip yeniden oluşturmak istiyor musunuz? (e/h): ")
            if user_input.lower() == 'e':
                print(f"Veritabanı {db_name} siliniyor...")
                
                # Veritabanını sil
                cursor.execute(f"""
                    SELECT pg_terminate_backend(pg_stat_activity.pid)
                    FROM pg_stat_activity
                    WHERE pg_stat_activity.datname = '{db_name}'
                    AND pid <> pg_backend_pid();
                """)
                cursor.execute(f"DROP DATABASE IF EXISTS {db_name};")
                print(f"Veritabanı {db_name} silindi.")
            else:
                print("İşlem iptal edildi.")
                sys.exit(0)
                
        # Veritabanını oluştur
        print(f"Veritabanı {db_name} oluşturuluyor...")
        cursor.execute(f"CREATE DATABASE {db_name};")
        print(f"Veritabanı {db_name} başarıyla oluşturuldu.")
        
        cursor.close()
        
    except Exception as e:
        print(f"Hata oluştu: {e}")
        sys.exit(1)
    finally:
        if conn:
            conn.close()
    
    # Tabloları oluştur
    print("Veritabanı tabloları oluşturuluyor...")
    try:
        init_db()
        print("Veritabanı tabloları başarıyla oluşturuldu.")
    except Exception as e:
        print(f"Tablo oluşturma hatası: {e}")
        sys.exit(1)
        
    print("Veritabanı kurulumu tamamlandı!")

if __name__ == "__main__":
    setup_database() 