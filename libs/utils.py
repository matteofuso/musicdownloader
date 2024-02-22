from mutagen.id3 import ID3, TIT2, TPE1, TALB, TDRC, TRCK, APIC, TPE2, TPOS
from io import BytesIO
from PIL import Image
import requests
import re


# Function to parse a promt to an array countaining the service, the type and the value of the request
def parse(input: str):
    match = re.match(r"(http[s]?://)?([a-zA-Z.]+)/(.*)?", input)
    # Check if the input is a link
    if match:
        URLparts = match.group(2).split(".")
        # Obtain the URL parts
        domain = ".".join(URLparts[-2:])
        path = match.group(3)
        # If the path is empty
        if path is None:
            return {"type": "error", "value": "A complete link must be given"}
        # Check if the service is youtube
        if domain in ["youtube.com", "youtu.be"]:
            return youtubeParse(path)
        if domain == "spotify.com":
            return spotifyParse(path)
        # If the service is not supported
        return {"type": "error", "value": "Not supported link"}
    # If the promt is a search query
    return {"service": "spotify", "type": "search", "value": input}


# Subfunction of parse, works only for youtube with the path of the link
def youtubeParse(path):
    match = re.match(r"((results|watch|playlist)\?)?(.*)", path)
    # Check if the path is valid
    if match:
        # Check if the path includes arguments
        if match.group(1) is None:
            # Check if all the chars in the path are valid for the video id
            if re.match(r"^[a-zA-Z0-9]+$", path):
                return {"service": "youtube", "type": "v", "value": path}
        else:
            # Get the link args
            args = match.group(3).split("&")
            for arg in args:
                key, value = arg.split("=", 1)
                # Check for valid arguments
                if key in ["search_query", "v", "list"] and value != "":
                    return {"service": "youtube", "type": key, "value": value}
                break
    # If no return yet, return an error
    return {"type": "error", "value": "Invalid URL"}


# Subfunction of parse, works only for spotify with the path of the link
def spotifyParse(path):
    # Check for valid path
    # https://open.spotify.com/intl-it/track/23RoR84KodL5HWvUTneQ1w?si=da5e578e6e574179
    if path.startswith("intl-"):
        path = path[8:]
    print(path)
    match = re.match(r"(track|playlist|album|show|search)\/([a-zA-Z0-9]+)", path)
    print(match)
    if match:
        # Return if valid
        return {"service": "spotify", "type": match.group(1), "value": match.group(2)}
    else:
        # If no return yet, return an error
        return {"type": "error", "value": "Invalid URL"}


# Function to add metadata to downloaded file
def add_metadata(path, metadata):
    # Open the file
    file = ID3(path)
    # Set title
    file["TIT2"] = TIT2(encoding=3, text=metadata["title"])
    # Set artists
    file["TPE1"] = TPE1(encoding=3, text=metadata["artists"])
    # Set artist
    file["TPE2"] = TPE2(encoding=3, text=metadata["artist"])
    # Set album
    file["TALB"] = TALB(encoding=3, text=metadata["album"])
    # Set year
    file["TDRC"] = TDRC(encoding=3, text=metadata["year"])
    # Download the image
    image_data = requests.get(metadata["image"]).content
    # If the track number and disk number are not specified
    if "number" in metadata:
        # Set track number
        file["TRCK"] = TRCK(encoding=3, text=str(metadata["number"]))
        # Set the disc number
        file["TPOS"] = TPOS(encoding=3, text=str(metadata["disc_number"]))
        # Set image (album art)
    # If it is from youtube music
    if "music" in metadata and metadata["music"]:
        # Open the image
        image = Image.open(BytesIO(image_data))
        # Crop the image
        width, height = image.size
        top_left = int((width - height) / 2)
        box = (top_left, 0, width - top_left, height)
        cropped_image = image.crop(box)
        # Save the image
        cropped_image_buffer = BytesIO()
        cropped_image.save(cropped_image_buffer, format="JPEG")
        image_data = cropped_image_buffer.getvalue()
    # Set the image
    file["APIC"] = APIC(
        encoding=3,
        mime="image/jpeg",
        type=3,
        desc="0",
        data=image_data,
    )
    # Save the modified file
    file.save()


def sanitize_file_name(file_name:str):
    return file_name.replace("/", "").replace("\\", "").replace(":", "").replace("*", "").replace("?", "").replace("<", "").replace(">", "").replace("|", "")