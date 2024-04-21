from flask import Flask, request, jsonify
from transformers import Wav2Vec2ForCTC, Wav2Vec2Processor
import torch
import librosa
from textprocess import recibirjson
from flask_cors import CORS  # Import CORS
import time


app = Flask(__name__)
CORS(app, resources={r"/transcribe": {"origins": "http://localhost:3000"}})

model = Wav2Vec2ForCTC.from_pretrained("jonatasgrosman/wav2vec2-large-xlsr-53-spanish")
model.load_state_dict(torch.load('./model.pth'))
processor = Wav2Vec2Processor.from_pretrained("jonatasgrosman/wav2vec2-large-xlsr-53-spanish")

@app.route('/transcribe', methods=['POST', 'GET'])
def transcribe():
    audio = request.files['audio'] # RECIBO DEL FRONT ( POR COMANDO UN WAV)

    input_audio,_   = librosa.load(audio, sr=16000)
    inputs = processor(input_audio, sampling_rate=16_000, return_tensors="pt", padding=True)

    start_time = time.time() # Inicia la medición del tiempo

    with torch.no_grad():
        logits = model(inputs.input_values, attention_mask=inputs.attention_mask).logits
    predicted_ids = torch.argmax(logits, dim=-1)
    predicted_sentences = processor.batch_decode(predicted_ids)
    end_time = time.time() # Finaliza la medición del tiempo
    processing_time = end_time - start_time # Calcula el tiempo de procesamiento 
    print(processing_time)
    print(predicted_sentences)
    return jsonify({"transcription": recibirjson(predicted_sentences[0])})


if __name__ == '__main__':
    app.run(debug=True)