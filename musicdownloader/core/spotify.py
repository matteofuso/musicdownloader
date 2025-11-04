# type: ignore
from musicdownloader.core.downloader import Downloader, DownlaodResource, DownloadException
from musicdownloader.core.metadata import Metadata as FMetadata
from musicdownloader.core.ffmpeg import FFMPEG
from musicdownloader.core.progress import ProgressHandler
from librespot.core import Session
from librespot.proto import Authentication_pb2 as Authentication
from librespot.metadata import TrackId, AlbumId, PlaylistId
from librespot.proto import Metadata_pb2 as Metadata
from librespot.audio.decoders import AudioQuality, VorbisOnlyAudioQuality
from collections.abc import Callable
from base64 import b64encode, b64decode
import webbrowser
import os

class SpotifyResource(DownlaodResource):
    TRACK = "track"
    ALBUM = "album"
    PLAYLIST = "playlist"

class SpotifyDownloader(Downloader):
    __session: Session | None = None
    __bitrate_map = {
        AudioQuality.VERY_HIGH: "320k",
        AudioQuality.HIGH: "160k",
        AudioQuality.NORMAL: "96k",
    }

    @staticmethod
    def login(username: str | None, credentials: str | None, typ: str | None) -> dict[str, str]:
        builder: Session.Builder

        builder = Session.Builder(Session.Configuration.Builder().set_store_credentials(False).build())
        if credentials is not None:
            try:
                builder.login_credentials = Authentication.LoginCredentials(
                    username=username,
                    auth_data=b64decode(credentials),
                    typ=int(typ)
                )
                SpotifyDownloader.__session = builder.create()
            except Exception:
                pass
        if SpotifyDownloader.__session is None or not SpotifyDownloader.__session.is_valid():
            try:
                SpotifyDownloader.__session = builder.oauth(webbrowser.open).create()
            except Exception:
                raise DownloadException("Failed to login to Spotify")
        
        return {
            "username": SpotifyDownloader.__session.ap_welcome().canonical_username,
            "credentials": b64encode(SpotifyDownloader.__session.ap_welcome().reusable_auth_credentials).decode(),
            "type": SpotifyDownloader.__session.ap_welcome().reusable_auth_credentials_type
        }

    @staticmethod
    def isLoggedIn() -> bool:
        if SpotifyDownloader.__session is None:
            return False
        return SpotifyDownloader.__session.is_valid()

    @staticmethod
    def download_resource(path: str, uri: str, resource_type: DownlaodResource, print_title: Callable[[Metadata], None] | None = None, progress: ProgressHandler | None = None) -> None:
        if type(resource_type) is not SpotifyResource:
            raise DownloadException("Invalid resource type for SpotifyDownloader")
        match resource_type:
            case SpotifyResource.TRACK:
                SpotifyDownloader.download_track(path, uri, print_title, progress)
            case SpotifyResource.ALBUM:
                pass
            case SpotifyResource.PLAYLIST:
                pass
    
    @staticmethod
    def __parse_track_metadata(protobuf) -> FMetadata:
        isrc: str | None = None
        for external in protobuf.external_id:
            if external.type == "isrc":
                isrc = external.id
                break

        return FMetadata(
            title=protobuf.name,
            album_artists=[artist.name for artist in protobuf.album.artist],
            artists=[artist.name for artist in protobuf.artist],
            album_name=protobuf.album.name,
            album_label=protobuf.album.label or None,
            release_year=protobuf.album.date.year or None,
            disk_number=protobuf.disc_number or None,
            track_number=protobuf.number or None,
            isrc=isrc,
            cover_url="https://i.scdn.co/image/" + max(protobuf.album.cover_group.image, key=lambda x: x.width).file_id.hex()
        )

    @staticmethod
    def download_track(path: str, uri: str, print_title: Callable[[Metadata], None] | None = None, progress: ProgressHandler | None = None) -> bool:
        if not SpotifyDownloader.isLoggedIn():
            raise DownloadException("Not logged in to Spotify")
        if progress is None:
            progress = ProgressHandler()

        try:
            track_id = TrackId.from_uri("spotify:track:" + uri)
            metadata_protobuf = SpotifyDownloader.__session.api().get_metadata_4_track(track_id)
        except Exception as e:
            progress.stop()
            raise DownloadException("Failed to fetch track metadata")
        metadata = SpotifyDownloader.__parse_track_metadata(metadata_protobuf)
        formats = [f.format for f in metadata_protobuf.file]

        if Metadata.AudioFile.Format.FLAC_FLAC_24BIT in formats:
            quality = AudioQuality.LOSSLESS
        elif Metadata.AudioFile.Format.FLAC_FLAC in formats:
            quality = AudioQuality.LOSSLESS
        elif Metadata.AudioFile.Format.OGG_VORBIS_320 in formats:
            quality = AudioQuality.VERY_HIGH
        elif Metadata.AudioFile.Format.OGG_VORBIS_160 in formats:
            quality = AudioQuality.HIGH
        else:
            quality = AudioQuality.NORMAL

        # Download audio stream
        if print_title is not None:
            print_title(metadata)
        filename = f"{metadata.title} - {metadata.album_artists[0]}"
        filename = Downloader._validate_filename(filename)
        # Check if track is already downloaded
        if os.path.isfile(f"{path}/{filename}.mp3") or os.path.isfile(f"{path}/{filename}.flac") or os.path.isfile(f"{path}/{filename}.ogg"):
            progress.stop()
            return True
        
        extension = "ogg" if quality != AudioQuality.LOSSLESS else "flac"
        try:
            stream = SpotifyDownloader.__session.content_feeder().load(track_id, VorbisOnlyAudioQuality(quality), False, None)
            if progress.has_task("download"):
                progress.update_task("download", total=stream.input_stream.stream().decoded_length(), visible=True)
            with open(f"{path}/{filename}.{extension}", "wb") as f:
                while True:
                    chunk = stream.input_stream.stream().read(4096)
                    if not chunk:
                        break
                    f.write(chunk)
                    if progress.has_task("download"):
                        progress.update_task("download", advance=len(chunk))
        except Exception:
            progress.stop()
            raise DownloadException("Failed to download track audio")
        
        # Post-process: convert to mp3 if needed and attach metadata
        if quality != AudioQuality.LOSSLESS:
            if not FFMPEG.is_initialized():
                raise DownloadException("FFMPEG is not initialized. Cannot convert audio to mp3.")
            try:
                if progress.has_task("convert"):
                    progress.update_task("convert", total=1, visible=True)
                FFMPEG.execute_command(['-i', f"{path}/{filename}.{extension}", '-b:a', SpotifyDownloader.__bitrate_map[quality], f"{path}/{filename}.mp3", '-y'])
                os.remove(f"{path}/{filename}.{extension}")
                extension = "mp3"
                if progress.has_task("convert"):
                    progress.update_task("convert", advance=1)
            except Exception:
                progress.stop()
                raise DownloadException("Failed to convert track audio to mp3")
        
        # Attach metadata
        try:
            if progress.has_task("metadata"):
                progress.update_task("metadata", total=1, visible=True)
            metadata.attach(f"{path}/{filename}.{extension}")
            if progress.has_task("metadata"):
                progress.update_task("metadata", advance=1)
        except Exception:
            progress.stop()
            raise DownloadException("Failed to attach metadata to track audio")
        
        progress.stop()
        return False