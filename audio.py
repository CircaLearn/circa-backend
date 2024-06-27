import warnings

# Suppress warnings related deprecation
warnings.filterwarnings("ignore", category=FutureWarning)

import sounddevice as sd
import torch
from transformers import Wav2Vec2ForCTC, Wav2Vec2Processor
import numpy as np
import queue
import sys


MODEL_ID = "jonatasgrosman/wav2vec2-large-xlsr-53-english"
processor = Wav2Vec2Processor.from_pretrained(MODEL_ID)
model = Wav2Vec2ForCTC.from_pretrained(MODEL_ID)

q = queue.Queue()


def main():
    record_audio()
    audio = get_all_audio_from_queue().flatten()
    transcription = transcribe_audio(audio)

    print(f"Transcription: {transcription}")


def pad_audio(audio, target_length=16000):
    """pads audio that is too short (less than 1s)"""

    if len(audio) < target_length:
        padding = target_length - len(audio)
        audio = np.pad(audio, (0, padding), "constant")
    return audio


def record_audio(fs=16000, chunk_duration=1, max_duration=20):
    """Records audio input continuously up to a max_duration for testing of
    model transcription"""

    sd.default.samplerate = fs
    sd.default.channels = 1
    q.queue.clear()

    # continuously add to our queue the new recordings
    try:
        print("Recording audio... Press Ctrl+C to stop")
        recorded_time = 0
        with sd.InputStream(
            callback=audio_callback, blocksize=int(chunk_duration * fs)
        ):
            while True:
                sd.sleep(int(chunk_duration * 1000))
                recorded_time += chunk_duration * 1000
                if recorded_time >= max_duration * 1000:
                    print(f"Recording stopped after {max_duration} seconds")
                    break
    except KeyboardInterrupt:
        print("Recording stopped")

    print("Processing audio...")


def audio_callback(indata, frames, time, status):
    """audio callback function used by sounddevice InputStream"""
    if status:
        print(status, file=sys.stderr)
    q.put(indata.copy())


def get_all_audio_from_queue():
    """outputs all audio recorded to queue in a np array for model processing"""

    all_audio = []
    while not q.empty():
        all_audio.append(q.get())  # returns and removes top elem from queue
    return np.concatenate(all_audio, axis=0)


def transcribe_audio(audio, processor=processor, model=model):
    """uses model inference to transcribe an audio recording"""

    audio = pad_audio(audio)
    # preprocessing
    inputs = processor(audio, sampling_rate=16000, return_tensors="pt", padding=True)
    # inference
    # no_grad turns off gradient descent, which we don't need for inference
    # (only for training) and speed up this computation
    with torch.no_grad():
        logits = model(inputs.input_values, attention_mask=inputs.attention_mask).logits
    predicted_ids = torch.argmax(logits, dim=-1)
    transcription = processor.batch_decode(predicted_ids)
    return transcription[0]


if __name__ == "__main__":
    main()
