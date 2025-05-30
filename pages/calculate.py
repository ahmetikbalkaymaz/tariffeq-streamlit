import streamlit as st
from datetime import datetime, timedelta # Ana UI'da hala kullanılıyor (CAR/EAR tarihleri için)
from translations import T 
import pandas as pd # Ana UI'da DataFrame gösterimi için değil, ama kalabilir.
from utils import premium_calculations as pc
from utils import ui_helpers as ui

# ------------------------------------------------------------
# STREAMLIT CONFIG (must be first)
# ------------------------------------------------------------
st.set_page_config(page_title="TariffEQ", layout="wide", initial_sidebar_state="expanded")

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

# Kenar Çubuğu Navigasyonu ve Dil Seçimi (Değişiklik yok)
with st.sidebar:
    st.image("assets/logo.png", width=1000) 
    st.page_link("home.py", label=T["home"][st.session_state.lang], icon="🏠")
    st.page_link("pages/calculate.py", label=T["calc"][st.session_state.lang]) 
    st.page_link("pages/earthquake_zones.py", label=T["earthquake_zones_nav"][st.session_state.lang]) 
    st.page_link("pages/scenario_calculator_page.py", label=T["scenario_page_title"][st.session_state.lang], icon="📉") 
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
                data_group["ec_fixed"], data_group["ec_mobile"], data_group["mk_fixed"], data_group["mk_mobile"],
                scenario_def["koas_key"], scenario_def["deduct_key"],
                fx_rate_fire_val, inflation_rate_val,
                skip_limit_warnings= True  # Limit uyarılarını atla, çünkü senaryo hesaplamaları için bu önemli değil
            )
            scenario_results_per_group.append({
                "group_key": group_key,
                "pd_premium_try": pd_scenario_premium_try,
                "bi_premium_try": bi_scenario_premium_try
            })
        calculated_scenarios_for_session.append({
            "name": tr(scenario_def["name_key"]), # tr() burada kullanılıyor
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
with col_btn2:
    if st.button(tr("select_car_button"), use_container_width=True, key="btn_select_car"):
        st.session_state.active_calc_module = CALC_MODULE_CAR

if st.session_state.active_calc_module == CALC_MODULE_FIRE:
    st.markdown(f'<h3 class="section-header">{tr("fire_header")}</h3>', unsafe_allow_html=True)

    fire_general_col1, fire_general_col2 = st.columns(2)
    with fire_general_col1:
        currency_fire = st.selectbox(tr("currency"), ["TRY", "USD", "EUR"], key="main_fire_module_currency")
    with fire_general_col2:
        fx_rate_fire, fx_info_fire = ui.fx_input(currency_fire, "main_fire_module") # ui.fx_input
    
    num_locations = st.number_input(tr("num_locations"), min_value=1, max_value=10, value=1, step=1, help=tr("num_locations_help"))
    
    locations_data = []
    # Temel grup etiketleri (A, B, C...)
    # Lokasyon sayısı 1 olsa bile en az bir grup ("A") olmalı
    base_groups = [chr(65 + i) for i in range(max(1, num_locations))] 
    
    # Kullanıcıya gösterilecek formatlanmış grup etiketleri
    # Bu, tr fonksiyonunun "group_label_format" gibi bir anahtara sahip olmasını gerektirir:
    # "group_label_format": {"TR": "{group_char} Kümülü", "EN": "{group_char} Aggregate"}
    # formatted_group_options = [tr("group_label_format").format(group_char=g) for g in base_groups] # Bu artık doğrudan selectbox içinde kullanılmayacak

    for i in range(num_locations):
        with st.expander(f"Lokasyon {i + 1}" if lang == "TR" else f"Location {i + 1}", expanded=True if i == 0 else False):
            col1, col2 = st.columns(2)
            with col1:
                building_type = st.selectbox(tr("building_type"), ["Betonarme", "Diğer"], key=f"building_type_{i}", help=tr("building_type_help"))
                risk_group = st.selectbox(
                    tr("risk_group"), 
                    [1, 2, 3, 4, 5, 6, 7], 
                    key=f"risk_group_{i}", 
                    help=tr("risk_group_help")
                )
                # Buton yerine Markdown linki kullanarak yeni sekmede açma
                earthquake_zone_page_url = "earthquake_zones" # Streamlit sayfa adını / olmadan kullanır
                button_label = tr("learn_earthquake_zone_button")
                
                # Streamlit'in kendi buton stilini taklit etmeye çalışalım
                # Not: Bu, tam olarak st.button gibi görünmeyebilir ve CSS ile daha fazla özelleştirme gerektirebilir.
                # Basit bir link olarak da bırakabilirsiniz:
                # st.markdown(f'<a href="{earthquake_zone_page_url}" target="_blank">{button_label}</a>', unsafe_allow_html=True)

                # Daha çok butona benzemesi için bir deneme (CSS ile desteklenmeli)
                st.markdown(f"""
                <a href="{earthquake_zone_page_url}" target="_blank" style="
                    display: inline-block;
                    padding: 0.5em 1em;
                    background-color: #2E86C1; /* Ana buton renginiz */
                    color: white;
                    text-decoration: none;
                    border-radius: 50px; /* Ana buton border-radius'unuz */
                    text-align: center;
                    width: 100%; /* use_container_width=True etkisi */
                    box-sizing: border-box; /* padding ve border'ın genişliği etkilememesi için */
                ">
                    {button_label}
                </a>
                """, unsafe_allow_html=True)
                
                # Eski st.button kodu:
                # if st.button(tr("learn_earthquake_zone_button"), key=f"learn_zone_btn_{i}", use_container_width=True):
                #     st.switch_page("pages/earthquake_zones.py")
            with col2:
                group_for_this_location = "A" # Varsayılan grup, eğer num_locations > 1 ise selectbox'tan alınacak

                if num_locations > 1: # Sadece birden fazla lokasyon varsa grup seçimi göster
                    with col2:
                        # format_func, seçilen değeri (örn: "A") alır ve nasıl gösterileceğini döndürür.
                        # options olarak base_groups (A, B, C) kullanılır,
                        # ama kullanıcı formatlanmış hallerini (A Kümülü, B Kümülü) görür.
                        # Seçilen değer yine "A", "B" gibi temel karakter olacaktır.
                        group_for_this_location = st.selectbox(
                            tr("location_group"), 
                            options=base_groups, # Seçenekler hala A, B, C...
                            format_func=lambda x: tr("group_label_format").format(group_char=x), # Gösterim formatı
                            key=f"group_{i}", 
                            help=tr("location_group_help") + " " + tr("location_group_help_cumulative")
                        )
                        st.caption(tr("location_group_cumulative_info"))
                # else: # Tek lokasyon varsa col2 boş kalabilir veya başka bir bilgi gösterilebilir.
                # with col2:
                #    st.empty() # veya st.info(tr("single_location_default_group_info").format(group_char="A"))
                #    # translations.py'ye eklenecek:
                #    # "single_location_default_group_info": {"TR": "Tek lokasyon otomatik olarak {group_char} Kümülüne atanmıştır.", "EN": "Single location automatically assigned to {group_char} Aggregate."}


            st.markdown(f"#### {tr('insurance_sums')}")
            main_col1, main_col2, ec_mk_main_col = st.columns([2, 2, 3]) 
            with main_col1:
                building = st.number_input(tr("building_sum"), min_value=0.0, value=0.0, step=100000.0, key=f"building_{i}", help=tr("building_sum_help"), format="%.2f")
                if building > 0: st.write(f"{tr('entered_value')}: {ui.format_number(building, currency_fire)}") # ui.format_number
                fixture = st.number_input(tr("fixture_sum"), min_value=0.0, value=0.0, step=100000.0, key=f"fixture_{i}", help=tr("fixture_sum_help"), format="%.2f")
                if fixture > 0: st.write(f"{tr('entered_value')}: {ui.format_number(fixture, currency_fire)}") # ui.format_number
                decoration = st.number_input(tr("decoration_sum"), min_value=0.0, value=0.0, step=100000.0, key=f"decoration_{i}", help=tr("decoration_sum_help"), format="%.2f")
                if decoration > 0: st.write(f"{tr('entered_value')}: {ui.format_number(decoration, currency_fire)}") # ui.format_number
                bi = st.number_input(tr("bi"), min_value=0.0, value=0.0, step=100000.0, key=f"bi_{i}", help=tr("bi_help"), format="%.2f")
                if bi > 0: st.write(f"{tr('entered_value')}: {ui.format_number(bi, currency_fire)}") # ui.format_number
            with main_col2:
                commodity = st.number_input(tr("commodity_sum"), min_value=0.0, value=0.0, step=100000.0, key=f"commodity_{i}", help=tr("commodity_sum_help"), format="%.2f")
                commodity_is_subscription = st.checkbox(tr("commodity_is_subscription"), key=f"commodity_is_subscription_{i}", help=tr("commodity_is_subscription_help"))
                if commodity > 0:
                    display_comm_value = commodity * 0.40 if commodity_is_subscription else commodity
                    st.write(f"{tr('entered_value')}: {ui.format_number(commodity, currency_fire)} ({tr('effective_value')}: {ui.format_number(display_comm_value, currency_fire)})" if commodity_is_subscription else f"{tr('entered_value')}: {ui.format_number(commodity, currency_fire)}") # ui.format_number
                safe = st.number_input(tr("safe_sum"), min_value=0.0, value=0.0, step=100000.0, key=f"safe_{i}", help=tr("safe_sum_help"), format="%.2f")
                if safe > 0: st.write(f"{tr('entered_value')}: {ui.format_number(safe, currency_fire)}") # ui.format_number
                machinery = st.number_input(tr("mk_sum"), min_value=0.0, value=0.0, step=100000.0, key=f"machinery_{i}", help=tr("mk_sum_help"), format="%.2f")
                if machinery > 0: st.write(f"{tr('entered_value')}: {ui.format_number(machinery, currency_fire)}") # ui.format_number
            
            ec_fixed, ec_mobile, mk_fixed, mk_mobile = 0.0, 0.0, 0.0, 0.0
            with ec_mk_main_col:
                st.markdown(f"###### {tr('ec_mk_cover_options_header')}")
                include_ec_mk_cover = st.checkbox(tr("include_ec_mk_cover"), key=f"include_ec_mk_cover_{i}", value=True)
                if include_ec_mk_cover:
                    ec_fixed = st.number_input(tr("ec_fixed"), min_value=0.0, value=0.0, step=100000.0, key=f"ec_fixed_{i}", help=tr("ec_fixed_help"), format="%.2f")
                    if ec_fixed > 0: st.write(f"{tr('entered_value')}: {ui.format_number(ec_fixed, currency_fire)}") # ui.format_number
                    ec_mobile = st.number_input(tr("ec_mobile"), min_value=0.0, value=0.0, step=100000.0, key=f"ec_mobile_{i}", help=tr("ec_mobile_help"), format="%.2f")
                    if ec_mobile > 0: st.write(f"{tr('entered_value')}: {ui.format_number(ec_mobile, currency_fire)}") # ui.format_number
                    st.markdown(f"**{tr('mk_cover_subheader')}**") 
                    mk_fixed = st.number_input(tr("mk_fixed"), min_value=0.0, value=0.0, step=100000.0, key=f"mk_fixed_cover_{i}", help=tr("mk_fixed_cover_help"), format="%.2f")
                    if mk_fixed > 0: st.write(f"{tr('entered_value')}: {ui.format_number(mk_fixed, currency_fire)}") # ui.format_number
                    mk_mobile = st.number_input(tr("mk_mobile"), min_value=0.0, value=0.0, step=100000.0, key=f"mk_mobile_cover_{i}", help=tr("mk_mobile_cover_help"), format="%.2f")
                    if mk_mobile > 0: st.write(f"{tr('entered_value')}: {ui.format_number(mk_mobile, currency_fire)}") # ui.format_number
            
            locations_data.append({
                "group": group_for_this_location, # Değiştirildi: group -> group_for_this_location
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
        # ui.display_current_total_sums fonksiyonu artık emtea abonman mantığını içeriyor.
        ui.display_current_total_sums(locations_data, currency_fire) 

    st.markdown(f"#### {tr('coinsurance_deductible')}")
    col5, col6, col7 = st.columns(3)
    with col5:
        koas = st.selectbox(tr("koas"), list(pc.koasurans_indirimi.keys()), help=tr("koas_help")) # pc.koasurans_indirimi
    with col6:
        deduct = st.selectbox(tr("deduct"), sorted(list(pc.muafiyet_indirimi.keys()), reverse=True), index=4, help=tr("deduct_help")) # pc.muafiyet_indirimi
    with col7:
        inflation_rate = st.number_input(tr("inflation_rate"), min_value=0.0, value=0.0, step=5.0, help=tr("inflation_rate_help"), format="%.2f")

if st.button(tr("btn_calc"), key="fire_calc"):
    total_entered_pd_orig_ccy = 0.0
    total_entered_bi_orig_ccy = 0.0
    for loc_data_item in locations_data: 
        # Toplam girilen PD bedeli gösterimi için emteanın %100'ünü al
        commodity_value_for_total_display = loc_data_item["commodity"]
        
        total_entered_pd_orig_ccy += (
            loc_data_item["building"] + loc_data_item["fixture"] +
            loc_data_item["decoration"] + commodity_value_for_total_display + # %100 emtea
            loc_data_item["safe"] + loc_data_item["machinery"] +
            loc_data_item["ec_fixed"] + loc_data_item["ec_mobile"] + 
            loc_data_item["mk_fixed"] + loc_data_item["mk_mobile"] 
        )
        total_entered_bi_orig_ccy += loc_data_item["bi"]

    proceed_with_calculation = True
    if total_entered_pd_orig_ccy * fx_rate_fire < 3500000000: # 3.5 Milyar TL
        if koas in ["90/10", "100/0"]:
            proceed_with_calculation = False
            st.warning(tr("warning_koas_below_3_5B").format(koas_value=koas))
        if deduct in [0.1, 0.5, 1.0, 1.5]: # %0.1, %0.5, %1, %1.5
            proceed_with_calculation = False
            st.warning(tr("warning_deduct_below_3_5B").format(deduct_value=str(deduct)))

    st.markdown(f"---")
    st.markdown(f"<h5>{tr('entered_sums_summary_header')}</h5>", unsafe_allow_html=True)
    st.markdown(f'<div class="info-box">ℹ️ <b>{tr("total_entered_pd_sum")}:</b> {ui.format_number(total_entered_pd_orig_ccy, currency_fire)}</div>', unsafe_allow_html=True) # ui.format_number
    if total_entered_bi_orig_ccy > 0:
        st.markdown(f'<div class="info-box">ℹ️ <b>{tr("total_entered_bi_sum")}:</b> {ui.format_number(total_entered_bi_orig_ccy, currency_fire)}</div>', unsafe_allow_html=True) # ui.format_number
    st.markdown(f"---")

    if proceed_with_calculation:
        groups_determined = pc.determine_group_params(locations_data) # pc.determine_group_params
        total_premium_all_groups_try = 0.0
        
        # display_fire_results için hazırlanacak veriler
        # Tek grup/lokasyon durumu için
        single_group_display_data_for_table = [] 
        last_applied_rate_for_single_group = None # Başlangıçta None

        # Çoklu grup/lokasyon durumu için
        premium_results_by_group_for_multi = {}

        display_currency_for_output = currency_fire
        display_fx_rate_for_output = fx_rate_fire if currency_fire != "TRY" else 1.0

        for group_key, data in groups_determined.items(): 
            # pc.determine_group_params fonksiyonunun, 'data["commodity"]' içinde
            # prim hesaplaması için doğru (gerekirse %40 uygulanmış) emtea bedelini
            # zaten sağladığından emin olun. Eğer sağlamıyorsa, burada bir ayarlama yapmanız gerekir.
            # Örnek:
            # commodity_for_premium = data["commodity"]
            # if data.get("commodity_is_subscription_in_group", False): # Bu flag'in groups_determined içinde olması lazım
            #     commodity_for_premium *= 0.40
            # Sonra commodity_for_premium'u pc.calculate_fire_premium'a geçin.
            # Şimdilik, data["commodity"]'nin zaten doğru olduğunu varsayıyorum.

            pd_premium_try, bi_premium_try, ec_premium_try, mk_premium_try, group_total_premium_try, applied_rate = pc.calculate_fire_premium(
                data["building_type"], data["risk_group"], currency_fire, 
                data["building"], data["fixture"], data["decoration"], data["commodity"], data["safe"], # data["commodity"] prim için ayarlanmış olmalı
                data["machinery"], data["bi"], data["ec_fixed"], data["ec_mobile"], 
                data["mk_fixed"], data["mk_mobile"],
                koas, deduct, fx_rate_fire, inflation_rate 
            )
            total_premium_all_groups_try += group_total_premium_try
            
            # Çoklu grup/lokasyon için veri toplama
            premium_results_by_group_for_multi[group_key] = {
                "pd_premium_try": pd_premium_try,
                "bi_premium_try": bi_premium_try,
                "ec_premium_try": ec_premium_try,
                "mk_premium_try": mk_premium_try,
                "total_premium_try": group_total_premium_try, # Bu anahtar ui_helpers'da bekleniyor
                "applied_rate": applied_rate # İsteğe bağlı, belki ileride kullanılır
            }

            # Tek grup/lokasyon durumu için veri hazırlığı (sadece bir grup varsa bu veriler kullanılacak)
            if len(groups_determined) == 1:
                last_applied_rate_for_single_group = applied_rate # Tek grup varsa bu atanır

                pd_premium_display_val = pd_premium_try / display_fx_rate_for_output
                bi_premium_display_val = bi_premium_try / display_fx_rate_for_output
                ec_premium_display_val = ec_premium_try / display_fx_rate_for_output
                mk_premium_display_val = mk_premium_try / display_fx_rate_for_output

                pd_sum_orig_ccy = (data["building"] + data["fixture"] + data["decoration"] + data["commodity"] + data["safe"] + data["machinery"])
                bi_sum_orig_ccy = data["bi"]
                ec_sum_orig_ccy = data["ec_fixed"] + data["ec_mobile"]
                mk_sum_orig_ccy = data["mk_fixed"] + data["mk_mobile"]
                
                if pd_sum_orig_ccy > 0 or pd_premium_display_val > 0 :
                    single_group_display_data_for_table.append({
                        tr("table_col_coverage_type"): tr("coverage_pd_combined"),
                        "sum_insured_numeric": pd_sum_orig_ccy, "premium_numeric": pd_premium_display_val, 
                        tr("table_col_sum_insured"): ui.format_number(pd_sum_orig_ccy, display_currency_for_output),
                        tr("table_col_premium"): ui.format_number(pd_premium_display_val, display_currency_for_output)
                    })
                if data["bi"] > 0:
                    single_group_display_data_for_table.append({
                        tr("table_col_coverage_type"): tr("coverage_bi"),
                        "sum_insured_numeric": bi_sum_orig_ccy, "premium_numeric": bi_premium_display_val,
                        tr("table_col_sum_insured"): ui.format_number(bi_sum_orig_ccy, display_currency_for_output),
                        tr("table_col_premium"): ui.format_number(bi_premium_display_val, display_currency_for_output)
                    })
                if data["ec_fixed"] > 0 or data["ec_mobile"] > 0:
                    single_group_display_data_for_table.append({
                        tr("table_col_coverage_type"): tr("coverage_ec"),
                        "sum_insured_numeric": ec_sum_orig_ccy, "premium_numeric": ec_premium_display_val,
                        tr("table_col_sum_insured"): ui.format_number(ec_sum_orig_ccy, display_currency_for_output),
                        tr("table_col_premium"): ui.format_number(ec_premium_display_val, display_currency_for_output)
                    })
                if data["mk_fixed"] > 0 or data["mk_mobile"] > 0:
                    single_group_display_data_for_table.append({
                        tr("table_col_coverage_type"): tr("coverage_mk"),
                        "sum_insured_numeric": mk_sum_orig_ccy, "premium_numeric": mk_premium_display_val,
                        tr("table_col_sum_insured"): ui.format_number(mk_sum_orig_ccy, display_currency_for_output),
                        tr("table_col_premium"): ui.format_number(mk_premium_display_val, display_currency_for_output)
                    })
            
            # ui.display_fire_results çağrısını güncelle
            # Eğer tek lokasyon ve tek grup varsa, eski tablo verilerini ve uygulanan oranı gönder
            # Aksi halde, çoklu grup için hazırlanan premium_results_by_group_for_multi'yi gönder
            if num_locations == 1 and len(groups_determined) == 1:
                ui.display_fire_results(
                    num_locations_val=num_locations,
                    groups_determined_data=groups_determined, 
                    premium_results_by_group=None, # Tek grup için bu None olacak
                    all_groups_display_data_for_table_val=single_group_display_data_for_table, 
                    total_premium_all_groups_try_val=total_premium_all_groups_try, 
                    display_currency_for_output_val=display_currency_for_output, 
                    display_fx_rate_for_output_val=display_fx_rate_for_output, 
                    applied_rate_val=last_applied_rate_for_single_group
                )
            else: # Birden fazla lokasyon veya grup varsa
                ui.display_fire_results(
                    num_locations_val=num_locations,
                    groups_determined_data=groups_determined, 
                    premium_results_by_group=premium_results_by_group_for_multi, 
                    all_groups_display_data_for_table_val=None, # Çoklu grup için bu None olacak
                    total_premium_all_groups_try_val=total_premium_all_groups_try, 
                    display_currency_for_output_val=display_currency_for_output, 
                    display_fx_rate_for_output_val=display_fx_rate_for_output, 
                    applied_rate_val=None # Çoklu grup için genel bir "uygulanan oran" yok
                )

            st.markdown("---") 
            scenario_definitions = [
                {"name_key": "scenario_8020_2_name", "koas_key": "80/20", "deduct_key": 2},
                {"name_key": "scenario_9010_2_name", "koas_key": "90/10", "deduct_key": 2},
                {"name_key": "scenario_8020_5_name", "koas_key": "80/20", "deduct_key": 5},
                {"name_key": "scenario_9010_5_name", "koas_key": "90/10", "deduct_key": 5},
                {"name_key": "scenario_7030_5_name", "koas_key": "70/30", "deduct_key": 5},
            ]
            # prepare_scenario_data_for_session çağrısı burada kalıyor, içindeki pc.calculate_fire_premium güncellendi
            prepare_scenario_data_for_session(
                scenario_definitions, groups_determined, currency_fire, fx_rate_fire, 
                inflation_rate, total_entered_pd_orig_ccy, total_entered_bi_orig_ccy,
                num_locations, koas, deduct
            )
            st.page_link("pages/scenario_calculator_page.py", label=tr("goto_scenario_page_button"), icon="💡", use_container_width=True)

elif st.session_state.active_calc_module == CALC_MODULE_CAR:
    st.markdown(f'<h3 class="section-header">{tr("car_header")}</h3>', unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        risk_group_type = st.selectbox(tr("risk_group_type"), ["RiskGrubuA", "RiskGrubuB"], format_func=lambda x: "A" if x == "RiskGrubuA" else "B", key="risk_group_type", help=tr("risk_group_type_help"))
        risk_class = st.selectbox(tr("risk_class"), [1, 2, 3, 4, 5, 6, 7], help=tr("risk_class_help"))
        start_date = st.date_input(tr("start_date"), value=datetime.today(),format="DD-MM-YYYY")
        end_date = st.date_input(tr("end_date"), value=datetime.today() + timedelta(days=365),format="DD-MM-YYYY")
    with col2:
        duration_months = pc.calculate_months_difference(start_date, end_date) # pc.calculate_months_difference
        st.write(f"⏳ {tr('duration')}: {duration_months} {tr('months')}", help=tr("duration_help"))
        currency = st.selectbox(tr("currency"), ["TRY", "USD", "EUR"], key="car_currency") 
        fx_rate, fx_info = ui.fx_input(currency, "car") # ui.fx_input
    
    st.markdown(f"### {tr('insurance_sums')}")
    # if currency != "TRY": # Bu satır ui.fx_input içinde zaten st.info ile gösterildiği için gereksiz olabilir.
    #     st.info(fx_info) 
    
    col3, col4, col5 = st.columns(3)
    with col3:
        project = st.number_input(tr("project"), min_value=0.0000, value=0.0000, step=100000.0, help=tr("project_help"), format="%.4f")
        if project > 0: st.write(f"{tr('entered_value')}: {ui.format_number(project, currency)}") # ui.format_number
    with col4:
        cpm = st.number_input(tr("cpm"), min_value=0.0000, value=0.0000, step=100000.0, help=tr("cpm_help"), format="%.4f")
        if cpm > 0: st.write(f"{tr('entered_value')}: {ui.format_number(cpm, currency)}") # ui.format_number
    with col5:
        cpe = st.number_input(tr("cpe"), min_value=0.0000, value=0.0000, step=100000.0, help=tr("cpe_help"), format="%.4f")
        if cpe > 0: st.write(f"{tr('entered_value')}: {ui.format_number(cpe, currency)}") # ui.format_number
    
    st.markdown(f"### {tr('coinsurance_deductible')}")
    col6, col7, col8 = st.columns(3)
    with col6:
        koas_car = st.selectbox(tr("coins"), list(pc.koasurans_indirimi_car.keys()), help=tr("coins_help"), key="car_koas") # pc.koasurans_indirimi_car
    with col7:
        deduct_car = st.selectbox(tr("ded"), sorted(list(pc.muafiyet_indirimi_car.keys()), reverse=True), help=tr("ded_help"), key="car_deduct") # pc.muafiyet_indirimi_car
    with col8:
        inflation_rate_car = st.number_input(tr("inflation_rate"), min_value=0.0, value=0.0, step=0.1, help=tr("inflation_rate_help"), format="%.2f", key="car_inflation")
    
    if st.button(tr("btn_calc"), key="car_calc"):
        car_premium_try, cpm_premium_try, cpe_premium_try, total_premium_try, applied_car_rate = pc.calculate_car_ear_premium( # pc.calculate_car_ear_premium
            risk_group_type, risk_class, start_date, end_date, project, cpm, cpe, currency, 
            koas_car, deduct_car, fx_rate, inflation_rate_car
        )
        
        ui.display_car_ear_results( # ui.display_car_ear_results
            car_premium_try, cpm_premium_try, cpe_premium_try, total_premium_try, 
            applied_car_rate, 
            project, cpm, cpe, 
            currency, fx_rate
        )