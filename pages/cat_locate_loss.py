import streamlit as st
import streamlit.components.v1 as components
import os
from pages.sidebar import sidebar

st.set_page_config(layout="wide")


sidebar()

try:
    html_file_path = os.path.join(os.path.dirname(__file__), 'cat_loss.html')

    with open(html_file_path, 'r', encoding='utf-8') as f:
        html_content = f.read()

    components.html(html_content, height=900, scrolling=True)

except FileNotFoundError:
    st.error("cat_loss.html dosyası bulunamadı. Lütfen app.py ile aynı dizinde olduğundan emin olun.")
