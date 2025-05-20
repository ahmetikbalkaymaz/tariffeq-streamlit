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
    "calc": {"TR": "🚀 Hemen Hesapla", "EN": "🚀 Calculate Now"},

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
    "location_group_help": {"TR": "Aynı riziko adresindeki lokasyonları aynı gruba atayın.", "EN": "Assign locations at the same risk address to the same group."},
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
    "mk_mobile": {"TR": "Makine Kırılması Bedeli (Seyyar)", "EN": "Machinery Breakdown Sum Insured (Portable)"},
    "mk_mobile_help": {"TR": "Seyyar makineler için sigorta bedeli.", "EN": "Sum insured for portable machinery."},
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
    "entered_sums_summary_header": {"TR": "Girilen Bedel Özeti", "EN": "Entered Sums Summary"},
    "total_entered_pd_sum": {"TR": "Toplam Girilen PD Bedeli", "EN": "Total Entered PD Sum"},
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
}