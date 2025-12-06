from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pytube import YouTube

app = FastAPI()

# Allow all domains (important for Streamlit)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def home():
    return {"status": "YT Backend Running"}

@app.get("/get_streams")
def get_streams(url: str):
    yt = YouTube(url)
    streams = yt.streams.filter(progressive=True, file_extension="mp4").all()

    result = []
    for s in streams:
        result.append({
            "itag": s.itag,
            "resolution": s.resolution,
            "mime_type": s.mime_type,
            "fps": s.fps,
            "url": s.url,
        })

    # Audio-only streams
    audio_streams = yt.streams.filter(only_audio=True).all()
    audio_list = []
    for a in audio_streams:
        audio_list.append({
            "itag": a.itag,
            "abr": a.abr,
            "mime_type": a.mime_type,
            "url": a.url,
        })

    return {
        "title": yt.title,
        "thumbnail": yt.thumbnail_url,
        "video_streams": result,
        "audio_streams": audio_list,
    }
