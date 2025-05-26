import streamlit as st
from translations import T
import pandas as pd

# Dil seçimi için session state başlatma
if 'lang' not in st.session_state:
    st.session_state.lang = "TR"  # Varsayılan dil
lang = st.session_state.lang

def tr(key: str) -> str:
    return T.get(key, {}).get(lang, key)

def format_number_display(value, currency_symbol):
    if isinstance(value, (int, float)):
        try:
            # Format as integer, then handle localization for separators
            formatted_value = f"{int(value):,}".replace(",", "X").replace(".", ",").replace("X", ".")
            return f"{formatted_value} {currency_symbol}"
        except (ValueError, TypeError):
            return f"{value} {currency_symbol}" # Fallback
    return str(value)

# --- Hesaplama Fonksiyonları (Kullanıcı Tarafından Sağlanan) ---
def deprem_hasar_orani(bolge, yapi_tipi_str, bina_yasi_str_option, kat_sayisi_str_option, faaliyet_str_option, guclendirme_str_option):
    oranlar = {
        1: {"minor": 0.07, "expected": 0.20, "severe": 0.45},
        2: {"minor": 0.06, "expected": 0.17, "severe": 0.40},
        3: {"minor": 0.05, "expected": 0.13, "severe": 0.32},
        4: {"minor": 0.04, "expected": 0.09, "severe": 0.24},
        5: {"minor": 0.03, "expected": 0.06, "severe": 0.15},
        6: {"minor": 0.03, "expected": 0.06, "severe": 0.15}, # 5-7 aynı
        7: {"minor": 0.03, "expected": 0.06, "severe": 0.15}, # 5-7 aynı
    }
    carpani = 1.0

    # Yapı Tipi (selectbox'tan gelen çevrilmiş string'e göre)
    if yapi_tipi_str == tr("structural_type_option_masonry"): # "Yığma"
        carpani *= 1.15
    elif yapi_tipi_str == tr("structural_type_option_steel"): # "Çelik"
        carpani *= 0.85
    # "Betonarme" (structural_type_option_concrete) için çarpan 1.0
    # "Diğer" (structural_type_option_other) için çarpan 1.0

    # Bina Yaşı (selectbox'tan gelen çevrilmiş string'e göre)
    if bina_yasi_str_option == tr("building_age_option_more_30"): # ">30 yıl"
        carpani *= 1.20
    elif bina_yasi_str_option == tr("building_age_option_less_10"): # "<10 yıl"
        carpani *= 0.90
    elif bina_yasi_str_option == tr("building_age_option_10_30"): # "10–30 yıl"
        carpani *= 1.05

    # Kat Sayısı (selectbox'tan gelen çevrilmiş string'e göre)
    if kat_sayisi_str_option == tr("num_floors_option_8_plus"): # "8 ve üzeri"
        carpani *= 1.10
    elif kat_sayisi_str_option == tr("num_floors_option_1_3"): # "1–3"
        carpani *= 0.95
    # "4–7" (num_floors_option_4_7) için çarpan 1.0

    # Faaliyet Tipi (selectbox'tan gelen çevrilmiş string'e göre)
    if faaliyet_str_option == tr("activity_type_option_warehouse"): # "Depolama"
        carpani *= 1.15
    elif faaliyet_str_option == tr("activity_type_option_office"): # "Ofis"
        carpani *= 0.90
    elif faaliyet_str_option == tr("activity_type_option_manufacturing"): # "Üretim"
        carpani *= 1.05
    # "Ticaret" (activity_type_option_retail) ve "Diğer" (activity_type_option_other_activity) için çarpan 1.0

    # Güçlendirme (selectbox'tan gelen çevrilmiş string'e göre)
    if guclendirme_str_option == tr("strengthening_option_yes"): # "Evet"
        carpani *= 0.85

    base = oranlar.get(bolge)
    if not base:
        return {"minor": 0, "expected": 0, "severe": 0}

    res = {k: min(round(v * carpani, 3), 0.7) for k, v in base.items()}
    return res

def hasar_senaryosu_hesapla(sigorta_bedeli, oran, muafiyet, koasurans): # koasurans: sigortacının payı (örn: 0.80)
    brut = sigorta_bedeli * oran
    muaf = brut * muafiyet
    kalan = max(brut - muaf, 0)
    sirket = kalan * koasurans # Sigorta şirketinin ödediği
    sigorta = kalan * (1 - koasurans) # Sigortalının kalan hasardan üstlendiği pay
    return int(brut), int(muaf), int(sirket), int(sigorta)

# --- Sayfa Yapılandırması ---
st.set_page_config(page_title=tr("loss_scenario_page_title"), layout="wide", initial_sidebar_state="expanded")

# Custom CSS
st.markdown("""
<style>
    /* ... (Önceki CSS kodunuz buraya eklenebilir) ... */
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
    .risk-input-container {
        background-color: #f0f2f6;
        padding: 20px;
        border-radius: 10px;
        margin-bottom: 20px;
    }
    .results-container {
        margin-top: 20px;
    }
</style>
""", unsafe_allow_html=True)

# --- Sidebar ---
with st.sidebar:
    st.image("./assets/logo.png", width=1000)
    st.page_link("home.py", label=tr("home"), icon="🏠")
    st.page_link("pages/calculate.py", label=tr("calc"))
    st.page_link("pages/earthquake_zones.py", label=tr("earthquake_zones_nav"))
    st.page_link("pages/loss_scenario.py", label=tr("loss_scenario_nav"))

    st.markdown("---")
    lang_options = ["TR", "EN"]
    current_lang_index = lang_options.index(st.session_state.lang)
    selected_lang_sidebar = st.radio(
        "Language / Dil", options=lang_options, index=current_lang_index,
        key="sidebar_language_selector_loss_scenario_detail"
    )
    if selected_lang_sidebar != st.session_state.lang:
        st.session_state.lang = selected_lang_sidebar
        st.rerun()
    st.markdown("---")
    st.markdown(f"<div class='sidebar-footer footer'>{tr('footer')}</div>", unsafe_allow_html=True)

# --- Ana İçerik ---
st.title(tr("loss_scenario_page_title")) # Başlık güncellendi

# Sektör Alternatifleri
sektor_alternatifleri = {
    "80/20-%2": {"koasurans_sirket_payi": 0.80, "muafiyet_yuzdesi": 0.02},
    "90/10-%2": {"koasurans_sirket_payi": 0.90, "muafiyet_yuzdesi": 0.02},
    "80/20-%5": {"koasurans_sirket_payi": 0.80, "muafiyet_yuzdesi": 0.05},
    "90/10-%5": {"koasurans_sirket_payi": 0.90, "muafiyet_yuzdesi": 0.05},
    "70/30-%5": {"koasurans_sirket_payi": 0.70, "muafiyet_yuzdesi": 0.05},
}

# calculate.py'den gelen verileri kontrol et
if 'loss_scenario_analysis_data' in st.session_state and st.session_state.loss_scenario_analysis_data:
    base_data = st.session_state.loss_scenario_analysis_data
    
    calculated_premiums_from_calc_page = {}
    if 'results' in base_data:
        for item in base_data['results']:
            # calculate.py'den gelen 'koas' ve 'deduct' değerlerine göre anahtar oluşturma
            # Bu anahtarın `sektor_alternatifleri` ile eşleşmesi gerekiyor.
            # `item['deduct']` formatı "2.0%" ise:
            deduct_str_for_key = item['deduct'].replace(".0%", "%").replace("%", "") # "2.0%" -> "2"
            alt_key = f"{item['koas']}-%{deduct_str_for_key}" # "80/20-%2"
            
            # Eğer `item['deduct']` formatı sadece sayı ise (örn: 2.0), o zaman:
            # alt_key = f"{item['koas']}-%{int(item['deduct'])}" # Koas: "80/20", Deduct: 2.0 -> "80/20-%2"

            calculated_premiums_from_calc_page[alt_key] = {
                "pd_premium": item.get("pd_premium_scenario_display"), # Sayısal olmalı
                "bi_premium": item.get("bi_premium_scenario_display"), # Sayısal olmalı
                "total_premium": item.get("total_premium_scenario_display") # Sayısal olmalı
            }

    sigorta_bedeli_ana = base_data.get("total_sum_insured_orig_ccy", 0) 
    currency_symbol = base_data.get("currency", "N/A")

    st.info(tr("info_base_sum_insured_display").format(
        sum_insured=format_number_display(sigorta_bedeli_ana, currency_symbol)
    ))
    st.markdown("---")

    st.subheader(tr("loss_scenario_risk_inputs_header"))
    with st.container(): 
        col1, col2 = st.columns(2)
        with col1:
            deprem_bolgesi_input = st.selectbox(
                tr("earthquake_zone_label"), options=list(range(1, 8)), index=0,
                key="deprem_bolgesi_ls"
            )
            
            bina_yasi_options = [tr("building_age_option_less_10"), tr("building_age_option_10_30"), tr("building_age_option_more_30")]
            bina_yasi_input_select = st.selectbox(
                tr("building_age_q"), options=bina_yasi_options, index=1, 
                key="bina_yasi_select_ls"
            )

            yapi_tipi_options_display = [tr("structural_type_option_concrete"), tr("structural_type_option_steel"), tr("structural_type_option_masonry"), tr("structural_type_option_other")]
            yapi_tipi_input_select = st.selectbox(
                tr("structural_type_q"), options=yapi_tipi_options_display, index=0, 
                key="yapi_tipi_select_ls"
            )
            
        with col2:
            kat_sayisi_options = [tr("num_floors_option_1_3"), tr("num_floors_option_4_7"), tr("num_floors_option_8_plus")]
            kat_sayisi_input_select = st.selectbox(
                tr("num_floors_q"), options=kat_sayisi_options, index=1, 
                key="kat_sayisi_select_ls"
            )

            faaliyet_tipi_options_display = [
                tr("activity_type_option_warehouse"), 
                tr("activity_type_option_manufacturing"), 
                tr("activity_type_option_office"), 
                tr("activity_type_option_retail"),
                tr("activity_type_option_other_activity")
            ]
            faaliyet_tipi_input_select = st.selectbox(
                tr("activity_type_q"), options=faaliyet_tipi_options_display, index=0, 
                key="faaliyet_tipi_select_ls"
            )

            guclendirme_options = [tr("strengthening_option_no"), tr("strengthening_option_yes")] 
            guclendirme_input_select = st.selectbox(
                tr("strengthening_q"), options=guclendirme_options, index=0, 
                key="guclendirme_select_ls"
            )

        # "Hesapla" butonu
        if st.button(tr("calculate_scenarios_button"), key="calculate_detailed_scenarios"):
            
            hasar_oranlari_senaryo = deprem_hasar_orani(
                deprem_bolgesi_input, 
                yapi_tipi_input_select, 
                bina_yasi_input_select,
                kat_sayisi_input_select, 
                faaliyet_tipi_input_select, 
                guclendirme_input_select # Bu artık "Evet" veya "Hayır" string'i
            )

            results_list = []
            senaryo_turleri_map = {
                "minor": tr("minor_scenario"),
                "expected": tr("expected_scenario"),
                "severe": tr("severe_scenario")
            }

            for alt_isim, alt_degerler in sektor_alternatifleri.items():
                prim_bilgileri = calculated_premiums_from_calc_page.get(alt_isim, {
                    "pd_premium": 0, "bi_premium": 0, "total_premium": 0 # Hata durumunda 0 kabul edelim
                })
                
                # Primleri sayısal değere çevirmeye çalış, değilse 0 ata
                current_total_premium = prim_bilgileri["total_premium"]
                if not isinstance(current_total_premium, (int, float)):
                    current_total_premium = 0 # veya hata yönetimi

                current_pd_premium = prim_bilgileri["pd_premium"]
                if not isinstance(current_pd_premium, (int, float)):
                    current_pd_premium = 0

                current_bi_premium = prim_bilgileri["bi_premium"]
                if not isinstance(current_bi_premium, (int, float)):
                    current_bi_premium = 0
                
                for senaryo_kodu, hasar_orani in hasar_oranlari_senaryo.items():
                    brut_hasar, muafiyet_tutari, sirket_payi, sigortali_kalan_hasar_payi = hasar_senaryosu_hesapla(
                        sigorta_bedeli_ana,
                        hasar_orani,
                        alt_degerler["muafiyet_yuzdesi"], 
                        alt_degerler["koasurans_sirket_payi"] 
                    )
                    
                    tcor_value = "N/A"
                    if isinstance(current_total_premium, (int, float)) and isinstance(sigortali_kalan_hasar_payi, (int, float)):
                        tcor_value = current_total_premium + sigortali_kalan_hasar_payi
                    else:
                        # Eğer prim veya sigortalı payı sayısal değilse, TCoR hesaplanamaz.
                        # current_total_premium ve sigortali_kalan_hasar_payi zaten 0'a ayarlanıyor
                        # eğer başta sayısal değillerse. Bu yüzden bu else bloğu nadiren çalışır.
                        tcor_value = 0 # veya "N/A"

                    results_list.append({
                        tr("alternative_col"): alt_isim,
                        tr("pd_premium_col"): current_pd_premium,
                        tr("bi_premium_col"): current_bi_premium,
                        tr("total_premium_col"): current_total_premium,
                        tr("tcor_col"): tcor_value, # Bu artık bir tutar
                        tr("scenario_type_col"): senaryo_turleri_map[senaryo_kodu],
                        tr("gross_loss_col"): brut_hasar,
                        tr("deductible_amount_col"): muafiyet_tutari,
                        tr("insurer_share_col"): sirket_payi, 
                        tr("insured_share_col"): sigortali_kalan_hasar_payi 
                    })

            if results_list:
                df_results = pd.DataFrame(results_list)
                st.session_state['detailed_scenario_results_df'] = df_results
            else:
                st.warning(tr("no_results_to_display"))

    # Sonuçları gösterme (eğer hesaplandıysa)
    if 'detailed_scenario_results_df' in st.session_state:
        st.markdown("---")
        st.subheader(tr("scenario_analysis_results_header")) 
        df_to_display = st.session_state['detailed_scenario_results_df'].copy()

        # Sütunları yeniden sırala
        desired_column_order = [
            tr("alternative_col"),
            tr("pd_premium_col"),
            tr("bi_premium_col"),
            tr("total_premium_col"),
            tr("gross_loss_col"),
            tr("deductible_amount_col"),
            tr("insurer_share_col"),
            tr("insured_share_col"),
            tr("tcor_col") # TCoR (Tutar) sona alındı, isteğe bağlı olarak yeri değişebilir
        ]
        # DataFrame'de olmayan sütunları listeden çıkar
        actual_columns = [col for col in desired_column_order if col in df_to_display.columns]
        df_to_display = df_to_display[actual_columns]


        # Sayısal sütunları formatla
        currency_cols_to_format = [
            tr("pd_premium_col"), tr("bi_premium_col"), tr("total_premium_col"),
            tr("gross_loss_col"), tr("deductible_amount_col"), 
            tr("insurer_share_col"), tr("insured_share_col"),
            tr("tcor_col") # TCoR da artık bir para birimi tutarı
        ]
        for col in currency_cols_to_format:
            if col in df_to_display.columns:
                 df_to_display[col] = df_to_display[col].apply(lambda x: format_number_display(x, currency_symbol) if isinstance(x, (int, float)) else x)
        
        # TCoR sütununu formatla (binde olarak) # BU KISIM ARTIK GEREKLİ DEĞİL, TCoR bir tutar.
        # tcor_col_name = tr("tcor_col")
        # if tcor_col_name in df_to_display.columns:
        #     df_to_display[tcor_col_name] = df_to_display[tcor_col_name].apply(
        #         lambda x: f"{x:.2f}‰" if isinstance(x, (int, float)) else x 
        #     ) # Bu formatlama kaldırıldı çünkü TCoR artık bir tutar.

        st.dataframe(df_to_display, use_container_width=True, hide_index=True)
        st.markdown(f"*{tr('all_values_in_currency').format(currency=currency_symbol)}*")
        # st.markdown(f"*{tr('insured_share_explanation')}*") # Bu satır kaldırılabilir veya yorumlanabilir
        st.markdown(f"*{tr('tcor_explanation_detailed')}*") # Bu çeviriyi TCoR tanımına göre güncelleyin


else:
    st.warning(tr("navigate_from_calculate_page_for_scenario_detail"))
    st.info(tr("info_how_to_get_base_sum_insured"))

st.markdown("---")
if st.button(tr("back_to_calculator_button")):
    # Detaylı senaryo sonuçlarını temizle ki bir sonraki gelişte eski data görünmesin
    if 'detailed_scenario_results_df' in st.session_state:
        del st.session_state['detailed_scenario_results_df']
    st.switch_page("pages/calculate.py")

