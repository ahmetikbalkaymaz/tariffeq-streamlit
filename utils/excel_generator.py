import pandas as pd
import io
from openpyxl.styles import Font
from translations import T
from datetime import date

def create_fire_excel(
    locations_data,
    groups_determined,
    num_locations,
    currency_fire,
    koas,
    deduct,
    inflation_rate,
    limited_policy_multiplier,
    premium_results_by_group,
    total_premium_all_groups_try,
    display_currency,
    display_fx_rate,
    ui_helpers,
    language="TR",
    scenario_data=None,
    apply_limited_policy=False,
    limited_policy_limit=0,
    fx_info="" # YENİ: Parametre eklendi
):
    """
    Hesaplanan prim ve bedel tablolarını, her grup için ayrı bir sayfada olacak şekilde
    bir Excel dosyası olarak oluşturur.
    """
    # YENİ: Limitli poliçe durumuna göre gösterilecek koasürans/muafiyet değerlerini belirle
    if apply_limited_policy:
        koas_display = "-"
        deduct_display = "-"
    else:
        koas_display = koas
        deduct_display = f"{deduct}%"

    def _tr_excel(key):
        return T.get(key, {}).get(language, key)
    output = io.BytesIO()

    # Excel dosyasını bir context manager ile oluşturuyoruz, bu sayede otomatik olarak kaydedilir.
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        # YENİ: Sayı formatlarını tanımla
        currency_format = f'#,##0.00 "{display_currency}"'
        rate_format = '0.0000'

        # --- Genel Bilgiler Sayfası ---
        info_data = {
            _tr_excel("info_label"): [_tr_excel("report_date"), _tr_excel("currency"), _tr_excel("koas"), _tr_excel("deduct"), _tr_excel("inflation_rate")],
            _tr_excel("info_value"): [date.today().strftime('%d.%m.%Y'), currency_fire, koas_display, deduct_display, f"{inflation_rate}%"]
        }
        # YENİ: Dövizli poliçe ise kur bilgisini ekle
        if currency_fire != "TRY":
            info_data[_tr_excel("info_label")].insert(2, _tr_excel("exchange_rate_info"))
            info_data[_tr_excel("info_value")].insert(2, fx_info)

        if apply_limited_policy:
            info_data[_tr_excel("info_label")].append(_tr_excel("limited_policy_limit"))
            info_data[_tr_excel("info_value")].append(limited_policy_limit)

        df_info = pd.DataFrame(info_data)

        # Genel Bilgiler sayfasını oluştur
        sheet_name_info = _tr_excel("general_info_sheet_name")
        df_info.to_excel(writer, sheet_name=sheet_name_info, index=False, header=False)

        worksheet_info = writer.sheets[sheet_name_info]
        for column_cells in worksheet_info.columns:
            max_length = max(len(str(cell.value)) for cell in column_cells)
            worksheet_info.column_dimensions[column_cells[0].column_letter].width = max_length + 2

        # --- İcmal (Özet) Tablosu için verileri toplama ---
        icmal_data_summary = {
            "Yangın": {"Bedel": 0, "Prim": 0},
            "Kar Kaybı": {"Bedel": 0, "Prim": 0},
            "Elektronik Cihaz": {"Bedel": 0, "Prim": 0},
            "Makine Kırılması": {"Bedel": 0, "Prim": 0},
        }

        # --- Her bir Kümül Grubu için ayrı bir Sayfa oluşturma ---
        for group_key, data in groups_determined.items():
            premiums = premium_results_by_group[group_key]

            pd_sum = data.get("building", 0) + data.get("fixture", 0) + data.get("decoration", 0) + data.get("commodity_raw_for_display", data.get("commodity", 0)) + data.get("safe", 0) + data.get("machinery", 0)
            bi_sum = data.get("bi", 0)
            ec_sum = data.get("ec_fixed", 0) + data.get("ec_mobile", 0)
            mk_sum = data.get("mk_fixed", 0) + data.get("mk_mobile", 0)
            
            pd_premium = premiums['pd_premium_try'] / display_fx_rate
            bi_premium = premiums['bi_premium_try'] / display_fx_rate
            ec_premium = premiums['ec_premium_try'] / display_fx_rate
            mk_premium = premiums['mk_premium_try'] / display_fx_rate
            
            pd_rate = (pd_premium / pd_sum) * 1000 if pd_sum > 0 else 0.0
            bi_rate = (bi_premium / bi_sum) * 1000 if bi_sum > 0 else 0.0
            ec_rate = (ec_premium / ec_sum) * 1000 if ec_sum > 0 else 0.0
            mk_rate = (mk_premium / mk_sum) * 1000 if mk_sum > 0 else 0.0

            icmal_data_summary["Yangın"]["Bedel"] += pd_sum
            icmal_data_summary["Yangın"]["Prim"] += pd_premium
            icmal_data_summary["Kar Kaybı"]["Bedel"] += bi_sum
            icmal_data_summary["Kar Kaybı"]["Prim"] += bi_premium
            icmal_data_summary["Elektronik Cihaz"]["Bedel"] += ec_sum
            icmal_data_summary["Elektronik Cihaz"]["Prim"] += ec_premium
            icmal_data_summary["Makine Kırılması"]["Bedel"] += mk_sum
            icmal_data_summary["Makine Kırılması"]["Prim"] += mk_premium

            table_data = []
            col_teminat = _tr_excel("table_col_coverage_type")
            col_bedel = f'{_tr_excel("table_col_sum_insured")} ({display_currency})'
            col_rate = _tr_excel("table_col_rate_per_mille")
            col_prim = f'{_tr_excel("table_col_premium")} ({display_currency})'

            if pd_sum > 0: table_data.append({col_teminat: _tr_excel("fire"), col_bedel: pd_sum, col_rate: pd_rate, col_prim: pd_premium})
            if bi_sum > 0: table_data.append({col_teminat: _tr_excel("bi"), col_bedel: bi_sum, col_rate: bi_rate, col_prim: bi_premium})
            if ec_sum > 0: table_data.append({col_teminat: _tr_excel("ec"), col_bedel: ec_sum, col_rate: ec_rate, col_prim: ec_premium})
            if mk_sum > 0: table_data.append({col_teminat: _tr_excel("mb"), col_bedel: mk_sum, col_rate: mk_rate, col_prim: mk_premium})
            
            if not table_data: continue

            df_group = pd.DataFrame(table_data)
            total_bedel = df_group[col_bedel].sum()
            total_prim = df_group[col_prim].sum()
            total_rate = (total_prim / total_bedel) * 1000 if total_bedel > 0 else 0.0
            total_row = pd.DataFrame([{col_teminat: _tr_excel("total"), col_bedel: total_bedel, col_rate: total_rate, col_prim: total_prim}])
            df_group = pd.concat([df_group, total_row], ignore_index=True)

            sheet_name = f"{group_key} " + _tr_excel("cumulative_group_suffix")
            df_group.to_excel(writer, sheet_name=sheet_name, index=False)

            worksheet = writer.sheets[sheet_name]
            for col_idx, col_name in enumerate(df_group.columns):
                col_letter = chr(ord('A') + col_idx)
                if col_name == col_bedel or col_name == col_prim:
                    for cell in worksheet[col_letter][1:]: cell.number_format = currency_format
                elif col_name == col_rate:
                    for cell in worksheet[col_letter][1:]: cell.number_format = rate_format
            
            for column_cells in worksheet.columns:
                max_length = max(len(str(cell.value)) for cell in column_cells)
                worksheet.column_dimensions[column_cells[0].column_letter].width = max_length + 2

        # --- İcmal (Özet) Sayfasını Oluşturma ---
        icmal_table_data = []
        col_teminat = _tr_excel("table_col_coverage_type")
        col_bedel = f'{_tr_excel("table_col_sum_insured")} ({display_currency})'
        col_rate = _tr_excel("table_col_rate_per_mille")
        col_prim = f'{_tr_excel("table_col_premium")} ({display_currency})'

        def get_rate(prim, bedel): return (prim / bedel) * 1000 if bedel > 0 else 0.0

        if icmal_data_summary["Yangın"]["Bedel"] > 0: icmal_table_data.append({col_teminat: _tr_excel("fire"), col_bedel: icmal_data_summary["Yangın"]["Bedel"], col_rate: get_rate(icmal_data_summary["Yangın"]["Prim"], icmal_data_summary["Yangın"]["Bedel"]), col_prim: icmal_data_summary["Yangın"]["Prim"]})
        if icmal_data_summary["Kar Kaybı"]["Bedel"] > 0: icmal_table_data.append({col_teminat: _tr_excel("bi"), col_bedel: icmal_data_summary["Kar Kaybı"]["Bedel"], col_rate: get_rate(icmal_data_summary["Kar Kaybı"]["Prim"], icmal_data_summary["Kar Kaybı"]["Bedel"]), col_prim: icmal_data_summary["Kar Kaybı"]["Prim"]})
        if icmal_data_summary["Elektronik Cihaz"]["Bedel"] > 0: icmal_table_data.append({col_teminat: _tr_excel("ec"), col_bedel: icmal_data_summary["Elektronik Cihaz"]["Bedel"], col_rate: get_rate(icmal_data_summary["Elektronik Cihaz"]["Prim"], icmal_data_summary["Elektronik Cihaz"]["Bedel"]), col_prim: icmal_data_summary["Elektronik Cihaz"]["Prim"]})
        if icmal_data_summary["Makine Kırılması"]["Bedel"] > 0: icmal_table_data.append({col_teminat: _tr_excel("mb"), col_bedel: icmal_data_summary["Makine Kırılması"]["Bedel"], col_rate: get_rate(icmal_data_summary["Makine Kırılması"]["Prim"], icmal_data_summary["Makine Kırılması"]["Bedel"]), col_prim: icmal_data_summary["Makine Kırılması"]["Prim"]})
        
        if icmal_table_data:
            df_icmal = pd.DataFrame(icmal_table_data)
            total_bedel_icmal = df_icmal[col_bedel].sum()
            total_prim_icmal = df_icmal[col_prim].sum()
            total_rate_icmal = get_rate(total_prim_icmal, total_bedel_icmal)
            total_row_icmal = pd.DataFrame([{col_teminat: _tr_excel("total"), col_bedel: total_bedel_icmal, col_rate: total_rate_icmal, col_prim: total_prim_icmal}])
            df_icmal = pd.concat([df_icmal, total_row_icmal], ignore_index=True)

            sheet_name_icmal = _tr_excel("summary_sheet_name")
            df_icmal.to_excel(writer, sheet_name=sheet_name_icmal, index=False)
            
            worksheet_icmal = writer.sheets[sheet_name_icmal]
            for col_idx, col_name in enumerate(df_icmal.columns):
                col_letter = chr(ord('A') + col_idx)
                if col_name == col_bedel or col_name == col_prim:
                    for cell in worksheet_icmal[col_letter][1:]: cell.number_format = currency_format
                elif col_name == col_rate:
                    for cell in worksheet_icmal[col_letter][1:]: cell.number_format = rate_format

            for column_cells in worksheet_icmal.columns:
                max_length = max(len(str(cell.value)) for cell in column_cells)
                worksheet_icmal.column_dimensions[column_cells[0].column_letter].width = max_length + 2

        # --- Senaryo Analizi Sayfasını Oluşturma ---
        if not apply_limited_policy and scenario_data and scenario_data.get('calculated_scenarios'):
            scenarios_list = []
            main_total_premium_orig = total_premium_all_groups_try / display_fx_rate
            
            # Oran hesaplaması için toplam PD ve BI bedelini al
            total_pd_sum_orig = sum(g.get("building", 0) + g.get("fixture", 0) + g.get("decoration", 0) + g.get("commodity", 0) + g.get("safe", 0) + g.get("machinery", 0) for g in groups_determined.values())
            total_bi_sum_orig = sum(g.get("bi", 0) for g in groups_determined.values())
            total_scenario_sum_orig = (total_pd_sum_orig + total_bi_sum_orig)

            main_rate = (main_total_premium_orig / total_scenario_sum_orig) * 1000 if total_scenario_sum_orig > 0 else 0.0
            
            # Ana senaryo satırı
            scenarios_list.append({
                _tr_excel('scenario_name'): f"{_tr_excel('main_scenario_name')} ({koas} - {deduct}%)",
                _tr_excel('coinsurance_label'): koas,
                f"{_tr_excel('deductible_label')} (%)": deduct,
                _tr_excel("table_col_rate_per_mille"): main_rate,
                f"{_tr_excel('total_premium_try')} ({display_currency})": main_total_premium_orig,
                f"{_tr_excel('difference_from_main')} (%)": "-"
            })

            # Diğer senaryolar
            for scenario in scenario_data['calculated_scenarios']:
                scenario_total_premium_try = sum(g['pd_premium_try'] + g['bi_premium_try'] for g in scenario['results_per_group'])
                scenario_total_premium_orig = scenario_total_premium_try / display_fx_rate
                percentage_diff = ((scenario_total_premium_orig - main_total_premium_orig) / main_total_premium_orig) * 100 if main_total_premium_orig > 0 else 0
                scenario_rate = (scenario_total_premium_orig / total_scenario_sum_orig) * 1000 if total_scenario_sum_orig > 0 else 0.0

                scenarios_list.append({
                    _tr_excel('scenario_name'): scenario['name'],
                    _tr_excel('coinsurance_label'): scenario['koas_key'],
                    f"{_tr_excel('deductible_label')} (%)": scenario['deduct_key'],
                    _tr_excel("table_col_rate_per_mille"): scenario_rate,
                    f"{_tr_excel('total_premium_try')} ({display_currency})": scenario_total_premium_orig,
                    f"{_tr_excel('difference_from_main')} (%)": f"{percentage_diff:+.1f}%"
                })
            
            scenario_df = pd.DataFrame(scenarios_list)
            if not scenario_df.empty:
                sheet_name_scenario = _tr_excel("scenario_analysis_sheet_name")
                scenario_df.to_excel(writer, sheet_name=sheet_name_scenario, index=False)

                worksheet_scenario = writer.sheets[sheet_name_scenario]
                
                premium_col_name = f"{_tr_excel('total_premium_try')} ({display_currency})"
                rate_col_name = _tr_excel("table_col_rate_per_mille")

                for col_idx, col_name in enumerate(scenario_df.columns):
                    col_letter = chr(ord('A') + col_idx)
                    if col_name == premium_col_name:
                        for cell in worksheet_scenario[col_letter][1:]: cell.number_format = currency_format
                    elif col_name == rate_col_name:
                        for cell in worksheet_scenario[col_letter][1:]: cell.number_format = rate_format

                for column_cells in worksheet_scenario.columns:
                    max_length = max(len(str(cell.value)) for cell in column_cells)
                    worksheet_scenario.column_dimensions[column_cells[0].column_letter].width = max_length + 2
        
        # --- HATA KONTROLÜ ---
        # Kaydetmeden önce en az bir sayfa oluşturulduğundan emin ol.
        # Eğer hiç sayfa yoksa (veri girilmemişse), hata vermesini engelle.
        if not writer.sheets:
            return b""

    output.seek(0)
    return output.getvalue()


def create_car_excel(data, ui_helpers, language="TR"):
    """
    Hesaplama verilerini kullanarak CAR/EAR Poliçesi için bir Excel raporu oluşturur.
    Yangın modülü ile aynı kütüphane ve mantık kullanılarak yeniden düzenlenmiştir.
    """
    def _tr(key, lang=language):
        """Yerel çeviri yardımcısı"""
        return T.get(key, {}).get(lang, key)

    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        # --- Riziko Bilgileri ---
        risk_info = {
            _tr("info_label"): [_tr("report_date"), _tr("currency"), _tr("risk_group_type"), _tr("risk_class"), _tr("start_date"), _tr("end_date"), _tr("duration"), _tr("koas"), _tr("deduct"), _tr("inflation_rate")],
            _tr("info_value"): [date.today().strftime('%d.%m.%Y'), data.get('currency', '-'), data.get('risk_group_type', '-'), data.get('risk_class', '-'), data.get('start_date').strftime('%d.%m.%Y'), data.get('end_date').strftime('%d.%m.%Y'), f"{data.get('duration_months', '-')} Ay", data.get('koas', '-'), f"{data.get('deduct', '-')}%", f"{data.get('inflation_rate', 0.0)}%"]
        }
        # YENİ: Dövizli poliçe ise kur bilgisini ekle
        if data.get('currency') != "TRY" and data.get('fx_info'):
            risk_info[_tr("info_label")].insert(2, _tr("exchange_rate_info"))
            risk_info[_tr("info_value")].insert(2, data.get('fx_info'))

        df_risk_info = pd.DataFrame(risk_info)

        # --- Prim Detayları ---
        display_currency = data['currency']
        fx_rate = data.get('fx_rate', 1.0)

        col_teminat = _tr('table_col_coverage_type')
        col_bedel_orig = f"{_tr('table_col_sum_insured')} ({display_currency})"
        col_bedel_try = f"{_tr('table_col_sum_insured')} (TRY)"
        col_rate = _tr('table_col_rate_per_mille')
        col_prim_try = f"{_tr('table_col_premium')} (TRY)"

        premium_data = [
            {col_teminat: _tr('coverage_car_ear'), col_bedel_orig: data['project_sum'], col_prim_try: data['car_premium_try']},
            {col_teminat: _tr('coverage_cpm'), col_bedel_orig: data['cpm_sum'], col_prim_try: data['cpm_premium_try']},
            {col_teminat: _tr('coverage_cpe'), col_bedel_orig: data['cpe_sum'], col_prim_try: data['cpe_premium_try']},
        ]
        df_premium = pd.DataFrame(premium_data)
        
        # TRY bedellerini ve oranları hesapla
        df_premium[col_bedel_try] = df_premium[col_bedel_orig] * fx_rate
        df_premium[col_rate] = (df_premium[col_prim_try] / df_premium[col_bedel_try]) * 1000 if fx_rate > 0 else 0

        # Toplam satırını ekle
        total_row = pd.DataFrame([{
            col_teminat: _tr('total_overall'),
            col_bedel_orig: df_premium[col_bedel_orig].sum(),
            col_bedel_try: df_premium[col_bedel_try].sum(),
            col_rate: (df_premium[col_prim_try].sum() / df_premium[col_bedel_try].sum()) * 1000 if df_premium[col_bedel_try].sum() > 0 else 0,
            col_prim_try: df_premium[col_prim_try].sum()
        }])
        df_premium = pd.concat([df_premium, total_row], ignore_index=True)
        
        # Sütun sırasını düzenle
        df_premium = df_premium[[col_teminat, col_bedel_orig, col_bedel_try, col_rate, col_prim_try]]

        # --- Excel'e Yazma ve Biçimlendirme ---
        sheet_name = 'CAR-EAR Raporu'
        df_risk_info.to_excel(writer, sheet_name=sheet_name, index=False, startrow=0)
        df_premium.to_excel(writer, sheet_name=sheet_name, index=False, startrow=len(df_risk_info) + 2)

        worksheet = writer.sheets[sheet_name]

        # Sayı formatlarını tanımla
        format_orig = f'"{display_currency}" #,##0.00'
        format_try = '"TRY" #,##0.00'
        format_rate = '0.0000'

        # Prim tablosu için formatlama
        start_row = len(df_risk_info) + 4 # Başlık ve bir boşluk satırı sonrası
        for row in worksheet.iter_rows(min_row=start_row, max_row=start_row + len(df_premium) -1):
            row[1].number_format = format_orig # Orijinal Bedel
            row[2].number_format = format_try  # TRY Bedel
            row[3].number_format = format_rate # Oran
            row[4].number_format = format_try  # TRY Prim

        # Sütun genişliklerini ayarla
        for column_cells in worksheet.columns:
            max_length = max(len(str(cell.value).strip()) for cell in column_cells if cell.value)
            worksheet.column_dimensions[column_cells[0].column_letter].width = max_length + 4

        # YENİ: Senaryo Analizi Sayfasını Oluşturma
        scenario_data = data.get('scenario_data')
        if scenario_data:
            scenarios_list = []
            main_total_premium_orig = data['total_premium_try'] / fx_rate
            
            # Ana senaryo satırı
            scenarios_list.append({
                _tr('scenario_name'): f"{_tr('main_scenario_name')} ({data['koas']} - {data['deduct']}%)",
                _tr('coinsurance_label'): data['koas'],
                f"{_tr('deductible_label')} (%)": data['deduct'],
                f"{_tr('total_premium_try')} ({display_currency})": main_total_premium_orig,
                f"{_tr('difference_from_main')} (%)": "-"
            })

            # Diğer senaryolar
            for scenario in scenario_data:
                scenario_total_premium_orig = scenario['total_premium'] / fx_rate
                percentage_diff = ((scenario_total_premium_orig - main_total_premium_orig) / main_total_premium_orig) * 100 if main_total_premium_orig > 0 else 0
                
                scenarios_list.append({
                    _tr('scenario_name'): scenario['name'],
                    _tr('coinsurance_label'): scenario['koas_key'],
                    f"{_tr('deductible_label')} (%)": scenario['deduct_key'],
                    f"{_tr('total_premium_try')} ({display_currency})": scenario_total_premium_orig,
                    f"{_tr('difference_from_main')} (%)": f"{percentage_diff:+.1f}%"
                })
            
            scenario_df = pd.DataFrame(scenarios_list)
            if not scenario_df.empty:
                sheet_name_scenario = _tr("scenario_analysis_sheet_name")
                scenario_df.to_excel(writer, sheet_name=sheet_name_scenario, index=False)

                worksheet_scenario = writer.sheets[sheet_name_scenario]
                premium_col_name = f"{_tr('total_premium_try')} ({display_currency})"

                for col_idx, col_name in enumerate(scenario_df.columns):
                    col_letter = chr(ord('A') + col_idx)
                    if col_name == premium_col_name:
                        for cell in worksheet_scenario[col_letter][1:]: cell.number_format = format_orig

                for column_cells in worksheet_scenario.columns:
                    max_length = max(len(str(cell.value)) for cell in column_cells)
                    worksheet_scenario.column_dimensions[column_cells[0].column_letter].width = max_length + 2

    output.seek(0)
    return output.getvalue()
