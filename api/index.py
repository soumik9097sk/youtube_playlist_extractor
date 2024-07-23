from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from .extractor import extract_playlist_info
from mangum import Mangum

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)


class PlaylistRequest(BaseModel):
    url: str


@app.post("/api/extract-playlist")
async def extract_playlist(request: PlaylistRequest):
    try:
        playlist_info = extract_playlist_info(request.url)
        return {"playlist_info": playlist_info}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/api/health")
async def health_check():
    return {"status": "healthy"}


# Handler for AWS Lambda
handler = Mangum(app)

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
