from typing import List, Optional
from fastapi import APIRouter, HTTPException, Body
from pydantic import BaseModel


class SearchRequest(BaseModel):
    name: str


class AnimeInfoRequest(BaseModel):
    id: str
    title: str
    status: str
    summary: Optional[str] = None
    cover_url: Optional[str] = None
    username: Optional[str] = None
    password: Optional[str] = None
