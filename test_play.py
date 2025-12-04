#!/usr/bin/env python3
import subprocess
import wave
import io
import pyaudio
import os

BASE_DIR = os.path.dirname(__file__)
VOICE_MODEL = os.path.join(BASE_DIR, "voices", "en_US-kathleen-low.onnx")
AUDIO_OUTPUT_DEVICE_INDEX = 0  # your USB device

CHUNK = 1024

# Sample text
text = "Hello world! This is a test of mono to stereo playback."

# Run Piper to generate raw PCM
piper_path = os.path.join(BASE_DIR, "bin", "piper", "piper")
piper_proc = subprocess.Popen(
    [piper_path, "--model", VOICE_MODEL, "--output_raw"],
    stdin=subprocess.PIPE,
    stdout=subprocess.PIPE,
    stderr=subprocess.DEVNULL
)
tts_pcm, _ = piper_proc.communicate(input=text.encode())

# Convert raw PCM (mono) -> stereo WAV at 16kHz
sox_proc = subprocess.Popen(
    ["sox", "-t", "raw", "-r", "16000", "-c", "1", "-b", "16", "-e", "signed-integer",
     "-", "-c", "2", "-r", "16000", "-t", "wav", "-"],
    stdin=subprocess.PIPE,
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE
)
final_bytes, sox_err = sox_proc.communicate(input=tts_pcm)
if sox_err:
    print("SoX error:", sox_err.decode())

# Playback with PyAudio
wf = wave.open(io.BytesIO(final_bytes), "rb")
pa = pyaudio.PyAudio()
stream = pa.open(
    format=pa.get_format_from_width(wf.getsampwidth()),
    channels=wf.getnchannels(),
    rate=wf.getframerate(),
    output=True,
    output_device_index=AUDIO_OUTPUT_DEVICE_INDEX
)

data = wf.readframes(CHUNK)
while data:
    stream.write(data)
    data = wf.readframes(CHUNK)

stream.stop_stream()
stream.close()
pa.terminate()
wf.close()

print("Playback done.")
