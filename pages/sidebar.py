import streamlit as st
from translations import T 

def sidebar():

    with st.sidebar:
        st.image("assets/logo.png", width=1000) 
        st.page_link("home.py", label=T["home"][st.session_state.lang], icon="🏠")
        st.page_link("pages/calculate.py", label=T["calc"][st.session_state.lang]) 
        st.page_link("pages/earthquake_zones.py", label=T["earthquake_zones_nav"][st.session_state.lang]) 
        st.page_link("pages/information.py", label=T["information_page_nav"][st.session_state.lang]) # BİLGİLENDİRME SAYFASI LİNKİ
        st.page_link("pages/roadmap.py", label=T["roadmap_page_nav"][st.session_state.lang], icon="🚀") # YOL HARİTASI SAYFASI LİNKİ
        st.page_link("pages/locate_loss.py", label=T["locate_loss_page_nav"][st.session_state.lang], icon="📍")
        st.page_link("pages/cat_locate_loss.py", label=T["cat_locate_loss_page_nav"][st.session_state.lang], icon="🔥")
        st.page_link("pages/loss_analysis.py", label=T["loss_analysis_page_nav"][st.session_state.lang], icon="🔥")
        # st.page_link("pages/scenario_calculator_page.py", label=T["scenario_page_title"][st.session_state.lang], icon="📉") 
        st.markdown("---") 

        lang_options = ["TR", "EN"]
        if st.session_state.lang not in lang_options:
            st.session_state.lang = "TR" 

        current_lang_index = lang_options.index(st.session_state.lang)
        
        selected_lang_sidebar = st.radio(
            "Language / Dil", 
            options=lang_options, 
            index=current_lang_index, 
            key="sidebar_language_selector" 
        )

        if selected_lang_sidebar != st.session_state.lang:
            st.session_state.lang = selected_lang_sidebar
            st.rerun() 
        
        st.markdown("---") 
        st.markdown(f"<div class='sidebar-footer footer'>{T['footer'][st.session_state.lang]}</div>", unsafe_allow_html=True)