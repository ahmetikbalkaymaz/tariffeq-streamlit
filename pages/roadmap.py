import streamlit as st
from translations import T
from pages.sidebar import sidebar

# --- Sayfa Konfigürasyonu ---
st.set_page_config(
    page_title="Yol Haritası",
    page_icon="🚀",
    layout="wide",
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

sidebar()

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

st.markdown("---")
st.markdown(f"""
<div style='text-align: center; font-size: 0.9em; color: #666; padding: 10px; background-color: #f8f9fa; border-radius: 5px; margin-top: 20px;'>
    ⚠️ <strong>{tr('disclaimer_title')}:</strong> {tr('disclaimer_text')}
</div>
""", unsafe_allow_html=True)

# Footer
st.markdown(f"<div class='footer'>{T['footer'][lang]}</div>", unsafe_allow_html=True)