# backend/routes/voice.py

from fastapi import APIRouter, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
import os
import uuid
import shutil
import speech_recognition as sr
from pydub import AudioSegment
from langdetect import detect

router = APIRouter()

VOICE_DIR = "uploads/voice"
os.makedirs(VOICE_DIR, exist_ok=True)

@router.post("/upload", tags=["Voice Reporting"])
async def upload_voice(file: UploadFile = File(...)):
    if not file.filename.endswith((".wav", ".mp3", ".m4a")):
        raise HTTPException(status_code=400, detail="Unsupported audio format. Please upload WAV, MP3, or M4A.")

    # Save audio file temporarily
    file_id = f"{uuid.uuid4()}"
    audio_path = os.path.join(VOICE_DIR, f"{file_id}_{file.filename}")
    with open(audio_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    try:
        # Convert to WAV if necessary
        if audio_path.endswith(".mp3"):
            sound = AudioSegment.from_mp3(audio_path)
            audio_path = audio_path.replace(".mp3", ".wav")
            sound.export(audio_path, format="wav")
        elif audio_path.endswith(".m4a"):
            sound = AudioSegment.from_file(audio_path, "m4a")
            audio_path = audio_path.replace(".m4a", ".wav")
            sound.export(audio_path, format="wav")

        recognizer = sr.Recognizer()
        with sr.AudioFile(audio_path) as source:
            audio = recognizer.record(source)

        # Recognize using Google Web Speech API
        text = recognizer.recognize_google(audio)
        language = detect(text)

        return JSONResponse(content={
            "message": "✅ Audio processed successfully",
            "transcription": text,
            "language": language,
            "file": audio_path
        })

    except sr.UnknownValueError:
        raise HTTPException(status_code=422, detail="Unable to recognize speech.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing audio: {e}")
