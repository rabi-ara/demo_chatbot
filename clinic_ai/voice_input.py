# voice_input.py
import sounddevice as sd
import numpy as np
from scipy.io.wavfile import write
import tempfile
import subprocess
import os

def record_audio(seconds=4, samplerate=16000):
    print("🎤 Speak now...")
    audio = sd.rec(
        int(seconds * samplerate),
        samplerate=samplerate,
        channels=1,
        dtype=np.int16
    )
    sd.wait()
    return audio, samplerate


def get_voice_input(prompt_text: str) -> str:
    print(prompt_text)

    audio, sr = record_audio()

    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
        wav_path = f.name
        write(wav_path, sr, audio)

    # ✅ OFFICIAL OLLAMA WHISPER USAGE (CLI)
    result = subprocess.run(
        ["ollama", "run", "dimavz/whisper-tiny"],
        input=open(wav_path, "rb").read(),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        shell=True,
    )

    os.remove(wav_path)

    text = result.stdout.decode("utf-8").strip()

    clean = (
        text.lower()
        .replace("patient id", "")
        .replace("appointment id", "")
        .replace("date", "")
        .replace("time", "")
        .replace("at", "")
        .replace("is", "")
        .strip()
    )

    print(f"📝 Transcribed: {clean}")
    return clean
