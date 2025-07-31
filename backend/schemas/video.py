from typing import List, Optional
from pydantic import BaseModel
from fastapi import APIRouter, Depends, HTTPException, Request


class ProxyVideo(BaseModel):
    file_id: str
