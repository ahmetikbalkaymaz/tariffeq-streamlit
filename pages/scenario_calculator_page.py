import streamlit as st
from translations import T # Projenizin ana dizinindeki translations.py dosyasından T'yi import edin

# Dil seçimi için session state başlatma (EĞER YOKSA)
if 'lang' not in st.session_state:
    st.session_state.lang = "TR"  # Varsayılan dil

# Dil değişkenini session state'den al
lang = st.session_state.lang

# Çeviri fonksiyonu
def tr(key: str, **kwargs) -> str:
    translation = T.get(key, {}).get(lang, key)
    if kwargs:
        return translation.format(**kwargs)
    return translation

st.set_page_config(page_title=tr("scenario_page_title"), layout="wide")

# Kenar Çubuğu Navigasyonu ve Dil Seçimi (calculate.py'den benzer şekilde eklenebilir)
with st.sidebar:
    st.image("./assets/logo.png", width=1000) # Ana dizine göre yol
    st.page_link("home.py", label=tr("home"), icon="🏠")
    st.page_link("pages/calculate.py", label=tr("calc"))
    st.page_link("pages/scenario_calculator_page.py", label=tr("scenario_page_title")) # Mevcut sayfa
    
    st.markdown("---")

    lang_options = ["TR", "EN"]
    current_lang_index = lang_options.index(st.session_state.lang)
    
    selected_lang_sidebar = st.radio(
        "Language / Dil", 
        options=lang_options, 
        index=current_lang_index, 
        key="sidebar_language_selector_scenario" # Bu sayfa için benzersiz anahtar
    )

    if selected_lang_sidebar != st.session_state.lang:
        st.session_state.lang = selected_lang_sidebar
        st.rerun()
    
    st.markdown("---")
    # Footer eklenebilir: st.markdown(f"<div class='sidebar-footer footer'>{tr('footer')}</div>", unsafe_allow_html=True)


st.title(tr("scenario_page_title"))

# Gerekli session state verilerini kontrol et
if 'scenario_data_for_page' not in st.session_state or \
   not st.session_state.scenario_data_for_page.get("groups_details"):
    st.warning(tr("scenario_data_missing_warning"))
    if st.button(tr("go_back_to_calculate_page")):
        st.switch_page("pages/calculate.py")
else:
    scenario_data = st.session_state.scenario_data_for_page
    groups_details = scenario_data.get("groups_details", {})
    num_groups = len(groups_details)

    if 'scenario_additional_inputs' not in st.session_state:
        st.session_state.scenario_additional_inputs = {}

    # Her grup (lokasyon) için ek bilgileri topla
    for i, group_key in enumerate(groups_details.keys()):
        # Her grup için session_state'de bir alt dictionary oluştur
        if group_key not in st.session_state.scenario_additional_inputs:
            st.session_state.scenario_additional_inputs[group_key] = {}

        # --- PD (Fiziksel Hasar) Bilgileri için Expander ---
        pd_expander_label = tr("additional_info_for_location_group", group_key=group_key, location_index=i+1, total_locations=num_groups)
        with st.expander(pd_expander_label, expanded=(i == 0)):
            st.subheader(f"{tr('building_info_header')} - {tr('group_label')} {group_key}")

            # 1. Bina Yaşı
            building_age_options_translated = tr("building_age_options")
            current_building_age_value = st.session_state.scenario_additional_inputs[group_key].get("building_age", building_age_options_translated[0])
            current_building_age_index = building_age_options_translated.index(current_building_age_value)
            st.session_state.scenario_additional_inputs[group_key]["building_age"] = st.selectbox(
                label=tr("building_age"),
                options=building_age_options_translated,
                key=f"building_age_group_{group_key}_pd",
                index=current_building_age_index
            )

            # 2. Yapı Tipi
            structural_type_options_translated = tr("structural_type_options")
            current_structural_type_value = st.session_state.scenario_additional_inputs[group_key].get("structural_type", structural_type_options_translated[0])
            current_structural_type_index = structural_type_options_translated.index(current_structural_type_value)
            st.session_state.scenario_additional_inputs[group_key]["structural_type"] = st.selectbox(
                label=tr("structural_type"),
                options=structural_type_options_translated,
                key=f"structural_type_group_{group_key}_pd",
                index=current_structural_type_index
            )

            # 3. Kat Sayısı
            num_floors_options_translated = tr("num_floors_options")
            current_num_floors_value = st.session_state.scenario_additional_inputs[group_key].get("num_floors", num_floors_options_translated[0])
            current_num_floors_index = num_floors_options_translated.index(current_num_floors_value)
            st.session_state.scenario_additional_inputs[group_key]["num_floors"] = st.selectbox(
                label=tr("num_floors"),
                options=num_floors_options_translated,
                key=f"num_floors_group_{group_key}_pd",
                index=current_num_floors_index
            )

            # 4. Faaliyet Türü (PD ve BI için ortak kullanılacak)
            activity_type_options_translated = tr("activity_type_options")
            current_activity_type_value = st.session_state.scenario_additional_inputs[group_key].get("activity_type", activity_type_options_translated[0])
            current_activity_type_index = activity_type_options_translated.index(current_activity_type_value)
            st.session_state.scenario_additional_inputs[group_key]["activity_type"] = st.selectbox(
                label=tr("activity_type"),
                options=activity_type_options_translated,
                key=f"activity_type_group_{group_key}_common",
                index=current_activity_type_index
            )

            # 5. Güçlendirme Durumu
            strengthening_options_translated = tr("strengthening_options")
            current_strengthening_value = st.session_state.scenario_additional_inputs[group_key].get("strengthening", strengthening_options_translated[1]) # Varsayılan "Hayır"
            current_strengthening_index = strengthening_options_translated.index(current_strengthening_value)
            st.session_state.scenario_additional_inputs[group_key]["strengthening"] = st.radio(
                label=tr("strengthening"),
                options=strengthening_options_translated,
                key=f"strengthening_group_{group_key}_pd",
                index=current_strengthening_index,
                horizontal=True
            )
            st.markdown("---")

        # --- BI (Kar Kaybı) Bilgileri için Ayrı Expander (Eğer BI bedeli varsa) ---
        group_data_from_calc = groups_details.get(group_key, {})
        bi_value_for_group = group_data_from_calc.get("bi", 0)

        if bi_value_for_group > 0:
            bi_expander_label = tr("bi_additional_info_header_for_group", group_key=group_key, location_index=i+1, total_locations=num_groups)
            with st.expander(bi_expander_label, expanded=(i == 0)):
                st.subheader(f"{tr('bi_info_header')} - {tr('group_label')} {group_key}")

                # 6. Alternatif Üretim Yeri (BI)
                alt_prod_options_translated = tr("alternative_production_site_options")
                current_alt_prod_value = st.session_state.scenario_additional_inputs[group_key].get("alternative_production_site", alt_prod_options_translated[1]) # Varsayılan "Hayır"
                current_alt_prod_index = alt_prod_options_translated.index(current_alt_prod_value)
                st.session_state.scenario_additional_inputs[group_key]["alternative_production_site"] = st.radio(
                    label=tr("alternative_production_site"),
                    options=alt_prod_options_translated,
                    key=f"alt_prod_site_group_{group_key}_bi",
                    index=current_alt_prod_index,
                    horizontal=True
                )

                # 7. Yıllık Ciro (BI)
                annual_turnover_options_translated = tr("annual_turnover_options")
                current_annual_turnover_value = st.session_state.scenario_additional_inputs[group_key].get("annual_turnover", annual_turnover_options_translated[0])
                current_annual_turnover_index = annual_turnover_options_translated.index(current_annual_turnover_value)
                st.session_state.scenario_additional_inputs[group_key]["annual_turnover"] = st.selectbox(
                    label=tr("annual_turnover"),
                    options=annual_turnover_options_translated,
                    key=f"annual_turnover_group_{group_key}_bi",
                    index=current_annual_turnover_index
                )

                # 8. İş Sürekliliği Planı (BI)
                bcp_options_translated = tr("business_continuity_plan_options")
                current_bcp_value = st.session_state.scenario_additional_inputs[group_key].get("business_continuity_plan", bcp_options_translated[1]) # Varsayılan "Hayır"
                current_bcp_index = bcp_options_translated.index(current_bcp_value)
                st.session_state.scenario_additional_inputs[group_key]["business_continuity_plan"] = st.radio(
                    label=tr("business_continuity_plan"),
                    options=bcp_options_translated,
                    key=f"bcp_group_{group_key}_bi",
                    index=current_bcp_index,
                    horizontal=True
                )
                st.markdown("---")

    # Tüm girdiler toplandıktan sonra bir sonraki adıma geçmek için bir buton veya bilgi mesajı eklenebilir.
    all_inputs_collected = True
    if num_groups > 0:
        for group_key in groups_details.keys():
            group_inputs = st.session_state.scenario_additional_inputs.get(group_key, {})
            
            required_pd_keys = ["building_age", "structural_type", "num_floors", "activity_type", "strengthening"]
            for pd_key in required_pd_keys:
                if pd_key not in group_inputs:
                    all_inputs_collected = False
                    break
            if not all_inputs_collected:
                break

            group_data_from_calc = groups_details.get(group_key, {})
            bi_value_for_group = group_data_from_calc.get("bi", 0)
            if bi_value_for_group > 0:
                required_bi_keys = ["alternative_production_site", "annual_turnover", "business_continuity_plan"]
                for bi_key in required_bi_keys:
                    if bi_key not in group_inputs:
                        all_inputs_collected = False
                        break
            if not all_inputs_collected:
                break
                
    elif num_groups == 0:
        all_inputs_collected = False

    if all_inputs_collected and num_groups > 0:
        st.success(tr("scenario_inputs_collected_info"))
        
        # --- HESAPLAMA VE VERİ HAZIRLAMA KISMINI BUTON DIŞINA TAŞIYORUZ ---
        # Bu kısım, all_inputs_collected True olduğunda her zaman çalışacak.
        # Filtreler değiştiğinde de bu veriler yeniden hesaplanacak.

        # Helper functions (Mevcut fonksiyonlarınız)
        def deprem_hasar_orani(bolge, yapi_tipi, bina_yasi, kat_sayisi, faaliyet, guclendirme):
            oranlar = {
                1: {"minor": 0.07, "expected": 0.20, "severe": 0.45},
                2: {"minor": 0.06, "expected": 0.17, "severe": 0.40},
                3: {"minor": 0.05, "expected": 0.13, "severe": 0.32},
                4: {"minor": 0.04, "expected": 0.09, "severe": 0.24},
                5: {"minor": 0.03, "expected": 0.06, "severe": 0.15},
                6: {"minor": 0.03, "expected": 0.06, "severe": 0.15},
                7: {"minor": 0.03, "expected": 0.06, "severe": 0.15},
            }
            carpani = 1.0
            if yapi_tipi == tr("structural_type_options")[1]: carpani *= 0.85 # Çelik
            elif yapi_tipi == tr("structural_type_options")[2]: carpani *= 1.15 # Yığma
            if bina_yasi == tr("building_age_options")[0]: carpani *= 0.90 # <10 yıl
            elif bina_yasi == tr("building_age_options")[1]: carpani *= 1.05 # 10–30 yıl
            elif bina_yasi == tr("building_age_options")[2]: carpani *= 1.20 # >30 yıl
            if kat_sayisi == tr("num_floors_options")[0]: carpani *= 0.95 # 1–3
            elif kat_sayisi == tr("num_floors_options")[2]: carpani *= 1.10 # 8 ve üzeri
            if faaliyet == tr("activity_type_options")[0]: carpani *= 1.15 # Depolama
            elif faaliyet == tr("activity_type_options")[1]: carpani *= 1.05 # Üretim
            elif faaliyet == tr("activity_type_options")[2]: carpani *= 0.90 # Ofis
            if guclendirme == tr("strengthening_options")[0]: carpani *= 0.85 # Evet
            base = oranlar.get(bolge, oranlar[7])
            res = {k: min(round(v * carpani, 3), 0.7) for k, v in base.items()}
            return res

        def calculate_bi_damage_ratio_multiplier(activity_type_selected, alt_prod_site_selected, annual_turnover_selected, bcp_selected):
            bi_carpani = 1.0
            if activity_type_selected == tr("activity_type_options")[0]: bi_carpani *= 0.80
            elif activity_type_selected == tr("activity_type_options")[1]: bi_carpani *= 1.00
            elif activity_type_selected == tr("activity_type_options")[2]: bi_carpani *= 0.60
            elif activity_type_selected == tr("activity_type_options")[3]: bi_carpani *= 0.90
            if alt_prod_site_selected == tr("alternative_production_site_options")[0]: bi_carpani *= 0.70
            if annual_turnover_selected == tr("annual_turnover_options")[2]: bi_carpani *= 1.05
            if bcp_selected == tr("business_continuity_plan_options")[0]: bi_carpani *= 0.90
            elif bcp_selected == tr("business_continuity_plan_options")[1]: bi_carpani *= 1.10
            return bi_carpani

        def hasar_senaryosu_hesapla(sigorta_bedeli, oran, muafiyet_orani, koasurans_sirket_payi):
            brut = sigorta_bedeli * oran
            muaf = brut * muafiyet_orani
            kalan = max(brut - muaf, 0)
            sirket_odeyecegi = kalan * koasurans_sirket_payi
            sigortali_odeyecegi = kalan * (1 - koasurans_sirket_payi)
            return int(brut), int(muaf), int(sirket_odeyecegi), int(sigortali_odeyecegi)

        alternatives_definition = [
            {"name_key": "alt_8020_2", "koasurans_sigortaci": 0.80, "muafiyet_oran": 0.02},
            {"name_key": "alt_9010_2", "koasurans_sigortaci": 0.90, "muafiyet_oran": 0.02},
            {"name_key": "alt_8020_5", "koasurans_sigortaci": 0.80, "muafiyet_oran": 0.05},
            {"name_key": "alt_9010_5", "koasurans_sigortaci": 0.90, "muafiyet_oran": 0.05},
            {"name_key": "alt_7030_5", "koasurans_sigortaci": 0.70, "muafiyet_oran": 0.05},
        ]

        fx_rate = scenario_data.get("fx_rate_at_calculation", 1.0)
        currency_code = scenario_data.get("currency_code", "TRY")
        
        def format_value_for_display(value, currency, rate, is_premium=False):
            if currency == "TRY" or rate == 0 or rate == 1.0:
                return f"{value:,.2f} TRY" if is_premium else f"{int(value):,} TRY"
            else:
                value_orig_ccy = value / rate
                if is_premium:
                    return f"{value_orig_ccy:,.2f} {currency} ({value:,.2f} TRY)"
                else:
                    return f"{int(value_orig_ccy):,} {currency} ({int(value):,} TRY)"

        pre_calculated_premiums = scenario_data.get("calculated_scenarios", [])

        # --- DEPREM HASAR SENARYO ANALİZİ BAŞLIĞI ---
        # Bu başlık, buton tıklandıktan sonra bir kez gösterilebilir veya her zaman gösterilebilir.
        # Eğer sadece buton tıklandıktan sonra gösterilmesi isteniyorsa, bir session_state değişkeni ile kontrol edilebilir.
        # Şimdilik her zaman gösterilecek şekilde bırakıyorum (all_inputs_collected True ise).
        st.markdown("---")
        st.subheader(tr("earthquake_scenario_analysis_title"))

        # Her grup için verileri bir sözlükte toplayalım
        all_groups_data_for_display = {}

        for group_key, group_data_orig_ccy in groups_details.items():
            # Bu döngü içindeki hesaplamalar her grup için yapılacak
            # ve sonuçlar all_groups_data_for_display altında saklanacak.
            
            additional_inputs = st.session_state.scenario_additional_inputs[group_key]
            bina_yasi_secilen = additional_inputs.get("building_age")
            yapi_tipi_secilen = additional_inputs.get("structural_type")
            kat_sayisi_secilen = additional_inputs.get("num_floors")
            faaliyet_secilen = additional_inputs.get("activity_type")
            guclendirme_secilen = additional_inputs.get("strengthening")
            alt_prod_site_secilen = additional_inputs.get("alternative_production_site")
            annual_turnover_secilen = additional_inputs.get("annual_turnover")
            bcp_secilen = additional_inputs.get("business_continuity_plan")

            deprem_bolgesi = group_data_orig_ccy.get("risk_group")
            if not deprem_bolgesi:
                # Bu uyarıyı döngü içinde göstermek yerine, belki en başta bir kontrol yapılabilir.
                # Şimdilik burada bırakıyorum.
                # st.warning(tr("risk_group_missing_for_group", group_key=group_key)) 
                continue

            pd_damage_ratios = deprem_hasar_orani(
                deprem_bolgesi, yapi_tipi_secilen, bina_yasi_secilen, kat_sayisi_secilen, faaliyet_secilen, guclendirme_secilen
            )
            bi_ratio_multiplier = 1.0
            if group_data_orig_ccy.get("bi", 0) > 0 and alt_prod_site_secilen is not None and annual_turnover_secilen is not None and bcp_secilen is not None:
                bi_ratio_multiplier = calculate_bi_damage_ratio_multiplier(
                    faaliyet_secilen, alt_prod_site_secilen, annual_turnover_secilen, bcp_secilen
                )

            pd_sum_insured_group_try = sum(group_data_orig_ccy.get(k, 0) for k in ["building", "fixture", "decoration", "commodity", "safe", "machinery", "ec_fixed", "ec_mobile", "mk_fixed", "mk_mobile"]) * fx_rate
            bi_sum_insured_group_try = group_data_orig_ccy.get("bi", 0) * fx_rate
            
            current_group_results_table_data = []
            for alt_def in alternatives_definition:
                alt_name_display = tr(alt_def["name_key"])
                koas_sigortaci_pd = alt_def["koasurans_sigortaci"]
                muafiyet_oran_pd = alt_def["muafiyet_oran"]
                etiket_display = ""
                if koas_sigortaci_pd == 0.70: etiket_display = tr("label_min_protection")
                elif koas_sigortaci_pd == 0.80: etiket_display = tr("label_balanced_protection")
                elif koas_sigortaci_pd == 0.90: etiket_display = tr("label_max_protection")
                
                current_pd_premium_try = 0
                current_bi_premium_try = 0
                for pre_calc_scen in pre_calculated_premiums:
                    if pre_calc_scen["name"] == alt_name_display:
                        for res_group in pre_calc_scen["results_per_group"]:
                            if res_group["group_key"] == group_key:
                                current_pd_premium_try = res_group.get("pd_premium_try", 0)
                                current_bi_premium_try = res_group.get("bi_premium_try", 0)
                                break
                        break
                total_premium_for_alt_try = current_pd_premium_try + current_bi_premium_try

                for scenario_key, pd_base_damage_rate in pd_damage_ratios.items():
                    scenario_name_display = tr(f"damage_scenario_{scenario_key}")
                    pd_brut, pd_muaf, pd_sirket, pd_sigortali = 0,0,0,0
                    if pd_sum_insured_group_try > 0:
                        pd_brut, pd_muaf, pd_sirket, pd_sigortali = hasar_senaryosu_hesapla(pd_sum_insured_group_try, pd_base_damage_rate, muafiyet_oran_pd, koas_sigortaci_pd)
                    bi_brut, bi_muaf, bi_sirket, bi_sigortali = 0,0,0,0
                    if bi_sum_insured_group_try > 0:
                        bi_effective_damage_rate = min(pd_base_damage_rate * bi_ratio_multiplier, 1.0)
                        bi_brut, bi_muaf, bi_sirket, bi_sigortali = hasar_senaryosu_hesapla(bi_sum_insured_group_try, bi_effective_damage_rate, 0.0, 1.0)
                    tcor_try = total_premium_for_alt_try + pd_sigortali
                    current_group_results_table_data.append({
                        tr("table_col_label"): etiket_display,
                        tr("table_col_alternative"): alt_name_display,
                        tr("table_col_pd_premium"): format_value_for_display(current_pd_premium_try, currency_code, fx_rate, is_premium=True),
                        tr("table_col_bi_premium"): format_value_for_display(current_bi_premium_try, currency_code, fx_rate, is_premium=True),
                        tr("table_col_total_premium"): format_value_for_display(total_premium_for_alt_try, currency_code, fx_rate, is_premium=True),
                        tr("table_col_scenario"): scenario_name_display,
                        tr("table_col_pd_gross_loss"): format_value_for_display(pd_brut, currency_code, fx_rate),
                        tr("table_col_pd_insurer_share"): format_value_for_display(pd_sirket, currency_code, fx_rate),
                        tr("table_col_pd_insured_share"): format_value_for_display(pd_sigortali, currency_code, fx_rate),
                        tr("table_col_bi_gross_loss"): format_value_for_display(bi_brut, currency_code, fx_rate),
                        tr("table_col_tcor"): format_value_for_display(tcor_try, currency_code, fx_rate, is_premium=False),
                    })
            
            # Her grup için hesaplanan verileri sakla
            all_groups_data_for_display[group_key] = {
                "results_for_group_table_data": current_group_results_table_data,
                "pd_damage_ratios": pd_damage_ratios,
                "bi_ratio_multiplier": bi_ratio_multiplier,
                "pd_sum_insured_group_try": pd_sum_insured_group_try,
                "bi_sum_insured_group_try": bi_sum_insured_group_try
                # Grafik ve limit önerileri için gerekli diğer veriler de buraya eklenebilir.
            }
        # --- TÜM GRUPLAR İÇİN VERİ HAZIRLAMA BİTTİ ---

        # Şimdi buton ile sadece gösterim ve etkileşim kısımlarını kontrol edebiliriz.
        # VEYA butonu tamamen kaldırıp, veriler hazır olduğunda her zaman gösterebiliriz.
        # Şimdilik butonu bırakıyorum, ancak içindeki mantık sadece gösterim olacak.

        # Eğer "Senaryo Hesapla" butonu hiç tıklanmadıysa veya state'i korumak istiyorsak,
        # bir session_state değişkeni kullanabiliriz.
        if 'show_scenario_results' not in st.session_state:
            st.session_state.show_scenario_results = False

        if st.button(tr("calculate_scenario_button"), key="calc_scenario_and_show_table_button"):
            st.session_state.show_scenario_results = True # Buton tıklandığında gösterimi aktifleştir

        if st.session_state.show_scenario_results: # Sadece buton tıklandıysa veya state True ise göster
            for group_key in groups_details.keys(): # groups_details.keys() yerine all_groups_data_for_display.keys() de kullanılabilir
                
                group_display_data = all_groups_data_for_display.get(group_key)
                if not group_display_data:
                    st.warning(tr("risk_group_missing_for_group", group_key=group_key)) # Eğer veri hazırlanamadıysa
                    continue

                results_for_group_table_data = group_display_data["results_for_group_table_data"]
                pd_damage_ratios_display = group_display_data["pd_damage_ratios"]
                bi_ratio_multiplier_display = group_display_data["bi_ratio_multiplier"]
                pd_sum_insured_group_try_display = group_display_data["pd_sum_insured_group_try"]
                bi_sum_insured_group_try_display = group_display_data["bi_sum_insured_group_try"]

                st.markdown(f"#### {tr('analysis_for_group', group_key=group_key)}")
                
                # --- PD Hasar Oranları ve Tahmini Kayıplar için st.metric Kullanımı ---
                st.markdown(f"##### {tr('pd_damage_ratios_for_group', group_key=group_key)}")
                col1, col2, col3 = st.columns(3)
                with col1:
                    minor_rate = pd_damage_ratios_display.get("minor", 0)
                    minor_loss_try = pd_sum_insured_group_try_display * minor_rate
                    st.metric(label=tr("minor_loss_rate_label"), value=f"{minor_rate:.1%}")
                    st.metric(label=tr("estimated_minor_loss_label"), value=format_value_for_display(minor_loss_try, currency_code, fx_rate))
                with col2:
                    expected_rate = pd_damage_ratios_display.get("expected", 0)
                    expected_loss_try = pd_sum_insured_group_try_display * expected_rate
                    st.metric(label=tr("expected_loss_rate_label"), value=f"{expected_rate:.1%}")
                    st.metric(label=tr("estimated_expected_loss_label"), value=format_value_for_display(expected_loss_try, currency_code, fx_rate))
                with col3:
                    severe_rate = pd_damage_ratios_display.get("severe", 0)
                    severe_loss_try = pd_sum_insured_group_try_display * severe_rate
                    st.metric(label=tr("severe_loss_rate_label"), value=f"{severe_rate:.1%}")
                    st.metric(label=tr("estimated_severe_loss_label"), value=format_value_for_display(severe_loss_try, currency_code, fx_rate))
                st.markdown("---")
                
                if bi_sum_insured_group_try_display > 0:
                    st.markdown(f"##### {tr('bi_damage_ratios_for_group', group_key=group_key)}")
                    st.metric(label=tr("bi_multiplier_label"), value=f"{bi_ratio_multiplier_display:.2f}x")
                    bi_col1, bi_col2, bi_col3 = st.columns(3)
                    with bi_col1:
                        bi_minor_rate = min(pd_damage_ratios_display.get("minor", 0) * bi_ratio_multiplier_display, 1.0)
                        bi_minor_loss_try = bi_sum_insured_group_try_display * bi_minor_rate
                        st.metric(label=tr("bi_minor_loss_rate_label"), value=f"{bi_minor_rate:.1%}")
                        st.metric(label=tr("estimated_bi_minor_loss_label"), value=format_value_for_display(bi_minor_loss_try, currency_code, fx_rate))
                    with bi_col2:
                        bi_expected_rate = min(pd_damage_ratios_display.get("expected", 0) * bi_ratio_multiplier_display, 1.0)
                        bi_expected_loss_try = bi_sum_insured_group_try_display * bi_expected_rate
                        st.metric(label=tr("bi_expected_loss_rate_label"), value=f"{bi_expected_rate:.1%}")
                        st.metric(label=tr("estimated_bi_expected_loss_label"), value=format_value_for_display(bi_expected_loss_try, currency_code, fx_rate))
                    with bi_col3:
                        bi_severe_rate = min(pd_damage_ratios_display.get("severe", 0) * bi_ratio_multiplier_display, 1.0)
                        bi_severe_loss_try = bi_sum_insured_group_try_display * bi_severe_rate
                        st.metric(label=tr("bi_severe_loss_rate_label"), value=f"{bi_severe_rate:.1%}")
                        st.metric(label=tr("estimated_bi_severe_loss_label"), value=format_value_for_display(bi_severe_loss_try, currency_code, fx_rate))
                    st.markdown("---")

                if results_for_group_table_data:
                    # --- FİLTRELEME SEÇENEKLERİ ---
                    # Bu kısım artık her zaman çalışacak (eğer results_for_group_table_data varsa)
                    # ve filtrelenmiş tabloyu gösterecek.
                    st.markdown("---") 
                    col_filter1, col_filter2 = st.columns(2)
                    etiket_filter_options = [tr("filter_option_all")] + sorted(list(set([d[tr("table_col_label")] for d in results_for_group_table_data if d[tr("table_col_label")]])))
                    selected_etiket_filter = col_filter1.selectbox(tr("filter_label_table_filters"), options=etiket_filter_options, key=f"etiket_filter_{group_key}")
                    scenario_filter_options = [tr("filter_option_all")] + sorted(list(set([d[tr("table_col_scenario")] for d in results_for_group_table_data])))
                    selected_scenario_filter = col_filter2.selectbox(tr("filter_label_damage_type_filters"), options=scenario_filter_options, key=f"scenario_filter_{group_key}")
                    st.markdown("---")

                    import pandas as pd
                    df_results_unfiltered = pd.DataFrame(results_for_group_table_data)
                    df_filtered = df_results_unfiltered.copy()
                    if selected_etiket_filter != tr("filter_option_all"):
                        df_filtered = df_filtered[df_filtered[tr("table_col_label")] == selected_etiket_filter]
                    if selected_scenario_filter != tr("filter_option_all"):
                        df_filtered = df_filtered[df_filtered[tr("table_col_scenario")] == selected_scenario_filter]

                    display_columns = [
                        tr("table_col_label"), tr("table_col_alternative"), tr("table_col_pd_premium"), tr("table_col_bi_premium"),
                        tr("table_col_total_premium"), tr("table_col_scenario"), tr("table_col_pd_gross_loss"),
                        tr("table_col_pd_insurer_share"), tr("table_col_pd_insured_share"), tr("table_col_bi_gross_loss"), tr("table_col_tcor")
                    ]
                    if not df_filtered.empty:
                        ordered_df_results = df_filtered[[col for col in display_columns if col in df_filtered.columns]]
                        st.dataframe(ordered_df_results, use_container_width=True, hide_index=True)
                    else:
                        st.warning(tr("no_data_after_filter"))
                    
                    # --- Bar Grafik Oluşturma ---
                    # Grafik verisi için results_for_group_table_data (filtrelenmemiş) veya df_filtered (filtrelenmiş) kullanılabilir.
                    # Eğer grafik de filtrelenecekse, aşağıdaki chart_data_list oluşturma df_filtered'ı kullanmalı.
                    # Şimdilik filtrelenmemiş veriden devam ediyorum.
                    chart_data_list_source = results_for_group_table_data # VEYA df_filtered.to_dict('records') EĞER GRAFİK DE FİLTRELENECEKSE
                    
                    if chart_data_list_source: # Grafik için veri kontrolü
                        chart_data_list = []
                        # ... (extract_try_value_from_formatted_string fonksiyonu burada veya globalde tanımlı olmalı) ...
                        def extract_try_value_from_formatted_string(formatted_str):
                            try:
                                if "(" in formatted_str and "TRY)" in formatted_str: return float(formatted_str.split('(')[1].split(' ')[0].replace(',', ''))
                                elif "TRY" in formatted_str: return float(formatted_str.split(' ')[0].replace(',', ''))
                                return 0
                            except ValueError: return 0

                        alternatives_for_chart = {}
                        for row_idx, row_data in enumerate(chart_data_list_source): # enumerate ile index de alabiliriz
                            # row_data bir sözlük olmalı (DataFrame.to_dict('records') sonucu gibi)
                            alt_name = row_data[tr("table_col_alternative")]
                            pd_premium_str = row_data[tr("table_col_pd_premium")]
                            pd_premium_val = extract_try_value_from_formatted_string(pd_premium_str)

                            if alt_name not in alternatives_for_chart:
                                alternatives_for_chart[alt_name] = {"pd_premium_try": pd_premium_val, "scenarios": {}}
                            
                            pd_insurer_share_str = row_data[tr("table_col_pd_insurer_share")]
                            bi_gross_loss_str = row_data[tr("table_col_bi_gross_loss")]
                            pd_insurer_share_val = extract_try_value_from_formatted_string(pd_insurer_share_str)
                            bi_gross_loss_val = extract_try_value_from_formatted_string(bi_gross_loss_str)
                            y_axis_value = pd_insurer_share_val + bi_gross_loss_val
                            
                            scenario_type_str = row_data[tr("table_col_scenario")]
                            scenario_legend_key = ""
                            if scenario_type_str == tr("damage_scenario_minor"): scenario_legend_key = tr("legend_minor_damage")
                            elif scenario_type_str == tr("damage_scenario_expected"): scenario_legend_key = tr("legend_expected_damage")
                            elif scenario_type_str == tr("damage_scenario_severe"): scenario_legend_key = tr("legend_severe_damage")
                            
                            if scenario_legend_key:
                                alternatives_for_chart[alt_name]["scenarios"][scenario_legend_key] = y_axis_value
                        
                        y_axis_column_name = tr("chart_yaxis_label_pd_insurer_plus_bi_gross_try")
                        final_chart_data_list = [] # Grafik için yeni liste
                        for alt_name, data_for_alt in alternatives_for_chart.items():
                            formatted_premium_display = f"{alt_name}\nPrim: {data_for_alt['pd_premium_try']:,.0f} TRY"
                            for scenario_legend_name, total_loss_value in data_for_alt["scenarios"].items():
                                final_chart_data_list.append({
                                    "alternative_label": formatted_premium_display,
                                    "scenario": scenario_legend_name,
                                    y_axis_column_name: total_loss_value
                                })
                        
                        if final_chart_data_list:
                            chart_df = pd.DataFrame(final_chart_data_list)
                            # ... (Altair grafik kodu aynı kalır) ...
                            import altair as alt
                            scenario_domain_sorted = [tr("legend_minor_damage"), tr("legend_expected_damage"), tr("legend_severe_damage")]
                            color_scale = alt.Scale(domain=scenario_domain_sorted, range=['#FFC107', '#FF9800', '#F44336'])
                            base_chart = alt.Chart(chart_df).mark_bar().encode(
                                x=alt.X('alternative_label:N', title=tr("chart_xaxis_label_alternatives_with_premium"), sort=None, axis=alt.Axis(labelAngle=0)),
                                y=alt.Y(f'{y_axis_column_name}:Q', title=y_axis_column_name), 
                                color=alt.Color('scenario:N', scale=color_scale, legend=alt.Legend(title=None)), # Legend'ı base chart'ta gizle
                                xOffset='scenario:N'
                            ).properties(title=tr("chart_title_combined_insurer_loss_scenarios", group_key=group_key))
                            
                            text_layer = alt.Chart(chart_df).mark_text(align='center', baseline='bottom', dy=-5).encode(
                                x=alt.X('alternative_label:N', sort=None),
                                y=alt.Y(f'{y_axis_column_name}:Q'),
                                text=alt.Text(f'{y_axis_column_name}:Q', format=",.0f"),
                                xOffset='scenario:N',
                                color=alt.Color('scenario:N', scale=color_scale, legend=None) # Metin katmanı için legend yok
                            )
                            
                            # Legend'ı sadece bir kez ve doğru şekilde oluşturmak için base_chart'ın bir kopyasını kullanabiliriz
                            # veya legend'ı ayrıca oluşturup ekleyebiliriz.
                            # Şimdilik configure_legend ile devam edelim, base_chart'ın color encoding'indeki legend=None'ı kaldırabiliriz.
                            # VEYA: Legend'ı sadece base_chart'a ait olacak şekilde bırakıp, text_layer'da legend=None kullanmak doğru.
                            # Eğer legend base_chart'tan geliyorsa ve text_layer'da legend=None ise sorun olmamalı.
                            # Sorun configure_legend'ın kendisiyle ilgili olabilir.
                            # Önceki configure_legend ayarlarınızı geri yükleyebilirsiniz.
                            
                            # Legend'ı manuel olarak oluşturup base_chart'a ekleyelim:
                            legend_selection = alt.selection_multi(fields=['scenario'], bind='legend')

                            final_layered_chart = (base_chart + text_layer).add_selection(
                                legend_selection # Eğer interaktif legend isteniyorsa
                            ).configure_axis(
                                labelFontSize=10, titleFontSize=12
                            ).configure_legend( # Bu configure_legend'ı base_chart'a veya layered_chart'a uygulayabilirsiniz
                                title=None, # Legend başlığını kaldır
                                labelFontSize=10,
                                titleFontSize=12, # Başlık kaldırıldığı için bu etkisiz olabilir
                                symbolStrokeWidth=2, # Sembol kenar kalınlığı
                                padding=5 # Legend etrafındaki boşluk
                            ).configure_view(
                                strokeWidth=0
                            ).properties(
                                width=alt.Step(80) 
                            )
                            st.altair_chart(final_layered_chart, use_container_width=True)
                        st.markdown("---")

                # --- LİMİT TAVSİYELERİ BÖLÜMÜ ---
                # Bu kısım da group_display_data içindeki pd_sum_insured_group_try_display vb. kullanmalı
                st.subheader(tr("limit_recommendations_title", group_key=group_key))
                st.info(tr("limit_recommendation_intro"))
                limit_recommendations_data = []
                pd_sector_recommendation_text = ""
                bi_sector_recommendation_text = ""

                pd_full_value = pd_sum_insured_group_try_display
                pd_minor_limit = pd_sum_insured_group_try_display * pd_damage_ratios_display.get("minor", 0)
                pd_expected_limit = pd_sum_insured_group_try_display * pd_damage_ratios_display.get("expected", 0)
                pd_severe_limit = pd_sum_insured_group_try_display * pd_damage_ratios_display.get("severe", 0)
                pd_expected_limit_str = format_value_for_display(pd_expected_limit, currency_code, fx_rate).split(' (')[0]
                pd_severe_limit_str = format_value_for_display(pd_severe_limit, currency_code, fx_rate).split(' (')[0]
                pd_sector_recommendation_text = tr("sector_recommendation_text_pd", expected_limit_str=pd_expected_limit_str, severe_limit_str=pd_severe_limit_str)
                limit_recommendations_data.append({
                    tr("limit_table_col_coverage"): tr("coverage_pd"),
                    tr("limit_table_col_full_value"): format_value_for_display(pd_full_value, currency_code, fx_rate),
                    tr("limit_table_col_minor_limit"): format_value_for_display(pd_minor_limit, currency_code, fx_rate),
                    tr("limit_table_col_expected_limit"): format_value_for_display(pd_expected_limit, currency_code, fx_rate),
                    tr("limit_table_col_severe_limit"): format_value_for_display(pd_severe_limit, currency_code, fx_rate),
                })

                if bi_sum_insured_group_try_display > 0:
                    bi_full_value = bi_sum_insured_group_try_display
                    bi_minor_rate_for_limit = min(pd_damage_ratios_display.get("minor", 0) * bi_ratio_multiplier_display, 1.0)
                    bi_expected_rate_for_limit = min(pd_damage_ratios_display.get("expected", 0) * bi_ratio_multiplier_display, 1.0)
                    bi_severe_rate_for_limit = min(pd_damage_ratios_display.get("severe", 0) * bi_ratio_multiplier_display, 1.0)
                    bi_minor_limit = bi_sum_insured_group_try_display * bi_minor_rate_for_limit
                    bi_expected_limit = bi_sum_insured_group_try_display * bi_expected_rate_for_limit
                    bi_severe_limit = bi_sum_insured_group_try_display * bi_severe_rate_for_limit
                    bi_expected_limit_str = format_value_for_display(bi_expected_limit, currency_code, fx_rate).split(' (')[0]
                    bi_severe_limit_str = format_value_for_display(bi_severe_limit, currency_code, fx_rate).split(' (')[0]
                    bi_sector_recommendation_text = tr("sector_recommendation_text_bi", expected_limit_str=bi_expected_limit_str, severe_limit_str=bi_severe_limit_str)
                    limit_recommendations_data.append({
                        tr("limit_table_col_coverage"): tr("coverage_bi"),
                        tr("limit_table_col_full_value"): format_value_for_display(bi_full_value, currency_code, fx_rate),
                        tr("limit_table_col_minor_limit"): format_value_for_display(bi_minor_limit, currency_code, fx_rate),
                        tr("limit_table_col_expected_limit"): format_value_for_display(bi_expected_limit, currency_code, fx_rate),
                        tr("limit_table_col_severe_limit"): format_value_for_display(bi_severe_limit, currency_code, fx_rate),
                    })
                
                if limit_recommendations_data:
                    df_limit_recommendations = pd.DataFrame(limit_recommendations_data)
                    st.table(df_limit_recommendations)
                    if pd_sector_recommendation_text: st.info(f"**{tr('coverage_pd')} {tr('limit_table_col_sector_recommendation')}:** {pd_sector_recommendation_text}")
                    if bi_sector_recommendation_text: st.info(f"**{tr('coverage_bi')} {tr('limit_table_col_sector_recommendation')}:** {bi_sector_recommendation_text}")
                    st.markdown("---")

            # --- TÜM GRUPLAR İÇİN ANALİZ BİTTİKTEN SONRA GENEL LİMİT TAVSİYELERİ ---
            if st.session_state.show_scenario_results: # Sadece sonuçlar gösteriliyorsa genel tavsiyeleri de göster
                st.subheader(tr("general_limit_advice_title"))
                st.markdown(tr("general_limit_advice_text"), unsafe_allow_html=True)
                st.markdown("---")

    elif num_groups == 0:
        st.info(tr("no_location_data_for_additional_info"))

    # calculate.py'den gelen prim senaryolarını gösterme kısmı isteğe bağlı olarak kalabilir veya kaldırılabilir.
    # Şimdilik yorum satırı yapıyorum, çünkü yeni tablo daha kapsamlı.
    # if scenario_data.get("calculated_scenarios"):
    #     st.markdown("---")
    #     st.subheader(tr("premium_scenarios_from_calculate_page")) 
    #     # ... (önceki kod) ...


# CSS stillerini ekleyebilirsiniz (calculate.py'den benzer şekilde)
# st.markdown("""<style>...</style>""", unsafe_allow_html=True)


