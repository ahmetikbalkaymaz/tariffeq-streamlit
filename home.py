import streamlit as st

# Sayfa Ayarları (en üstte olmalı)
st.set_page_config(
    page_title="TariffEQ – Smart Insurance Calculator",
    layout="wide",
    page_icon="📊"
)

# Dil seçimi için session state başlatma (EĞER YOKSA)
if 'lang' not in st.session_state:
    st.session_state.lang = "TR"  # Varsayılan dil

# Dil değişkenini session state'den al
lang = st.session_state.lang

# Dil seçimi (en üstte) - BU SATIRI SİLİN VEYA YORUM SATIRI YAPIN
# lang = st.radio("Language / Dil", ["TR", "EN"], index=0, horizontal=True)

# Çeviri sözlüğü
T = {
    "title": {"TR": "TariffEQ", "EN": "TariffEQ"},
    "subtitle": {
        "TR": "Deprem Teminatı için Hızlı ve Güvenilir Prim Hesaplama",
        "EN": "Fast & Reliable Premium Calculation for Earthquake Cover"
    },
    "desc": {
        "TR": "Karmaşık sigorta tarifelerini unutun. Güncel mevzuata %100 uyumlu, teknik olarak doğru prim hesaplaması artık sadece birkaç tık uzağınızda!",
        "EN": "Forget about complicated insurance tariffs. 100% compliant with current regulations, technically accurate premium calculation is just a few clicks away!"
    },
    "why": {"TR": "Nasıl Çalışır?", "EN": "How It Works?"},
    "feature1": {"TR": "Hesaplama Türünü Seçin", "EN": "Select the Calculation Type"},
    "feature2": {"TR": "Teminat ve Risk Bilgilerinizi Girin", "EN": "Enter Your Coverage and Risk Details"},
    "feature3": {"TR": "Minimum Deprem Primi Tutarını Hemen Öğrenin", "EN": "Instantly Get the Minimum Earthquake Premium"},
    "founders": {"TR": "Geliştiriciler", "EN": "Developers"},
    "contact": {
        "TR": "Sorularınız için bize info@tariffeq.com adresinden ulaşabilirsiniz.",
        "EN": "For inquiries, contact us at info@tariffeq.com"
    },
    "footer": {
        "TR": "©️ 2025 TariffEQ. Tüm Hakları Saklıdır.",
        "EN": "©️ 2025 TariffEQ. All rights reserved."
    },
    "comment": {"TR": "Yorum Bırak", "EN": "Leave a Comment"},
    "comment_placeholder": {"TR": "Yorumunuzu buraya yazın...", "EN": "Write your comment here..."},
    "submit": {"TR": "Gönder", "EN": "Submit"},
    "home": {"TR": "Ana Sayfa", "EN": "Home"},
    "calc": {"TR": "🚀 Hemen Hesapla", "EN": "🚀 Calculate Now"},
    "featured_features_header": {"TR": "Öne Çıkan Özellikler", "EN": "Featured Features"},
    "feature_fast": {"TR": "Hızlı ve Kolay Kullanım: 30 saniyede teklif alın", "EN": "Fast & Easy to Use: Get a quote in 30 seconds"},
    "feature_accurate": {"TR": "Teknik Doğruluk: Resmi deprem tarifesine tam uyum", "EN": "Technical Accuracy: Full compliance with the official earthquake tariff"},
    "feature_currency": {"TR": "Döviz Desteği: TRY, USD, EUR ile anında hesaplama", "EN": "Currency Support: Instant calculation with TRY, USD, EUR"},
    "feature_multilocation": {"TR": "Çoklu Lokasyon: Birden fazla işyeri/şantiye için tek ekranda hesaplama", "EN": "Multi-Location: Calculation for multiple workplaces/sites on a single screen"},
    "feature_coinsurance": {"TR": "Koasürans & Muafiyet: Tüm teknik indirim ve ek primler otomatik hesaplansın", "EN": "Coinsurance & Deductible: All technical discounts and additional premiums are calculated automatically"},
    "who_is_it_for_header": {"TR": "👥 Kimler İçin?", "EN": "👥 Who Is It For?"},
    "target_insurers": {"TR": "🏢 Sigorta şirketi ekipleri ve underwriterlar", "EN": "🏢 Insurance company teams and underwriters"},
    "target_brokers": {"TR": "🤝 Brokerlar, acenteler", "EN": "🤝 Brokers, agents"},
    "target_professionals": {"TR": "⏱️ Hızlı teklif hazırlamak isteyen sigorta profesyonelleri", "EN": "⏱️ Insurance professionals who want to prepare quick quotes"},
    "target_owners": {"TR": "🏗️ Proje sahipleri ve işletme yöneticileri", "EN": "🏗️ Project owners and business managers"}
}

# Özel CSS (Navigasyon butonlarını gizle ve özel navigasyon için stil)
st.markdown("""
<style>
    /* Streamlit'in varsayılan navigasyon menüsünü gizle - BU SATIRI SİLİN VEYA YORUM SATIRI YAPIN */
    /* [data-testid="stSidebarNav"] {
        display: none;
    } */

    /* Sidebar arka plan rengi */
    [data-testid="stSidebar"] {
        background: #edf7fa;
        display: flex; /* Sidebar'ı da flex container yap */
        flex-direction: column; /* İçeriği dikey sırala */
    }

    /* Kenar çubuğu içindeki ana içerik alanını flex container yap */
    /* Bu seçici Streamlit versiyonlarına göre değişebilir, gerekirse daha spesifik hale getirin */
    [data-testid="stSidebar"] > div:first-child {
        display: flex;
        flex-direction: column;
        flex-grow: 1; /* Bu container'ın mevcut tüm boş alanı doldurmasını sağla */
        /* height: 100%;  Bu satırı flex-grow ile değiştirebilir veya kaldırabilirsiniz */
    }

    /* Kenar çubuğundaki footer için özel stil */
    .sidebar-footer {
        margin-top: auto !important; /* Footer'ı flex container'ın en altına it */
        padding-bottom: 1em; /* Altbilginin en altta biraz boşluğu olması için (opsiyonel) */
        width: 100%; /* Genişliğin tamamını kaplamasını sağla (opsiyonel) */
        /* Diğer .footer stilleri (text-align, font-size, padding-top, border-top vb.)
           <div class='sidebar-footer footer'> kullanıldığı için miras alınacaktır. */
    }

    .header img {
        max-height: 400px;
        margin-bottom: 1em;
        border-radius: 8px;
    }
    /* .header h1 bölümü güncellenecek veya genel h1 kuralı kullanılacak */
    /* .header h1 {
        font-size: 3.2em;
        color: #2E86C1; // Bu satır kaldırılacak veya yorumlanacak
        margin-bottom: 0.2em;
        font-weight: 700;
    } */
    .header h1 { /* Font boyutu ve diğer stiller kalabilir, renk genel kuraldan gelecek */
        font-size: 3.2em;
        margin-bottom: 0.2em;
        font-weight: 700;
        white-space: nowrap; /* Başlığın alt satıra kaymasını engeller */
    }

    /* .header h3 bölümü güncellenecek veya genel h3 kuralı kullanılacak */
    /* .header h3 {
        color: #5DADE2; // Bu satır kaldırılacak veya yorum satırı yapılacak
        font-weight: 400;
        font-size: 1.5em;
    } */
    .header h3 { /* Font boyutu ve diğer stiller kalabilir, renk genel kuraldan gelecek */
        color: #5DADE2 !important; /* Alt başlık rengi eklendi */
        font-weight: 400;
        font-size: 1.5em;
    }

    .tariff-part {
        color: #2E86C1 !important;
        font-weight: bold; /* calculate.py ile uyumlu */
    }
    .eq-part {
        color: #5DADE2 !important;
        font-weight: bold; /* calculate.py ile uyumlu */
    }

    /* Tüm başlık seviyeleri için genel renk tanımı */
    h1, h2, h3, h4, h5, h6 {
        color: black !important;
    }

    .card {
        background: linear-gradient(135deg, #F0F4FA 0%, #E0E7FF 100%);
        padding: 1.5em;
        border-radius: 12px;
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.05);
        text-align: center;
        margin-bottom: 1em;
        transition: transform 0.3s ease;
        font-size: 1.1em; /* Yazı boyutunu biraz büyütmek için eklendi */
    }
    .card:hover {
        transform: translateY(-5px);
    }
    .footer {
        text-align: center;
        font-size: 0.9em;
        color: #64748B;
        margin-top: 2em;
        padding-top: 1em;
        border-top: 1px solid #E0E7FF;
    }
    .nav-buttons {
        display: flex;
        gap: 10px;
        margin-bottom: 1em;
    }
    .nav-buttons button {
        background-color: #2E86C1;
        color: white;
        border-radius: 8px;
        padding: 0.5em 1em;
        border: none;
        cursor: pointer;
        transition: background-color 0.3s ease;
    }
    .nav-buttons button:hover {
        background-color: #1A5276;
    }
    /* Başlıklardaki çapa ikonlarını gizle */
    h1 a, h2 a, h3 a, h4 a, h5 a, h6 a {
        display: none !important;
    }
</style>
""", unsafe_allow_html=True)

# Kenar Çubuğu Navigasyonu
with st.sidebar:
    st.image("assets/logo.png", width=1000)
    st.page_link("home.py", label=T["home"][st.session_state.lang], icon="🏠")
    st.page_link("pages/calculate.py", label=T["calc"][st.session_state.lang]) # Navigasyon için session_state.lang kullanın
    
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

title_html = """
<span class="tariff-part">Tariff</span><span class="eq-part">EQ</span>
"""

st.markdown(f"""
<div class="header">
    <h1>{title_html}</h1>
    <h3><strong>{T["subtitle"][lang]}</strong></h3>
</div>
""", unsafe_allow_html=True)

# Açıklama ve Başlat Butonu
st.markdown(f"*{T['desc'][lang]}*") # Sadece italik, başlık (####) kaldırıldı

# YENİ: Hemen Hesapla Butonu
if st.button(T["calc"][lang], use_container_width=True, type="primary"):
    st.switch_page("pages/calculate.py")

st.markdown("---") # Buton ile sonraki bölüm arasına bir ayırıcı

# Neden TariffEQ
st.markdown(f"### {T['why'][lang]}")
col1, col2, col3 = st.columns(3)
with col1:
    st.markdown(f"<div class='card'>📝 <strong>{T['feature1'][lang]}</strong></div>", unsafe_allow_html=True)
with col2:
    st.markdown(f"<div class='card'>🛡️ <strong>{T['feature2'][lang]}</strong></div>", unsafe_allow_html=True)
with col3:
    st.markdown(f"<div class='card'>💰 <strong>{T['feature3'][lang]}</strong></div>", unsafe_allow_html=True)

# Öne Çıkan Özellikler
st.markdown(f"### {T['featured_features_header'][lang]}")
ff_col1, ff_col2, ff_col3, ff_col4 = st.columns(4)

# feature_fast
text_fast = T['feature_fast'][lang]
parts_fast = text_fast.split(':', 1)
html_fast = f"⚡ <strong>{parts_fast[0]}:</strong> {parts_fast[1].strip()}" if len(parts_fast) == 2 else f"⚡ <strong>{text_fast}</strong>"
with ff_col1:
    st.markdown(f"<div class='card'>{html_fast}</div>", unsafe_allow_html=True)

# feature_accurate
text_accurate = T['feature_accurate'][lang]
parts_accurate = text_accurate.split(':', 1)
html_accurate = f"📐 <strong>{parts_accurate[0]}:</strong> {parts_accurate[1].strip()}" if len(parts_accurate) == 2 else f"📐 <strong>{text_accurate}</strong>"
with ff_col2:
    st.markdown(f"<div class='card'>{html_accurate}</div>", unsafe_allow_html=True)

# feature_currency
text_currency = T['feature_currency'][lang]
parts_currency = text_currency.split(':', 1)
html_currency = f"🌎 <strong>{parts_currency[0]}:</strong> {parts_currency[1].strip()}" if len(parts_currency) == 2 else f"🌎 <strong>{text_currency}</strong>"
with ff_col3:
    st.markdown(f"<div class='card'>{html_currency}</div>", unsafe_allow_html=True)

# feature_multilocation
text_multilocation = T['feature_multilocation'][lang]
parts_multilocation = text_multilocation.split(':', 1)
html_multilocation = f"🏢 <strong>{parts_multilocation[0]}:</strong> {parts_multilocation[1].strip()}" if len(parts_multilocation) == 2 else f"🏢 <strong>{text_multilocation}</strong>"
with ff_col4:
    st.markdown(f"<div class='card'>{html_multilocation}</div>", unsafe_allow_html=True)

# Kimler İçin?
st.markdown(f"### {T['who_is_it_for_header'][lang]}")
wif_col1, wif_col2, wif_col3, wif_col4 = st.columns(4)
with wif_col1:
    st.markdown(f"<div class='card'><strong>{T['target_insurers'][lang]}</strong></div>", unsafe_allow_html=True)
with wif_col2:
    st.markdown(f"<div class='card'><strong>{T['target_brokers'][lang]}</strong></div>", unsafe_allow_html=True)
with wif_col3:
    st.markdown(f"<div class='card'><strong>{T['target_professionals'][lang]}</strong></div>", unsafe_allow_html=True)
with wif_col4:
    st.markdown(f"<div class='card'><strong>{T['target_owners'][lang]}</strong></div>", unsafe_allow_html=True)
st.markdown("---") # Bir sonraki bölümden ayırmak için opsiyonel ayırıcı

# Kurucular
st.markdown(f"### {T['founders'][lang]}")
f1, f2 = st.columns(2)

# LinkedIn Logo SVG (basit bir versiyon)
linkedin_logo_svg = """
<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="currentColor">
  <path d="M19 0h-14c-2.761 0-5 2.239-5 5v14c0 2.761 2.239 5 5 5h14c2.762 0 5-2.239 5-5v-14c0-2.761-2.238-5-5-5zm-11 19h-3v-11h3v11zm-1.5-12.268c-.966 0-1.75-.79-1.75-1.764s.784-1.764 1.75-1.764 1.75.79 1.75 1.764-.783 1.764-1.75 1.764zm13.5 12.268h-3v-5.604c0-3.368-4-3.113-4 0v5.604h-3v-11h3v1.765c1.396-2.586 7-2.777 7 2.476v6.759z"/>
</svg>
"""

with f1:
    st.markdown(f"""
    <div style="text-align: center;">
        <img src="https://i.imgur.com/d0JoyE1.jpeg" alt="Osman Furkan Kaymaz" style="width: 150px; height: auto; border-radius: 8px; margin-bottom: 10px;">
        <p style="margin-bottom: 5px;"><strong>Osman Furkan Kaymaz</strong><br>Broker</p>
        <a href='https://www.linkedin.com/in/furkan-kaymaz-97736718b/' target='_blank' title="Osman Furkan Kaymaz LinkedIn'de">
            {linkedin_logo_svg}</a>
    </div>
    """, unsafe_allow_html=True)

with f2:
    st.markdown(f"""
    <div style="text-align: center;">
        <img src="https://i.ibb.co/K3ysQ1x/ubeydullah.jpg" alt="Ubeydullah Ayvaz" style="width: 150px; height: auto; border-radius: 8px; margin-bottom: 10px;">
        <p style="margin-bottom: 5px;"><strong>Ubeydullah Ayvaz</strong><br>Underwriter</p>
        <a href='https://www.linkedin.com/in/ubeydullah-ayvaz-762269143/' target='_blank' title="Ubeydullah Ayvaz LinkedIn'de">
            {linkedin_logo_svg}</a>
    </div>
    """, unsafe_allow_html=True)

# Yorum Kutusu
st.markdown(f"### {T['comment'][lang]}")
comment = st.text_area(label="", placeholder=T['comment_placeholder'][lang], height=100)
if st.button(T['submit'][lang]):
    if comment.strip():
        st.success("Teşekkürler, yorumunuz alınmıştır.")
    else:
        st.warning("Lütfen boş yorum göndermeyiniz.")