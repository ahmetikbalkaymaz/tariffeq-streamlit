import sqlite3
import json
from pathlib import Path

# --- Konfigürasyon ---
JSON_FILES = [
    'files/yangin_verisi_part_1.json',
    'files/yangin_verisi_part_2.json',
    'files/yangin_verisi_part_3.json'
]
DB_FILE = 'fires.db'
TABLE_NAME = 'fires'

def create_database():
    """
    JSON dosyalarındaki verileri okur ve bir SQLite veritabanına yazar.
    Bu fonksiyonu sadece bir kez çalıştırmanız yeterlidir.
    """
    # Proje ana dizinini baz al
    base_path = Path(__file__).parent
    
    # Veritabanı bağlantısı oluştur
    conn = sqlite3.connect(base_path / DB_FILE)
    cursor = conn.cursor()

    # Eğer tablo varsa sil ve yeniden oluştur (temiz bir başlangıç için)
    cursor.execute(f'DROP TABLE IF EXISTS {TABLE_NAME}')
    
    # Yangın verilerini saklamak için yeni bir tablo oluştur
    # 'properties' ve 'geometry' sütunlarını JSON metni olarak saklayacağız (TEXT)
    cursor.execute(f'''
        CREATE TABLE {TABLE_NAME} (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            fire_id INTEGER UNIQUE,
            properties TEXT,
            geometry TEXT
        )
    ''')

    print(f"'{TABLE_NAME}' tablosu '{DB_FILE}' içinde başarıyla oluşturuldu.")

    # Tüm JSON dosyalarını işle
    total_records = 0
    for json_file in JSON_FILES:
        file_path = base_path / json_file
        print(f"'{file_path}' işleniyor...")
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                features = data.get("features", [])
                
                for feature in features:
                    props = feature.get("properties", {})
                    geom = feature.get("geometry", {})
                    fire_id = props.get("id")

                    if fire_id is not None and geom:
                        # 'properties' ve 'geometry' Python dict'lerini JSON string'ine çevir
                        properties_str = json.dumps(props)
                        geometry_str = json.dumps(geom)
                        
                        # Veritabanına ekle
                        cursor.execute(
                            f'INSERT INTO {TABLE_NAME} (fire_id, properties, geometry) VALUES (?, ?, ?)',
                            (fire_id, properties_str, geometry_str)
                        )
                        total_records += 1

        except FileNotFoundError:
            print(f"UYARI: '{file_path}' bulunamadı, atlanıyor.")
        except Exception as e:
            print(f"HATA: '{file_path}' işlenirken bir sorun oluştu: {e}")

    # Değişiklikleri kaydet ve bağlantıyı kapat
    conn.commit()
    conn.close()
    
    print("-" * 30)
    print(f"✅ İşlem tamamlandı! Toplam {total_records} kayıt '{DB_FILE}' veritabanına eklendi.")


if __name__ == '__main__':
    create_database()