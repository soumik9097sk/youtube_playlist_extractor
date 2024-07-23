from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import requests
from bs4 import BeautifulSoup
import json
import re

app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

class PlaylistRequest(BaseModel):
    url: str

def extract_playlist_info(playlist_url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    try:
        response = requests.get(playlist_url, headers=headers)
        response.raise_for_status()
    except requests.RequestException as e:
        raise HTTPException(status_code=400, detail=f"Error fetching the playlist: {str(e)}")

    soup = BeautifulSoup(response.text, 'html.parser')
    
    script_tag = soup.find("script", string=re.compile("var ytInitialData ="))
    if not script_tag:
        raise HTTPException(status_code=400, detail="Could not find playlist data in the page.")

    json_text = re.search(r'var ytInitialData = (.+?);', script_tag.string).group(1)
    data = json.loads(json_text)

    try:
        playlist_info = []
        videos = data['contents']['twoColumnBrowseResultsRenderer']['tabs'][0]['tabRenderer']['content']['sectionListRenderer']['contents'][0]['itemSectionRenderer']['contents'][0]['playlistVideoListRenderer']['contents']
        
        for video in videos:
            if 'playlistVideoRenderer' in video:
                video_data = video['playlistVideoRenderer']
                title = video_data['title']['runs'][0]['text']
                video_id = video_data['videoId']
                video_url = f"https://www.youtube.com/watch?v={video_id}"
                playlist_info.append({'title': title, 'url': video_url})
        
        return playlist_info
    except KeyError as e:
        raise HTTPException(status_code=400, detail=f"Error parsing JSON data: {str(e)}")

@app.post("/extract-playlist")
async def extract_playlist(request: PlaylistRequest):
    playlist_info = extract_playlist_info(request.url)
    return {"playlist_info": playlist_info}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
