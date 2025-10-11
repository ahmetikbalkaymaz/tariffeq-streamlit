# import streamlit as st
# import streamlit.components.v1 as components
# import os
# from pages.sidebar import sidebar

# st.set_page_config(layout="wide")


# sidebar()

# try:
#     html_file_path = os.path.join(os.path.dirname(__file__), 'cat_loss.html')

#     with open(html_file_path, 'r', encoding='utf-8') as f:
#         html_content = f.read()

#     components.html(html_content, height=900, scrolling=True)

# except FileNotFoundError:
#     st.error("cat_loss.html dosyası bulunamadı. Lütfen app.py ile aynı dizinde olduğundan emin olun.")


import streamlit as st
import streamlit.components.v1 as components
import os
import json
import glob
from pages.sidebar import sidebar

st.set_page_config(layout="wide")
sidebar()

def load_json_data(folder_path):
    """JSON klasöründeki tüm dosyaları okur ve birleştirir"""
    all_data = []
    json_files = glob.glob(os.path.join(folder_path, "*.json"))
    
    for file_path in json_files:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                # Her veriye dosya adını ekle
                if isinstance(data, list):
                    for item in data:
                        item['_source_file'] = os.path.basename(file_path)
                    all_data.extend(data)
                else:
                    data['_source_file'] = os.path.basename(file_path)
                    all_data.append(data)
        except Exception as e:
            st.warning(f"'{os.path.basename(file_path)}' dosyası okunamadı: {str(e)}")
    
    return all_data

def convert_to_incident_format(json_data):
    """JSON verilerini HTML'deki incidents formatına dönüştürür"""
    incidents = []
    unknown_incidents = []  # Bilinmeyen olayları takip et
    
    for item in json_data:
        tesis_adi = item.get('tesisAdi', '')
        
        # Eğer tesisAdi boş veya yok ise kaydet
        if not tesis_adi or tesis_adi.strip() == '':
            unknown_incidents.append({
                'dosya': item.get('_source_file', 'Bilinmiyor'),
                'id': item.get('id', 'ID yok'),
                'tarih': item.get('tarih', ''),
                'il': item.get('il', ''),
                'ilce': item.get('ilce', ''),
                'konum': item.get('konum', ''),
                'sektor': item.get('sektor', '')
            })
        
        incident = {
            "id": f"incident-{item.get('id', '')}",
            "tarih": item.get('tarih', ''),
            "il": item.get('il', ''),
            "ilce": item.get('ilce', ''),
            "konum": item.get('konum', ''),
            "tehlikeTuru": item.get('olayTuru', 'Yangın'),
            "olayAdi": tesis_adi if tesis_adi else 'Bilinmeyen Olay',
            "sektor": item.get('sektor', ''),
            "etkiSeviyesi": item.get('etkiSeviyesi', 'Düşük'),
            "yananAlanHa": 0,
            "insaniEtki": "Belirtilmedi",
            "maddiEtki": item.get('etki', ''),
            "lat": item.get('lat', 0),
            "lng": item.get('lng', 0),
            "geometri": "Nokta",
            "dogrulamaYontemi": item.get('dogrulamaYontemi', 'B'),
            "dogrulukOrani": item.get('dogrulukOrani', 90),
            "ozet": item.get('ozet', ''),
            "kaynaklar": []
        }
        
        # Kaynakları dönüştür
        if 'kaynaklar' in item and isinstance(item['kaynaklar'], dict):
            for kaynak_adi, url in item['kaynaklar'].items():
                incident["kaynaklar"].append({
                    "kaynak": kaynak_adi,
                    "alinti": url
                })
        
        incidents.append(incident)
    
    return incidents, unknown_incidents

try:
    # Dosya yollarını düzelt
    current_dir = os.path.dirname(__file__)
    parent_dir = os.path.dirname(current_dir)
    
    json_folder = os.path.join(parent_dir, 'Hasarlar_v2 JSON Format')
    html_file_path = os.path.join(current_dir, 'cat_loss.html')
    
    # JSON verilerini yükle
    if not os.path.exists(json_folder):
        st.error(f"JSON klasörü bulunamadı: {json_folder}")
        st.info("Beklenen konum: app.py ile aynı dizinde 'Hasarlar_v2 JSON FORMAT' klasörü")
    else:
        json_data = load_json_data(json_folder)
        
        if not json_data:
            st.error("JSON klasöründe veri bulunamadı!")
        else:
            st.success(f"✅ {len(json_data)} adet olay verisi yüklendi")
            
            # Verileri incidents formatına dönüştür
            incidents_data, unknown_incidents = convert_to_incident_format(json_data)
            
            # Bilinmeyen olayları göster
            if unknown_incidents:
                with st.expander(f"⚠️ {len(unknown_incidents)} adet 'Bilinmeyen Olay' tespit edildi - Detayları görmek için tıklayın"):
                    # Dosyaya göre grupla
                    from collections import defaultdict
                    grouped = defaultdict(list)
                    for item in unknown_incidents:
                        grouped[item['dosya']].append(item)
                    
                    for dosya, items in grouped.items():
                        st.subheader(f"📄 {dosya} ({len(items)} adet)")
                        for item in items:
                            st.write(f"- **ID:** {item['id']} | **Tarih:** {item['tarih']} | **Konum:** {item['il']}/{item['ilce']} - {item['konum']} | **Sektör:** {item['sektor']}")
                        st.divider()
            
            # HTML dosyasını oku
            if not os.path.exists(html_file_path):
                st.error(f"HTML dosyası bulunamadı: {html_file_path}")
            else:
                with open(html_file_path, 'r', encoding='utf-8') as f:
                    html_content = f.read()
                
                # JavaScript veri dizisini oluştur
                incidents_js = json.dumps(incidents_data, ensure_ascii=False, indent=4)
                
                # HTML içindeki sabit veri dizisini dinamik verilerle değiştir
                import re
                pattern = r'const incidentsData = \[.*?\];'
                replacement = f'const incidentsData = {incidents_js};'
                html_content = re.sub(pattern, replacement, html_content, flags=re.DOTALL)
                
                # HTML'i render et
                components.html(html_content, height=900, scrolling=True)
        
except FileNotFoundError as e:
    st.error(f"Dosya bulunamadı: {str(e)}")
    st.info(f"Aranan konum: {e.filename if hasattr(e, 'filename') else 'bilinmiyor'}")
except Exception as e:
    st.error(f"Bir hata oluştu: {str(e)}")
    st.exception(e)