import streamlit as st
from translations import T

# --- Sayfa Konfigürasyonu ---
st.set_page_config(
    page_title="Yol Haritası",
    page_icon="🚀"
)

if 'lang' not in st.session_state:
    st.session_state.lang = "TR"  # Varsayılan dil

# Dil değişkenini session state'den al
lang = st.session_state.lang

def tr(key: str) -> str:
    # `T` sözlüğünüzde "location_name" ve "location_name_help" anahtarlarını eklemeyi unutmayın.
    # Örnek:
    # "location_name": {"TR": "Lokasyon Adı / Adresi", "EN": "Location Name / Address"},
    # "location_name_help": {"TR": "Bu lokasyon için tanımlayıcı bir isim veya adres girin.", "EN": "Enter a descriptive name or address for this location."},
    return T.get(key, {}).get(lang, key)

st.markdown("""
<style>
    [data-testid="stSidebar"] {
        background-color: #edf7fa; /* Mevcut arka plan rengi korunuyor */
        display: flex; /* Sidebar'ı da flex container yap */
        flex-direction: column; /* İçeriği dikey sırala */
    }
    /* Kenar çubuğu içindeki ana içerik alanını flex container yap */
    [data-testid="stSidebar"] > div:first-child {
        display: flex;
        flex-direction: column;
        flex-grow: 1; /* Bu container'ın mevcut tüm boş alanı doldurmasını sağla */
    }

    /* Kenar çubuğundaki footer için özel stil */
    .sidebar-footer {
        margin-top: auto !important; /* Footer'ı flex container'ın en altına it */
        padding-bottom: 1em; /* Altbilginin en altta biraz boşluğu olması için (opsiyonel) */
        width: 100%; /* Genişliğin tamamını kaplamasını sağla (opsiyonel) */
    }
        </style>
""", unsafe_allow_html=True)

with st.sidebar:
    st.image("assets/logo.png", width=1000) 
    st.page_link("home.py", label=T["home"][st.session_state.lang], icon="🏠")
    st.page_link("pages/calculate.py", label=T["calc"][st.session_state.lang]) 
    st.page_link("pages/earthquake_zones.py", label=T["earthquake_zones_nav"][st.session_state.lang]) 
    st.page_link("pages/information.py", label=T["information_page_nav"][st.session_state.lang]) # BİLGİLENDİRME SAYFASI LİNKİ
    st.page_link("pages/roadmap.py", label=T["roadmap_page_nav"][st.session_state.lang], icon="🚀") # YOL HARİTASI SAYFASI LİNKİ
    # st.page_link("pages/scenario_calculator_page.py", label=T["scenario_page_title"][st.session_state.lang], icon="📉") 
    st.markdown("---") 

    # Dil seçimini kenar çubuğuna ekle
    lang_options = ["TR", "EN"]
    # st.session_state.lang'ın geçerli bir seçenek olduğundan emin olun
    if st.session_state.lang not in lang_options:
        st.session_state.lang = "TR" # Varsayılana sıfırla
        # Değişikliğin hemen yansıması için rerun gerekebilir, ancak bir sonraki etkileşimde düzelecektir.
        # İsterseniz st.rerun() satırını burada aktif edebilirsiniz.

    current_lang_index = lang_options.index(st.session_state.lang)
    
    selected_lang_sidebar = st.radio(
        "Language / Dil", 
        options=lang_options, 
        index=current_lang_index, 
        key="sidebar_language_selector" # Benzersiz bir anahtar
    )

    if selected_lang_sidebar != st.session_state.lang:
        st.session_state.lang = selected_lang_sidebar
        st.rerun() # Dil değiştiğinde uygulamayı yeniden çalıştır
    
    st.markdown("---") # Dil seçimi ile footer arasına bir ayırıcı daha eklenebilir (opsiyonel)
    st.markdown(f"<div class='sidebar-footer footer'>{T['footer'][lang]}</div>", unsafe_allow_html=True) # Footer buraya eklendi, sınıf güncellendi




# --- Sayfa İçeriği ---
st.markdown(f"<h2>🚀 {tr('roadmap_title')}</h2>", unsafe_allow_html=True)
st.markdown(f"**{tr('roadmap_subtitle')}**")
st.write(tr('roadmap_intro'))
st.markdown("---")

# AI Destekli Risk Analizi
st.markdown(f"<h3>🧠 {tr('ai_analysis_header')}</h3>", unsafe_allow_html=True)
st.write(tr('ai_analysis_desc'))
st.markdown(f"- 🔍 {tr('ai_analysis_item1')}")
st.markdown(f"- 📉 {tr('ai_analysis_item2')}")
st.markdown("---")

# Simülasyonlu Deprem Primi Hesabı
st.markdown(f"<h3>📊 {tr('simulation_header')}</h3>", unsafe_allow_html=True)
st.write(tr('simulation_desc'))
st.markdown(f"- {tr('simulation_item1')}")
st.markdown(f"- {tr('simulation_item2')}")
st.markdown("---")

# Optimum Limit Belirleme Aracı
st.markdown(f"<h3>🎯 {tr('limit_tool_header')}</h3>", unsafe_allow_html=True)
st.write(tr('limit_tool_desc'))
st.markdown(tr('limit_tool_item1'))
st.markdown("---")

# Çıktı & Raporlama Araçları
st.markdown(f"<h3>🧾 {tr('reporting_header')}</h3>", unsafe_allow_html=True)
st.write(tr('reporting_desc'))
st.markdown(f"- 📥 {tr('reporting_item1')}")
st.markdown(f"- 📬 {tr('reporting_item2')}")
st.markdown("---")

# Kurumsal Paketler
st.markdown(f"<h3>💼 {tr('corporate_header')}</h3>", unsafe_allow_html=True)
st.write(tr('corporate_desc'))
st.markdown(f"- {tr('corporate_item1')}")
st.markdown(f"- {tr('corporate_item2')}")
st.markdown(f"- {tr('corporate_item3')}")
st.markdown("---")

# Demo Sürüm Hakkında
st.markdown(f"<h3>🆓 {tr('demo_header')}</h3>", unsafe_allow_html=True)
st.write(tr('demo_desc1'))
st.markdown(f"📌 {tr('demo_desc2')}")
st.write(tr('demo_desc3'))
st.markdown("---")

st.markdown(f"**{tr('roadmap_conclusion')}**")