import time
from unicodedata import name
import streamlit as st
from src.components.subject_card import subject_card
from src.components.header import header_dashboard
from src.ui.base_layout import style_background_dashboard
from src.ui.base_layout import style_base_layout
from src.components.footer import footer_dashboard
from src.databse.db import check_teacher_exists, create_teacher, teacher_login,get_teacher_subjects,get_attendance_for_teacher
from src.components.dialog_create_subject import create_subject_dialog
from src.components.dialog_share_subject import share_subject_dialog
from src.components.dialog_photo_add import add_photos_dialog
from src.components.dialog_attendence_result import attendence_result_dialog
from src.components.dialog_voice_attendance import voice_attendence_dialog
import numpy as np
import pandas as pd
from datetime import datetime
from src.pipelines.face_pipeline import predict_attendence
from src.databse.config import supabase

def login_teacher(username, password):
    if not username or not password:
        return False
    teacher = teacher_login(username, password)
    if teacher:
        st.session_state.teacher_data = teacher
        st.session_state.teacher_login_state = 'logged_in'
        st.session_state.user_role = 'teacher'
        return True
    return False

def teacher_tab_take_attendance():
    teacher_id = st.session_state.teacher_data["teacher_id"]
    st.header("Take AI Attendance")
    
    if 'attendence_images' not in st.session_state:
        st.session_state.attendence_images = []
    subjects = get_teacher_subjects(teacher_id)
    if not subjects:
        st.warning("No subjects found. Please add a subject to take attendance.",icon="ℹ️")
        return
    
    subject_options = {f"{subject['name']} - {subject['subject_code']}": subject['subject_id'] for subject in subjects}
    col1,col2 = st.columns([3,1],vertical_alignment='bottom')
    with col1:
        selected_subject_label = st.selectbox("Select Subject", options=list(subject_options.keys()))
        
    with col2:
        if st.button('Add Images', type='primary', width='stretch', icon="📸"):
            add_photos_dialog()
    
    selected_subject_id = subject_options.get(selected_subject_label)
    st.divider()
    
    if st.session_state.attendence_images:
        st.header("Added Photos")
        gallery_cols = st.columns(4)
        
        for idx,img in enumerate(st.session_state.attendence_images):
            with gallery_cols[idx % 4]:
                st.image(img, width = 'stretch',caption=f"Photo {idx+1}")
    has_images = bool(st.session_state.attendence_images)            
    c1,c2,c3 = st.columns(3)
    with c1:
        if st.button("Clear all photos", type="tertiary", width="stretch", icon="🗑️",disabled=not has_images):
            st.session_state.attendence_images = []
            st.rerun()
    with c2:
        if st.button("Run face Analysis",type = "tertiary",width="stretch",icon="🤖",disabled=not has_images):
            with st.spinner("Analyzing photos, please wait..."):
                all_detected_faces = {}
                for idx,img in enumerate(st.session_state.attendence_images):
                    img_np = np.array(img.convert('RGB'))
                    detected,_,_ = predict_attendence(img_np)
                    
                    if detected:
                        for sid in detected.keys():
                            student_id = int(sid)
                            all_detected_faces.setdefault(student_id, []).append(f"Photo {idx+1}")
                            
                enrolled_res = supabase.table("subject_students").select("*,students(*)").eq("subject_id", selected_subject_id).execute()
                enrolled_students = enrolled_res.data
                if not enrolled_students:
                    st.warning("No students enrolled in this subject.",icon="⚠️")
                else:
                    results,attendence_to_log = [],[]
                    current_timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    
                    for node in enrolled_students:
                        student = node['students']
                        sources = all_detected_faces.get(int(student['student_id']), [])
                        is_present = len(sources)>0
                        results.append({
                            'Name':student['name'],
                            'ID':student['student_id'],
                            'Sources':", ".join(sources) if is_present else '-',
                            'Status': "Present" if is_present else "Absent" 
                        })
                        attendence_to_log.append({
                            "student_id": student['student_id'],
                            "subject_id": selected_subject_id,
                            "timestamp": current_timestamp,
                            "is_present": is_present
                        })
                attendence_result_dialog(pd.DataFrame(results),attendence_to_log)
    with c3:
        if st.button('Voice attendance',type='primary',width='stretch',icon="🎤"):
            voice_attendence_dialog(selected_subject_id)
                    
                

def teacher_tab_manage_subjects():
    teacher_id = st.session_state.teacher_data["teacher_id"]
    col1,col2 = st.columns(2)
    with col1:
        st.header("Manage Subjects",width="stretch")
    with col2:
        if st.button("Add Subject",type="primary",width="stretch",icon="➕"):
            create_subject_dialog(teacher_id)
            
    subjects = get_teacher_subjects(teacher_id)
    if subjects:
        for subject in subjects:
            stats=[
                ("👥","Total Students", subject["total_students"]),
                ("📅","Classes", subject["total_classes"])
            ]
        def share_button():
            if st.button(f"Share code: {subject['name']}",key = f"share_{subject['subject_code']}",icon="🔗"):
                share_subject_dialog(subject['name'],subject['subject_code'])
            st.space()
        
        subject_card(
            name = subject["name"],
            code = subject["subject_code"],
            section = subject["section"],
            stats = stats,
            footer_callback = share_button
        )
        
    else:
        st.info("No subjects found. Please add a subject.",icon="ℹ️")   
            
def teacher_tab_view_attendance():
    st.header("Attendance Records")
    teacher_id = st.session_state.teacher_data["teacher_id"]
    record = get_attendance_for_teacher(teacher_id)
    if not record:
        return
    data = []
    for r in record:
        ts = r.get("timestamp")
        data.append({
            'ts_group':ts.split(".")[0] if ts else None,
            'Time': datetime.fromisoformat(ts).strftime("%Y-%m-%d %H:%M:%p") if ts else None,
            'Subject':r.get("subject",{}).get("name"),
            'Subject Code':r.get("subject",{}).get("subject_code"),
            'is_present':bool(r.get("is_present",False))
        })        
        
    df = pd.DataFrame(data)
    summary = (
        df.groupby(['ts_group','Subject','Subject Code'])
        .agg(
            Present_Count = ('is_present', 'sum'),
            Total_Count = ('is_present', 'count')
        ).reset_index()
    )
    summary['Attendance Stats'] = (
        "👥" +summary['Present_Count'].astype(str) + "/" + summary['Total_Count'].astype(str)+'Students'
    )
    
    display_df = (summary.sort_values('ts_group',ascending=False)
                  .rename(columns={'ts_group':'Time'})
                  [['Time','Subject','Subject Code','Attendance Stats']]
                  )
    
    st.dataframe(display_df,hide_index=True,width='stretch')

def teacher_dashboard():
    teacher_data = st.session_state.teacher_data
    c1, c2 = st.columns([3, 2], gap='small')

    with c1:
        header_dashboard()

    with c2:
        st.subheader(f"""Welcome back!, {teacher_data['name']}""")
        if st.button("Logout", type="secondary", key="loginbackbtn", shortcut = "control+backspace",  width='stretch'):
            st.session_state.is_logged_in = False
            del st.session_state.teacher_data
            st.rerun()
    
    st.space()
    
    if 'current_teacher_tab' not in st.session_state:
        st.session_state.current_teacher_tab = 'take attendance'
        
    tab1,tab2,tab3 = st.columns(3)
    with tab1:
        type1 = "primary" if st.session_state.current_teacher_tab == 'take attendance' else "tertiary"
        if st.button("Take Attendance",type=type1,width="stretch",icon="📸"):
            st.session_state.current_teacher_tab = 'take attendance'
            st.rerun()
            
    with tab2:
        type2 = "primary" if st.session_state.current_teacher_tab == 'manage subjects' else "tertiary"
        if st.button("Manage Subjects",type=type2,width="stretch",icon="📚"):
            st.session_state.current_teacher_tab = 'manage subjects'
            st.rerun()
            
    with tab3:
        type3 = "primary" if st.session_state.current_teacher_tab == 'view attendance' else "tertiary"
        if st.button("View Attendance",type=type3,width="stretch",icon="📊"):
            st.session_state.current_teacher_tab = 'view attendance'
            st.rerun()
            
    st.divider()
    
    if st.session_state.current_teacher_tab == 'take attendance':
        teacher_tab_take_attendance()
    if st.session_state.current_teacher_tab == 'manage subjects':
        teacher_tab_manage_subjects()
    if st.session_state.current_teacher_tab == 'view attendance':
        teacher_tab_view_attendance()
        
    footer_dashboard()
    

def teacher_screen():
    style_background_dashboard()
    style_base_layout()

    if (
        'teacher_login_state' not in st.session_state
        or st.session_state.teacher_login_state == "login"
    ):
        teacher_screen_login()

    elif st.session_state.teacher_login_state == "register":
        teacher_screen_register()

    elif st.session_state.teacher_login_state == "logged_in":
        teacher_dashboard()

def register_teacher(teacher_username, teacher_password, teacher_password_confirm, teacher_name):
    if not teacher_username or not teacher_password or not teacher_password_confirm or not teacher_name:
        return False, "Please fill in all fields."

    if teacher_password != teacher_password_confirm:
        return False, "Passwords do not match."

    if check_teacher_exists(teacher_username):
        return False, "Username already exists. Please choose a different one."
    try:
        create_teacher(teacher_username, teacher_password, teacher_name)
        return True, "Teacher registered successfully. Please login now."
    except Exception as e:
        return False, f"An error occurred during registration: {str(e)}"
def teacher_screen_login():

    c1, c2 = st.columns([3, 2], gap='small')

    with c1:
        header_dashboard()

    with c2:
        if st.button(
            "← Go back to Home",
            type="secondary",
            key="loginbackbtn",
            shortcut = "control+backspace",
            width='stretch'
        ):
            st.session_state.login_state = None
            st.rerun()

    st.header("Login using Password")

    st.space()
    st.space()

    teacher_username = st.text_input(
        "Enter username",
        placeholder="ahlele"
    )

    teacher_password = st.text_input(
        "Enter password",
        type="password",
        placeholder="Enter Password"
    )

    st.divider()

    bt1, bt2 = st.columns(2)

    with bt1:
        if st.button('Login', width='stretch', type='primary'):
            if login_teacher(teacher_username, teacher_password):
                st.toast("Welcome back!",icon="👋")
                time.sleep(1)
                st.rerun()
            else:
                st.error("Invalid username or password. Please try again.",icon="❌")

    with bt2:
        if st.button(
            "Register Instead",
            width='stretch'
        ):
            st.session_state.teacher_login_state = 'register'
            st.rerun()

    footer_dashboard()


def teacher_screen_register():

    c1, c2 = st.columns([3, 2], gap='small')

    with c1:
        header_dashboard()

    with c2:
        if st.button(
            "← Go back to Home",
            type="secondary",
            key="registerbackbtn",
            width='stretch'
        ):
            st.session_state.login_state = None
            st.rerun()

    st.header("Register your teacher profile")

    st.space()
    st.space()

    teacher_username = st.text_input(
        "Enter username",
        placeholder="ahlele",
        key="reg_username"
    )

    teacher_name = st.text_input(
        "Enter your name",
        placeholder="Ahlele Tsegay"
    )

    teacher_password = st.text_input(
        "Enter password",
        type="password",
        placeholder="Enter Password",
        key="reg_password"
    )

    teacher_pass_confirm = st.text_input(
        "Confirm password",
        type="password",
        placeholder="Confirm Password"
    )

    st.divider()

    bt1, bt2 = st.columns(2)

    with bt1:
        if st.button('Register now',width='stretch',type='primary'):
            success, message =   register_teacher(teacher_username, teacher_password, teacher_pass_confirm, teacher_name)
            if success: 
                st.success(message)
                time.sleep(2)
                st.session_state.teacher_login_state = 'login'
                st.rerun()
            else:
                st.error(message)
    with bt2:
        if st.button(
            "Login Instead",
            width='stretch'
        ):
            st.session_state.teacher_login_state = 'login'
            st.rerun()

    footer_dashboard()