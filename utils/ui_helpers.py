import streamlit as st
import requests
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta
from translations import T # Ana dizindeki translations.py'den T'yi içe aktar
import pandas as pd # DataFrame için

# Bu modül içinde kullanılacak yerel bir tr fonksiyonu
def _tr(key: str) -> str:
    lang_code = st.session_state.get('lang', 'TR') # Varsayılan dil TR
    return T.get(key, {}).get(lang_code, key)

# Teminat türleri için yapılandırma
# Bu yapılandırma, calculate.py'deki premium_results_by_group ve groups_determined_data
# anahtarlarıyla ve çeviri anahtarlarıyla uyumlu olmalıdır.
coverage_config = [
    {
        "name_tr_key": "coverage_pd_combined", # Çeviri anahtarı (örn: "Maddi Hasarlar (Bina, Mef., Dek., Emtea, Kasa, Mak.)")
        "sum_fields": ["building", "fixture", "decoration", "commodity", "safe", "machinery"], # DEĞIŞTI: commodity_raw_for_display -> commodity
        "premium_field_in_results": "pd_premium_try" # premium_results_by_group'daki prim alanı
    },
    {
        "name_tr_key": "coverage_bi",
        "sum_fields": ["bi"],
        "premium_field_in_results": "bi_premium_try"
    },
    {
        "name_tr_key": "coverage_ec",
        "sum_fields": ["ec_fixed", "ec_mobile"],
        "premium_field_in_results": "ec_premium_try"
    },
    {
        "name_tr_key": "coverage_mk",
        "sum_fields": ["mk_fixed", "mk_mobile"],
        "premium_field_in_results": "mk_premium_try"
    }
]

# ------------------------------------------------------------
# TCMB FX MODULE & FORMATTING
# ------------------------------------------------------------
@st.cache_data(ttl=3600) # TCMB kurlarını 1 saat cache'le
def get_tcmb_rate(ccy: str):
    """Belirtilen para birimi için TCMB'den günlük kur alır."""
    try:
        # Bugünün kurlarını dene
        r = requests.get("https://www.tcmb.gov.tr/kurlar/today.xml", timeout=4) # Timeout eklendi
        r.raise_for_status() # HTTP hatalarını yakala
        root = ET.fromstring(r.content)
        for cur in root.findall("Currency"):
            if cur.attrib.get("CurrencyCode") == ccy:
                # BanknoteSelling yoksa ForexSelling kullan
                txt = cur.findtext("BanknoteSelling") or cur.findtext("ForexSelling")
                return float(txt.replace(",", ".")), datetime.strptime(root.attrib["Date"], "%d.%m.%Y").strftime("%Y-%m-%d")
    except Exception: # requests.exceptions.RequestException veya ET.ParseError gibi
        pass # Hata olursa bir önceki güne geç
    
    # Bugün kur yoksa veya hata oluştuysa, son 7 günü dene
    today = datetime.today()
    for i in range(1, 8): # Son 7 gün
        d = today - timedelta(days=i)
        url = f"https://www.tcmb.gov.tr/kurlar/{d:%Y%m}/{d:%d%m%Y}.xml"
        try:
            r = requests.get(url, timeout=4)
            if not r.ok: # Sadece başarılı istekleri işle
                continue
            root = ET.fromstring(r.content)
            for cur in root.findall("Currency"):
                if cur.attrib.get("CurrencyCode") == ccy:
                    txt = cur.findtext("BanknoteSelling") or cur.findtext("ForexSelling")
                    return float(txt.replace(",", ".")), d.strftime("%Y-%m-%d")
        except Exception: # requests.exceptions.RequestException veya ET.ParseError
            continue # Hata olursa bir sonraki güne geç
    return None, None # Kur bulunamazsa

def fx_input(ccy: str, key_prefix: str) -> tuple[float, str]:
    """Para birimi TRY değilse kur girişi ve TCMB'den otomatik kur alma alanı oluşturur."""
    if ccy == "TRY":
        return 1.0, "" # TRY için kur 1.0 ve bilgi mesajı boş

    # Session state anahtarları
    r_key = f"{key_prefix}_{ccy}_rate"       # Kullanılan kur
    s_key = f"{key_prefix}_{ccy}_src"       # Kur kaynağı (TCMB/MANUEL)
    tcmb_rate_key = f"{key_prefix}_{ccy}_tcmb_rate" # TCMB'den alınan kur
    tcmb_date_key = f"{key_prefix}_{ccy}_tcmb_date" # TCMB kur tarihi

    # Eğer TCMB kuru session state'de yoksa, çek ve kaydet
    if tcmb_rate_key not in st.session_state:
        tcmb_rate, tcmb_date = get_tcmb_rate(ccy)
        if tcmb_rate is None: # Kur çekilemediyse
            st.session_state.update({
                tcmb_rate_key: 0.0, # Varsayılan olarak 0 ata
                tcmb_date_key: "-",
                r_key: 0.0,         # Kullanılan kur da 0 olsun
                s_key: "MANUEL"     # Kaynak manuel olsun
            })
        else:
            st.session_state.update({
                tcmb_rate_key: tcmb_rate,
                tcmb_date_key: tcmb_date,
                r_key: tcmb_rate,   # Başlangıçta kullanılan kur TCMB kuru olsun
                s_key: "TCMB"       # Kaynak TCMB
            })
    
    # Manuel kur girişi için number_input
    # Varsayılan değer session state'deki r_key'den gelir
    default_rate = float(st.session_state[r_key])
    new_rate = st.number_input(
        _tr("manual_fx"), 
        value=default_rate, 
        step=0.0001, 
        format="%.4f", 
        key=f"{key_prefix}_{ccy}_manual" # Her kur girişi için benzersiz anahtar
    )
    
    # Eğer girilen kur, TCMB'den çekilen kurdan farklıysa, kaynağı MANUEL yap
    if new_rate != st.session_state.get(tcmb_rate_key, 0.0): # TCMB kuru yoksa 0 ile karşılaştır
        st.session_state[s_key] = "MANUEL"
    else: # Aynıysa TCMB
        st.session_state[s_key] = "TCMB"
    
    # Kullanılan kuru güncelle
    st.session_state[r_key] = new_rate
    
    # Bilgi mesajı
    info_message = (
        f"💱 TCMB Kuru: 1 {ccy} = {st.session_state[tcmb_rate_key]:,.4f} TL (TCMB, {st.session_state[tcmb_date_key]}) | "
        f"Kullanılan Kur: 1 {ccy} = {st.session_state[r_key]:,.4f} TL ({st.session_state[s_key]})"
    )
    st.info(info_message) # Bu mesajı her zaman göster
    return st.session_state[r_key], info_message

def format_number(value, currency_code):
    # Mevcut format_number fonksiyonunuz
    if value is None:
        return "-"
    try:
        # Türkçe formatı için: 1.234.567,89
        # İngilizce formatı için: 1,234,567.89
        # Şimdilik basit bir replace ile yapalım, daha gelişmiş locale kütüphaneleri kullanılabilir.
        formatted_value = f"{value:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        return f"{formatted_value} {currency_code}"
    except (ValueError, TypeError):
        return f"{value} {currency_code}"

def format_rate(rate_value):
    """Oran değerini 4 ondalık basamakla ve Türkçe yerel ayarına uygun formatlar."""
    if rate_value is None:
        return "-"
    try:
        # Örnek: 3,0000
        return f"{rate_value:,.4f}".replace(",", "X").replace(".", ",").replace("X", ".")
    except (ValueError, TypeError):
        return str(rate_value)

# ------------------------------------------------------------
# UI DISPLAY FUNCTIONS
# ------------------------------------------------------------
def display_current_total_sums(locations_data_list, currency_code):
    """
    Kullanıcının girdiği mevcut toplam PD ve BI bedellerini gösterir.
    Emtea abonman ise, PD toplamına %40'ı ile katılır.
    """
    if not locations_data_list:
        return

    total_pd_sum_for_display = 0.0
    total_bi_sum_for_display = 0.0

    for loc_data in locations_data_list:
        current_commodity_for_pd_display = loc_data.get("commodity", 0.0)
        if loc_data.get("commodity_is_subscription", False):
            current_commodity_for_pd_display *= 0.40
        
        total_pd_sum_for_display += (
            loc_data.get("building", 0.0) +
            loc_data.get("fixture", 0.0) +
            loc_data.get("decoration", 0.0) +
            current_commodity_for_pd_display + # Ayarlanmış emtea bedeli
            loc_data.get("safe", 0.0) +
            loc_data.get("machinery", 0.0) 
            # (loc_data.get("ec_fixed", 0.0) if loc_data.get("include_ec_mk_cover", False) else 0.0) +
            # (loc_data.get("ec_mobile", 0.0) if loc_data.get("include_ec_mk_cover", False) else 0.0) +
            # (loc_data.get("mk_fixed", 0.0) if loc_data.get("include_ec_mk_cover", False) else 0.0) +
            # (loc_data.get("mk_mobile", 0.0) if loc_data.get("include_ec_mk_cover", False) else 0.0)
        )
        total_bi_sum_for_display += loc_data.get("bi", 0.0)

    st.markdown(f"##### {_tr('current_entered_sums_header')}") # Yeni çeviri anahtarı
    info_box_content = f"ℹ️ <b>{_tr('total_entered_pd_sum_effective')}:</b> {format_number(total_pd_sum_for_display, currency_code)}" # Yeni çeviri anahtarı
    if total_bi_sum_for_display > 0:
        info_box_content += f"<br>ℹ️ <b>{_tr('total_entered_bi_sum')}:</b> {format_number(total_bi_sum_for_display, currency_code)}"
    
    st.markdown(f'<div class="info-box">{info_box_content}</div>', unsafe_allow_html=True)
    st.markdown("---")

def display_fire_results(
    num_locations_val,
    groups_determined_data,
    premium_results_by_group,
    total_premium_all_groups_try_val,
    display_currency_for_output_val,
    display_fx_rate_for_output_val,
    limited_policy_multiplier_val
    ):
    lang = st.session_state.lang # Bu satır kalabilir veya _tr zaten session state'i kullandığı için kaldırılabilir.
    
    st.markdown(f"#### {_tr('results_table_header')}")

    # Tek lokasyon ve çoklu lokasyon için ortak veri hazırlama mantığı
    all_groups_display_data_for_table_val = []
    if num_locations_val == 1:
        group_key = list(groups_determined_data.keys())[0]
        data = groups_determined_data[group_key]
        premiums = premium_results_by_group[group_key]
        
        for config in coverage_config:
            sum_insured_orig = sum(data.get(field, 0.0) for field in config["sum_fields"])
            premium_try = premiums.get(config["premium_field_in_results"], 0.0)
            
            if sum_insured_orig > 0 or premium_try > 0:
                sum_insured_display = sum_insured_orig
                premium_display = premium_try / display_fx_rate_for_output_val if display_fx_rate_for_output_val != 0 else 0.0
                
                rate_permille = (premium_display / sum_insured_display) * 1000 if sum_insured_display > 0 else 0.0

                all_groups_display_data_for_table_val.append({
                    _tr("table_col_coverage_type"): _tr(config["name_tr_key"]),
                    _tr("table_col_sum_insured"): format_number(sum_insured_display, display_currency_for_output_val),
                    _tr("table_col_rate_per_mille"): format_rate(rate_permille),
                    _tr("table_col_premium"): format_number(premium_display, display_currency_for_output_val),
                    "sum_insured_numeric": sum_insured_display,
                    "premium_numeric": premium_display
                })


    if num_locations_val == 1 and all_groups_display_data_for_table_val:
        # Tek lokasyon, tek grup için tablo
        df_single = pd.DataFrame(all_groups_display_data_for_table_val)

        # Görüntülenecek sütunlar ve sıraları
        display_columns_keys = [
            _tr("table_col_coverage_type"),
            _tr("table_col_sum_insured"),
            _tr("table_col_rate_per_mille"), # YENİ SÜTUN
            _tr("table_col_premium")
        ]
        
        # Sadece görüntüleme için kullanılacak DataFrame
        df_display_single = df_single[display_columns_keys].copy()

        # Toplamları hesapla (sayısal değerler üzerinden)
        total_sum_insured_single_numeric = df_single["sum_insured_numeric"].sum()
        total_premium_single_numeric = df_single["premium_numeric"].sum()
        
        total_effective_rate_numeric = 0.0
        if total_sum_insured_single_numeric > 0:
            total_effective_rate_numeric = (total_premium_single_numeric / total_sum_insured_single_numeric) * 1000

        # Toplam satırını df_display_single'a ekle
        total_row_data = {
            _tr("table_col_coverage_type"): _tr("total_overall"),
            _tr("table_col_sum_insured"): format_number(total_sum_insured_single_numeric, display_currency_for_output_val),
            _tr("table_col_rate_per_mille"): format_rate(total_effective_rate_numeric), # YENİ
            _tr("table_col_premium"): format_number(total_premium_single_numeric, display_currency_for_output_val)
        }
        
        # df_display_single = df_display_single.append(total_row_data, ignore_index=True) # append kaldırıldı
        df_display_single.loc[len(df_display_single)] = total_row_data


        st.dataframe(
            df_display_single,
            hide_index=True,
            use_container_width=True,
            column_config={
                _tr("table_col_sum_insured"): st.column_config.TextColumn(
                    label=_tr("table_col_sum_insured"), 
                    help=_tr("table_col_sum_insured_help")
                ),
                _tr("table_col_rate_per_mille"): st.column_config.TextColumn( # YENİ
                    label=_tr("table_col_rate_per_mille"), 
                    help=_tr("table_col_rate_per_mille_help") # Yeni çeviri anahtarı eklenecek
                ),
                _tr("table_col_premium"): st.column_config.TextColumn(
                    label=_tr("table_col_premium"), 
                    help=_tr("table_col_premium_help")
                ),
            }
        )
        # ... (kalan tek lokasyon sonuç gösterimi) ...
        # PD için uygulanan oranı göster (bu değişmedi)
        # if applied_rate_val is not None:
        #     st.markdown(f"**{_tr('applied_pd_rate_label')}:** {format_rate(applied_rate_val)} %o")

    elif num_locations_val > 1 and premium_results_by_group:
        group_keys = sorted(list(groups_determined_data.keys()))
        
        table_rows_data = []

        # Teminat satırları
        for config in coverage_config:
            row_data = {_tr("table_col_coverage_type"): _tr(config["name_tr_key"])}
            for gk in group_keys:
                group_sums = groups_determined_data.get(gk, {})
                group_premiums_try = premium_results_by_group.get(gk, {})

                sum_insured_orig_ccy = sum(group_sums.get(field, 0.0) for field in config["sum_fields"])
                premium_try = group_premiums_try.get(config["premium_field_in_results"], 0.0)

                sum_insured_display = sum_insured_orig_ccy 
                premium_display = premium_try / display_fx_rate_for_output_val if display_fx_rate_for_output_val != 0 else 0.0
                
                sum_insured_try_for_rate_calc = sum_insured_orig_ccy * display_fx_rate_for_output_val
                
                effective_rate_permille = 0.0
                if sum_insured_try_for_rate_calc > 0:
                    effective_rate_permille = (premium_try / sum_insured_try_for_rate_calc) * 1000
                
                row_data[f"{_tr('table_col_sum_insured')} ({gk})"] = format_number(sum_insured_display, display_currency_for_output_val)
                # format_rate fonksiyonunu burada da kullanalım
                row_data[f"{_tr('table_col_rate_permille')} ({gk})"] = format_rate(effective_rate_permille) 
                row_data[f"{_tr('table_col_premium')} ({gk})"] = format_number(premium_display, display_currency_for_output_val)
            table_rows_data.append(row_data)

        # Toplam satırı
        total_row_data = {_tr("table_col_coverage_type"): _tr('total_overall')} # Markdown bold kaldırıldı
        for gk in group_keys:
            group_sums = groups_determined_data.get(gk, {})
            group_premiums_try = premium_results_by_group.get(gk, {})

            current_group_total_sum_orig_ccy = 0.0
            for cfg in coverage_config:
                current_group_total_sum_orig_ccy += sum(group_sums.get(field, 0.0) for field in cfg["sum_fields"])
            
            current_group_total_premium_try = group_premiums_try.get("total_premium_try", 0.0)

            total_sum_insured_display = current_group_total_sum_orig_ccy
            total_premium_display = current_group_total_premium_try / display_fx_rate_for_output_val if display_fx_rate_for_output_val != 0 else 0.0

            total_sum_insured_try_for_rate_calc = current_group_total_sum_orig_ccy * display_fx_rate_for_output_val
            
            total_effective_rate_permille = 0.0
            if total_sum_insured_try_for_rate_calc > 0:
                total_effective_rate_permille = (current_group_total_premium_try / total_sum_insured_try_for_rate_calc) * 1000
            
            # Markdown bold kaldırıldı
            total_row_data[f"{_tr('table_col_sum_insured')} ({gk})"] = format_number(total_sum_insured_display, display_currency_for_output_val)
            total_row_data[f"{_tr('table_col_rate_permille')} ({gk})"] = format_rate(total_effective_rate_permille)
            total_row_data[f"{_tr('table_col_premium')} ({gk})"] = format_number(total_premium_display, display_currency_for_output_val)
        table_rows_data.append(total_row_data)
        
        # DataFrame Sütun Başlıkları
        df_columns = [_tr("table_col_coverage_type")]
        for gk_col_header in group_keys:
            df_columns.extend([
                f"{_tr('table_col_sum_insured')} ({gk_col_header})",
                f"{_tr('table_col_rate_permille')} ({gk_col_header})",
                f"{_tr('table_col_premium')} ({gk_col_header})"
            ])
        
        results_df = pd.DataFrame(table_rows_data, columns=df_columns)

        # "Toplam" satırını belirleyen sütun adı ve değeri
        # Bu değerlerin DataFrame'deki gerçek değerlerle eşleştiğinden emin olun.
        TARGET_COLUMN_NAME_FOR_TOTAL = _tr("table_col_coverage_type")
        TARGET_TEXT_FOR_TOTAL_ROW = _tr('total_overall')

        # Debug için değerleri yazdırabilirsiniz:
        # st.write(f"Debug: TARGET_COLUMN_NAME_FOR_TOTAL = '{TARGET_COLUMN_NAME_FOR_TOTAL}'")
        # st.write(f"Debug: TARGET_TEXT_FOR_TOTAL_ROW = '{TARGET_TEXT_FOR_TOTAL_ROW}'")
        # st.write("Debug: DataFrame'in ilk birkaç satırı:")
        # st.write(results_df.head())


        def style_last_row(row):
            if row.name == results_df.index[-1]:  # Son satırın indeksini kontrol et
                return ['font-weight: bold'] * len(row)
            return [''] * len(row)
        
        st.dataframe(
            results_df.style.apply(
                style_last_row, 
                axis=1
            ).set_table_styles([
                {'selector': 'th', 'props': [('font-weight', 'bold')]}
            ]),
            hide_index=True,
            use_container_width=True
        )

        # --- YENİ İCMAL TABLOSU BAŞLANGICI ---
        st.markdown(f"### {_tr('summary_results_table_title')}")
        
        summary_table_rows = []
        grand_total_sum_insured_summary_numeric = 0.0
        grand_total_premium_summary_numeric = 0.0

        for config in coverage_config: # Daha önce tanımlanmış coverage_config'i kullanıyoruz
            current_coverage_total_sum_orig_ccy = 0.0
            current_coverage_total_premium_try = 0.0

            for gk in group_keys:
                group_data = groups_determined_data.get(gk, {})
                group_premiums = premium_results_by_group.get(gk, {})
                
                # Bu teminat türü için bu gruptaki bedeli topla
                # sum_fields, data["commodity_raw_for_display"] gibi alanları içerir
                sum_insured_for_coverage_in_group = sum(group_data.get(field, 0.0) for field in config["sum_fields"])
                current_coverage_total_sum_orig_ccy += sum_insured_for_coverage_in_group
                
                # Bu teminat türü için bu gruptaki primi (TRY) topla
                premium_for_coverage_in_group_try = group_premiums.get(config["premium_field_in_results"], 0.0)
                current_coverage_total_premium_try += premium_for_coverage_in_group_try

            # Bedel ve Primi gösterim para birimine çevir
            # current_coverage_total_sum_orig_ccy zaten orijinal/gösterim para biriminde
            sum_insured_display_val = current_coverage_total_sum_orig_ccy
            
            # display_fx_rate_for_output_val, orijinal para biriminin TRY'ye olan kurudur.
            # Primi (TRY) orijinal/gösterim para birimine çevirmek için böleriz.
            premium_display_val = current_coverage_total_premium_try / display_fx_rate_for_output_val if display_fx_rate_for_output_val != 0 else 0.0
            
            effective_rate_permille = 0.0
            if sum_insured_display_val > 0:
                effective_rate_permille = (premium_display_val / sum_insured_display_val) * 1000
            
            summary_table_rows.append({
                _tr("table_col_coverage_type"): _tr(config["name_tr_key"]),
                "sum_insured_numeric": sum_insured_display_val,
                "rate_per_mille_numeric": effective_rate_permille,
                "premium_numeric": premium_display_val,
                _tr("table_col_sum_insured"): format_number(sum_insured_display_val, display_currency_for_output_val),
                _tr("table_col_rate_per_mille"): format_rate(effective_rate_permille),
                _tr("table_col_premium"): format_number(premium_display_val, display_currency_for_output_val)
            })
            
            grand_total_sum_insured_summary_numeric += sum_insured_display_val
            grand_total_premium_summary_numeric += premium_display_val

        # İcmal tablosu için DataFrame oluştur
        summary_df = pd.DataFrame(summary_table_rows)

        if not summary_df.empty:
            # İcmal tablosu için genel toplam satırı
            overall_summary_effective_rate = 0.0
            if grand_total_sum_insured_summary_numeric > 0:
                overall_summary_effective_rate = (grand_total_premium_summary_numeric / grand_total_sum_insured_summary_numeric) * 1000
            
            summary_total_row = pd.DataFrame([{
                _tr("table_col_coverage_type"): _tr("total_overall"), # Tek lokasyon tablosundaki gibi "Toplam"
                "sum_insured_numeric": grand_total_sum_insured_summary_numeric,
                "rate_per_mille_numeric": overall_summary_effective_rate,
                "premium_numeric": grand_total_premium_summary_numeric,
                _tr("table_col_sum_insured"): format_number(grand_total_sum_insured_summary_numeric, display_currency_for_output_val),
                _tr("table_col_rate_per_mille"): format_rate(overall_summary_effective_rate),
                _tr("table_col_premium"): format_number(grand_total_premium_summary_numeric, display_currency_for_output_val)
            }])
            summary_df_display = pd.concat([summary_df, summary_total_row], ignore_index=True)

            # İcmal tablosunu göster (tek lokasyon tablosuyla aynı stil fonksiyonunu kullanabiliriz)
            # Sütun isimleri tek lokasyon tablosuyla aynı olmalı
            display_columns_summary_keys = [
                _tr("table_col_coverage_type"),
                _tr("table_col_sum_insured"),
                _tr("table_col_rate_per_mille"),
                _tr("table_col_premium")
            ]
            
            # Sadece gösterilecek sütunları ve doğru sırayı al
            summary_df_for_styling = summary_df_display[display_columns_summary_keys]

            st.dataframe(
                summary_df_for_styling.style.apply(
                    style_last_row, # Bu fonksiyon 'total_row_label' ile eşleşen satırı bold yapar
                    axis=1
                ).set_table_styles([
                    {'selector': 'th', 'props': [('font-weight', 'bold')]}
                ]).format(precision=4, thousands=".", decimal=","), # Sayı formatlaması
                hide_index=True,
                use_container_width=True,
                column_config={ # Tek lokasyon tablosundaki gibi column_config
                    _tr("table_col_sum_insured"): st.column_config.TextColumn(
                        label=_tr("table_col_sum_insured"), 
                        help=_tr("table_col_sum_insured_help")
                    ),
                    _tr("table_col_rate_per_mille"): st.column_config.TextColumn(
                        label=_tr("table_col_rate_per_mille"), 
                        help=_tr("table_col_rate_per_mille_help")
                    ),
                    _tr("table_col_premium"): st.column_config.TextColumn(
                        label=_tr("table_col_premium"), 
                        help=_tr("table_col_premium_help")
                    ),
                }
            )
        # --- YENİ İCMAL TABLOSU SONU ---

        # Genel Toplam Prim (tüm gruplar için) - Bu zaten vardı, yerinde kalıyor
        if total_premium_all_groups_try_val > 0:
            total_premium_all_groups_display = total_premium_all_groups_try_val / display_fx_rate_for_output_val if display_fx_rate_for_output_val != 0 else 0.0
            st.markdown(f'<div class="info-box">💰 <b>{_tr("total_premium")}:</b> {format_number(total_premium_all_groups_display, display_currency_for_output_val)}</div>', unsafe_allow_html=True)
            
    else:
        st.info(_tr("no_premium_calculated_msg")) # Hiçbir prim hesaplanmadıysa

def display_car_ear_results(
    car_premium_try, 
    cpm_premium_try, 
    cpe_premium_try, 
    total_premium_try, 
    applied_car_rate, # Bu genel oran, toplam üzerinden hesaplanmış olmalı
    project_sum_insured_orig_ccy, 
    cpm_sum_insured_orig_ccy, 
    cpe_sum_insured_orig_ccy,
    currency_code, # örn: "TRY", "USD"
    fx_rate_to_try # Orijinal para biriminden TRY'ye çevrim kuru
    ):
    """CAR/EAR modülü hesaplama sonuçlarını tablo formatında gösterir."""

    st.markdown(f"### {_tr('results_table_header')}") # Yeni çeviri anahtarı: "results_table_header": {"TR": "Sonuç Tablosu", "EN": "Results Table"}

    # Çıkış para birimi ve kuru belirle
    # Eğer giriş para birimi TRY ise, çıkış kuru 1.0 olur.
    # Diğer para birimleri için, TRY'den o para birimine çevirmek üzere 1/fx_rate_to_try kullanılır.
    # Ancak, bedeller zaten orijinal para biriminde olduğu için, primleri TRY'den orijinal para birimine çevireceğiz.
    
    display_currency = currency_code
    # TRY'den orijinal para birimine çevirmek için kullanılacak kur
    # Eğer orijinal para birimi TRY ise, fx_rate_to_output = 1.0
    # Eğer orijinal para birimi USD ise ve fx_rate_to_try (USD->TRY) = 30 ise, fx_rate_to_output (TRY->USD) = 1/30
    fx_rate_to_output_ccy = 1.0
    if currency_code != "TRY" and fx_rate_to_try != 0:
        fx_rate_to_output_ccy = 1.0 / fx_rate_to_try
    elif currency_code == "TRY":
        fx_rate_to_output_ccy = 1.0 # Zaten TRY, çevrime gerek yok
    else: # fx_rate_to_try == 0 ise (hata durumu)
        fx_rate_to_output_ccy = 0 # Hata durumunda primleri 0 göster


    table_data = []

    # CAR/EAR Satırı
    car_sum_display = project_sum_insured_orig_ccy
    car_premium_display = car_premium_try * fx_rate_to_output_ccy
    car_rate_permille = 0.0
    if project_sum_insured_orig_ccy > 0 and fx_rate_to_try > 0: # Oran her zaman TRY bedel üzerinden hesaplanır
        car_rate_permille = (car_premium_try / (project_sum_insured_orig_ccy * fx_rate_to_try)) * 1000

    table_data.append({
        _tr("table_col_coverage_type"): _tr("coverage_car_ear"),
        _tr("table_col_sum_insured"): format_number(car_sum_display, display_currency),
        _tr("table_col_rate_permille"): f"{car_rate_permille:.4f}",
        _tr("table_col_premium"): format_number(car_premium_display, display_currency),
        "sum_insured_numeric": car_sum_display, # Toplam için
        "premium_numeric": car_premium_display # Toplam için
    })

    # CPM Satırı
    if cpm_sum_insured_orig_ccy > 0 or cpm_premium_try > 0:
        cpm_sum_display = cpm_sum_insured_orig_ccy
        cpm_premium_display = cpm_premium_try * fx_rate_to_output_ccy
        cpm_rate_permille = 0.0
        if cpm_sum_insured_orig_ccy > 0 and fx_rate_to_try > 0:
            cpm_rate_permille = (cpm_premium_try / (cpm_sum_insured_orig_ccy * fx_rate_to_try)) * 1000
        
        table_data.append({
            _tr("table_col_coverage_type"): _tr("coverage_cpm"),
            _tr("table_col_sum_insured"): format_number(cpm_sum_display, display_currency),
            _tr("table_col_rate_permille"): f"{cpm_rate_permille:.4f}",
            _tr("table_col_premium"): format_number(cpm_premium_display, display_currency),
            "sum_insured_numeric": cpm_sum_display,
            "premium_numeric": cpm_premium_display
        })

    # CPE Satırı
    if cpe_sum_insured_orig_ccy > 0 or cpe_premium_try > 0:
        cpe_sum_display = cpe_sum_insured_orig_ccy
        cpe_premium_display = cpe_premium_try * fx_rate_to_output_ccy
        cpe_rate_permille = 0.0
        if cpe_sum_insured_orig_ccy > 0 and fx_rate_to_try > 0:
            cpe_rate_permille = (cpe_premium_try / (cpe_sum_insured_orig_ccy * fx_rate_to_try)) * 1000

        table_data.append({
            _tr("table_col_coverage_type"): _tr("coverage_cpe"),
            _tr("table_col_sum_insured"): format_number(cpe_sum_display, display_currency),
            _tr("table_col_rate_permille"): f"{cpe_rate_permille:.4f}",
            _tr("table_col_premium"): format_number(cpe_premium_display, display_currency),
            "sum_insured_numeric": cpe_sum_display,
            "premium_numeric": cpe_premium_display
        })
    
    # Toplam Satırı
    total_sum_insured_display = sum(item.get("sum_insured_numeric", 0.0) for item in table_data)
    total_premium_display = sum(item.get("premium_numeric", 0.0) for item in table_data)
    
    # Toplam oran, pc.calculate_car_ear_premium'dan gelen applied_car_rate kullanılabilir
    # Bu oran zaten toplam TRY prim / toplam TRY bedel üzerinden hesaplanmış olmalı.
    total_rate_permille_overall = applied_car_rate # Bu, pc modülünden gelen genel oran

    table_data.append({
        _tr("table_col_coverage_type"): f"{_tr('total_overall')}",
        _tr("table_col_sum_insured"): f"{format_number(total_sum_insured_display, display_currency)}",
        _tr("table_col_rate_permille"): f"{total_rate_permille_overall:.4f}",
        _tr("table_col_premium"): f"{format_number(total_premium_display, display_currency)}"
    })

    df_display_columns = [
        _tr("table_col_coverage_type"), 
        _tr("table_col_sum_insured"), 
        _tr("table_col_rate_permille"), 
        _tr("table_col_premium")
    ]
    df_results_table = pd.DataFrame(table_data)[df_display_columns]
    
    st.dataframe(
        df_results_table.style.set_properties(**{'text-align': 'left'})
                           .set_table_styles([dict(selector='th', props=[('text-align', 'left')])]), 
        use_container_width=True, 
        hide_index=True
    )

    # İsteğe bağlı: Genel toplam primi ayrıca vurgulamak için
    # total_premium_overall_display = total_premium_try * fx_rate_to_output_ccy
    # st.markdown(f'<div class="info-box">💰 <b>{tr("total_premium")}:</b> {format_number(total_premium_overall_display, display_currency)}</div>', unsafe_allow_html=True)
    # Yukarıdaki satır zaten tablonun toplam satırında var, bu yüzden tekrar göstermek gerekmeyebilir