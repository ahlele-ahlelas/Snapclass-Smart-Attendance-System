import streamlit as st

# resemblyzer and librosa temporarily disabled — re-enable once ffmpeg/torch confirmed working on cloud
VOICE_ENABLED = False

def load_voice_encoder():
    return None

def get_voice_embedding(audio_file):
    st.error("Voice features are temporarily disabled during deployment testing.")
    return None

def identify_speaker(new_embedding, candidates_dict, threshold=0.65):
    return None, 0.0

def process_bulk_audio(audio_file, candidates_dict, threshold=0.65):
    st.error("Voice features are temporarily disabled during deployment testing.")
    return {}
