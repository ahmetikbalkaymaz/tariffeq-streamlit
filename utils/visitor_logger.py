# utils/visitor_logger.py (GELIŞTIRILMIŞ)
import streamlit as st
# YENİ: Streamlit'in dahili API'lerine erişim için farklı importlar kullanılıyor
from streamlit.runtime.scriptrunner import get_script_run_ctx
from streamlit.runtime import get_instance
from .email_notifier import notifier
import time
import os
import requests
from datetime import datetime

def get_session_id():
    """Geçerli kullanıcının oturum kimliğini alır."""
    try:
        ctx = get_script_run_ctx()
        if ctx:
            return ctx.session_id
    except Exception:
        pass
    return None

def get_client_ip():
    """Geçerli kullanıcının IP adresini döndürür."""
    session_id = get_session_id()
    if not session_id:
        return "Bilinmiyor"
    
    try:
        # Bu dahili bir API'dir ve gelecekteki Streamlit sürümlerinde değişebilir.
        session_info = get_instance()._session_mgr.get_session_info(session_id)
        if session_info:
            return session_info.client.ip
    except Exception:
        pass
    return "Bilinmiyor"

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
            user_agent = st.experimental_get_query_params().get('user_agent', [None])[0]
            
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
    session_id = get_session_id()
    if not session_id or 'visitor_log' not in st.session_state or session_id not in st.session_state.visitor_log:
        return

    log = st.session_state.visitor_log[session_id]
    if page_name in log['pages'] and 'duration' not in log['pages'][page_name]:
        duration = time.time() - log['pages'][page_name]['visit_time']
        log['pages'][page_name]['duration'] = round(duration)
        
        # Oturum özeti gönder (örneğin, belirli bir süre sonra veya tarayıcı kapandığında)
        # Bu kısım daha karmaşık bir mantık gerektirebilir. Şimdilik basit tutuyoruz.
        # notifier.send_session_summary(log['ip'], log['pages'])

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
    session_id = get_session_id()
    if not session_id:
        return

    if 'visitor_log' not in st.session_state:
        st.session_state.visitor_log = {}
    
    if session_id not in st.session_state.visitor_log:
        ip = get_client_ip()
        # User agent bilgisi daha karmaşık olduğu için şimdilik basitleştirildi.
        user_agent = "Bilinmiyor" 
        st.session_state.visitor_log[session_id] = {
            'ip': ip,
            'start_time': time.time(),
            'notified': True, # İlk bildirim gönderildi olarak işaretle
            'pages': {}
        }
        # İlk ziyaret bildirimi gönder
        notifier.send_visitor_notification(ip, page_name, user_agent)

    st.session_state.visitor_log[session_id]['pages'][page_name] = {
        'visit_time': time.time()
    }

def trigger_session_summary():
    """Manuel olarak session özetini tetikle"""
    send_session_summary()