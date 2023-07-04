from librespot.audio.decoders import AudioQuality, VorbisOnlyAudioQuality
from librespot.metadata import TrackId
from librespot.core import Session
from libs import enviroment, utils
from pydub import AudioSegment
from dotenv import load_dotenv
from getpass import getpass
import datetime
import requests
import os

# Costants
buffer_size = 1024
token_refresh_interval = 60 * 60  # 1 Hour

# Load .env variables
load_dotenv(enviroment.dotenv_path)

# Check or create a new session
authenticated = True
if os.path.isfile("credentials.json"):
    try:
        SESSION = Session.Builder().stored_file().create()
    except:
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
        "image": response["album"]["images"][0]["url"],
        "disc_number": response["disc_number"]
    }


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
        metadata = track_metadata(request["value"])
        # Prepare file path
        file = f"{file_path}/{metadata['title']} - {metadata['artist']}.mp3"
        # If the file is already present
        if not os.path.exists(file):
            # Get the data stream
            track_id = TrackId.from_uri(f"spotify:track:{request['value']}")
            stream = SESSION.content_feeder().load(
                track_id, VorbisOnlyAudioQuality(QUALITY), False, None
            )
            # Write the stream
            with open(file, "wb") as track:
                for data in iter(
                    lambda: stream.input_stream.stream().read(buffer_size), b""
                ):
                    track.write(data)
            track.close()
            # Postprocess the raw file
            postprocess(file, metadata)
        return True
    return False
