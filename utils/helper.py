import streamlit as st
import requests
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta


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
        
        # Emtia bedelini abonman durumuna göre hesapla
        commodity_sum_for_group = 0
        for loc_data in locs_in_group:
            comm_val = loc_data["commodity"]
            if loc_data.get("commodity_is_subscription", False): # Abonman seçiliyse %40'ını al
                comm_val *= 0.40
            commodity_sum_for_group += comm_val
        commodity = commodity_sum_for_group
        
        safe = sum(loc["safe"] for loc in locs_in_group)
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
            "commodity": commodity, # Abonman uygulanmış emtia toplamı
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