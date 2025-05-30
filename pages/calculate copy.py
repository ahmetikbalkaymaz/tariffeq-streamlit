import streamlit as st
import requests
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta
from translations import T # YENİ: translations.py dosyasından tr fonksiyonunu içe aktarın
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

# Custom CSS for styling
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

# Kenar Çubuğu Navigasyonu ve Dil Seçimi
with st.sidebar:
    st.image("assets/logo.png", width=1000) # width=1000 logonuz büyükse küçültün, örneğin 200
    st.page_link("home.py", label=T["home"][st.session_state.lang], icon="🏠")
    st.page_link("pages/calculate.py", label=T["calc"][st.session_state.lang]) # "calc" yerine farklı bir anahtar kullanmak daha iyi olabilir
    st.page_link("pages/earthquake_zones.py", label=T["earthquake_zones_nav"][st.session_state.lang]) # YENİ SAYFA LİNKİ
    st.page_link("pages/scenario_calculator_page.py", label=T["scenario_page_title"][st.session_state.lang]) # Mevcut sayfa
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
    for loc_item_for_grouping in locations_data:
        group_val = loc_item_for_grouping["group"]
        if group_val not in groups:
            groups[group_val] = []
        groups[group_val].append(loc_item_for_grouping)
    
    result = {}
    for group_key, locs_in_group in groups.items():
        building_types = [loc["building_type"] for loc in locs_in_group]
        building_type = "Diğer" if "Diğer" in building_types else "Betonarme"
        
        risk_groups = [loc["risk_group"] for loc in locs_in_group]
        risk_group = min(risk_groups)
        
        building = sum(loc["building"] for loc in locs_in_group)
        fixture = sum(loc["fixture"] for loc in locs_in_group)
        decoration = sum(loc["decoration"] for loc in locs_in_group)
        
        commodity_sum_for_group = 0
        for loc_data in locs_in_group:
            comm_val = loc_data["commodity"]
            if loc_data.get("commodity_is_subscription", False):
                comm_val *= 0.40
            commodity_sum_for_group += comm_val
        commodity = commodity_sum_for_group
        
        safe = sum(loc["safe"] for loc in locs_in_group)
        machinery = sum(loc["machinery"] for loc in locs_in_group) # YENİ: Makine bedellerini topla
        bi = sum(loc["bi"] for loc in locs_in_group)
        ec_fixed = sum(loc["ec_fixed"] for loc in locs_in_group)
        ec_mobile = sum(loc["ec_mobile"] for loc in locs_in_group)
        mk_fixed = sum(loc["mk_fixed"] for loc in locs_in_group)
        mk_mobile = sum(loc["mk_mobile"] for loc in locs_in_group)
        
        result[group_key] = {
            "building_type": building_type,
            "risk_group": risk_group,
            "building": building,
            "fixture": fixture,
            "decoration": decoration,
            "commodity": commodity,
            "safe": safe,
            "machinery": machinery, # YENİ: Toplanmış makine bedelini ekle
            "bi": bi,
            "ec_fixed": ec_fixed,
            "ec_mobile": ec_mobile,
            "mk_fixed": mk_fixed,
            "mk_mobile": mk_mobile
        }
    return result

def calculate_fire_premium(building_type, risk_group, currency, building, fixture, decoration, commodity, safe, machinery, bi, ec_fixed, ec_mobile, mk_fixed, mk_mobile, koas, deduct, fx_rate, inflation_rate): # YENİ: machinery parametresi eklendi
    # Calculate individual sums insured in TRY
    building_sum_insured = building * fx_rate
    fixture_sum_insured = fixture * fx_rate
    decoration_sum_insured = decoration * fx_rate
    commodity_sum_insured = commodity * fx_rate
    safe_sum_insured = safe * fx_rate
    machinery_sum_insured = machinery * fx_rate # YENİ: Makine bedelini TRY'ye çevir
    bi_sum_insured = bi * fx_rate
    ec_fixed_sum_insured = ec_fixed * fx_rate
    ec_mobile_sum_insured = ec_mobile * fx_rate
    mk_fixed_sum_insured = mk_fixed * fx_rate
    mk_mobile_sum_insured = mk_mobile * fx_rate
    
    # Calculate total sum insured for PD (including EC and MK for limit check)
    pd_sum_insured = (building_sum_insured + fixture_sum_insured + decoration_sum_insured + commodity_sum_insured + safe_sum_insured + machinery_sum_insured ) # YENİ: machinery_sum_insured eklendi
    
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
    pd_sum_for_premium = (building_sum_insured + fixture_sum_insured + decoration_sum_insured + commodity_sum_insured + safe_sum_insured + machinery_sum_insured) # YENİ: machinery_sum_insured eklendi
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
    cpm_rate = base_rate * duration_multiplier  # Apply inflation to CPM rate
    if cpm_sum_insured > LIMIT:
        st.warning(tr("limit_warning_car"))
        cpm_rate *= (LIMIT / cpm_sum_insured)
    cpm_premium = (cpm_sum_insured * cpm_rate) / 1000
    
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
prefix_to_remove = brand_name 

if calc_title_full.startswith(prefix_to_remove):
    descriptive_part = calc_title_full[len(prefix_to_remove):]
elif calc_title_full == brand_name:
    descriptive_part = "" # Sadece marka adı var, açıklama yok
else:
    # Beklenmedik format veya marka adı başta değilse, tam metni açıklama olarak kullan
    descriptive_part = calc_title_full


# Main Content
st.markdown('<h2 class="section-header">📊 ' + (tr("select_calc")) + '</h2>', unsafe_allow_html=True)

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

# İçeriği dil-bağımsız anahtara göre göster
if st.session_state.active_calc_module == CALC_MODULE_FIRE:
    st.markdown(f'<h3 class="section-header">{tr("fire_header")}</h3>', unsafe_allow_html=True)

    # Para birimi ve kur girişi genel alana taşındı
    fire_general_col1, fire_general_col2 = st.columns(2)
    with fire_general_col1:
        # Benzersiz bir anahtar sağlamak için key güncellendi
        currency_fire = st.selectbox(tr("currency"), ["TRY", "USD", "EUR"], key="main_fire_module_currency")
    with fire_general_col2:
        # Benzersiz bir key_prefix sağlamak için güncellendi
        fx_rate_fire, fx_info_fire = fx_input(currency_fire, "main_fire_module")
    
    # fx_input fonksiyonu zaten TRY olmayan durumlar için st.info mesajını gösteriyor.
    # if currency_fire != "TRY":
    #     st.info(fx_info_fire) # Bu satır fx_input tarafından zaten yönetiliyor.

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
                
                risk_group = st.selectbox(
                    tr("risk_group"), 
                    [1, 2, 3, 4, 5, 6, 7], 
                    key=f"risk_group_{i}", 
                    help=tr("risk_group_help") # Sadece temel yardım metni
                )
                # YENİ: Selectbox'ın hemen altına st.button ile sayfa değiştirme
                if st.button(tr("learn_earthquake_zone_button"), key=f"learn_zone_btn_{i}", use_container_width=True):
                    st.switch_page("pages/earthquake_zones.py")

            with col2:
                group = st.selectbox(
                    tr("location_group"), 
                    groups, 
                    key=f"group_{i}", 
                    help=tr("location_group_help") + " " + tr("location_group_help_cumulative") # YENİ: Ek açıklama eklendi
                )
            
            st.markdown(f"#### {tr('insurance_sums')}")
            
            # İstenen düzende 3 ana kolon
            main_col1, main_col2, ec_mk_main_col = st.columns([2, 2, 3]) 

            with main_col1: # Sol Kolon
                building = st.number_input(tr("building_sum"), min_value=0.0, value=0.0, step=100000.0, key=f"building_{i}", help=tr("building_sum_help"), format="%.2f")
                if building > 0:
                    st.write(f"{tr('entered_value')}: {format_number(building, currency_fire)}")
                
                fixture = st.number_input(tr("fixture_sum"), min_value=0.0, value=0.0, step=100000.0, key=f"fixture_{i}", help=tr("fixture_sum_help"), format="%.2f")
                if fixture > 0:
                    st.write(f"{tr('entered_value')}: {format_number(fixture, currency_fire)}")
                
                decoration = st.number_input(tr("decoration_sum"), min_value=0.0, value=0.0, step=100000.0, key=f"decoration_{i}", help=tr("decoration_sum_help"), format="%.2f")
                if decoration > 0:
                    st.write(f"{tr('entered_value')}: {format_number(decoration, currency_fire)}")
                
                bi = st.number_input(tr("bi"), min_value=0.0, value=0.0, step=100000.0, key=f"bi_{i}", help=tr("bi_help"), format="%.2f")
                if bi > 0:
                    st.write(f"{tr('entered_value')}: {format_number(bi, currency_fire)}")
            
            with main_col2: # Orta Kolon
                commodity = st.number_input(tr("commodity_sum"), min_value=0.0, value=0.0, step=100000.0, key=f"commodity_{i}", help=tr("commodity_sum_help"), format="%.2f")
                commodity_is_subscription = st.checkbox(tr("commodity_is_subscription"), key=f"commodity_is_subscription_{i}", help=tr("commodity_is_subscription_help"))
                if commodity > 0:
                    display_comm_value = commodity * 0.40 if commodity_is_subscription else commodity
                    st.write(f"{tr('entered_value')}: {format_number(commodity, currency_fire)} ({tr('effective_value')}: {format_number(display_comm_value, currency_fire)})" if commodity_is_subscription else f"{tr('entered_value')}: {format_number(commodity, currency_fire)}")

                safe = st.number_input(tr("safe_sum"), min_value=0.0, value=0.0, step=100000.0, key=f"safe_{i}", help=tr("safe_sum_help"), format="%.2f")
                if safe > 0:
                    st.write(f"{tr('entered_value')}: {format_number(safe, currency_fire)}")
                
                machinery = st.number_input(tr("mk_sum"), min_value=0.0, value=0.0, step=100000.0, key=f"machinery_{i}", help=tr("mk_sum_help"), format="%.2f") # Genel Makine Bedeli
                if machinery > 0:
                    st.write(f"{tr('entered_value')}: {format_number(machinery, currency_fire)}")
                
            ec_fixed, ec_mobile, mk_fixed, mk_mobile = 0.0, 0.0, 0.0, 0.0 # Varsayılan değerler

            with ec_mk_main_col: # Sağ Kolon
                st.markdown(f"###### {tr('ec_mk_cover_options_header')}")
                include_ec_mk_cover = st.checkbox(tr("include_ec_mk_cover"), key=f"include_ec_mk_cover_{i}", value=True)

                if include_ec_mk_cover:
                    # Elektronik Cihaz Bedelleri
                    ec_fixed = st.number_input(tr("ec_fixed"), min_value=0.0, value=0.0, step=100000.0, key=f"ec_fixed_{i}", help=tr("ec_fixed_help"), format="%.2f")
                    if ec_fixed > 0:
                        st.write(f"{tr('entered_value')}: {format_number(ec_fixed, currency_fire)}")
                    
                    ec_mobile = st.number_input(tr("ec_mobile"), min_value=0.0, value=0.0, step=100000.0, key=f"ec_mobile_{i}", help=tr("ec_mobile_help"), format="%.2f")
                    if ec_mobile > 0:
                        st.write(f"{tr('entered_value')}: {format_number(ec_mobile, currency_fire)}")
                    

                    # Makine Kırılması Bedelleri
                    st.markdown(f"**{tr('mk_cover_subheader')}**") 
                    mk_fixed = st.number_input(tr("mk_fixed"), min_value=0.0, value=0.0, step=100000.0, key=f"mk_fixed_cover_{i}", help=tr("mk_fixed_cover_help"), format="%.2f")
                    if mk_fixed > 0:
                        st.write(f"{tr('entered_value')}: {format_number(mk_fixed, currency_fire)}")
                    
                    mk_mobile = st.number_input(tr("mk_mobile"), min_value=0.0, value=0.0, step=100000.0, key=f"mk_mobile_cover_{i}", help=tr("mk_mobile_cover_help"), format="%.2f")
                    if mk_mobile > 0:
                        st.write(f"{tr('entered_value')}: {format_number(mk_mobile, currency_fire)}")
            
            locations_data.append({
                "group": group,
                "building_type": building_type,
                "risk_group": risk_group,
                "building": building,
                "fixture": fixture,
                "decoration": decoration,
                "commodity": commodity,
                "commodity_is_subscription": commodity_is_subscription,
                "safe": safe,
                "machinery": machinery, # Orta kolondaki genel makine bedeli
                "bi": bi,             # Sol kolondaki kar kaybı bedeli
                "ec_fixed": ec_fixed if include_ec_mk_cover else 0.0,
                "ec_mobile": ec_mobile if include_ec_mk_cover else 0.0,
                "mk_fixed": mk_fixed if include_ec_mk_cover else 0.0,     # Sağ kolondaki Makine Kırılması (Sabit)
                "mk_mobile": mk_mobile if include_ec_mk_cover else 0.0,   # Sağ kolondaki Makine Kırılması (Mobil)
                "include_ec_mk_cover": include_ec_mk_cover
            })
    
    # YENİ: Dinamik Toplam Bedel Gösterimi (Hesapla Butonundan Önce)
    # locations_data listesi bu noktada en güncel kullanıcı girdilerini içerir.
    # Bu bedelleri, seçilen orijinal para biriminde toplayalım.
    current_total_pd_orig_ccy_display = 0.0
    current_total_bi_orig_ccy_display = 0.0
    for loc_data_item_display in locations_data:
        current_commodity_for_display = loc_data_item_display["commodity"]
        if loc_data_item_display.get("commodity_is_subscription", False):
            current_commodity_for_display *= 0.40
        
        current_total_pd_orig_ccy_display += (
            loc_data_item_display["building"] + loc_data_item_display["fixture"] +
            loc_data_item_display["decoration"] +
            current_commodity_for_display +
            loc_data_item_display["safe"] + 
            loc_data_item_display["machinery"] +
            loc_data_item_display["ec_fixed"] +  # EC/MK bedelleri de PD toplamına dahil
            loc_data_item_display["ec_mobile"] +
            loc_data_item_display["mk_fixed"] +
            loc_data_item_display["mk_mobile"]
        )
        current_total_bi_orig_ccy_display += loc_data_item_display["bi"]

    # Stil için info-box sınıfını kullanalım veya st.info() da tercih edilebilir.
    # currency_fire değişkeni yukarıda tanımlanmış olmalı.
    st.markdown(f"---") # Önceki bölümle arasına ayırıcı
    st.markdown(f"<h5>{tr('current_entered_sums_header')}</h5>", unsafe_allow_html=True) # Yeni başlık
    st.markdown(f'<div class="info-box">ℹ️ <b>{tr("total_entered_pd_sum")}:</b> {format_number(current_total_pd_orig_ccy_display, currency_fire)}</div>', unsafe_allow_html=True)
    if current_total_bi_orig_ccy_display > 0:
        st.markdown(f'<div class="info-box">ℹ️ <b>{tr("total_entered_bi_sum")}:</b> {format_number(current_total_bi_orig_ccy_display, currency_fire)}</div>', unsafe_allow_html=True)
    # YENİ KOD SONU

    st.markdown(f"#### {tr('coinsurance_deductible')}") # Bu satır zaten vardı
    col5, col6, col7 = st.columns(3)
    with col5:
        koas = st.selectbox(tr("koas"), list(koasurans_indirimi.keys()), help=tr("koas_help"))
    with col6:
        deduct = st.selectbox(tr("deduct"), sorted(list(muafiyet_indirimi.keys()), reverse=True), index=4, help=tr("deduct_help"))
    with col7:
        inflation_rate = st.number_input(tr("inflation_rate"), min_value=0.0, value=0.0, step=5.0, help=tr("inflation_rate_help"), format="%.2f")
    
    if st.button(tr("btn_calc"), key="fire_calc"):
        # Kullanıcının girdiği toplam ham bedelleri hesapla (orijinal para biriminde)
        total_entered_pd_orig_ccy = 0.0
        total_entered_bi_orig_ccy = 0.0
        for loc_data_item in locations_data: 
            current_commodity_for_total = loc_data_item["commodity"]
            if loc_data_item.get("commodity_is_subscription", False): # Abonman seçiliyse %40'ını al
                current_commodity_for_total *= 0.40
            
            total_entered_pd_orig_ccy += (
                loc_data_item["building"] + loc_data_item["fixture"] +
                loc_data_item["decoration"] +
                current_commodity_for_total + # Güncellenmiş emtia değeri
                loc_data_item["safe"] + 
                loc_data_item["machinery"] + # Genel Makine Bedeli eklendi
                loc_data_item["ec_fixed"] +
                loc_data_item["ec_mobile"] + 
                loc_data_item["mk_fixed"] +
                loc_data_item["mk_mobile"] 
            )
            total_entered_bi_orig_ccy += loc_data_item["bi"]

        proceed_with_calculation = True
        # if total_entered_pd_orig_ccy < 3500000000 or koas in ["90/10", "100/0"] or deduct in [0.1, 0.5, 1.0, 1.5]:
        if total_entered_pd_orig_ccy * fx_rate_fire < 3500000000: # Bedeli TRY'ye çevirerek kontrol et
            # Koasürans kontrolü
            if koas in ["90/10", "100/0"]:
                proceed_with_calculation = False
                st.warning(tr("warning_koas_below_3_5B").format(koas_value=koas))
            
            # Muafiyet kontrolü (deduct değeri muafiyet_indirimi dictionary'sindeki key'lerdir: 2, 3, 0.1, 0.5 vb.)
            # %2'den küçük muafiyetler: 0.1, 0.5, 1.0, 1.5
            if deduct in [0.1, 0.5, 1.0, 1.5]: # Bu muafiyetler % cinsinden değil, doğrudan anahtar değerleri
                proceed_with_calculation = False
                st.warning(tr("warning_deduct_below_3_5B").format(deduct_value=str(deduct)))


        # Girilen bedel özetini göster
        st.markdown(f"---")
        st.markdown(f"<h5>{tr('entered_sums_summary_header')}</h5>", unsafe_allow_html=True)
        st.markdown(f'<div class="info-box">ℹ️ <b>{tr("total_entered_pd_sum")}:</b> {format_number(total_entered_pd_orig_ccy, currency_fire)}</div>', unsafe_allow_html=True)
        if total_entered_bi_orig_ccy > 0: # Sadece BI bedeli girilmişse göster
            st.markdown(f'<div class="info-box">ℹ️ <b>{tr("total_entered_bi_sum")}:</b> {format_number(total_entered_bi_orig_ccy, currency_fire)}</div>', unsafe_allow_html=True)
        st.markdown(f"---")
        if proceed_with_calculation == True:
            groups_determined = determine_group_params(locations_data)
            total_premium_all_groups_try = 0.0
            all_groups_display_data_for_table = [] 
            all_groups_info_boxes = []
            grand_total_sum_insured_numeric = 0.0 # Bu değişkenler döngü içinde değil, burada sıfırlanmalı
            grand_total_premium_numeric = 0.0   # Bu değişkenler döngü içinde değil, burada sıfırlanmalı


            for group_key, data in groups_determined.items(): 
                pd_premium_try, bi_premium_try, ec_premium_try, mk_premium_try, group_premium_try, applied_rate = calculate_fire_premium(
                    data["building_type"], data["risk_group"], currency_fire, 
                    data["building"], data["fixture"], data["decoration"], data["commodity"], data["safe"],
                    data["machinery"], 
                    data["bi"], data["ec_fixed"], data["ec_mobile"], data["mk_fixed"], data["mk_mobile"],
                    koas, deduct, fx_rate_fire, inflation_rate 
                )
                total_premium_all_groups_try += group_premium_try
                
                display_currency_for_output = currency_fire
                display_fx_rate_for_output = fx_rate_fire if currency_fire != "TRY" else 1.0

                pd_premium_display_val = pd_premium_try / display_fx_rate_for_output
                bi_premium_display_val = bi_premium_try / display_fx_rate_for_output
                ec_premium_display_val = ec_premium_try / display_fx_rate_for_output
                mk_premium_display_val = mk_premium_try / display_fx_rate_for_output
                group_premium_display_val = group_premium_try / display_fx_rate_for_output

                pd_sum_orig_ccy = (data["building"] + data["fixture"] + data["decoration"] + data["commodity"] + data["safe"] + data["machinery"])
                bi_sum_orig_ccy = data["bi"]
                ec_sum_orig_ccy = data["ec_fixed"] + data["ec_mobile"]
                mk_sum_orig_ccy = data["mk_fixed"] + data["mk_mobile"]
                
                # Her grup için tablo verilerini geçici olarak topla
                current_group_table_data_for_this_iteration = []
                if pd_sum_orig_ccy > 0 or pd_premium_display_val > 0 :
                    current_group_table_data_for_this_iteration.append({
                        tr("table_col_coverage_type"): tr("coverage_pd_combined"),
                        "sum_insured_numeric": pd_sum_orig_ccy, 
                        "premium_numeric": pd_premium_display_val, 
                        tr("table_col_sum_insured"): format_number(pd_sum_orig_ccy, display_currency_for_output),
                        tr("table_col_premium"): format_number(pd_premium_display_val, display_currency_for_output)
                    })
                if data["bi"] > 0:
                    current_group_table_data_for_this_iteration.append({
                        tr("table_col_coverage_type"): tr("coverage_bi"),
                        "sum_insured_numeric": bi_sum_orig_ccy,
                        "premium_numeric": bi_premium_display_val,
                        tr("table_col_sum_insured"): format_number(bi_sum_orig_ccy, display_currency_for_output),
                        tr("table_col_premium"): format_number(bi_premium_display_val, display_currency_for_output)
                    })
                if data["ec_fixed"] > 0 or data["ec_mobile"] > 0:
                    current_group_table_data_for_this_iteration.append({
                        tr("table_col_coverage_type"): tr("coverage_ec"),
                        "sum_insured_numeric": ec_sum_orig_ccy,
                        "premium_numeric": ec_premium_display_val,
                        tr("table_col_sum_insured"): format_number(ec_sum_orig_ccy, display_currency_for_output),
                        tr("table_col_premium"): format_number(ec_premium_display_val, display_currency_for_output)
                    })
                if data["mk_fixed"] > 0 or data["mk_mobile"] > 0:
                    current_group_table_data_for_this_iteration.append({
                        tr("table_col_coverage_type"): tr("coverage_mk"),
                        "sum_insured_numeric": mk_sum_orig_ccy,
                        "premium_numeric": mk_premium_display_val,
                        tr("table_col_sum_insured"): format_number(mk_sum_orig_ccy, display_currency_for_output),
                        tr("table_col_premium"): format_number(mk_premium_display_val, display_currency_for_output)
                    })
                if current_group_table_data_for_this_iteration: 
                    all_groups_display_data_for_table.extend(current_group_table_data_for_this_iteration)

                # Info box'ları da hazırla (birden fazla grup durumu için)
                all_groups_info_boxes.append(f'<div class="info-box">✅ <b>{tr("group_premium")} ({group_key}):</b> {format_number(group_premium_display_val, display_currency_for_output)}</div>')
                if pd_sum_orig_ccy > 0 or pd_premium_display_val > 0:
                    all_groups_info_boxes.append(f'<div class="info-box">🏢 <b>{tr("pd_premium")} ({group_key}):</b> {format_number(pd_premium_display_val, display_currency_for_output)}</div>')
                if data["bi"] > 0:
                    all_groups_info_boxes.append(f'<div class="info-box">📉 <b>{tr("bi_premium")} ({group_key}):</b> {format_number(bi_premium_display_val, display_currency_for_output)}</div>')
                if data["ec_fixed"] > 0 or data["ec_mobile"] > 0:
                    all_groups_info_boxes.append(f'<div class="info-box">💻 <b>{tr("ec_premium")} ({group_key}):</b> {format_number(ec_premium_display_val, display_currency_for_output)}</div>')
                if data["mk_fixed"] > 0 or data["mk_mobile"] > 0:
                    all_groups_info_boxes.append(f'<div class="info-box">⚙️ <b>{tr("mk_premium")} ({group_key}):</b> {format_number(mk_premium_display_val, display_currency_for_output)}</div>')
                all_groups_info_boxes.append(f'<div class="info-box">📊 <b>{tr("applied_rate")} ({group_key}):</b> {applied_rate:.2f}‰</div>')



            if num_locations == 1 and len(groups_determined) == 1 and all_groups_display_data_for_table:
                # Sayısal toplamları SADECE bu tek grup için hesapla (all_groups_display_data_for_table zaten sadece bu gruba ait olmalı)
                grand_total_sum_insured_numeric = 0.0 # Yeniden sıfırla
                grand_total_premium_numeric = 0.0   # Yeniden sıfırla
                for row in all_groups_display_data_for_table: # Bu liste zaten tek gruba ait verileri içermeli
                    grand_total_sum_insured_numeric += row.get("sum_insured_numeric", 0.0)
                    grand_total_premium_numeric += row.get("premium_numeric", 0.0)

                # Geçici bir kopya oluşturup ona toplam satırını ekleyelim ki orijinal liste bozulmasın
                table_data_with_total = list(all_groups_display_data_for_table) 
                table_data_with_total.append({
                    tr("table_col_coverage_type"): f"**{tr('total_overall')}**",
                    tr("table_col_sum_insured"): f"**{format_number(grand_total_sum_insured_numeric, display_currency_for_output)}**",
                    tr("table_col_premium"): f"**{format_number(grand_total_premium_numeric, display_currency_for_output)}**"
                })
                
                import pandas as pd
                df_display_columns = [tr("table_col_coverage_type"), tr("table_col_sum_insured"), tr("table_col_premium")]
                # DataFrame'i toplam satırını içeren kopyadan oluştur
                df_results_table = pd.DataFrame(table_data_with_total)[df_display_columns]
                
                # st.table(df_results_table.style.set_properties(**{'text-align': 'left'}).set_table_styles([dict(selector='th', props=[('text-align', 'left')])])) # İndeksi gizle
                st.dataframe(df_results_table.style.set_properties(**{'text-align': 'left'}).set_table_styles([dict(selector='th', props=[('text-align', 'left')])]), use_container_width=True) # İndeksi gizle
                st.markdown(f'<div class="info-box">📊 <b>{tr("applied_rate")}:</b> {applied_rate:.2f}‰</div>', unsafe_allow_html=True)
            
            elif all_groups_info_boxes: # Eğer info box'lar için veri varsa (birden fazla grup veya tek grup ama tablo koşulu sağlanmadıysa)
                for box_html in all_groups_info_boxes: 
                    st.markdown(box_html, unsafe_allow_html=True)
                
                # Birden fazla grup varsa genel toplam primi de göster
                if not (num_locations == 1 and len(groups_determined) == 1):
                    total_premium_all_groups_display = total_premium_all_groups_try / display_fx_rate_for_output
                    st.markdown(f'<div class="info-box">💰 <b>{tr("total_premium")}:</b> {format_number(total_premium_all_groups_display, display_currency_for_output)}</div>', unsafe_allow_html=True)
            else:
                st.info(tr("no_premium_calculated_msg")) # Hesaplama sonucu gösterilecek bir şey yoksa mesaj

            # --- SENARYO HESAPLAMA VERİLERİNİ HAZIRLA ---
            st.markdown("---") # Ayırıcı
            scenario_definitions = [
                {"name_key": "scenario_8020_2_name", "koas_key": "80/20", "deduct_key": 2},
                {"name_key": "scenario_9010_2_name", "koas_key": "90/10", "deduct_key": 2},
                {"name_key": "scenario_8020_5_name", "koas_key": "80/20", "deduct_key": 5},
                {"name_key": "scenario_9010_5_name", "koas_key": "90/10", "deduct_key": 5},
                {"name_key": "scenario_7030_5_name", "koas_key": "70/30", "deduct_key": 5},
            ]

            calculated_scenarios_for_session = []

            for scenario_def in scenario_definitions:
                scenario_results_per_group = []
                # HATA BURADAYDI: 'groups' yerine 'groups_determined' kullanılmalı
                for group_key, data_group in groups_determined.items(): # DÜZELTİLDİ: groups_determined.items() kullanıldı
                    # Senaryo koasürans ve muafiyet değerleriyle PD ve BI primlerini hesapla
                    # calculate_fire_premium fonksiyonu primleri TRY cinsinden döndürür
                    pd_scenario_premium_try, bi_scenario_premium_try, _, _, _, _ = calculate_fire_premium(
                        data_group["building_type"], data_group["risk_group"], currency_fire,
                        data_group["building"], data_group["fixture"], data_group["decoration"], data_group["commodity"], data_group["safe"],
                        data_group["machinery"], data_group["bi"],
                        data_group["ec_fixed"], data_group["ec_mobile"], data_group["mk_fixed"], data_group["mk_mobile"],
                        scenario_def["koas_key"], scenario_def["deduct_key"],
                        fx_rate_fire, inflation_rate
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
                "num_locations": num_locations, # Kullanıcının girdiği lokasyon sayısı
                "total_pd_sum_orig_ccy": total_entered_pd_orig_ccy, # EC/MK dahil toplam PD bedeli
                "total_bi_sum_orig_ccy": total_entered_bi_orig_ccy,
                "currency_code": currency_fire,
                "fx_rate_at_calculation": fx_rate_fire,
                "groups_details": groups_determined, # DÜZELTİLDİ: groups_determined kullanıldı
                "calculated_scenarios": calculated_scenarios_for_session,
                "inflation_rate_at_calculation": inflation_rate,
                "main_koas": koas, # Ana hesaplamada kullanılan koasürans
                "main_deduct": deduct # Ana hesaplamada kullanılan muafiyet
            }

            # --- SENARYO HESAPLAMA SAYFASINA YÖNLENDİRME BUTONU ---
            # Bu buton 'pages/scenario_calculator_page.py' adlı yeni bir sayfaya yönlendirecektir.
            # Kullanıcının bu sayfayı oluşturması gerekmektedir.
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