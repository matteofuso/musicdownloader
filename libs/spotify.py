from librespot.audio.decoders import AudioQuality, VorbisOnlyAudioQuality
from librespot.metadata import TrackId
from librespot.core import Session
from libs import enviroment, utils
from pydub import AudioSegment
from dotenv import load_dotenv
from getpass import getpass
import datetime
import requests
import time
import os
import re
import json

# Costants
buffer_size = 1024
token_refresh_interval = 60 * 60  # 1 Hour
timeout = 10 # Minimun time to wait between two songs to be downloaded (to avoid ban)

# Gloval variables
last_download = datetime.datetime.now().timestamp()
SESSION = None
QUALITY = None

# Load .env variables
load_dotenv(enviroment.dotenv_path)

# Check or create a new session
authenticated = False
if os.path.isfile("credentials.json"):
    try:
        SESSION = Session.Builder().stored_file().create()
        authenticated = True
    except:
        authenticated = False
while not authenticated:
    user_name = input("Username Spotify: ")
    password = input("Password Spotify: ")
    try:
        SESSION = Session.Builder().user_pass(user_name, password).create()
        break
    except:
        continue


# Set the quality
if SESSION.get_user_attribute("type") == "premium":
    QUALITY = AudioQuality.VERY_HIGH
else:
    QUALITY = AudioQuality.HIGH

# Bitrate array
bitrate = ["96k", "160k", "320k"]


# Function to get api key
def get_token():
    # Get the time when the API key was issued
    time = os.getenv("spotify_token_request")
    # If the token is expired generate a new one
    if (
        time is None
        or int(datetime.datetime.now().timestamp())
        > float(time) + token_refresh_interval
    ):
        token = SESSION.tokens().get("user-read-email")
        # Update the env variable
        enviroment.update("spotify_token", token)
        enviroment.update(
            "spotify_token_request", str(datetime.datetime.now().timestamp())
        )
    return os.getenv("spotify_token")


# Function to get song metadata
def format_metadata(raw, basic=False):
    if "error" in raw:
        return False
    artists_names = [artist["name"] for artist in raw["artists"]]
    title = re.sub(r'\(feat\..*?\)', '', raw["name"])
    title = re.sub(r'\(con.*?\)', '', title).rstrip()
    if basic:
        return {
            "title": title,
            "artists": ", ".join(artists_names),
        }
    return {
        "title": title,
        "artist": raw["artists"][0]["name"],
        "artists": ", ".join(artists_names),
        "album": raw["album"]["name"],
        "year": raw["album"]["release_date"].split("-")[0],
        "number": raw["track_number"],
        "image": raw["album"]["images"][0]["url"],
        "disc_number": raw["disc_number"],
    }


# Function to search for a song and download
def search(name):
    headers = {
        "Authorization": f"Bearer {get_token()}",
        "Content-Type": "application/json",
    }
    url = f"https://api.spotify.com/v1/search?q={name.replace(' ', '+')}&type=track&limit=10"
    api = requests.get(url, headers=headers)
    response = api.json()
    if "tracks" in response:
        print("\nHere a list of suitable tracks:")
        for i, item in enumerate(response["tracks"]["items"], 1):
            metadata = format_metadata(item, True)
            print(f"{i}. {metadata['title']} - {metadata['artists']}")
        while True:
            i = input("Select the song (or write exit): ")
            try:
                i = int(i) - 1
            except:
                if i == "exit":
                    return False
                else:
                    continue
            else:
                if i >= 0 and i < len(response["tracks"]["items"]):
                    return response["tracks"]["items"][i]
    return False


# Functions directly related to modifying the downloaded audio and its metadata
def postprocess(filename, metadata):
    # Export the audio from raw to playable format
    raw_audio = AudioSegment.from_file(
        filename, format="ogg", frame_rate=44100, channels=2, sample_width=2
    )
    raw_audio.export(filename, format="mp3", bitrate=bitrate[QUALITY.value])
    # Add metadata
    utils.add_metadata(filename, metadata)


# Download function
def download(request, file_path):
    # If the request is about a track
    if request["type"] == "track":
        # Get metadata
        headers = {
            "Authorization": f"Bearer {get_token()}",
            "Content-Type": "application/json",
        }
        api = requests.get(f"https://api.spotify.com/v1/tracks/{request['value']}", headers=headers)
        # Response to file
        metadata = format_metadata(api.json())
        # If the resource does not exist
        if not metadata:
            return metadata
        # Download the track
        download_track(request["value"], metadata, file_path)
        return True
    # If the request is about a search request
    if request["type"] == "search":
        raw = search(request["value"])
        # If no match
        if raw:
            download_track(raw["id"], format_metadata(raw), file_path)
            return True
    return False


# Function to downloa a track
def download_track(id, metadata, file_path):
    global last_download
    # Get the data stream
    track_id = TrackId.from_uri(f"spotify:track:{id}")
    stream = SESSION.content_feeder().load(
        track_id, VorbisOnlyAudioQuality(QUALITY), False, None
    )
    # Prepare file path
    file = f"{metadata['title']}.mp3"
    file = f"{file_path}/{utils.sanitize_file_name(file)}"
    # If the file is already present
    if os.path.exists(file):
        print("Song already exists, skipping...\n")
        return
    while datetime.datetime.now().timestamp() - last_download < timeout:
        print(datetime.datetime.now().timestamp() - last_download)
        time.sleep(1)
    # Write the stream
    with open(file, "wb") as track:
        print("Downloading...")
        for data in iter(lambda: stream.input_stream.stream().read(buffer_size), b""):
            track.write(data)
        track.close()
        last_download = datetime.datetime.now().timestamp()
        # Postprocess the raw file
        postprocess(file, metadata)
        print("Downloaded successfully!\n")
