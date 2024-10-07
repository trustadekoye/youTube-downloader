import yt_dlp
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.http import FileResponse
import os
import tempfile
import subprocess


@api_view(["POST"])
def get_video_info(request):
    url = request.data.get("url")
    if not url:
        return Response({"error": "URL is required"}, status=400)

    ydl_opts = {
        "format": "bestaudio/best",
        "postprocessors": [
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": "192",
            }
        ],
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            formats = []
            for f in info["formats"]:
                if f.get("vcodec", "none") != "none":
                    format_info = {
                        "format_id": f.get("format_id", "Unknown"),
                        "ext": f.get("ext", "Unknown"),
                        "quality": f.get(
                            "format_note", f.get("resolution", "Unknown quality")
                        ),
                        "filesize": f.get("filesize", "Unknown size"),
                    }
                    formats.append(format_info)
            return Response(
                {
                    "title": info.get("title", "Unknown title"),
                    "thumbnail": info.get("thumbnail", ""),
                    "duration": info.get("duration_string", "Unknown duration"),
                    "formats": formats,
                }
            )
    except Exception as e:
        return Response({"error": str(e)}, status=400)


@api_view(["POST"])
def download_video(request):
    url = request.data.get("url")
    quality = request.data.get("quality", "bestvideo+bestaudio/best")
    if not url:
        return Response({"error": "URL is required"}, status=400)

    try:
        with tempfile.TemporaryDirectory() as tmp_dir:
            ydl_opts = {
                "format": quality,
                "outtmpl": os.path.join(tmp_dir, "%(title)s.%(ext)s"),
                "merge_output_format": "mp4",
                "postprocessors": [
                    {
                        "key": "FFmpegVideoConvertor",
                        "preferedformat": "mp4",
                    }
                ],
                "verbose": True,
            }

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                filename = ydl.prepare_filename(info)

                # Ensure the file exists and has content
                if not os.path.exists(filename) or os.path.getsize(filename) == 0:
                    return Response(
                        {"error": "Failed to download the video"}, status=400
                    )

                # Check if the file has audio using FFprobe
                has_audio = check_audio(filename)

                if not has_audio:
                    # If no audio, try to download audio separately and merge
                    audio_filename = download_audio(url, tmp_dir)
                    if audio_filename:
                        merged_filename = merge_audio_video(
                            filename, audio_filename, tmp_dir
                        )
                        if merged_filename:
                            filename = merged_filename

                # Serve the file as a response for download
                response = FileResponse(open(filename, "rb"), as_attachment=True)
                response[
                    "Content-Disposition"
                ] = f'attachment; filename="{os.path.basename(filename)}"'
                return response
    except Exception as e:
        return Response({"error": str(e)}, status=400)


def check_audio(filename):
    try:
        result = subprocess.run(
            [
                "ffprobe",
                "-v",
                "error",
                "-select_streams",
                "a:0",
                "-count_packets",
                "-show_entries",
                "stream=nb_read_packets",
                "-of",
                "csv=p=0",
                filename,
            ],
            capture_output=True,
            text=True,
        )
        return int(result.stdout.strip()) > 0
    except:
        return False


def download_audio(url, tmp_dir):
    ydl_opts = {
        "format": "bestaudio/best",
        "outtmpl": os.path.join(tmp_dir, "audio.%(ext)s"),
        "postprocessors": [
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": "m4a",
            }
        ],
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])

    # Find the audio file (it might be .m4a instead of .aac)
    for file in os.listdir(tmp_dir):
        if file.startswith("audio.") and file.endswith((".m4a", ".aac")):
            return os.path.join(tmp_dir, file)
    return None


def merge_audio_video(video_file, audio_file, tmp_dir):
    output_file = os.path.join(tmp_dir, "merged_output.mp4")
    try:
        subprocess.run(
            [
                "ffmpeg",
                "-i",
                video_file,
                "-i",
                audio_file,
                "-c:v",
                "copy",
                "-c:a",
                "aac",
                "-strict",
                "experimental",
                output_file,
            ],
            check=True,
            capture_output=True,
            text=True,
        )
        return output_file
    except subprocess.CalledProcessError as e:
        print(f"FFmpeg error: {e.stderr}")
        return None
