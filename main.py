#backend
from fastapi import FastAPI
from fastapi.responses import FileResponse
import yt_dlp
import json
import time
from pydantic import BaseModel
import os
import uuid

app=FastAPI()
class data(BaseModel):
	url:str
class VideoRequest(BaseModel):
	url:str
	format_id:str
class file(BaseModel):
	file_path:str
	file_name:str
os.makedirs('downloads',exist_ok=True)

#will return audio+video file formats with title,format_id,resolution,height,ext and takes input as-url:str
@app.post('/get_format')
def get_format(data:data):
	ydl_opts={'list_formats':True,'skip_download':True}
	with yt_dlp.YoutubeDL(ydl_opts) as yd1:
		content=yd1.extract_info(data.url ,download=False)
	info={}
	info['title']=content.get('title','video')
	avl_formats={}
	for f in content.get('formats',[]):
		if f['vcodec'] != 'none' and f['acodec'] != 'none':
			avl_formats[f['format_id']]=f['height']
	info['avl_formats']=avl_formats
	title_info=content.get('title','video').replace(' ','_')
	return info
file_name=''
#downloads the video and takes input as url in string and format_id in str as well
@app.post('/download')
def download_vid(data:VideoRequest):
	url=data.url
	format_id=data.format_id
	file_name=str(uuid.uuid4())+'.mp4'
	ydl_opts={'format':format_id,'outtmpl':file_name}
	with yt_dlp.YoutubeDL(ydl_opts) as yd1:
		yd1.download([url])
	return {'file_location':f'downloads/{file_name}','file_name':file_name}
	
	
@app.get('/download_file/')
def download_video_device(file_path:str,file_name:str):
	return FileResponse(path=file_path,media_type='video/mp4',filename=file_name)
	
