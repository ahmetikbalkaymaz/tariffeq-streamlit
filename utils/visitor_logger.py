# utils/visitor_logger.py (GELIŞTIRILMIŞ)
import streamlit as st
import os
import requests
from datetime import datetime
import time
import json
from utils.email_notifier import notifier

def get_client_ip():
    """IP adresini almak için farklı yöntemler dene"""
    try:
        if 'user_ip' in st.session_state:
            return st.session_state.user_ip
        
        try:
            response = requests.get('https://api.ipify.org?format=text', timeout=3)
            if response.status_code == 200:
                ip = response.text.strip()
                st.session_state.user_ip = ip
                return ip
        except:
            pass
        
        if hasattr(st, 'context') and hasattr(st.context, 'headers'):
            headers = st.context.headers
            
            for header in ['x-forwarded-for', 'x-real-ip', 'cf-connecting-ip', 'x-client-ip']:
                if header in headers:
                    ip = headers[header].split(',')[0].strip()
                    if ip and ip != '127.0.0.1' and ip != 'localhost':
                        st.session_state.user_ip = ip
                        return ip
            
            user_agent = headers.get('user-agent', 'unknown')
            st.session_state.user_agent = user_agent
            
        return 'unknown'
        
    except Exception as e:
        return 'unknown'

def get_user_agent():
    """User agent bilgisini al"""
    try:
        if 'user_agent' in st.session_state:
            return st.session_state.user_agent
            
        if hasattr(st, 'context') and hasattr(st.context, 'headers'):
            user_agent = st.context.headers.get('user-agent', 'unknown')
            st.session_state.user_agent = user_agent
            return user_agent
            
        return 'unknown'
    except:
        return 'unknown'

def init_session_tracking():
    """Session tracking'i başlat"""
    if 'session_pages' not in st.session_state:
        st.session_state.session_pages = {}
        st.session_state.session_start_time = time.time()

def format_duration(seconds):
    """Süreyi formatla"""
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

def log_page_entry(page_name):
    """Sayfa girişini logla"""
    try:
        if not os.path.exists("logs"):
            os.makedirs("logs")
        
        init_session_tracking()
        
        page_key = f'page_entry_{page_name}'
        current_time = time.time()
        
        # Önceki sayfanın süresini hesapla ve kaydet
        for prev_page, prev_data in st.session_state.session_pages.items():
            if 'entry_time' in prev_data and 'duration' not in prev_data:
                duration = int(current_time - prev_data['entry_time'])
                if duration > 2:  # 2 saniyeden fazla kaldıysa kaydet
                    st.session_state.session_pages[prev_page]['duration'] = duration
                    
                    # Exit log'u yaz
                    log_file = f"logs/visitors_{datetime.now().strftime('%Y_%m')}.log"
                    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    ip = st.session_state.session_pages[prev_page]['ip']
                    
                    duration_str = format_duration(duration)
                    log_message = f"{timestamp} | IP: {ip} | Page: {prev_page} | Action: EXIT | Duration: {duration_str}\n"
                    
                    with open(log_file, "a", encoding="utf-8") as f:
                        f.write(log_message)
        
        # Bu sayfaya daha önce giriş yapıldı mı?
        if page_key not in st.session_state:
            
            ip = get_client_ip()
            user_agent = get_user_agent()
            
            # Session tracking'e ekle
            st.session_state.session_pages[page_name] = {
                'entry_time': current_time,
                'ip': ip,
                'user_agent': user_agent
            }
            
            # Giriş log'u yaz
            log_file = f"logs/visitors_{datetime.now().strftime('%Y_%m')}.log"
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            log_message = f"{timestamp} | IP: {ip} | Page: {page_name} | Action: ENTER\n"
            
            with open(log_file, "a", encoding="utf-8") as f:
                f.write(log_message)
            
            # İlk ziyaret bildirimi gönder (sadece session'ın ilk sayfası için)
            if 'notification_sent' not in st.session_state:
                success = notifier.send_visitor_notification(ip, page_name, user_agent)
                if success:
                    st.session_state.notification_sent = True
                    email_log = f"{timestamp} | IP: {ip} | EMAIL NOTIFICATION SENT\n"
                    with open(log_file, "a", encoding="utf-8") as f:
                        f.write(email_log)
            
            st.session_state[page_key] = True

    except Exception as e:
        pass

def log_page_exit(page_name):
    """Sayfa çıkışını logla"""
    try:
        if 'session_pages' in st.session_state and page_name in st.session_state.session_pages:
            page_data = st.session_state.session_pages[page_name]
            
            if 'entry_time' in page_data and 'duration' not in page_data:
                current_time = time.time()
                duration = int(current_time - page_data['entry_time'])
                
                if duration > 2:  # 2 saniyeden fazla kaldıysa logla
                    st.session_state.session_pages[page_name]['duration'] = duration
                    
                    # Exit log'u yaz
                    log_file = f"logs/visitors_{datetime.now().strftime('%Y_%m')}.log"
                    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    ip = page_data['ip']
                    
                    duration_str = format_duration(duration)
                    log_message = f"{timestamp} | IP: {ip} | Page: {page_name} | Action: EXIT | Duration: {duration_str}\n"
                    
                    with open(log_file, "a", encoding="utf-8") as f:
                        f.write(log_message)
    
    except Exception as e:
        pass

def send_session_summary():
    """Session özetini e-posta ile gönder"""
    try:
        if 'session_pages' in st.session_state and st.session_state.session_pages:
            
            # Son sayfanın süresini de hesapla
            current_time = time.time()
            for page, data in st.session_state.session_pages.items():
                if 'entry_time' in data and 'duration' not in data:
                    duration = int(current_time - data['entry_time'])
                    if duration > 2:
                        st.session_state.session_pages[page]['duration'] = duration
            
            # Sadece süresi olan sayfaları gönder
            pages_with_duration = {
                page: data for page, data in st.session_state.session_pages.items() 
                if 'duration' in data and data['duration'] > 2
            }
            
            if pages_with_duration:
                ip = next(iter(st.session_state.session_pages.values())).get('ip', 'unknown')
                success = notifier.send_session_summary(ip, pages_with_duration)
                
                if success:
                    # Log'a özet gönderildiğini yaz
                    log_file = f"logs/visitors_{datetime.now().strftime('%Y_%m')}.log"
                    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    log_message = f"{timestamp} | IP: {ip} | SESSION SUMMARY EMAIL SENT\n"
                    
                    with open(log_file, "a", encoding="utf-8") as f:
                        f.write(log_message)
    
    except Exception as e:
        pass

def track_page_visit(page_name):
    """Sayfa ziyaretini takip et"""
    log_page_entry(page_name)
    
    # Session bitiş kontrolü için JavaScript kodu ekle
    st.markdown(f"""
    <script>
        // Sayfa kapatılırken session özeti gönder
        window.addEventListener('beforeunload', function() {{
            // Streamlit session'ına session bitiş sinyali gönder
            // Bu tam olarak çalışmayabilir, alternatif yöntem gerekebilir
        }});
        
        // Sayfa değişikliğinde önceki sayfanın süresini hesapla
        if (sessionStorage.getItem('current_page') && 
            sessionStorage.getItem('current_page') !== '{page_name}') {{
            // Önceki sayfa süresi hesaplanacak
        }}
        sessionStorage.setItem('current_page', '{page_name}');
    </script>
    """, unsafe_allow_html=True)

def trigger_session_summary():
    """Manuel olarak session özetini tetikle"""
    send_session_summary()