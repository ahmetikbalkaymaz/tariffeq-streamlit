# # import streamlit as st
# # import streamlit.components.v1 as components
# # import os
# # from pages.sidebar import sidebar

# # st.set_page_config(layout="wide")


# # sidebar()

# # try:
# #     html_file_path = os.path.join(os.path.dirname(__file__), 'foresight.html')

# #     with open(html_file_path, 'r', encoding='utf-8') as f:
# #         html_content = f.read()

# #     components.html(html_content, height=900, scrolling=True)

# # except FileNotFoundError:
# #     st.error("foresight.html dosyası bulunamadı. Lütfen app.py ile aynı dizinde olduğundan emin olun.")


# import streamlit as st
# import streamlit.components.v1 as components
# import os
# import json
# from pathlib import Path  # Dosya yolları için daha modern bir kütüphane
# from pages.sidebar import sidebar

# st.set_page_config(layout="wide")
# sidebar()


# # --- 1. ADIM: VERİYİ PYTHON TARAFINDA OKUMA ---

# all_features_data = []
# try:
#     # foresight.py'nin bulunduğu 'pages' klasöründen bir üst dizine çıkıp 'files' klasörünü buluyoruz.
#     # Bu yöntem, projenizin nerede çalıştığından bağımsız olarak doğru yolu bulur.
#     files_dir = Path(__file__).parent.parent / "files"

#     data_file_names = [
#         'yangin_verisi_part_1.json',
#         'yangin_verisi_part_2.json',
#         'yangin_verisi_part_3.json'
#     ]

#     for file_name in data_file_names:
#         file_path = files_dir / file_name
#         with open(file_path, 'r', encoding='utf-8') as f:
#             data = json.load(f)
#             # Her dosyadaki 'features' listesini ana listemize ekliyoruz
#             if "features" in data and isinstance(data["features"], list):
#                 all_features_data.extend(data["features"])

#     # Python listesini, JavaScript'in anlayacağı bir JSON metnine dönüştürüyoruz.
#     # Bu, HTML'e gömeceğimiz dev bir string olacak.
#     all_features_json_string = json.dumps(all_features_data)

# except FileNotFoundError as e:
#     st.error(f"❌ Veri dosyası bulunamadı: {e.filename}. Lütfen 'files' klasörünün proje ana dizininde olduğundan emin olun.")
#     st.stop()
# except Exception as e:
#     st.error(f"❌ Veri dosyaları okunurken bir hata oluştu: {e}")
#     st.stop()


# # --- 2. ADIM: HTML DOSYASINI OKUMA VE VERİYİ İÇİNE YERLEŞTİRME ---

# try:
#     html_file_path = os.path.join(os.path.dirname(__file__), 'foresight.html')

#     with open(html_file_path, 'r', encoding='utf-8') as f:
#         html_content = f.read()

#     # HTML içindeki özel yer tutucuyu, okuduğumuz JSON verisiyle değiştiriyoruz.
#     # Tek tırnakları korumak için escape ediyoruz
#     html_content = html_content.replace("'__VERI_BURAYA_GELECEK__'", all_features_json_string)  

#     components.html(html_content, height=900, scrolling=True)

# except FileNotFoundError:
#     st.error("foresight.html dosyası bulunamadı. Lütfen 'foresight.py' ile aynı dizinde olduğundan emin olun.")
# except Exception as e:
#     st.error(f"HTML işlenirken bir hata oluştu: {e}")


import streamlit as st
import streamlit.components.v1 as components
import os
import json
import sqlite3
from pathlib import Path
from pages.sidebar import sidebar

st.set_page_config(layout="wide")
sidebar()

DB_FILE = Path(__file__).parent.parent / "fires.db"

# @st.cache_data decorator'ı ve get_data_from_db() fonksiyonu aynı kalıyor...
@st.cache_data
def get_data_from_db():
    """
    SQLite veritabanından tüm yangın verilerini çeker ve
    JavaScript'in beklediği 'features' listesi formatına dönüştürür.
    """
    if not DB_FILE.exists():
        st.error(f"❌ Veritabanı dosyası bulunamadı: {DB_FILE}")
        st.info("Lütfen önce `setup_db.py` scriptini çalıştırarak veritabanını oluşturun.")
        return None
    try:
        conn = sqlite3.connect(DB_FILE, check_same_thread=False)
        cursor = conn.cursor()
        cursor.execute("SELECT properties, geometry FROM fires")
        rows = cursor.fetchall()
        conn.close()
        features_list = []
        for row in rows:
            properties = json.loads(row[0])
            geometry = json.loads(row[1])
            feature = {
                "type": "Feature",
                "properties": properties,
                "geometry": geometry
            }
            features_list.append(feature)
        return features_list
    except Exception as e:
        st.error(f"❌ Veritabanından veri okunurken bir hata oluştu: {e}")
        return None

# --- ANA UYGULAMA MANTIĞI ---

# 1. ADIM: VERİYİ VE API ANAHTARINI ALMA
all_features_data = get_data_from_db()

# Streamlit Secrets'tan Gemini API anahtarını al
try:
    gemini_api_key = st.secrets["GEMINI_API_KEY"]
except KeyError:
    st.error("🔑 Gemini API anahtarı bulunamadı. Lütfen Streamlit Cloud > Settings > Secrets bölümüne `GEMINI_API_KEY` olarak eklediğinizden emin olun.")
    st.stop() # Anahtar yoksa uygulamayı durdur

# Eğer veri ve anahtar başarıyla okunduysa devam et
if all_features_data and gemini_api_key:
    all_features_json_string = json.dumps(all_features_data)

    # 2. ADIM: HTML DOSYASINI OKUMA VE VERİLERİ İÇİNE YERLEŞTİRME
    try:
        html_file_path = os.path.join(os.path.dirname(__file__), 'foresight.html')
        with open(html_file_path, 'r', encoding='utf-8') as f:
            html_content = f.read()

        # 1. Değişiklik: Veri yer tutucusunu değiştir
        html_content = html_content.replace("'__VERI_BURAYA_GELECEK__'", all_features_json_string)  
        
        # 2. Değişiklik: API anahtarı yer tutucusunu değiştir
        html_content = html_content.replace("__GEMINI_API_KEY__", gemini_api_key)

        components.html(html_content, height=900, scrolling=True)

    except FileNotFoundError:
        st.error("foresight.html dosyası bulunamadı. Lütfen 'foresight.py' ile aynı dizinde olduğundan emin olun.")
    except Exception as e:
        st.error(f"HTML işlenirken bir hata oluştu: {e}")