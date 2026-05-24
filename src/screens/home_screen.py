import streamlit as st
from src.components.header import header_home   
from src.ui.base_layout import style_background_home
from src.ui.base_layout import style_base_layout
from src.components.footer import footer_home

def home_screen():
    style_background_home()
    style_base_layout()
    
    header_home()
    col1, col2 = st.columns(2)
    with col2:
        st.header("I'm teacher")
        st.image(r"teacher.png",width=150)
        if st.button("Teacher Login ↗",type="primary"):
            st.session_state.login_state = 'teacher'
            st.rerun()
    with col1:
        st.header("I'm student")
        st.image(r"student.png",width=150)
        if st.button("Student Login ↗",type="primary"):
            st.session_state.login_state = 'student'
            st.rerun()
            
    footer_home()