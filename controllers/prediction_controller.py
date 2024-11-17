from flask import request, jsonify
import os
from services.prediction_service import PredictionService

class PredictionController:
    def __init__(self):
        self.prediction_service = PredictionService()

    def predict_image(self):
        if 'image' not in request.files:
            return jsonify({"error": "No image file provided"}), 400
        image_file = request.files['image']
        image_path = f"temp/{image_file.filename}"
        image_file.save(image_path)
        prediction = self.prediction_service.predict_new_image(image_path)
        os.remove(image_path)
        authorized = prediction != -1
        user = prediction if authorized else "unknown"
        return jsonify({"authorized": authorized, "user": str(user)})

    def predict_audio(self):
        if 'audio' not in request.files:
            return jsonify({"error": "No audio file provided"}), 400
        audio_file = request.files['audio']
        audio_path = f"temp/{audio_file.filename}"
        audio_file.save(audio_path)
        prediction = self.prediction_service.predict_new_audio(audio_path)
        os.remove(audio_path)
        authorized = prediction != -1
        user = prediction if authorized else "unknown"
        return jsonify({"authorized": authorized, "user": str(user)})

    def authenticate(self):
        if 'image' not in request.files or 'audio' not in request.files:
            return jsonify({"error": "No image or audio file provided"}), 400
        image_file = request.files['image']
        audio_file = request.files['audio']
        image_path = f"temp/{image_file.filename}"
        audio_path = f"temp/{audio_file.filename}"
        image_file.save(image_path)
        audio_file.save(audio_path)
        auth_result, user = self.prediction_service.authenticate_user(image_path, audio_path)
        os.remove(image_path)
        os.remove(audio_path)
        return jsonify({"authorized": auth_result, "user": user})
