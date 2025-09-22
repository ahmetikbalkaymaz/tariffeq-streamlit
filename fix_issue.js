const https = require('https');
const fs = require('fs');

const apiKey = process.env.GEMINI_API_KEY;
const issueTitle = process.env.ISSUE_TITLE;
const issueBody = process.env.ISSUE_BODY;

const payload = JSON.stringify({
  contents: [{
    parts: [{
      text: `Sen bir yazılım geliştiricisisin. Bu issue için basit bir çözüm öner ve küçük bir kod örneği ver:
      
      Issue: "${issueTitle}"
      Açıklama: "${issueBody}"
      
      Sadece 2-3 satır kod veya README güncellemesi yap. Basit tut!`
    }]
  }]
});

const options = {
  hostname: 'generativelanguage.googleapis.com',
  path: `/v1beta/models/gemini-1.5-flash:generateContent?key=${apiKey}`,
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
        
        // Basit bir README güncellemesi yap
        const updateText = `\n## AI Güncellemesi\n\n**Issue #${process.env.ISSUE_NUMBER}:** ${issueTitle}\n\n**AI Önerisi:** ${aiResponse.substring(0, 200)}...\n\n*Son güncelleme: ${new Date().toLocaleString('tr-TR')}*\n`;
        
        if (fs.existsSync('README.md')) {
          fs.appendFileSync('README.md', updateText);
        } else {
          fs.writeFileSync('README.md', `# Project\n${updateText}`);
        }
        
        console.log('✅ README.md güncellendi!');
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
