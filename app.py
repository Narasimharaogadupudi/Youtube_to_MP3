
from flask import (
    Flask, render_template, redirect, url_for,
    request, flash, send_file, jsonify
)
import yt_dlp
import os

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "local-development-key")


@app.route("/")
def main():
    return redirect(url_for("home"))


@app.route("/home", methods=["GET", "POST"])
def home():
    if request.method == "GET":
        return render_template("index.html")

    is_ajax = (
        request.headers.get("X-Requested-With") == "XMLHttpRequest"
    )

    def error_response(message, status=400):
        if is_ajax:
            return jsonify({"error": message}), status

        flash(message)
        return redirect(url_for("home"))

    url = request.form.get("url", "").strip()
    quality = request.form.get("quality", "192")

    if not url:
        return error_response("Please enter a YouTube URL.")

    if not ("youtube.com/" in url or "youtu.be/" in url):
        return error_response("Enter a valid YouTube URL.")

    if quality not in ["128", "192", "320"]:
        return error_response("Invalid quality selected.")

    options = {
        "format": "bestaudio/best",
        "outtmpl": "downloads/%(id)s-%(title)s.%(ext)s",
        "ffmpeg_location": "/usr/bin/ffmpeg",
        "postprocessors": [
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": quality
            }
        ],
        "retries": 3,
        "fragment_retries": 3,
        "continuedl": True,
        "noplaylist": True,
        "quiet": False,
        "no_warnings": False
    }

    try:
        os.makedirs("downloads", exist_ok=True)

        with yt_dlp.YoutubeDL(options) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)

        mp3_file = os.path.splitext(filename)[0] + ".mp3"

        if not os.path.isfile(mp3_file):
            raise FileNotFoundError("MP3 file was not created.")

        response = send_file(
            mp3_file,
            as_attachment=True,
            download_name=os.path.basename(mp3_file),
            mimetype="audio/mpeg"
        )

        def cleanup():
            try:
                if os.path.exists(mp3_file):
                    os.remove(mp3_file)
                    print("Temporary file deleted.")
            except OSError as exc:
                print("File deletion failed:", exc)

        response.call_on_close(cleanup)
        return response

    except Exception as exc:
        print("DOWNLOAD ERROR:", repr(exc))
        return error_response(
            "Download failed. This video may be unavailable or YouTube may have blocked the request.",
            500
        )


if __name__ == "__main__":
    app.run(debug=True)
