# type: ignore
from musicdownloader.core.downloader import Downloader, DownlaodResource, DownloadException
from musicdownloader.core.metadata import Metadata as FMetadata
from librespot.core import Session
from librespot.proto import Authentication_pb2 as Authentication
from librespot.metadata import TrackId, AlbumId, PlaylistId
from librespot.proto import Metadata_pb2 as Metadata
from librespot.audio.decoders import AudioQuality, VorbisOnlyAudioQuality
from base64 import b64encode, b64decode
import webbrowser

class SpotifyResource(DownlaodResource):
    TRACK = "track"
    ALBUM = "album"
    PLAYLIST = "playlist"

class SpotifyDownloader(Downloader):
    __session: Session | None = None

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
    def download_resource(path: str, uri: str, resource_type: DownlaodResource) -> None:
        if type(resource_type) is not SpotifyResource:
            raise DownloadException("Invalid resource type for SpotifyDownloader")
        match resource_type:
            case SpotifyResource.TRACK:
                SpotifyDownloader.download_track(path, uri)
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
            external_id=isrc,
            cover_url="https://i.scdn.co/image/" + max(protobuf.album.cover_group.image, key=lambda x: x.width).file_id.hex()
        )

    @staticmethod
    def download_track(path: str, uri: str) -> None:
        if not SpotifyDownloader.isLoggedIn():
            raise DownloadException("Not logged in to Spotify")

        try:
            track_id = TrackId.from_uri("spotify:track:" + uri)
            metadata_protobuf = SpotifyDownloader.__session.api().get_metadata_4_track(track_id)
        except Exception as e:
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

        print(metadata.__dict__)
        print(f"Selected quality: {quality.name}")
