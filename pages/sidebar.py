import streamlit as st
from translations import T 

def sidebar():
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

    /* Genel footer stili (home.py'den alındı) */
    .footer {
        text-align: center;
        font-size: 0.9em;
        color: #64748B; /* home.py ile tutarlı renk */
        padding-top: 1em; /* .sidebar-footer'daki margin-top:auto bunu etkilemeyecek */
        /* border-top: 1px solid #E0E7FF;  Kenar çubuğunda bu kenarlık gerekmeyebilir, isteğe bağlı */
    }

    .main-title {
        font-size: 2.5em;
        /* color: #2E86C1 !important; */ /* Kaldırıldı - h1 için genel siyah kuralı uygulanacak */
        margin-bottom: 0.5em;
        display: flex;
        flex-direction: column; /* Öğeleri dikey olarak sırala */
        align-items: center;   /* Öğeleri yatayda ortala */
        justify-content: center;
        /* white-space: nowrap;  Bu satır kaldırıldı */
    }
    .main-title > span:first-child { /* "TariffEQ" kısmının kaymasını engelle */
        white-space: nowrap;
    }
    .main-title img {
        height: 1em; /* Ana başlık yazı boyutuna göre ölçeklenir */
        margin-right: 0.25em;
    }
    .tariff-part {
        color: #2E86C1 !important;
        font-weight: bold; /* İsteğe bağlı: daha belirgin yapmak için */
    }
    .eq-part {
        color: #5DADE2 !important;
        font-weight: bold; /* İsteğe bağlı: daha belirgin yapmak için */
    }
    .subtitle {
        font-size: 1.2em;
        color: #5DADE2; /* Bu bir başlık değil, rengi korunuyor */
        text-align: center;
        margin-bottom: 0.5em;
    }
    .founders {
        font-size: 1em;
        color: #1A5276; /* Bu bir başlık değil, rengi korunuyor */
        text-align: center;
        margin-bottom: 1em;
    }
    .section-header {
        font-size: 1.5em;
        /* color: #2E86C1 !important; */ /* Kaldırıldı - h2,h3 için genel siyah kuralı uygulanacak */
        margin-top: 1em;
        margin-bottom: 0.5em;
    }

    /* Tüm başlık seviyeleri için genel renk tanımı */
    h1, h2, h3, h4, h5, h6 {
        color: black !important;
    }

    .stButton>button {
        background-color: #2E86C1;
        color: white;
        border-radius: 10px; /* Streamlit butonlarının varsayılan border-radius'u daha az olabilir, 10px sizin tercihiniz */
        padding: 0.5em 1em;
        border: none; /* Streamlit butonlarında genellikle border olmaz */
        cursor: pointer;
    }
    .stButton>button:hover {
        background-color: #1A5276;
        color: white;
    }

    /* Linki butona benzetmek için yeni sınıf */
    a.styled-link-button {
        display: inline-block; /* veya block, eğer tam genişlik isteniyorsa */
        padding: 0.5em 1em;
        background-color: #2E86C1; /* Ana buton renginiz */
        color: white !important; /* !important, <a> etiketinin varsayılan rengini geçersiz kılmak için */
        text-decoration: none;
        border-radius: 10px; /* .stButton>button ile aynı */
        text-align: center;
        border: none;
        cursor: pointer;
        width: 100%; /* use_container_width=True etkisi */
        box-sizing: border-box;
    }
    a.styled-link-button:hover {
        background-color: #1A5276; /* Hover rengi */
        color: white !important;
    }

    .info-box {
        background-color: #F0F8FF;
        padding: 1em;
        border-radius: 10px;
        margin-bottom: 1em;
    }
    /* Başlıklardaki çapa ikonlarını gizle */
    h1 a, h2 a, h3 a, h4 a, h5 a, h6 a {
        display: none !important;
    }
</style>
""", unsafe_allow_html=True)

    if 'lang' not in st.session_state:
        st.session_state.lang = 'tr'
    with st.sidebar:
        st.image("assets/logo.png", width=1000) 
        st.page_link("home.py", label=T["home"][st.session_state.lang], icon="🏠")
        st.page_link("pages/calculate.py", label=T["calc"][st.session_state.lang]) 
        st.page_link("pages/earthquake_zones.py", label=T["earthquake_zones_nav"][st.session_state.lang]) 
        st.page_link("pages/information.py", label=T["information_page_nav"][st.session_state.lang]) # BİLGİLENDİRME SAYFASI LİNKİ
        # st.page_link("pages/roadmap.py", label=T["roadmap_page_nav"][st.session_state.lang], icon="🚀") # YOL HARİTASI SAYFASI LİNKİ
        st.page_link("pages/locate_loss.py", label=T["locate_loss_page_nav"][st.session_state.lang], icon="📍")
        st.page_link("pages/cat_locate_loss.py", label=T["cat_locate_loss_page_nav"][st.session_state.lang], icon="🔥")
        st.page_link("pages/loss_analysis.py", label=T["loss_analysis_page_nav"][st.session_state.lang], icon="🔥")
        st.page_link("pages/foresight.py", label=T["foresight_page_nav"][st.session_state.lang], icon="🔥")
        # st.page_link("pages/scenario_calculator_page.py", label=T["scenario_page_title"][st.session_state.lang], icon="📉") 
        st.markdown("---") 

        lang_options = ["TR", "EN"]
        if st.session_state.lang not in lang_options:
            st.session_state.lang = "TR" 

        current_lang_index = lang_options.index(st.session_state.lang)
        
        selected_lang_sidebar = st.radio(
            "Language / Dil", 
            options=lang_options, 
            index=current_lang_index, 
            key="sidebar_language_selector" 
        )

        if selected_lang_sidebar != st.session_state.lang:
            st.session_state.lang = selected_lang_sidebar
            st.rerun() 
        
        st.markdown("---") 
        st.markdown(f"<div class='sidebar-footer footer'>{T['footer'][st.session_state.lang]}</div>", unsafe_allow_html=True)