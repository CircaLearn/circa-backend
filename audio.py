import warnings
import sounddevice as sd
import torch
from transformers import Wav2Vec2ForCTC, Wav2Vec2Processor
import numpy as np
import queue
import sys

# Suppress warnings related to deprecation
warnings.filterwarnings("ignore", category=FutureWarning)

MODEL_ID = "jonatasgrosman/wav2vec2-large-xlsr-53-english"
processor = Wav2Vec2Processor.from_pretrained(MODEL_ID)
model = Wav2Vec2ForCTC.from_pretrained(MODEL_ID)

q = queue.Queue()


def main():
    test_audio_io()
    record_audio()
    audio = get_all_audio_from_queue().flatten()
    print(audio)

    sd.play(audio)
    print("Playing...")
    sd.wait()
    transcription = transcribe_audio(audio)
    print(f"Transcription: {transcription}")


def test_audio_io():
    # this works with my iMac + Bose headphones 
    # also works with MacBook Mic + MacBook Speakers
    # did not work with AirPods IO...
    print(sd.query_devices())


def pad_audio(audio, target_length=16000):
    """Pads audio that is too short (less than 1s)"""
    if len(audio) < target_length:
        padding = target_length - len(audio)
        audio = np.pad(audio, (0, padding), "constant")
    return audio


def record_audio(fs=16000, chunk_duration=1, max_duration=20):
    """Records audio input continuously up to a max_duration for testing of model transcription"""
    sd.default.samplerate = fs
    sd.default.channels = 1
    q.queue.clear()

    # Continuously add to our queue the new recordings
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
        print("\nRecording stopped")

    print("Processing audio...\n")


def audio_callback(indata, frames, time, status):
    """Audio callback function used by sounddevice InputStream"""
    if status:
        print(status, file=sys.stderr)
    q.put(indata.copy())


def get_all_audio_from_queue():
    """Outputs all audio recorded to queue in a np array for model processing"""
    all_audio = []
    while not q.empty():
        all_audio.append(q.get())  # Returns and removes top elem from queue
    if all_audio:
        return np.concatenate(all_audio, axis=0)
    return np.array([])


def transcribe_audio(audio, processor=processor, model=model):
    """Uses model inference to transcribe an audio recording"""
    audio = pad_audio(audio)
    # Preprocessing
    inputs = processor(audio, sampling_rate=16000, return_tensors="pt", padding=True)
    # Inference
    # no_grad turns off gradient descent, which we don't need for inference
    # (only for training) and speeds up this computation
    with torch.no_grad():
        logits = model(inputs.input_values, attention_mask=inputs.attention_mask).logits
    predicted_ids = torch.argmax(logits, dim=-1)
    transcription = processor.batch_decode(predicted_ids)
    return transcription[0]


if __name__ == "__main__":
    main()
