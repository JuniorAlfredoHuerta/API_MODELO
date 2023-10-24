from flask import Flask, request
from flask import jsonify
from transformers import Wav2Vec2ForCTC, Wav2Vec2Processor
import torch
import librosa

app = Flask(__name__)

model = Wav2Vec2ForCTC.from_pretrained("jonatasgrosman/wav2vec2-large-xlsr-53-spanish")
model.load_state_dict(torch.load('./model.pth'))
processor = Wav2Vec2Processor.from_pretrained("jonatasgrosman/wav2vec2-large-xlsr-53-spanish")

#input_audio, _ = librosa.load(audio3, sr=16000)
#inputs = processor(input_audio, sampling_rate=16_000, return_tensors="pt", padding=True)
#with torch.no_grad():
#    logits = model(inputs.input_values, attention_mask=inputs.attention_mask).logits
#predicted_ids = torch.argmax(logits, dim=-1)
#predicted_sentences = processor.batch_decode(predicted_ids)
#print("Prediction:", predicted_sentences)


@app.route('/transcribe', methods=['POST'])
def transcribe():
    audio = request.files['audio']
    audio.save('audio.wav')
    input_audio, _ = librosa.load('audio.wav', sr=16000)
    inputs = processor(input_audio, sampling_rate=16_000, return_tensors="pt", padding=True)
    with torch.no_grad():
        logits = model(inputs.input_values, attention_mask=inputs.attention_mask).logits
    predicted_ids = torch.argmax(logits, dim=-1)
    predicted_sentences = processor.batch_decode(predicted_ids)
    return {"transcription": predicted_sentences[0]}

if __name__ == '__main__':
    app.run(debug=True)