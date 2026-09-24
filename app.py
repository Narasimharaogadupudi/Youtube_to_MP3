from flask import Flask, render_template, redirect, url_for, request, flash, send_file
import yt_dlp
import threading
import time
import os

app = Flask(__name__)
app.secret_key = "your-secret-key"

def delete_file(file_path):
    time.sleep(5)

    try:
        if os.path.exists(file_path):
            os.remove(file_path)
            print("Temporary file deleted.")
    except Exception as e:
        print("File deletion failed:", e)

@app.route("/")
def main():
    return redirect(url_for("home"))


@app.route("/home", methods=["GET", "POST"])
def home():

    if request.method == "GET":
        return render_template("index.html")

    if request.method == "POST":

        url = request.form.get("url")
        quality = request.form.get("quality", "192")

        def is_valid_yt_url(url):
            return ("youtube.com/" in url or "youtu.be/" in url)

        if not url:
            flash("Please enter a YouTube URL.")
            return redirect(url_for("home"))

        if not is_valid_yt_url(url):
            flash("Enter Valid Youtube URL...")
            return redirect(url_for("home"))

        if quality not in ["128", "192", "320"]:
            flash("Invalid quality selected.")
            return redirect(url_for("home"))


        options = {
            "format": "bestaudio/best",
            "outtmpl": "downloads/%(title)s.%(ext)s",
        
            "ffmpeg_location": "/usr/bin/ffmpeg",
        
            "extractor_args": {
                "youtube": {
                    "player_client": ["mweb"]
                }
            },
        
            "postprocessors": [
                {
                    "key": "FFmpegExtractAudio",
                    "preferredcodec": "mp3",
                    "preferredquality": quality
                }
            ]
        }

        try:

            with yt_dlp.YoutubeDL(options) as ydl:
                info = ydl.extract_info(url, download=True)
                filename = ydl.prepare_filename(info)

            mp3_file = os.path.splitext(filename)[0] + ".mp3"


            response = send_file(
                mp3_file,
                as_attachment=True,
                download_name=os.path.basename(mp3_file)
            )
            
            
            threading.Thread(
                target=delete_file,
                args=(mp3_file,)
            ).start()
            
            return response

        except Exception as e:

            print(e)
            flash("Download failed!")
            return redirect(url_for("home"))



if __name__ == "__main__":
    app.run(debug=True)