import streamlit as st
from src.databse.db import enroll_student_to_subject
from src.databse.config import supabase
from PIL import Image
@st.dialog("Capture or upload photos for attendance")
def add_photos_dialog():
    st.write("Add photos for attendance")
    
    if 'photo_tab' not in st.session_state:
        st.session_state.photo_tab = 'camera'
        
    t1,t2 = st.columns(2)
    with t1:
        type_camera = "primary" if st.session_state.photo_tab == 'camera' else "tertiary"
        if st.button("Use Camera", type=type_camera, width="stretch", icon="📷"):
            st.session_state.photo_tab = 'camera'
            st.rerun()
    with t2:
        type_upload = "primary" if st.session_state.photo_tab == 'upload' else "tertiary"
        if st.button("Upload Photos", type=type_upload, width="stretch", icon="📁"):
            st.session_state.photo_tab = 'upload'
            st.rerun()
            
    if st.session_state.photo_tab == 'camera':
        cam_photo = st.camera_input("Take a photo",key="camera_input")
        if cam_photo:
            st.session_state.attendence_images.append(Image.open(cam_photo))
            st.toast("Photo captured!",icon="✅")
            st.rerun()
            
    if st.session_state.photo_tab == 'upload':
        uploaded_photos = st.file_uploader("Upload photos", accept_multiple_files=True, type=["jpg", "jpeg", "png"],key="upload_input")
        if uploaded_photos:
            for photo in uploaded_photos:
                st.session_state.attendence_images.append(Image.open(photo))
            st.toast(f"{len(uploaded_photos)} photos uploaded successfully!",icon="✅")
            st.rerun()
    st.divider()
    if st.button("Done", type="primary", width="stretch"):
        st.session_state.attendence_images = []
        st.toast("Photos added for attendance!",icon="✅")
        st.rerun()