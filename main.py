from libs import enviroment, utils, spotify, youtube
from enum import Enum

# Check if  the environment variable is set correctly
enviroment.init()


# Initialize an enum of service
class Services(Enum):
    youtube = 0
    spotify = 1


# Initialize a dictionary mapping services to download functions
download_functions = {
    Services.youtube: youtube.download,
    Services.spotify: spotify.download,
}


# If the script is not running as a module
if __name__ == "__main__":
    request = utils.parse(
        "https://open.spotify.com/track/1dV2NyQUs4fnjIt03nsObq?si=9889900b14e44103"
    )
    download_functions[Services[request["service"]]](request)
