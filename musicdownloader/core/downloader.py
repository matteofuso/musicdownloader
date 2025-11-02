from enum import Enum

class DownlaodResource(Enum):
    pass

class DownloadException(Exception):
    pass

class Downloader:
    resource_type: DownlaodResource
    uri: str

    def __init__(self, resource_type: DownlaodResource, uri: str) -> None:
        self.resource_type = resource_type
        self.uri = uri

    def download(self, path: str) -> None:
        self.download_resource(path, self.uri, self.resource_type)

    @staticmethod
    def isLoggedIn() -> bool:
        return True

    @staticmethod
    def login(**kwargs: str | None) -> dict[str, str]:
        return {}

    @staticmethod
    def download_resource(path: str, uri: str, resource_type: DownlaodResource) -> None:
        raise NotImplementedError()