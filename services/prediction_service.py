# services/prediction_service.py

import os
import cv2 as cv
import numpy as np
import tensorflow as tf
import subprocess
import soundfile as sf
import librosa
from models.model_loader import ModelLoader
from deep_speaker.constants import SAMPLE_RATE, NUM_FRAMES
from deep_speaker.audio import read_mfcc
from deep_speaker.batcher import sample_from_mfcc

class PredictionService:
    def __init__(self):
        self.model_loader = ModelLoader()
        self.model_loaded, self.encoder, self.audio_model_nn, self.label_encoder = self.model_loader.load_models()
        self.embedder = self.model_loader.get_embedder()
        self.detector = self.model_loader.get_detector()
        self.deep_speaker_model = self.model_loader.get_audio_embedder()

    def get_embedding(self, face_img):
        face_img = face_img.astype('float32')
        face_img = np.expand_dims(face_img, axis=0)
        yhat = self.embedder.embeddings(face_img)
        return yhat[0]

    def predict_new_image(self, image_path):
        t_im = cv.imread(image_path)
        t_im = cv.cvtColor(t_im, cv.COLOR_BGR2RGB)
        detection = self.detector.detect_faces(t_im)
        if detection:
            x, y, w, h = detection[0]['box']
            t_im = t_im[y:y + h, x:x + w]
            t_im = cv.resize(t_im, (160, 160))
            test_im = self.get_embedding(t_im)
            test_im = [test_im]
            probs = self.model_loaded.predict_proba(test_im)[0]
            threshold = 0.7
            if max(probs) < threshold:
                return -1
            else:
                ypreds = self.model_loaded.predict(test_im)
                return ypreds
        else:
            return "Aucune face détectée"

    def extract_audio_embedding(self, audio_file):
        # Charger l'audio et convertir en MFCC
        audio, sr = librosa.load(audio_file, sr=SAMPLE_RATE, mono=True)
        audio = np.reshape(audio, (-1,))
        audio = audio[:16000]  # Garder seulement la première seconde
        
        # Extraire les MFCC et obtenir les embeddings avec DeepSpeaker
        mfcc = sample_from_mfcc(read_mfcc(audio_file, SAMPLE_RATE), NUM_FRAMES)
        embeddings = self.deep_speaker_model.m.predict(np.expand_dims(mfcc, axis=0))
        
        return embeddings

    def predict_new_audio(self, audio_file):
        new_embedding = self.extract_audio_embedding(audio_file)
        probs = self.audio_model_nn.predict(new_embedding.reshape(1, -1))[0]
        threshold = 0.8
        if max(probs) < threshold:
            return -1
        else:
            predicted_class = np.argmax(probs)
            predicted_label = self.label_encoder.inverse_transform([predicted_class])[0]
            return predicted_class

    def authenticate_user(self, image_path, audio_path):
        image_prediction = self.predict_new_image(image_path)
        audio_prediction = self.predict_new_audio(audio_path)
        if image_prediction == -1 or audio_prediction == -1:
            return False, "unknown"
        elif image_prediction == audio_prediction:
            if image_prediction == 1:
                return True, "Ayoub El Maalmi"
            else:
                return True, "Amine Hmidani Filali"
        else:
            return False, "incoherence between image and audio"
