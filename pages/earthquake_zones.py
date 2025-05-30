import streamlit as st
from translations import T
import pandas as pd

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


with st.sidebar:
    st.image("assets/logo.png", width=1000) # width=1000 logonuz büyükse küçültün, örneğin 200
    st.page_link("home.py", label=T["home"][st.session_state.lang], icon="🏠")
    st.page_link("pages/calculate.py", label=T["calc"][st.session_state.lang]) # "calc" yerine farklı bir anahtar kullanmak daha iyi olabilir
    st.page_link("pages/earthquake_zones.py", label=T["earthquake_zones_nav"][st.session_state.lang]) # YENİ SAYFA LİNKİ
    st.page_link("pages/scenario_calculator_page.py", label=tr("scenario_page_title"), icon="📉") # Mevcut sayfa
    st.markdown("---") # Ayırıcı

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



# Veriyi önbelleğe alarak yükleyen fonksiyon
@st.cache_data
def load_data():
    df = pd.read_excel("files/Deprem Bölgesi Bulma-Tariffeq.xlsx", sheet_name="Veri")
    df = df[["ILADI", "ILCEADI", "KOYADI", "MAHADI", "Yeni Sınıf"]].dropna()
    return df

# Veriyi yükle
df = load_data()

st.title(T["earthquake_zones_search"][st.session_state.lang], anchor=False)

# 1. İl Seçimi
# İl seçeneklerini bir kere hesaplayıp saklayabiliriz, ancak selectbox zaten dinamik olarak güncellenecek.
# Sıralama işlemini de burada yapabiliriz.
il_options = sorted(df["ILADI"].unique())
selected_il = st.selectbox(T["select_province"][st.session_state.lang], il_options)

# 2. İlçe Seçimi
if selected_il:
    ilce_options = sorted(df[df["ILADI"] == selected_il]["ILCEADI"].unique())
    selected_ilce = st.selectbox(T["select_district"][st.session_state.lang], ilce_options)
else:
    selected_ilce = None # Veya boş bir liste ile selectbox'ı devre dışı bırak

# 3. Köy/Bucak Seçimi
if selected_il and selected_ilce:
    koy_options = sorted(df[(df["ILADI"] == selected_il) & (df["ILCEADI"] == selected_ilce)]["KOYADI"].unique())
    selected_koy = st.selectbox(T["select_village"][st.session_state.lang], koy_options)
else:
    selected_koy = None

# 4. Mahalle Seçimi
if selected_il and selected_ilce and selected_koy:
    mah_options = sorted(df[
        (df["ILADI"] == selected_il) &
        (df["ILCEADI"] == selected_ilce) &
        (df["KOYADI"] == selected_koy)
    ]["MAHADI"].unique())
    selected_mah = st.selectbox(T["select_neighborhood"][st.session_state.lang], mah_options)
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
    else:
        st.warning(T["no_data_found"][st.session_state.lang]) # Yeni çeviri anahtarı
elif selected_il: # Eğer sadece il seçilmişse veya diğer seçimler henüz yapılmamışsa bir mesaj gösterme
    pass # Veya "Lütfen tüm seçimleri yapınız" gibi bir uyarı eklenebilir.
else:
    st.info(T["start_selection"][st.session_state.lang]) # Yeni çeviri anahtarı