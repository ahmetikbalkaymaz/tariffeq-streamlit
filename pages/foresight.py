# import streamlit as st
# import streamlit.components.v1 as components
# import os
# from pages.sidebar import sidebar

# st.set_page_config(layout="wide")


# sidebar()

# try:
#     html_file_path = os.path.join(os.path.dirname(__file__), 'foresight.html')

#     with open(html_file_path, 'r', encoding='utf-8') as f:
#         html_content = f.read()

#     components.html(html_content, height=900, scrolling=True)

# except FileNotFoundError:
#     st.error("foresight.html dosyası bulunamadı. Lütfen app.py ile aynı dizinde olduğundan emin olun.")


import streamlit as st
import streamlit.components.v1 as components
import os
import json
from pathlib import Path  # Dosya yolları için daha modern bir kütüphane
from pages.sidebar import sidebar

st.set_page_config(layout="wide")
sidebar()


# --- 1. ADIM: VERİYİ PYTHON TARAFINDA OKUMA ---

all_features_data = []
try:
    # foresight.py'nin bulunduğu 'pages' klasöründen bir üst dizine çıkıp 'files' klasörünü buluyoruz.
    # Bu yöntem, projenizin nerede çalıştığından bağımsız olarak doğru yolu bulur.
    files_dir = Path(__file__).parent.parent / "files"

    data_file_names = [
        'yangin_verisi_part_1.json',
        'yangin_verisi_part_2.json',
        'yangin_verisi_part_3.json'
    ]

    for file_name in data_file_names:
        file_path = files_dir / file_name
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            # Her dosyadaki 'features' listesini ana listemize ekliyoruz
            if "features" in data and isinstance(data["features"], list):
                all_features_data.extend(data["features"])

    # Python listesini, JavaScript'in anlayacağı bir JSON metnine dönüştürüyoruz.
    # Bu, HTML'e gömeceğimiz dev bir string olacak.
    all_features_json_string = json.dumps(all_features_data)

except FileNotFoundError as e:
    st.error(f"❌ Veri dosyası bulunamadı: {e.filename}. Lütfen 'files' klasörünün proje ana dizininde olduğundan emin olun.")
    st.stop()
except Exception as e:
    st.error(f"❌ Veri dosyaları okunurken bir hata oluştu: {e}")
    st.stop()


# --- 2. ADIM: HTML DOSYASINI OKUMA VE VERİYİ İÇİNE YERLEŞTİRME ---

try:
    html_file_path = os.path.join(os.path.dirname(__file__), 'foresight.html')

    with open(html_file_path, 'r', encoding='utf-8') as f:
        html_content = f.read()

    # HTML içindeki özel yer tutucuyu, okuduğumuz JSON verisiyle değiştiriyoruz.
    # Tek tırnakları korumak için escape ediyoruz
    html_content = html_content.replace("'__VERI_BURAYA_GELECEK__'", all_features_json_string)  

    components.html(html_content, height=900, scrolling=True)

except FileNotFoundError:
    st.error("foresight.html dosyası bulunamadı. Lütfen 'foresight.py' ile aynı dizinde olduğundan emin olun.")
except Exception as e:
    st.error(f"HTML işlenirken bir hata oluştu: {e}")