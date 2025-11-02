
class Metadata:
    title: str
    album_artists: list[str] | None
    artists: list[str] | None
    album_name: str | None
    album_label: str | None
    release_year: int | None
    disk_number: int | None
    track_number: int | None
    external_id: str | None
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
        external_id: str | None = None,
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
        self.external_id = external_id
        self.cover_url = cover_url