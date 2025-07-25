from typing import List
from pydantic import BaseModel


class EpisodeListRequest(BaseModel):
    folder_id: str


class FileDeleteRequest(EpisodeListRequest):
    username: str
    password: str
    file_ids: List[str]


class FileRenameRequest(EpisodeListRequest):
    username: str
    password: str
    file_id: str
    new_name: str
