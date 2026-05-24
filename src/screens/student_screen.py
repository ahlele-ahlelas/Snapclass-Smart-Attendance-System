import time
import numpy as np
import streamlit as st
from src.components.header import header_dashboard
from src.ui.base_layout import style_background_dashboard
from src.ui.base_layout import style_base_layout
from src.components.footer import footer_dashboard
from PIL import Image
from src.pipelines.face_pipeline import predict_attendence,get_all_students,train_classifier,get_face_embedding
from src.pipelines.voice_pipeline import get_voice_embedding
from src.databse.db import create_student, create_attendance, check_student_exists,get_student_subjects,get_student_attendance,unenroll_student_from_subject 
from src.components.dialog_enroll import enroll_subject_dialog
from src.components.subject_card import subject_card

def student_dashboard():
    student_data = st.session_state.student_data
    student_id = student_data['student_id']
    c1, c2 = st.columns([3, 2], gap='small')

    with c1:
        header_dashboard()

    with c2:
        st.subheader(f"""Welcome back!, {student_data['name']}""")
        if st.button("Logout", type="secondary", key="loginbackbtn", shortcut = "control+backspace",  width='stretch'):
            st.session_state.is_logged_in = False
            del st.session_state.student_data
            st.rerun()
    
    st.space()
    c1,c2 = st.columns(2)
    with c1:
        st.header("Your enrolled subjects 📚")
    with c2:
        if st.button("Join new subject",type="primary",width="stretch",icon="➕"):
            enroll_subject_dialog()
            
    st.divider()
    with st.spinner("Loading your subjects..."):
        subjects = get_student_subjects(student_id)
        logs = get_student_attendance(student_id)
        
    stats_map = {}
    
    for log in logs:
        sid = log["subject_id"]
        if sid not in stats_map:
            stats_map[sid] = {"total_classes": 0, "attended": 0}
        stats_map[sid]["total_classes"] += 1
        if log.get('is_present'):
            stats_map[sid]["attended"] += 1
    
    cols = st.columns(2)
    for i,sub_node in enumerate(subjects):
        sub = sub_node["subject"]
        sid = sub["subject_id"]
        
        stats = stats_map.get(sid, {"total_classes": 0, "attended": 0})
        def unenroll_btn():
            if st.button("Unenroll from this course",type="tertiary",width="stretch",icon="🗑"):
                unenroll_student_from_subject(student_id, sid)
                st.toast(f"Unenrolled from {sub['name']}",icon="✅")
                st.rerun()
        with cols[i % 2]:
            subject_card(
                name = sub["name"],
                code = sub["subject_code"],
                section = sub["section"],
                stats = [
                    ("📅","Total Classes", stats["total_classes"]),
                    ("✅","Attended", stats["attended"])
                ],
                footer_callback=unenroll_btn
            )
def student_screen():
    style_background_dashboard()
    style_base_layout()
    
    if "student_data" in st.session_state:
        student_dashboard()
        return
    c1, c2 = st.columns([3, 2], gap='small')

    with c1:
        header_dashboard()

    with c2:
        if st.button("← Go back to Home",type="secondary",key="loginbackbtn",shortcut = "control+backspace",width='stretch'):
            st.session_state.login_state = None
            st.rerun()

    st.header("Login using FaceID",text_alignment="center")

    st.space()
    st.space()
    show_registration = False
    photo_source = st.camera_input("Position your face in center and take a picture to login")
    if photo_source:
        img = np.array(Image.open(photo_source))
        try:
            with st.spinner("AI is recognizing you..."):
                detected,all_ids,num_face = predict_attendence(img)
                if num_face == 0:
                    st.error("No face detected. Please try again.",icon="❌")
                elif num_face > 1:
                    st.error("Multiple faces detected. Please ensure only your face is visible and try again.",icon="❌")
                else:
                    if detected:
                        student_id = list(detected.keys())[0]
                        all_students = get_all_students()
                        student = next((s for s in all_students if s["student_id"] == student_id), None)
                        if student:
                            st.session_state.student_data = student
                            st.session_state.is_logged_in = True
                            st.session_state.user_role = 'student'
                            create_attendance(student_id)
                            st.toast(f"Welcome back, {student['name']}!",icon="👋")
                            time.sleep(1)
                            st.rerun()
                        else:
                            st.info("You might be a new user. Please register first.",icon="ℹ️")
                            show_registration = True
                    else:
                        st.info("You might be a new user. Please register first.",icon="ℹ️")
                        show_registration = True
        except Exception as e:
            st.error(f"Something went wrong: {e}", icon="❌")
        if show_registration:
            with st.container(border = True):
                st.header("Register your new profile")
                new_name = st.text_input("Enter your name", placeholder="Akash Kumar")
                new_username = st.text_input("Choose a username", placeholder="akash123")
                new_password = st.text_input("Set a password", type="password", placeholder="••••••••")
                new_password_confirm = st.text_input("Confirm password", type="password", placeholder="••••••••")

                st.subheader('Optional: Voice Enrollment')
                st.info("Enroll your voice for voice only attendence")

                audio_data = None

                try:
                    audio_data = st.audio_input('Record a short phrase like, I am Akash')
                except Exception:
                    st.error('Audio Data Failed')
                if st.button('Create Account',type='primary'):
                    if not new_name:
                        st.warning('Please enter your name!')
                    elif not new_username:
                        st.warning('Please choose a username!')
                    elif not new_password:
                        st.warning('Please set a password!')
                    elif new_password != new_password_confirm:
                        st.error('Passwords do not match.', icon="❌")
                    elif check_student_exists(new_username):
                        st.error('Username already taken. Please choose a different one.', icon="❌")
                    else:
                        with st.spinner("Creating your profile..."):
                            img = np.array(Image.open(photo_source))
                            encodings = get_face_embedding(img)
                            if encodings:
                                face_emb = encodings[0].tolist()
                                voice_emb = None
                                if audio_data:
                                    voice_emb = get_voice_embedding(audio_data.read())
                                response_data = create_student(new_name, new_username, new_password, face_embedding=face_emb, voice_embedding=voice_emb)
                                
                                if response_data:
                                    train_classifier()
                                    st.session_state.student_data = response_data
                                    st.session_state.is_logged_in = True
                                    st.session_state.user_role = 'student'
                                    st.toast(f"Welcome, {new_name}! Your profile has been created.",icon="👋")
                                    time.sleep(1)
                                    st.rerun()
                                else:
                                    st.error("Failed to save profile. Check your database connection and try again.",icon="❌")
                            else:
                                st.error("Face encoding failed. Please try again with a clearer photo.",icon="❌")
    if photo_source:
        np.array(Image.open(photo_source))
    footer_dashboard()