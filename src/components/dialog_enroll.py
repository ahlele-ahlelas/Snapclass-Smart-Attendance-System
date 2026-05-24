import streamlit as st
from src.databse.db import enroll_student_to_subject
from src.databse.config import supabase

@st.dialog("Enroll in subject")

def enroll_subject_dialog():
    st.write("Enter subject code provided by your teacher to enroll")
    join_code = st.text_input("Subject Code",placeholder="e.g. CS101")
    
    if st.button(" Enroll now",type="primary",width="stretch"):
        if not join_code:
            st.warning("Please enter the subject code.",icon="⚠️")
        else:
            res = supabase.table("subject").select("subject_id,name,subject_code").eq("subject_code", join_code).execute()
            if res.data:
                subject = res.data[0]
                student_id = st.session_state.student_data["student_id"]
                check = supabase.table("subject_students").select("*").eq("student_id", student_id).eq("subject_id", subject["subject_id"]).execute()
                if check.data:
                    st.info("You are already enrolled in this subject.",icon="ℹ️")
                else:
                    enroll_student_to_subject(student_id, subject["subject_id"])
                    st.success(f"Successfully enrolled in {subject['name']}!",icon="✅")
                    st.rerun()
            else:
                st.error("Subject code not found. Please check and try again.",icon="❌")