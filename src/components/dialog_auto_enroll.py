import streamlit as st
from src.databse.db import enroll_student_to_subject
from src.databse.config import supabase

@st.dialog("Quick Enrollment")

def auto_enroll_dialog(subject_code):
    student_id = st.session_state.student_data["student_id"]
    
    res = supabase.table("subject").select("subject_id,name").eq("subject_code", subject_code).execute()
    if not res.data:
        st.error("Invalid subject code. Please check and try again.",icon="❌")
        if st.button("Close"):
            st.query_params.clear()
            st.rerun()
        return
    subject = res.data[0]
    check = supabase.table("subject_students").select("*").eq("student_id", student_id).eq("subject_id", subject["subject_id"]).execute()
    if check.data:
        st.info(f"You are already enrolled in {subject['name']}.",icon="ℹ️")
        if st.button("Got it!"):
            st.query_params.clear()
            st.rerun()
        return
    
    st.markdown(f"Would you like to enroll in the subject: **{subject['name']}**?")
    
    col1,col2 = st.columns(2)
    with col1:
        if st.button("No thanks"):
            st.query_params.clear()
            st.rerun()
    with col2:
        if st.button("Yes enroll Now!",type="primary",width="stretch"):
            enroll_student_to_subject(student_id, subject["subject_id"])
            st.success(f"Successfully enrolled in {subject['name']}!",icon="✅")
            st.query_params.clear()
            st.rerun()