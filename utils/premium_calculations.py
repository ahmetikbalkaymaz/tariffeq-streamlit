import streamlit as st
from datetime import datetime, timedelta # calculate_months_difference için
# from ..translations import T # Ana dizindeki translations.py'den T'yi içe aktar
from translations import T # Ana dizindeki translations.py'den T'yi içe aktar
# Bu modül içinde kullanılacak yerel bir tr fonksiyonu
# st.session_state'e erişim gerektirir
def _tr(key: str) -> str:
    lang_code = st.session_state.get('lang', 'TR') # Varsayılan dil TR
    return T.get(key, {}).get(lang_code, key)

# ------------------------------------------------------------
# CONSTANT TABLES
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

# Limitli Poliçe İndirim Oranları
limited_policy_discounts = {
    2: 0.30, 3: 0.35, 4: 0.40, 5: 0.45, 6: 0.50,
    7: 0.55, 8: 0.60, 9: 0.65, 10: 0.70, 11: 0.73,
    12: 0.75, 13: 0.78, 14: 0.80, 15: 0.83, 16: 0.85,
    17: 0.88, 18: 0.90, 19: 0.93, 20: 0.95
}

# ------------------------------------------------------------
# CALCULATION LOGIC FUNCTIONS
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
    estimated_days = (year_diff * 365) + (month_diff * 30) # Ortalama ay süresi
    remaining_days = total_days - estimated_days
    if remaining_days >= 15: # Ayın yarısından fazlası geçmişse bir sonraki aya yuvarla
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
        # Eğer grupta "Diğer" varsa, grubun yapı türü "Diğer" olur.
        building_type = "Diğer" if "Diğer" in building_types else "Betonarme"
        
        risk_groups = [loc["risk_group"] for loc in locs_in_group]
        risk_group = min(risk_groups) # En düşük risk grubu (en riskli olan) seçilir.
        
        # Bedelleri topla
        building = sum(loc["building"] for loc in locs_in_group)
        fixture = sum(loc["fixture"] for loc in locs_in_group)
        decoration = sum(loc["decoration"] for loc in locs_in_group)
        
        # Emtia için abonman kontrolü
        commodity_sum_for_group = 0
        for loc_data in locs_in_group:
            comm_val = loc_data["commodity"]
            if loc_data.get("commodity_is_subscription", False): # Abonman ise %40'ını al
                comm_val *= 0.40
            commodity_sum_for_group += comm_val
        commodity = commodity_sum_for_group
        
        safe = sum(loc["safe"] for loc in locs_in_group)
        machinery = sum(loc["machinery"] for loc in locs_in_group) 
        bi = sum(loc["bi"] for loc in locs_in_group)
        ec_fixed = sum(loc["ec_fixed"] for loc in locs_in_group)
        ec_mobile = sum(loc["ec_mobile"] for loc in locs_in_group)
        # mk_fixed = sum(loc["mk_fixed"] for loc in locs_in_group)
        mk_mobile = sum(loc["mk_mobile"] for loc in locs_in_group)
        
        result[group_key] = {
            "building_type": building_type,
            "risk_group": risk_group,
            "building": building,
            "fixture": fixture,
            "decoration": decoration,
            "commodity": commodity,
            "safe": safe,
            "machinery": machinery, 
            "bi": bi,
            "ec_fixed": ec_fixed,
            "ec_mobile": ec_mobile,
            # "mk_fixed": mk_fixed,
            "mk_mobile": mk_mobile
        }
    return result


def calculate_fire_premium(
    building_type, risk_group, currency,
    building, fixture, decoration, commodity, safe, machinery, bi,
    ec_fixed, ec_mobile, mk_fixed, mk_mobile,
    koas, deduct, fx_rate, inflation_rate,
    skip_limit_warnings=False,
    limited_policy_multiplier=1.0
):
    """
    Yangın ve ilişkili teminatlar için deprem primini hesaplar.
    Önceki doğru çalışan mantık temel alınarak yeniden düzenlenmiştir.
    """
    # 1. Temel Oranın Belirlenmesi ve Enflasyon Düzeltmesi
    base_rate = tarife_oranlari[building_type][risk_group - 1]
    inflation_multiplier = 1 + (inflation_rate / 100) / 2
    rate_with_inflation = base_rate * inflation_multiplier
    applied_rate = base_rate # PDF'te gösterilecek temel oran

    # 2. Teminat Bedellerinin Hesaplanması (TRY)
    building_try = building * fx_rate
    fixture_try = fixture * fx_rate
    decoration_try = decoration * fx_rate
    commodity_try = commodity * fx_rate
    safe_try = safe * fx_rate
    machinery_try = machinery * fx_rate
    bi_try = bi * fx_rate
    ec_fixed_try = ec_fixed * fx_rate
    ec_mobile_try = ec_mobile * fx_rate
    mk_fixed_try = mk_fixed * fx_rate
    mk_mobile_try = mk_mobile * fx_rate

    # 3. Limit Tanımları
    LIMIT_FIRE = 3_500_000_000
    LIMIT_EC_MK = 840_000_000

    # 4. Prim Hesaplamaları
    # PD (Yangın) Primi
    pd_sum_insured_try = building_try + fixture_try + decoration_try + commodity_try + safe_try + machinery_try
    koas_discount = koasurans_indirimi.get(koas, 0)
    deduct_discount = muafiyet_indirimi.get(deduct, 0)
    adjusted_rate_pd = rate_with_inflation * (1 - koas_discount) * (1 - deduct_discount)
    if pd_sum_insured_try > LIMIT_FIRE:
        if not skip_limit_warnings:
            st.warning(_tr("limit_warning_fire_pd"))
        adjusted_rate_pd *= (LIMIT_FIRE / pd_sum_insured_try)
    pd_premium_final = (pd_sum_insured_try * adjusted_rate_pd) / 1000

    # BI (Kar Kaybı) Primi - Koasürans ve muafiyet indirimi uygulanmaz
    adjusted_rate_bi = rate_with_inflation
    if bi_try > LIMIT_FIRE:
        if not skip_limit_warnings:
            st.warning(_tr("limit_warning_fire_bi"))
        adjusted_rate_bi *= (LIMIT_FIRE / bi_try)
    bi_premium_final = (bi_try * adjusted_rate_bi) / 1000

    # EC (Elektronik Cihaz) Primi
    ec_premium_final = 0.0
    if ec_fixed_try > 0:
        ec_fixed_rate = rate_with_inflation * (1 - koas_discount) * (1 - deduct_discount)
        if ec_fixed_try > LIMIT_EC_MK:
            if not skip_limit_warnings:
                st.warning(_tr("limit_warning_ec"))
            ec_fixed_rate *= (LIMIT_EC_MK / ec_fixed_try)
        ec_premium_final += (ec_fixed_try * ec_fixed_rate) / 1000
    if ec_mobile_try > 0:
        ec_mobile_rate = 2.00 * inflation_multiplier # Sabit oran 2.00
        if ec_mobile_try > LIMIT_EC_MK:
            if not skip_limit_warnings:
                st.warning(_tr("limit_warning_ec"))
            ec_mobile_rate *= (LIMIT_EC_MK / ec_mobile_try)
        ec_premium_final += (ec_mobile_try * ec_mobile_rate) / 1000

    # MK (Makine Kırılması) Primi
    mk_premium_final = 0.0
    if mk_fixed_try > 0: # Sabit makineler PD ile aynı mantıkta
        mk_fixed_rate = rate_with_inflation * (1 - koas_discount) * (1 - deduct_discount)
        if mk_fixed_try > LIMIT_EC_MK:
             if not skip_limit_warnings:
                st.warning(_tr("limit_warning_mk"))
             mk_fixed_rate *= (LIMIT_EC_MK / mk_fixed_try)
        mk_premium_final += (mk_fixed_try * mk_fixed_rate) / 1000
    if mk_mobile_try > 0: # Hareketli makineler EC mobil ile aynı mantıkta
        mk_mobile_rate = 2.00 * inflation_multiplier # Sabit oran 2.00
        if mk_mobile_try > LIMIT_EC_MK:
            if not skip_limit_warnings:
                st.warning(_tr("limit_warning_mk"))
            mk_mobile_rate *= (LIMIT_EC_MK / mk_mobile_try)
        mk_premium_final += (mk_mobile_try * mk_mobile_rate) / 1000

    # 5. Toplam Prim ve Limitli Poliçe Çarpanı
    total_premium = (pd_premium_final + bi_premium_final + ec_premium_final + mk_premium_final)
    final_premium = total_premium * limited_policy_multiplier

    # 6. Primleri orantısal olarak yeniden dağıt (limitli poliçe çarpanı sonrası)
    if total_premium > 0:
        pd_premium_final = (pd_premium_final / total_premium) * final_premium
        bi_premium_final = (bi_premium_final / total_premium) * final_premium
        ec_premium_final = (ec_premium_final / total_premium) * final_premium
        mk_premium_final = (mk_premium_final / total_premium) * final_premium
    else: # Eğer toplam prim sıfırsa, hepsi sıfır kalır
        pd_premium_final, bi_premium_final, ec_premium_final, mk_premium_final = 0, 0, 0, 0


    return pd_premium_final, bi_premium_final, ec_premium_final, mk_premium_final, final_premium, applied_rate

def calculate_car_ear_premium(
    risk_group_type, risk_class, start_date, end_date, 
    project, cpm, cpe, currency, koas, deduct, fx_rate, inflation_rate,
    skip_limit_warnings=False # Yeni parametre
    ):
    duration_months = calculate_months_difference(start_date, end_date)
    
    # Temel oran
    base_rate = tarife_oranlari[risk_group_type][risk_class - 1]
    
    # Enflasyon düzeltmesi
    inflation_multiplier = 1 + (inflation_rate / 100) / 2 
    base_rate *= inflation_multiplier
    
    # Süre çarpanı, koasürans ve muafiyet indirimleri
    duration_multiplier = calculate_duration_multiplier(duration_months)
    koas_discount = koasurans_indirimi_car[koas]
    deduct_discount = muafiyet_indirimi_car[deduct]
    
    LIMIT = 840_000_000 
    
    # CAR Primi (Proje Bedeli)
    project_sum_insured = project * fx_rate
    car_rate = base_rate * duration_multiplier * (1 - koas_discount) * (1 - deduct_discount)
    if project_sum_insured > LIMIT:
        if not skip_limit_warnings:
            st.warning(_tr("limit_warning_car"))
        car_rate *= (LIMIT / project_sum_insured) 
    car_premium = (project_sum_insured * car_rate) / 1000
    
    # CPM Primi (İnşaat/Montaj Makineleri) - Koasürans ve muafiyet indirimi uygulanmaz
    cpm_sum_insured = cpm * fx_rate
    cpm_rate = base_rate * duration_multiplier  
    if cpm_sum_insured > LIMIT:
        if not skip_limit_warnings:
            st.warning(_tr("limit_warning_car")) 
        cpm_rate *= (LIMIT / cpm_sum_insured)
    cpm_premium = (cpm_sum_insured * cpm_rate) / 1000
    
    # CPE Primi (Mevcut Yapı ve Tesisler) - Koasürans ve muafiyet indirimi uygulanmaz
    cpe_sum_insured = cpe * fx_rate
    cpe_rate = base_rate * duration_multiplier 
    if cpe_sum_insured > LIMIT:
        if not skip_limit_warnings:
            st.warning(_tr("limit_warning_car")) 
        cpe_rate *= (LIMIT / cpe_sum_insured)
    cpe_premium = (cpe_sum_insured * cpe_rate) / 1000
    
    total_premium = car_premium + cpm_premium + cpe_premium
    
    return car_premium, cpm_premium, cpe_premium, total_premium, car_rate