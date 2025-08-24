# utils/email_notifier.py
import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
import streamlit as st

class EmailNotifier:
    def __init__(self):
        # E-posta ayarları (environment variables'dan alın)
        self.smtp_server = "smtp.gmail.com"  # Gmail için
        self.smtp_port = 587
        self.sender_email = os.getenv("SENDER_EMAIL", "ahmetkaymazyedek@gmail.com")
        self.sender_password = os.getenv("SENDER_PASSWORD", "onvf vlkz srlg bfhf")
        self.notification_email = os.getenv("NOTIFICATION_EMAIL", "osmanfurkankaymaz@gmail.com")
    
    def send_visitor_notification(self, ip, page, user_agent=None):
        """İlk ziyaret bildirimi gönder"""
        try:
            subject = f"🔔 TariffEQ - Yeni Ziyaretçi: {ip}"
            
            body = f"""
            Merhaba,
            
            TariffEQ uygulamanıza yeni bir ziyaretçi girdi:
            
            📅 Tarih/Saat: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
            🌐 IP Adresi: {ip}
            📄 İlk Sayfa: {page}
            🖥️ Tarayıcı: {user_agent or 'Bilinmiyor'}
            
            Ziyaretçinin sayfa aktiviteleri takip edilecek ve özet bildirim gönderilecektir.
            
            Bu otomatik bir bildirimdir.
            
            İyi günler,
            TariffEQ Bildiri Sistemi
            """
            
            return self._send_email(subject, body)
            
        except Exception as e:
            print(f"İlk ziyaret e-postası gönderme hatası: {e}")
            return False
    
    def send_session_summary(self, ip, session_data):
        """Session özeti e-postası gönder"""
        try:
            total_duration = sum(data.get('duration', 0) for data in session_data.values())
            
            # Süreyi formatla
            def format_duration(seconds):
                if seconds < 60:
                    return f"{seconds}s"
                elif seconds < 3600:
                    minutes = seconds // 60
                    secs = seconds % 60
                    return f"{minutes}m {secs}s"
                else:
                    hours = seconds // 3600
                    minutes = (seconds % 3600) // 60
                    return f"{hours}h {minutes}m"
            
            subject = f"📊 TariffEQ - Ziyaret Özeti: {ip}"
            
            # Sayfa aktivitelerini listele
            page_activities = ""
            for page, data in session_data.items():
                if 'duration' in data:
                    page_activities += f"    • {page}: {format_duration(data['duration'])}\n"
                else:
                    page_activities += f"    • {page}: Aktif (devam ediyor)\n"
            
            body = f"""
            Merhaba,
            
            TariffEQ'da bir kullanıcı oturumu sona erdi:
            
            📅 Tarih/Saat: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
            🌐 IP Adresi: {ip}
            ⏱️ Toplam Süre: {format_duration(total_duration)}
            📄 Ziyaret Edilen Sayfalar:
            
{page_activities}
            
            🔍 Detaylar:
            • En uzun kalınan sayfa: {max(session_data.keys(), key=lambda x: session_data[x].get('duration', 0)) if session_data else 'Bilinmiyor'}
            • Sayfa sayısı: {len(session_data)}
            
            Bu otomatik bir özet bildirimidir.
            
            İyi günler,
            TariffEQ Bildiri Sistemi
            """
            
            return self._send_email(subject, body)
            
        except Exception as e:
            print(f"Session özeti e-postası gönderme hatası: {e}")
            return False

    def send_calculation_notification(self, ip, module_name, calculation_details):
        """Bir hesaplama yapıldığında bildirim gönderir."""
        try:
            subject = f"✅ TariffEQ - Hesaplama Yapıldı: {module_name}"

            # Detayları güzel bir şekilde formatla
            details_formatted = ""
            for key, value in calculation_details.items():
                details_formatted += f"    • {key}: {value}\n"

            body = f"""
            Merhaba,

            TariffEQ uygulamanızda yeni bir hesaplama gerçekleştirildi:

            📅 Tarih/Saat: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
            🌐 IP Adresi: {ip}
            🧮 Modül: {module_name}

            Hesaplama Detayları:
            {details_formatted}
            Bu otomatik bir bildirimdir.

            İyi günler,
            TariffEQ Bildiri Sistemi
            """

            return self._send_email(subject, body)

        except Exception as e:
            print(f"Hesaplama bildirimi e-postası gönderme hatası: {e}")
            return False
    
    def _send_email(self, subject, body):
        """E-posta gönderme ortak fonksiyonu"""
        try:
            # E-posta mesajını oluştur
            msg = MIMEMultipart()
            msg['From'] = self.sender_email
            msg['To'] = self.notification_email
            msg['Subject'] = subject
            
            msg.attach(MIMEText(body, 'plain', 'utf-8'))
            
            # E-postayı gönder
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.sender_email, self.sender_password)
                text = msg.as_string()
                server.sendmail(self.sender_email, self.notification_email, text)
            
            return True
            
        except Exception as e:
            print(f"E-posta gönderme hatası: {e}")
            return False

# Global notifier instance
notifier = EmailNotifier()