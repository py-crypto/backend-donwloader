from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel
import yt_dlp
import uuid
import os

app = FastAPI()

DOWNLOAD_DIR = "downloads"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

class VideoRequest(BaseModel):
    url: str
    format: str = "480p"   # default format


def get_format_code(formats, target_format):
    for f in formats:
        if f.get("height") and str(f["height"]) == target_format.replace("p", ""):
            return f["format_id"]
    return None


@app.post("/download")
def download_video(data: VideoRequest):
    url = data.url
    target_format = data.format

    temp_id = str(uuid.uuid4())
    output_path = f"{DOWNLOAD_DIR}/{temp_id}.mp4"

    try:
        # First fetch info to find correct format ID
        ydl_opts_info = {"quiet": True, "skip_download": True}
        with yt_dlp.YoutubeDL(ydl_opts_info) as ydl:
            info = ydl.extract_info(url, download=False)

        format_code = get_format_code(info.get("formats", []), target_format)

        if not format_code:
            raise HTTPException(
                status_code=400,
                detail=f"Format {target_format} not available for this video."
            )

        # Download specific format
        ydl_opts = {
            "format": format_code,
            "outtmpl": output_path
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

        return {"download_id": temp_id, "status": "success"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/get_file/{download_id}")
def get_file(download_id: str):
    file_path = f"{DOWNLOAD_DIR}/{download_id}.mp4"
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found.")

    return FileResponse(
        file_path,
        media_type="video/mp4",
        filename="video.mp4"
    )

