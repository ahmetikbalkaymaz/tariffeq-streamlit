import streamlit as st
import requests # requests kütüphanesini import edin (eğer daha önce eklenmediyse)

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
    "desc_highlight": {
        "TR": "Karmaşık sigorta tarifelerini unutun.",
        "EN": "Forget complex insurance tariffs."
    },
    "desc_main": {
        "TR": "Deprem bölgesi tespiti ve güncel mevzuata %100 uyumlu, teknik olarak doğru prim hesaplaması artık sadece birkaç tık uzağınızda. Ayrıca, yapay zeka destekli hasar analizi ile riskinizi daha akıllı yönetin!",
        "EN": "Detect earthquake zones and calculate premiums that are 100% compliant with current regulations, all with just a few clicks. Plus, manage your risks smarter with AI-powered damage analysis!"
    },
    # "why": {"TR": "Nasıl Çalışır?", "EN": "How It Works?"}, # Bu satırı güncelleyeceğiz veya yenisini ekleyeceğiz
    "usage_steps_header": {"TR": "TariffEQ Kullanım Adımları", "EN": "TariffEQ Usage Steps"}, # YENİ
    "step1_select_calc_type": {"TR": "1️⃣ Hesaplama Türünü Seçin", "EN": "1️⃣ Select Calculation Type"}, # YENİ (veya feature1'i güncelle)
    "step2_enter_details": {"TR": "2️⃣ Teminat ve Risk Bilgilerinizi Girin", "EN": "2️⃣ Enter Your Coverage and Risk Details"}, # YENİ (veya feature2'yi güncelle)
    "step3_get_premium_scenario": {"TR": "3️⃣ Minimum Deprem Primini ve Teknik Hasar Senaryonuzu Hemen Öğrenin", "EN": "3️⃣ Instantly Get the Minimum Earthquake Premium and Your Technical Damage Scenario"}, # YENİ (veya feature3'ü güncelle)
    "step4_ai_consultant": {"TR": "4️⃣ AI Danışman Yorumuyla Risklerinizi Değerlendirin", "EN": "4️⃣ Evaluate Your Risks with AI Consultant Commentary"}, # YENİ
    # Eski feature1, feature2, feature3 anahtarlarını kaldırabilir veya bu yenilerle değiştirebilirsiniz.
    # Benzerlikten dolayı mevcut feature anahtarlarını güncellemek daha mantıklı olabilir.
    # Örnek olarak yenilerini ekliyorum, siz duruma göre karar verin.
    "feature1": {"TR": "1️⃣ Hesaplama Türünü Seçin", "EN": "1️⃣ Select Calculation Type"}, # GÜNCELLENDİ
    "feature2": {"TR": "2️⃣ Teminat ve Risk Bilgilerinizi Girin", "EN": "2️⃣ Enter Your Coverage and Risk Details"}, # GÜNCELLENDİ
    "feature3": {"TR": "3️⃣ Minimum Deprem Primini ve Teknik Hasar Senaryonuzu Hemen Öğrenin", "EN": "3️⃣ Instantly Get the Minimum Earthquake Premium and Your Technical Damage Scenario"}, # GÜNCELLENDİ
    "feature4_ai_advice": {"TR": "4️⃣ AI Danışman Yorumuyla Risklerinizi Değerlendirin", "EN": "4️⃣ Evaluate Your Risks with AI Consultant Commentary"}, # YENİ
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
    "comment_institution_label": {
        "TR": "Kurum (Opsiyonel)",
        "EN": "Institution (Optional)"
    },
    "comment_institution_placeholder": {
        "TR": "Örn: Allianz Sigorta A.Ş., Türk Reasürans A.Ş., Lockton Omni A.Ş.",
        "EN": "e.g., Allianz Insurance Plc, Turkish Reinsurance Inc., Lockton Omni Ltd."
    },
    "comment_name_label": {
        "TR": "Ad Soyad (Opsiyonel)",
        "EN": "Full Name (Optional)"
    },
    "comment_name_placeholder": {
        "TR": "Adınız ve soyadınız",
        "EN": "Your full name"
    },
    "comment_text_label": { # Yorum metin alanı için etiket (placeholder yerine)
        "TR": "Yorumunuz",
        "EN": "Your Comment"
    },
    "comment_placeholder": {"TR": "Yorumunuzu buraya yazın...", "EN": "Write your comment here..."}, # Bu zaten vardı, label ile birlikte kullanılabilir.
    "submit": {"TR": "Gönder", "EN": "Submit"},
    "home": {"TR": "Ana Sayfa", "EN": "Home"},
    "calc": {"TR": "🚀 Deprem Primi ve Hasar Riskini Hesapla", "EN": "🚀 Calculate Earthquake Premium and Damage Risk"},
    "earthquake": {"TR": "🗺️ Deprem Bölgeni Öğren", "EN": "🗺️ Learn Your Earthquake Zone"}, # YENİ: Deprem Bölgeleri sayfası için etiket
    "calc_nav_label": {"TR": "🚀  Deprem Primi ve Hasar Riski", "EN": "🚀 Earthquake Premium and Damage Risk"}, # YENİ: Navigasyon için farklı etiket
    "earthquake_zones_nav": {"TR": "🗺️ Deprem Bölgeleri", "EN": "🗺️ Earthquake Zones"}, # YENİ: Deprem Bölgeleri sayfası için etiket
    "featured_features_header": {"TR": "Öne Çıkan Özellikler", "EN": "Featured Features"},
    "feature_fast": {"TR": " Hızlı ve Kolay Kullanım: 30 saniyede deprem primini öğrenin", "EN": " Fast and Easy to Use: Learn the earthquake premium in 30 seconds"},
    "feature_accurate": {"TR": "Teknik Doğruluk: Resmi deprem tarifesine tam uyum", "EN": "Technical Accuracy: Full compliance with the official earthquake tariff"},
    "feature_currency": {"TR": "AI Destekli Hasar Analizi", "EN": "AI-Powered Damage Analysis"},
    "feature_multilocation": {"TR": "Çoklu Lokasyon: Birden fazla işyeri/şantiye için tek ekranda hesaplama", "EN": "Multi-Location: Calculation for multiple workplaces/sites on a single screen"},
    "feature_coinsurance": {"TR": "Koasürans & Muafiyet: Tüm teknik indirim ve ek primler otomatik hesaplansın", "EN": "Coinsurance & Deductible: All technical discounts and additional premiums are calculated automatically"},
    "who_is_it_for_header": {"TR": "👥 Kimler İçin?", "EN": "👥 Who Is It For?"},
    "target_insurers": {"TR": "🏢 Sigorta şirketi ekipleri ve underwriterlar", "EN": "🏢 Insurance company teams and underwriters"},
    "target_brokers": {"TR": "🤝 Brokerlar, acenteler", "EN": "🤝 Brokers, agents"},
    "target_professionals": {"TR": "⏱️ Hızlı teklif hazırlamak isteyen sigorta profesyonelleri", "EN": "⏱️ Insurance professionals who want to prepare quick quotes"},
    "target_owners": {"TR": "🏗️ Proje sahipleri ve işletme yöneticileri", "EN": "🏗️ Project owners and business managers"},
    "scenario_page_title": {
        "TR": "Senaryo Hesaplama ",
        "EN": "Scenario Calculation"
    },
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
        
        /* YENİ EKLENEN ÖZELLİKLER */
        min-height: 150px; /* Kartlar için minimum bir yükseklik belirleyin. Bu değeri içeriğinize göre ayarlayın. */
        display: flex; /* Flexbox'ı etkinleştir */
        flex-direction: column; /* İçeriği dikey olarak sırala */
        justify-content: center; /* İçeriği dikeyde ortala (eğer metin azsa) */
        align-items: center; /* İçeriği yatayda ortala (text-align: center zaten vardı ama flex için de iyi) */
    }
    .card:hover {
        transform: translateY(-params_grup);
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
    st.image("assets/logo.png", width=1000) # width=1000 logonuz büyükse küçültün, örneğin 200
    st.page_link("home.py", label=T["home"][st.session_state.lang], icon="🏠")
    st.page_link("pages/calculate.py", label=T["calc_nav_label"][st.session_state.lang]) # "calc" yerine farklı bir anahtar kullanmak daha iyi olabilir
    st.page_link("pages/earthquake_zones.py", label=T["earthquake_zones_nav"][st.session_state.lang]) # YENİ SAYFA LİNKİ
    st.page_link("pages/scenario_calculator_page.py", label=T["scenario_page_title"][st.session_state.lang], icon="📉") # Mevcut sayfa
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
</div>
""", unsafe_allow_html=True)

# Açıklama ve Başlat Butonu
st.markdown(f"""
<div style="font-weight: bold;">
    <strong style="font-weight: 900;">{T['desc_highlight'][lang]}</strong> {T['desc_main'][lang]}
</div>
""", unsafe_allow_html=True)

col1, col2 = st.columns([1, 1]) # İki sütun: sol geniş, sağ dar
# YENİ: Hemen Hesapla Butonu
with col1:
    if st.button(T["calc"][lang], use_container_width=True, type="primary"):
        st.switch_page("pages/calculate.py")
with col2:
    if st.button(T["earthquake"][lang], use_container_width=True, type="primary"):
        st.switch_page("pages/earthquake_zones.py")
st.markdown("---") # Buton ile sonraki bölüm arasına bir ayırıcı

# TariffEQ Kullanım Adımları
st.markdown(f"### {T['usage_steps_header'][lang]}") # Başlık güncellendi
col1, col2, col3, col4 = st.columns(4) # 4 sütun oluşturuldu
with col1:
    st.markdown(f"<div class='card'><strong>{T['feature1'][lang]}</strong></div>", unsafe_allow_html=True) # feature1 güncellenmiş metni kullanır
with col2:
    st.markdown(f"<div class='card'><strong>{T['feature2'][lang]}</strong></div>", unsafe_allow_html=True) # feature2 güncellenmiş metni kullanır
with col3:
    st.markdown(f"<div class='card'><strong>{T['feature3'][lang]}</strong></div>", unsafe_allow_html=True) # feature3 güncellenmiş metni kullanır
with col4: # Yeni 4. kart
    st.markdown(f"<div class='card'><strong>{T['feature4_ai_advice'][lang]}</strong></div>", unsafe_allow_html=True)


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
html_currency = f"🤖 <strong>{parts_currency[0]}:</strong> {parts_currency[1].strip()}" if len(parts_currency) == 2 else f"🤖 <strong>{text_currency}</strong>"
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

# Formspree endpoint URL'nizi buraya girin
formspree_url = "https://formspree.io/f/xxxxxxxx"  # KENDİ FORM ENDPOINT URL'NİZİ GİRİN

with st.form(key="comment_form"):
    institution_name = st.text_input(
        label=T['comment_institution_label'][lang],
        placeholder=T['comment_institution_placeholder'][lang],
        key="institution_input"
    )
    full_name = st.text_input(
        label=T['comment_name_label'][lang],
        placeholder=T['comment_name_placeholder'][lang],
        key="fullname_input"
    )
    comment_text = st.text_area(
        label=T['comment_text_label'][lang],  # Placeholder yerine label kullanıldı
        placeholder=T['comment_placeholder'][lang], # Placeholder hala kullanılabilir
        height=150,
        key="comment_text_area"
    )
    
    submitted = st.form_submit_button(T['submit'][lang])

    if submitted:
        if comment_text.strip(): # En azından yorumun dolu olmasını kontrol edelim
            try:
                form_data = {
                    "Kurum": institution_name.strip(),
                    "Ad Soyad": full_name.strip(),
                    "Yorum": comment_text.strip(),
                    "_subject": f"TariffEQ Yeni Yorum: {full_name.strip() if full_name.strip() else 'Anonim'}", # E-posta konusu
                    # "email": "form_sender@example.com", # İsterseniz sabit bir gönderen e-postası ekleyebilirsiniz
                }
                
                response = requests.post(formspree_url, data=form_data)
                response.raise_for_status() 
                st.success("Teşekkürler, yorumunuz başarıyla gönderilmiştir.")
                # Formu temizlemek için session state'leri sıfırla ve rerun yap
                # st.session_state.institution_input = ""
                # st.session_state.fullname_input = ""
                # st.session_state.comment_text_area = ""
                # st.rerun() # Bu satır, formu temizledikten sonra sayfayı yeniden yükler.
                            # Ancak st.form içindeyken rerun bazen beklenmedik davranışlara yol açabilir.
                            # Genellikle success mesajı yeterlidir, kullanıcı yeni bir yorum için formu tekrar doldurabilir.
            except requests.exceptions.RequestException as e:
                st.error(f"Yorum gönderilirken bir hata oluştu: {e}")
            except Exception as e:
                st.error(f"Beklenmedik bir hata oluştu: {e}")
        else:
            st.warning("Lütfen yorum alanını boş bırakmayınız.")