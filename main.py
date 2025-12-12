from fastapi import FastAPI
from fastapi.responses import FileResponse
import yt_dlp
from pydantic import BaseModel
import os
import uuid

app = FastAPI()
base_dir = os.getcwd()

class Data(BaseModel):
    url: str

class VideoRequest(BaseModel):
    url: str
    format_id: str

os.makedirs("downloads", exist_ok=True)


@app.post('/get_format')
def get_format(data: Data):
    ydl_opts = {'list_formats': True, 'skip_download': True}
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(data.url, download=False)

    formats = {}
    for f in info.get("formats", []):
        if f['vcodec'] != 'none' and f['acodec'] != 'none':
            formats[f["height"]] = f["format_id"]
    return formats


@app.post('/download')
def download_vid(data: VideoRequest):
    file_name = f"{uuid.uuid4()}.mp4"
    file_path = os.path.join("downloads", file_name)

    ydl_opts = {"format": data.format_id, "outtmpl": file_path}
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([data.url])

    return {"file_name": file_name}


@app.get('/download_file')
def download_file(file_name: str):
    file_path = os.path.join(base_dir, "downloads", file_name)
    return FileResponse(
        path=file_path,
        media_type="video/mp4",
        filename=file_name
    )
