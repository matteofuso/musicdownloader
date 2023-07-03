from mutagen.id3 import ID3, TIT2, TPE1, TALB, TDRC, TRCK, APIC, TPE2
from librespot.audio.decoders import AudioQuality, VorbisOnlyAudioQuality
from librespot.metadata import TrackId
from librespot.core import Session
from pydub import AudioSegment
from dotenv import load_dotenv
from getpass import getpass
from libs import enviroment
import datetime
import requests
import os

# Costants
buffer_size = 1024
token_refresh_interval = 50 * 60  # 50 minutes
file_path = "./download"

# Check or create a new session
if os.path.isfile("credentials.json"):
    SESSION = Session.Builder().stored_file().create()
else:
    authenticated = False
    while not authenticated:
        user_name = input("Username Spotify: ")
        password = getpass("Password Spotify: ")
        try:
            SESSION = Session.Builder().user_pass(user_name, password).create()
            authenticated = True
        except:
            pass


# Set the quality
if SESSION.get_user_attribute("type") == "premium":
    QUALITY = AudioQuality.VERY_HIGH
else:
    QUALITY = AudioQuality.HIGH

# Bitrate array
bitrate = ["96k", "160k", "320k"]


# Function to get api key
def get_token():
    load_dotenv(enviroment.dotenv_path)
    time = os.getenv("spotify_token_request")
    if (
        time is None
        or int(datetime.datetime.now().timestamp())
        > float(time) + token_refresh_interval
    ):
        token = SESSION.tokens().get("user-read-email")
        enviroment.update("spotify_token", token)
        enviroment.update(
            "spotify_token_request", str(datetime.datetime.now().timestamp())
        )
        load_dotenv(enviroment.dotenv_path)
    return os.getenv("spotify_token")


# Function to get song metadata
def track_metadata(id):
    headers = {
        "Authorization": f"Bearer {get_token()}",
        "Content-Type": "application/json",
    }
    api = requests.get(f"https://api.spotify.com/v1/tracks/{id}", headers=headers)
    response = api.json()
    artists_names = [artist["name"] for artist in response["artists"]]
    return {
        "title": response["name"],
        "artist": response["artists"][0]["name"],
        "artists": ", ".join(artists_names),
        "album": response["album"]["name"],
        "year": response["album"]["release_date"].split("-")[0],
        "number": response["track_number"],
        "duration": response["duration_ms"],
        "image": response["album"]["images"][0]["url"],
        "bitrate": bitrate[QUALITY.value],
    }


# Functions directly related to modifying the downloaded audio and its metadata
def export(filename, metadata):
    raw_audio = AudioSegment.from_file(
        filename, format="ogg", frame_rate=44100, channels=2, sample_width=2
    )
    raw_audio.export(filename, format="mp3", bitrate=metadata["bitrate"])
    audio = ID3(filename)
    # Set title
    audio["TIT2"] = TIT2(encoding=3, text=metadata["title"])
    # Set artists
    audio["TPE1"] = TPE1(encoding=3, text=metadata["artists"])
    # Set artist
    audio["TPE2"] = TPE2(encoding=3, text=metadata["artist"])
    # Set album
    audio["TALB"] = TALB(encoding=3, text=metadata["album"])
    # Set year
    audio["TDRC"] = TDRC(encoding=3, text=metadata["year"])
    # Set track number
    audio["TRCK"] = TRCK(encoding=3, text=str(metadata["number"]))
    # Set image (album art)
    image_data = requests.get(metadata["image"]).content
    audio["APIC"] = APIC(
        encoding=3,
        mime="image/jpeg",
        type=3,
        desc="0",
        data=image_data,
    )
    # Save the modified audio file
    audio.save()


# Download function
def download(request):
    if request["type"] == "track":
        track_id = TrackId.from_uri(f"spotify:track:{request['value']}")
        metadata = track_metadata(request["value"])
        stream = SESSION.content_feeder().load(
            track_id, VorbisOnlyAudioQuality(QUALITY), False, None
        )
        file = f"{file_path}/{metadata['title']} - {metadata['artist']}.mp3"
        with open(file, "wb") as track:
            for data in iter(
                lambda: stream.input_stream.stream().read(buffer_size), b""
            ):
                track.write(data)
        track.close()
        export(file, metadata)
        return True
    return False
