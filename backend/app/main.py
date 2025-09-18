from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
import yt_dlp
import os

app = FastAPI()

# Allow frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # You can restrict this to your frontend URL if you want
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DOWNLOAD_DIR = "downloads"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)


@app.get("/formats")
async def get_formats(url: str):
    """Fetch only metadata + streaming URLs (no download)."""
    try:
        ydl_opts = {"quiet": True, "skip_download": True}
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)

        formats = []
        for f in info.get("formats", []):
            if f.get("ext") == "mp4" and f.get("url"):
                note = f.get("format_note") or f.get("height", "unknown")
                if str(note).lower() == "watermarked":
                    note = "Highest Quality"

                formats.append({
                    "format_id": f.get("format_id"),
                    "resolution": note,
                    "filesize": f.get("filesize"),
                    "acodec": f.get("acodec"),
                    "direct_url": f.get("url"),  # ✅ for preview streaming
                })

        return {"title": info.get("title"), "formats": formats}

    except Exception as e:
        return JSONResponse(status_code=400, content={"error": str(e)})


@app.get("/download")
async def download_video(url: str, format_id: str):
    """Download once, cache file, then reuse on next request."""
    try:
        # Generate safe filename
        safe_title = "video"
        ydl_info_opts = {"quiet": True, "skip_download": True}
        with yt_dlp.YoutubeDL(ydl_info_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            safe_title = info.get("title", "video").replace("/", "_").replace("\\", "_")

        output_path = os.path.join(DOWNLOAD_DIR, f"{safe_title}.mp4")

        # ✅ Reuse if file already downloaded
        if os.path.exists(output_path):
            return FileResponse(output_path, media_type="video/mp4", filename=os.path.basename(output_path))

        # ✅ Otherwise download fresh
        ydl_opts = {
            "format": format_id,
            "outtmpl": output_path,
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

        return FileResponse(output_path, media_type="video/mp4", filename=os.path.basename(output_path))

    except Exception as e:
        return JSONResponse(status_code=400, content={"error": str(e)})
