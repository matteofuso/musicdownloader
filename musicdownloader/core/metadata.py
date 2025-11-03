# type: ignore
import os
import base64
import requests
from mutagen.id3 import (
    ID3, TIT2, TPE1, TPE2, TALB, TPUB, TYER, TPOS, TRCK, APIC, ID3NoHeaderError
)
from mutagen.flac import FLAC, Picture
from mutagen.oggvorbis import OggVorbis


class Metadata:
    title: str
    album_artists: list[str] | None
    artists: list[str] | None
    album_name: str | None
    album_label: str | None
    release_year: int | None
    disk_number: int | None
    track_number: int | None
    isrc: str | None  # Changed from external_id to isrc for clarity
    cover_url: str | None

    def __init__(
        self,
        title: str,
        album_artists: list[str] | None = None,
        artists: list[str] | None = None,
        album_name: str | None = None,
        album_label: str | None = None,
        release_year: int | None = None,
        disk_number: int | None = None,
        track_number: int | None = None,
        isrc: str | None = None,
        cover_url: str | None = None,
    ) -> None:
        self.title = title
        self.album_artists = album_artists
        self.artists = artists
        self.album_name = album_name
        self.album_label = album_label
        self.release_year = release_year
        self.disk_number = disk_number
        self.track_number = track_number
        self.isrc = isrc
        self.cover_url = cover_url

    def attach(self, filename) -> None:
        ext = os.path.splitext(filename)[1].lower()
        try:
            cover_data = None
            if self.cover_url:
                response = requests.get(self.cover_url)
                if response.ok:
                    cover_data = response.content

            if ext == ".mp3":
                try:
                    audio = ID3(filename)
                except ID3NoHeaderError:
                    audio = ID3()
                audio.clear()
                audio.add(TIT2(encoding=3, text=self.title))
                if self.artists:
                    audio.add(TPE1(encoding=3, text=self.artists))
                if self.album_artists:
                    audio.add(TPE2(encoding=3, text=self.album_artists))
                if self.album_name:
                    audio.add(TALB(encoding=3, text=self.album_name))
                if self.album_label:
                    audio.add(TPUB(encoding=3, text=self.album_label))
                if self.release_year:
                    audio.add(TYER(encoding=3, text=str(self.release_year)))
                if self.disk_number:
                    audio.add(TPOS(encoding=3, text=str(self.disk_number)))
                if self.track_number:
                    audio.add(TRCK(encoding=3, text=str(self.track_number)))
                if self.isrc:
                    # ISRC is stored in TSRC frame in ID3v2.3 and later
                    from mutagen.id3 import TSRC
                    audio.add(TSRC(encoding=3, text=self.isrc))
                if cover_data:
                    audio.add(APIC(
                        encoding=3,
                        mime='image/jpeg',
                        type=3,
                        desc='Cover',
                        data=cover_data,
                    ))
                audio.save(filename, v2_version=3)

            elif ext == ".flac":
                audio = FLAC(filename)
                audio.delete()
                audio["TITLE"] = self.title
                if self.artists:
                    audio["ARTIST"] = self.artists
                if self.album_artists:
                    audio["ALBUMARTIST"] = self.album_artists
                if self.album_name:
                    audio["ALBUM"] = self.album_name
                if self.album_label:
                    audio["LABEL"] = self.album_label
                if self.release_year:
                    audio["DATE"] = str(self.release_year)
                if self.disk_number:
                    audio["DISCNUMBER"] = str(self.disk_number)
                if self.track_number:
                    audio["TRACKNUMBER"] = str(self.track_number)
                if self.isrc:
                    audio["ISRC"] = self.isrc
                if cover_data:
                    pic = Picture()
                    pic.type = 3  # Front cover
                    pic.mime = "image/jpeg"
                    pic.desc = "Cover"
                    pic.data = cover_data
                    audio.clear_pictures()
                    audio.add_picture(pic)
                audio.save()

            elif ext in [".ogg", ".oga"]:
                audio = OggVorbis(filename)
                audio.delete()
                audio["TITLE"] = self.title
                if self.artists:
                    audio["ARTIST"] = self.artists
                if self.album_artists:
                    audio["ALBUMARTIST"] = self.album_artists
                if self.album_name:
                    audio["ALBUM"] = self.album_name
                if self.album_label:
                    audio["LABEL"] = self.album_label
                if self.release_year:
                    audio["DATE"] = str(self.release_year)
                if self.disk_number:
                    audio["DISCNUMBER"] = str(self.disk_number)
                if self.track_number:
                    audio["TRACKNUMBER"] = str(self.track_number)
                if self.isrc:
                    audio["ISRC"] = self.isrc
                if cover_data:
                    pic = Picture()
                    pic.type = 3
                    pic.mime = "image/jpeg"
                    pic.desc = "Cover"
                    pic.data = cover_data
                    audio["METADATA_BLOCK_PICTURE"] = [base64.b64encode(pic.write()).decode("ascii")]
                audio.save()

        except Exception as e:
            print(f"Failed to attach tags: {e}")
