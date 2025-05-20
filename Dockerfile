# Temel Python imajını belirleyin (Streamlit ile uyumlu bir versiyon seçin)
FROM python:3.9-slim

# Çalışma dizinini ayarlayın
WORKDIR /app

# Bağımlılık dosyasını kopyalayın ve kurun
COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Uygulama dosyalarını çalışma dizinine kopyalayın
# .dockerignore dosyası kullanarak gereksiz dosyaların kopyalanmasını engelleyebilirsiniz
COPY . .

# Streamlit uygulamasının çalışacağı portu belirtin (varsayılan 8501)
EXPOSE 80

# Uygulamayı başlatma komutu
# --server.enableCORS=false ve --server.enableXsrfProtection=false ayarları bazı ortamlarda gerekebilir,
# ancak genellikle varsayılanlar yeterlidir.
# 0.0.0.0 adresi, konteynerin dışarıdan erişilebilir olmasını sağlar.
CMD ["streamlit", "run", "home.py", "--server.port=80", "--server.address=0.0.0.0", "--server.enableCORS=false"]
