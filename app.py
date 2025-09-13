from flask import Flask, request, send_file, Response, jsonify
from flask_cors import CORS
import yt_dlp
import os
import uuid

app = Flask(__name__)
CORS(app)

DOWNLOAD_DIR = "downloads"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)


@app.route("/metadata")
def metadata():
    url = request.args.get("url")
    if not url:
        return jsonify({"error": "Missing 'url' parameter"}), 400

    ydl_opts = {
        "quiet": True,
        "no_warnings": True,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
        return jsonify({
            "title": info.get("title"),
            "thumbnail": info.get("thumbnail"),
            "duration": info.get("duration"),
            "uploader": info.get("uploader"),
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/download")
def download():
    url = request.args.get("url")
    fmt = request.args.get("format", "mp4")  # default mp4

    if not url:
        return Response("Missing 'url' parameter", status=400)

    file_id = str(uuid.uuid4())
    base_path = os.path.join(DOWNLOAD_DIR, file_id)

    if fmt == "mp3":
        ydl_opts = {
            "format": "bestaudio/best",
            "outtmpl": base_path + ".%(ext)s",  # yt-dlp decides extension
            "postprocessors": [
                {
                    "key": "FFmpegExtractAudio",
                    "preferredcodec": "mp3",
                    "preferredquality": "192",
                }
            ],
        }
    else:  # mp4
        ydl_opts = {
            "format": "best",
            "outtmpl": base_path + ".%(ext)s",
        }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            downloaded_file = ydl.prepare_filename(info)

        # If MP3, yt-dlp may append a different extension; force .mp3
        if fmt == "mp3":
            downloaded_file = os.path.splitext(downloaded_file)[0] + ".mp3"

        return send_file(
            downloaded_file,
            as_attachment=True,
            download_name=f"video.{fmt}"
        )

    except Exception as e:
        return Response(f"Error downloading video: {e}", status=500)


if __name__ == "__main__":
    # For local development only
    app.run(host="0.0.0.0", port=5000, debug=True)

# For production deployment (Streamlit Cloud, Heroku, etc.)
# The app object will be used by the WSGI server
