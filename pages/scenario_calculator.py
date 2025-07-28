import streamlit as st
from translations import T # Ana dizindeki translations.py dosyasını import ediyoruz
import pandas as pd # Pandas'ı tablo için import edelim
import plotly.express as px # Plotly Express'i ekleyin

# Dil değişkenini session state'den al
if 'lang' not in st.session_state:
    st.session_state.lang = "TR" # Varsayılan dil
lang = st.session_state.lang

def tr(key: str) -> str:
    # tr fonksiyonu seçenek listeleri için de çalışacak şekilde güncellenmeli
    translation = T.get(key, {}).get(lang, key)
    if isinstance(translation, list):
        return [T.get(item, {}).get(lang, item) if isinstance(item, str) and item in T else item for item in translation]
    return translation

# --- SABİT VERİLER ---
DEPREM_BOLGESI_ORANLARI = {
    # Deprem Bölgesi: {"minor": %, "expected": %, "severe": %}
    1: {"minor": 0.07, "expected": 0.20, "severe": 0.45},
    2: {"minor": 0.06, "expected": 0.17, "severe": 0.40},
    3: {"minor": 0.05, "expected": 0.13, "severe": 0.32},
    4: {"minor": 0.04, "expected": 0.09, "severe": 0.24},
    5: {"minor": 0.03, "expected": 0.06, "severe": 0.15},
    6: {"minor": 0.03, "expected": 0.06, "severe": 0.15},
    7: {"minor": 0.03, "expected": 0.06, "severe": 0.15},
}

SEKTOR_ALTERNATIFLERI = {
    # Alternatif Adı: {"koasurans_sirket_payi": float, "muafiyet_yuzdesi": float, "etiket_key": str}
    "80/20 - %2": {"koasurans_sirket_payi": 0.80, "muafiyet_yuzdesi": 0.02, "etiket_key": "balance_icon"},
    "90/10 - %2": {"koasurans_sirket_payi": 0.90, "muafiyet_yuzdesi": 0.02, "etiket_key": "shield_icon"},
    "80/20 - %5": {"koasurans_sirket_payi": 0.80, "muafiyet_yuzdesi": 0.05, "etiket_key": "balance_icon"},
    "90/10 - %5": {"koasurans_sirket_payi": 0.90, "muafiyet_yuzdesi": 0.05, "etiket_key": "shield_icon"},
    "70/30 - %5": {"koasurans_sirket_payi": 0.70, "muafiyet_yuzdesi": 0.05, "etiket_key": "low_risk_icon"},
}


# --- YARDIMCI HESAPLAMA FONKSİYONLARI ---
def deprem_hasar_orani_modifiye(bolge, yapi_tipi_str, bina_yasi_str, kat_sayisi_str, faaliyet_str, guclendirme_str):
    """
    Verilen deprem bölgesi için temel hasar oranlarını alır ve
    bina özelliklerine göre bir çarpan uygulayarak modifiye eder.
    """
    base_oranlar = DEPREM_BOLGESI_ORANLARI.get(bolge)
    if not base_oranlar:
        st.warning(f"Geçersiz risk bölgesi '{bolge}' için varsayılan 1. bölge oranları kullanılıyor.")
        base_oranlar = DEPREM_BOLGESI_ORANLARI[1]

    carpani = 1.0
    # Bina Yaşı (string'den sayıya ve aralığa)
    bina_yasi_val = 0
    if "10" in bina_yasi_str and "<" in bina_yasi_str : bina_yasi_val = 5
    elif "10" in bina_yasi_str and "30" in bina_yasi_str: bina_yasi_val = 20
    elif "30" in bina_yasi_str and ">" in bina_yasi_str: bina_yasi_val = 40
    else:
        try: bina_yasi_val = int(bina_yasi_str)
        except ValueError: bina_yasi_val = 20

    if yapi_tipi_str == tr("structural_type_options")[2]: carpani *= 1.15 # Yığma
    elif yapi_tipi_str == tr("structural_type_options")[1]: carpani *= 0.85 # Çelik

    if bina_yasi_val > 30: carpani *= 1.20
    elif bina_yasi_val < 10: carpani *= 0.90
    elif 10 <= bina_yasi_val <= 30: carpani *= 1.05

    # Kat Sayısı
    kat_sayisi_val = 0
    if "1" in kat_sayisi_str and "3" in kat_sayisi_str: kat_sayisi_val = 2
    elif "4" in kat_sayisi_str and "7" in kat_sayisi_str: kat_sayisi_val = 5
    elif "8" in kat_sayisi_str: kat_sayisi_val = 10
    else:
        try: kat_sayisi_val = int(kat_sayisi_str)
        except ValueError: kat_sayisi_val = 5

    if kat_sayisi_val >= 8: carpani *= 1.10
    elif kat_sayisi_val <= 3: carpani *= 0.95

    # Faaliyet
    if faaliyet_str == tr("activity_type_options")[0]: carpani *= 1.15 # Depolama
    elif faaliyet_str == tr("activity_type_options")[2]: carpani *= 0.90 # Ofis
    elif faaliyet_str == tr("activity_type_options")[1]: carpani *= 1.05 # Üretim

    guclendirme_bool = (guclendirme_str == tr("strengthening_options")[0])
    if guclendirme_bool: carpani *= 0.85
    
    # Çarpanı temel oranlara uygula ve maksimum %70 ile sınırla
    modifiye_oranlar = {k: min(round(v * carpani, 4), 0.7) for k, v in base_oranlar.items()}
    return modifiye_oranlar

def bi_carpan_hesapla(activity_bi_str, alt_site_str, turnover_str, continuity_plan_str, lang_options_tr_format):
    """
    İş Kesintisi (BI) için risk çarpanını hesaplar.
    lang_options_tr_format: tr() fonksiyonundan dönen seçenek listelerini içerir.
    Örn: {"bi_activity_options": ["Depolama", "Üretim", ...], "yes_no_options": ["Evet", "Hayır"], ...}
    """
    carpani = 1.0

    # Faaliyet türü (BI)
    # İstenen Sıralama: Depolama, Üretim, Ofis, Ticaret, Diğer
    # tr("bi_activity_options") -> ["Depolama", "Üretim", "Ofis", "Ticaret", "Diğer"] (Çeviride bu sıra varsayıldı)
    bi_activity_options = lang_options_tr_format.get("bi_activity_options", [])
    
    # Çarpanlar (yapılacaklar.txt satır 334'e göre)
    # Üretim ×1.00, Depolama ×0.80, Ofis ×0.60, Perakende ×0.90
    # Not: "Ticaret" seçeneği "Perakende" ile eşleştirildi.
    if activity_bi_str == bi_activity_options[0]: # Depolama
        carpani *= 0.80
    # activity_bi_str == bi_activity_options[1] (Üretim) için çarpan 1.0 (değişiklik yok)
    elif activity_bi_str == bi_activity_options[2]: # Ofis
        carpani *= 0.60
    elif activity_bi_str == bi_activity_options[3]: # Ticaret (Perakende olarak kabul edildi)
        carpani *= 0.90
    # Diğer için çarpan 1.0 (değişiklik yok)


    # Alternatif üretim yeri
    yes_no_options = lang_options_tr_format.get("yes_no_options", [])
    if alt_site_str == yes_no_options[0]: # Evet
        carpani *= 0.70

    # Yıllık ciro
    # İstenen Seçenekler: "1–10 M TL", "10–50 M TL", "50+ M TL"
    # tr("turnover_options") -> ["1–10 M TL", "10–50 M TL", "50+ M TL"] (Çeviride bu sıra varsayıldı)
    turnover_options = lang_options_tr_format.get("turnover_options", [])
    # Sadece "50+ M TL" için çarpan uygulanıyor (yapılacaklar.txt satır 337)
    if len(turnover_options) == 3 and turnover_str == turnover_options[2]: # 50+ M TL
        carpani *= 1.05
    
    # İş sürekliliği planı
    if continuity_plan_str == yes_no_options[0]: # Var (Evet)
        carpani *= 0.90
    else: # Yok (Hayır)
        carpani *= 1.10 # yapılacaklar.txt satır 338'de "Yok x1.10" belirtilmiş.
    
    return carpani

def bi_hasar_senaryosu_hesapla(bi_bedeli, pd_senaryo_oranlari_dict, bi_carpan_value):
    """
    İş Kesintisi (BI) hasarını her senaryo için hesaplar.
    pd_senaryo_oranlari_dict: {'minor': oran, 'expected': oran, 'severe': oran}
    """
    st.text(2)
    sonuc_bi = {}
    if bi_bedeli > 0 and bi_carpan_value > 0:
        for senaryo_tipi, pd_oran in pd_senaryo_oranlari_dict.items():
            # BI senaryo oranı = PD oranı * BI çarpanı (max %70) - yapılacaklar.txt (satır 341-342)
            toplam_bi_oran = min(pd_oran * bi_carpan_value, 0.7) 
            sonuc_bi[senaryo_tipi] = {
                "oran": toplam_bi_oran,
                "hasar": int(bi_bedeli * toplam_bi_oran)
            }
    return sonuc_bi

def hasar_senaryosu_hesapla(pd_bedel_calc, hasar_orani_calc, muafiyet_orani_calc, koas_sirket_payi_orani_calc): # koas_sigortali_payi_orani_calc kaldırıldı


    pd_brut_hasar = pd_bedel_calc * hasar_orani_calc
    muafiyet_tutari = pd_brut_hasar * muafiyet_orani_calc # Bu muafiyet brüt hasar üzerinden mi, yoksa bedel üzerinden mi olmalı? Genellikle bedel üzerinden olur. Şimdilik brüt hasar üzerinden bırakıyorum.
    kalan_hasar = max(pd_brut_hasar - muafiyet_tutari, 0)
    sirket_odedigi = kalan_hasar * koas_sirket_payi_orani_calc
    sigortali_odedigi = kalan_hasar * (1 - koas_sirket_payi_orani_calc) # Burada hesaplanıyor
    return int(pd_brut_hasar), int(muafiyet_tutari), int(sirket_odedigi), int(sigortali_odedigi)

def pd_limit_onerileri_hesapla(toplam_pd_bedeli, modifiye_hasar_oranlari_dict, risk_bolgesi):
    """PD için limit önerilerini hesaplar."""
    oneriler = {
        "tam_bedel": toplam_pd_bedeli,
        "hafif_limit": 0,
        "beklenen_limit": 0,
        "agir_limit": 0,
        "sektor_tavsiyesi_alt": 0,
        "sektor_tavsiyesi_ust": 0,
        "tavsiye_metni_key": "pd_limit_recommendation_default" # Varsayılan tavsiye metni anahtarı
    }
    if modifiye_hasar_oranlari_dict and toplam_pd_bedeli > 0:
        st.text(toplam_pd_bedeli)
        oneriler["hafif_limit"] = int(toplam_pd_bedeli * modifiye_hasar_oranlari_dict.get("minor", 0.0))
        oneriler["beklenen_limit"] = int(toplam_pd_bedeli * modifiye_hasar_oranlari_dict.get("expected", 0.0))
        oneriler["agir_limit"] = int(toplam_pd_bedeli * modifiye_hasar_oranlari_dict.get("severe", 0.0))
        
        # Sektör tavsiyesi mantığı
        if risk_bolgesi <= 3: # Yüksek riskli bölgeler (1, 2, 3)
            oneriler["sektor_tavsiyesi_alt"] = oneriler["beklenen_limit"]
            oneriler["sektor_tavsiyesi_ust"] = oneriler["agir_limit"]
            oneriler["tavsiye_metni_key"] = "pd_limit_recommendation_high_risk"
        else: # Düşük riskli bölgeler (4, 5, 6, 7)
            oneriler["sektor_tavsiyesi_alt"] = oneriler["beklenen_limit"]
            oneriler["sektor_tavsiyesi_ust"] = oneriler["beklenen_limit"] # Tek değer olarak gösterilebilir
            oneriler["tavsiye_metni_key"] = "pd_limit_recommendation_low_risk"
            
    return oneriler

def bi_limit_onerileri_hesapla(toplam_bi_bedeli, modifiye_hasar_oranlari_dict, bi_carpan_value, risk_bolgesi):
    """BI için limit önerilerini hesaplar."""
    oneriler = {
        "tam_bedel": toplam_bi_bedeli,
        "hafif_limit": 0,
        "beklenen_limit": 0,
        "agir_limit": 0,
        "sektor_tavsiyesi_alt": 0,
        "sektor_tavsiyesi_ust": 0,
        "tavsiye_metni_key": "bi_limit_recommendation_default"
    }
    if modifiye_hasar_oranlari_dict and toplam_bi_bedeli > 0 and bi_carpan_value > 0:
        bi_oran_minor = min(modifiye_hasar_oranlari_dict.get("minor", 0.0) * bi_carpan_value, 0.7)
        bi_oran_expected = min(modifiye_hasar_oranlari_dict.get("expected", 0.0) * bi_carpan_value, 0.7)
        bi_oran_severe = min(modifiye_hasar_oranlari_dict.get("severe", 0.0) * bi_carpan_value, 0.7)

        oneriler["hafif_limit"] = int(toplam_bi_bedeli * bi_oran_minor)
        oneriler["beklenen_limit"] = int(toplam_bi_bedeli * bi_oran_expected)
        oneriler["agir_limit"] = int(toplam_bi_bedeli * bi_oran_severe)

        if risk_bolgesi <= 3: # Yüksek riskli bölgeler
            oneriler["sektor_tavsiyesi_alt"] = oneriler["beklenen_limit"]
            oneriler["sektor_tavsiyesi_ust"] = oneriler["agir_limit"]
            oneriler["tavsiye_metni_key"] = "bi_limit_recommendation_high_risk"
        else: # Düşük riskli bölgeler
            oneriler["sektor_tavsiyesi_alt"] = oneriler["beklenen_limit"]
            oneriler["sektor_tavsiyesi_ust"] = oneriler["beklenen_limit"]
            oneriler["tavsiye_metni_key"] = "bi_limit_recommendation_low_risk"
    return oneriler

# --- CSS ---
st.markdown("""
<style>
    /* ... calculate.py'deki stiller buraya eklenebilir ... */
    .info-box {
        background-color: #E6F7FF; /* Biraz farklı bir renk */
        padding: 1em;
        border-radius: 10px;
        margin-bottom: 1em;
        border-left: 5px solid #1890FF;
    }
    h1, h2, h3, h4, h5, h6 {
        color: black !important;
    }
    /* Başlıklardaki çapa ikonlarını gizle */
    h1 a, h2 a, h3 a, h4 a, h5 a, h6 a {
        display: none !important;
    }
</style>
""", unsafe_allow_html=True)

# --- Kenar Çubuğu ---
with st.sidebar:
    st.image("./assets/logo.png", width=1000)
    st.page_link("home.py", label=tr("home"), icon="🏠")
    st.page_link("pages/calculate.py", label=tr("calc_nav_label"))
    st.page_link("pages/earthquake_zones.py", label=tr("earthquake_zones_nav"), icon="🗺️")
    st.page_link("pages/scenario_calculator.py", label=tr("scenario_nav_label"), icon="🧪")
    st.markdown("---")

    lang_options = ["TR", "EN"]
    # lang session_state'de zaten başta tanımlanıyor, burada tekrar kontrol etmeye gerek yok.
    current_lang_index = lang_options.index(st.session_state.lang)
    selected_lang_sidebar = st.radio(
        "Language / Dil",
        options=lang_options,
        index=current_lang_index,
        key="sidebar_language_selector_scenario"
    )
    if selected_lang_sidebar != st.session_state.lang:
        st.session_state.lang = selected_lang_sidebar
        st.rerun()
    st.markdown("---")
    st.markdown(f"<div class='sidebar-footer footer'>{tr('footer')}</div>", unsafe_allow_html=True)


st.title(tr("scenario_header"))

if 'scenario_data' in st.session_state and st.session_state.scenario_data:
    scenario_data = st.session_state.scenario_data
    st.subheader(tr("received_data_header"))


    total_pd_orig_ccy = scenario_data.get("total_pd_orig_ccy", 0.0)
    st.text(total_pd_orig_ccy)
    total_bi_orig_ccy = scenario_data.get("total_bi_orig_ccy", 0.0)
    currency = scenario_data.get("currency", "TRY")
    locations_summary = scenario_data.get("locations_summary", [])
    # fx_rate_at_calc = scenario_data.get("fx_rate", 1.0) # Bu değişken kullanılmıyor gibi, kaldırılabilir.

    st.markdown(f"""
    <div class='info-box'>
        {tr("total_pd_sum")}: {total_pd_orig_ccy:,.2f} {currency}<br>
        {tr("total_bi_sum")}: {total_bi_orig_ccy:,.2f} {currency}<br>
        {tr("currency")}: {currency}<br>
    </div>
    """, unsafe_allow_html=True)

    st.subheader(tr("locations_summary_header"))
    for i, loc_summary in enumerate(locations_summary):
        st.markdown(f"""
        <div class='info-box'>
            <b>{tr("location_label")} {i+1} ({loc_summary.get("group", "N/A")})</b><br>
            {tr("risk_group")}: {loc_summary.get("risk_group", "N/A")}<br>
            {tr("pd_sum_loc")}: {loc_summary.get("pd_sum_loc", 0.0):,.2f} {currency}<br>
            {tr("bi_sum_loc")}: {loc_summary.get("bi_sum_loc", 0.0):,.2f} {currency}
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")
    st.header(tr("scenario_parameters_header"))

    # Her lokasyon için senaryo parametreleri
    for i, loc_summary in enumerate(locations_summary):
        location_label = f"{tr('location_label')} {i+1} ({loc_summary.get('group', 'N/A')})"
        sigorta_bedeli_pd_loc_display = loc_summary.get("pd_sum_loc", 0.0)
        sigorta_bedeli_bi_loc_display = loc_summary.get("bi_sum_loc", 0.0)

        with st.expander(location_label, expanded=(i == 0)):
            st.markdown(f"**{tr('pd_sum_loc')}:** {sigorta_bedeli_pd_loc_display:,.2f} {currency}")
            if sigorta_bedeli_bi_loc_display > 0:
                st.markdown(f"**{tr('bi_sum_loc')}:** {sigorta_bedeli_bi_loc_display:,.2f} {currency}")
            st.markdown(f"**{tr('risk_group')}:** {loc_summary.get('risk_group', 'N/A')}")
            st.markdown("---")

            st.subheader(tr("pd_parameters_header"))
            cols_loc_scenario_pd = st.columns(2)
            with cols_loc_scenario_pd[0]:
                st.selectbox(tr("building_age"), options=tr("building_age_options"), key=f"scenario_building_age_{i}")
                st.selectbox(tr("num_floors"), options=tr("num_floors_options"), key=f"scenario_num_floors_{i}")
                st.radio(tr("strengthening"), options=tr("strengthening_options"), key=f"scenario_strengthening_{i}", horizontal=True)
            with cols_loc_scenario_pd[1]:
                st.selectbox(tr("structural_type"), options=tr("structural_type_options"), key=f"scenario_structural_type_{i}")
                st.selectbox(tr("activity_type"), options=tr("activity_type_options"), key=f"scenario_activity_type_{i}")

            if sigorta_bedeli_bi_loc_display > 0:
                st.markdown("---")
                st.subheader(tr("bi_parameters_header"))
                cols_loc_scenario_bi = st.columns(2)
                with cols_loc_scenario_bi[0]:
                    st.selectbox(tr("bi_activity_type_label"), options=tr("bi_activity_options"), key=f"scenario_bi_activity_type_{i}")
                    st.selectbox(tr("annual_turnover_label"), options=tr("turnover_options"), key=f"scenario_turnover_{i}")
                with cols_loc_scenario_bi[1]:
                    st.selectbox(tr("alternate_production_site_label"), options=tr("yes_no_options"), key=f"scenario_alternate_site_{i}")
                    st.selectbox(tr("business_continuity_plan_label"), options=tr("yes_no_options"), key=f"scenario_continuity_plan_{i}")

    # --- HESAPLAMA BUTONU ---
    if st.button(tr("recalculate_scenario_button"), use_container_width=True, type="primary"):
        all_locations_results_list_calc = []
        st.session_state.loc_specific_metrics_calc = {}

        # calculate.py'den gelen toplam hesaplanmış primleri al
        # Bu anahtarların scenario_data içinde olduğundan emin olun!
        # total_pd_premium_try ve total_bi_premium_try olarak eklendiğini varsayıyoruz.
        base_total_pd_premium_from_calc = scenario_data.get("total_pd_premium_try", 0)
        base_total_bi_premium_from_calc = scenario_data.get("total_bi_premium_try", 0)
        
        # Eğer birden fazla lokasyon varsa ve primler lokasyon bazında dağıtılacaksa,
        # bu toplam primlerin nasıl bölüneceği veya her lokasyon için ayrı primlerin
        # calculate.py'den gelip gelmediği önemlidir.
        # Şimdilik, bu toplam primlerin tüm portföy için olduğunu ve her alternatif için
        # aynı kalacağını varsayıyoruz.

        for i, loc_summary_original_calc in enumerate(locations_summary):
            # Lokasyona özel senaryo girdilerini session_state'den al
            bina_yasi_input_calc = st.session_state[f"scenario_building_age_{i}"]
            yapi_tipi_input_calc = st.session_state[f"scenario_structural_type_{i}"]
            kat_sayisi_input_calc = st.session_state[f"scenario_num_floors_{i}"]
            faaliyet_input_calc = st.session_state[f"scenario_activity_type_{i}"]
            guclendirme_input_calc = st.session_state[f"scenario_strengthening_{i}"]

            risk_bolgesi_loc_calc = int(loc_summary_original_calc.get("risk_group", 1))
            sigorta_bedeli_pd_loc_calc = loc_summary_original_calc.get("pd_sum_loc", 0.0)
            sigorta_bedeli_bi_loc_calc = loc_summary_original_calc.get("bi_sum_loc", 0.0)

            modifiye_hasar_oranlari_calc = deprem_hasar_orani_modifiye(
                bolge=risk_bolgesi_loc_calc, yapi_tipi_str=yapi_tipi_input_calc,
                bina_yasi_str=bina_yasi_input_calc, kat_sayisi_str=kat_sayisi_input_calc,
                faaliyet_str=faaliyet_input_calc, guclendirme_str=guclendirme_input_calc
            )
            st.session_state.loc_specific_metrics_calc[i] = {"modifiye_hasar_oranlari": modifiye_hasar_oranlari_calc}

            bi_carpan_calc = 0
            bi_hasarlar_dict_calc = {}
            if sigorta_bedeli_bi_loc_calc > 0:
                activity_bi_input_calc = st.session_state[f"scenario_bi_activity_type_{i}"]
                alternate_site_input_calc = st.session_state[f"scenario_alternate_site_{i}"]
                turnover_input_calc = st.session_state[f"scenario_turnover_{i}"]
                continuity_plan_input_calc = st.session_state[f"scenario_continuity_plan_{i}"]
                lang_options_for_bi_calc_loc = {
                    "bi_activity_options": tr("bi_activity_options"),
                    "yes_no_options": tr("yes_no_options"),
                    "turnover_options": tr("turnover_options")
                }
                bi_carpan_calc = bi_carpan_hesapla(
                    activity_bi_input_calc, alternate_site_input_calc,
                    turnover_input_calc, continuity_plan_input_calc, lang_options_for_bi_calc_loc
                )
                bi_hasarlar_dict_calc = bi_hasar_senaryosu_hesapla(
                    sigorta_bedeli_bi_loc_calc, modifiye_hasar_oranlari_calc, bi_carpan_calc
                )
                st.session_state.loc_specific_metrics_calc[i]["bi_carpan"] = bi_carpan_calc
                st.session_state.loc_specific_metrics_calc[i]["bi_hasarlar_dict"] = bi_hasarlar_dict_calc

            results_for_location_table_calc = []
            for alt_adi_calc, alt_degerleri_calc in SEKTOR_ALTERNATIFLERI.items():
                koas_sirket_calc = alt_degerleri_calc["koasurans_sirket_payi"]
                muaf_yuzde_calc = alt_degerleri_calc["muafiyet_yuzdesi"]
                etiket_key_calc = alt_degerleri_calc["etiket_key"]
                
                # --- PRİM ATAMASI ---
                # calculate.py'den gelen primleri doğrudan kullan.
                # Bu, tüm alternatifler için aynı primi kullanır.
                # Bu primlerin, tüm lokasyonların toplam primi olduğunu varsayıyoruz.
                # Eğer tek lokasyon varsa veya primler alternatiflere göre değişmiyorsa bu geçerli olabilir.
                
                # PD Primi:
                # Eğer birden fazla lokasyon varsa ve toplam PD primi bu lokasyonlara
                # sigorta bedelleri oranında dağıtılacaksa, burada bir hesaplama gerekir.
                # Şimdilik, calculate.py'den gelen toplam PD primini doğrudan atıyoruz.
                # Bu, her bir alternatif satırının aynı toplam PD primine sahip olacağı anlamına gelir.
                # Bu durum, genellikle TCoR hesaplamasında toplam primin sabit kaldığı senaryolarda mantıklıdır.
                pd_prim_calc = base_total_pd_premium_from_calc
                
                # BI Primi:
                # Benzer şekilde, toplam BI primini atıyoruz. BI bedeli varsa BI primi olur.
                bi_prim_calc = base_total_bi_premium_from_calc if sigorta_bedeli_bi_loc_calc > 0 else 0
                
                toplam_prim_calc = pd_prim_calc + bi_prim_calc

                for hasar_tipi_key_calc, hasar_orani_pd_calc in modifiye_hasar_oranlari_calc.items():
                    pd_brut_calc, pd_muaf_calc, pd_sirket_calc, pd_sigortali_calc = 0, 0, 0, 0
                    if sigorta_bedeli_pd_loc_calc > 0 and hasar_orani_pd_calc > 0:
                        pd_brut_calc, pd_muaf_calc, pd_sirket_calc, pd_sigortali_calc = hasar_senaryosu_hesapla(
                            sigorta_bedeli_pd_loc_calc, hasar_orani_pd_calc, muaf_yuzde_calc, koas_sirket_calc
                        )
                    bi_hasar_senaryo_calc = 0
                    if sigorta_bedeli_bi_loc_calc > 0 and bi_hasarlar_dict_calc and hasar_tipi_key_calc in bi_hasarlar_dict_calc:
                        bi_hasar_senaryo_calc = bi_hasarlar_dict_calc[hasar_tipi_key_calc].get('hasar', 0)
                    tcor_val_calc = toplam_prim_calc + pd_sigortali_calc + bi_hasar_senaryo_calc
                    
                    results_for_location_table_calc.append({
                        # Çevirileri burada değil, DataFrame oluşturulduktan sonra sütun adlarında kullanacağız
                        "alternative_col_raw": alt_adi_calc, "label_col_raw": etiket_key_calc,
                        "pd_premium_raw": pd_prim_calc, 
                        "bi_premium_raw": bi_prim_calc,
                        "total_premium_raw": toplam_prim_calc, 
                        "scenario_type_key_raw": hasar_tipi_key_calc,
                        "gross_damage_raw": pd_brut_calc, 
                        "insurer_share_raw": pd_sirket_calc,
                        "insured_share_raw": pd_sigortali_calc, 
                        "bi_loss_amount_raw": bi_hasar_senaryo_calc,
                        "tcor_raw": tcor_val_calc,
                        # Ham değerleri de saklayalım (zaten yukarıdakiler ham)
                        "_pd_sirket_payi_raw": pd_sirket_calc, # Grafik için _ ile başlayanlar
                        "_pd_sigortali_payi_raw": pd_sigortali_calc,
                        "_bi_hasar_raw": bi_hasar_senaryo_calc,
                        "_total_prim_raw": toplam_prim_calc, # Grafik için de güncellenmiş prim
                        "_hasar_tipi_key": hasar_tipi_key_calc, # Grafik ve filtreleme için
                        "_etiket_key": etiket_key_calc # Filtreleme için
                    })
            if results_for_location_table_calc:
                all_locations_results_list_calc.extend(results_for_location_table_calc)

        if all_locations_results_list_calc:
            st.session_state.all_results_df_calculated = pd.DataFrame(all_locations_results_list_calc)
            st.session_state.calculation_performed = True
        else:
            st.session_state.all_results_df_calculated = None
            st.session_state.calculation_performed = False # Eğer hiçbir sonuç üretilemediyse
            st.info(tr("no_damage_calculated_for_loc")) # Buton içinde gösterilebilir
        st.rerun() # Sayfayı yeniden çalıştırarak aşağıdaki gösterim kısmını tetikle

    # --- SONUÇ GÖSTERİM KISMI (BUTON DIŞINDA, SESSION_STATE'DEN OKUYARAK) ---
    if st.session_state.get('calculation_performed', False):
        st.subheader(tr("scenario_recalculation_results_header")) # Ana başlık

        # Lokasyon bazlı metrikleri göster (session_state'den)
        if 'loc_specific_metrics_calc' in st.session_state:
            for i, loc_summary_disp in enumerate(locations_summary):
                st.markdown(f"### {tr('location_label')} {i+1} ({loc_summary_disp.get('group', 'N/A')})")
                loc_metrics = st.session_state.loc_specific_metrics_calc.get(i, {})
                
                mod_hasar_oranlari_disp = loc_metrics.get("modifiye_hasar_oranlari")
                if mod_hasar_oranlari_disp:
                    st.write(f"**{tr('calculated_modified_damage_ratios')}:**")
                    col_r1_disp, col_r2_disp, col_r3_disp = st.columns(3)
                    col_r1_disp.metric(label=tr("minor_loss_ratio"), value=f"{mod_hasar_oranlari_disp.get('minor', 0.0):.2%}")
                    col_r2_disp.metric(label=tr("expected_loss_ratio"), value=f"{mod_hasar_oranlari_disp.get('expected', 0.0):.2%}")
                    col_r3_disp.metric(label=tr("severe_loss_ratio"), value=f"{mod_hasar_oranlari_disp.get('severe', 0.0):.2%}")

                if loc_summary_disp.get("bi_sum_loc", 0.0) > 0:
                    bi_carpan_disp = loc_metrics.get("bi_carpan")
                    bi_hasarlar_dict_disp = loc_metrics.get("bi_hasarlar_dict")
                    if bi_carpan_disp is not None: # 0 da geçerli bir değer olabilir
                        st.markdown("---")
                        st.subheader(tr("bi_calculations_header"))
                        st.metric(label=tr("bi_multiplier_label"), value=f"{bi_carpan_disp:.2f}x")
                    if bi_hasarlar_dict_disp:
                        st.write(f"**{tr('calculated_bi_damage_ratios_and_amounts')}:**")
                        cols_bi_r_disp_loc = st.columns(len(bi_hasarlar_dict_disp))
                        col_idx_disp_loc = 0
                        for scenario_name_disp, bi_data_disp in bi_hasarlar_dict_disp.items():
                            with cols_bi_r_disp_loc[col_idx_disp_loc]:
                                st.metric(label=f"{tr(scenario_name_disp)} {tr('bi_loss_ratio_col')}", value=f"{bi_data_disp.get('oran', 0.0):.2%}")
                                st.metric(label=f"{tr(scenario_name_disp)} {tr('bi_loss_amount_col')}", value=f"{bi_data_disp.get('hasar', 0):,.0f} {currency}")
                            col_idx_disp_loc +=1
                    elif bi_carpan_disp is not None: # BI çarpanı hesaplandı ama hasar yoksa
                        st.info(tr("no_bi_damage_calculated_for_loc"))
                st.markdown("---")

        # Birleştirilmiş tablo ve filtreler
        if 'all_results_df_calculated' in st.session_state and st.session_state.all_results_df_calculated is not None:
            df_display_master = st.session_state.all_results_df_calculated.copy()

            # Sütun adlarını çevir (DataFrame'de)
            # Ham sütun adlarından çevrilmiş sütun adlarına bir harita oluştur
            column_rename_map = {
                "alternative_col_raw": tr("alternative_col"), "label_col_raw": tr("label_col"),
                "pd_premium_raw": tr("pd_premium_col"), "bi_premium_raw": tr("bi_premium_col"),
                "total_premium_raw": tr("total_premium_col"), "scenario_type_key_raw": tr("scenario_type_col"),
                "gross_damage_raw": tr("gross_damage_col"), "insurer_share_raw": tr("insurer_share_col"),
                "insured_share_raw": tr("insured_share_col"), "bi_loss_amount_raw": tr("bi_loss_amount_col"),
                "tcor_raw": tr("tcor_col")
                # _ ile başlayan ham değerler için çeviriye gerek yok, onlar arka planda kalacak
            }
            # Sadece var olan sütunları çevir
            df_display_master.rename(columns={k: v for k, v in column_rename_map.items() if k in df_display_master.columns}, inplace=True)
            
            # scenario_type_col içindeki key'leri de çevir
            if tr("scenario_type_col") in df_display_master.columns:
                 df_display_master[tr("scenario_type_col")] = df_display_master["_hasar_tipi_key"].apply(lambda x: tr(x))
            if tr("label_col") in df_display_master.columns:
                 df_display_master[tr("label_col")] = df_display_master["_etiket_key"].apply(lambda x: tr(x))


            st.subheader(tr("filter_options_label"))
            col_f1_disp, col_f2_disp = st.columns(2)

            # Filtreler için session_state anahtarları
            filter_alt_key_ss = "scenario_filter_alt_type"
            filter_damage_key_ss = "scenario_filter_damage_type"

            with col_f1_disp:
                filter_alternative_type_options_disp = {
                    "all": tr("filter_show_all"), "best_tcor": tr("filter_best_alternative"),
                    "shield_icon": tr("filter_max_protection"), "low_risk_icon": tr("filter_min_premium")
                }
                selected_filter_alt_type_key_disp = st.selectbox(
                    tr("filter_options_label"), options=list(filter_alternative_type_options_disp.keys()),
                    format_func=lambda x: filter_alternative_type_options_disp[x],
                    key=filter_alt_key_ss, # Session state'i kullan
                    index=list(filter_alternative_type_options_disp.keys()).index(st.session_state.get(filter_alt_key_ss, "all"))
                )

            with col_f2_disp:
                # Hasar tipi seçeneklerini dinamik olarak al (ilk lokasyonun metriklerinden)
                damage_keys_for_filter_disp = ['minor', 'expected', 'severe'] # Varsayılan
                if 'loc_specific_metrics_calc' in st.session_state and 0 in st.session_state.loc_specific_metrics_calc:
                    if 'modifiye_hasar_oranlari' in st.session_state.loc_specific_metrics_calc[0]:
                        damage_keys_for_filter_disp = list(st.session_state.loc_specific_metrics_calc[0]['modifiye_hasar_oranlari'].keys())
                
                damage_type_options_keys_filter_disp = ["all_damage_types"] + damage_keys_for_filter_disp
                damage_type_options_display_filter_disp = [tr("all_damage_types")] + [tr(key) for key in damage_keys_for_filter_disp]
                
                selected_damage_type_display_disp = st.selectbox(
                    tr("filter_by_damage_type_label"), options=damage_type_options_display_filter_disp,
                    key=filter_damage_key_ss,
                    index=damage_type_options_display_filter_disp.index(st.session_state.get(filter_damage_key_ss, tr("all_damage_types")))
                            if st.session_state.get(filter_damage_key_ss, tr("all_damage_types")) in damage_type_options_display_filter_disp else 0
                )
                selected_damage_type_key_filter_disp = "all"
                if selected_damage_type_display_disp != tr("all_damage_types"):
                    for k_filt_disp, v_tr_filt_disp in zip(damage_keys_for_filter_disp, [tr(key) for key in damage_keys_for_filter_disp]):
                        if selected_damage_type_display_disp == v_tr_filt_disp:
                            selected_damage_type_key_filter_disp = k_filt_disp
                            break
            
            df_filtered_for_display = df_display_master.copy()

            if selected_filter_alt_type_key_disp == "best_tcor":
                if not df_filtered_for_display.empty and "tcor_raw" in df_filtered_for_display.columns:
                    best_tcor_val_disp_filt = df_filtered_for_display["tcor_raw"].min()
                    df_filtered_for_display = df_filtered_for_display[df_filtered_for_display["tcor_raw"] == best_tcor_val_disp_filt]
            elif selected_filter_alt_type_key_disp in ["shield_icon", "low_risk_icon"]:
                 df_filtered_for_display = df_filtered_for_display[df_filtered_for_display["_etiket_key"] == selected_filter_alt_type_key_disp]

            if selected_damage_type_key_filter_disp != "all":
                df_filtered_for_display = df_filtered_for_display[df_filtered_for_display["_hasar_tipi_key"] == selected_damage_type_key_filter_disp]

            display_columns_final = [
                tr("alternative_col"), tr("label_col"), tr("pd_premium_col"), tr("bi_premium_col"),
                tr("total_premium_col"), tr("scenario_type_col"), tr("gross_damage_col"),
                tr("insurer_share_col"), tr("insured_share_col"), tr("bi_loss_amount_col"), tr("tcor_col")
            ]
            # Sadece var olan sütunları göster
            display_columns_final_existing = [col for col in display_columns_final if col in df_filtered_for_display.columns]

            if not df_filtered_for_display.empty:
                # Formatlama için (sayısal sütunlar)
                # Bu formatlamayı en sonda yapmak daha iyi olabilir, _raw değerleri etkilenmesin diye.
                # Şimdilik dataframe'i olduğu gibi gösterelim, formatlama daha sonra eklenebilir.
                st.dataframe(df_filtered_for_display[display_columns_final_existing], use_container_width=True, hide_index=True)

                # --- AI Özet Kutusu ---
                st.subheader(tr("ai_summary_header"))
                # AI özeti için df_display_master (filtrelenmemiş ama çevrilmiş sütun adları olan) kullanılabilir
                if not df_display_master.empty and "tcor_raw" in df_display_master.columns:
                    idx_min_tcor_disp = df_display_master["tcor_raw"].idxmin()
                    best_alt_tcor_disp = df_display_master.loc[idx_min_tcor_disp, tr("alternative_col")]
                    best_scenario_tcor_key_disp = df_display_master.loc[idx_min_tcor_disp, "_hasar_tipi_key"] # Ham key'i al
                    best_scenario_tcor_display_val = tr(best_scenario_tcor_key_disp) # Sonra çevir
                    best_tcor_value_disp = df_display_master.loc[idx_min_tcor_disp, "tcor_raw"]
                    
                    recommended_alt_df_disp = df_display_master[df_display_master["_etiket_key"] == "balance_icon"]
                    recommended_alt_name_disp = recommended_alt_df_disp[tr("alternative_col")].iloc[0] if not recommended_alt_df_disp.empty else "N/A"

                    ai_text_disp = tr("ai_summary_placeholder").format(
                        best_alt_tcor=best_alt_tcor_disp, best_scenario_tcor=best_scenario_tcor_display_val,
                        best_tcor_value=f"{best_tcor_value_disp:,.0f}", currency=currency, recommended_alt=recommended_alt_name_disp
                    )
                    st.info(ai_text_disp)

                # --- Grafikler ---
                st.subheader(tr("visualizations_header"))
                chart_scenario_key_for_graphs = 'expected' # Grafik için varsayılan senaryo
                
                # Grafik için df_filtered_for_display'i kullanacağız (tablo filtreleri uygulanmış)
                # ve ayrıca chart_scenario_key_for_graphs'a göre filtreleyeceğiz
                df_for_graphs_final = df_filtered_for_display[df_filtered_for_display["_hasar_tipi_key"] == chart_scenario_key_for_graphs].copy()

                if not df_for_graphs_final.empty:
                    # Bar Grafik
                    # Grafik için _alternative_col_raw yerine çevrilmiş tr("alternative_col") kullanalım
                    # df_melted için de _raw sütunları kullanalım
                    df_melted_graph = df_for_graphs_final.melt(
                        id_vars=[tr("alternative_col")], # Çevrilmiş sütun adını kullanalım
                        value_vars=["_pd_sigortali_payi_raw", "_bi_hasar_raw", "_total_prim_raw", "_pd_sirket_payi_raw"],
                        var_name="Pay Tipi Key", # Geçici isim
                        value_name="Tutar"
                    )
                    pay_tipi_display_names_graph = {
                        "_pd_sigortali_payi_raw": tr("insured_share_col"), "_bi_hasar_raw": tr("bi_loss_amount_col"),
                        "_total_prim_raw": tr("total_premium_col"), "_pd_sirket_payi_raw": tr("insurer_share_col")
                    }
                    df_melted_graph["Pay Tipi"] = df_melted_graph["Pay Tipi Key"].map(pay_tipi_display_names_graph)
                    
                    color_map_graph = {
                        tr("insured_share_col"): 'orange', tr("bi_loss_amount_col"): 'salmon',
                        tr("total_premium_col"): 'skyblue', tr("insurer_share_col"): 'lightgreen'
                    }
                    category_orders_graph = {
                        "Pay Tipi": [tr("total_premium_col"), tr("insured_share_col"), tr("bi_loss_amount_col"), tr("insurer_share_col")]
                    }

                    st.markdown(f"#### {tr('chart_title_risk_distribution_by_alternative').format(scenario=tr(chart_scenario_key_for_graphs))}")
                    fig_stacked_bar_graph = px.bar(
                        df_melted_graph, x=tr("alternative_col"), y="Tutar", color="Pay Tipi",
                        labels={tr("alternative_col"): tr("alternative_col"), "Tutar": f"{tr('amount_label')} ({currency})", "Pay Tipi": tr("share_type_label")},
                        barmode='stack', color_discrete_map=color_map_graph, category_orders=category_orders_graph, height=500
                    )
                    fig_stacked_bar_graph.update_layout(
                        yaxis_title=f"{tr('amount_label')} ({currency})", xaxis_title=tr("alternative_col"), legend_title_text=tr("share_type_label")
                    )
                    st.plotly_chart(fig_stacked_bar_graph, use_container_width=True)
                    
                    st.markdown("---")
                    st.markdown(f"#### {tr('chart_title_donut_per_alternative').format(scenario=tr(chart_scenario_key_for_graphs))}")
                    
                    num_alt_donut_graph = len(df_for_graphs_final[tr("alternative_col")].unique()) # Benzersiz alternatif sayısını al
                    if num_alt_donut_graph > 0:
                        cols_donut_graph = st.columns(num_alt_donut_graph)
                        col_idx_donut_graph = 0
                        # df_for_graphs_final'ı alternatif bazında gruplayarak döngüye alabiliriz
                        # veya unique alternatifler üzerinden dönebiliriz.
                        # Şu anki yapı df_for_graphs_final zaten tek bir senaryo için filtrelenmiş olmalı.
                        for alt_name_graph, group_data_graph in df_for_graphs_final.groupby(tr("alternative_col")):
                             if col_idx_donut_graph < num_alt_donut_graph : # Kolon sayısını aşmamak için
                                with cols_donut_graph[col_idx_donut_graph]:
                                    # Her gruptan ilk satırı alabiliriz, çünkü değerler aynı olmalı (tek senaryo için)
                                    row_graph = group_data_graph.iloc[0]
                                    sirket_payi_pd_graph = row_graph["_pd_sirket_payi"]
                                    prim_graph = row_graph["_total_prim_raw"]
                                    sigortali_pd_graph = row_graph["_pd_sigortali_payi"]
                                    bi_hasar_graph = row_graph["_bi_hasar_raw"]

                                    labels_donut_graph = [tr("total_premium_col"), tr("insured_share_col"), tr("bi_loss_amount_col"), tr("insurer_share_col")]
                                    values_donut_graph = [prim_graph, sigortali_pd_graph, bi_hasar_graph, sirket_payi_pd_graph]
                                    
                                    valid_indices_graph = [i_g for i_g, v_g in enumerate(values_donut_graph) if v_g > 0]
                                    labels_donut_filtered_graph = [labels_donut_graph[i_g] for i_g in valid_indices_graph]
                                    values_donut_filtered_graph = [values_donut_graph[i_g] for i_g in valid_indices_graph]

                                    if values_donut_filtered_graph:
                                        fig_donut_graph = px.pie(
                                            names=labels_donut_filtered_graph, values=values_donut_filtered_graph, title=f"{alt_name_graph}",
                                            hole=0.4, color_discrete_map=color_map_graph, height=350
                                        )
                                        fig_donut_graph.update_layout(
                                            showlegend=True, legend_orientation="h", legend_yanchor="bottom", legend_y= -0.2,
                                            margin=dict(t=50, b=80, l=0, r=0)
                                        )
                                        st.plotly_chart(fig_donut_graph, use_container_width=True)
                                col_idx_donut_graph += 1
                else:
                    st.info(tr("no_data_for_selected_scenario_chart"))
            else:
                st.info(tr("no_results_for_filters"))
        elif st.session_state.get('calculation_performed', False) and st.session_state.all_results_df_calculated is None:
             st.info(tr("no_damage_calculated_for_loc")) # Butona basıldı ama sonuç üretilemedi

else: # scenario_data yoksa
    st.warning(tr("no_scenario_data_warning"))
    st.page_link("pages/calculate.py", label=tr("go_to_calculation_page"), icon="⬅️")

# Gerekli yeni çeviriyi ekleyin (zaten bir önceki adımda eklenmiş olmalı):
# "no_results_for_filters": {
# "TR": "Seçilen filtrelere uygun sonuç bulunamadı. Lütfen filtrelerinizi değiştirin veya tüm sonuçları görmek için sıfırlayın.",
# "EN": "No results found for the selected filters. Please change your filters or reset to see all results."
# },


st.markdown("---")
st.markdown(f"""
<div style='text-align: center; font-size: 0.9em; color: #666; padding: 10px; background-color: #f8f9fa; border-radius: 5px; margin-top: 20px;'>
    ⚠️ <strong>{tr('disclaimer_title')}:</strong> {tr('disclaimer_text')}
</div>
""", unsafe_allow_html=True)

# Footer
st.markdown(f"<div class='footer'>{T['footer'][lang]}</div>", unsafe_allow_html=True)