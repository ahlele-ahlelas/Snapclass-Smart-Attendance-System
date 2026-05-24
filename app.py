import streamlit as st

st.write("APP STARTING")
print("APP STARTING")

from src.screens.teacher_screen import teacher_screen
from src.screens.student_screen import student_screen
from src.screens.home_screen import home_screen
from src.components.dialog_auto_enroll import auto_enroll_dialog
from src.components.dialog_enroll import enroll_subject_dialog

def main():
    st.set_page_config(page_title="SnapClass - Smart Attendance System",
                    page_icon="logo.png", layout="centered")
    if 'login_state' not in st.session_state:
        st.session_state.login_state = None
        
    match st.session_state.login_state:
        case 'teacher':
            teacher_screen()
        case 'student':
            student_screen()
        case None:
            home_screen()
            
    join_code = st.query_params.get("join-code")
    if join_code:
        if st.session_state.get("is_logged_in") and st.session_state.get("user_role") == "student":
            auto_enroll_dialog(join_code)
        elif st.session_state.get("login_state") != "student":
            st.session_state["login_state"] = "student"
            st.rerun()
            

main()