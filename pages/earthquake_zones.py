import streamlit as st
from translations import T
import pandas as pd
from pathlib import Path  # Dosyanın en üstüne ekleyin
import os
from datetime import datetime
from utils.visitor_logger import track_page_visit, log_page_exit
from pages.sidebar import sidebar  # Kenar çubuğu fonksiyonunu içe aktar

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
        border-radius: 10px;
        padding: 0.5em 1em;
    }
    .stButton>button:hover {
        background-color: #1A5276;
        color: white;
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
    st.session_state.lang = "TR" # Varsayılan dil
lang = st.session_state.lang

def tr(key: str, **kwargs) -> str:
    translation = T.get(key, {}).get(lang, key)
    if kwargs:
        return translation.format(**kwargs)
    return translation

sidebar()

# Sayfa ziyaretini takip et
track_page_visit("Earthquake_Zones")

# Önceki sayfadan çıkışı logla
if 'previous_page' in st.session_state and st.session_state.previous_page != "Earthquake_Zones":
    log_page_exit(st.session_state.previous_page)

st.session_state.previous_page = "Earthquake_Zones" # Geçerli sayfayı önceki sayfa olarak kaydet

# Veriyi önbelleğe alarak yükleyen fonksiyon
@st.cache_data
def load_data():
    excel_path = Path(__file__).parent.parent / "files" / "deprem.xlsx"
    df = pd.read_excel(excel_path, sheet_name="Veri")
    df = df[["ILADI", "ILCEADI", "KOYADI", "MAHADI", "Yeni Sınıf"]].dropna()
    return df

# Veriyi yükle
df = load_data()

st.title(T["earthquake_zones_search"][st.session_state.lang], anchor=False)

# 1. İl Seçimi
# İl seçeneklerini bir kere hesaplayıp saklayabiliriz, ancak selectbox zaten dinamik olarak güncellenecek.
# Sıralama işlemini de burada yapabiliriz.
il_options = sorted(df["ILADI"].unique())
selected_il = st.selectbox(T["select_province"][st.session_state.lang], il_options,index=None)

# 2. İlçe Seçimi
if selected_il:
    ilce_options = sorted(df[df["ILADI"] == selected_il]["ILCEADI"].unique())
    selected_ilce = st.selectbox(T["select_district"][st.session_state.lang], ilce_options,index=None)
else:
    selected_ilce = None # Veya boş bir liste ile selectbox'ı devre dışı bırak

# 3. Köy/Bucak Seçimi
if selected_il and selected_ilce:
    koy_options = sorted(df[(df["ILADI"] == selected_il) & (df["ILCEADI"] == selected_ilce)]["KOYADI"].unique())
    selected_koy = st.selectbox(T["select_village"][st.session_state.lang], koy_options, index=None)
else:
    selected_koy = None

# 4. Mahalle Seçimi
if selected_il and selected_ilce and selected_koy:
    mah_options = sorted(df[
        (df["ILADI"] == selected_il) &
        (df["ILCEADI"] == selected_ilce) &
        (df["KOYADI"] == selected_koy)
    ]["MAHADI"].unique())
    selected_mah = st.selectbox(T["select_neighborhood"][st.session_state.lang], mah_options,index=None)
else:
    selected_mah = None

# 5. Deprem Bölgesi (Yeni Sınıf)
if selected_il and selected_ilce and selected_koy and selected_mah:
    result_df = df[
        (df["ILADI"] == selected_il) &
        (df["ILCEADI"] == selected_ilce) &
        (df["KOYADI"] == selected_koy) &
        (df["MAHADI"] == selected_mah)
    ]
    if not result_df.empty:
        # f-string kullanarak düzeltme
        deprem_sinifi = result_df['Yeni Sınıf'].values[0]
        st.success(f"{T['earthquake_zones_result'][st.session_state.lang]} {deprem_sinifi}")
        
        # Deprem bölgesi açıklaması
        st.markdown("---") # Sonuç ile açıklama arasına bir ayırıcı
        st.markdown(f"#### {T['earthquake_zone_explanation_header'][st.session_state.lang]}")
        st.markdown(T['earthquake_zone_explanation_text'][st.session_state.lang])
    else:
        st.warning(T["no_data_found"][st.session_state.lang]) # Yeni çeviri anahtarı
elif selected_il: # Eğer sadece il seçilmişse veya diğer seçimler henüz yapılmamışsa bir mesaj gösterme
    pass # Veya "Lütfen tüm seçimleri yapınız" gibi bir uyarı eklenebilir.
else:
    st.info(T["start_selection"][st.session_state.lang]) # Yeni çeviri anahtarı


st.divider()
# --- YENİ EKLENEN BÖLÜM ---

col1, col2 = st.columns([1, 1])

with col1:
    # Başlık
    st.subheader(tr("fire_section_title"), anchor=False)
    st.image("files/earthquake-2.jpeg")
    st.caption(tr("sddk_reference_text_fire"))

with col2:
    st.subheader(tr("car_section_title"), anchor=False)
    st.image("files/earthquake.jpeg")
    st.caption(tr("sddk_reference_text_car"))


st.markdown("---")
st.markdown(f"""
<div style='text-align: center; font-size: 0.9em; color: #666; padding: 10px; background-color: #f8f9fa; border-radius: 5px; margin-top: 20px;'>
    ⚠️ <strong>{tr('disclaimer_title')}:</strong> {tr('disclaimer_text')}
</div>
""", unsafe_allow_html=True)

# Footer
st.markdown(f"<div class='footer'>{T['footer'][lang]}</div>", unsafe_allow_html=True)