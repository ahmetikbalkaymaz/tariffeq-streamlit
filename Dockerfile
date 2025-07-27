# Temel Python imajını belirleyin (Streamlit ile uyumlu bir versiyon seçin)
FROM python:3.9-slim

# apt-get komutlarının etkileşimli olmayan modda çalışmasını sağla
ENV DEBIAN_FRONTEND=noninteractive

# WeasyPrint için sistem bağımlılıklarını kurma
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    build-essential \
    libffi-dev \
    libcairo2 \
    libpango-1.0-0 \
    libpangocairo-1.0-0 \
    libgdk-pixbuf-2.0-0 \
    shared-mime-info && \
    rm -rf /var/lib/apt/lists/*

# Çalışma dizinini ayarlayın
WORKDIR /app

# === GÜNCELLENMİŞ VE DAHA SAĞLAM KOPYALAMA BÖLÜMÜ ===

# 1. Adım: Bağımlılıkları ayrı kopyalayarak Docker önbelleğinden faydalanın.
# Bu satırda bir değişiklik olmadığı sürece, pip install adımı tekrar çalıştırılmaz.

RUN mkdir -p logs
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# 2. Adım: Geriye kalan tüm proje dosyalarını kopyalayın.
# Bu komut, `.dockerignore` dosyasında belirtilmeyen HER ŞEYİ kopyalar.
# Yani `.streamlit`, `.devcontainer`, `files`, `assets` vb. tüm klasörleriniz dahil edilir.
COPY . .

# Streamlit uygulamasının çalışacağı portu belirtin
EXPOSE 80

ENV SENDER_EMAIL="ahmetkaymazyedek@gmail.com"
ENV SENDER_PASSWORD="onvf vlkz srlg bfhf"
ENV NOTIFICATION_EMAIL="tariffeq@gmail.com"

# Uygulamayı başlatma komutu
# 0.0.0.0 adresi, konteynerin dışarıdan erişilebilir olmasını sağlar.
CMD ["streamlit", "run", "home.py", "--server.port=80", "--server.address=0.0.0.0", "--server.enableCORS=false"]
