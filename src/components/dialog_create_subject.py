import streamlit as st
from src.databse.db import create_subject

@st.dialog("Add new subject")

def create_subject_dialog(teacher_id):
    st.write("Enter subject details")
    subject_name = st.text_input("Subject Name",placeholder="e.g. Computer Science 101")
    subject_code = st.text_input("Subject Code",placeholder="e.g. CS101")
    subject_section = st.text_input("Section",placeholder="e.g. A")
    
    if st.button("Create Subject",type="primary",width="stretch"):
        if subject_code and subject_name and subject_section:
            try:
                create_subject(subject_name, subject_code, subject_section, teacher_id)
                st.toast("Subject created successfully!",icon="✅")
                st.rerun()
            except Exception as e:
                st.error(f"Failed to create subject: {e}",icon="❌")
        else:
            st.warning("Please fill in all fields.",icon="⚠️")