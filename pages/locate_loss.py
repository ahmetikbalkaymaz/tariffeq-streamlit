import streamlit as st
import streamlit.components.v1 as components
import json
import os
import glob
from pathlib import Path
from pages.sidebar import sidebar  # Assuming you have a sidebar.py for sidebar content

# Sayfa yapılandırması
st.set_page_config(
    page_title="Yapay Zeka Destekli Hasar Paneli",
    page_icon="⚠️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

sidebar()
# JSON dosyalarını okuma fonksiyonu
@st.cache_data
def load_incidents_from_json_folder(folder_path="Hasarlar_v2 JSON Format"):
    """
    Belirtilen klasördeki tüm JSON dosyalarını okur ve birleştirir
    """
    all_incidents = []
    
    if not os.path.exists(folder_path):
        st.error(f"❌ '{folder_path}' klasörü bulunamadı!")
        return []
    
    json_files = glob.glob(os.path.join(folder_path, "*.json"))
    
    if not json_files:
        st.warning(f"⚠️ '{folder_path}' klasöründe JSON dosyası bulunamadı!")
        return []
    
    for json_file in json_files:
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                if isinstance(data, list):
                    all_incidents.extend(data)
                elif isinstance(data, dict):
                    all_incidents.append(data)
                    
        except json.JSONDecodeError as e:
            st.error(f"❌ '{os.path.basename(json_file)}' dosyası okunamadı: {str(e)}")
        except Exception as e:
            st.error(f"❌ '{os.path.basename(json_file)}' işlenirken hata: {str(e)}")
    
    return all_incidents

# Verileri yükle
incidents_data = load_incidents_from_json_folder()

if not incidents_data:
    st.error("⚠️ Gösterilecek veri bulunamadı. Lütfen JSON dosyalarınızı kontrol edin.")
    st.stop()

st.success(f"✅ {len(incidents_data)} adet hasar kaydı yüklendi.")

# HTML içeriği
html_content = f"""
<!DOCTYPE html>
<html lang="tr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Yapay Zeka Destekli Hasar Paneli</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" integrity="sha256-p4NxAoJBhIIN+hmNHrzRCf9tD/miZyoHS5obTRR9BMY=" crossorigin=""/>
    <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js" integrity="sha256-20nQCchB9co0qIjJZRGuk2/Z9VM+kNiyxNV1lvTlZBo=" crossorigin=""></script>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.1/css/all.min.css" integrity="sha512-DTOQO9RWCH3ppGqcWaEA1BIZOC6xxalwEsw9c2QQeAIftl+Vegovlnee1c9QX4TctnWMn13TZye+giMm8e2LwA==" crossorigin="anonymous" referrerpolicy="no-referrer" />

    <style>
        body {{
            font-family: 'Inter', sans-serif;
            background-color: #f0f2f5;
            overflow: hidden;
        }}
        .main-grid {{
            display: grid;
            grid-template-columns: 380px 1fr;
            grid-template-rows: 1fr;
            height: calc(100vh - 120px);
            gap: 1rem;
        }}
        #incident-list-container, #main-content-area {{
            overflow-y: auto;
            height: 100%;
        }}
        .active-item {{
            background-color: #eef2ff;
            border-left-color: #4f46e5;
            transform: translateX(-4px);
        }}
        #map {{
            height: 100%;
            width: 100%;
            border-radius: 0.75rem;
            z-index: 10;
        }}
        .leaflet-div-icon {{ background: transparent; border: none; }}
        .spinner {{ border: 4px solid rgba(0, 0, 0, 0.1); width: 36px; height: 36px; border-radius: 50%; border-left-color: #4f46e5; animation: spin 1s ease infinite; }}
        @keyframes spin {{ 0% {{ transform: rotate(0deg); }} 100% {{ transform: rotate(360deg); }} }}
        ::-webkit-scrollbar {{ width: 8px; }}
        ::-webkit-scrollbar-track {{ background: #f1f1f1; }}
        ::-webkit-scrollbar-thumb {{ background: #c5c5c5; border-radius: 4px; }}
        ::-webkit-scrollbar-thumb:hover {{ background: #a3a3a3; }}
        .chart-container {{ position: relative; height: 350px; width: 100%; }}
    </style>
</head>
<body class="text-gray-800">
    <div class="flex flex-col h-screen">
        <header class="bg-white shadow-sm w-full p-4 z-20 flex-shrink-0">
            <div class="max-w-screen-2xl mx-auto flex justify-between items-center">
                <div class="flex items-center space-x-3">
                      <svg class="w-8 h-8 text-indigo-600" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor">
                          <path stroke-linecap="round" stroke-linejoin="round" d="M12 9v3.75m-9.303 3.376c-.866 1.5.217 3.374 1.948 3.374h14.71c1.73 0 2.813-1.874 1.948-3.374L13.949 3.378c-.866-1.5-3.032-1.5-3.898 0L2.697 16.126ZM12 15.75h.007v.008H12v-.008Z" />
                      </svg>
                      <div>
                          <h1 class="text-2xl font-bold text-gray-800">Yapay Zeka Destekli Hasar Paneli</h1>
                          <p class="text-sm text-gray-500">Türkiye: Son 5 Yıllık Endüstriyel & Enerji Hasarları Analizi</p>
                      </div>
                </div>
            </div>
        </header>

        <div class="bg-white/80 backdrop-blur-sm w-full p-3 shadow-md z-10 flex-shrink-0">
            <div class="max-w-screen-2xl mx-auto flex flex-wrap gap-2 items-center">
                <p class="font-semibold text-gray-600 mr-2 w-full md:w-auto">Filtreler:</p>
                <input type="text" id="search-name-input" placeholder="Tesis Adı Ara..." class="w-full md:w-auto p-2 border rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500 text-sm">
                <input type="text" id="search-coord-input" placeholder="Koordinat Ara (örn: 41, 28.9)" class="w-full md:w-auto p-2 border rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500 text-sm">
                <select id="il-filter" class="w-full md:w-auto p-2 border rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500 text-sm"><option value="all">Tüm İller</option></select>
                <select id="sektor-filter" class="w-full md:w-auto p-2 border rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500 text-sm"><option value="all">Tüm Sektörler</option></select>
                <select id="olay-filter" class="w-full md:w-auto p-2 border rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500 text-sm"><option value="all">Tüm Olay Türleri</option></select>
                <select id="etki-filter" class="w-full md:w-auto p-2 border rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500 text-sm"><option value="all">Tüm Etki Seviyeleri</option><option value="Yüksek">Yüksek</option><option value="Orta">Orta</option><option value="Düşük">Düşük</option></select>
                <button id="reset-filters" class="w-full md:w-auto bg-gray-200 hover:bg-gray-300 text-gray-700 font-semibold py-2 px-4 rounded-md text-sm transition duration-150">Filtreleri Temizle</button>
                <div id="result-count" class="ml-auto text-sm font-medium text-gray-600 pr-2"></div>
            </div>
        </div>

        <main class="max-w-screen-2xl mx-auto w-full p-4 flex-grow">
            <div class="main-grid">
                <aside id="incident-list-container" class="bg-white p-2 rounded-lg shadow-sm">
                    <h2 class="text-lg font-bold mb-3 p-2 border-b">Hasar Listesi (En Yeni)</h2>
                    <div id="incident-list" class="space-y-1"></div>
                </aside>
                <div id="main-content-area">
                    <div id="details-panel" class="hidden bg-white p-6 rounded-lg shadow-lg"></div>
                    <div id="analysis-panel" class="grid grid-cols-1 xl:grid-cols-2 gap-4">
                        <div class="xl:col-span-2 h-[450px] bg-white rounded-lg shadow-lg p-4">
                             <h3 class="font-bold text-gray-700 text-lg mb-2">Hasar Konumları Haritası</h3>
                             <div id="map-container" class="w-full h-[calc(100%-40px)]"><div id="map"></div></div>
                        </div>
                        <div class="xl:col-span-2 bg-white rounded-lg shadow-lg p-4">
                            <div class="flex justify-between items-center mb-3">
                                <h3 class="font-bold text-gray-700 text-lg">Öne Çıkan Analizler</h3>
                            </div>
                            <div id="analysis-cards" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4"></div>
                        </div>
                        <div class="bg-white rounded-lg shadow-lg p-4">
                            <h3 class="font-semibold text-center mb-2 text-gray-600">Sektörlere Göre Hasar Sayısı (Top 10)</h3>
                            <div class="chart-container"><canvas id="sektorChart"></canvas></div>
                        </div>
                         <div class="bg-white rounded-lg shadow-lg p-4">
                            <h3 class="font-semibold text-center mb-2 text-gray-600">Aylara Göre Hasar Dağılımı</h3>
                            <div class="chart-container"><canvas id="aylikChart"></canvas></div>
                        </div>
                    </div>
                </div>
            </div>
        </main>
    </div>

    <script>
        document.addEventListener('DOMContentLoaded', function () {{
            
            const incidentsData = {json.dumps(incidents_data, ensure_ascii=False)};

            let map, markersLayer, polylinesLayer, sektorChart, aylikChart;
            let currentIncident = null;
            let currentFilteredData = incidentsData;
            
            // YENİ: Arama kutuları elements objesine eklendi
            const elements = {{ 
                ilFilter: document.getElementById('il-filter'), 
                sektorFilter: document.getElementById('sektor-filter'), 
                olayFilter: document.getElementById('olay-filter'), 
                etkiFilter: document.getElementById('etki-filter'), 
                incidentList: document.getElementById('incident-list'), 
                resultCount: document.getElementById('result-count'), 
                resetBtn: document.getElementById('reset-filters'), 
                detailsPanel: document.getElementById('details-panel'), 
                analysisPanel: document.getElementById('analysis-panel'), 
                mainContentArea: document.getElementById('main-content-area'), 
                mapContainer: document.getElementById('map-container'), 
                analysisCards: document.getElementById('analysis-cards'),
                searchNameInput: document.getElementById('search-name-input'),
                searchCoordInput: document.getElementById('search-coord-input')
            }};

            function init() {{ populateFilters(); initMap(); renderAll(incidentsData); addEventListeners(); }}

            function addEventListeners() {{
                // YENİ: Arama kutuları için olay dinleyiciler eklendi
                elements.searchNameInput.addEventListener('input', applyFilters);
                elements.searchCoordInput.addEventListener('input', applyFilters);
                elements.ilFilter.addEventListener('change', applyFilters);
                elements.sektorFilter.addEventListener('change', applyFilters);
                elements.olayFilter.addEventListener('change', applyFilters);
                elements.etkiFilter.addEventListener('change', applyFilters);
                elements.resetBtn.addEventListener('click', resetAllFilters);
                elements.incidentList.addEventListener('click', handleListClick);
            }}

            function renderAll(data) {{ renderIncidentList(data); updateAnalysis(data); updateMapMarkers(data); }}

            function populateFilters() {{
                const iller = [...new Set(incidentsData.map(item => item.il))].sort((a, b) => a.localeCompare(b, 'tr'));
                const sektorler = [...new Set(incidentsData.map(item => item.sektor.split(' / ')[0].trim()))].sort();
                const olaylar = [...new Set(incidentsData.map(item => item.olayTuru))].sort();
                iller.forEach(il => elements.ilFilter.innerHTML += `<option value="${{il}}">${{il}}</option>`);
                sektorler.forEach(sektor => elements.sektorFilter.innerHTML += `<option value="${{sektor}}">${{sektor}}</option>`);
                olaylar.forEach(olay => elements.olayFilter.innerHTML += `<option value="${{olay}}">${{olay}}</option>`);
            }}
            
            // YENİ: Tarihe göre sıralama eklendi
            function renderIncidentList(data) {{
                elements.incidentList.innerHTML = data.length === 0 ? '<p class="text-gray-500 text-center p-4">Filtre kriterlerine uygun sonuç bulunamadı.</p>' : '';
                if(data.length > 0) {{
                    // Tarihleri Date objesine çevirip sırala (yeniden eskiye)
                    data.sort((a, b) => {{
                        const dateA = new Date(a.tarih.split('.').reverse().join('-'));
                        const dateB = new Date(b.tarih.split('.').reverse().join('-'));
                        return dateB - dateA;
                    }});
                    
                    data.forEach(item => {{
                        const etkiRenk = {{ 'Yüksek': 'border-red-500', 'Orta': 'border-yellow-500', 'Düşük': 'border-green-500' }}[item.etkiSeviyesi] || 'border-gray-200';
                        const itemDiv = document.createElement('div');
                        itemDiv.className = `p-3 border-l-4 ${{etkiRenk}} cursor-pointer hover:bg-gray-100 transition duration-150 rounded-r-md`;
                        itemDiv.dataset.id = item.id;
                        itemDiv.innerHTML = `<div class="flex justify-between items-start"><p class="font-bold text-base text-gray-800">${{item.tesisAdi}}</p><span class="text-xs font-medium text-gray-500">${{item.tarih}}</span></div><p class="text-sm text-gray-600">${{item.il}}, ${{item.ilce}}</p><p class="text-xs text-gray-500 mt-1">${{item.olayTuru}}</p>`;
                        elements.incidentList.appendChild(itemDiv);
                    }});
                }}
                elements.resultCount.textContent = `${{data.length}} sonuç bulundu.`;
            }}

            function showDetails(incident) {{
                elements.analysisPanel.classList.add('hidden');
                elements.mapContainer.classList.add('hidden');
                const etkiBilgi = {{ 'Yüksek': {{ renk: 'red', ikon: 'fa-triangle-exclamation', metin: 'Yüksek Etki' }}, 'Orta': {{ renk: 'yellow', ikon: 'fa-circle-exclamation', metin: 'Orta Etki' }}, 'Düşük': {{ renk: 'green', ikon: 'fa-circle-info', metin: 'Düşük Etki' }} }}[incident.etkiSeviyesi];
                const dogrulamaText = incident.dogrulamaYontemi === 'A' ? 'Resmi kaynak/şirket açıklaması.' : 'Basın/harita servisleri.';
                let etkilenenTesisHTML = incident.etkilenenTesis ? `<div class="mt-4"><h4 class="font-bold text-red-700 flex items-center gap-2"><i class="fa-solid fa-link"></i> Teyitli Etkilenen Komşu Tesis</h4><p class="text-sm bg-red-50 p-3 rounded-lg mt-1 border border-red-200">${{incident.etkilenenTesis.ad}}</p></div>` : '';
                let potansiyelEtkilenenlerHTML = incident.potansiyelEtkilenenler ? `<div class="mt-4"><h4 class="font-bold text-sky-700 flex items-center gap-2"><i class="fa-solid fa-magnifying-glass-location"></i> Potansiyel Riskli Komşu Tesisler</h4><ul class="text-sm bg-sky-50 p-3 rounded-lg mt-1 border border-sky-200 space-y-1">${{incident.potansiyelEtkilenenler.map(p => `<li><strong>${{p.ad}}</strong> (${{p.sektor}})</li>`).join('')}}</ul></div>` : '';
                let kaynaklarHTML = incident.kaynaklar ? `<div class="mt-4"><h4 class="font-bold text-gray-700">Bilgi Kaynakları</h4><div class="flex flex-wrap gap-2 mt-2">${{Object.entries(incident.kaynaklar).map(([kaynak, link]) => `<a href="${{link}}" target="_blank" class="bg-gray-200 text-gray-700 text-xs font-semibold px-2.5 py-1 rounded-full hover:bg-indigo-100 hover:text-indigo-800 transition">${{kaynak}}</a>`).join('')}}</div></div>` : '';
                elements.detailsPanel.innerHTML = `<div class="grid grid-cols-1 md:grid-cols-3 gap-6"><div class="md:col-span-2"><div class="flex justify-between items-start relative"><button onclick="resetToAnalysisView()" class="absolute top-0 right-0 text-gray-500 hover:text-gray-800 font-bold p-2 text-2xl z-10">&times;</button><div><span class="inline-block px-3 py-1 text-sm font-semibold text-${{etkiBilgi.renk}}-800 bg-${{etkiBilgi.renk}}-100 rounded-full mb-2"><i class="fa-solid ${{etkiBilgi.ikon}} mr-2"></i>${{etkiBilgi.metin}}</span><h2 class="text-3xl font-bold text-gray-800">${{incident.tesisAdi}}</h2><p class="text-md text-gray-500 mt-1">${{incident.konum}}, ${{incident.ilce}}/${{incident.il}}</p></div></div><div class="grid grid-cols-2 gap-4 text-sm mt-6"><div class="bg-gray-50 p-3 rounded-lg"><p class="font-semibold text-gray-500">Tarih</p><p class="font-medium text-lg">${{incident.tarih}}</p></div><div class="bg-gray-50 p-3 rounded-lg"><p class="font-semibold text-gray-500">Olay Türü</p><p class="font-medium text-lg">${{incident.olayTuru}}</p></div><div class="bg-gray-50 p-3 rounded-lg"><p class="font-semibold text-gray-500">Sektör</p><p class="font-medium text-lg">${{incident.sektor}}</p></div><div class="bg-gray-50 p-3 rounded-lg"><p class="font-semibold text-gray-500">Doğruluk Oranı (%${{incident.dogrulukOrani}})</p><div class="w-full bg-gray-200 rounded-full h-2.5 mt-2"><div class="bg-indigo-600 h-2.5 rounded-full" style="width: ${{incident.dogrulukOrani}}%"></div></div><p class="text-xs text-right mt-1">${{dogrulamaText}}</p></div></div><div class="mt-4"><h4 class="font-bold text-gray-700">Olay Özeti</h4><p class="text-sm mt-1 bg-blue-50 p-3 rounded-lg border border-blue-200">${{incident.ozet}}</p></div><div class="mt-4"><h4 class="font-bold text-gray-700">Direkt Hasar Etkisi</h4><p class="text-sm mt-1">${{incident.etki}}</p></div>${{etkilenenTesisHTML}} ${{potansiyelEtkilenenlerHTML}}<div class="mt-4"><h4 class="font-bold text-gray-700">Haber Alıntıları</h4><ul class="list-disc list-inside text-sm space-y-1 pl-1 mt-1">${{incident.haberler.map(h => `<li>${{h}}</li>`).join('')}}</ul></div>${{kaynaklarHTML}}</div><div class="md:col-span-1 h-full min-h-[400px]"><div id="detail-map" class="w-full h-full rounded-lg shadow-md"></div></div></div>`;
                elements.detailsPanel.classList.remove('hidden');
                const detailMap = L.map('detail-map').setView([incident.lat, incident.lng], 15);
                L.tileLayer('https://{{s}}.basemaps.cartocdn.com/light_all/{{z}}/{{x}}/{{y}}{{r}}.png').addTo(detailMap);
                L.marker([incident.lat, incident.lng], {{ icon: createMapIcon(incident) }}).addTo(detailMap).bindPopup(`<b>${{incident.tesisAdi}}</b>`).openPopup();
                if (incident.etkilenenTesis) {{ L.marker([incident.etkilenenTesis.lat, incident.etkilenenTesis.lng], {{ icon: createMapIcon({{ olayTuru: 'Etkilenen', etkiSeviyesi: 'Yüksek' }}) }}).addTo(detailMap).bindPopup(`<b>Etkilenen:</b> ${{incident.etkilenenTesis.ad}}`); L.polyline([[incident.lat, incident.lng], [incident.etkilenenTesis.lat, incident.etkilenenTesis.lng]], {{ color: 'red', dashArray: '5, 10' }}).addTo(detailMap); }}
                if (incident.potansiyelEtkilenenler) {{ incident.potansiyelEtkilenenler.forEach(p => {{ L.marker([p.lat, p.lng], {{ icon: createMapIcon({{ olayTuru: 'Potansiyel', etkiSeviyesi: 'Potansiyel' }}) }}).addTo(detailMap).bindPopup(`<b>Potansiyel Risk:</b><br>${{p.ad}}`); L.polyline([[incident.lat, incident.lng], [p.lat, p.lng]], {{ color: '#0ea5e9', dashArray: '1, 5' }}).addTo(detailMap); }}); }}
            }}
            
            function updateAnalysis(data) {{
                const totalIncidents = data.length; const highImpactCount = data.filter(i => i.etkiSeviyesi === 'Yüksek').length; const mostFrequentIncident = Object.entries(countBy(data, 'olayTuru')).sort((a, b) => b[1] - a[1])[0] || ['-', 0]; const mostAffectedSector = Object.entries(countBy(data, 'sektor')).sort((a, b) => b[1] - a[1])[0] || ['-', 0];
                elements.analysisCards.innerHTML = `<div class="bg-blue-50 p-4 rounded-lg border border-blue-200"><p class="text-sm text-blue-700 font-semibold">Toplam Vaka</p><p class="text-3xl font-bold text-blue-900">${{totalIncidents}}</p></div><div class="bg-red-50 p-4 rounded-lg border border-red-200"><p class="text-sm text-red-700 font-semibold">Yüksek Etkili Vaka</p><p class="text-3xl font-bold text-red-900">${{highImpactCount}}</p></div><div class="bg-yellow-50 p-4 rounded-lg border border-yellow-200"><p class="text-sm text-yellow-700 font-semibold">En Sık Olay Türü</p><p class="text-xl font-bold text-yellow-900">${{mostFrequentIncident[0]}}</p></div><div class="bg-green-50 p-4 rounded-lg border border-green-200"><p class="text-sm text-green-700 font-semibold">En Riskli Sektör</p><p class="text-xl font-bold text-green-900">${{mostAffectedSector[0]}}</p></div>`;
                updateCharts(data);
            }}
            
            // YENİ: Filtreleme fonksiyonu arama kutularını içerecek şekilde güncellendi
            function applyFilters() {{ 
                const filters = {{ 
                    il: elements.ilFilter.value, 
                    sektor: elements.sektorFilter.value, 
                    olay: elements.olayFilter.value, 
                    etki: elements.etkiFilter.value, 
                    nameSearch: elements.searchNameInput.value.toLowerCase().trim(),
                    coordSearch: elements.searchCoordInput.value.trim()
                }}; 
                
                let [searchLat, searchLng] = [null, null];
                if (filters.coordSearch.includes(',')) {{
                    [searchLat, searchLng] = filters.coordSearch.split(',').map(s => s.trim());
                }} else if (filters.coordSearch) {{
                    searchLat = filters.coordSearch;
                }}
                
                currentFilteredData = incidentsData.filter(item => 
                    (filters.il === 'all' || item.il === filters.il) && 
                    (filters.sektor === 'all' || item.sektor.startsWith(filters.sektor)) && 
                    (filters.olay === 'all' || item.olayTuru === filters.olay) && 
                    (filters.etki === 'all' || item.etkiSeviyesi === filters.etki) &&
                    (filters.nameSearch === '' || item.tesisAdi.toLowerCase().includes(filters.nameSearch)) &&
                    (searchLat === null || String(item.lat).startsWith(searchLat)) &&
                    (searchLng === null || String(item.lng).startsWith(searchLng))
                ); 
                renderAll(currentFilteredData); 
                resetToAnalysisView(); 
            }}
            
            // YENİ: resetAllFilters fonksiyonuna arama kutularını temizleme eklendi
            function resetAllFilters() {{ 
                elements.ilFilter.value = 'all'; 
                elements.sektorFilter.value = 'all'; 
                elements.olayFilter.value = 'all'; 
                elements.etkiFilter.value = 'all'; 
                elements.searchNameInput.value = '';
                elements.searchCoordInput.value = '';
                applyFilters(); 
                map.setView([39.0, 35.0], 6); 
            }}
            
            window.resetToAnalysisView = function() {{ elements.detailsPanel.classList.add('hidden'); elements.analysisPanel.classList.remove('hidden'); elements.mapContainer.classList.remove('hidden'); currentIncident = null; document.querySelectorAll('.active-item').forEach(el => el.classList.remove('active-item')); if (map) map.invalidateSize(); }}

            function handleListClick(e) {{
                const itemDiv = e.target.closest('[data-id]');
                if (itemDiv) {{ const incidentId = parseInt(itemDiv.dataset.id); currentIncident = incidentsData.find(i => i.id === incidentId); document.querySelectorAll('.active-item').forEach(el => el.classList.remove('active-item')); itemDiv.classList.add('active-item'); itemDiv.scrollIntoView({{ behavior: 'smooth', block: 'center' }}); showDetails(currentIncident); if (map) map.flyTo([currentIncident.lat, currentIncident.lng], 14); }}
            }}
            
            function initMap() {{ map = L.map('map').setView([39.0, 35.0], 6); L.tileLayer('https://{{s}}.basemaps.cartocdn.com/light_all/{{z}}/{{x}}/{{y}}{{r}}.png', {{ attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> &copy; <a href="https://carto.com/attributions">CARTO</a>' }}).addTo(map); markersLayer = L.layerGroup().addTo(map); polylinesLayer = L.layerGroup().addTo(map); }}
            function createMapIcon(incident) {{ const icons = {{ 'Yangın': 'fa-fire', 'Patlama': 'fa-bomb', 'Kazan/Boiler': 'fa-temperature-three-quarters', 'Kimyasal': 'fa-flask-vial', 'Çökme': 'fa-house-crack', 'Kran': 'fa-helmet-safety', 'Etkilenen': 'fa-link', 'Potansiyel': 'fa-magnifying-glass' }}; const colors = {{ 'Yüksek': '#ef4444', 'Orta': '#f59e0b', 'Düşük': '#22c55e', 'Etkilenen': '#6b7280', 'Potansiyel': '#0ea5e9' }}; const iconClass = icons[incident.olayTuru.split(' ')[0].replace(/,/g, '')] || 'fa-circle-question'; const color = colors[incident.etkiSeviyesi] || '#6b7280'; return L.divIcon({{ html: `<div style="font-size: 20px; color: ${{color}}; text-shadow: 0 0 3px white;"><i class="fa-solid ${{iconClass}}"></i></div>`, className: 'leaflet-div-icon', iconSize: [24, 24], iconAnchor: [12, 12] }}); }}

            function updateMapMarkers(data) {{
                markersLayer.clearLayers(); polylinesLayer.clearLayers();
                data.forEach(item => {{
                    const marker = L.marker([item.lat, item.lng], {{ icon: createMapIcon(item) }}).addTo(markersLayer);
                    marker.bindPopup(`<b>${{item.tesisAdi}}</b><br>${{item.olayTuru}}`).on('click', () => handleListClick({{ target: document.querySelector(`[data-id="${{item.id}}"]`) }}));
                    if (item.etkilenenTesis) {{ const affectedMarker = L.marker([item.etkilenenTesis.lat, item.etkilenenTesis.lng], {{ icon: createMapIcon({{ olayTuru: 'Etkilenen', etkiSeviyesi: 'Etkilenen' }}) }}).addTo(markersLayer); affectedMarker.bindPopup(`<b>Etkilenen:</b><br>${{item.etkilenenTesis.ad}}`); L.polyline([[item.lat, item.lng], [item.etkilenenTesis.lat, item.etkilenenTesis.lng]], {{ color: 'red', dashArray: '5, 10' }}).addTo(polylinesLayer); }}
                }});
            }}

            function createOrUpdateChart(chartInstance, elementId, type, data, options) {{ if (chartInstance) {{ chartInstance.destroy(); }} const ctx = document.getElementById(elementId).getContext('2d'); return new Chart(ctx, {{ type, data, options }}); }}
            function updateCharts(data) {{
                const sektorData = Object.entries(countBy(data, 'sektor')).sort((a,b) => b[1] - a[1]).slice(0, 10);
                const ctxSektor = document.getElementById('sektorChart').getContext('2d');
                const gradientSektor = ctxSektor.createLinearGradient(0, 0, 0, 350);
                gradientSektor.addColorStop(0, 'rgba(79, 70, 229, 0.8)'); gradientSektor.addColorStop(1, 'rgba(129, 140, 248, 0.5)');
                sektorChart = createOrUpdateChart(sektorChart, 'sektorChart', 'bar', {{ labels: sektorData.map(d => d[0]), datasets: [{{ label: 'Hasar Sayısı', data: sektorData.map(d => d[1]), backgroundColor: gradientSektor, borderRadius: 4 }}] }}, {{ indexAxis: 'y', responsive: true, maintainAspectRatio: false, plugins: {{ legend: {{ display: false }} }}, scales: {{ x: {{ grid: {{ display: false }} }}, y: {{ grid: {{ display: false }} }} }} }});

                const aylikDataRaw = data.reduce((acc, item) => {{ const month = item.tarih.substring(3, 10); acc[month] = (acc[month] || 0) + 1; return acc; }}, {{}});
                const sortedAylikData = Object.entries(aylikDataRaw).sort((a, b) => {{ const [m1, y1] = a[0].split('.'); const [m2, y2] = b[0].split('.'); return new Date(y1, m1-1) - new Date(y2, m2-1); }});
                aylikChart = createOrUpdateChart(aylikChart, 'aylikChart', 'line', {{ labels: sortedAylikData.map(d => d[0]), datasets: [{{ label: 'Hasar Sayısı', data: sortedAylikData.map(d => d[1]), backgroundColor: 'rgba(22, 163, 74, 0.1)', borderColor: '#16a34a', tension: 0.3, fill: true, pointBackgroundColor: '#16a34a' }}] }}, {{ responsive: true, maintainAspectRatio: false, plugins: {{ legend: {{ display: false }} }}, scales: {{ x: {{ grid: {{ display: false }} }}, y: {{ grid: {{ display: false }} }} }} }});
            }}
            
            function countBy(arr, prop) {{ return arr.reduce((acc, item) => {{ const key = item[prop].split(' / ')[0].trim(); acc[key] = (acc[key] || 0) + 1; return acc; }}, {{}}); }}

            init();
        }});
    </script>
</body>
</html>
"""

# Streamlit'te HTML'i render etme
# Önceki kodunuzla aynı, yükseklik ve kaydırma ayarları
components.html(html_content, height=1000, scrolling=True)