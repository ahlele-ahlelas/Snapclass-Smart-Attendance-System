import streamlit as st
import base64

def header_home():
    logo_path = r"D:\Snapclass\d0ebd99fd87cae9bdca2acfe647bcbab_icon.webp"

    with open(logo_path, "rb") as image_file:
        encoded = base64.b64encode(image_file.read()).decode()

    st.markdown(f"""
        <div style="text-align:center;">
            <img src="data:image/webp;base64,{encoded}" width="100" style="border-radius: 25%;">
            <h1 style="color:#E0E3FF; margin-top:10px;">
                SnapClass
            </h1>
        </div>
    """, unsafe_allow_html=True)
    
def header_dashboard():
    logo_path = r"D:\Snapclass\d0ebd99fd87cae9bdca2acfe647bcbab_icon.webp"
    
    with open(logo_path, "rb") as image_file:
        encoded = base64.b64encode(image_file.read()).decode()
    
    st.markdown(f"""
        <div style="display:flex; align-items:center; gap: 15px; margin:0;">
            <img src="data:image/webp;base64,{encoded}" style="height: 85px; flex: 0 0 auto; border-radius:25%;">
            <h2 style="color:#5865F2; margin:0; line-height:1.1; white-space:nowrap;">
                Snap<br/>Class
            </h2>
        </div>
    """, unsafe_allow_html=True)