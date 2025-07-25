from typing import List
from pydantic import BaseModel


class EpisodeListRequest(BaseModel):
    folder_id: str


class FileDeleteRequest(BaseModel):
    username: str
    password: str
    folder_id: str
    file_ids: List[str]


class FileRenameRequest(BaseModel):
    username: str
    password: str
    folder_id: str
    file_id: str
    new_name: str
