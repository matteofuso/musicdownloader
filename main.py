from musicdownloader.helpers import Helpers
from musicdownloader.core.downloader import Downloader, DownloadException

def settings_menu():
    value: int
    download_dir: str | None
    userContinue: bool
    options: list[str]

    options = [
        "Set Download Directory",
        "Login to Spotify",
        "Logout from Spotify",
    ]
    userContinue = True

    try:
        while userContinue:
            value = Helpers.menu(options, "Settings Menu")
            match value:
                case 1:
                    download_dir = Helpers.get_env_variable("DOWNLOAD_DIRECTORY")
                    if download_dir is not None:
                        print(f"Current download directory: {download_dir}")
                    strValue = Helpers.input_with_validation("Enter the download directory path: ", Helpers.is_folder_creatable)
                    Helpers.set_env_variable("DOWNLOAD_DIRECTORY", strValue)
                    print()
                case 2:
                    print("Logging in to Spotify...")
                    # todo
                    print()
                case 3:
                    print("Logging out from Spotify...")
                    # todo
                    print()
                case _:
                    userContinue = False
    except KeyboardInterrupt:
        pass

def download_menu():
    value: str
    userContinue: bool
    downloader: Downloader
    download_dir: str | None
    path: str
    
    userContinue = True
    
    try:
        while userContinue:
            value = input("Enter the URL of the music to download (or press Enter to go back): ").strip()
            if value.lower() == "":
                userContinue = False
            else:
                try:
                    downloader = Helpers.url_parser(value)
                except DownloadException as e:
                    print(f"Error in given URL: {e}")
                else:
                    if not downloader.isLoggedIn():
                        print("You are not logged in. Please log in to continue.")
                        downloader.login()
                    download_dir = Helpers.get_env_variable("DOWNLOAD_DIRECTORY")
                    if download_dir is None:
                        path = Helpers.input_with_validation("Enter the download directory path: ", Helpers.is_folder_creatable)
                        Helpers.set_env_variable("DOWNLOAD_DIRECTORY", path)
                    else:
                        path = download_dir
                    try:
                        downloader.download(path)
                        print("Download completed successfully.")
                    except DownloadException as e:
                        print(f"Download failed: {e}")
                    print()

    except KeyboardInterrupt:
        pass

def main():
    value: int
    userContinue: bool
    options: list[str]
    
    userContinue = True
    options = [
        "Download Music",
        "Settings",
    ]
    
    Helpers.load_environment()
    try:
        while userContinue:
            value = Helpers.menu(options, "Main Menu")
            print()
            match value:
                case 1:
                    download_menu()
                    print()
                case 2:
                    settings_menu()
                    print()
                case _:
                    userContinue = False
    except KeyboardInterrupt:
        pass

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        pass