from flask import Flask, request, jsonify
from transformers import Wav2Vec2ForCTC, Wav2Vec2Processor
import torch
import librosa
import soundfile as sf
from textprocess import recibirjson
from flask_cors import CORS  # Import CORS
import time
import os

app = Flask(__name__)
CORS(app, resources={r"/transcribe": {"origins": "*"}})

model = None
processor = None

def load_model():
    global model, processor
    if model is None:
        model = Wav2Vec2ForCTC.from_pretrained("jonatasgrosman/wav2vec2-large-xlsr-53-spanish")
        model.load_state_dict(torch.load('./model.pth'))
        processor = Wav2Vec2Processor.from_pretrained("jonatasgrosman/wav2vec2-large-xlsr-53-spanish")

def save_audio(input_audio, transcription, sample_rate):
    if not os.path.exists('audios'):
        os.makedirs('audios')
    
    _, filename_suffix = recibirjson(transcription)
    
    filename = ''.join(e for e in filename_suffix if e.isalnum() or e.isspace()).replace(" ", "_") + '.wav'
    file_path = os.path.join('audios', filename)
    
    sf.write(file_path, input_audio, sample_rate)


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
    app.run(debug=True)