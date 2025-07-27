import weasyprint
from datetime import date
import base64
from translations import T
from utils import ui_helpers
# Logo dosyasını base64'e çevirerek HTML içine gömme fonksiyonu
def get_image_file_as_base64_data(path):
    try:
        with open(path, 'rb') as f:
            return base64.b64encode(f.read()).decode('utf-8')
    except FileNotFoundError:
        # Logo bulunamazsa, base64 verisi boş döner ve resim görüntülenmez.
        return ""
    
def _tr(key, lang="TR"):
    """PDF için çeviri fonksiyonu"""
    return T.get(key, {}).get(lang, key)

# FONKSİYON TANIMI DÜZELTİLDİ: 'locations_data' parametresi eklendi
def create_fire_pdf(
    locations_data,
    groups_determined,
    num_locations,
    currency_fire,
    koas,
    deduct,
    inflation_rate,
    premium_results_by_group,
    total_premium_all_groups_try,
    display_currency,
    display_fx_rate,
    ui_helpers,
    language="TR",
    scenario_data=None,  # YENİ PARAMETRE
    apply_limited_policy=False, # YENİ PARAMETRE
    limited_policy_limit=0      # YENİ PARAMETRE
    ):
    """
    Hesaplama verilerini kullanarak Yangın Poliçesi için bir PDF raporu oluşturur.
    Lokasyon adlarını da içerecek şekilde güncellenmiştir.
    """
    today_formatted = date.today().strftime('%d.%m.%Y')
    logo_base64 = get_image_file_as_base64_data("assets/logo.png")

    # ----- Tabloları HTML olarak oluşturma -----
    
    # 1. Riziko Bilgileri Tablosu (Genel)
    # YENİ: Limitli poliçe durumuna göre tabloyu ayarla
    koas_display = "-" if apply_limited_policy else koas
    deduct_display = "-" if apply_limited_policy else deduct
    
    risk_info_html = f"""
        <table class="info-table">
            <tr>
                <td>Para Birimi</td>
                <td>{currency_fire}</td>
            </tr>
            <tr>
                <td>Lokasyon Sayısı</td>
                <td>{num_locations}</td>
            </tr>
    """
    if apply_limited_policy:
        risk_info_html += f"""
            <tr>
                <td>Poliçe Limiti</td>
                <td>{ui_helpers.format_number(limited_policy_limit, currency_fire)}</td>
            </tr>
        """
    
    risk_info_html += f"""
            <tr>
                <td>Koasürans Oranı</td>
                <td>{koas_display}</td>
            </tr>
             <tr>
                <td>Muafiyet Oranı (%)</td>
                <td>{deduct_display}</td>
            </tr>
             <tr>
                <td>Enflasyon Artış Oranı (%)</td>
                <td>{inflation_rate}</td>
            </tr>
        </table>
    """

    # 2. YENİ: Lokasyon Detayları Tablosu
    location_details_html = "<h3>Lokasyon Bilgileri</h3>"
    location_details_html += """
    <table class="info-table location-details">
        <thead>
            <tr>
                <th>Lokasyon Adı / Adresi</th>
                <th>Kümül Grubu</th>
                <th>Yapı Tarzı</th>
                <th>Deprem Risk Grubu</th>
            </tr>
        </thead>
        <tbody>
    """
    # Her bir lokasyon için bir satır oluştur
    for loc in locations_data:
        location_details_html += f"""
        <tr>
            <td>{loc.get('location_name', 'N/A')}</td>
            <td>{_tr("group_label_format", lang=language).format(group_char=loc['group'])}</td>
            <td>{loc['building_type']}</td>
            <td>{loc['risk_group']}</td>
        </tr>
        """
    location_details_html += "</tbody></table>"

    # 3. Sonuçlar Tablosu (Teminat Bazında)
    results_html = f"<h3>{_tr('premium_summary_header', lang=language)}</h3>"
    results_html += """
    <table class="results-table">
        <thead>
            <tr>
                <th>Teminat</th>
                <th>Bedel</th>
                <th>Fiyat (‰)</th>
                <th>Prim</th>
            </tr>
        </thead>
        <tbody>
    """
    icmal_data = {
        "Yangın": {"Bedel": 0, "Prim": 0},
        "Kar Kaybı": {"Bedel": 0, "Prim": 0},
        "Elektronik Cihaz": {"Bedel": 0, "Prim": 0},
        "Makine Kırılması": {"Bedel": 0, "Prim": 0},
        "Toplam": {"Bedel": 0, "Prim": 0}
    }

    for group_key, data in groups_determined.items():
        premiums = premium_results_by_group[group_key]
        
        pd_sum = data.get("building", 0) + data.get("fixture", 0) + data.get("decoration", 0) + data.get("commodity_raw_for_display", data.get("commodity", 0)) + data.get("safe", 0) + data.get("machinery", 0)
        bi_sum = data.get("bi", 0)
        ec_sum = data.get("ec_fixed", 0) + data.get("ec_mobile", 0)
        mk_sum = data.get("mk_fixed", 0) + data.get("mk_mobile", 0)
        total_sum = pd_sum + bi_sum + ec_sum + mk_sum

        pd_premium = premiums['pd_premium_try'] / display_fx_rate
        bi_premium = premiums['bi_premium_try'] / display_fx_rate
        ec_premium = premiums['ec_premium_try'] / display_fx_rate
        mk_premium = premiums['mk_premium_try'] / display_fx_rate
        total_premium = premiums['total_premium_try'] / display_fx_rate
        
        # Efektif oranları hesapla (‰ cinsinden)
        pd_rate = (pd_premium / pd_sum) * 1000 if pd_sum > 0 else 0.0
        bi_rate = (bi_premium / bi_sum) * 1000 if bi_sum > 0 else 0.0
        ec_rate = (ec_premium / ec_sum) * 1000 if ec_sum > 0 else 0.0
        mk_rate = (mk_premium / mk_sum) * 1000 if mk_sum > 0 else 0.0
        total_rate = (total_premium / total_sum) * 1000 if total_sum > 0 else 0.0
        
        icmal_data["Yangın"]["Bedel"] += pd_sum
        icmal_data["Yangın"]["Prim"] += pd_premium
        icmal_data["Kar Kaybı"]["Bedel"] += bi_sum
        icmal_data["Kar Kaybı"]["Prim"] += bi_premium
        icmal_data["Elektronik Cihaz"]["Bedel"] += ec_sum
        icmal_data["Elektronik Cihaz"]["Prim"] += ec_premium
        icmal_data["Makine Kırılması"]["Bedel"] += mk_sum
        icmal_data["Makine Kırılması"]["Prim"] += mk_premium
        icmal_data["Toplam"]["Bedel"] += total_sum
        icmal_data["Toplam"]["Prim"] += total_premium

        results_html += f"<h3>{group_key} Kümülü Sonuçları</h3>"
        results_html += """
        <table class="results-table">
            <thead><tr><th>Teminat</th><th>Bedel</th><th>Fiyat (‰)</th><th>Prim</th></tr></thead>
            <tbody>"""
        if pd_sum > 0: results_html += f'<tr><td>Yangın</td><td>{ui_helpers.format_number(pd_sum, display_currency)}</td><td>{ui_helpers.format_rate(pd_rate)}</td><td>{ui_helpers.format_number(pd_premium, display_currency)}</td></tr>'
        if bi_sum > 0: results_html += f'<tr><td>Kar Kaybı</td><td>{ui_helpers.format_number(bi_sum, display_currency)}</td><td>{ui_helpers.format_rate(bi_rate)}</td><td>{ui_helpers.format_number(bi_premium, display_currency)}</td></tr>'
        if ec_sum > 0: results_html += f'<tr><td>Elektronik Cihaz</td><td>{ui_helpers.format_number(ec_sum, display_currency)}</td><td>{ui_helpers.format_rate(ec_rate)}</td><td>{ui_helpers.format_number(ec_premium, display_currency)}</td></tr>'
        if mk_sum > 0: results_html += f'<tr><td>Makine Kırılması</td><td>{ui_helpers.format_number(mk_sum, display_currency)}</td><td>{ui_helpers.format_rate(mk_rate)}</td><td>{ui_helpers.format_number(mk_premium, display_currency)}</td></tr>'
        results_html += f"""
                <tr class="total-row">
                    <td>Toplam</td>
                    <td>{ui_helpers.format_number(total_sum, display_currency)}</td>
                    <td>{ui_helpers.format_rate(total_rate)}</td>
                    <td>{ui_helpers.format_number(total_premium, display_currency)}</td>
                </tr></tbody></table>"""

    # İcmal tablosu için de fiyat sütunu eklendi
    icmal_html = "<h3>İcmal</h3>"
    icmal_html += """
    <table class="results-table">
        <thead><tr><th>Teminat</th><th>Bedel</th><th>Fiyat (‰)</th><th>Prim</th></tr></thead>
        <tbody>"""
    
    # İcmal için efektif oranları hesapla
    pd_icmal_rate = (icmal_data["Yangın"]["Prim"] / icmal_data["Yangın"]["Bedel"]) * 1000 if icmal_data["Yangın"]["Bedel"] > 0 else 0.0
    bi_icmal_rate = (icmal_data["Kar Kaybı"]["Prim"] / icmal_data["Kar Kaybı"]["Bedel"]) * 1000 if icmal_data["Kar Kaybı"]["Bedel"] > 0 else 0.0
    ec_icmal_rate = (icmal_data["Elektronik Cihaz"]["Prim"] / icmal_data["Elektronik Cihaz"]["Bedel"]) * 1000 if icmal_data["Elektronik Cihaz"]["Bedel"] > 0 else 0.0
    mk_icmal_rate = (icmal_data["Makine Kırılması"]["Prim"] / icmal_data["Makine Kırılması"]["Bedel"]) * 1000 if icmal_data["Makine Kırılması"]["Bedel"] > 0 else 0.0
    total_icmal_rate = (icmal_data["Toplam"]["Prim"] / icmal_data["Toplam"]["Bedel"]) * 1000 if icmal_data["Toplam"]["Bedel"] > 0 else 0.0
    
    if icmal_data["Yangın"]["Bedel"] > 0: icmal_html += f'<tr><td>Yangın</td><td>{ui_helpers.format_number(icmal_data["Yangın"]["Bedel"], display_currency)}</td><td>{ui_helpers.format_rate(pd_icmal_rate)}</td><td>{ui_helpers.format_number(icmal_data["Yangın"]["Prim"], display_currency)}</td></tr>'
    if icmal_data["Kar Kaybı"]["Bedel"] > 0: icmal_html += f'<tr><td>Kar Kaybı</td><td>{ui_helpers.format_number(icmal_data["Kar Kaybı"]["Bedel"], display_currency)}</td><td>{ui_helpers.format_rate(bi_icmal_rate)}</td><td>{ui_helpers.format_number(icmal_data["Kar Kaybı"]["Prim"], display_currency)}</td></tr>'
    if icmal_data["Elektronik Cihaz"]["Bedel"] > 0: icmal_html += f'<tr><td>Elektronik Cihaz</td><td>{ui_helpers.format_number(icmal_data["Elektronik Cihaz"]["Bedel"], display_currency)}</td><td>{ui_helpers.format_rate(ec_icmal_rate)}</td><td>{ui_helpers.format_number(icmal_data["Elektronik Cihaz"]["Prim"], display_currency)}</td></tr>'
    if icmal_data["Makine Kırılması"]["Bedel"] > 0: icmal_html += f'<tr><td>Makine Kırılması</td><td>{ui_helpers.format_number(icmal_data["Makine Kırılması"]["Bedel"], display_currency)}</td><td>{ui_helpers.format_rate(mk_icmal_rate)}</td><td>{ui_helpers.format_number(icmal_data["Makine Kırılması"]["Prim"], display_currency)}</td></tr>'
    icmal_html += f"""
            <tr class="total-row">
                <td>Toplam</td>
                <td>{ui_helpers.format_number(icmal_data["Toplam"]["Bedel"], display_currency)}</td>
                <td>{ui_helpers.format_rate(total_icmal_rate)}</td>
                <td>{ui_helpers.format_number(icmal_data["Toplam"]["Prim"], display_currency)}</td>
            </tr></tbody></table>"""

    # İcmal tablosu sonrası senaryo tablosunu ekle
    scenario_html = ""
    # YENİ: Limitli poliçe seçiliyse senaryo tablosunu oluşturma
    if not apply_limited_policy and scenario_data and scenario_data.get('calculated_scenarios'):
        scenario_html = f"<h3>{_tr('scenario_analysis_title', language)}</h3>"
        scenario_html += f"""
        <table class="results-table scenario-table">
            <thead>
                <tr>
                    <th>{_tr('scenario_name', language)}</th>
                    <th>{_tr('coinsurance_label', language)}</th>
                    <th>{_tr('deductible_label', language)} (%)</th>
                    <th>{_tr('total_premium_try', language)} ({display_currency})</th>
                    <th>{_tr('difference_from_main', language)} (%)</th>
                </tr>
            </thead>
            <tbody>"""
        
        # Ana senaryo (mevcut hesaplama) primi
        main_total_premium_orig = total_premium_all_groups_try / display_fx_rate
        
        # Ana senaryo satırı
        scenario_html += f"""
        <tr class="main-scenario-row">
            <td>{_tr('main_scenario_name', language)} ({koas} - {deduct}%)</td>
            <td>{koas}</td>
            <td>{deduct}</td>
            <td>{ui_helpers.format_number(main_total_premium_orig, display_currency)}</td>
            <td>-</td>
        </tr>"""
        
        # Senaryo satırları
        for scenario in scenario_data['calculated_scenarios']:
            scenario_total_premium_try = 0.0
            for group_result in scenario['results_per_group']:
                scenario_total_premium_try += (group_result['pd_premium_try'] + group_result['bi_premium_try'])
            
            scenario_total_premium_orig = scenario_total_premium_try / display_fx_rate
            
            # Ana senaryodan fark hesaplama
            if main_total_premium_orig > 0:
                percentage_diff = ((scenario_total_premium_orig - main_total_premium_orig) / main_total_premium_orig) * 100
                diff_text = f"{percentage_diff:+.1f}%"
                diff_color = "color: green;" if percentage_diff < 0 else "color: red;" if percentage_diff > 0 else ""
            else:
                diff_text = "-"
                diff_color = ""
            
            scenario_html += f"""
            <tr>
                <td>{scenario['name']}</td>
                <td>{scenario['koas_key']}</td>
                <td>{scenario['deduct_key']}</td>
                <td>{ui_helpers.format_number(scenario_total_premium_orig, display_currency)}</td>
                <td style="{diff_color}">{diff_text}</td>
            </tr>"""
        
        scenario_html += "</tbody></table>"

    # Ana HTML şablonunu güncelle
    html_template = f"""
    <html>
    <head>
        <meta charset="UTF-8">
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;700&display=swap');
            body {{ font-family: 'Poppins', sans-serif; color: #333; }}
            .page-break {{ page-break-after: always; }}
            .title-page {{ text-align: center; display: flex; flex-direction: column; justify-content: center; align-items: center; height: 90vh; }}
            .title-page .logo {{ width: 400px; margin-bottom: 40px; }}
            .title-page h1 {{ font-size: 36px; color: #2E86C1; margin-bottom: 20px; }}
            .title-page h2 {{ font-size: 24px; color: #5DADE2; margin-bottom: 40px; }}
            .title-page .date {{ font-size: 20px; margin-bottom: 100px; }}
            .title-page .footer-link {{ font-size: 16px; color: #64748B; text-decoration: none; }}
            h3 {{ font-size: 22px; color: #2E86C1; border-bottom: 2px solid #5DADE2; padding-bottom: 5px; margin-top: 30px; }}
            .info-table, .results-table {{ width: 100%; border-collapse: collapse; margin-top: 15px; margin-bottom: 25px; }}
            .info-table td {{ border: 1px solid #ddd; padding: 10px; font-size: 14px; }}
            .info-table td:first-child {{ font-weight: bold; background-color: #f2f2f2; width: 40%; }}
            .location-details th, .location-details td {{ padding: 10px; font-size: 14px; text-align: left; border: 1px solid #ddd;}}
            .location-details th {{ background-color: #f2f2f2; font-weight: bold;}}
            .results-table th, .results-table td {{ border: 1px solid #ddd; padding: 10px; text-align: left; font-size: 14px; }}
            .results-table th {{ background-color: #2E86C1; color: white; }}
            .results-table td:nth-child(2), .results-table td:nth-child(3), .results-table td:nth-child(4) {{ text-align: right; }}
            .results-table .total-row {{ font-weight: bold; background-color: #f2f2f2; }}
            .scenario-table th, .scenario-table td {{ font-size: 12px; }}
            .main-scenario-row {{ background-color: #e8f4f8; font-weight: bold; }}
            .scenario-table td:nth-child(4), .scenario-table td:nth-child(5) {{ text-align: right; }}
            .disclaimer {{ 
                text-align: center; 
                font-size: 12px; 
                color: #666; 
                padding: 15px; 
                background-color: #f8f9fa; 
                border-radius: 5px; 
                margin-top: 30px; 
                border: 1px solid #dee2e6;
            }}
        </style>
    </head>
    <body>
        <div class="title-page">
            <img src="data:image/png;base64,{logo_base64}" class="logo">
            <h1>DEPREM TARİFE PRİMİ</h1>
            <p class="date">{today_formatted}</p>
            <h2>Yangın, Kar Kaybı & Mühendislik Deprem Primi</h2>
            <a href="http://tariffeq.com" class="footer-link">http://tariffeq.com</a>
        </div>
        <div class="page-break"></div>
        <h2>{_tr('risk_information_title', language)}</h2>
        {risk_info_html}
        {location_details_html}
        <h2>{_tr('results_header', language)}</h2>
        {results_html}
        {icmal_html}
        {scenario_html}
        
        <div class="disclaimer">
            <strong>⚠️ Yasal Uyarı:</strong> TariffEQ hesaplamaları bilgilendirme amaçlıdır; hukuki veya ticari bağlayıcılığı yoktur.
        </div>
    </body>
    </html>
    """
    html = weasyprint.HTML(string=html_template)
    return html.write_pdf()

def create_car_pdf(data, ui_helpers, language="TR"):
    """
    CAR/EAR Poliçesi için, senaryo analizleri de içeren bir PDF raporu oluşturur.
    Yangın PDF şablonu ve mantığı kullanılarak güncellenmiştir.
    """
    today_formatted = date.today().strftime('%d.%m.%Y')
    logo_base64 = get_image_file_as_base64_data("assets/logo.png")

    # Verileri 'data' sözlüğünden al
    currency = data['currency']
    fx_rate = data.get('fx_rate', 1.0)
    display_currency = currency
    display_fx_rate = fx_rate if currency != 'TRY' else 1.0

    # ----- Tabloları HTML olarak oluşturma -----

    # 1. Riziko Bilgileri Tablosu
    risk_info_html = f"""
        <table class="info-table">
            <tr><td>{_tr("risk_group_type", lang=language)}</td><td>{data['risk_group_type'].replace('RiskGrubu', '')}</td></tr>
            <tr><td>{_tr("risk_class", lang=language)}</td><td>{data['risk_class']}</td></tr>
            <tr><td>{_tr("start_date", lang=language)}</td><td>{data['start_date'].strftime('%d.%m.%Y')}</td></tr>
            <tr><td>{_tr("end_date", lang=language)}</td><td>{data['end_date'].strftime('%d.%m.%Y')}</td></tr>
            <tr><td>{_tr("duration", lang=language)}</td><td>{data['duration_months']} {_tr("months", lang=language)}</td></tr>
            <tr><td>{_tr("currency", lang=language)}</td><td>{currency}</td></tr>
            {'<tr><td>' + _tr('fx_rate_pdf', lang=language) + ' (1 ' + currency + ')</td><td>' + str(round(fx_rate, 4)) + '</td></tr>' if currency != 'TRY' else ''}
            <tr><td>{_tr("koas", lang=language)}</td><td>{data['koas']}</td></tr>
            <tr><td>{_tr("deduct", lang=language)}</td><td>{data['deduct']}%</td></tr>
            <tr><td>{_tr("inflation_rate", lang=language)}</td><td>{data['inflation_rate']}%</td></tr>
        </table>
    """

    # 2. Ana Sonuçlar Tablosu
    total_sum_insured_orig = data['project_sum'] + data['cpm_sum'] + data['cpe_sum']
    total_premium_orig = data['total_premium_try'] / display_fx_rate
    total_rate = (total_premium_orig / (total_sum_insured_orig)) * 1000 if total_sum_insured_orig > 0 else 0.0

    results_html = f"""
    <h3>{_tr('premium_summary_header', lang=language)}</h3>
    <table class="results-table">
        <thead>
            <tr>
                <th>{_tr("table_col_coverage_type", lang=language)}</th>
                <th>{_tr("table_col_sum_insured", lang=language)} ({display_currency})</th>
                <th>{_tr("table_col_rate_per_mille", lang=language)}</th>
                <th>{_tr("table_col_premium", lang=language)} ({display_currency})</th>
            </tr>
        </thead>
        <tbody>
    """
    # Her bir teminat için oran ve primleri orijinal para biriminde hesapla
    if data['project_sum'] > 0:
        p_prem = data['car_premium_try'] / display_fx_rate
        p_rate = (p_prem / data['project_sum']) * 1000
        results_html += f"<tr><td>{_tr('coverage_car_ear', lang=language)}</td><td>{ui_helpers.format_number(data['project_sum'], display_currency)}</td><td>{ui_helpers.format_rate(p_rate)}</td><td>{ui_helpers.format_number(p_prem, display_currency)}</td></tr>"
    if data['cpm_sum'] > 0:
        cpm_prem = data['cpm_premium_try'] / display_fx_rate
        cpm_rate = (cpm_prem / data['cpm_sum']) * 1000
        results_html += f"<tr><td>{_tr('coverage_cpm', lang=language)}</td><td>{ui_helpers.format_number(data['cpm_sum'], display_currency)}</td><td>{ui_helpers.format_rate(cpm_rate)}</td><td>{ui_helpers.format_number(cpm_prem, display_currency)}</td></tr>"
    if data['cpe_sum'] > 0:
        cpe_prem = data['cpe_premium_try'] / display_fx_rate
        cpe_rate = (cpe_prem / data['cpe_sum']) * 1000
        results_html += f"<tr><td>{_tr('coverage_cpe', lang=language)}</td><td>{ui_helpers.format_number(data['cpe_sum'], display_currency)}</td><td>{ui_helpers.format_rate(cpe_rate)}</td><td>{ui_helpers.format_number(cpe_prem, display_currency)}</td></tr>"
    
    results_html += f"""
            <tr class="total-row">
                <td>{_tr("total", lang=language)}</td>
                <td>{ui_helpers.format_number(total_sum_insured_orig, display_currency)}</td>
                <td>{ui_helpers.format_rate(total_rate)}</td>
                <td>{ui_helpers.format_number(total_premium_orig, display_currency)}</td>
            </tr>
        </tbody>
    </table>
    """

    # 3. Senaryo Analizi Tablosu
    scenario_html = ""
    if 'calculated_scenarios' in data and data['calculated_scenarios']:
        scenario_html = f"<h3>{_tr('scenario_analysis_title', language)}</h3>"
        scenario_html += f"""
        <table class="results-table scenario-table">
            <thead>
                <tr>
                    <th>{_tr('scenario_name', language)}</th>
                    <th>{_tr('coinsurance_label', language)}</th>
                    <th>{_tr('deductible_label', language)} (%)</th>
                    <th>{_tr('total_premium_try', language)} ({display_currency})</th>
                    <th>{_tr('difference_from_main', language)} (%)</th>
                </tr>
            </thead>
            <tbody>
        """
        main_total_premium_orig = data['total_premium_try'] / display_fx_rate
        
        # Ana senaryo satırı
        scenario_html += f"""
        <tr class="main-scenario-row">
            <td>{_tr('main_scenario_name', language)} ({data['koas']} - {data['deduct']}%)</td>
            <td>{data['koas']}</td>
            <td>{data['deduct']}</td>
            <td>{ui_helpers.format_number(main_total_premium_orig, display_currency)}</td>
            <td>-</td>
        </tr>"""
        
        # Diğer senaryo satırları
        for scenario in data['calculated_scenarios']:
            scenario_total_premium_orig = scenario['total_premium_try'] / display_fx_rate
            
            if main_total_premium_orig > 0:
                percentage_diff = ((scenario_total_premium_orig - main_total_premium_orig) / main_total_premium_orig) * 100
                diff_text = f"{percentage_diff:+.1f}%"
                diff_color = "color: green;" if percentage_diff < 0 else "color: red;" if percentage_diff > 0 else ""
            else:
                diff_text = "-"
                diff_color = ""
            
            scenario_html += f"""
            <tr>
                <td>{scenario['name']}</td>
                <td>{scenario['koas_key']}</td>
                <td>{scenario['deduct_key']}</td>
                <td>{ui_helpers.format_number(scenario_total_premium_orig, display_currency)}</td>
                <td style="{diff_color}">{diff_text}</td>
            </tr>"""
        
        scenario_html += "</tbody></table>"

    # Ana HTML Şablonu (create_fire_pdf'ten kopyalandı)
    html_template = f"""
    <html>
    <head>
        <meta charset="UTF-8">
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;700&display=swap');
            body {{ font-family: 'Poppins', sans-serif; color: #333; }}
            .page-break {{ page-break-after: always; }}
            .title-page {{ text-align: center; display: flex; flex-direction: column; justify-content: center; align-items: center; height: 90vh; }}
            .title-page .logo {{ width: 400px; margin-bottom: 40px; }}
            .title-page h1 {{ font-size: 36px; color: #2E86C1; margin-bottom: 20px; }}
            .title-page h2 {{ font-size: 24px; color: #5DADE2; margin-bottom: 40px; }}
            .title-page .date {{ font-size: 20px; margin-bottom: 100px; }}
            .title-page .footer-link {{ font-size: 16px; color: #64748B; text-decoration: none; }}
            h3 {{ font-size: 22px; color: #2E86C1; border-bottom: 2px solid #5DADE2; padding-bottom: 5px; margin-top: 30px; }}
            .info-table, .results-table {{ width: 100%; border-collapse: collapse; margin-top: 15px; margin-bottom: 25px; }}
            .info-table td {{ border: 1px solid #ddd; padding: 10px; font-size: 14px; }}
            .info-table td:first-child {{ font-weight: bold; background-color: #f2f2f2; width: 40%; }}
            .results-table th, .results-table td {{ border: 1px solid #ddd; padding: 10px; text-align: left; font-size: 14px; }}
            .results-table th {{ background-color: #2E86C1; color: white; }}
            .results-table td:nth-child(2), .results-table td:nth-child(3), .results-table td:nth-child(4) {{ text-align: right; }}
            .results-table .total-row {{ font-weight: bold; background-color: #f2f2f2; }}
            .scenario-table th, .scenario-table td {{ font-size: 12px; }}
            .main-scenario-row {{ background-color: #e8f4f8; font-weight: bold; }}
            .scenario-table td:nth-child(4), .scenario-table td:nth-child(5) {{ text-align: right; }}
            .disclaimer {{ text-align: center; font-size: 12px; color: #666; padding: 15px; background-color: #f8f9fa; border-radius: 5px; margin-top: 30px; border: 1px solid #dee2e6; }}
        </style>
    </head>
    <body>
        <div class="title-page">
            <img src="data:image/png;base64,{logo_base64}" class="logo">
            <h1>DEPREM TARİFE PRİMİ</h1>
            <p class="date">{today_formatted}</p>
            <h2>{_tr("car_ear_report_title", language)}</h2>
            <a href="http://tariffeq.com" class="footer-link">http://tariffeq.com</a>
        </div>
        <div class="page-break"></div>
        <h2>{_tr('risk_information_title', language)}</h2>
        {risk_info_html}
        <h2>{_tr('results_header', language)}</h2>
        {results_html}
        {scenario_html}
        
        <div class="disclaimer">
            <strong>⚠️ {_tr("disclaimer_label", language)}:</strong> {_tr("disclaimer_text", language)}
        </div>
    </body>
    </html>
    """
    html = weasyprint.HTML(string=html_template)
    return html.write_pdf()

# Mevcut create_car_ear_pdf fonksiyonunu silin.
# def create_car_ear_pdf(...):
#     ...


