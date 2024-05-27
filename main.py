from flask import Flask, request, jsonify
from transformers import Wav2Vec2ForCTC, Wav2Vec2Processor
import torch
import librosa
import soundfile as sf
from textprocess import recibirjson
from flask_cors import CORS  # Import CORS
import time
from datetime import datetime 
import io
import os


from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload, MediaIoBaseDownload


app = Flask(__name__)
CORS(app, resources={r"/transcribe": {"origins": "*"}})

model = None
processor = None

def get_drive_service():
    SCOPES = ['https://www.googleapis.com/auth/drive']
    SERVICE_ACCOUNT_FILE = 'credentials.json'  # Reemplaza con la ruta a tu archivo de credenciales

    credentials = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES)

    service = build('drive', 'v3', credentials=credentials)
    return service


def upload_to_drive(file_buffer, file_name):
    drive_service = get_drive_service()

    file_metadata = {
        'name': file_name,
        'parents': ['1VUSPr0foTTpTyA8kf2GUtni7Fqp9LgZm']  # Reemplaza con el ID de la carpeta en Google Drive
    }
    media = MediaIoBaseUpload(file_buffer, mimetype='audio/wav')

    file = drive_service.files().create(
        body=file_metadata,
        media_body=media,
        fields='id'
    ).execute()

    print(f"File ID: {file.get('id')}")

def load_model():
    global model, processor
    if model is None:
        model = Wav2Vec2ForCTC.from_pretrained("jonatasgrosman/wav2vec2-large-xlsr-53-spanish")
        model.load_state_dict(torch.load('./model.pth'), strict = False)
        processor = Wav2Vec2Processor.from_pretrained("jonatasgrosman/wav2vec2-large-xlsr-53-spanish")

def save_audio(input_audio, transcription, sample_rate):
   
    _, filename_suffix = recibirjson(transcription)
    
    current_date = datetime.now().strftime("%Y%m%d")
    
    filename = ''.join(e for e in filename_suffix if e.isalnum() or e.isspace()).replace(" ", "_") + f'_{current_date}.wav'
    file_buffer = io.BytesIO()
    sf.write(file_buffer, input_audio, sample_rate, format='wav')
    file_buffer.seek(0)
    
    # Subir a Google Drive
    upload_to_drive(file_buffer, filename)

def download_file(file_id):
    drive_service = get_drive_service()
    
    file_info = drive_service.files().get(fileId=file_id, fields='name').execute()
    file_name = file_info.get('name')

    current_directory = os.path.dirname(os.path.abspath(__file__))
    destination = os.path.join(current_directory, file_name)

    request = drive_service.files().get_media(fileId=file_id)
    
    with open(destination, 'wb') as f:
        downloader = MediaIoBaseDownload(f, request)

@app.route('/transcribe', methods=['POST'])
def transcribe():
    load_model()
    audio_file = request.files['audio']
    
    input_audio, sample_rate = librosa.load(audio_file, sr=16000)
    inputs = processor(input_audio, sampling_rate=16000, return_tensors="pt", padding=True)
    
    with torch.no_grad():
        logits = model(inputs.input_values, attention_mask=inputs.attention_mask).logits
        
    predicted_ids = torch.argmax(logits, dim=-1)
    predicted_sentences = processor.batch_decode(predicted_ids)
    transcription = predicted_sentences[0]
    print(transcription)
    
    save_audio(input_audio, transcription, sample_rate)

    a , b = recibirjson(transcription)

    return jsonify({"transcription": a})

if __name__ == '__main__':
    file_id= '1uHWfcSbjckyu8DYLoEuXB4Gg6hYFWtaU'
    download_file(file_id)
    app.run(debug=True)
