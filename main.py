from libs import enviroment, utils, spotify, youtube
from enum import Enum

# Costants
file_path = "./download"

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
    try:
        while True:
            request = utils.parse(input('Input the song to download or hit "CTRL + C" to exit: '))
            if request["type"] != "error":
                if not download_functions[Services[request["service"]]](request, file_path):
                    print("Risorsa non esistente")
            else:
                print(request["value"])
    except KeyboardInterrupt:
        pass