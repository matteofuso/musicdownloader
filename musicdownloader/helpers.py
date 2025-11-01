import os
import re
from typing import Callable
from dotenv import load_dotenv, set_key
from musicdownloader.core.downloader import Downloader, DownloadException
from musicdownloader.core.spotify import SpotifyDownloader, SpotifyResource

class Helpers():
    __DOTENV: str = ".env"

    @staticmethod
    def load_environment():
        load_dotenv(Helpers.__DOTENV)

    @staticmethod
    def get_env_variable(var_name: str) -> str | None:
        return os.getenv(var_name)
    
    @staticmethod
    def set_env_variable(var_name: str, value: str) -> None:
        os.environ[var_name] = value
        if not os.path.exists(Helpers.__DOTENV):
            with open(Helpers.__DOTENV, 'w'):
                pass
        set_key(Helpers.__DOTENV, var_name, value)

    @staticmethod
    def exist_env_variable(var_name: str) -> bool:
        return var_name in os.environ
    
    @staticmethod
    def menu(options: list[str], title: str = "Menu") -> int:
        isValid: bool
        choice: str
        intChoice: int

        isValid = False
        intChoice = 0

        print(f"=== {title} ===")
        for i, option in enumerate(options, start=1):
            print(f"{i}. {option}")
        print(f"{len(options)+1}. Exit")
        while not isValid:
            choice = input(f"Select an option (1-{len(options) + 1}): ").strip()
            if choice != "":
                if choice.isdigit():
                    intChoice = int(choice)
                    if intChoice > 0 and intChoice < len(options) + 2:
                        isValid = True
                if not isValid:
                    print("Invalid choice. Please try again.")
        return intChoice
    
    @staticmethod
    def __default_validation(userInput: str) -> bool:
        return userInput != ""
    
    @staticmethod
    def is_folder_creatable(path: str) -> bool:
        try:
            os.makedirs(path, exist_ok=True)
            return True
        except Exception:
            return False

    @staticmethod
    def input_with_validation(prompt: str, validation_func: Callable[[str], bool] | None = None) -> str:
        isValid: bool
        userInput: str

        isValid = False
        userInput = ""

        if validation_func is None:
            validation_func = Helpers.__default_validation
        while not isValid:
            userInput = input(prompt).strip()
            if validation_func(userInput):
                isValid = True
            else:
                print("Invalid input. Please try again.")
        return userInput
    
    @staticmethod
    def url_parser(url: str) -> Downloader:
        url_match = re.match(r"^(http[s]?://)?([a-zA-Z.]+)/(.*)?", url)
        if url_match:
            domain = url_match.group(2).lower()
            path = url_match.group(3)

            if "spotify.com" in domain:
                spotify_match = re.search(r"(track|album|playlist)/([a-zA-Z0-9]+)", path)
                if spotify_match:
                    resource_type_str = spotify_match.group(1) 
                    if resource_type_str == "track":
                        resource_type = SpotifyResource.TRACK
                    elif resource_type_str == "album":
                        resource_type = SpotifyResource.ALBUM
                    elif resource_type_str == "playlist":
                        resource_type = SpotifyResource.PLAYLIST
                    else:
                        raise DownloadException("Unknown Spotify resource type")
                    downloader = SpotifyDownloader(resource_type, spotify_match.group(2))
                    return downloader
                else:
                    raise DownloadException("Invalid Spotify URL format")
            else:
                raise DownloadException("Unsupported domain")
        else:
            raise DownloadException("Invalid URL format")