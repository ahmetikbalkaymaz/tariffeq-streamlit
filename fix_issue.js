const https = require('https');
const fs = require('fs');

const apiKey = process.env.GEMINI_API_KEY;
const issueTitle = process.env.ISSUE_TITLE;
const issueBody = process.env.ISSUE_BODY;

const payload = JSON.stringify({
  contents: [{
    parts: [{
      text: `Sen sigorta matematik uzmanı ve Python/Streamlit developer'sın. Bu sigorta hesaplama uygulamasını geliştiriyorsun.

      Issue: "${issueTitle}"
      Açıklama: "${issueBody}"
      
      SİGORTA HESAPLAMA UZMANI OLARAK GÖREV:
      1. Sigorta matematik formüllerini doğru uygula
      2. Aktüerya hesaplamalarını implement et
      3. Professional Streamlit UI oluştur
      4. Risk analizi ve premium calculations
      
      STREAMLIT SPECIFIC:
      - st.sidebar, st.columns ile professional layout
      - st.cache_data ile performance optimization
      - Interactive charts sigorta verisi için
      - Forms ve validation sigorta parametreleri için
      - Export functionality raporlar için
      
      SİGORTA DOMAIN:
      - Life/Health/Property insurance calculations
      - Premium, reserve, solvency hesaplamaları
      - Risk modeling ve analysis
      - Regulatory compliance hesapları
      
      TAM ÇÖZÜMİ IMPLEMENTATION ET!
      Bu küçük patch değil, complete sigorta modülü olsun!`
    }]
  }]
});

const options = {
  hostname: 'generativelanguage.googleapis.com',
  path: `/v1beta/models/gemini-2.5-pro:generateContent?key=${apiKey}`,
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'Content-Length': payload.length
  },
  timeout: 30000
};

console.log('🌐 Doğrudan API çağrısı yapılıyor...');

const req = https.request(options, (res) => {
  let data = '';
  res.on('data', (chunk) => data += chunk);
  res.on('end', () => {
    try {
      const response = JSON.parse(data);
      if (response.candidates && response.candidates[0]) {
        const aiResponse = response.candidates[0].parts[0].text;
        console.log('🏦 Sigorta AI Analizi:', aiResponse.substring(0, 500) + '...');
        
        // Basit README güncellemesi - AI'ın kendi kod yazmasını bekle
        const readmeUpdate = `
## 🏦 AI Sigorta Geliştirmesi

### Issue #${process.env.ISSUE_NUMBER}: ${issueTitle}

**Tarih:** ${new Date().toLocaleString('tr-TR')}
**Durum:** AI-Powered Insurance Development

#### 📋 Issue Detayları:
${issueBody}

#### 🤖 AI Analizi:
${aiResponse.substring(0, 1000)}

---
*Bu analiz Gemini 2.5 Pro tarafından sigorta expertise ile yapılmıştır.*

`;
        
        if (fs.existsSync('README.md')) {
          fs.appendFileSync('README.md', readmeUpdate);
        } else {
          fs.writeFileSync('README.md', `# Sigorta Hesaplama Uygulaması\n\n${readmeUpdate}`);
        }
        
        console.log('✅ README.md güncellendi - AI Analysis logged');
        process.exit(0);
      } else {
        console.log('❌ API yanıtı boş');
        process.exit(1);
      }
    } catch (e) {
      console.log('❌ JSON parse hatası:', e.message);
      process.exit(1);
    }
  });
});

req.on('error', (e) => {
  console.log('❌ API hatası:', e.message);
  process.exit(1);
});

req.on('timeout', () => {
  console.log('❌ API timeout');
  req.destroy();
  process.exit(1);
});

req.write(payload);
req.end();
