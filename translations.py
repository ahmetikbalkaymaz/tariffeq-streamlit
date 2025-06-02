T = {
    "title": {"TR": "TariffEQ", "EN": "TariffEQ"}, # Ana sayfa ve hesaplama için ortak başlık veya her sayfa için ayrı
    "subtitle": { # Ana sayfa için
        "TR": "Akıllı Sigorta Prim Hesaplama Platformu",
        "EN": "Smart Insurance Premium Calculation Platform"
    },
    "start": {"TR": "Hesaplamaya Başla", "EN": "Start Calculation"},
    "desc": {
        "TR": "TariffEQ, deprem, inşaat ve ticari rizikolar için minimum prim hesaplamalarını saniyeler içinde yapmanızı sağlar.",
        "EN": "TariffEQ enables you to calculate minimum insurance premiums for earthquake, construction, and commercial risks within seconds."
    },
    "why": {"TR": "TariffEQ Nedir?", "EN": "What is TariffEQ?"},
    "feature1": {"TR": "⚡ Kolay ve Hızlı Kullanım", "EN": "⚡ Easy & Fast Use"},
    "feature2": {"TR": "📐 Teknik Doğruluk", "EN": "📐 Technical Accuracy"},
    "feature3": {"TR": "🤝 Reasürör ve Broker Dostu", "EN": "🤝 Reinsurer & Broker Friendly"},
    "founders": {"TR": "Kurucular", "EN": "Founders"},
    "contact": { # Ana sayfa için
        "TR": "Sorularınız için bize info@tariffeq.com adresinden ulaşabilirsiniz.",
        "EN": "For inquiries, contact us at info@tariffeq.com"
    },
    "footer": {
        "TR": "© 2025 TariffEQ. Tüm Hakları Saklıdır.",
        "EN": "© 2025 TariffEQ. All rights reserved."
    },
    "comment": {"TR": "Yorum Bırak", "EN": "Leave a Comment"},
    "comment_placeholder": {"TR": "Yorumunuzu buraya yazın...", "EN": "Write your comment here..."},
    "submit": {"TR": "Gönder", "EN": "Submit"},
    "home": {"TR": "Ana Sayfa", "EN": "Home"},
    "calc": {"TR": "🚀  Deprem Primi ve Hasar Riski", "EN": "🚀 Earthquake Premium and Damage Risk"},

    # calculate.py için özel çeviriler
    "calc_title": {"TR": "TariffEQ", "EN": "TariffEQ"}, # calculate.py başlığı
    "calc_subtitle": {"TR": "Deprem ve Yanardağ Püskürmesi Teminatı için Uygulanacak Güncel Tarife", "EN": "Current Tariff for Earthquake and Volcanic Eruption Coverage"}, # calculate.py altbaşlığı
    "fire_header": {"TR": "Riziko Bilgileri", "EN": "Risk Details"},
    "car_header": {"TR": "🏗️ Proje Bilgileri", "EN": "🏗️ Project Details"},
    "select_calc": {"TR": "Hesaplama Türünü Seçin", "EN": "Select Calculation Type"},
    "calc_fire": {"TR": "Deprem Teminatı - Ticari Sınai Rizikolar (PD & BI)", "EN": "Earthquake Coverage – Commercial / Industrial (PD & BI)"},
    "calc_car": {"TR": "İnşaat & Montaj (CAR & EAR)", "EN": "Construction & Erection (CAR & EAR)"},
    "num_locations": {"TR": "Lokasyon Sayısı", "EN": "Number of Locations"},
    "num_locations_help": {"TR": "Hesaplama yapılacak lokasyon sayısını girin (1-10).", "EN": "Enter the number of locations to calculate (1-10)."},
    "location_group": {"TR": "Riziko Adresi Grubu", "EN": "Risk Address Group"},
    "location_group_help": {
        "TR": "Bu lokasyonun hangi risk grubuna ait olduğunu seçin. Farklı gruplar için ayrı prim hesaplaması yapılır.",
        "EN": "Select the risk group this location belongs to. Separate premium calculations are made for different groups."
    },
    "location_group_help_cumulative": {
        "TR": "Kümül oluşturan adresleri aynı gruba atayınız.",
        "EN": "Assign addresses that form a cumulation to the same group."
    },
    "building_type": {"TR": "Yapı Tarzı", "EN": "Construction Type"},
    "building_type_help": {"TR": "Betonarme: Çelik veya betonarme taşıyıcı karkas bulunan yapılar. Diğer: Bu gruba girmeyen yapılar.", "EN": "Concrete: Structures with steel or reinforced concrete framework. Other: Structures not in this group."},
    "risk_group": {"TR": "Deprem Risk Grubu (1=En Yüksek Risk)", "EN": "Earthquake Risk Zone (1=Highest)"},
    "risk_group_help": {"TR": "Deprem risk grupları, Doğal Afet Sigortaları Kurumu tarafından belirlenir. 1. Grup en yüksek risktir.", "EN": "Earthquake risk zones are determined by the Natural Disaster Insurance Institution. Zone 1 is the highest risk."},
    "currency": {"TR": "Para Birimi", "EN": "Currency"},
    "manual_fx": {"TR": "Kuru manuel güncelleyebilirsiniz", "EN": "You can manually update the exchange rate"},
    "building_sum": {"TR": "Bina Bedeli", "EN": "Building Sum Insured"},
    "building_sum_help": {"TR": "Bina için sigorta bedeli. Betonarme binalar için birim metrekare fiyatı min. 18,600 TL, diğerleri için 12,600 TL.", "EN": "Sum insured for the building. Min. unit square meter price for concrete buildings: 18,600 TL; others: 12,600 TL."},
    "fixture_sum": {"TR": "Demirbaş Bedeli", "EN": "Fixture Sum Insured"},
    "fixture_sum_help": {"TR": "Demirbaşlar için sigorta bedeli.", "EN": "Sum insured for fixtures."},
    "decoration_sum": {"TR": "Dekorasyon Bedeli", "EN": "Decoration Sum Insured"},
    "decoration_sum_help": {"TR": "Dekorasyon için sigorta bedeli.", "EN": "Sum insured for decoration."},
    "commodity_sum": {"TR": "Emtea Bedeli", "EN": "Commodity Sum Insured"},
    "commodity_sum_help": {"TR": "İşyerinizdeki ticari malların (hammadde, yarı mamul, mamul) toplam değeri.", "EN": "Total value of commercial goods (raw materials, semi-finished, finished products) in your workplace."},
    "commodity_is_subscription": {"TR": "Emtea Abonman mı?", "EN": "Commodity Subscription?"},
    "commodity_is_subscription_help": {"TR": "Eğer emtia bedeli abonman poliçesi kapsamında ise işaretleyiniz (bedelin %40'ı dikkate alınır).", "EN": "Check if the commodity value is under a subscription policy (40% of the value is considered)."},
    "safe_sum": {"TR": "Kasa Muhteviyatı Bedeli", "EN": "Safe Contents Sum"},
    "safe_sum_help": {"TR": "Kasa için sigorta bedeli.", "EN": "Sum insured for the safe."},
    "bi": {"TR": "Kar Kaybı Bedeli (BI)", "EN": "Business Interruption Sum Insured (BI)"},
    "bi_help": {"TR": "Deprem sonrası ticari faaliyetin durması sonucu ciro azalması ve maliyet artışından kaynaklanan brüt kâr kaybı.", "EN": "Gross profit loss due to reduced turnover and increased costs from business interruption after an earthquake."},
    "ec_fixed": {"TR": "Elektronik Cihaz Bedeli (Sabit)", "EN": "Electronic Device Sum Insured (Fixed)"},
    "ec_fixed_help": {"TR": "Sabit elektronik cihazlar için sigorta bedeli.", "EN": "Sum insured for fixed electronic devices."},
    "ec_mobile": {"TR": "Elektronik Cihaz Bedeli (Taşınabilir)", "EN": "Electronic Device Sum Insured (Mobile)"},
    "ec_mobile_help": {"TR": "Taşınabilir elektronik cihazlar için sigorta bedeli.", "EN": "Sum insured for mobile electronic devices."},
    "mk_fixed": {"TR": "Makine Kırılması Bedeli (Sabit)", "EN": "Machinery Breakdown Sum Insured (Fixed)"},
    "mk_fixed_help": {"TR": "Sabit makineler için sigorta bedeli.", "EN": "Sum insured for fixed machinery."},
    "mk_mobile": {"TR": "Makine Kırılması Bedeli (Hareketli)", "EN": "Machinery Breakdown Sum Insured (Mobile)"},
    "mk_mobile_help": {"TR": "Hareketli makineler için sigorta bedeli.", "EN": "Sum insured for portable machinery."},
    "koas": {"TR": "Koasürans Oranı", "EN": "Coinsurance Share"},
    "koas_help": {"TR": "Örnek: (80/20) -  %80 Sigortacı , %20 Sigortalı Üzerinde Kalan Kısımdır.", "EN": "Example: (80/20) – 80% is carried by the Insurer, and the remaining 20% is retained by the Insured"},
    "deduct": {"TR": "Muafiyet Oranı (%)", "EN": "Deductible (%)"},
    "deduct_help": {"TR": "Her hasarda bina sigorta bedeli üzerinden uygulanır. Min. %2, artırılabilir (max. %35 indirim).", "EN": "Applied per loss on the building sum insured. Min. 2%, can be increased (max. 35% discount)."},
    "inflation_rate": {"TR": "Enflasyon Artış Oranı (%)", "EN": "Inflation Increase Rate (%)"},
    "inflation_rate_help": {"TR": "Enflasyona karşı teminat artışı oranı. Tarife fiyatı bu oranın yarısı kadar artırılır.", "EN": "Rate of increase for inflation protection. Tariff rate is increased by half of this rate."},
    "btn_calc": {"TR": "Hesapla", "EN": "Calculate"},
    "min_premium": {"TR": "Minimum Deprem Primi", "EN": "Minimum Earthquake Premium"},
    "applied_rate": {"TR": "Uygulanan Oran (binde)", "EN": "Applied Rate (per mille)"},
    "risk_class": {"TR": "Deprem Risk Grubu (1=En Yüksek Risk)", "EN": "Earthquake Risk Zone (1=Highest)"}, # Bu anahtar zaten yukarıda "risk_group" olarak var, birleştirilebilir veya biri seçilebilir. Şimdilik ikisini de tutuyorum.
    "risk_class_help": {"TR": "Deprem risk grupları, Doğal Afet Sigortaları Kurumu tarafından belirlenir. 1. Grup en yüksek risktir.", "EN": "Earthquake risk zones are determined by the Natural Disaster Insurance Institution. Zone 1 is the highest risk."}, # Yukarıdaki "risk_group_help" ile aynı.
    "start_date": {"TR": "Poliçe Başlangıcı", "EN": "Policy Start"}, # "start" anahtarı zaten var, bu "policy_start" gibi daha spesifik olabilir.
    "end_date": {"TR": "Poliçe Bitişi", "EN": "Policy End"}, # "policy_end" gibi.
    "duration": {"TR": "Süre", "EN": "Duration"},
    "months": {"TR": "ay", "EN": "months"},
    "duration_help": {"TR": "Sigorta süresi. 36 aydan uzun projelerde her ay için %3 eklenir.", "EN": "Policy duration. For projects over 36 months, 3% is added per month."},
    "coins": {"TR": "Koasürans", "EN": "Coinsurance"}, # "koas" anahtarı zaten var.
    "coins_help": {"TR": "Sigortalının hasara iştirak oranı. Min. %20 sigortalı üzerinde kalır. %60’a kadar artırılabilir (max. %50 indirim).", "EN": "Insured's share in the loss. Min. 20% remains with the insured. Can be increased to 60% (max. 50% discount)."}, # "koas_help" zaten var.
    "ded": {"TR": "Muafiyet (%)", "EN": "Deductible (%)"}, # "deduct" anahtarı zaten var.
    "ded_help": {"TR": "Her hasarda sigorta bedeli üzerinden uygulanır. Min. %2, artırılabilir (max. %35 indirim).", "EN": "Applied per loss on the sum insured. Min. 2%, can be increased (max. 35% discount)."}, # "deduct_help" zaten var.
    "project": {"TR": "Proje Bedeli (CAR & EAR)", "EN": "Project Sum Insured (CAR & EAR)"},
    "project_help": {"TR": "Proje nihai değeri (gümrük, vergi, nakliye ve işçilik dahil). Min. sözleşme bedeli kadar olmalı.", "EN": "Final project value (including customs, taxes, transport, and labor). Must be at least the contract value."},
    "cpm": {"TR": "İnşaat Makineleri (CPM)", "EN": "Construction Machinery (CPM)"},
    "cpm_help": {"TR": "İnşaat makineleri için teminat bedeli. Aynı riziko adresinde kullanılmalı.", "EN": "Sum insured for construction machinery. Must be used at the same risk address."},
    "cpe": {"TR": "Şantiye Tesisleri (CPE)", "EN": "Site Facilities (CPE)"},
    "cpe_help": {"TR": "Şantiye tesisleri için teminat bedeli. Aynı riziko adresinde bulunmalı.", "EN": "Sum insured for site facilities. Must be at the same risk address."},
    "total_premium": {"TR": "Toplam Minimum Prim", "EN": "Total Minimum Premium"},
    "car_premium": {"TR": "CAR Primi", "EN": "CAR Premium"},
    "cpm_premium": {"TR": "CPM Primi", "EN": "CPM Premium"},
    "cpe_premium": {"TR": "CPE Primi", "EN": "CPE Premium"},
    "ec_premium": {"TR": "Elektronik Cihaz Primi", "EN": "Electronic Device Premium"},
    "mk_premium": {"TR": "Makine Kırılması Primi", "EN": "Machinery Breakdown Premium"},
    "group_premium": {"TR": "Grup Primi", "EN": "Group Premium"},
    "limit_warning_fire_pd": {"TR": "⚠️ Yangın Sigorta Bedeli: 3.5 milyar TRY limitini aşıyor. Prim hesaplama bu limite göre yapılır.", "EN": "⚠️ Property Damage: Sum insured exceeds the 3.5 billion TRY limit. Premium calculation will be based on this limit."},
    "limit_warning_fire_bi": {"TR": "⚠️ Kar Kaybı Bedeli: 3.5 milyar TRY limitini aşıyor. Prim hesaplama bu limite göre yapılır.", "EN": "⚠️ Business Interruption: Sum insured exceeds the 3.5 billion TRY limit. Premium calculation will be based on this limit."},
    "limit_warning_ec": {"TR": "⚠️ Elektronik Cihaz: Sigorta bedeli 840 milyon TRY limitini aşıyor. Prim hesaplama bu limite göre yapılır.", "EN": "⚠️ Electronic Device: Sum insured exceeds the 840 million TRY limit. Premium calculation will be based on this limit."},
    "limit_warning_mk": {"TR": "⚠️ Makine Kırılması: Sigorta bedeli 840 milyon TRY limitini aşıyor. Prim hesaplama bu limite göre yapılır.", "EN": "⚠️ Machinery Breakdown: Sum insured exceeds the 840 million TRY limit. Premium calculation will be based on this limit."},
    "limit_warning_car": {"TR": "⚠️ İnşaat & Montaj: Toplam sigorta bedeli 840 milyon TRY limitini aşıyor. Prim hesaplama bu limite göre yapılır.", "EN": "⚠️ Construction & Erection: Total sum insured exceeds the 840 million TRY limit. Premium calculation will be based on this limit."},
    "entered_value": {"TR": "Girilen Değer", "EN": "Entered Value"},
    "pd_premium": {"TR": "PD Primi", "EN": "PD Premium"},
    "bi_premium": {"TR": "BI Primi", "EN": "BI Premium"},
    "risk_group_type": {"TR": "Risk Sınıfı", "EN": "Risk Class"},
    "risk_group_type_help": {
        "TR": "Risk Sınıfı A: Her türlü bina inşaatı, bina içi dekorasyon ve tadilat işleri, makine, teçhizat ve geçici baraka/yardımcı tesisler (yıllık). Risk Sınıfı B: Altyapı ve ağır mühendislik işleri: kara/demiryolu, tünel, köprü, viyadük, baraj, metro, havaalanı, liman vb. Endüstriyel tesisler: enerji santrali, iletim hattı, silo, kule, tank. Zemin ve temel işleri: iksa, istinat, zemin iyileştirme, dolgular. Sulama, kanalizasyon ve altyapı işleri. Peyzaj, saha düzenleme ve park-bahçe işleri. Montaj işleri ve A dışında kalan diğer inşaat türleri.",
        "EN": "Risk Class A: All types of building construction, interior decoration and renovation works, machinery, equipment, and temporary sheds/support facilities (annual). Risk Class B: Infrastructure and heavy engineering works: roads/railways, tunnels, bridges, viaducts, dams, metro, airports, ports, etc. Industrial facilities: power plants, transmission lines, silos, towers, tanks. Ground and foundation works: shoring, retaining walls, ground improvement, fills. Irrigation, sewerage, and infrastructure works. Landscaping, site arrangement, and park-garden works. Assembly works and other construction types outside A."
    },
    "insurance_sums": {"TR": "Sigorta Bedelleri 📋", "EN": "Insurance Sums Insured 📋"},
    "coinsurance_deductible": {"TR": "Koasürans / Muafiyet Oranı ⚖️", "EN": "Coinsurance / Deductible Rate ⚖️"},
    "select_fire_button": {
        "TR": "Yangın, Kâr Kaybı & Mühendislik Deprem Primi - Hemen Hesapla 🔍",
        "EN": "PD-BI & Engineering Earthquake Premium – Calculate Now 🔍"
    },
    "select_car_button": {
        "TR": "İnşaat & Montaj Primi - Hemen Hesapla 🏗️",
        "EN": "Construction & Erection Premium – Calculate Now 🏗️"
    },
    "current_entered_sums_header": {"TR": "Anlık Girilen Toplam Bedeller (Prim Hesaplamasına Esas)", "EN": "Current Entered Totals (Basis for Premium Calculation)"},
    "total_entered_pd_sum_effective": {"TR": "Toplam PD Bedeli (Etkin)", "EN": "Total PD Sum (Effective)"},
    "total_entered_bi_sum": {"TR": "Toplam Girilen BI Bedeli", "EN": "Total Entered BI Sum"},
    "total_entered_ec_sum": {"TR": "Toplam Girilen Elektronik Cihaz Bedeli", "EN": "Total Entered Electronic Device Sum"},
    "total_entered_mk_sum": {"TR": "Toplam Girilen Makine Kırılması Bedeli", "EN": "Total Entered Machinery Breakdown Sum"},
    "total_entered_car_sum": {"TR": "Toplam Girilen İnşaat & Montaj Bedeli", "EN": "Total Entered Construction & Erection Sum"},
    "total_entered_project_sum": {"TR": "Toplam Girilen Proje Bedeli", "EN": "Total Entered Project Sum"},
    "total_entered_cpm_sum": {"TR": "Toplam Girilen İnşaat Makineleri Bedeli", "EN": "Total Entered Construction Machinery Sum"},
    "total_entered_cpe_sum": {"TR": "Toplam Girilen Şantiye Tesisleri Bedeli", "EN": "Total Entered Site Facilities Sum"},
    "total_entered_commodity_sum": {"TR": "Toplam Girilen Emtea Bedeli", "EN": "Total Entered Commodity Sum"},
    "total_entered_safe_sum": {"TR": "Toplam Girilen Kasa Bedeli", "EN": "Total Entered Safe Sum"},
    "total_entered_bi_premium": {"TR": "Toplam Girilen BI Primi", "EN": "Total Entered BI Premium"},
    "total_entered_pd_premium": {"TR": "Toplam Girilen PD Primi", "EN": "Total Entered PD Premium"},
    "total_entered_ec_premium": {"TR": "Toplam Girilen Elektronik Cihaz Primi", "EN": "Total Entered Electronic Device Premium"},
    "total_entered_mk_premium": {"TR": "Toplam Girilen Makine Kırılması Primi", "EN": "Total Entered Machinery Breakdown Premium"},
    "total_entered_car_premium": {"TR": "Toplam Girilen İnşaat & Montaj Primi", "EN": "Total Entered Construction & Erection Premium"},
    "total_entered_project_premium": {"TR": "Toplam Girilen Proje Primi", "EN": "Total Entered Project Premium"},
    "total_entered_cpm_premium": {"TR": "Toplam Girilen İnşaat Makineleri Primi", "EN": "Total Entered Construction Machinery Premium"},
    "total_entered_cpe_premium": {"TR": "Toplam Girilen Şantiye Tesisleri Primi", "EN": "Total Entered Site Facilities Premium"},
    "effective_value": {"TR": "Kullanılan Değer", "EN": "Effective Value"},
    "limit_warning_mk": {"TR": "⚠️ Makine Kırılması bedeli 840 Milyon TL limitini aşıyor. Prim bu limite göre hesaplanacaktır.", "EN": "⚠️ Machinery Breakdown sum insured exceeds the 840 Million TRY limit. Premium will be calculated based on this limit."},
    "warning_koas_below_3_5B": {
        "TR": "⚠️ TSI 3.5 Milyar TL'den düşük olduğunda, seçilen '{koas_value}' koasürans oranı geçerli değildir. '90/10' ve '100/0' seçenekleri kullanılamaz. Lütfen uygun bir koasürans seçin.",
        "EN": "⚠️ When TSI is below 3.5 Billion TRY, the selected coinsurance '{koas_value}' is not valid. Options '90/10' and '100/0' cannot be used. Please select a valid coinsurance."
    },
    "warning_deduct_below_3_5B": {
        "TR": "⚠️ TSI 3.5 Milyar TL'den düşük olduğunda, seçilen '{deduct_value}%' muafiyet oranı geçerli değildir. Muafiyet %2'den düşük olamaz. Lütfen %2 veya daha yüksek bir muafiyet seçin.",
        "EN": "⚠️ When TSI is below 3.5 Billion TRY, the selected deductible '{deduct_value}%' is not valid. Deductible cannot be less than 2%. Please select a deductible of 2% or higher."
    },
    "error_invalid_selections_fire": {
        "TR": "❌ Geçersiz koasürans/muafiyet seçimi nedeniyle prim hesaplanamadı. Lütfen yukarıdaki uyarıları kontrol edin ve seçiminizi güncelleyin.",
        "EN": "❌ Premium could not be calculated due to invalid coinsurance/deductible selection. Please check the warnings above and update your selection."
    },
    "mk_sum_help": {"TR": "İşyerinizdeki makinelerin toplam değeri.", "EN": "Total value of machinery in your workplace."},
    "commodity_sum": {"TR": "Emtea Bedeli", "EN": "Commodity Sum"},
    "mk_sum": {"TR": "Makine Bedeli", "EN": "Machinery Sum"},
    "ec_mk_sums_header": {"TR": "Elektronik Cihaz ve Makine Kırılması Bedelleri", "EN": "Electronic Equipment and Machinery Breakdown Sums"},
    "ec_mk_cover_options_header": {"TR": "Elektronik Cihaz ve Makine Kırılması Teminatı Alınıyor mu?", "EN": "Electronic Equipment and Machinery Breakdown Coverage Taken?"},
    "mk_cover_subheader": {"TR": "Makine Kırılması teminatı Alınıyorsa Soldaki Bedeli Lütfen Aşağıya Giriniz", "EN": "If Machinery Breakdown coverage is taken, please enter the amount on the left below"},
    "include_ec_mk_cover" : {"TR": "Alınıyorsa İşaretleyin Aksi Halde Boş Bırakın", "EN": "Check if taken, otherwise leave blank"},
    "goto_scenario_page_button": {
        "TR": "Detaylı Senaryo Analizine Git",
        "EN": "Go to Detailed Scenario Analysis"
    },
    "scenario_8020_2_name": {
        "TR": "80/20 Koas. - %2 Muaf.",
        "EN": "80/20 Co-ins. - 2% Ded."
    },
    "scenario_9010_2_name": {
        "TR": "90/10 Koas. - %2 Muaf.",
        "EN": "90/10 Co-ins. - 2% Ded."
    },
    "scenario_8020_5_name": {
        "TR": "80/20 Koas. - %5 Muaf.",
        "EN": "80/20 Co-ins. - 5% Ded."
    },
    "scenario_9010_5_name": {
        "TR": "90/10 Koas. - %5 Muaf.",
        "EN": "90/10 Co-ins. - 5% Ded."
    },
    "scenario_7030_5_name": {
        "TR": "70/30 Koas. - %5 Muaf.",
        "EN": "70/30 Co-ins. - 5% Ded."
    },
    "scenario_page_title": {
        "TR": "Senaryo Hesaplama",
        "EN": "Scenario Calculation"
    },
    "scenario_data_missing_warning": {
        "TR": "Senaryo verileri bulunamadı. Lütfen önce 'Hesaplama' sayfasından bir hesaplama yapın ve ardından 'Detaylı Senaryo Analizine Git' butonuna tıklayın.",
        "EN": "Scenario data not found. Please perform a calculation on the 'Calculate' page first and then click the 'Go to Detailed Scenario Analysis' button."
    },
    "go_back_to_calculate_page": {
        "TR": "Hesaplama Sayfasına Geri Dön",
        "EN": "Go Back to Calculate Page"
    },
    "additional_info_for_location_group": {
        "TR": "Grup {group_key} ({location_index}/{total_locations}) için Ek Bina Bilgileri",
        "EN": "Additional Building Information for Group {group_key} ({location_index}/{total_locations})"
    },
    "building_age": {
        "TR": "Bina Kaç Yaşında?",
        "EN": "What is the age of the building?"
    },
    "building_age_options": {
        "TR": ["<10 yıl", "10–30 yıl", ">30 yıl"],
        "EN": ["<10 years", "10–30 years", ">30 years"]
    },
    "structural_type": {
        "TR": "Yapı Tipi Nedir?",
        "EN": "What is the structural type?"
    },
    "structural_type_options": {
        "TR": ["Betonarme", "Çelik", "Yığma", "Diğer"],
        "EN": ["Reinforced Concrete", "Steel", "Masonry", "Other"]
    },
    "num_floors": {
        "TR": "Kat Sayısı Kaçtır?",
        "EN": "How many floors does the building have?"
    },
    "num_floors_options": {
        "TR": ["1–3", "4–7", "8 ve üzeri"],
        "EN": ["1–3", "4–7", "8 or more"]
    },
    "activity_type": {
        "TR": "Binanın Kullanım Amacı Nedir?",
        "EN": "What is the activity type of the building?"
    },
    "activity_type_options": {
        "TR": ["Depolama", "Üretim", "Ofis", "Ticaret", "Diğer"],
        "EN": ["Warehouse", "Manufacturing", "Office", "Retail", "Other"]
    },
    "strengthening": {
        "TR": "Bina Deprem Güçlendirmesi Yapılmış mı?",
        "EN": "Has the building been retrofitted for earthquakes?"
    },
    "strengthening_options": {
        "TR": ["Evet", "Hayır"],
        "EN": ["Yes", "No"]
    },
    "scenario_inputs_collected_info": {
        "TR": "Tüm lokasyonlar için ek bilgiler toplandı.",
        "EN": "Additional information collected for all locations."
    },
    "earthquake_scenario_analysis_title": {
        "TR": "Deprem Hasar Senaryo Analizi",
        "EN": "Earthquake Damage Scenario Analysis"
    },
    "analysis_for_group": {
        "TR": "Grup {group_key} için Analiz",
        "EN": "Analysis for Group {group_key}"
    },
    "risk_group_missing_for_group": {
        "TR": "Grup {group_key} için deprem risk bölgesi bilgisi eksik.",
        "EN": "Earthquake risk zone information is missing for group {group_key}."
    },
    "alt_8020_2": {
        "TR": "80/20 Koas. - %2 Muaf.",
        "EN": "80/20 Co-ins. - 2% Ded."
    },
    "alt_9010_2": {
        "TR": "90/10 Koas. - %2 Muaf.",
        "EN": "90/10 Co-ins. - 2% Ded."
    },
    "alt_8020_5": {
        "TR": "80/20 Koas. - %5 Muaf.",
        "EN": "80/20 Co-ins. - 5% Ded."
    },
    "alt_9010_5": {
        "TR": "90/10 Koas. - %5 Muaf.",
        "EN": "90/10 Co-ins. - 5% Ded."
    },
    "alt_7030_5": {
        "TR": "70/30 Koas. - %5 Muaf.",
        "EN": "70/30 Co-ins. - 5% Ded."
    },
    "damage_scenario_minor": {
        "TR": "Düşük Hasar",
        "EN": "Minor Damage"
    },
    "damage_scenario_expected": {
        "TR": "Beklenen Hasar",
        "EN": "Expected Damage"
    },
    "damage_scenario_severe": {
        "TR": "Yüksek Hasar",
        "EN": "Severe Damage"
    },
    "table_col_alternative": {
        "TR": "Alternatif",
        "EN": "Alternative"
    },
    "table_col_scenario": {
        "TR": "Hasar Senaryosu",
        "EN": "Damage Scenario"
    },
    "table_col_pd_gross_loss": {
        "TR": "PD Brüt Hasar",
        "EN": "PD Gross Loss"
    },
    "table_col_pd_deductible": {
        "TR": "PD Muafiyet",
        "EN": "PD Deductible"
    },
    "table_col_pd_insurer_share": {
        "TR": "PD Sigortacı Payı",
        "EN": "PD Insurer Share"
    },
    "table_col_pd_insured_share": {
        "TR": "PD Sigortalı Payı",
        "EN": "PD Insured Share"
    },
    "table_col_bi_gross_loss": {
        "TR": "BI Brüt Hasar",
        "EN": "BI Gross Loss"
    },
    "table_col_bi_deductible": {
        "TR": "BI Muafiyet",
        "EN": "BI Deductible"
    },
    "table_col_bi_insurer_share": {
        "TR": "BI Sigortacı Payı",
        "EN": "BI Insurer Share"
    },
    "table_col_bi_insured_share": {
        "TR": "BI Sigortalı Payı",
        "EN": "BI Insured Share"
    },
    "total_pd_premium": { # Bu zaten eklenmiş olabilir, kontrol edin
        "TR": "Toplam PD Primi",
        "EN": "Total PD Premium"
    },
    "total_bi_premium": { # Bu zaten eklenmiş olabilir, kontrol edin
        "TR": "Toplam BI Primi",
        "EN": "Total BI Premium"
    },
    "premium_scenarios_from_calculate_page": { # Bu zaten eklenmiş olabilir
        "TR": "Hesaplama Sayfasından Gelen Prim Senaryoları",
        "EN": "Premium Scenarios from Calculate Page"
    },
    "building_info_header": { # Bu zaten eklenmiş olabilir
        "TR": "Bina Bilgileri",
        "EN": "Building Information"
    },
    "group_label": { # Bu zaten eklenmiş olabilir
        "TR": "Grup",
        "EN": "Group"
    },
    "bi_additional_info_header": {
        "TR": "Kar Kaybı (BI) için Ek Bilgiler",
        "EN": "Additional Information for Business Interruption (BI)"
    },
    "bi_activity_type": { # Bu zaten "activity_type" olarak mevcut olabilir, BI için ayrı bir başlık istenirse kullanılır.
        "TR": "Faaliyet Türü (BI için)",
        "EN": "Activity Type (for BI)"
    },
    "bi_activity_type_options": { # PD ile aynı seçenekler kullanılacaksa bu gerekmeyebilir.
        "TR": ["Depolama", "Üretim", "Ofis", "Ticaret", "Diğer"],
        "EN": ["Warehouse", "Manufacturing", "Office", "Retail", "Other"]
    },
    "alternative_production_site": {
        "TR": "Alternatif Üretim/Hizmet Yeri Var mı?",
        "EN": "Is there an alternative production/service site?"
    },
    "alternative_production_site_options": {
        "TR": ["Evet", "Hayır"],
        "EN": ["Yes", "No"]
    },
    "annual_turnover": {
        "TR": "Yıllık Ciro (TRY)",
        "EN": "Annual Turnover (TRY)"
    },
    "annual_turnover_options": {
        "TR": ["1 - 10 Milyon TL", "10 - 50 Milyon TL", "50 Milyon TL Üzeri", "1 Milyon TL Altı"],
        "EN": ["1 - 10 Million TRY", "10 - 50 Million TRY", "Over 50 Million TRY", "Below 1 Million TRY"]
    },
    "business_continuity_plan": {
        "TR": "İş Sürekliliği Planı Var mı?",
        "EN": "Is there a Business Continuity Plan?"
    },
    "business_continuity_plan_options": {
        "TR": ["Evet", "Hayır"],
        "EN": ["Yes", "No"]
    },
    "bi_info_header": {
        "TR": "Kar Kaybı (BI) Bilgileri",
        "EN": "Business Interruption (BI) Information"
    },
    "bi_additional_info_header_for_group": {
        "TR": "Grup {group_key} ({location_index}/{total_locations}) için Kar Kaybı (BI) Bilgileri",
        "EN": "Business Interruption (BI) Information for Group {group_key} ({location_index}/{total_locations})"
    },
    "calculate_scenario_button": {
        "TR": "Senaryo Hesapla ve Tabloyu Göster",
        "EN": "Calculate Scenario and Show Table"
    },
    "table_col_pd_premium": {
        "TR": "PD Prim",
        "EN": "PD Premium"
    },
    "table_col_bi_premium": {
        "TR": "BI Prim",
        "EN": "BI Premium"
    },
    "table_col_total_premium": {
        "TR": "Toplam Prim",
        "EN": "Total Premium"
    },
    "table_col_tcor": {
        "TR": "TCoR (Toplam Risk Maliyeti)",
        "EN": "TCoR (Total Cost of Risk)"
    },
    "pd_damage_ratios_for_group": {
        "TR": "Grup {group_key} için PD Hasar Oranları ve Tahmini Kayıplar",
        "EN": "PD Damage Ratios and Estimated Losses for Group {group_key}"
    },
    "bi_damage_ratios_for_group": {
        "TR": "Grup {group_key} için BI Hasar Oranları, Çarpan ve Tahmini Kayıplar",
        "EN": "BI Damage Ratios, Multiplier, and Estimated Losses for Group {group_key}"
    },
    "bi_multiplier_label": {
        "TR": "BI Çarpanı",
        "EN": "BI Multiplier"
    },
    "bi_minor_loss_rate_label": {
        "TR": "BI Düşük Hasar Oranı",
        "EN": "BI Minor Loss Rate"
    },
    "bi_expected_loss_rate_label": {
        "TR": "BI Beklenen Hasar Oranı",
        "EN": "BI Expected Loss Rate"
    },
    "bi_severe_loss_rate_label": {
        "TR": "BI Yüksek Hasar Oranı",
        "EN": "BI Severe Loss Rate"
    },
    "estimated_bi_minor_loss_label": {
        "TR": "Tahmini BI Düşük Kayıp",
        "EN": "Estimated BI Minor Loss"
    },
    "estimated_bi_expected_loss_label": {
        "TR": "Tahmini BI Beklenen Kayıp",
        "EN": "Estimated BI Expected Loss"
    },
    "estimated_bi_severe_loss_label": {
        "TR": "Tahmini BI Yüksek Kayıp",
        "EN": "Estimated BI Severe Loss"
    },
    "chart_title_pd_insurer_share": {
        "TR": "Farklı Alternatiflerde PD Sigortacı Payı Senaryoları (Grup {group_key})",
        "EN": "PD Insurer Share Scenarios for Different Alternatives (Group {group_key})"
    },
    "chart_xaxis_label_alternatives_with_premium": {
        "TR": "Alternatif (Muafiyet-Koasürans, PD Prim ile birlikte)",
        "EN": "Alternative (Deductible-Coinsurance, with PD Premium)"
    },
    "chart_yaxis_label_insurer_share_try": {
        "TR": "Sigorta Şirketi PD Payı (TRY)",
        "EN": "Insurer PD Share (TRY)"
    },
    "legend_minor_damage": {
        "TR": "Düşük Hasar",
        "EN": "Minor Damage"
    },
    "legend_expected_damage": {
        "TR": "Orta Hasar", # "Beklenen Hasar" yerine "Orta Hasar" olarak güncellendi
        "EN": "Expected Damage" # "Expected Damage" olarak kalabilir veya "Medium Damage"
    },
    "legend_severe_damage": {
        "TR": "Yüksek Hasar",
        "EN": "Severe Damage"
    },
    "limit_recommendations_title": {
        "TR": "Limit Tavsiyeleri (Grup {group_key})",
        "EN": "Limit Recommendations (Group {group_key})"
    },
    "limit_recommendation_intro": {
        "TR": "Poliçenizi aşağıdaki limitlerle yaptırmanız tavsiye edilir. Bu tavsiyeler, girilen bilgilere ve genel hasar senaryolarına dayanmaktadır.",
        "EN": "It is recommended to arrange your policy with the following limits. These recommendations are based on the information provided and general damage scenarios."
    },
    "limit_table_col_coverage": {
        "TR": "Teminat",
        "EN": "Coverage"
    },
    "limit_table_col_full_value": {
        "TR": "Tam Bedel (Full Value)",
        "EN": "Full Value"
    },
    "limit_table_col_minor_limit": {
        "TR": "Hafif Hasar Limiti",
        "EN": "Minor Damage Limit"
    },
    "limit_table_col_expected_limit": {
        "TR": "Beklenen Hasar Limiti",
        "EN": "Expected Damage Limit"
    },
    "limit_table_col_severe_limit": {
        "TR": "Ağır Hasar Limiti",
        "EN": "Severe Damage Limit"
    },
    "limit_table_col_sector_recommendation": {
        "TR": "Sektör Tavsiyesi",
        "EN": "Sector Recommendation"
    },
    "coverage_pd": {
        "TR": "PD (Fiziksel Hasar)",
        "EN": "PD (Physical Damage)"
    },
    "coverage_bi": {
        "TR": "BI (Kar Kaybı)",
        "EN": "BI (Business Interruption)"
    },
    "sector_recommendation_text_pd": {
        "TR": "{expected_limit_str} - {severe_limit_str}. Beklenen veya ağır hasar senaryosuna göre limit seçmeniz, olası deprem sonrası finansal kaybınızın önemli bir kısmını güvence altına alır.",
        "EN": "{expected_limit_str} - {severe_limit_str}. Choosing a limit based on the expected or severe damage scenario secures a significant portion of your potential financial loss after an earthquake."
    },
    "sector_recommendation_text_bi": {
        "TR": "{expected_limit_str} - {severe_limit_str}. İş durması süresince oluşabilecek kar kaybınızı karşılamak için bu aralıkta bir limit değerlendirilebilir.",
        "EN": "{expected_limit_str} - {severe_limit_str}. A limit within this range can be considered to cover your loss of profit during business interruption."
    },
    "general_limit_advice_title": {
        "TR": "Genel Limit Tavsiyeleri",
        "EN": "General Limit Advice"
    },
    "general_limit_advice_text": {
        "TR": """
- **Minimum Limit (Hafif Hasar):** En düşük hasar senaryosuna göre belirlenir. Genellikle tavsiye edilmez çünkü büyük bir hasarda yetersiz kalabilir.
- **Orta Seviye Limit (Beklenen Hasar):** Ortalama bir deprem senaryosunda oluşabilecek kayıpları hedefler. Daha dengeli bir koruma ve prim sunar.
- **Maksimum Koruma (Ağır Hasar):** En kötü senaryoya göre tam koruma sağlamayı amaçlar, primi daha yüksek olabilir.
- **Sektör Tavsiyesi:** Genellikle 'Beklenen Hasar Limiti' ile 'Ağır Hasar Limiti' arasında bir değer, risk iştahınıza ve bütçenize göre seçilir. Bu, potansiyel kaybın %80-90'ını karşılamayı hedefler. Limitiniz çok düşükse, hasar sonrası poliçeniz yetersiz kalabilir. Çok yüksekse prim artar, ancak daha kapsamlı koruma sağlanır.
        """,
        "EN": """
- **Minimum Limit (Minor Damage):** Based on the lowest damage scenario. Generally not recommended as it may be insufficient in a major event.
- **Medium Level Limit (Expected Damage):** Targets losses in an average earthquake scenario. Offers a more balanced protection and premium.
- **Maximum Protection (Severe Damage):** Aims for full protection against the worst-case scenario, premium may be higher.
- **Sector Recommendation:** Typically, a value between the 'Expected Damage Limit' and 'Severe Damage Limit' is chosen based on your risk appetite and budget. This aims to cover 80-90% of the potential loss. If your limit is too low, your policy may be inadequate after a loss. If it's too high, the premium increases, but more comprehensive protection is provided.
        """
    },
    "table_col_label": {
        "TR": "Etiket",
        "EN": "Label"
    },
    "label_min_protection": {
        "TR": "🛡️ Min. Koruma", # Kalkan ikonu (Shield)
        "EN": "🛡️ Min. Protection"
    },
    "label_balanced_protection": {
        "TR": "⚖️ Denge", # Terazi ikonu (Balance Scale)
        "EN": "⚖️ Balanced"
    },
    "label_max_protection": {
        "TR": "🏆 Maks. Koruma", # Kupa ikonu (Trophy)
        "EN": "🏆 Max. Protection"
    },
    "filter_label_table_filters": {
        "TR": "Etikete Göre Filtrele",
        "EN": "Filter by Label"
    },
    "filter_label_damage_type_filters": {
        "TR": "Hasar Tipine Göre Filtrele",
        "EN": "Filter by Damage Type"
    },
    "filter_option_all": {
        "TR": "Tümü",
        "EN": "All"
    },
    "table_col_coverage_type": {
        "TR": "Teminat Türü",
        "EN": "Coverage Type"
    },
    "table_col_sum_insured": {
        "TR": "Bedel",
        "EN": "Sum Insured"
    },
    "table_col_rate_permille": {"TR": "Fiyat (%o)", "EN": "Rate (%o)"},
    "coverage_pd_combined": {"TR": "Yangın ", "EN": "Fire"}, # Zaten olabilir, kontrol edin
    "coverage_bi": {"TR": "Kar Kaybı", "EN": "Business Interruption"}, # Zaten olabilir
    "coverage_ec": {"TR": "Elektronik Cihaz", "EN": "Electronic Equipment"}, # Zaten olabilir
    "coverage_mk": {"TR": "Makine Kırılması", "EN": "Machinery Breakdown"}, # Zaten olabilir
    "current_entered_sums_header": {
        "TR": "Anlık Girilen Toplam Bedeller",
        "EN": "Currently Entered Total Sums"
    },
     "earthquake_zones_nav": {
        "TR": "🗺️ Deprem Bölgeleri", 
        "EN": "🗺️ Earthquake Zones"
    },
    "earthquake_zones_search": {
        "TR": "🗺️ Deprem Bölgeleri", 
        "EN": "🗺️ Earthquake Zones"
    },
    "coverage_car_ear": {"TR": "CAR/EAR", "EN": "CAR/EAR"},
    "coverage_cpm": {"TR": "İnşaat Makineleri (CPM)", "EN": "Construction Plant & Machinery (CPM)"},
    "coverage_cpe": {"TR": "Şantiye Tesisleri (CPE)", "EN": "Construction/Erection Site Equipment (CPE)"},
    "table_col_coverage_type": {"TR": "Teminat", "EN": "Coverage"}, # Zaten olabilir
    "table_col_sum_insured": {"TR": "Bedel", "EN": "Sum Insured"}, # Zaten olabilir
    "table_col_rate_permille": {"TR": "Fiyat (%o)", "EN": "Rate (%o)"}, # Zaten olabilir
    "table_col_premium": {"TR": "Prim", "EN": "Premium"}, # Zaten olabilir
    "total_overall": {"TR": "Toplam", "EN": "Total"}, # Zaten olabilir
    "results_table_header": {"TR": "Sonuç Tablosu", "EN": "Results Table"},
    "learn_earthquake_zone_button": {
        "TR": "Deprem Bölgelerini Öğren",
        "EN": "Learn Earthquake Zones"
    },
    "group_label_format": {"TR": "{group_char} Kümülü", "EN": "{group_char} Aggregate"},
    "current_entered_sums_raw_header": {"TR": "Anlık Girilen Toplam Bedel", "EN": "Current Entered Totals"},
    "total_entered_pd_sum_raw": {"TR": "Toplam PD Bedeli", "EN": "Total PD Sum"},
    "total_entered_bi_sum_raw": {"TR": "Toplam BI Bedeli", "EN": "Total BI Sum"},
    "total_entered_pd_sum": {"TR": "Toplam Girilen PD Bedeli", "EN": "Total Entered PD Sum"},
    "entered_sums_summary_header": {
        "TR": "Girilen Bedel Özeti",
        "EN": "Entered Sum Summary"
    },
    "location_group_cumulative_info": {
        "TR": "ℹ️ Kümül oluşturan adresleri aynı gruba atayınız.", 
        "EN": "ℹ️ Assign addresses that form an aggregate to the same group."
    },
    "select_province" : {
        "TR": "Lütfen il seçiniz",
        "EN": "Please select a province"
    },
    "select_district" : {
        "TR": "Lütfen ilçe seçiniz",
        "EN": "Please select a district"
    },
    "select_neighborhood" : {
        "TR": "Lütfen mahalle seçiniz",
        "EN": "Please select a neighborhood"
    },
    "select_village" : {
        "TR": "Lütfen köy seçiniz",
        "EN": "Please select a village"
    },
    "earthquake_zones_result": {
        "TR": "Deprem Bölgeleri Sonucu",
        "EN": "Earthquake Zones Result"
    },
    "earthquake_zone_explanation_header": {
    "TR": "Deprem Bölgesi Açıklaması:",
    "EN": "Earthquake Zone Explanation:"
    },
    "earthquake_zone_explanation_text": {
        "TR": """ 
    Türkiye'de yer bilimleri ve afet yönetimi standartlarına göre belirlenen Deprem Bölgeleri, 1’den 7’ye kadar numaralandırılmıştır. Bu numaralandırma, bölgenin sismik risk derecesini ifade eder:

    - **1. Bölge:** En yüksek deprem riski taşıyan alanlardır.
    - **7. Bölge:** En düşük deprem riski taşıyan alanlardır.

    Prim hesaplamalarında, bölgenin risk seviyesi sigorta primi üzerinde doğrudan etkili olup, daha yüksek riskli bölgelerde prim tutarı artış gösterecektir.
    """,
        "EN": """
    Earthquake Zones in Turkey, determined according to earth sciences and disaster management standards, are numbered from 1 to 7. This numbering indicates the seismic risk level of the region:

    - **Zone 1:** Areas with the highest earthquake risk.
    - **Zone 7:** Areas with the lowest earthquake risk.

    In premium calculations, the risk level of the zone directly affects the insurance premium, with higher-risk zones resulting in increased premium amounts.
    """
    },
    "no_data_found": { # Bu anahtar zaten eklenmiş olabilir, kontrol edin.
        "TR": "Seçilen kriterlere uygun veri bulunamadı.",
        "EN": "No data found for the selected criteria."
    },
    "start_selection": { # Bu anahtar zaten eklenmiş olabilir, kontrol edin.
        "TR": "Lütfen yukarıdan seçim yapmaya başlayınız.",
        "EN": "Please start by making selections above."
    },
    "table_col_rate_per_mille": {"TR": "Fiyat (%o)", "EN": "Rate (%o)"},
    "table_col_rate_per_mille_help": {"TR": "Prim / Teminat Bedeli * 1000", "EN": "Premium / Sum Insured * 1000"},
    "applied_pd_rate_label": {"TR": "Uygulanan Oran (PD Bazında)", "EN": "Applied Rate (PD Basis)"}, # Bu zaten olabilir, kontrol edin
    "summary_results_table_title": {"TR": "📊 İcmal Sonuç Tablosu", "EN": "📊 Summary Results Table"},
}