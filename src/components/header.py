import streamlit as st
import base64
from pathlib import Path

_LOGO = Path(__file__).parent.parent.parent / "d0ebd99fd87cae9bdca2acfe647bcbab_icon.webp"

def _encoded_logo():
    with open(_LOGO, "rb") as f:
        return base64.b64encode(f.read()).decode()

def header_home():
    encoded = _encoded_logo()

    st.markdown(f"""
        <div style="text-align:center;">
            <img src="data:image/webp;base64,{encoded}" width="100" style="border-radius: 25%;">
            <h1 style="color:#E0E3FF; margin-top:10px;">
                SnapClass
            </h1>
        </div>
    """, unsafe_allow_html=True)

def header_dashboard():
    encoded = _encoded_logo()
    
    st.markdown(f"""
        <div style="display:flex; align-items:center; gap: 15px; margin:0;">
            <img src="data:image/webp;base64,{encoded}" style="height: 85px; flex: 0 0 auto; border-radius:25%;">
            <h2 style="color:#5865F2; margin:0; line-height:1.1; white-space:nowrap;">
                Snap<br/>Class
            </h2>
        </div>
    """, unsafe_allow_html=True)