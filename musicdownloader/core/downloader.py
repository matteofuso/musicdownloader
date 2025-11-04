from enum import Enum
from musicdownloader.core.progress import ProgressHandler
from musicdownloader.core.metadata import Metadata
from collections.abc import Callable

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

    def download(self, path: str, print_title: Callable[[Metadata], None] | None = None,  progress: ProgressHandler | None = None) -> None:
        self.download_resource(path, self.uri, self.resource_type, print_title, progress)

    @staticmethod
    def isLoggedIn() -> bool:
        return True

    @staticmethod
    def login(**kwargs: str | None) -> dict[str, str]:
        return {}

    @staticmethod
    def _validate_filename(filename: str) -> str:
        invalid_chars = '<>:"/\\|?*\0.'
        for char in invalid_chars:
            filename = filename.replace(char, '_')
        return filename.strip()

    @staticmethod
    def download_resource(path: str, uri: str, resource_type: DownlaodResource, print_title: Callable[[Metadata], None] | None = None,  progress: ProgressHandler | None = None) -> None:
        raise NotImplementedError()