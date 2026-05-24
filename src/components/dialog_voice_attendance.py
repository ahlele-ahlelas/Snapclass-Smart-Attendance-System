import streamlit as st
from src.databse.db import enroll_student_to_subject
from src.databse.config import supabase
from src.pipelines.voice_pipeline import process_bulk_audio
from src.components.dialog_attendence_result import show_attendence_result
from datetime import datetime
import pandas as pd

@st.dialog("Voice Attendance")
def voice_attendence_dialog(selected_subject_id):
    st.write('Record audio of students saying "I am Present" for attendance')
    audio_data = None
    audio_data = st.audio_input("Click to record audio",key="audio_input")
    if st.button("Analyze audio",width='stretch',type='primary'):
        with st.spinner("Analyzing audio for attendance..."):
            enrolled_res = supabase.table("subject_students").select("*,students(*)").eq("subject_id", selected_subject_id).execute()
            enrolled_students = enrolled_res.data
            if not enrolled_students:
                st.warning("No students enrolled in this subject.",icon="⚠️")
                return
            candidates_dict = {
                s['students']['student_id']: s['students']['voice_embedding']
                for s in enrolled_students if s['students']['voice_embedding'] is not None
            }
            if not candidates_dict:
                st.error("No enrolled students have voice data for attendance.",icon="❌")
                return
            
            audio_bytes = audio_data.read()
            detected_scores = process_bulk_audio(audio_bytes, candidates_dict)
            results,attendence_to_log = [],[]
            current_timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            for node in enrolled_students:
                student = node['students']
                score = detected_scores.get(int(student['student_id']), 0.0)
                is_present = bool(score>0.0)  # You can adjust the threshold as needed
                results.append({
                    'Name':student['name'],
                    'ID':student['student_id'],
                    'Sources':f"{score:.2f}" if is_present else '-',
                    'Status': "Present" if is_present else "Absent" 
                })
                attendence_to_log.append({
                    "student_id": student['student_id'],
                    "subject_id": selected_subject_id,
                    "timestamp": current_timestamp,
                    "is_present": is_present
                })
            st.session_state.voice_attendence_results = (pd.DataFrame(results),attendence_to_log)
        
    if st.session_state.get('voice_attendence_results'):
        st.divider()
        df_results,logs = st.session_state.voice_attendence_results
        show_attendence_result(df_results,logs)