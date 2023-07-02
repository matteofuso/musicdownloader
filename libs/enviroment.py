import os
from dotenv import load_dotenv, set_key

dotenv_path = ".env"

def init():
    if not os.path.exists(dotenv_path):
        open(dotenv_path, "w").close()
    load_dotenv(dotenv_path)
    for variable in ["spotifyAPI", "youtubeAPI"]:
        if os.getenv(variable) is None:
            set_key(dotenv_path, variable, input(f'{variable} is not defined. Please input: '))

def update(key:str, value:str):
    set_key(dotenv_path, key, value)