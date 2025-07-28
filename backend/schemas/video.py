from typing import List, Optional
from pydantic import BaseModel
from fastapi import APIRouter, Depends, HTTPException, Request


class ProxyVideo(BaseModel):
    file_id: str
    username: Optional[str] = (None,)
    password: Optional[str] = None
    request: Request  # FastAPI请求对象
