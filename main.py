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
    format: str = None  # optional for formats endpoint


@app.post("/download")
def download_video(data: VideoRequest):
    url = data.url
    format_id = data.format

    temp_id = str(uuid.uuid4())
    output_path = f"{DOWNLOAD_DIR}/{temp_id}.mp4"

    try:
        # Validate the URL and fetch available formats
        ydl_info_opts = {"quiet": True, "skip_download": True}
        with yt_dlp.YoutubeDL(ydl_info_opts) as ydl:
            info = ydl.extract_info(url, download=False)

        available_ids = [f["format_id"] for f in info.get("formats", [])]

        if format_id not in available_ids:
            raise HTTPException(
                status_code=400,
                detail=f"format_id {format_id} is not available for this video."
            )

        # Download EXACT format_id
        ydl_opts = {
            "format": format_id,
            "outtmpl": output_path
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

        return {"download_id": temp_id, "status": "success", "title": info.get("title", "video")}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/formats")
def get_formats(data: VideoRequest):
    url = data.url
    try:
        with yt_dlp.YoutubeDL({"quiet": True, "skip_download": True}) as ydl:
            info = ydl.extract_info(url, download=False)

        formats_list = []
        for f in info.get("formats", []):
            if f['vcodec'] != 'none' and f['acodec'] != 'none':  # only video+audio
                formats_list.append({
                    "format_id": f["format_id"],
                    "resolution": f.get("height"),
                    "ext": f.get("ext"),
                    "note": f.get("format_note")
                })

        # remove duplicates by resolution, keep highest quality per resolution
        seen_res = set()
        unique_formats = []
        for f in sorted(formats_list, key=lambda x: x["resolution"] or 0):
            if f["resolution"] not in seen_res and f["resolution"] is not None:
                seen_res.add(f["resolution"])
                unique_formats.append(f)

        return {"title": info.get("title", "video"), "formats": unique_formats}

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

