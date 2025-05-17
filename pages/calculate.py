import streamlit as st
import requests
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta
from translations import T # YENİ: translations.py dosyasından tr fonksiyonunu içe aktarın
# ------------------------------------------------------------
# STREAMLIT CONFIG (must be first)
# ------------------------------------------------------------
st.set_page_config(page_title="TariffEQ", layout="wide")

# Dil seçimi için session state başlatma (EĞER YOKSA)
if 'lang' not in st.session_state:
    st.session_state.lang = "TR"  # Varsayılan dil

# Dil değişkenini session state'den al
lang = st.session_state.lang

# Dil-bağımsız anahtarlar için sabitler
CALC_MODULE_FIRE = "fire_module"
CALC_MODULE_CAR = "car_module"

# Custom CSS for styling
st.markdown("""
<style>
    [data-testid="stSidebar"] {
        background-color: #039df426; /* Mevcut arka plan rengi korunuyor */
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
        align-items: center;
        justify-content: center;
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

# Kenar Çubuğu Navigasyonu ve Dil Seçimi
with st.sidebar:
    st.image("../logo.png", width=1000)
    # st.write(f"### {T['title'][st.session_state.lang]}") # Ana başlık için 'title' kullanılıyor, gerekirse 'calc_title' olarak değiştirilebilir.
    st.page_link("home.py", label=T["home"][st.session_state.lang], icon="🏠")
    st.page_link("pages/calculate.py", label=T["calc"][st.session_state.lang])
    
    st.markdown("---") 

    lang_options = ["TR", "EN"]
    if st.session_state.lang not in lang_options:
        st.session_state.lang = "TR" 

    current_lang_index = lang_options.index(st.session_state.lang)
    
    selected_lang_sidebar = st.radio(
        "Language / Dil", 
        options=lang_options, 
        index=current_lang_index, 
        key="sidebar_language_selector_calc" # calculate.py için benzersiz bir anahtar
    )

    if selected_lang_sidebar != st.session_state.lang:
        st.session_state.lang = selected_lang_sidebar
        st.rerun()

    st.markdown("---") # Dil seçimi ile footer arasına bir ayırıcı daha eklenebilir (opsiyonel)
    st.markdown(f"<div class='sidebar-footer footer'>{T['footer'][lang]}</div>", unsafe_allow_html=True) # Footer buraya eklendi

def tr(key: str) -> str:
    # lang değişkeni artık dosyanın başında st.session_state'den alınıyor
    return T.get(key, {}).get(lang, key)

# ------------------------------------------------------------
# 1) TCMB FX MODULE
# ------------------------------------------------------------
@st.cache_data(ttl=3600)
def get_tcmb_rate(ccy: str):
    try:
        r = requests.get("https://www.tcmb.gov.tr/kurlar/today.xml", timeout=4)
        r.raise_for_status()
        root = ET.fromstring(r.content)
        for cur in root.findall("Currency"):
            if cur.attrib.get("CurrencyCode") == ccy:
                txt = cur.findtext("BanknoteSelling") or cur.findtext("ForexSelling")
                return float(txt.replace(",", ".")), datetime.strptime(root.attrib["Date"], "%d.%m.%Y").strftime("%Y-%m-%d")
    except Exception:
        pass
    today = datetime.today()
    for i in range(1, 8):
        d = today - timedelta(days=i)
        url = f"https://www.tcmb.gov.tr/kurlar/{d:%Y%m}/{d:%d%m%Y}.xml"
        try:
            r = requests.get(url, timeout=4)
            if not r.ok:
                continue
            root = ET.fromstring(r.content)
            for cur in root.findall("Currency"):
                if cur.attrib.get("CurrencyCode") == ccy:
                    txt = cur.findtext("BanknoteSelling") or cur.findtext("ForexSelling")
                    return float(txt.replace(",", ".")), d.strftime("%Y-%m-%d")
        except Exception:
            continue
    return None, None

def fx_input(ccy: str, key_prefix: str) -> float:
    if ccy == "TRY":
        return 1.0, ""
    r_key = f"{key_prefix}_{ccy}_rate"
    s_key = f"{key_prefix}_{ccy}_src"
    tcmb_rate_key = f"{key_prefix}_{ccy}_tcmb_rate"
    tcmb_date_key = f"{key_prefix}_{ccy}_tcmb_date"
    
    if tcmb_rate_key not in st.session_state:
        tcmb_rate, tcmb_date = get_tcmb_rate(ccy)
        if tcmb_rate is None:
            st.session_state.update({
                tcmb_rate_key: 0.0,
                tcmb_date_key: "-",
                r_key: 0.0,
                s_key: "MANUEL"
            })
        else:
            st.session_state.update({
                tcmb_rate_key: tcmb_rate,
                tcmb_date_key: tcmb_date,
                r_key: tcmb_rate,
                s_key: "TCMB"
            })
    
    default_rate = float(st.session_state[r_key])
    new_rate = st.number_input(tr("manual_fx"), value=default_rate, step=0.0001, format="%.4f", key=f"{key_prefix}_{ccy}_manual")
    
    if new_rate != st.session_state.get(tcmb_rate_key, 0.0):
        st.session_state[s_key] = "MANUEL"
    else:
        st.session_state[s_key] = "TCMB"
    
    st.session_state[r_key] = new_rate
    
    info_message = (
        f"💱 TCMB Kuru: 1 {ccy} = {st.session_state[tcmb_rate_key]:,.4f} TL (TCMB, {st.session_state[tcmb_date_key]}) | "
        f"Kullanılan Kur: 1 {ccy} = {st.session_state[r_key]:,.4f} TL ({st.session_state[s_key]})"
    )
    st.info(info_message)
    return st.session_state[r_key], info_message

# Helper function to format numbers with thousand separators
def format_number(value: float, currency: str) -> str:
    formatted_value = f"{value:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    return f"{formatted_value} {currency}"

# ------------------------------------------------------------
# 2) CONSTANT TABLES
# ------------------------------------------------------------
tarife_oranlari = {
    "Betonarme": [3.13, 2.63, 2.38, 1.94, 1.38, 1.06, 0.75],
    "Diğer": [6.13, 5.56, 3.75, 2.00, 1.56, 1.24, 1.06],
    "RiskGrubuA": [1.56, 1.31, 1.19, 0.98, 0.69, 0.54, 0.38],
    "RiskGrubuB": [3.06, 2.79, 1.88, 1.00, 0.79, 0.63, 0.54]
}
koasurans_indirimi = {
    "80/20": 0.0, "75/25": 0.0625, "70/30": 0.125, "65/35": 0.1875,
    "60/40": 0.25, "55/45": 0.3125, "50/50": 0.375, "45/55": 0.4375,
    "40/60": 0.50,
    "30/70": 0.125, "25/75": 0.0625,
    "90/10": -0.125, "100/0": -0.25
}
koasurans_indirimi_car = {
    "80/20": 0.0, "75/25": 0.0625, "70/30": 0.125, "65/35": 0.1875,
    "60/40": 0.25, "55/45": 0.3125, "50/50": 0.375, "45/55": 0.4375,
    "40/60": 0.50
}
muafiyet_indirimi = {
    2: 0.0, 3: 0.06, 4: 0.13, 5: 0.19, 10: 0.35,
    0.1: -0.12, 0.5: -0.09, 1: -0.06, 1.5: -0.03
}
muafiyet_indirimi_car = {
    2: 0.0, 3: 0.06, 4: 0.13, 5: 0.19, 10: 0.35
}
sure_carpani_tablosu = {
    6: 0.70, 7: 0.75, 8: 0.80, 9: 0.85, 10: 0.90, 11: 0.95, 12: 1.00,
    13: 1.05, 14: 1.10, 15: 1.15, 16: 1.20, 17: 1.25, 18: 1.30,
    19: 1.35, 20: 1.40, 21: 1.45, 22: 1.50, 23: 1.55, 24: 1.60,
    25: 1.65, 26: 1.70, 27: 1.74, 28: 1.78, 29: 1.82, 30: 1.86,
    31: 1.90, 32: 1.94, 33: 1.98, 34: 2.02, 35: 2.06, 36: 2.10
}

# ------------------------------------------------------------
# 3) CALCULATION LOGIC
# ------------------------------------------------------------
def calculate_duration_multiplier(months: int) -> float:
    if months <= 36:
        return sure_carpani_tablosu.get(months, 1.0)
    base = sure_carpani_tablosu[36]
    extra_months = months - 36
    return base + (0.03 * extra_months)

def calculate_months_difference(start_date, end_date):
    months = (end_date.year - start_date.year) * 12 + (end_date.month - start_date.month)
    total_days = (end_date - start_date).days
    year_diff = end_date.year - start_date.year
    month_diff = end_date.month - start_date.month
    estimated_days = (year_diff * 365) + (month_diff * 30)
    remaining_days = total_days - estimated_days
    if remaining_days >= 15:
        months += 1
    return months

def determine_group_params(locations_data):
    groups = {}
    for loc in locations_data:
        group = loc["group"]
        if group not in groups:
            groups[group] = []
        groups[group].append(loc)
    
    result = {}
    for group, locs in groups.items():
        building_types = [loc["building_type"] for loc in locs]
        building_type = "Diğer" if "Diğer" in building_types else "Betonarme"
        
        risk_groups = [loc["risk_group"] for loc in locs]
        risk_group = min(risk_groups)
        
        building = sum(loc["building"] for loc in locs)
        fixture = sum(loc["fixture"] for loc in locs)
        decoration = sum(loc["decoration"] for loc in locs)
        commodity = sum(loc["commodity"] for loc in locs)
        safe = sum(loc["safe"] for loc in locs)
        bi = sum(loc["bi"] for loc in locs)
        ec_fixed = sum(loc["ec_fixed"] for loc in locs)
        ec_mobile = sum(loc["ec_mobile"] for loc in locs)
        mk_fixed = sum(loc["mk_fixed"] for loc in locs)
        mk_mobile = sum(loc["mk_mobile"] for loc in locs)
        
        result[group] = {
            "building_type": building_type,
            "risk_group": risk_group,
            "building": building,
            "fixture": fixture,
            "decoration": decoration,
            "commodity": commodity,
            "safe": safe,
            "bi": bi,
            "ec_fixed": ec_fixed,
            "ec_mobile": ec_mobile,
            "mk_fixed": mk_fixed,
            "mk_mobile": mk_mobile
        }
    return result

def calculate_fire_premium(building_type, risk_group, currency, building, fixture, decoration, commodity, safe, bi, ec_fixed, ec_mobile, mk_fixed, mk_mobile, koas, deduct, fx_rate, inflation_rate):
    # Calculate individual sums insured in TRY
    building_sum_insured = building * fx_rate
    fixture_sum_insured = fixture * fx_rate
    decoration_sum_insured = decoration * fx_rate
    commodity_sum_insured = commodity * fx_rate
    safe_sum_insured = safe * fx_rate
    bi_sum_insured = bi * fx_rate
    ec_fixed_sum_insured = ec_fixed * fx_rate
    ec_mobile_sum_insured = ec_mobile * fx_rate
    mk_fixed_sum_insured = mk_fixed * fx_rate
    mk_mobile_sum_insured = mk_mobile * fx_rate
    
    # Calculate total sum insured for PD (including EC and MK for limit check)
    pd_sum_insured = (building_sum_insured + fixture_sum_insured + decoration_sum_insured + commodity_sum_insured + safe_sum_insured + ec_fixed_sum_insured + ec_mobile_sum_insured + mk_fixed_sum_insured + mk_mobile_sum_insured)
    
    # Base rate from tariff table
    rate = tarife_oranlari[building_type][risk_group - 1]
    
    # Adjust rate for inflation (increase by half of the inflation rate)
    inflation_multiplier = 1 + (inflation_rate / 100) / 2
    rate *= inflation_multiplier
    
    LIMIT_FIRE = 3_500_000_000
    LIMIT_EC_MK = 840_000_000
    
    # Check total sum insured against the 3.5 billion TRY limit
    if pd_sum_insured > LIMIT_FIRE:
        st.warning(tr("limit_warning_fire_pd"))
    
    # PD Premium (excluding EC and MK for actual premium calculation, but included in limit check)
    pd_sum_for_premium = (building_sum_insured + fixture_sum_insured + decoration_sum_insured + commodity_sum_insured + safe_sum_insured)
    koas_discount = koasurans_indirimi[koas]
    deduct_discount = muafiyet_indirimi[deduct]
    adjusted_rate_pd = rate * (1 - koas_discount) * (1 - deduct_discount)
    if pd_sum_insured > LIMIT_FIRE:
        adjusted_rate_pd = round(adjusted_rate_pd * (LIMIT_FIRE / pd_sum_insured), 6)
    pd_premium = (pd_sum_for_premium * adjusted_rate_pd) / 1000
    
    # BI Premium (no koas/deduct discount as per tariff)
    adjusted_rate_bi = rate
    if bi_sum_insured > LIMIT_FIRE:
        st.warning(tr("limit_warning_fire_bi"))
        adjusted_rate_bi = round(adjusted_rate_bi * (LIMIT_FIRE / bi_sum_insured), 6)
    bi_premium = (bi_sum_insured * adjusted_rate_bi) / 1000
    
    # EC Premium
    ec_premium = 0.0
    ec_fixed_premium = 0.0
    ec_mobile_premium = 0.0
    if ec_fixed > 0:
        ec_fixed_rate = rate * (1 - koas_discount) * (1 - deduct_discount)
        if ec_fixed_sum_insured > LIMIT_EC_MK:
            st.warning(tr("limit_warning_ec"))
            ec_fixed_rate = round(ec_fixed_rate * (LIMIT_EC_MK / ec_fixed_sum_insured), 6)
        ec_fixed_premium = (ec_fixed_sum_insured * ec_fixed_rate) / 1000
    if ec_mobile > 0:
        ec_mobile_rate = 2.00 * inflation_multiplier  # Apply inflation to mobile rate as well
        if ec_mobile_sum_insured > LIMIT_EC_MK:
            st.warning(tr("limit_warning_ec"))
            ec_mobile_rate = round(ec_mobile_rate * (LIMIT_EC_MK / ec_mobile_sum_insured), 6)
        ec_mobile_premium = (ec_mobile_sum_insured * ec_mobile_rate) / 1000
    ec_premium = ec_fixed_premium + ec_mobile_premium
    
    # MK Premium
    mk_premium = 0.0
    mk_fixed_premium = 0.0
    mk_mobile_premium = 0.0
    if mk_fixed > 0:
        mk_fixed_rate = rate * (1 - koas_discount) * (1 - deduct_discount)
        if mk_fixed_sum_insured > LIMIT_EC_MK:
            st.warning(tr("limit_warning_mk"))
            mk_fixed_rate = round(mk_fixed_rate * (LIMIT_EC_MK / mk_fixed_sum_insured), 6)
        mk_fixed_premium = (mk_fixed_sum_insured * mk_fixed_rate) / 1000
    if mk_mobile > 0:
        mk_mobile_rate = 2.00 * inflation_multiplier  # Apply inflation to mobile rate as well
        if mk_mobile_sum_insured > LIMIT_EC_MK:
            st.warning(tr("limit_warning_mk"))
            mk_mobile_rate = round(mk_mobile_rate * (LIMIT_EC_MK / mk_mobile_sum_insured), 6)
        mk_mobile_premium = (mk_mobile_sum_insured * mk_mobile_rate) / 1000
    mk_premium = mk_fixed_premium + mk_mobile_premium
    
    total_premium = pd_premium + bi_premium + ec_premium + mk_premium
    
    return pd_premium, bi_premium, ec_premium, mk_premium, total_premium, rate

def calculate_car_ear_premium(risk_group_type, risk_class, start_date, end_date, project, cpm, cpe, currency, koas, deduct, fx_rate, inflation_rate):
    duration_months = calculate_months_difference(start_date, end_date)
    
    base_rate = tarife_oranlari[risk_group_type][risk_class - 1]
    
    # Adjust base rate for inflation (increase by half of the inflation rate)
    inflation_multiplier = 1 + (inflation_rate / 100) / 2
    base_rate *= inflation_multiplier
    
    duration_multiplier = calculate_duration_multiplier(duration_months)
    koas_discount = koasurans_indirimi_car[koas]
    deduct_discount = muafiyet_indirimi_car[deduct]
    
    LIMIT = 840_000_000
    
    project_sum_insured = project * fx_rate
    car_rate = base_rate * duration_multiplier * (1 - koas_discount) * (1 - deduct_discount)
    if project_sum_insured > LIMIT:
        st.warning(tr("limit_warning_car"))
        car_rate *= (LIMIT / project_sum_insured)
    car_premium = (project_sum_insured * car_rate) / 1000
    
    cpm_sum_insured = cpm * fx_rate
    cpm_rate = 1.25 * inflation_multiplier  # Apply inflation to CPM rate
    if cpm_sum_insured > LIMIT:
        st.warning(tr("limit_warning_car"))
        cpm_rate *= (LIMIT / cpm_sum_insured)
    cpm_premium = (cpm_sum_insured * cpm_rate / 1000) * duration_multiplier
    
    cpe_sum_insured = cpe * fx_rate
    cpe_rate = base_rate * duration_multiplier
    if cpe_sum_insured > LIMIT:
        st.warning(tr("limit_warning_car"))
        cpe_rate *= (LIMIT / cpe_sum_insured)
    cpe_premium = (cpe_sum_insured * cpe_rate) / 1000
    
    total_premium = car_premium + cpm_premium + cpe_premium
    
    return car_premium, cpm_premium, cpe_premium, total_premium, car_rate

# ------------------------------------------------------------
# 4) STREAMLIT UI
# ------------------------------------------------------------
# Header with Image

# tr("calc_title") içeriği "TariffEQ – Akıllı Sigorta Prim Hesaplama Uygulaması" gibi bir metin döndürür.
# "TariffEQ" kısmını özel renklendireceğiz, kalanını ayıracağız.
calc_title_full = tr("calc_title")
descriptive_part = ""
brand_name = "TariffEQ" # Renklendirilecek ana marka adı
prefix_to_remove = brand_name + " – "

if calc_title_full.startswith(prefix_to_remove):
    descriptive_part = calc_title_full[len(prefix_to_remove):]
elif calc_title_full == brand_name:
    descriptive_part = "" # Sadece marka adı var, açıklama yok
else:
    # Beklenmedik format veya marka adı başta değilse, tam metni açıklama olarak kullan
    descriptive_part = calc_title_full

st.markdown(f"""
<h1 class="main-title">
    <span>
        <span class="tariff-part">Tariff</span><span class="eq-part">EQ</span>
    </span>
    <span style="margin-left: 0.3em;">– {descriptive_part}</span>
</h1>
""", unsafe_allow_html=True)


# Main Content
st.markdown('<h2 class="section-header">📌 ' + (tr("select_calc")) + '</h2>', unsafe_allow_html=True)

# Hesaplama türü seçimi için session_state başlatma (dil-bağımsız anahtar ile)
if 'active_calc_module' not in st.session_state:
    st.session_state.active_calc_module = CALC_MODULE_FIRE # Varsayılan olarak "fire" (İşletme) modülünü göster

col_btn1, col_btn2 = st.columns(2)

with col_btn1:
    if st.button(tr("select_fire_button"), use_container_width=True, key="btn_select_fire"):
        st.session_state.active_calc_module = CALC_MODULE_FIRE
        # st.rerun() # Genellikle gerekli değil

with col_btn2:
    if st.button(tr("select_car_button"), use_container_width=True, key="btn_select_car"):
        st.session_state.active_calc_module = CALC_MODULE_CAR
        # st.rerun()

# Eski session_state kullanımı:
# if 'calc_display_type' not in st.session_state:
#     st.session_state.calc_display_type = tr("calc_fire") 
# calc_type = st.selectbox(tr("select_calc"), [tr("calc_fire"), tr("calc_car")], help="Hesaplama türünü seçerek başlayın." if lang == "TR" else "Start by selecting the calculation type.") # BU SATIRI SİLİN

# İçeriği dil-bağımsız anahtara göre göster
if st.session_state.active_calc_module == CALC_MODULE_FIRE:
    st.markdown(f'<h3 class="section-header">{tr("fire_header")}</h3>', unsafe_allow_html=True)
    
    # Number of Locations
    num_locations = st.number_input(tr("num_locations"), min_value=1, max_value=10, value=1, step=1, help=tr("num_locations_help"))
    
    # Locations Input
    locations_data = []
    groups = [chr(65 + i) for i in range(num_locations)]  # A, B, C, ...
    for i in range(num_locations):
        with st.expander(f"Lokasyon {i + 1}" if lang == "TR" else f"Location {i + 1}", expanded=True if i == 0 else False):
            col1, col2 = st.columns(2)
            with col1:
                building_type = st.selectbox(tr("building_type"), ["Betonarme", "Diğer"], key=f"building_type_{i}", help=tr("building_type_help"))
                risk_group = st.selectbox(tr("risk_group"), [1, 2, 3, 4, 5, 6, 7], key=f"risk_group_{i}", help=tr("risk_group_help"))
            with col2:
                group = st.selectbox(tr("location_group"), groups, key=f"group_{i}", help=tr("location_group_help"))
                if i == 0: # Para birimi ve kur girişi sadece ilk lokasyonda veya genel bir alanda olmalı
                    currency = st.selectbox(tr("currency"), ["TRY", "USD", "EUR"], key="fire_currency")
                    fx_rate, fx_info = fx_input(currency, "fire") # fx_input zaten format="%.4f" kullanıyor
            
            st.markdown(f"#### {tr('insurance_sums')}")
            if i == 0 and currency != "TRY": # Kur bilgisini sadece bir kere göster
                st.info(fx_info)
            
            col3, col4, col5 = st.columns(3)
            with col3:
                building = st.number_input(tr("building_sum"), min_value=0.0, value=0.0, step=1000.0, key=f"building_{i}", help=tr("building_sum_help"), format="%.2f")
                if building > 0:
                    st.write(f"{tr('entered_value')}: {format_number(building, currency)}")
                fixture = st.number_input(tr("fixture_sum"), min_value=0.0, value=0.0, step=1000.0, key=f"fixture_{i}", help=tr("fixture_sum_help"), format="%.2f")
                if fixture > 0:
                    st.write(f"{tr('entered_value')}: {format_number(fixture, currency)}")
                decoration = st.number_input(tr("decoration_sum"), min_value=0.0, value=0.0, step=1000.0, key=f"decoration_{i}", help=tr("decoration_sum_help"), format="%.2f")
                if decoration > 0:
                    st.write(f"{tr('entered_value')}: {format_number(decoration, currency)}")
                bi = st.number_input(tr("bi"), min_value=0.0, value=0.0, step=1000.0, key=f"bi_{i}", help=tr("bi_help"), format="%.2f")
                if bi > 0:
                    st.write(f"{tr('entered_value')}: {format_number(bi, currency)}")
            with col4:
                commodity = st.number_input(tr("commodity_sum"), min_value=0.0, value=0.0, step=1000.0, key=f"commodity_{i}", help=tr("commodity_sum_help"), format="%.2f")
                if commodity > 0:
                    st.write(f"{tr('entered_value')}: {format_number(commodity, currency)}")
                safe = st.number_input(tr("safe_sum"), min_value=0.0, value=0.0, step=1000.0, key=f"safe_{i}", help=tr("safe_sum_help"), format="%.2f")
                if safe > 0:
                    st.write(f"{tr('entered_value')}: {format_number(safe, currency)}")
            with col5:
                ec_fixed = st.number_input(tr("ec_fixed"), min_value=0.0, value=0.0, step=1000.0, key=f"ec_fixed_{i}", help=tr("ec_fixed_help"), format="%.2f")
                if ec_fixed > 0:
                    st.write(f"{tr('entered_value')}: {format_number(ec_fixed, currency)}")
                ec_mobile = st.number_input(tr("ec_mobile"), min_value=0.0, value=0.0, step=1000.0, key=f"ec_mobile_{i}", help=tr("ec_mobile_help"), format="%.2f")
                if ec_mobile > 0:
                    st.write(f"{tr('entered_value')}: {format_number(ec_mobile, currency)}")
                mk_fixed = st.number_input(tr("mk_fixed"), min_value=0.0, value=0.0, step=1000.0, key=f"mk_fixed_{i}", help=tr("mk_fixed_help"), format="%.2f")
                if mk_fixed > 0:
                    st.write(f"{tr('entered_value')}: {format_number(mk_fixed, currency)}")
                mk_mobile = st.number_input(tr("mk_mobile"), min_value=0.0, value=0.0, step=1000.0, key=f"mk_mobile_{i}", help=tr("mk_mobile_help"), format="%.2f")
                if mk_mobile > 0:
                    st.write(f"{tr('entered_value')}: {format_number(mk_mobile, currency)}")
            
            locations_data.append({
                "group": group,
                "building_type": building_type,
                "risk_group": risk_group,
                "building": building,
                "fixture": fixture,
                "decoration": decoration,
                "commodity": commodity,
                "safe": safe,
                "bi": bi,
                "ec_fixed": ec_fixed,
                "ec_mobile": ec_mobile,
                "mk_fixed": mk_fixed,
                "mk_mobile": mk_mobile
            })
    
    st.markdown(f"#### {tr('coinsurance_deductible')}")
    col5, col6, col7 = st.columns(3)
    with col5:
        koas = st.selectbox(tr("koas"), list(koasurans_indirimi.keys()), help=tr("koas_help"))
    with col6:
        deduct = st.selectbox(tr("deduct"), sorted(list(muafiyet_indirimi.keys()), reverse=True), index=4, help=tr("deduct_help"))
    with col7:
        inflation_rate = st.number_input(tr("inflation_rate"), min_value=0.0, value=0.0, step=0.1, help=tr("inflation_rate_help"), format="%.2f")
    
    if st.button(tr("btn_calc"), key="fire_calc"):
        groups = determine_group_params(locations_data)
        total_premium = 0.0
        for group, data in groups.items():
            pd_premium, bi_premium, ec_premium, mk_premium, group_premium, applied_rate = calculate_fire_premium(
                data["building_type"], data["risk_group"], currency,
                data["building"], data["fixture"], data["decoration"], data["commodity"], data["safe"],
                data["bi"], data["ec_fixed"], data["ec_mobile"], data["mk_fixed"], data["mk_mobile"],
                koas, deduct, fx_rate, inflation_rate
            )
            total_premium += group_premium
            if currency != "TRY":
                pd_premium_converted = pd_premium / fx_rate
                bi_premium_converted = bi_premium / fx_rate
                ec_premium_converted = ec_premium / fx_rate
                mk_premium_converted = mk_premium / fx_rate
                group_premium_converted = group_premium / fx_rate
                st.markdown(f'<div class="info-box">✅ <b>{tr("group_premium")} ({group}):</b> {format_number(group_premium_converted, currency)}</div>', unsafe_allow_html=True)
                st.markdown(f'<div class="info-box">✅ <b>{tr("pd_premium")} ({group}):</b> {format_number(pd_premium_converted, currency)}</div>', unsafe_allow_html=True)
                st.markdown(f'<div class="info-box">✅ <b>{tr("bi_premium")} ({group}):</b> {format_number(bi_premium_converted, currency)}</div>', unsafe_allow_html=True)
                if data["ec_fixed"] > 0 or data["ec_mobile"] > 0:
                    st.markdown(f'<div class="info-box">✅ <b>{tr("ec_premium")} ({group}):</b> {format_number(ec_premium_converted, currency)}</div>', unsafe_allow_html=True)
                if data["mk_fixed"] > 0 or data["mk_mobile"] > 0:
                    st.markdown(f'<div class="info-box">✅ <b>{tr("mk_premium")} ({group}):</b> {format_number(mk_premium_converted, currency)}</div>', unsafe_allow_html=True)
                st.markdown(f'<div class="info-box">📊 <b>{tr("applied_rate")} ({group}):</b> {applied_rate:.2f}‰</div>', unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="info-box">✅ <b>{tr("group_premium")} ({group}):</b> {format_number(group_premium, "TRY")}</div>', unsafe_allow_html=True)
                st.markdown(f'<div class="info-box">✅ <b>{tr("pd_premium")} ({group}):</b> {format_number(pd_premium, "TRY")}</div>', unsafe_allow_html=True)
                st.markdown(f'<div class="info-box">✅ <b>{tr("bi_premium")} ({group}):</b> {format_number(bi_premium, "TRY")}</div>', unsafe_allow_html=True)
                if data["ec_fixed"] > 0 or data["ec_mobile"] > 0:
                    st.markdown(f'<div class="info-box">✅ <b>{tr("ec_premium")} ({group}):</b> {format_number(ec_premium, "TRY")}</div>', unsafe_allow_html=True)
                if data["mk_fixed"] > 0 or data["mk_mobile"] > 0:
                    st.markdown(f'<div class="info-box">✅ <b>{tr("mk_premium")} ({group}):</b> {format_number(mk_premium, "TRY")}</div>', unsafe_allow_html=True)
                st.markdown(f'<div class="info-box">📊 <b>{tr("applied_rate")} ({group}):</b> {applied_rate:.2f}‰</div>', unsafe_allow_html=True)
        
        if currency != "TRY":
            total_premium_converted = total_premium / fx_rate
            st.markdown(f'<div class="info-box">✅ <b>{tr("total_premium")}:</b> {format_number(total_premium_converted, currency)}</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="info-box">✅ <b>{tr("total_premium")}:</b> {format_number(total_premium, "TRY")}</div>', unsafe_allow_html=True)

elif st.session_state.active_calc_module == CALC_MODULE_CAR:
    st.markdown(f'<h3 class="section-header">{tr("car_header")}</h3>', unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        risk_group_type = st.selectbox(tr("risk_group_type"), ["RiskGrubuA", "RiskGrubuB"], format_func=lambda x: "A" if x == "RiskGrubuA" else "B", key="risk_group_type", help=tr("risk_group_type_help"))
        risk_class = st.selectbox(tr("risk_class"), [1, 2, 3, 4, 5, 6, 7], help=tr("risk_class_help"))
        start_date = st.date_input(tr("start_date"), value=datetime.today())
        end_date = st.date_input(tr("end_date"), value=datetime.today() + timedelta(days=365))
    with col2:
        duration_months = calculate_months_difference(start_date, end_date)
        st.write(f"⏳ {tr('duration')}: {duration_months} {tr('months')}", help=tr("duration_help"))
        currency = st.selectbox(tr("currency"), ["TRY", "USD", "EUR"], key="car_currency") # Farklı key kullandık
        fx_rate, fx_info = fx_input(currency, "car") # fx_input zaten format="%.4f" kullanıyor
    
    st.markdown(f"### {tr('insurance_sums')}")
    if currency != "TRY":
        st.info(fx_info)
    
    col3, col4, col5 = st.columns(3)
    with col3:
        project = st.number_input(tr("project"), min_value=0.0, value=0.0, step=1000.0, help=tr("project_help"), format="%.2f")
        if project > 0:
            st.write(f"{tr('entered_value')}: {format_number(project, currency)}")
    with col4:
        cpm = st.number_input(tr("cpm"), min_value=0.0, value=0.0, step=1000.0, help=tr("cpm_help"), format="%.2f")
        if cpm > 0:
            st.write(f"{tr('entered_value')}: {format_number(cpm, currency)}")
    with col5:
        cpe = st.number_input(tr("cpe"), min_value=0.0, value=0.0, step=1000.0, help=tr("cpe_help"), format="%.2f")
        if cpe > 0:
            st.write(f"{tr('entered_value')}: {format_number(cpe, currency)}")
    
    st.markdown(f"### {tr('coinsurance_deductible')}")
    col6, col7, col8 = st.columns(3)
    with col6:
        koas = st.selectbox(tr("coins"), list(koasurans_indirimi_car.keys()), help=tr("coins_help"))
    with col7:
        deduct = st.selectbox(tr("ded"), sorted(list(muafiyet_indirimi_car.keys()), reverse=True), help=tr("ded_help")) # index belirtilmemiş, varsayılan ilk eleman olacak
    with col8:
        inflation_rate = st.number_input(tr("inflation_rate"), min_value=0.0, value=0.0, step=0.1, help=tr("inflation_rate_help"), format="%.2f")
    
    if st.button(tr("btn_calc"), key="car_calc"):
        car_premium, cpm_premium, cpe_premium, total_premium, applied_rate = calculate_car_ear_premium(
            risk_group_type, risk_class, start_date, end_date, project, cpm, cpe, currency, koas, deduct, fx_rate, inflation_rate
        )
        if currency != "TRY":
            car_premium_converted = car_premium / fx_rate
            cpm_premium_converted = cpm_premium / fx_rate
            cpe_premium_converted = cpe_premium / fx_rate
            total_premium_converted = total_premium / fx_rate
            st.markdown(f'<div class="info-box">✅ <b>{tr("car_premium")}:</b> {format_number(car_premium_converted, currency)}</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="info-box">✅ <b>{tr("cpm_premium")}:</b> {format_number(cpm_premium_converted, currency)}</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="info-box">✅ <b>{tr("cpe_premium")}:</b> {format_number(cpe_premium_converted, currency)}</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="info-box">✅ <b>{tr("total_premium")}:</b> {format_number(total_premium_converted, currency)}</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="info-box">✅ <b>{tr("car_premium")}:</b> {format_number(car_premium, "TRY")}</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="info-box">✅ <b>{tr("cpm_premium")}:</b> {format_number(cpm_premium, "TRY")}</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="info-box">✅ <b>{tr("cpe_premium")}:</b> {format_number(cpe_premium, "TRY")}</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="info-box">✅ <b>{tr("total_premium")}:</b> {format_number(total_premium, "TRY")}</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="info-box">📊 <b>{tr("applied_rate")} (CAR):</b> {applied_rate:.2f}‰</div>', unsafe_allow_html=True)
        total_rate = (total_premium / (project + cpm + cpe)) * 1000 if (project + cpm + cpe) > 0 else 0
        st.markdown(f'<div class="info-box">📊 <b>{tr("applied_rate")} (Toplam):</b> {total_rate:.2f}‰</div>', unsafe_allow_html=True)