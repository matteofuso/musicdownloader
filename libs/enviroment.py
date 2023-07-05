from dotenv import load_dotenv, set_key
import requests
import os

dotenv_path = ".env"
variables = ["youtubeAPI"]

# Function to check youtube api key
def check_youtube_api_key(key):
    url = f'https://youtube.googleapis.com/youtube/v3/videos?part=snippet&id=dQw4w9WgXcQ&key={key}'
    response = requests.get(url).json()
    return "error" not in response or response["error"]["details"][0]["reason"] != "API_KEY_INVALID"

# Function to check enviromental variable
def init():
    if not os.path.exists(dotenv_path):
        open(dotenv_path, "w").close()
    load_dotenv(dotenv_path)
    for variable in variables:
        if os.getenv(variable) is None:
            if variable == variables[0]:
                while True:
                    value = input("Youtube API key is not defined, please provide one: ")
                    if check_youtube_api_key(value):
                        break
            set_key(
                dotenv_path,
                variable,
                value,
            )

# Function to update env variables
def update(key: str, value: str):
    set_key(dotenv_path, key, value)