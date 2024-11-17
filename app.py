from flask import Flask
import os
from controllers.prediction_controller import PredictionController
from flask_cors import CORS


os.environ['TFHUB_CACHE_DIR'] = './tfhub_modules'


app = Flask(__name__)
CORS(app)
controller = PredictionController()

# Définir les routes
app.add_url_rule('/predict_image', 'predict_image', controller.predict_image, methods=['POST'])
app.add_url_rule('/predict_audio', 'predict_audio', controller.predict_audio, methods=['POST'])
app.add_url_rule('/authenticate', 'authenticate', controller.authenticate, methods=['POST'])


if __name__ == '__main__':
    os.makedirs('temp', exist_ok=True)
    app.run(debug=True)
