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
                risk_group = st.selectbox(
                    tr("risk_group"), 
                    [1, 2, 3, 4, 5, 6, 7], 
                    key=f"risk_group_{i}", 
                    help=tr("risk_group_help")
                )
                earthquake_zone_page_url = "earthquake_zones"
                button_label = tr("learn_earthquake_zone_button")
                st.markdown(f"""
                <a href="{earthquake_zone_page_url}" target="_blank" class="styled-link-button">
                    {button_label}
                </a>
                """, unsafe_allow_html=True)
                
            with col2:
                group_for_this_location = "A"
                if num_locations > 1:
                    group_for_this_location = st.selectbox(
                        tr("location_group"), 
                        options=base_groups,
                        format_func=lambda x: tr("group_label_format").format(group_char=x),
                        key=f"group_{i}", 
                        help=tr("location_group_help") + " " + tr("location_group_help_cumulative")
                    )
                    st.caption(tr("location_group_cumulative_info"))

            st.markdown(f"#### {tr('insurance_sums')}")
            main_col1, main_col2, ec_mk_main_col = st.columns([2, 2, 3]) 
            with main_col1:
                building = st.number_input(tr("building_sum"), min_value=0.0, value=0.0, step=100000.0, key=f"building_{i}", help=tr("building_sum_help"), format="%.2f")
                if building > 0: st.write(f"{tr('entered_value')}: {ui.format_number(building, currency_fire)}")
                fixture = st.number_input(tr("fixture_sum"), min_value=0.0, value=0.0, step=100000.0, key=f"fixture_{i}", help=tr("fixture_sum_help"), format="%.2f")
                if fixture > 0: st.write(f"{tr('entered_value')}: {ui.format_number(fixture, currency_fire)}")
                decoration = st.number_input(tr("decoration_sum"), min_value=0.0, value=0.0, step=100000.0, key=f"decoration_{i}", help=tr("decoration_sum_help"), format="%.2f")
                if decoration > 0: st.write(f"{tr('entered_value')}: {ui.format_number(decoration, currency_fire)}")
                bi = st.number_input(tr("bi"), min_value=0.0, value=0.0, step=100000.0, key=f"bi_{i}", help=tr("bi_help"), format="%.2f")
                if bi > 0: st.write(f"{tr('entered_value')}: {ui.format_number(bi, currency_fire)}")
            with main_col2:
                commodity = st.number_input(tr("commodity_sum"), min_value=0.0, value=0.0, step=100000.0, key=f"commodity_{i}", help=tr("commodity_sum_help"), format="%.2f")
                commodity_is_subscription = st.checkbox(tr("commodity_is_subscription"), key=f"commodity_is_subscription_{i}", help=tr("commodity_is_subscription_help"))
                if commodity > 0:
                    display_comm_value = commodity * 0.40 if commodity_is_subscription else commodity
                    st.write(f"{tr('entered_value')}: {ui.format_number(commodity, currency_fire)} ({tr('effective_value')}: {ui.format_number(display_comm_value, currency_fire)})" if commodity_is_subscription else f"{tr('entered_value')}: {ui.format_number(commodity, currency_fire)}")
                safe = st.number_input(tr("safe_sum"), min_value=0.0, value=0.0, step=100000.0, key=f"safe_{i}", help=tr("safe_sum_help"), format="%.2f")
                if safe > 0: st.write(f"{tr('entered_value')}: {ui.format_number(safe, currency_fire)}")
                machinery = st.number_input(tr("mk_sum"), min_value=0.0, value=0.0, step=100000.0, key=f"machinery_{i}", help=tr("mk_sum_help"), format="%.2f")
                if machinery > 0: st.write(f"{tr('entered_value')}: {ui.format_number(machinery, currency_fire)}")
            
            ec_fixed, ec_mobile, mk_fixed, mk_mobile = 0.0, 0.0, 0.0, 0.0
            with ec_mk_main_col:
                st.markdown(f"###### {tr('ec_mk_cover_options_header')}")
                include_ec_mk_cover = st.checkbox(tr("include_ec_mk_cover"), key=f"include_ec_mk_cover_{i}", value=True)
                if include_ec_mk_cover:
                    ec_fixed = st.number_input(tr("ec_fixed"), min_value=0.0, value=0.0, step=100000.0, key=f"ec_fixed_{i}", help=tr("ec_fixed_help"), format="%.2f")
                    if ec_fixed > 0: st.write(f"{tr('entered_value')}: {ui.format_number(ec_fixed, currency_fire)}")
                    ec_mobile = st.number_input(tr("ec_mobile"), min_value=0.0, value=0.0, step=100000.0, key=f"ec_mobile_{i}", help=tr("ec_mobile_help"), format="%.2f")
                    if ec_mobile > 0: st.write(f"{tr('entered_value')}: {ui.format_number(ec_mobile, currency_fire)}")
                    st.markdown(f"**{tr('mk_cover_subheader')}**") 
                    mk_fixed = st.number_input(tr("mk_fixed"), min_value=0.0, value=0.0, step=100000.0, key=f"mk_fixed_cover_{i}", help=tr("mk_fixed_cover_help"), format="%.2f")
                    if mk_fixed > 0: st.write(f"{tr('entered_value')}: {ui.format_number(mk_fixed, currency_fire)}")
                    mk_mobile = st.number_input(tr("mk_mobile"), min_value=0.0, value=0.0, step=100000.0, key=f"mk_mobile_cover_{i}", help=tr("mk_mobile_cover_help"), format="%.2f")
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
                "mk_fixed": mk_fixed if include_ec_mk_cover else 0.0,
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

    if st.button(tr("btn_calc"), key="fire_calc"):
        if 'export_data' in st.session_state:
            del st.session_state['export_data']

        total_entered_pd_orig_ccy = 0.0
        total_entered_bi_orig_ccy = 0.0
        for loc_data_item in locations_data: 
            commodity_value_for_total_display = loc_data_item["commodity"]
            total_entered_pd_orig_ccy += (
                loc_data_item["building"] + loc_data_item["fixture"] +
                loc_data_item["decoration"] + commodity_value_for_total_display + 
                loc_data_item["safe"] + loc_data_item["machinery"] +
                (loc_data_item.get("ec_fixed", 0.0) if loc_data_item.get("include_ec_mk_cover", False) else 0.0) +
                (loc_data_item.get("ec_mobile", 0.0) if loc_data_item.get("include_ec_mk_cover", False) else 0.0) +
                (loc_data_item.get("mk_fixed", 0.0) if loc_data_item.get("include_ec_mk_cover", False) else 0.0) +
                (loc_data_item.get("mk_mobile", 0.0) if loc_data_item.get("include_ec_mk_cover", False) else 0.0)
            )
            total_entered_bi_orig_ccy += loc_data_item["bi"]

        proceed_with_calculation = True
        if total_entered_pd_orig_ccy * fx_rate_fire < 3500000000:
            if koas in ["90/10", "100/0"]:
                proceed_with_calculation = False
                st.warning(tr("warning_koas_below_3_5B").format(koas_value=koas))
            if deduct in [0.1, 0.5, 1.0, 1.5]:
                proceed_with_calculation = False
                st.warning(tr("warning_deduct_below_3_5B").format(deduct_value=str(deduct)))

        st.markdown("---")
        st.markdown(f"<h5>{tr('entered_sums_summary_header')}</h5>", unsafe_allow_html=True)
        st.markdown(f'<div class="info-box">ℹ️ <b>{tr("total_entered_pd_sum")}:</b> {ui.format_number(total_entered_pd_orig_ccy, currency_fire)}</div>', unsafe_allow_html=True) 
        if total_entered_bi_orig_ccy > 0:
            st.markdown(f'<div class="info-box">ℹ️ <b>{tr("total_entered_bi_sum")}:</b> {ui.format_number(total_entered_bi_orig_ccy, currency_fire)}</div>', unsafe_allow_html=True) 
        st.markdown("---")

        if proceed_with_calculation:
            groups_determined = pc.determine_group_params(locations_data) 
            total_premium_all_groups_try = 0.0
            single_group_display_data_for_table = [] 
            last_applied_rate_for_single_group = None 
            premium_results_by_group_for_multi = {}
            display_currency_for_output = currency_fire
            display_fx_rate_for_output = fx_rate_fire if currency_fire != "TRY" else 1.0

            for group_key, data in groups_determined.items(): 
                pd_premium_try, bi_premium_try, ec_premium_try, mk_premium_try, group_total_premium_try, applied_rate = pc.calculate_fire_premium(
                    data["building_type"], data["risk_group"], currency_fire, 
                    data["building"], data["fixture"], data["decoration"], data["commodity"], data["safe"], 
                    data["machinery"], data["bi"], data.get("ec_fixed", 0.0), data.get("ec_mobile", 0.0), 
                    data.get("mk_fixed", 0.0), data.get("mk_mobile", 0.0),
                    koas, deduct, fx_rate_fire, inflation_rate 
                )
                total_premium_all_groups_try += group_total_premium_try
                premium_results_by_group_for_multi[group_key] = {
                    "pd_premium_try": pd_premium_try, "bi_premium_try": bi_premium_try,
                    "ec_premium_try": ec_premium_try, "mk_premium_try": mk_premium_try,
                    "total_premium_try": group_total_premium_try, "applied_rate": applied_rate 
                }
                if len(groups_determined) == 1:
                    last_applied_rate_for_single_group = applied_rate 
                    last_applied_rate_for_single_group = applied_rate 

                    # Tek grup için primlerü gösterim para birimine çevir
                    pd_premium_display_val = pd_premium_try / display_fx_rate_for_output
                    bi_premium_display_val = bi_premium_try / display_fx_rate_for_output
                    ec_premium_display_val = ec_premium_try / display_fx_rate_for_output
                    mk_premium_display_val = mk_premium_try / display_fx_rate_for_output

                    # Tek grup için bedelleri hesapla (%100 ham emtea değerini kullan)
                    pd_sum_orig_ccy = (
                        data["building"] + data["fixture"] + data["decoration"] + 
                        data.get("commodity_raw_for_display", data["commodity"]) + # %100 emtea değeri
                        data["safe"] + data["machinery"]
                    )
                    bi_sum_orig_ccy = data["bi"]
                    ec_sum_orig_ccy = data.get("ec_fixed", 0.0) + data.get("ec_mobile", 0.0)
                    mk_sum_orig_ccy = data.get("mk_fixed", 0.0) + data.get("mk_mobile", 0.0)
                    
                    # PD (Yangın) satırını her zaman ekle
                    if pd_sum_orig_ccy > 0 or pd_premium_display_val > 0:
                        pd_effective_rate = (pd_premium_display_val / pd_sum_orig_ccy) * 1000 if pd_sum_orig_ccy > 0 else 0.0
                        single_group_display_data_for_table.append({
                            tr("table_col_coverage_type"): tr("coverage_pd_combined"),
                            "sum_insured_numeric": pd_sum_orig_ccy,
                            "rate_per_mille_numeric": pd_effective_rate,
                            "premium_numeric": pd_premium_display_val, 
                            tr("table_col_sum_insured"): ui.format_number(pd_sum_orig_ccy, display_currency_for_output),
                            tr("table_col_rate_per_mille"): ui.format_rate(pd_effective_rate),
                            tr("table_col_premium"): ui.format_number(pd_premium_display_val, display_currency_for_output)
                        })
                    
                    # BI (Kar Kaybı) satırını sadece değeri varsa ekle
                    if bi_sum_orig_ccy > 0:
                        bi_effective_rate = (bi_premium_display_val / bi_sum_orig_ccy) * 1000 if bi_sum_orig_ccy > 0 else 0.0
                        single_group_display_data_for_table.append({
                            tr("table_col_coverage_type"): tr("coverage_bi"),
                            "sum_insured_numeric": bi_sum_orig_ccy,
                            "rate_per_mille_numeric": bi_effective_rate,
                            "premium_numeric": bi_premium_display_val,
                            tr("table_col_sum_insured"): ui.format_number(bi_sum_orig_ccy, display_currency_for_output),
                            tr("table_col_rate_per_mille"): ui.format_rate(bi_effective_rate),
                            tr("table_col_premium"): ui.format_number(bi_premium_display_val, display_currency_for_output)
                        })
                    
                    # EC (Elektronik Cihaz) satırını sadece değeri varsa ekle
                    if ec_sum_orig_ccy > 0:
                        ec_effective_rate = (ec_premium_display_val / ec_sum_orig_ccy) * 1000 if ec_sum_orig_ccy > 0 else 0.0
                        single_group_display_data_for_table.append({
                            tr("table_col_coverage_type"): tr("coverage_ec"),
                            "sum_insured_numeric": ec_sum_orig_ccy,
                            "rate_per_mille_numeric": ec_effective_rate,
                            "premium_numeric": ec_premium_display_val,
                            tr("table_col_sum_insured"): ui.format_number(ec_sum_orig_ccy, display_currency_for_output),
                            tr("table_col_rate_per_mille"): ui.format_rate(ec_effective_rate),
                            tr("table_col_premium"): ui.format_number(ec_premium_display_val, display_currency_for_output)  # Eksik parantez eklendi
                        })
                    
                    # MK (Makine Kırılması) satırını sadece değeri varsa ekle
                    if mk_sum_orig_ccy > 0:
                        mk_effective_rate = (mk_premium_display_val / mk_sum_orig_ccy) * 1000 if mk_sum_orig_ccy > 0 else 0.0
                        single_group_display_data_for_table.append({
                            tr("table_col_coverage_type"): tr("coverage_mk"),
                            "sum_insured_numeric": mk_sum_orig_ccy,
                            "rate_per_mille_numeric": mk_effective_rate,
                            "premium_numeric": mk_premium_display_val,
                            tr("table_col_sum_insured"): ui.format_number(mk_sum_orig_ccy, display_currency_for_output),
                            tr("table_col_rate_per_mille"): ui.format_rate(mk_effective_rate),
                            tr("table_col_premium"): ui.format_number(mk_premium_display_val, display_currency_for_output)
                        })

            if num_locations == 1 and len(groups_determined) == 1:
                 ui.display_fire_results(
                    num_locations_val=num_locations, groups_determined_data=groups_determined, 
                    premium_results_by_group=None, all_groups_display_data_for_table_val=single_group_display_data_for_table, 
                    total_premium_all_groups_try_val=total_premium_all_groups_try, 
                    display_currency_for_output_val=display_currency_for_output, 
                    display_fx_rate_for_output_val=display_fx_rate_for_output, 
                    applied_rate_val=last_applied_rate_for_single_group
                )
            else: 
                # Çoklu grup için primlerü gösterim para birimine çevir
                premium_results_by_group_for_display = {}
                for group_key, premium_data in premium_results_by_group_for_multi.items():
                    premium_results_by_group_for_display[group_key] = {
                        "pd_premium_try": premium_data["pd_premium_try"] / display_fx_rate_for_output,  # Gösterim para birimine çevir
                        "bi_premium_try": premium_data["bi_premium_try"] / display_fx_rate_for_output,  # Gösterim para birimine çevir
                        "ec_premium_try": premium_data["ec_premium_try"] / display_fx_rate_for_output,  # Gösterim para birimine çevir
                        "mk_premium_try": premium_data["mk_premium_try"] / display_fx_rate_for_output,  # Gösterim para birimine çevir
                        "total_premium_try": premium_data["total_premium_try"] / display_fx_rate_for_output,  # Gösterim para birimine çevir
                        "applied_rate": premium_data["applied_rate"]
                    }
                
                # Toplam primi de gösterim para birimine çevir
                total_premium_display = total_premium_all_groups_try / display_fx_rate_for_output
                
                ui.display_fire_results(
                    num_locations_val=num_locations, groups_determined_data=groups_determined, 
                    premium_results_by_group=premium_results_by_group_for_display,  # Çevrilmiş veriler
                    all_groups_display_data_for_table_val=None, 
                    total_premium_all_groups_try_val=total_premium_display,  # Çevrilmiş toplam
                    display_currency_for_output_val=display_currency_for_output, 
                    display_fx_rate_for_output_val=1.0,  # Artık 1.0 çünkü çeviri yapıldı
                    applied_rate_val=None 
                )
            
            # PDF ve Excel için kullanılacak verileri session state'e kaydet
            st.session_state.export_data = {
                "locations_data": locations_data,
                "num_locations": num_locations, "currency_fire": currency_fire,
                "koas": koas, "deduct": deduct, "inflation_rate": inflation_rate,
                "groups_determined": groups_determined,
                "premium_results_by_group": premium_results_by_group_for_multi,
                "total_premium_all_groups_try": total_premium_all_groups_try,
                "display_currency": display_currency_for_output,
                "display_fx_rate": display_fx_rate_for_output,
                "ui_helpers": ui,
                "language": lang
            }
            
            scenario_definitions = [
                {"name_key": "scenario_8020_2_name", "koas_key": "80/20", "deduct_key": 2},
                {"name_key": "scenario_9010_2_name", "koas_key": "90/10", "deduct_key": 2},
                {"name_key": "scenario_8020_5_name", "koas_key": "80/20", "deduct_key": 5},
                {"name_key": "scenario_9010_5_name", "koas_key": "90/10", "deduct_key": 5},
                {"name_key": "scenario_7030_5_name", "koas_key": "70/30", "deduct_key": 5},
            ]
            prepare_scenario_data_for_session(
                scenario_definitions, groups_determined, currency_fire, fx_rate_fire, 
                inflation_rate, total_entered_pd_orig_ccy, total_entered_bi_orig_ccy,
                num_locations, koas, deduct
            )

    # --- HESAPLAMA SONRASI GÖSTERİLECEK BUTONLAR ---
    if 'export_data' in st.session_state:
        st.markdown("---") 

        col1, col2, col3 = st.columns(3)
        col2, col3 = st.columns(2)

        # with col1:
        #     if st.button(label=tr("goto_scenario_page_button") + " 💡", use_container_width=True, key="goto_scenario_btn"):
        #         st.switch_page("pages/scenario_calculator_page.py") 
        
        with col2:
            try:
                pdf_data = st.session_state.export_data
                
                # Senaryo verilerini session state'den al
                scenario_data_for_pdf = st.session_state.get('scenario_data_for_page', None)
                
                # PDF oluşturucuya senaryo verilerini de gönder
                pdf_bytes = pdf_generator.create_fire_pdf(
                    locations_data=pdf_data['locations_data'],
                    groups_determined=pdf_data['groups_determined'],
                    num_locations=pdf_data['num_locations'],
                    currency_fire=pdf_data['currency_fire'],
                    koas=pdf_data['koas'],
                    deduct=pdf_data['deduct'],
                    inflation_rate=pdf_data['inflation_rate'],
                    premium_results_by_group=pdf_data['premium_results_by_group'],
                    total_premium_all_groups_try=pdf_data['total_premium_all_groups_try'],
                    display_currency=pdf_data['display_currency'],
                    display_fx_rate=pdf_data['display_fx_rate'],
                    ui_helpers=pdf_data['ui_helpers'],
                    language=pdf_data.get('language', 'TR'),
                    scenario_data=scenario_data_for_pdf  # YENİ PARAMETRE
                )

                st.download_button(
                    label="📄 PDF Olarak İndir",
                    data=pdf_bytes,
                    file_name=f"TariffEQ_Yangin_Raporu_{date.today().strftime('%Y%m%d')}.pdf",
                    mime="application/pdf",
                    use_container_width=True,
                    key="download_pdf_btn"
                )
            except Exception as e:
                st.error(f"PDF oluşturulurken bir hata oluştu: {e}")

        with col3:
            try:
                excel_data = st.session_state.export_data
                
                excel_bytes = excel_generator.create_excel_report(
                    groups_determined=excel_data['groups_determined'],
                    premium_results_by_group=excel_data['premium_results_by_group'],
                    display_currency=excel_data['display_currency'],
                    display_fx_rate=excel_data['display_fx_rate']
                )

                st.download_button(
                    label="📊 Excel'e Aktar",
                    data=excel_bytes,
                    file_name=f"TariffEQ_Sonuclari_{date.today().strftime('%Y%m%d')}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    use_container_width=True,
                    key="download_excel_btn"
                )
            except Exception as e:
                st.error(f"Excel dosyası oluşturulurken bir hata oluştu: {e}")

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
        project = st.number_input(tr("project"), min_value=0.0000, value=0.0000, step=100000.0, help=tr("project_help"), format="%.4f")
        if project > 0: st.write(f"{tr('entered_value')}: {ui.format_number(project, currency)}")
    with col4:
        cpm = st.number_input(tr("cpm"), min_value=0.0000, value=0.0000, step=100000.0, help=tr("cpm_help"), format="%.4f")
        if cpm > 0: st.write(f"{tr('entered_value')}: {ui.format_number(cpm, currency)}")
    with col5:
        cpe = st.number_input(tr("cpe"), min_value=0.0000, value=0.0000, step=100000.0, help=tr("cpe_help"), format="%.4f")
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
st.markdown("---")
st.markdown("""
<div style='text-align: center; font-size: 0.9em; color: #666; padding: 10px; background-color: #f8f9fa; border-radius: 5px; margin-top: 20px;'>
    ⚠️ <strong>Yasal Uyarı:</strong> TariffEQ hesaplamaları bilgilendirme amaçlıdır; hukuki veya ticari bağlayıcılığı yoktur.
</div>
""", unsafe_allow_html=True)

# Footer
st.markdown(f"<div class='footer'>{T['footer'][lang]}</div>", unsafe_allow_html=True)