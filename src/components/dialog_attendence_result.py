import streamlit as st
from src.databse.db import create_attendance
from src.databse.config import supabase

@st.dialog("Attendance Results")
def show_attendence_result(df,logs):
    st.write("Plese review the attendance results before confiming.")
    st.dataframe(df,hide_index=True,width='stretch')
    
    col1,col2 = st.columns(2)
    with col1:
        if st.button('Discard',width='stretch'):
            st.session_state.voice_attendence_results = None
            st.session_state.attendence_images = []
            st.rerun()
    with col2:
        if st.button('Confirm & Save',width='stretch',type="primary"):
            try:
                create_attendance(logs)
                st.toast("Attendance results saved successfully!",icon="✅")
                st.session_state.attendence_images = []
                st.session_state.voice_attendence_results = None
                st.rerun()
            except Exception as e:
                st.error(f"Sync failed: {e}",icon="❌")
def attendence_result_dialog(df,logs):
    st.write("Plese review the attendance results before confiming.")
    st.dataframe(df,hide_index=True,width='stretch')
    
    col1,col2 = st.columns(2)
    with col1:
        if st.button('Discard',width='stretch'):
            st.rerun()
    with col2:
        if st.button('Confirm & Save',width='stretch',type="primary"):
            try:
                create_attendance(logs)
                st.toast("Attendance results saved successfully!",icon="✅")
                st.session_state.attendence_images = []
                st.rerun()
            except Exception as e:
                st.error(f"Sync failed: {e}",icon="❌")
                
        
    
    