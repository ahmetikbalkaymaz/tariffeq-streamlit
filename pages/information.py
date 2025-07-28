import streamlit as st
import base64
from translations import T 

# Dil seçimi için session state kontrolü ve varsayılan atama
if 'lang' not in st.session_state:
    st.session_state.lang = "TR"
lang = st.session_state.lang

def tr(key: str, **kwargs) -> str:
    translation = T.get(key, {}).get(lang, key)
    if kwargs:
        return translation.format(**kwargs)
    return translation

# Sayfa yapılandırması
st.set_page_config(page_title="Bilgilendirme - TariffEQ", layout="wide", page_icon="ℹ️")

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
    st.markdown(f"<div class='sidebar-footer footer'>{T['footer'][lang]}</div>", unsafe_allow_html=True)


# Sayfa için çeviri sözlüğü
T_INFO = {
    "page_title": {
        "TR": "ℹ️ Bilgilendirme",
        "EN": "ℹ️ Legal Notice"
    },
    "general_info_header": {
        "TR": "⚖️ Genel Bilgilendirme",
        "EN": "⚖️ General Information"
    },
    "general_info_content": {
        "TR": """
        Bu platformda sunulan veriler ve hesaplamalar, SEDDK tarafından yayımlanan güncel İhtiyari Deprem Teminatı Tarifesi esas alınarak hazırlanmıştır.
        Tarife verileri, ticari ve sınai riskler için belirlenmiş resmî oranları yansıtmaktadır.
        Platformda hesaplanan primler, Deprem ve Yanardağ Püskürmesi Teminatı eklenmesi halinde uygulanacak minimum primi göstermektedir.
        """,
        "EN": """
        The data and calculations presented on this platform are based on the latest Voluntary Earthquake Insurance Tariff published by SEDDK.
        The tariff rates reflect official premium percentages determined for commercial and industrial risks.
        The platform calculates the minimum applicable premium for adding Earthquake and Volcanic Eruption Coverage.
        """
    },
    "disclaimer_header": {
        "TR": "🛑 Sorumluluk Reddi",
        "EN": "🛑 Disclaimer"
    },
    "disclaimer_content": {
        "TR": """
        - Platform, yalnızca deprem teminatı için teknik hesaplama sunar.
        - Platform üzerinden yapılan hesaplamalar, bağlayıcı teklif niteliği taşımaz.
        - Sigorta şirketleri, kendi analizleri doğrultusunda ilave risk primi uygulayabilir.
        - Platform, Zorunlu Deprem Sigortası (DASK) ve sivil rizikolar kapsamında hesaplama yapmamaktadır.
        """,
        "EN": """
        - This platform provides technical calculations for earthquake coverage only.
        - Calculations made on the platform do not constitute a binding offer.
        - Insurance companies may apply additional risk surcharges based on their own assessments.
        - The platform does not perform calculations for Compulsory Earthquake Insurance (DASK) or residential risks.
        """
    },
    "sources_header": {
        "TR": "📚 Kaynaklar",
        "EN": "📚 Sources"
    },
    "sources_content": {
        "TR": """
        - İhtiyari Deprem ve Yanardağ Püskürmesi Teminatı Tarife ve Talimatı, SEDDK – seddk.gov.tr
        - Türkiye Cumhuriyet Merkez Bankası (TCMB) – tcmb.gov.tr
        """,
        "EN": """
        - Voluntary Earthquake and Volcanic Eruption Insurance Tariff and Guidelines, SEDDK – seddk.gov.tr
        - Central Bank of the Republic of Türkiye (CBRT) – tcmb.gov.tr
        """
    },
    "notes_header": {
        "TR": "📌 Uygulama Notları",
        "EN": "📌 Application Notes"
    },
    "notes_content": {
        "TR": """
        - Hesaplanan prim, vergiler hariç net primdir.
        - Kar kaybı teminatı için koasürans muafiyetleri (%20–80 vb.) uygulanmaz; bunun yerine sabit süreli muafiyet uygulanır.
        - Kar kaybı hesaplamalarında tazminat süresi 12 ay olarak esas alınır.
        - Yapısal bağlantılı veya aynı parsel içinde yer alan iki yapı, kümül riziko olarak kabul edilir.
        - Dövizli poliçelerde kur bilgisi, TCMB kuru esas alınarak hesaplanır.
        """,
        "EN": """
        - Calculated premiums are net amounts excluding taxes.
        - For business interruption coverage, coinsurance deductibles (e.g., 20%–80%) are not applied; instead, a fixed waiting period is used.
        - The indemnity period for business interruption coverage is set at 12 months.
        - Two structures that are structurally connected or located within the same parcel are treated as a cumulative risk.
        - For FX-based policies, exchange rates are determined based on the CBRT exchange selling rate.
        """
    }
}

# Özel CSS
st.markdown("""
<style>
    /* Başlıklardaki çapa ikonlarını gizle */
    h1 a, h2 a, h3 a, h4 a, h5 a, h6 a {
        display: none !important;
    }
    .content-box {
        background-color: #f8f9fa;
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 5px solid #2E86C1;
        margin-bottom: 1.5rem;
    }
    h2 {

        padding-bottom: 0.5rem;
        margin-top: 1rem;
        margin-bottom: 1rem;
    }
    ul {
        list-style-position: inside;
        padding-left: 0;
    }
    li {
        margin-bottom: 0.5rem;
    }
</style>
""", unsafe_allow_html=True)

# Sayfa başlığı
st.header(T_INFO["page_title"][lang])

st.divider()

# Genel Bilgilendirme
# st.subheader(T_INFO["general_info_header"][lang])
st.markdown(T_INFO["general_info_content"][lang])

st.divider()

# Sorumluluk Reddi
st.subheader(T_INFO["disclaimer_header"][lang])
st.markdown(T_INFO["disclaimer_content"][lang])

st.divider()

# Kaynaklar
st.subheader(T_INFO["sources_header"][lang])
st.markdown(T_INFO["sources_content"][lang])

st.divider()

# Uygulama Notları
st.subheader(T_INFO["notes_header"][lang])
st.markdown(T_INFO["notes_content"][lang])


# Footer (home.py'den kopyalandı)
footer_text = {
    "TR": "©️ 2025 TariffEQ. Tüm Hakları Saklıdır.",
    "EN": "©️ 2025 TariffEQ. All rights reserved."
}
st.markdown(f"<div style='text-align: center; font-size: 0.9em; color: #64748B; margin-top: 2em; padding-top: 1em; border-top: 1px solid #E0E7FF;'>{footer_text[lang]}</div>", unsafe_allow_html=True)

st.markdown("---")
st.markdown(f"""
<div style='text-align: center; font-size: 0.9em; color: #666; padding: 10px; background-color: #f8f9fa; border-radius: 5px; margin-top: 20px;'>
    ⚠️ <strong>{tr('disclaimer_title')}:</strong> {tr('disclaimer_text')}
</div>
""", unsafe_allow_html=True)

# Footer
st.markdown(f"<div class='footer'>{T['footer'][lang]}</div>", unsafe_allow_html=True)