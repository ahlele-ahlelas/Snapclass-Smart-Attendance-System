import numpy as np
from deepface import DeepFace
from sklearn.svm import SVC
import streamlit as st
from src.databse.db import get_all_students

def get_face_embedding(image_np):
    try:
        results = DeepFace.represent(
            image_np,
            model_name="Facenet",
            enforce_detection=False,
            detector_backend="retinaface"
        )
        return [np.array(r["embedding"]) for r in results]
    except Exception:
        return []

def get_trained_model():
    X, y = [], []
    student_db = get_all_students()
    if not student_db:
        return None
    for student in student_db:
        embedding = student.get("face_embedding")
        if embedding:
            emb = np.array(embedding)
            emb = emb / (np.linalg.norm(emb) + 1e-10)
            X.append(emb.tolist())
            y.append(student["student_id"])
    if len(X) == 0:
        return 0
    clf = SVC(kernel='linear', probability=True, class_weight='balanced')
    try:
        clf.fit(X, y)
    except ValueError:
        pass
    return {'clf': clf, 'X': X, 'y': y}

def train_classifier():
    st.cache_resource.clear()
    return bool(get_trained_model())

def predict_attendence(class_image_np):
    encodings = get_face_embedding(class_image_np)
    detected_students = {}
    model_data = get_trained_model()
    if not model_data:
        return detected_students, {}, len(encodings)
    clf = model_data['clf']
    X_train = model_data['X']
    y_train = model_data['y']
    all_students = sorted(list(set(y_train)))
    # Normalise before comparing so Euclidean distance is in [0, 2] regardless of embedding scale
    # Same person ~<0.7, different person ~>1.0 after normalisation
    resemblance_threshold = 0.9
    for encoding in encodings:
        norm_enc = encoding / (np.linalg.norm(encoding) + 1e-10)
        if len(all_students) >= 2:
            predicted_id = clf.predict([norm_enc])[0]
        else:
            predicted_id = all_students[0]
        stored = np.array(X_train[y_train.index(predicted_id)])
        norm_stored = stored / (np.linalg.norm(stored) + 1e-10)
        best_match_score = np.linalg.norm(norm_stored - norm_enc)
        if best_match_score <= resemblance_threshold:
            detected_students[int(predicted_id)] = True
    return detected_students, model_data, len(encodings)
