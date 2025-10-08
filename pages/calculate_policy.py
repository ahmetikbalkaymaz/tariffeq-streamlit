import streamlit as st
import pandas as pd
import math
from pages.sidebar import sidebar


def calculate_bedel_primi_permille_rate(toplam_bedel_try):
    """Verilen Excel formülüne göre Bedel Primi ORANINI (BİNDE FİYATINI) hesaplar."""
    if toplam_bedel_try <= 0:
        return 0
    try:
        if toplam_bedel_try <= 1_000_000_000:
            rate = 0.0005 * math.log(1 + toplam_bedel_try) / math.log(1 + 1_000_000_000)
        elif toplam_bedel_try <= 3_000_000_000:
            rate = 0.005 * math.log(1 + (toplam_bedel_try - 1_000_000_000)) / math.log(1 + 2_000_000_000)
        elif toplam_bedel_try <= 5_000_000_000:
            rate = 0.05 * math.log(1 + (toplam_bedel_try - 3_000_000_000)) / math.log(1 + 2_000_000_000)
        elif toplam_bedel_try <= 10_000_000_000:
            rate = 0.1 * math.log(1 + (toplam_bedel_try - 5_000_000_000)) / math.log(1 + 5_000_000_000)
        else:
            rate = 0.5 * math.log(1 + (toplam_bedel_try - 10_000_000_000)) / math.log(1 + 10_000_000_000)
        return rate # Bu değer binde cinsinden orandır (permille)
    except ValueError:
        return 0

RISK_CLASSIFICATION = {
    "Ticari Faaliyetler (Alım-Satım)": {"Düşük Riskli Ticari": ["Ofis ve bürolar", "Giyim mağazası", "Kitapçı", "Emlakçı"],"Orta Riskli Ticari": ["Süpermarket / Market", "Elektronik eşya mağazası", "Yedek parçacı"],"Yüksek Riskli Ticari": ["Mobilya mağazası (Showroom)", "Yapı market", "AVM (Alışveriş Merkezi)", "Boya satıcısı"]},
    "Sınai Faaliyetler (Üretim/İmalat)": {"Düşük Riskli Sınai (Hafif Sanayi)": ["Tehlikesiz parça montajı", "Gıda paketleme (pişirmesiz)", "Dikiş atölyesi"],"Orta Riskli Sınai": ["Metal işleme atölyesi", "Matbaacılık", "Gıda üretimi (pişirmeli)"],"Yüksek Riskli Sınai (Ağır/Tehlikeli)": ["Ahşap ve mobilya imalatı", "Kimya sanayi (Boya, plastik, kauçuk vb.)", "Tekstil imalatı (Dokuma, iplik)"]},
    "Hizmet ve Diğer Faaliyetler": {"Düşük Riskli Hizmet": ["Okul / Eğitim Kurumu", "İbadethane", "Dernek / STK"],"Orta / Yüksek Riskli Hizmet": ["Otel / Konaklama Tesisi", "Restoran / Lokanta", "Hastane / Sağlık Kuruluşu", "Tamirhane"]},
    "Depolama Faaliyetleri (Lojistik)": {"Düşük Riskli Depolama": ["Yanıcı olmayan ürün depolama (Metal, cam, taş vb.)"],"Yüksek Riskli Depolama": ["Yanıcı/Parlayıcı madde depolama (Kimyasal, pamuk, kağıt vb.)"]},
    "Enerji Santralleri": {"Düşük Riskli Enerji": ["Güneş Enerji Santrali (GES)", "Hidroelektrik Santrali (HES - Nehir Tipi)"],"Orta Riskli Enerji": ["Rüzgar Enerji Santrali (RES)", "Jeotermal Enerji Santrali (JES)", "Hidroelektrik Santrali (HES - Barajlı)"],"Yüksek Riskli Enerji": ["Doğalgaz Çevrim Santrali", "Kömürlü Termik Santral", "Biyokütle Enerji Santrali"]}
}

def render_police_hesaplama_page():
    sidebar()
    st.title("🏢 Poliçe Hesaplama ve Detayları")
    st.header("Aşama 2: Poliçe Detayları ve Brüt Prim")
    if st.button("⬅️ Geri Dön ve Değiştir", key="back_button_top"): st.session_state.page = 'calculate'; st.rerun()
    
    sonuc_tablosu = st.session_state.get('sonuc_tablosu_df', pd.DataFrame())
    print("SONUÇ TABLOSU:")
    print(sonuc_tablosu['Prim (TRY)'].sum())
    para_birimi, kur = st.session_state.get('para_birimi', 'TRY'), st.session_state.get('kur', 1.0)
    enflasyon, limit = st.session_state.get('enflasyon_orani', 0), st.session_state.get('limit_orani', None)
    deprem_net_prim_try = sonuc_tablosu['Prim (TRY)'].sum()
    toplam_sigorta_bedeli_try = sonuc_tablosu['Bedel (TRY)'].sum()
    sabit_makine_bedeli_try = st.session_state.get('sabit_makine_bedeli_try', 0)
    sabit_makine_bedeli_doviz = sabit_makine_bedeli_try / kur if kur > 0 else 0

    st.markdown("---")
    with st.container(border=True):
        st.subheader("Deprem Primi Hesaplama Özeti")
        col1, col2 = st.columns(2)
        with col1:
            st.markdown(f"**Para Birimi:** `{para_birimi}` | **Güncel Kur:** `{kur:.4f}`")
            st.markdown(f"**Enflasyon Oranı (PD):** `%{enflasyon}`" if enflasyon > 0 else "**Enflasyon Oranı:** `Yok`")
            if limit: st.markdown(f"**Tazminat Limiti:** `%{limit}`")
        with col2:
            deprem_net_prim_doviz = deprem_net_prim_try / kur if kur > 0 else 0
            st.metric(label=f"Hesaplanan Deprem Net Primi ({para_birimi})", value=f"{deprem_net_prim_doviz:,.2f}")
        df_display = pd.DataFrame()
        df_display['Kalem'] = sonuc_tablosu['Kalem']
        df_display[f'Bedel ({para_birimi})'] = sonuc_tablosu['Bedel (TRY)'] / kur if kur > 0 else 0
        df_display['Nihai Fiyat (‰)'] = sonuc_tablosu['Nihai Fiyat (‰)']
        df_display[f'Prim ({para_birimi})'] = sonuc_tablosu['Prim (TRY)'] / kur if kur > 0 else 0
        st.dataframe(df_display, use_container_width=True, hide_index=True,
                         column_config={
                              f"Bedel ({para_birimi})": st.column_config.NumberColumn(format="%,.2f"),
                              "Nihai Fiyat (‰)": st.column_config.NumberColumn(format="%.4f"),
                              f"Prim ({para_birimi})": st.column_config.NumberColumn(format="%,.2f"),
                         })

    st.markdown("---"); st.subheader("Firma Risk Sınıflandırması")
    risk_primi_rate = 0.0
    with st.container(border=True):
        main_activity = st.selectbox("1. Ana Faaliyet Grubunu Seçin:", options=list(RISK_CLASSIFICATION.keys()), index=None, placeholder="Seçim yapınız...")
        if main_activity:
            faaliyet_df = pd.DataFrame([(ex, sg) for sg, ex_list in RISK_CLASSIFICATION[main_activity].items() for ex in ex_list], columns=['Faaliyet', 'AltGrup'])
            final_activity = st.selectbox("2. Faaliyet Alanını Seçin:", options=faaliyet_df['Faaliyet'].tolist(), index=None, placeholder="Faaliyet alanını seçiniz...")
            if final_activity:
                selected_subgroup = faaliyet_df[faaliyet_df['Faaliyet'] == final_activity]['AltGrup'].iloc[0]
                st.success(f"**Seçilen Risk Sınıfı:** {selected_subgroup} -> {final_activity}")
                
                if selected_subgroup.startswith("Düşük Riskli"):
                    st.session_state.makine_kirilmasi_orani = 0.5
                elif selected_subgroup.startswith("Orta Riskli"):
                    st.session_state.makine_kirilmasi_orani = 0.9
                elif selected_subgroup.startswith("Yüksek Riskli"):
                    st.session_state.makine_kirilmasi_orani = 1.5
                else: 
                    st.session_state.makine_kirilmasi_orani = 0.5

                RISK_PREMIUM_RATES = {
                    "Düşük Riskli Sınai (Hafif Sanayi)": 0.02, "Orta Riskli Sınai": 0.05, "Yüksek Riskli Sınai (Ağır/Tehlikeli)": 0.5,
                    "Düşük Riskli Depolama": 0.02, "Yüksek Riskli Depolama": 0.5,
                    "Düşük Riskli Enerji": 0.02, "Orta Riskli Enerji": 0.05, "Yüksek Riskli Enerji": 0.5
                }
                if main_activity in ["Sınai Faaliyetler (Üretim/İmalat)", "Depolama Faaliyetleri (Lojistik)", "Enerji Santralleri"]:
                    risk_primi_rate = RISK_PREMIUM_RATES.get(selected_subgroup, 0)

    st.markdown("---"); st.subheader("Hasar Geçmişi")
    hasar_primi_rate = 0.0
    bedel_primi_permille_rate = calculate_bedel_primi_permille_rate(toplam_sigorta_bedeli_try)
    with st.container(border=True):
        hp_option = st.selectbox("Son 5 Yıllık Hasar/Net Poliçe Primi Oranı", options=["Bilinmiyor", "< 50%", "50% - 100%", "> 100%"])
        if hp_option == "50% - 100%":
            hasar_primi_rate = bedel_primi_permille_rate / 2
        elif hp_option == "> 100%":
            hasar_primi_rate = bedel_primi_permille_rate

    st.markdown("---"); st.subheader("Otomatik Hesaplanan Fiyatlar")
    with st.container(border=True):
        rate_col1, rate_col2, rate_col3 = st.columns(3)
        rate_col1.metric("Faaliyet Kolu Risk Fiyatı (‰)", f"{risk_primi_rate:.4f}")
        rate_col2.metric("Bedel Primi Fiyatı (‰)", f"{bedel_primi_permille_rate:.4f}")
        rate_col3.metric("Hasar Primi Fiyatı (‰)", f"{hasar_primi_rate:.4f}")

    bedel_primi_try = toplam_sigorta_bedeli_try * (bedel_primi_permille_rate / 1000)
    risk_primi_try = toplam_sigorta_bedeli_try * (risk_primi_rate / 1000)
    hasar_primi_try = toplam_sigorta_bedeli_try * (hasar_primi_rate / 1000)

    st.markdown("---"); st.subheader("İsteğe Bağlı Ek Teminatlar")
    makine_kirilmasi_orani = st.session_state.get('makine_kirilmasi_orani', 0.0)
    EK_TEMINATLAR = {
        "Sel ve Su Baskını": {"oran": 0.0001, "limit_kurali": lambda pd: pd, "baz": "limit"},
        "Dahili Su": {"oran": 0.0001, "limit_kurali": lambda pd: pd, "baz": "limit"},
        "Fırtına": {"oran": 0.0001, "limit_kurali": lambda pd: pd, "baz": "limit"},
        "Dolu": {"oran": 0.0001, "limit_kurali": lambda pd: pd, "baz": "limit"},
        "Yer Kayması": {"oran": 0.0001, "limit_kurali": lambda pd: pd, "baz": "limit"},
        "Kar Ağırlığı": {"oran": 0.0001, "limit_kurali": lambda pd: pd, "baz": "limit"},
        "Duman": {"oran": 0.0001, "limit_kurali": lambda pd: pd, "baz": "limit"},
        "Kara/Hava/Deniz Taşıtları Çarpması": {"oran": 0.0001, "limit_kurali": lambda pd: pd, "baz": "limit"},
        "Hırsızlık": {"oran": 0.0001, "limit_kurali": lambda pd: pd, "baz": "limit"},
        "Enkaz Kaldırma Masrafları": {"oran": 0.0001, "limit_kurali": lambda pd: pd * 0.04, "baz": "limit"},
        "Cam Kırılması": {"oran": 0.1, "limit_kurali": lambda pd: pd * 0.01, "baz": "limit"},
        "Alternatif İş Yeri Masrafları": {"oran": 0.001, "limit_kurali": lambda pd: pd * 0.0001, "baz": "limit"},
        "İş Durması (Diğer Rizikolar)": {"oran": 0.001, "limit_kurali": lambda pd: pd * 0.0001, "baz": "prim"},
        "Yangın Mali Mesuliyet": {"oran": 0.01, "limit_kurali": lambda pd: pd * 0.10, "baz": "limit"},
        "Sabit Makine Kırılması": {"oran": makine_kirilmasi_orani, "limit_kurali": lambda pd: sabit_makine_bedeli_doviz, "baz": "limit"}
    }
    secilen_teminatlar_ve_limitleri, toplam_pd_bedeli_try = {}, sonuc_tablosu[~sonuc_tablosu['Kalem'].str.contains("Kar Kaybı")]['Bedel (TRY)'].sum()
    toplam_pd_bedeli_doviz = toplam_pd_bedeli_try / kur if kur > 0 else 0
    with st.container(border=True):
        for teminat, detay in EK_TEMINATLAR.items():
            col1, col2, col3 = st.columns([0.5, 3, 1.5])
            is_selected = col1.checkbox("", key=f"cb_{teminat}", label_visibility="collapsed")
            label_style = "color: black;" if is_selected else "color: grey;"
            col2.markdown(f"<p style='{label_style}'>{teminat}</p>", unsafe_allow_html=True)
            default_limit = detay["limit_kurali"](toplam_pd_bedeli_doviz)
            limit_bedeli = col3.number_input(f"Limit ({para_birimi})", disabled=not is_selected, key=f"limit_{teminat}", value=int(default_limit), format="%d")
            secilen_teminatlar_ve_limitleri[teminat] = {"secili": is_selected, "limit_try": limit_bedeli * kur}
        st.caption("Not: Başlangıçta gösterilen limitler öneri niteliğindedir ve değiştirilebilir.")

    st.markdown("---"); st.subheader("Nihai Poliçe Tutarı")
    ek_prim_detaylari = []
    
    # Adım 1: Limite dayalı teminatların primlerini hesapla
    limit_based_premiums = []
    for teminat, durum in secilen_teminatlar_ve_limitleri.items():
        if durum["secili"]:
            teminat_detay = EK_TEMINATLAR[teminat]
            if teminat_detay.get("baz") == "limit":
                prim_val = durum["limit_try"] * (teminat_detay["oran"] / 1000)
                limit_based_premiums.append({"Teminat": teminat, "Prim (TRY)": prim_val})

    ek_prim_detaylari.extend(limit_based_premiums)
    
    # Adım 2: Yukarıdakilere dayalı olan prime dayalı teminatları hesapla
    diger_teminatlarin_primi_toplami = sum(item['Prim (TRY)'] for item in limit_based_premiums)
    
    if secilen_teminatlar_ve_limitleri.get("İş Durması (Diğer Rizikolar)", {}).get("secili"):
        teminat_detay_is_durmasi = EK_TEMINATLAR["İş Durması (Diğer Rizikolar)"]
        # 'oran'ın bu teminat için bir yüzde olduğunu varsayıyoruz
        prim_is_durmasi = diger_teminatlarin_primi_toplami * (teminat_detay_is_durmasi["oran"] / 100)
        ek_prim_detaylari.append({"Teminat": "İş Durması (Diğer Rizikolar)", "Prim (TRY)": prim_is_durmasi})

    # Adım 3: Nihai ek teminatlar toplam primini hesapla
    toplam_ek_teminat_primi_try = sum(item['Prim (TRY)'] for item in ek_prim_detaylari)

    with st.container(border=True):
        col1, col2 = st.columns(2)
        with col1:
            st.write("**Poliçe Kalemleri**")
            acente_komisyon_orani = st.number_input("Acente Komisyon Oranı (%)", min_value=0.0, max_value=100.0, value=17.0, step=0.5)
            BSMV_ORANI = 5.0
            net_prim_tabani_try = deprem_net_prim_try + toplam_ek_teminat_primi_try + risk_primi_try + bedel_primi_try + hasar_primi_try
            ysv_primi_try = net_prim_tabani_try / 9999 # YSV, Toplam Net Prim'in 1/10000'i ise bu hesaplama doğrudur.
            toplam_net_prim_try = net_prim_tabani_try + ysv_primi_try
            acente_komisyon_tutari = toplam_net_prim_try * (acente_komisyon_orani / 100)
            bsmv_tutari = toplam_net_prim_try * (BSMV_ORANI / 100)
            odenecek_toplam_try = toplam_net_prim_try + bsmv_tutari
            odenecek_toplam_doviz = odenecek_toplam_try / kur if kur > 0 else 0
        with col2:
            st.write(f"**Tutar ({para_birimi})**")
            left, right = st.columns([3,2])
            left.write("**Toplam Net Prim:**"); right.markdown(f"<p style='text-align: right;'><strong>{toplam_net_prim_try / kur:,.2f}</strong></p>", unsafe_allow_html=True)
            left.write(f"Acente Komisyonu (%{acente_komisyon_orani:.1f}):"); right.markdown(f"<p style='text-align: right;'>{acente_komisyon_tutari / kur:,.2f}</p>", unsafe_allow_html=True)
            left.write("YSV Primi:"); right.markdown(f"<p style='text-align: right;'>{ysv_primi_try / kur:,.2f}</p>", unsafe_allow_html=True)
            left.write(f"BSMV (%{BSMV_ORANI:.1f}):"); right.markdown(f"<p style='text-align: right;'>{bsmv_tutari / kur:,.2f}</p>", unsafe_allow_html=True)
            left.markdown("---"); right.markdown("---")
            left.write("**Toplam Brüt Prim:**"); right.markdown(f"<p style='text-align: right;'><strong>{odenecek_toplam_doviz:,.2f}</strong></p>", unsafe_allow_html=True)

    if ek_prim_detaylari:
        with st.expander("Seçilen Ek Teminatların Prim Dağılımını Gör"): st.dataframe(pd.DataFrame(ek_prim_detaylari), use_container_width=True, hide_index=True)
    st.markdown("---")
    if st.button("Yeni Hesaplama Yap", use_container_width=True, key="new_calculation_button_bottom"):
        keys_to_clear = ['sonuc_verileri', 'sonuc_tablosu_df', 'para_birimi', 'kur', 'enflasyon_orani', 'limit_orani', 'sabit_makine_bedeli_try', 'makine_kirilmasi_orani']
        for key in keys_to_clear:
            if key in st.session_state: del st.session_state[key]
        st.switch_page("pages/calculate.py")

render_police_hesaplama_page()