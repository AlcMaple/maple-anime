from typing import List, Optional
from pydantic import BaseModel


class AnimeItem(BaseModel):
    id: int
    title: str
    magnet: str


class SeasonGroup(BaseModel):
    title: str
    anime_list: List[AnimeItem]


class PikPakCredentials(BaseModel):
    username: str
    password: str


class DownloadRequest(PikPakCredentials):
    mode: str
    title: Optional[str] = None
    anime_list: Optional[List[AnimeItem]] = None
    groups: Optional[List[SeasonGroup]] = None


class UpdateAnimeRequest(PikPakCredentials):
    folder_id: str
    anime_list: List[AnimeItem]


class VideoUrlUpdateRequest(PikPakCredentials):
    file_ids: List[str]
    folder_id: str


class DeleteAnimeRequest(PikPakCredentials):
    folder_id: str
