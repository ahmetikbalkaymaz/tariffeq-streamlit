import streamlit as st
from utils.visitor_logger import track_page_visit, log_page_exit

# Sayfa konfigürasyonu
st.set_page_config(
    page_title="TariffEQ - Hesaplama",
    layout="wide",
    page_icon="🚀"
)

# Sayfa ziyaretini takip et
track_page_visit("Calculate")

# Önceki sayfadan çıkışı logla
if 'previous_page' in st.session_state and st.session_state.previous_page != "Calculate":
    log_page_exit(st.session_state.previous_page)

st.session_state.previous_page = "Calculate"

from datetime import datetime, timedelta, date # 'date' import'unu eklediğinizden emin olun
from translations import T 
import pandas as pd
from utils import premium_calculations as pc
from utils import ui_helpers as ui
from utils import pdf_generator
from utils import excel_generator # YENİ: Excel oluşturucuyu import et

# ------------------------------------------------------------
# STREAMLIT CONFIG (must be first)
# ------------------------------------------------------------

# Dil seçimi için session state başlatma (EĞER YOKSA)
if 'lang' not in st.session_state:
    st.session_state.lang = "TR"  # Varsayılan dil

# Dil değişkenini session state'den al
lang = st.session_state.lang

# Dil-bağımsız anahtarlar için sabitler
CALC_MODULE_FIRE = "fire_module"
CALC_MODULE_CAR = "car_module"

# Custom CSS for styling (Değişiklik yok)
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

# Kenar Çubuğu Navigasyonu ve Dil Seçimi (Değişiklik yok)
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

# tr fonksiyonu burada kalıyor, ana UI tarafından kullanılıyor
def tr(key: str) -> str:
    # `T` sözlüğünüzde "location_name" ve "location_name_help" anahtarlarını eklemeyi unutmayın.
    # Örnek:
    # "location_name": {"TR": "Lokasyon Adı / Adresi", "EN": "Location Name / Address"},
    # "location_name_help": {"TR": "Bu lokasyon için tanımlayıcı bir isim veya adres girin.", "EN": "Enter a descriptive name or address for this location."},
    return T.get(key, {}).get(lang, key)

# Sabit tablolar pc modülüne taşındı
# Hesaplama fonksiyonları pc modülüne taşındı
# UI yardımcı fonksiyonları ui modülüne taşındı

# ------------------------------------------------------------
# SCENARIO DATA PREPARATION (Burada kalabilir veya scenario_utils.py'ye taşınabilir)
# ------------------------------------------------------------
def prepare_scenario_data_for_session(
    scenario_definitions_list, 
    groups_determined_val, 
    currency_fire_val, 
    fx_rate_fire_val, 
    inflation_rate_val,
    total_entered_pd_orig_ccy_val,
    total_entered_bi_orig_ccy_val,
    num_locations_val,
    main_koas_val,
    main_deduct_val
    ):
    """Senaryo hesaplama verilerini hazırlar ve session_state'e kaydeder."""
    calculated_scenarios_for_session = []

    for scenario_def in scenario_definitions_list:
        scenario_results_per_group = []
        for group_key, data_group in groups_determined_val.items():
            # pc.calculate_fire_premium çağrısı
            pd_scenario_premium_try, bi_scenario_premium_try, _, _, _, _ = pc.calculate_fire_premium(
                data_group["building_type"], data_group["risk_group"], currency_fire_val,
                data_group["building"], data_group["fixture"], data_group["decoration"], data_group["commodity"], data_group["safe"],
                data_group["machinery"], data_group["bi"],
                data_group.get("ec_fixed", 0.0), data_group.get("ec_mobile", 0.0), data_group.get("mk_fixed", 0.0), data_group.get("mk_mobile", 0.0),
                scenario_def["koas_key"], scenario_def["deduct_key"],
                fx_rate_fire_val, inflation_rate_val,
                skip_limit_warnings= True
            )
            scenario_results_per_group.append({
                "group_key": group_key,
                "pd_premium_try": pd_scenario_premium_try,
                "bi_premium_try": bi_scenario_premium_try
            })
        calculated_scenarios_for_session.append({
            "name": tr(scenario_def["name_key"]),
            "koas_key": scenario_def["koas_key"],
            "deduct_key": scenario_def["deduct_key"],
            "results_per_group": scenario_results_per_group
        })

    st.session_state.scenario_data_for_page = {
        "num_locations": num_locations_val,
        "total_pd_sum_orig_ccy": total_entered_pd_orig_ccy_val,
        "total_bi_sum_orig_ccy": total_entered_bi_orig_ccy_val,
        "currency_code": currency_fire_val,
        "fx_rate_at_calculation": fx_rate_fire_val,
        "groups_details": groups_determined_val,
        "calculated_scenarios": calculated_scenarios_for_session,
        "inflation_rate_at_calculation": inflation_rate_val,
        "main_koas": main_koas_val,
        "main_deduct": main_deduct_val
    }

# ------------------------------------------------------------
# STREAMLIT UI MAIN
# ------------------------------------------------------------
calc_title_full = tr("calc_title")
descriptive_part = ""
brand_name = "TariffEQ" 
prefix_to_remove = brand_name 

if calc_title_full.startswith(prefix_to_remove):
    descriptive_part = calc_title_full[len(prefix_to_remove):]
elif calc_title_full == brand_name:
    descriptive_part = "" 
else:
    descriptive_part = calc_title_full

st.markdown('<h2 class="section-header">📊 ' + (tr("select_calc")) + '</h2>', unsafe_allow_html=True)

if 'active_calc_module' not in st.session_state:
    st.session_state.active_calc_module = CALC_MODULE_FIRE 

col_btn1, col_btn2 = st.columns(2)
with col_btn1:
    if st.button(tr("select_fire_button"), use_container_width=True, key="btn_select_fire"):
        st.session_state.active_calc_module = CALC_MODULE_FIRE
        if 'export_data' in st.session_state:
            del st.session_state['export_data'] # Modül değiştiğinde eski veriyi sil
with col_btn2:
    if st.button(tr("select_car_button"), use_container_width=True, key="btn_select_car"):
        st.session_state.active_calc_module = CALC_MODULE_CAR
        if 'export_data' in st.session_state:
            del st.session_state['export_data'] # Modül değiştiğinde eski veriyi sil


if st.session_state.active_calc_module == CALC_MODULE_FIRE:
    st.markdown(f'<h3 class="section-header">{tr("fire_header")}</h3>', unsafe_allow_html=True)

    fire_general_col1, fire_general_col2 = st.columns(2)
    with fire_general_col1:
        currency_fire = st.selectbox(tr("currency"), ["TRY", "USD", "EUR"], key="main_fire_module_currency")
    with fire_general_col2:
        fx_rate_fire, fx_info_fire = ui.fx_input(currency_fire, "main_fire_module")
    
    num_locations = st.number_input(tr("num_locations"), min_value=1, max_value=10, value=1, step=1, help=tr("num_locations_help"))
    
    locations_data = []
    base_groups = [chr(65 + i) for i in range(max(1, num_locations))] 
    
    # Kümül grupları için seçilen deprem bölgelerini saklamak için bir sözlük
    group_risk_mapping = {}
    
    for i in range(num_locations):
        expander_label = f"Lokasyon {i + 1}" if lang == "TR" else f"Location {i + 1}"
        with st.expander(expander_label, expanded=True if i == 0 else False):
            # YENİ: Lokasyon adı girişi eklendi
            location_name = st.text_input(
                tr("location_name"), 
                value=expander_label, 
                key=f"location_name_{i}",
                help=tr("location_name_help")
            )

            col1, col2 = st.columns(2)
            with col1:
                building_type = st.selectbox(tr("building_type"), ["Betonarme", "Diğer"], key=f"building_type_{i}", help=tr("building_type_help"))
                
                # Kümül grubu seçimi, deprem bölgesi seçiminden önce yapılmalı
                group_for_this_location = "A"
                if num_locations > 1:
                    # Bu selectbox'ı deprem bölgesi seçiminden önceye taşıdık
                    group_for_this_location = st.selectbox(
                        tr("location_group"), 
                        options=base_groups,
                        format_func=lambda x: tr("group_label_format").format(group_char=x),
                        key=f"group_{i}", 
                        help=tr("location_group_help") + " " + tr("location_group_help_cumulative")
                    )

                # Deprem bölgesi seçimi için mantığı burada kuruyoruz
                risk_group_options = [1, 2, 3, 4, 5, 6, 7]
                is_disabled = False
                help_text = tr("risk_group_help")
                
                # Eğer bu lokasyonun kümül grubu için daha önce bir deprem bölgesi seçilmişse
                if group_for_this_location in group_risk_mapping:
                    # Seçimi devre dışı bırak
                    is_disabled = True
                    # Değeri, o grup için daha önce seçilen değere ayarla
                    default_value = group_risk_mapping[group_for_this_location]
                    help_text = tr("risk_group_help_disabled") # Yeni bir çeviri anahtarı eklemek iyi olur
                else:
                    # Bu grup için ilk defa seçim yapılıyor, varsayılan değer 1 olsun
                    default_value = 1

                risk_group = st.selectbox(
                    tr("risk_group"), 
                    options=risk_group_options, 
                    index=risk_group_options.index(default_value), # Değeri index ile ayarla
                    key=f"risk_group_{i}", 
                    help=help_text,
                    disabled=is_disabled
                )
                
                # Eğer seçim etkinse (yani bu grup için ilk lokasyonsa), seçilen değeri haritaya kaydet
                if not is_disabled:
                    group_risk_mapping[group_for_this_location] = risk_group

                earthquake_zone_page_url = "earthquake_zones"
                button_label = tr("learn_earthquake_zone_button")
                st.markdown(f"""
                <a href="{earthquake_zone_page_url}" target="_blank" class="styled-link-button">
                    {button_label}
                </a>
                """, unsafe_allow_html=True)
                
            with col2:
                # Kümül grubu seçimi yukarı taşındığı için burası boş veya başka bir widget için kullanılabilir
                # st.caption(tr("location_group_cumulative_info")) # Bu da yukarı taşınabilir
                if num_locations > 1:
                    st.caption(tr("location_group_cumulative_info"))


            st.markdown(f"#### {tr('insurance_sums')}")
            main_col1, main_col2, ec_mk_main_col = st.columns([2, 2, 3]) 
            with main_col1:
                building = st.number_input(tr("building_sum"), min_value=0, value=0, step=100000,key=f"building_{i}", help=tr("building_sum_help"), format="%d")
                if building > 0: st.write(f"{tr('entered_value')}: {ui.format_number(building, currency_fire)}")
                fixture = st.number_input(tr("fixture_sum"), min_value=0, value=0, step=100000,key=f"fixture_{i}", help=tr("fixture_sum_help"), format="%d")
                if fixture > 0: st.write(f"{tr('entered_value')}: {ui.format_number(fixture, currency_fire)}")
                decoration = st.number_input(tr("decoration_sum"), min_value=0, value=0, step=100000,key=f"decoration_{i}", help=tr("decoration_sum_help"), format="%d")
                if decoration > 0: st.write(f"{tr('entered_value')}: {ui.format_number(decoration, currency_fire)}")
                bi = st.number_input(tr("bi"), min_value=0, value=0, step=100000,key=f"bi_{i}", help=tr("bi_help"), format="%d")
                if bi > 0: st.write(f"{tr('entered_value')}: {ui.format_number(bi, currency_fire)}")
            with main_col2:
                commodity = st.number_input(tr("commodity_sum"), min_value=0, value=0, step=100000,key=f"commodity_{i}", help=tr("commodity_sum_help"), format="%d")
                commodity_is_subscription = st.checkbox(tr("commodity_is_subscription"), key=f"commodity_is_subscription_{i}", help=tr("commodity_is_subscription_help"))
                if commodity > 0:
                    display_comm_value = commodity * 0.40 if commodity_is_subscription else commodity
                    st.write(f"{tr('entered_value')}: {ui.format_number(commodity, currency_fire)} ({tr('effective_value')}: {ui.format_number(display_comm_value, currency_fire)})" if commodity_is_subscription else f"{tr('entered_value')}: {ui.format_number(commodity, currency_fire)}")
                safe = st.number_input(tr("safe_sum"), min_value=0, value=0, step=100000,key=f"safe_{i}", help=tr("safe_sum_help"), format="%d")
                if safe > 0: st.write(f"{tr('entered_value')}: {ui.format_number(safe, currency_fire)}")
                machinery = st.number_input(tr("mk_sum"), min_value=0, value=0, step=100000,key=f"machinery_{i}", help=tr("mk_sum_help"), format="%d")
                if machinery > 0: st.write(f"{tr('entered_value')}: {ui.format_number(machinery, currency_fire)}")
            
            ec_fixed, ec_mobile, mk_mobile = 0.0, 0.0, 0.0 # mk_fixed kaldırıldı
            with ec_mk_main_col:
                st.markdown(f"###### {tr('ec_mk_cover_options_header')}")
                include_ec_mk_cover = st.checkbox(tr("include_ec_mk_cover"), key=f"include_ec_mk_cover_{i}", value=True)
                if include_ec_mk_cover:
                    ec_fixed = st.number_input(tr("ec_fixed"), min_value=0, value=0, step=100000, key=f"ec_fixed_{i}", help=tr("ec_fixed_help"), format="%d")
                    if ec_fixed > 0: st.write(f"{tr('entered_value')}: {ui.format_number(ec_fixed, currency_fire)}")
                    ec_mobile = st.number_input(tr("ec_mobile"), min_value=0, value=0, step=100000, key=f"ec_mobile_{i}", help=tr("ec_mobile_help"), format="%d")
                    if ec_mobile > 0: st.write(f"{tr('entered_value')}: {ui.format_number(ec_mobile, currency_fire)}")
                    # st.markdown(f"**{tr('mk_cover_subheader')}**") 
                    # mk_fixed = st.number_input(tr("mk_fixed"), min_value=0.0, value=0.0, step=100000.0, key=f"mk_fixed_cover_{i}", help=tr("mk_fixed_cover_help"), format="%.2f")
                    # if mk_fixed > 0: st.write(f"{tr('entered_value')}: {ui.format_number(mk_fixed, currency_fire)}")
                    mk_mobile = st.number_input(tr("mk_mobile"), min_value=0, value=0, step=100000, key=f"mk_mobile_cover_{i}", help=tr("mk_mobile_cover_help"), format="%d")
                    if mk_mobile > 0: st.write(f"{tr('entered_value')}: {ui.format_number(mk_mobile, currency_fire)}")
            
            locations_data.append({
                "location_name": location_name, # YENİ: Lokasyon adı eklendi
                "group": group_for_this_location,
                "building_type": building_type, "risk_group": risk_group,
                "building": building, "fixture": fixture, "decoration": decoration,
                "commodity": commodity, "commodity_is_subscription": commodity_is_subscription,
                "safe": safe, "machinery": machinery, "bi": bi,
                "ec_fixed": ec_fixed if include_ec_mk_cover else 0.0,
                "ec_mobile": ec_mobile if include_ec_mk_cover else 0.0,
                # "mk_fixed": mk_fixed if include_ec_mk_cover else 0.0, # Kaldırıldı
                "mk_mobile": mk_mobile if include_ec_mk_cover else 0.0,
                "include_ec_mk_cover": include_ec_mk_cover
            })
    
    if locations_data:
        ui.display_current_total_sums(locations_data, currency_fire) 

    st.markdown(f"#### {tr('coinsurance_deductible')}")
    col5, col6, col7 = st.columns(3)
    with col5:
        koas = st.selectbox(tr("koas"), list(pc.koasurans_indirimi.keys()), help=tr("koas_help"))
    with col6:
        deduct = st.selectbox(tr("deduct"), sorted(list(pc.muafiyet_indirimi.keys()), reverse=True), index=4, help=tr("deduct_help"))
    with col7:
        inflation_rate = st.number_input(tr("inflation_rate"), min_value=0.0, value=0.0, step=5.0, help=tr("inflation_rate_help"), format="%.2f")

    st.markdown("---")
    # --- LİMİTLİ POLİÇE BÖLÜMÜ ---
    st.markdown(f"#### {tr('limited_policy_info_header')}")
    
    # Toplam PD bedelini hesapla (sadece bu bölüm için geçici olarak)
    total_pd_for_limit_check = 0.0
    for loc_data in locations_data:
        commodity_value = loc_data["commodity"] * 0.40 if loc_data["commodity_is_subscription"] else loc_data["commodity"]
        total_pd_for_limit_check += (
            loc_data["building"] + loc_data["fixture"] + loc_data["decoration"] + 
            commodity_value + loc_data["safe"] + loc_data["machinery"]
        )
    
    total_pd_try = total_pd_for_limit_check * fx_rate_fire
    MIN_LIMIT_TRY = 420_000_000
    
    limit_col1, limit_col2 = st.columns(2)
    with limit_col1:
        apply_limited_policy = st.checkbox(
            tr("apply_limited_policy"), 
            key="apply_limited_policy",
            help=tr("apply_limited_policy_help"),
            disabled=total_pd_try < MIN_LIMIT_TRY
        )
    
    limited_policy_limit = 0.0
    if apply_limited_policy:
        with limit_col2:
            limited_policy_limit = st.number_input(
                tr("limited_policy_limit"),
                min_value=0.0,
                value=0.0,
                step=1_000_000.0,
                key="limited_policy_limit",
                help=tr("limited_policy_limit_help"),
                format="%.2f"
            )
            if limited_policy_limit > 0:
                st.write(f"{tr('entered_value')}: {ui.format_number(limited_policy_limit, currency_fire)}")

    if total_pd_try < MIN_LIMIT_TRY and apply_limited_policy:
         st.warning(tr("warning_limit_too_low").format(min_limit_try=f"{MIN_LIMIT_TRY:,.0f}"))
         st.session_state.apply_limited_policy = False # Checkbox'ı geri al
         apply_limited_policy = False


    if st.button(tr("btn_calc"), key="fire_calc"):
        if 'export_data' in st.session_state:
            del st.session_state['export_data'] # Önceki hesaplama verilerini temizle
        if 'scenario_data_for_page' in st.session_state:
            del st.session_state['scenario_data_for_page'] # Önceki senaryo verilerini temizle

        # --- YENİ: Değer Girişi Kontrolü ---
        total_sum_insured = sum(
            loc.get('building', 0) + loc.get('fixture', 0) + loc.get('decoration', 0) +
            loc.get('commodity', 0) + loc.get('safe', 0) + loc.get('machinery', 0) +
            loc.get('bi', 0) + loc.get('ec_fixed', 0) + loc.get('ec_mobile', 0) +
            loc.get('mk_mobile', 0)
            for loc in locations_data
        )

        if total_sum_insured <= 0:
            st.warning(tr("warning_no_sum_insured")) # Bu çeviri anahtarını translations.py'ye eklemeyi unutmayın.
            st.stop()
        # --- KONTROL SONU ---


        total_entered_pd_orig_ccy = 0.0
        total_entered_bi_orig_ccy = 0.0
        for loc_data_item in locations_data:
            # Abonman emtia değerini hesaplamalarda doğru kullanmak için geçici bir anahtar ekle
            if loc_data_item["commodity_is_subscription"]:
                loc_data_item["commodity_for_calc"] = loc_data_item["commodity"] * 0.40
            else:
                loc_data_item["commodity_for_calc"] = loc_data_item["commodity"]

            total_entered_pd_orig_ccy += (
                loc_data_item["building"] + loc_data_item["fixture"] +
                loc_data_item["decoration"] + loc_data_item["commodity_for_calc"] +
                loc_data_item["safe"] + loc_data_item["machinery"]
            )
            total_entered_bi_orig_ccy += loc_data_item["bi"]

        proceed_with_calculation = True
        total_pd_sum_try = total_entered_pd_orig_ccy * fx_rate_fire

        # Kural: Toplam PD bedeli 3.5 Milyar TL'den küçükse belirli koasürans ve muafiyetler kısıtlanır.
        if total_pd_sum_try < 3_500_000_000:
            if koas in ["90/10", "100/0"]:
                st.error(tr("error_koas_not_allowed").format(koas_rate=koas))
                proceed_with_calculation = False
            if deduct < 2:
                st.error(tr("error_deduct_not_allowed").format(deduct_rate=deduct))
                proceed_with_calculation = False

        st.markdown("---")
        st.markdown(f"<h5>{tr('entered_sums_summary_header')}</h5>", unsafe_allow_html=True)
        st.markdown(f'<div class="info-box">ℹ️ <b>{tr("total_entered_pd_sum")}:</b> {ui.format_number(total_entered_pd_orig_ccy, currency_fire)}</div>', unsafe_allow_html=True)
        if total_entered_bi_orig_ccy > 0:
             st.markdown(f'<div class="info-box">ℹ️ <b>{tr("total_entered_bi_sum")}:</b> {ui.format_number(total_entered_bi_orig_ccy, currency_fire)}</div>', unsafe_allow_html=True)
        st.markdown("---")

        if proceed_with_calculation:
            # --- LİMİTLİ POLİÇE HESAPLAMALARI (EĞER SEÇİLDİYSE) ---
            limited_policy_multiplier = 1.0
            if apply_limited_policy:
                if limited_policy_limit <= 0 or limited_policy_limit >= total_entered_pd_orig_ccy:
                    st.error(tr("warning_limit_value_invalid").format(total_pd_sum=ui.format_number(total_entered_pd_orig_ccy, currency_fire)))
                    st.stop()
                else:
                    limit_ratio_float = total_entered_pd_orig_ccy / limited_policy_limit
                    if limit_ratio_float < 5:
                        discount_rate = 1.0
                        st.info(tr("info_limit_no_discount"))
                    else:
                        limit_ratio = int(round(limit_ratio_float))
                        capped_ratio = max(5, min(20, limit_ratio))
                        discount_rate = pc.limited_policy_discounts.get(capped_ratio, 1.0)
                    limited_policy_multiplier = 1.3 * discount_rate

            groups_determined = pc.determine_group_params(locations_data)
            premium_results_by_group = {}
            total_premium_all_groups_try = 0.0

            for group_key, data in groups_determined.items():
                pd_premium_try, bi_premium_try, ec_premium_try, mk_premium_try, total_premium_try, applied_rate = pc.calculate_fire_premium(
                    data["building_type"], data["risk_group"], currency_fire,
                    data["building"], data["fixture"], data["decoration"], data["commodity"], data["safe"],
                    data["machinery"], data["bi"],
                    data.get("ec_fixed", 0.0), data.get("ec_mobile", 0.0), data.get("mk_fixed", 0.0), data.get("mk_mobile", 0.0),
                    koas, deduct, fx_rate_fire, inflation_rate,
                    limited_policy_multiplier=limited_policy_multiplier
                )
                premium_results_by_group[group_key] = {
                    "pd_premium_try": pd_premium_try, "bi_premium_try": bi_premium_try,
                    "ec_premium_try": ec_premium_try, "mk_premium_try": mk_premium_try,
                    "total_premium_try": total_premium_try, "applied_rate": applied_rate
                }
                total_premium_all_groups_try += total_premium_try

            ui.display_fire_results(
                num_locations_val=num_locations,
                groups_determined_data=groups_determined,
                premium_results_by_group=premium_results_by_group,
                total_premium_all_groups_try_val=total_premium_all_groups_try,
                display_currency_for_output_val=currency_fire,
                display_fx_rate_for_output_val=fx_rate_fire,
                limited_policy_multiplier_val=limited_policy_multiplier
            )

            # --- SENARYO HESAPLAMALARI ---
            all_koas_keys = list(pc.koasurans_indirimi.keys())
            all_deduct_keys = sorted(list(pc.muafiyet_indirimi.keys()))

            # Kurala göre senaryoları filtrele
            if total_pd_sum_try < 3_500_000_000:
                allowed_koas = [k for k in all_koas_keys if k not in ["90/10", "100/0"]]
                allowed_deduct = [d for d in all_deduct_keys if d >= 2]
            else:
                allowed_koas = all_koas_keys
                allowed_deduct = all_deduct_keys

            scenario_definitions = []
            for k in allowed_koas:
                for d in allowed_deduct:
                    # Ana hesaplama ile aynı olan senaryoyu atla
                    if k == koas and d == deduct:
                        continue
                    scenario_definitions.append({
                        "name_key": f"Scenario {k} / {d}%", # Dinamik isim
                        "koas_key": k,
                        "deduct_key": d
                    })

            prepare_scenario_data_for_session(
                scenario_definitions,
                groups_determined,
                currency_fire,
                fx_rate_fire,
                inflation_rate,
                total_entered_pd_orig_ccy,
                total_entered_bi_orig_ccy,
                num_locations,
                koas,
                deduct
            )

            st.session_state['export_data'] = {
                'locations_data': locations_data,
                'groups_determined': groups_determined,
                'num_locations': num_locations,
                'currency_fire': currency_fire,
                'koas': koas,
                'deduct': deduct,
                'inflation_rate': inflation_rate,
                'premium_results_by_group': premium_results_by_group,
                'total_premium_all_groups_try': total_premium_all_groups_try,
                'display_currency': currency_fire,
                'display_fx_rate': fx_rate_fire,
                'limited_policy_multiplier': limited_policy_multiplier
            }

    # --- HESAPLAMA SONRASI GÖSTERİLECEK BUTONLAR ---
    if 'export_data' in st.session_state:
        st.markdown("---")

        # col1, col2, col3 = st.columns(3)
        col2, col3 = st.columns(2)

        # with col1:
        #     if st.button(label=tr("goto_scenario_page_button") + " 💡", use_container_width=True, key="goto_scenario_btn"):
        #         st.switch_page("pages/scenario_calculator_page.py")

        with col2:
            if 'export_data' in st.session_state:
                pdf_bytes = pdf_generator.create_fire_pdf(
                    locations_data=st.session_state.export_data['locations_data'],
                    groups_determined=st.session_state.export_data['groups_determined'],
                    num_locations=st.session_state.export_data['num_locations'],
                    currency_fire=st.session_state.export_data['currency_fire'],
                    koas=st.session_state.export_data['koas'],
                    deduct=st.session_state.export_data['deduct'],
                    inflation_rate=st.session_state.export_data['inflation_rate'],
                    premium_results_by_group=st.session_state.export_data['premium_results_by_group'],
                    total_premium_all_groups_try=st.session_state.export_data['total_premium_all_groups_try'],
                    display_currency=st.session_state.export_data['display_currency'],
                    display_fx_rate=st.session_state.export_data['display_fx_rate'],
                    ui_helpers=ui,
                    language=lang,
                    scenario_data=st.session_state.get('scenario_data_for_page') # YENİ
                )
                st.download_button(
                    label="📄 " + tr("download_pdf_button"),
                    data=pdf_bytes,
                    file_name=f"TariffEQ_Fire_Report_{datetime.now().strftime('%Y%m%d')}.pdf",
                    mime="application/pdf",
                    use_container_width=True,
                    key="download_pdf"
                )

        with col3:
            if 'export_data' in st.session_state:
                try:
                    excel_bytes = excel_generator.create_fire_excel(
                        **st.session_state['export_data'],
                        ui_helpers=ui,
                        language=lang
                    )
                    st.download_button(
                        label="📊 " + tr("download_excel_button"),
                        data=excel_bytes,
                        file_name=f"TariffEQ_Fire_Report_{datetime.now().strftime('%Y%m%d')}.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                        use_container_width=True,
                        key="download_fire_excel"
                    )
                except ValueError as e:
                    # Excel oluşturmak için veri olmadığında bu blok çalışır.
                    # Kullanıcıya bir uyarı göstermek yerine butonu devre dışı bırakabilir veya hiçbir şey yapmayabiliriz.
                    # Şimdilik, butonu oluşturmuyoruz ve bir uyarı veriyoruz.
                    st.warning(tr("warning_car_no_sum_insured"))


elif st.session_state.active_calc_module == CALC_MODULE_CAR:
    st.markdown(f'<h3 class="section-header">{tr("car_header")}</h3>', unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        risk_group_type = st.selectbox(tr("risk_group_type"), ["RiskGrubuA", "RiskGrubuB"], format_func=lambda x: "A" if x == "RiskGrubuA" else "B", key="risk_group_type", help=tr("risk_group_type_help"))
        risk_class = st.selectbox(tr("risk_class"), [1, 2, 3, 4, 5, 6, 7], help=tr("risk_class_help"))
        start_date = st.date_input(tr("start_date"), value=datetime.today(),format="DD-MM-YYYY")
        end_date = st.date_input(tr("end_date"), value=datetime.today() + timedelta(days=365),format="DD-MM-YYYY")
    with col2:
        duration_months = pc.calculate_months_difference(start_date, end_date)
        st.write(f"⏳ {tr('duration')}: {duration_months} {tr('months')}", help=tr("duration_help"))
        currency = st.selectbox(tr("currency"), ["TRY", "USD", "EUR"], key="car_currency") 
        fx_rate, fx_info = ui.fx_input(currency, "car")
    
    st.markdown(f"### {tr('insurance_sums')}")
    
    col3, col4, col5 = st.columns(3)
    with col3:
        project = st.number_input(tr("project"), min_value=0, value=0, step=100000, help=tr("project_help"), format="%d")
        if project > 0: st.write(f"{tr('entered_value')}: {ui.format_number(project, currency)}")
    with col4:
        cpm = st.number_input(tr("cpm"), min_value=0, value=0, step=100000, help=tr("cpm_help"), format="%d")
        if cpm > 0: st.write(f"{tr('entered_value')}: {ui.format_number(cpm, currency)}")
    with col5:
        cpe = st.number_input(tr("cpe"), min_value=0, value=0, step=100000, help=tr("cpe_help"), format="%d")
        if cpe > 0: st.write(f"{tr('entered_value')}: {ui.format_number(cpe, currency)}")
    
    st.markdown(f"### {tr('coinsurance_deductible')}")
    col6, col7, col8 = st.columns(3)
    with col6:
        koas_car = st.selectbox(tr("coins"), list(pc.koasurans_indirimi_car.keys()), help=tr("coins_help"), key="car_koas")
    with col7:
        deduct_car = st.selectbox(tr("ded"), sorted(list(pc.muafiyet_indirimi_car.keys()), reverse=True),index=4, help=tr("ded_help"), key="car_deduct")
    with col8:
        inflation_rate_car = st.number_input(tr("inflation_rate"), min_value=0.0, value=0.0, step=0.1, help=tr("inflation_rate_help"), format="%.2f", key="car_inflation")
    
    if st.button(tr("btn_calc"), key="car_calc"):
        # Değerlerin girilip girilmediğini kontrol et
        if project <= 0 and cpm <= 0 and cpe <= 0:
            st.warning(tr("warning_car_no_sum_insured"))
            st.stop() # Hesaplamanın geri kalanını çalıştırmayı durdur

        if 'car_export_data' in st.session_state:
            del st.session_state['car_export_data']

        # Ana Hesaplama
        car_premium_try, cpm_premium_try, cpe_premium_try, total_premium_try, applied_car_rate = pc.calculate_car_ear_premium(
            risk_group_type, risk_class, start_date, end_date, project, cpm, cpe, currency, 
            koas_car, deduct_car, fx_rate, inflation_rate_car
        )
        
        ui.display_car_ear_results(
            car_premium_try, cpm_premium_try, cpe_premium_try, total_premium_try, 
            applied_car_rate, 
            project, cpm, cpe, 
            currency, fx_rate
        )

        # --- YENİ: Senaryo Hesaplamaları ---
        calculated_scenarios = []
        all_koas_keys = list(pc.koasurans_indirimi_car.keys())
        all_deduct_keys = sorted(list(pc.muafiyet_indirimi_car.keys()))

        for k in all_koas_keys:
            for d in all_deduct_keys:
                if k == koas_car and d == deduct_car:
                    continue # Ana hesaplamayı tekrar ekleme
                
                # Senaryo için primleri hesapla
                s_car_prem, s_cpm_prem, s_cpe_prem, s_total_prem, _ = pc.calculate_car_ear_premium(
                    risk_group_type, risk_class, start_date, end_date, project, cpm, cpe, currency, 
                    k, d, fx_rate, inflation_rate_car
                )
                calculated_scenarios.append({
                    "name": f"Senaryo {k} / {d}%",
                    "koas_key": k,
                    "deduct_key": d,
                    "total_premium_try": s_total_prem
                })
        # --- SENARYO HESAPLAMA SONU ---


        # YENİ: Raporlar için verileri session state'e kaydet (senaryolar dahil)
        st.session_state['car_export_data'] = {
            'risk_group_type': risk_group_type,
            'risk_class': risk_class,
            'start_date': start_date,
            'end_date': end_date,
            'duration_months': pc.calculate_months_difference(start_date, end_date),
            'project_sum': project,
            'cpm_sum': cpm,
            'cpe_sum': cpe,
            'currency': currency,
            'koas': koas_car,
            'deduct': deduct_car,
            'fx_rate': fx_rate,
            'inflation_rate': inflation_rate_car,
            'car_premium_try': car_premium_try,
            'cpm_premium_try': cpm_premium_try,
            'cpe_premium_try': cpe_premium_try,
            'total_premium_try': total_premium_try,
            'applied_car_rate': applied_car_rate,
            'calculated_scenarios': calculated_scenarios # Senaryo verilerini ekle
        }

    # YENİ: CAR/EAR için indirme butonları
    if 'car_export_data' in st.session_state:
        st.markdown("---")
        col_pdf, col_excel = st.columns(2)
        with col_pdf:
            # Düzeltme: PDF oluşturucuya göndermeden önce tarih string'lerini doğru formatla date objesine çevir
            pdf_data = st.session_state['car_export_data'].copy()
            
            # Gelen tarih nesnesi bir string ise (session state'den dolayı), onu date objesine çevir.
            # Hata mesajına göre format 'DD.MM.YYYY' olarak geliyor.
            if isinstance(pdf_data['start_date'], str):
                pdf_data['start_date'] = datetime.strptime(pdf_data['start_date'], '%d.%m.%Y').date()
            if isinstance(pdf_data['end_date'], str):
                pdf_data['end_date'] = datetime.strptime(pdf_data['end_date'], '%d.%m.%Y').date()

            pdf_bytes = pdf_generator.create_car_pdf(
                data=pdf_data,
                ui_helpers=ui,
                language=lang
            )
            st.download_button(
                label="📄 " + tr("download_pdf_button"),
                data=pdf_bytes,
                file_name=f"TariffEQ_CAR_Report_{datetime.now().strftime('%Y%m%d')}.pdf",
                mime="application/pdf",
                use_container_width=True,
                key="download_car_pdf"
            )

        with col_excel:
            excel_bytes = excel_generator.create_car_excel(
                data=st.session_state['car_export_data'],
                ui_helpers=ui,
                language=lang
            )
            st.download_button(
                label="📊 " + tr("download_excel_button"),
                data=excel_bytes,
                file_name=f"TariffEQ_CAR_Report_{datetime.now().strftime('%Y%m%d')}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True,
                key="download_car_excel"
            )
st.markdown("---")
st.markdown("""
<div style='text-align: center; font-size: 0.9em; color: #666; padding: 10px; background-color: #f8f9fa; border-radius: 5px; margin-top: 20px;'>
    ⚠️ <strong>Yasal Uyarı:</strong> TariffEQ hesaplamaları bilgilendirme amaçlıdır; hukuki veya ticari bağlayıcılığı yoktur.
</div>
""", unsafe_allow_html=True)

# Footer
st.markdown(f"<div class='footer'>{T['footer'][lang]}</div>", unsafe_allow_html=True)