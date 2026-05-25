import streamlit as st
import numpy as np
import io

try:
    from resemblyzer import VoiceEncoder, preprocess_wav
    import librosa
    _VOICE_AVAILABLE = True
except ImportError:
    _VOICE_AVAILABLE = False

@st.cache_resource
def load_voice_encoder():
    if not _VOICE_AVAILABLE:
        return None
    return VoiceEncoder()

def get_voice_embedding(audio_file):
    if not _VOICE_AVAILABLE:
        st.error("Voice recognition is not available in this environment.")
        return None
    try:
        encoder = load_voice_encoder()
        audio, sr = librosa.load(io.BytesIO(audio_file), sr=16000)
        wav = preprocess_wav(audio, sr)
        embedding = encoder.embed_utterance(wav)
        return embedding.tolist()
    except Exception as e:
        st.error(f"Error processing audio: {str(e)}")
        return None
    
def identify_speaker(new_embedding, candidates_dict, threshold=0.65):
    if new_embedding is None or not candidates_dict:
        return None,0.0
    
    best_sid = None #sid = student id
    best_score = -1.0
    
    for sid, stored_embedding in candidates_dict.items():
        if stored_embedding:
            similarity = np.dot(new_embedding, stored_embedding) / (np.linalg.norm(new_embedding) * np.linalg.norm(stored_embedding))
            if similarity > best_score:
                best_score = similarity
                best_sid = sid
    if best_score >= threshold:
        return best_sid, best_score
    
    return None, best_score

def process_bulk_audio(audio_file, candidates_dict, threshold=0.65):
    if not _VOICE_AVAILABLE:
        st.error("Voice recognition is not available in this environment.")
        return {}
    try:
        encoder = load_voice_encoder()
        audio, sr = librosa.load(io.BytesIO(audio_file), sr=16000)
        segments = librosa.effects.split(audio, top_db=30)
        identified_results = {}
        
        for start, end in segments:
            if (end-start)/sr < 0.5:
                continue
            segment_audio = audio[start:end]
            wav = preprocess_wav(segment_audio)
            embedding = encoder.embed_utterance(wav)
            
            sid, score = identify_speaker(embedding, candidates_dict, threshold)
            
            if sid:
                if sid not in identified_results or score > identified_results[sid]:
                    identified_results[sid] = score
        return identified_results
    except Exception as e:
        st.error(f"Error processing bulk audio: {str(e)}")
        return {}
    
            
    
    
        