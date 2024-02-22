from enum import Enum
from libs import youtube, spotify


class Source(Enum):
    Youtube = 0
    Spotify = 1


class Song:
    def __init__(self, source: Source, id: str) -> None:
        self._source = source
        self._id = id

    def Download(self) -> bool:
        if self._source == Source.Youtube:
            self._metadata, self._filename = youtube.download(self)
        elif self._source == Source.Spotify:
            self._metadata, self._filename = spotify.download(self)
        return self._metadata == dict()
