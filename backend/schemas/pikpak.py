from typing import List, Optional
from pydantic import BaseModel


class AnimeItem(BaseModel):
    id: int
    title: str
    magnet: str


class SeasonGroup(BaseModel):
    title: str
    anime_list: List[AnimeItem]


class DownloadRequest(BaseModel):
    username: str
    password: str
    mode: str
    title: Optional[str] = None
    anime_list: Optional[List[AnimeItem]] = None
    groups: Optional[List[SeasonGroup]] = None


class PikPakCredentials(BaseModel):
    username: str
    password: str


class UpdateAnimeRequest(BaseModel):
    username: str
    password: str
    folder_id: str
    anime_list: List[AnimeItem]


class VideoUrlUpdateRequest(BaseModel):
    username: str
    password: str
    file_ids: List[str]
    folder_id: str


class DeleteAnimeRequest(BaseModel):
    username: str
    password: str
    folder_id: str
