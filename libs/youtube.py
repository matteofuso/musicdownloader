from libs import enviroment, utils
from dotenv import load_dotenv
import requests
import yt_dlp
import os

# yt-dlp download options
download_option = {
    "postprocessors": [
        {
            "key": "FFmpegExtractAudio",
            "preferredcodec": "mp3",
        }
    ],
    "format": "bestaudio/best",
    "quiet": True,
}

# Load the youtube api key
load_dotenv(enviroment.dotenv_path)


# Function to fetch the video metadata from youtube
def video_metadatadata(id):
    api = requests.get(
        f'https://youtube.googleapis.com/youtube/v3/videos?part=snippet&id={id}&key={os.getenv("youtubeAPI")}'
    )
    response = api.json()
    if len(response["items"]) == 0:
        return False
    snippet = response["items"][0]["snippet"]
    description = snippet["description"]
    args = description.split("\n")
    music = False
    # If it is a music
    if args[-1] == "Auto-generated by YouTube.":
        music = True
        file = args[2].split(" · ")
        autors_list = file[1:]
        title = file[0]
        artists = ", ".join(autors_list)
        artist = autors_list[0]
        album = args[4]
        year = args[8].removeprefix("Released on: ").split("-")[0]
        filename = f"{title} - {artist}"
    else:
        title = snippet["title"]
        artist = snippet["channelTitle"]
        artists = artist
        album = title
        year = snippet["publishedAt"].split("-")[0]
        filename = title
    return {
        "title": title,
        "artist": artist,
        "artists": artists,
        "album": album,
        "year": year,
        "image": f"https://i.ytimg.com/vi/{id}/maxresdefault.jpg",
        "music": music,
        "filename": filename,
    }


# Download function
def download(request, file_path):
    # If the request is about a video
    if request["type"] == "v":
        # Get metadata
        metadata = video_metadatadata(request["value"])
        # Check if the resource exists
        if not metadata:
            return metadata
        # Prepare file path
        filename = f"{file_path}/{metadata['filename']}"
        # If the file already exists
        if os.path.exists(filename + ".mp3"):
            print("Video already exists, skipping...")
        else:
            # Download the video
            with yt_dlp.YoutubeDL({**download_option, "outtmpl": filename}) as ydl:
                ydl.download(f"https://www.youtube.com/watch?v={request['value']}")
                # Add the metadata
                ydl.add_post_hook(utils.add_metadata(filename + ".mp3", metadata))
        return True
    return False
