import sounddevice as sd
import torch
from transformers import Wav2Vec2ForCTC, Wav2Vec2Processor
import numpy as np

MODEL_ID = "jonatasgrosman/wav2vec2-large-xlsr-53-english"

processor = Wav2Vec2Processor.from_pretrained(MODEL_ID)
model = Wav2Vec2ForCTC.from_pretrained(MODEL_ID)

### Recording audio input for testing
def record_audio(duration, fs = 16000):
    sd.default.samplerate = fs
    sd.default.channels= 1

    print(f"Recording audio for {duration} seconds...")
    recording = sd.rec(int(duration*fs))
    sd.wait()
    print("Recording complete!")
    return recording

def pad_audio(audio, target_length = 16000):
    if len(audio) < target_length:
        padding = target_length - len(audio)
        audio = np.pad(audio, (0, padding), "constant")
    return audio


def transcribe_audio(audio, processor=processor, model=model):
    audio = pad_audio(audio)

    # preprocessing
    inputs = processor(audio, sampling_rate=16000, return_tensors="pt", padding=True)

    # inference
    with torch.no_grad():
        logits = model(inputs.input_values, attention_mask=inputs.attention_mask).logits

    predicted_ids = torch.argmax(logits, dim=-1)
    transcription = processor.batch_decode(predicted_ids)

    return transcription[0]

duration = 3
audio = record_audio(duration).flatten()

transcription = transcribe_audio(audio)

print(f"Transcription: {transcription}")
