import sys
import json
import urllib.request
import urllib.parse
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import traceback
import logging
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
import uvicorn
import httpx
from pikpakapi import PikPakApi
from apis.anime_garden_api import AnimeSearch

app = FastAPI()

@app.posr("/api/search")
async def search_anime(name: str):
    try:
        anime_search = AnimeSearch()
        data = await anime_search.search_anime(name)
        return data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

def main():
    uvicorn.run(app, host="0.0.0.0", port=8000)

if __name__ == "__main__":
    main()