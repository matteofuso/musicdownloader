from musicdownloader.core.downloader import Downloader, DownlaodResource, DownloadException

class SpotifyResource(DownlaodResource):
    TRACK = "track"
    ALBUM = "album"
    PLAYLIST = "playlist"

class SpotifyDownloader(Downloader):
    @staticmethod
    def download_resource(path: str, uri: str, resource_type: DownlaodResource) -> None:
        if type(resource_type) is not SpotifyResource:
            raise DownloadException("Invalid resource type for SpotifyDownloader")
        
        print(f"Downloading {resource_type.value} from Spotify with URI: {uri}")
        
    @staticmethod
    def isLoggedIn() -> bool:
        return True