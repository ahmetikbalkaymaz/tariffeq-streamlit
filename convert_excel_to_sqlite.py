import pandas as pd
import sqlite3
from pathlib import Path
import time

# Projenin kök dizinini baz al
BASE_DIR = Path(__file__).parent.parent.parent
EXCEL_PATH = Path("/Users/ahmetikbalkaymaz/Desktop/PROJELER/tariffeq-streamlit/files/deprem.xlsx")
DB_DIR = BASE_DIR / "backend" / "app" / "data"
DB_PATH = DB_DIR / "locations.db"

def convert():
    print(f"Excel dosyasından okunuyor: {EXCEL_PATH}")
    if not EXCEL_PATH.exists():
        print(f"HATA: Excel dosyası bulunamadı: {EXCEL_PATH}")
        return

    start_time = time.time()
    df = pd.read_excel(EXCEL_PATH, sheet_name="Veri")
    print(f"Excel okundu. ({time.time() - start_time:.2f}s)")

    # Sadece gerekli sütunları al ve temizle
    df = df[["ILADI", "ILCEADI", "KOYADI", "MAHADI", "Yeni Sınıf"]].dropna()
    # SQL için daha kolay sütun adları
    df.columns = ['province', 'district', 'village', 'neighborhood', 'zone']
    
    # Veritabanı klasörünü oluştur
    DB_DIR.mkdir(parents=True, exist_ok=True)

    print(f"SQLite veritabanına yazılıyor: {DB_PATH}")
    conn = sqlite3.connect(DB_PATH)
    
    # Veriyi 'locations' tablosuna yaz
    df.to_sql('locations', conn, if_exists='replace', index=False)
    print("Veri yazıldı. İndeksler oluşturuluyor...")

    # Hızlı sorgulama için İNDEKS OLUŞTURMA (En Önemli Kısım)
    cursor = conn.cursor()
    cursor.execute("CREATE INDEX idx_prov ON locations (province)")
    cursor.execute("CREATE INDEX idx_prov_dist ON locations (province, district)")
    cursor.execute("CREATE INDEX idx_prov_dist_vill ON locations (province, district, village)")
    cursor.execute("CREATE INDEX idx_full ON locations (province, district, village, neighborhood)")
    
    conn.commit()
    conn.close()
    
    end_time = time.time()
    print(f"Başarıyla tamamlandı! ({end_time - start_time:.2f}s)")
    print(f"Veritabanı dosyası oluşturuldu: {DB_PATH}")

if __name__ == "__main__":
    convert()