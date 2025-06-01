#!/usr/bin/env python3
"""
文件夹扫描播放版番剧服务器
重点功能：扫描所有文件夹(包括My Pack) + 优化播放功能 + 支持外部播放器
"""

import sys
import json
import urllib.request
import urllib.parse
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import traceback
import logging

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 检查依赖
print("🔍 检查系统依赖...")
try:
    from fastapi import FastAPI, HTTPException, BackgroundTasks
    from fastapi.middleware.cors import CORSMiddleware
    from fastapi.responses import HTMLResponse
    from pydantic import BaseModel
    import uvicorn

    FASTAPI_AVAILABLE = True
    print("✅ FastAPI 可用")
except ImportError as e:
    FASTAPI_AVAILABLE = False
    print(f"❌ FastAPI 不可用: {e}")

try:
    import httpx

    HTTPX_AVAILABLE = True
    print("✅ httpx 可用")
except ImportError:
    HTTPX_AVAILABLE = False
    print("⚠️ httpx 不可用，将使用urllib")

try:
    from pikpakapi import PikPakApi

    PIKPAK_AVAILABLE = True
    print("✅ PikPak API 可用")
except ImportError as e:
    PIKPAK_AVAILABLE = False
    print(f"❌ PikPak API 不可用: {e}")
    print("💡 安装命令: pip install pikpakapi")


class PikPakFolderService:
    """PikPak文件夹扫描服务 - 支持递归扫描所有文件夹"""

    def __init__(self):
        self.clients = {}
        self.debug_info = []

    def log_debug(self, message: str, data: Any = None):
        """记录调试信息"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        debug_entry = {
            "time": timestamp,
            "message": message,
            "data": data
        }
        self.debug_info.append(debug_entry)
        logger.info(f"[PikPak] {message}")
        if data:
            logger.info(f"[PikPak] Data: {data}")

    async def get_client(self, username: str, password: str):
        """获取或创建PikPak客户端"""
        client_key = f"{username}:{password}"

        if client_key not in self.clients:
            if not PIKPAK_AVAILABLE:
                return None

            self.log_debug(f"创建新的PikPak客户端: {username}")
            client = PikPakApi(username=username, password=password)
            await client.login()
            self.clients[client_key] = client
            self.log_debug("客户端创建并登录成功")

        return self.clients.get(client_key)

    async def test_connection(self, username: str, password: str) -> Dict:
        """测试PikPak连接"""
        self.log_debug(f"开始测试连接", {"username": username})

        if not PIKPAK_AVAILABLE:
            return {
                "success": False,
                "message": "PikPak API 库未安装",
                "debug_info": "需要运行: pip install pikpakapi"
            }

        try:
            client = await self.get_client(username, password)
            if client:
                return {
                    "success": True,
                    "message": "PikPak连接成功"
                }
            else:
                return {"success": False, "message": "无法创建客户端"}

        except Exception as e:
            self.log_debug("连接失败", str(e))
            return {
                "success": False,
                "message": f"PikPak连接失败: {str(e)}"
            }

    async def add_magnet_download(self, username: str, password: str, magnet: str, title: str) -> Dict:
        """添加磁力下载"""
        self.log_debug(f"添加磁力下载", {"title": title[:50]})

        if not PIKPAK_AVAILABLE:
            return {
                "success": False,
                "message": "PikPak API 库未安装"
            }

        try:
            client = await self.get_client(username, password)
            if not client:
                return {"success": False, "message": "无法获取PikPak客户端"}

            self.log_debug("调用 offline_download API")
            result = await client.offline_download(magnet)
            self.log_debug("offline_download 结果", result)

            if result:
                return {
                    "success": True,
                    "message": "磁力下载任务添加成功！",
                    "task_info": result
                }
            else:
                return {
                    "success": False,
                    "message": "添加下载任务失败 - API返回空结果"
                }

        except Exception as e:
            self.log_debug("添加下载失败", str(e))
            return {
                "success": False,
                "message": f"添加下载失败: {str(e)}"
            }

    async def get_download_tasks(self, username: str, password: str) -> Dict:
        """获取下载任务列表"""
        self.log_debug("=== 开始获取下载任务列表 ===")

        if not PIKPAK_AVAILABLE:
            return {
                "success": False,
                "tasks": [],
                "message": "PikPak API 库未安装"
            }

        try:
            client = await self.get_client(username, password)
            if not client:
                return {
                    "success": False,
                    "tasks": [],
                    "message": "无法获取PikPak客户端"
                }

            self.log_debug("调用 offline_list API")
            result = await client.offline_list()
            self.log_debug("offline_list 原始结果", result)

            if result is None:
                return {
                    "success": True,
                    "tasks": [],
                    "message": "暂无下载任务"
                }

            # 处理不同的响应格式
            tasks = []
            if isinstance(result, dict):
                tasks = result.get("tasks", [])
                if "data" in result:
                    tasks = result["data"]
            elif isinstance(result, list):
                tasks = result

            self.log_debug(f"解析后的任务数量: {len(tasks)}")

            # 格式化任务信息
            formatted_tasks = []
            for task in tasks:
                if isinstance(task, dict):
                    formatted_task = {
                        "id": task.get("id", "unknown"),
                        "name": task.get("name", task.get("title", "未知任务")),
                        "phase": task.get("phase", task.get("status", "UNKNOWN")),
                        "progress": int(task.get("progress", 0)),
                        "size": task.get("size", 0),
                        "created_time": task.get("created_time", task.get("created_at", "")),
                        "file_count": task.get("file_count", 1)
                    }
                    formatted_tasks.append(formatted_task)

            return {
                "success": True,
                "tasks": formatted_tasks,
                "message": f"获取到 {len(formatted_tasks)} 个下载任务"
            }

        except Exception as e:
            self.log_debug("获取下载任务失败", str(e))
            return {
                "success": False,
                "tasks": [],
                "message": f"获取下载任务失败: {str(e)}"
            }

    async def scan_folder_recursive(self, client, parent_id: str = "", parent_name: str = "根目录", max_depth: int = 3,
                                    current_depth: int = 0) -> List[Dict]:
        """递归扫描文件夹获取所有视频文件"""
        all_videos = []

        if current_depth >= max_depth:
            self.log_debug(f"达到最大扫描深度 {max_depth}，停止扫描")
            return all_videos

        try:
            self.log_debug(f"扫描文件夹: {parent_name} (深度: {current_depth})")

            # 获取当前文件夹的文件列表
            result = await client.file_list(parent_id=parent_id)

            if result is None:
                self.log_debug(f"文件夹 {parent_name} 为空")
                return all_videos

            # 处理响应格式
            files = []
            if isinstance(result, dict):
                files = result.get("files", [])
                if "data" in result:
                    files = result["data"]
            elif isinstance(result, list):
                files = result

            self.log_debug(f"文件夹 {parent_name} 包含 {len(files)} 个项目")

            video_extensions = [".mp4", ".mkv", ".avi", ".mov", ".m4v", ".webm", ".flv", ".rmvb", ".wmv"]

            for file in files:
                if not isinstance(file, dict):
                    continue

                file_name = file.get("name", "")
                file_kind = file.get("kind", "")
                file_type = file.get("type", "")

                # 检查是否为文件夹
                is_folder = file_kind == "drive#folder" or file_type == "folder"

                if is_folder:
                    # 递归扫描子文件夹
                    folder_path = f"{parent_name}/{file_name}" if parent_name != "根目录" else file_name
                    self.log_debug(f"发现子文件夹: {folder_path}")

                    sub_videos = await self.scan_folder_recursive(
                        client,
                        parent_id=file.get("id", ""),
                        parent_name=folder_path,
                        max_depth=max_depth,
                        current_depth=current_depth + 1
                    )
                    all_videos.extend(sub_videos)

                else:
                    # 检查是否为视频文件
                    is_file = file_kind == "drive#file" or file_type == "file"
                    is_video = any(ext in file_name.lower() for ext in video_extensions)

                    if is_file and is_video:
                        folder_path = parent_name if parent_name != "根目录" else "根目录"

                        formatted_file = {
                            "id": file.get("id", file.get("file_id", "unknown")),
                            "name": file_name,
                            "size": int(file.get("size", 0)),
                            "kind": file_kind,
                            "created_time": file.get("created_time", file.get("created_at", "")),
                            "mime_type": file.get("mime_type", "video/unknown"),
                            "thumbnail": file.get("thumbnail", ""),
                            "hash": file.get("hash", ""),
                            "folder_path": folder_path  # 记录文件所在文件夹
                        }
                        all_videos.append(formatted_file)
                        self.log_debug(f"找到视频文件: {folder_path}/{file_name}")

        except Exception as e:
            self.log_debug(f"扫描文件夹 {parent_name} 失败", str(e))

        return all_videos

    async def get_all_video_files(self, username: str, password: str) -> Dict:
        """获取所有视频文件 - 递归扫描版本"""
        self.log_debug("=== 开始递归扫描所有视频文件 ===")

        if not PIKPAK_AVAILABLE:
            return {
                "success": False,
                "videos": [],
                "message": "PikPak API 库未安装"
            }

        try:
            client = await self.get_client(username, password)
            if not client:
                return {
                    "success": False,
                    "videos": [],
                    "message": "无法获取PikPak客户端"
                }

            # 递归扫描所有文件夹
            all_videos = await self.scan_folder_recursive(client, parent_id="", parent_name="根目录", max_depth=3)

            # 按创建时间排序，最新的在前
            all_videos.sort(key=lambda x: x.get("created_time", ""), reverse=True)

            self.log_debug(f"总共找到 {len(all_videos)} 个视频文件")

            return {
                "success": True,
                "videos": all_videos,
                "message": f"找到 {len(all_videos)} 个视频文件（递归扫描）",
                "scan_type": "recursive"
            }

        except Exception as e:
            error_msg = str(e)
            self.log_debug("递归扫描视频文件失败", error_msg)

            return {
                "success": False,
                "videos": [],
                "message": f"扫描视频文件失败: {error_msg}"
            }

    async def get_video_play_url(self, username: str, password: str, file_id: str, file_name: str) -> Dict:
        """获取视频播放链接 - 增强版本"""
        self.log_debug(f"=== 获取播放链接: {file_name} ===")

        if not PIKPAK_AVAILABLE:
            return {
                "success": False,
                "message": "PikPak API 库未安装"
            }

        try:
            client = await self.get_client(username, password)
            if not client:
                return {
                    "success": False,
                    "message": "无法获取PikPak客户端"
                }

            # 方法1：尝试获取流媒体播放链接
            self.log_debug("尝试获取流媒体播放链接")
            try:
                file_info = await client.get_file_info(file_id)
                self.log_debug("文件信息", file_info)

                if file_info and "medias" in file_info:
                    medias = file_info["medias"]
                    self.log_debug(f"找到 {len(medias)} 个媒体链接")

                    for i, media in enumerate(medias):
                        if "link" in media and media.get("is_visible", True):
                            streaming_url = media["link"]["url"]

                            # 检查链接类型
                            quality = media.get("quality", "unknown")
                            width = media.get("width", 0)
                            height = media.get("height", 0)

                            self.log_debug(f"流媒体链接 {i + 1}: {quality} ({width}x{height})")

                            return {
                                "success": True,
                                "play_url": streaming_url,
                                "type": "streaming",
                                "file_name": file_name,
                                "quality": quality,
                                "resolution": f"{width}x{height}" if width and height else "unknown",
                                "message": "获取流媒体链接成功"
                            }
            except Exception as e:
                self.log_debug("获取流媒体链接失败", str(e))

            # 方法2：获取下载链接
            self.log_debug("尝试获取下载链接")
            try:
                download_result = await client.get_download_url(file_id)
                self.log_debug("下载链接结果", download_result)

                if download_result:
                    # 尝试不同的字段名
                    download_url = None
                    for field in ["web_content_link", "download_url", "url", "link"]:
                        if field in download_result:
                            download_url = download_result[field]
                            break

                    if download_url:
                        return {
                            "success": True,
                            "play_url": download_url,
                            "type": "download",
                            "file_name": file_name,
                            "message": "获取下载链接成功"
                        }
            except Exception as e:
                self.log_debug("获取下载链接失败", str(e))

            return {
                "success": False,
                "message": "无法获取播放链接 - 所有方法都失败了",
                "file_name": file_name
            }

        except Exception as e:
            error_msg = str(e)
            self.log_debug("获取播放链接异常", error_msg)

            return {
                "success": False,
                "message": f"获取播放链接失败: {error_msg}",
                "file_name": file_name
            }


class AnimeGardenService:
    """AnimeGarden服务"""

    def search_resources_sync(self, anime_name: str) -> List[Dict]:
        try:
            url = "https://api.animes.garden/resources"
            payload = {"include": [anime_name]}
            data = json.dumps(payload).encode('utf-8')

            req = urllib.request.Request(
                url,
                data=data,
                headers={
                    'Content-Type': 'application/json',
                    'User-Agent': 'Maple-Anime/1.0'
                }
            )

            with urllib.request.urlopen(req, timeout=15) as response:
                result = response.read().decode('utf-8')

            api_data = json.loads(result)
            resources = api_data.get('resources', [])

            exact_matches = [
                resource for resource in resources
                if anime_name in resource.get("title", "")
            ]

            exact_matches.sort(key=lambda x: x.get("size", 0), reverse=True)
            return exact_matches[:20]

        except Exception as e:
            raise Exception(f"搜索资源失败: {str(e)}")


# FastAPI应用
if FASTAPI_AVAILABLE:

    class PikPakCredentials(BaseModel):
        username: str
        password: str


    class DownloadRequest(BaseModel):
        magnet: str
        title: str
        credentials: PikPakCredentials


    class PlayUrlRequest(BaseModel):
        file_id: str
        file_name: str
        credentials: PikPakCredentials


    class SearchRequest(BaseModel):
        anime_name: str


    app = FastAPI(title="Folder Scan Anime Server", description="文件夹扫描播放版番剧服务器")

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # 服务实例
    pikpak_service = PikPakFolderService()
    anime_garden_service = AnimeGardenService()


    @app.get("/", response_class=HTMLResponse)
    async def get_homepage():
        return """
        <!DOCTYPE html>
        <html lang="zh-CN">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>📁 Folder Scan Anime - 文件夹扫描版</title>
            <style>
                * { margin: 0; padding: 0; box-sizing: border-box; }
                body { 
                    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; 
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    min-height: 100vh; color: #333;
                }
                .container { max-width: 1400px; margin: 0 auto; padding: 20px; }
                .header { text-align: center; margin-bottom: 30px; color: white; }
                .header h1 { font-size: 3em; margin-bottom: 10px; text-shadow: 2px 2px 4px rgba(0,0,0,0.3); }
                .header p { font-size: 1.2em; opacity: 0.9; }

                .main-grid { display: grid; grid-template-columns: 1fr 350px; gap: 20px; }
                .content-area { display: grid; grid-template-columns: 1fr; gap: 20px; }

                .section { 
                    background: rgba(255,255,255,0.95); padding: 25px; border-radius: 15px; 
                    box-shadow: 0 5px 20px rgba(0,0,0,0.1); transition: transform 0.3s ease;
                }
                .section:hover { transform: translateY(-5px); }
                .section h3 { margin-bottom: 15px; color: #444; font-size: 1.4em; }

                .sidebar { 
                    background: rgba(255,255,255,0.95); padding: 25px; border-radius: 15px;
                    box-shadow: 0 5px 20px rgba(0,0,0,0.1); height: fit-content;
                }

                .button { 
                    background: linear-gradient(45deg, #667eea, #764ba2); color: white; border: none; 
                    padding: 12px 25px; border-radius: 25px; cursor: pointer; margin: 8px 5px; 
                    transition: all 0.3s ease; font-size: 14px; display: inline-block;
                }
                .button:hover { transform: translateY(-2px); box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4); }
                .button.small { padding: 8px 15px; font-size: 12px; margin: 3px; }
                .button.success { background: linear-gradient(45deg, #4CAF50, #45a049); }
                .button.warning { background: linear-gradient(45deg, #FF9800, #f57c00); }
                .button.info { background: linear-gradient(45deg, #2196F3, #1976D2); }

                .input { 
                    width: 100%; padding: 12px; border: 2px solid #ddd; border-radius: 8px; 
                    margin: 8px 0; transition: border-color 0.3s ease;
                }
                .input:focus { outline: none; border-color: #667eea; }

                .result { 
                    background: #fff; border: 1px solid #ddd; padding: 20px; margin: 15px 0; 
                    border-radius: 10px; max-height: 500px; overflow-y: auto; 
                }

                .debug-panel {
                    background: #1a1a1a; color: #00ff00; padding: 15px; border-radius: 8px;
                    font-family: 'Courier New', monospace; font-size: 12px; max-height: 250px; overflow-y: auto;
                    margin: 15px 0; white-space: pre-wrap;
                }

                .status-indicator {
                    display: inline-block; width: 12px; height: 12px; border-radius: 50%; margin-right: 8px;
                }
                .status-success { background: #4CAF50; }
                .status-error { background: #f44336; }
                .status-warning { background: #FF9800; }

                .anime-card {
                    border: 1px solid #eee; padding: 15px; margin: 10px 0; border-radius: 8px; 
                    background: #f9f9f9; transition: all 0.3s ease;
                }
                .anime-card:hover { background: #f0f8ff; border-color: #667eea; }

                .video-card {
                    border: 1px solid #ddd; padding: 15px; margin: 10px 0; border-radius: 8px; 
                    background: #f9f9f9; font-size: 12px; position: relative;
                }
                .video-card.my-pack { border-color: #4CAF50; background: #e8f5e9; }
                .video-card .folder-badge {
                    position: absolute; top: 5px; right: 5px;
                    background: #667eea; color: white; padding: 2px 8px;
                    border-radius: 10px; font-size: 10px;
                }
                .video-card.my-pack .folder-badge { background: #4CAF50; }

                .task-card {
                    border: 1px solid #ddd; padding: 12px; margin: 8px 0; border-radius: 8px; 
                    background: #f9f9f9; font-size: 12px;
                }
                .task-card.complete { border-color: #4CAF50; background: #e8f5e9; }
                .task-card.running { border-color: #FF9800; background: #fff3e0; }

                .progress-bar {
                    width: 100%; height: 8px; background: #eee; border-radius: 4px; 
                    overflow: hidden; margin: 5px 0;
                }
                .progress-fill { height: 100%; background: #4CAF50; transition: width 0.3s ease; }

                .badge {
                    display: inline-block; background: #667eea; color: white;
                    padding: 4px 8px; border-radius: 12px; font-size: 12px; margin: 2px;
                }
                .badge.success { background: #4CAF50; }
                .badge.error { background: #f44336; }
                .badge.warning { background: #FF9800; }
                .badge.info { background: #2196F3; }

                .player-section {
                    background: #000; border-radius: 10px; padding: 20px; margin: 20px 0;
                }
                .video-player {
                    width: 100%; max-width: 800px; height: 450px; border-radius: 10px;
                }

                .checkbox { margin: 5px 10px 5px 0; }

                .success { color: #2e7d32; }
                .error { color: #d32f2f; }
                .loading { color: #666; }

                @media (max-width: 768px) {
                    .main-grid { grid-template-columns: 1fr; }
                    .header h1 { font-size: 2em; }
                }
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>📁 Folder Scan Anime</h1>
                    <p>文件夹扫描版 | 支持My Pack文件夹 ✅ | 递归扫描所有文件夹 ✅ | 在线播放优化 ✅</p>
                </div>

                <div class="main-grid">
                    <div class="content-area">
                        <!-- 番剧搜索 -->
                        <div class="section">
                            <h3>🔍 番剧资源搜索</h3>
                            <input type="text" id="animeSearchInput" class="input" 
                                   placeholder="输入番剧名称" value="赛马娘">
                            <button class="button" onclick="searchAnime()">🔍 搜索番剧资源</button>
                            <div id="searchResult" class="result" style="display: none;"></div>
                        </div>

                        <!-- 在线播放器 -->
                        <div class="section" id="playerSection" style="display: none;">
                            <h3>🎬 在线播放器</h3>
                            <div id="playerContainer" class="player-section"></div>
                        </div>

                        <!-- 调试面板 -->
                        <div class="section">
                            <h3>🔧 调试信息面板</h3>
                            <div style="margin-bottom: 15px;">
                                <label><input type="checkbox" id="autoDebug" class="checkbox" checked> 自动显示调试信息</label>
                                <button class="button small" onclick="clearDebugLog()">清空日志</button>
                                <button class="button small success" onclick="testFolderScan()">🧪 测试文件夹扫描</button>
                            </div>
                            <div id="debugLog" class="debug-panel">等待操作...</div>
                        </div>
                    </div>

                    <!-- 侧边栏 -->
                    <div class="sidebar">
                        <!-- PikPak配置 -->
                        <h3>🔐 PikPak 配置</h3>
                        <input type="text" id="pikpakUsername" class="input" 
                               placeholder="PikPak 用户名">
                        <input type="password" id="pikpakPassword" class="input" 
                               placeholder="PikPak 密码">
                        <div style="margin: 10px 0;">
                            <label><input type="checkbox" id="saveCredentials" class="checkbox"> 保存账号密码</label>
                        </div>
                        <button class="button success" onclick="testPikPakConnection()">🔗 测试连接</button>
                        <button class="button small" onclick="clearCredentials()">🗑️ 清除保存</button>

                        <div id="pikpakStatus" style="margin: 15px 0;">
                            <div class="status-indicator status-warning"></div>
                            <span>未连接</span>
                        </div>

                        <!-- 下载任务 -->
                        <h3 style="margin-top: 30px;">📥 下载任务</h3>
                        <button class="button small success" onclick="refreshTasks()">🔄 刷新任务</button>
                        <div id="tasksList" style="margin-top: 10px;"></div>

                        <!-- 视频文件 -->
                        <h3 style="margin-top: 30px;">🎥 视频文件</h3>
                        <button class="button small success" onclick="scanAllFolders()">📁 扫描所有文件夹</button>
                        <button class="button small info" onclick="scanMyPackFolder()">📦 扫描My Pack文件夹</button>
                        <div id="videosList" style="margin-top: 10px;"></div>
                    </div>
                </div>
            </div>

            <script>
                let debugMessages = [];

                // 页面加载时执行
                window.onload = function() {
                    loadSavedCredentials();
                    addDebugMessage('📁 文件夹扫描版系统初始化完成');
                    addDebugMessage('✅ 支持My Pack文件夹扫描');
                    addDebugMessage('✅ 支持递归扫描所有文件夹');
                    addDebugMessage('✅ 优化播放功能');
                };

                function addDebugMessage(message, data = null) {
                    const timestamp = new Date().toLocaleTimeString();
                    const debugEntry = {
                        time: timestamp,
                        message: message,
                        data: data
                    };
                    debugMessages.push(debugEntry);

                    if (document.getElementById('autoDebug').checked) {
                        updateDebugDisplay();
                    }
                }

                function updateDebugDisplay() {
                    const debugLog = document.getElementById('debugLog');
                    const recent = debugMessages.slice(-15);

                    let logText = '';
                    recent.forEach(entry => {
                        logText += `[${entry.time}] ${entry.message}\\n`;
                        if (entry.data) {
                            logText += `    数据: ${JSON.stringify(entry.data, null, 2)}\\n`;
                        }
                        logText += '\\n';
                    });

                    debugLog.textContent = logText;
                    debugLog.scrollTop = debugLog.scrollHeight;
                }

                function clearDebugLog() {
                    debugMessages = [];
                    document.getElementById('debugLog').textContent = '调试日志已清空';
                }

                function saveCredentials() {
                    if (document.getElementById('saveCredentials').checked) {
                        const username = document.getElementById('pikpakUsername').value;
                        const password = document.getElementById('pikpakPassword').value;
                        localStorage.setItem('pikpak_username', username);
                        localStorage.setItem('pikpak_password', password);
                        addDebugMessage('💾 账号密码已保存到本地');
                    }
                }

                function loadSavedCredentials() {
                    const savedUsername = localStorage.getItem('pikpak_username');
                    const savedPassword = localStorage.getItem('pikpak_password');

                    if (savedUsername && savedPassword) {
                        document.getElementById('pikpakUsername').value = savedUsername;
                        document.getElementById('pikpakPassword').value = savedPassword;
                        document.getElementById('saveCredentials').checked = true;
                        addDebugMessage('📂 已加载保存的账号密码');
                    }
                }

                function clearCredentials() {
                    localStorage.removeItem('pikpak_username');
                    localStorage.removeItem('pikpak_password');
                    document.getElementById('pikpakUsername').value = '';
                    document.getElementById('pikpakPassword').value = '';
                    document.getElementById('saveCredentials').checked = false;
                    addDebugMessage('🗑️ 已清除保存的账号密码');
                }

                function getPikPakCredentials() {
                    const username = document.getElementById('pikpakUsername').value.trim();
                    const password = document.getElementById('pikpakPassword').value.trim();

                    if (!username || !password) {
                        alert('请先填写 PikPak 账号信息');
                        return null;
                    }

                    return { username, password };
                }

                async function testPikPakConnection() {
                    const credentials = getPikPakCredentials();
                    if (!credentials) return;

                    const statusDiv = document.getElementById('pikpakStatus');
                    statusDiv.innerHTML = '<div class="status-indicator status-warning"></div><span>连接测试中...</span>';

                    addDebugMessage('🔗 开始测试PikPak连接', { username: credentials.username });

                    try {
                        const response = await fetch('/api/pikpak/test', {
                            method: 'POST',
                            headers: { 'Content-Type': 'application/json' },
                            body: JSON.stringify(credentials)
                        });

                        const data = await response.json();
                        addDebugMessage('🔗 PikPak连接测试结果', data);

                        if (data.success) {
                            statusDiv.innerHTML = '<div class="status-indicator status-success"></div><span>✅ 连接成功</span>';
                            saveCredentials();
                            // 自动扫描所有文件夹
                            scanAllFolders();
                        } else {
                            statusDiv.innerHTML = `<div class="status-indicator status-error"></div><span>❌ ${data.message}</span>`;
                        }

                    } catch (error) {
                        statusDiv.innerHTML = '<div class="status-indicator status-error"></div><span>❌ 连接错误</span>';
                        addDebugMessage('🔗 PikPak连接测试异常', error.message);
                    }
                }

                async function searchAnime() {
                    const animeName = document.getElementById('animeSearchInput').value.trim();
                    const resultDiv = document.getElementById('searchResult');

                    if (!animeName) return;

                    resultDiv.style.display = 'block';
                    resultDiv.innerHTML = '<span class="loading">🔍 搜索番剧资源中...</span>';

                    addDebugMessage('🔍 开始搜索番剧', { anime_name: animeName });

                    try {
                        const response = await fetch('/api/search/resources', {
                            method: 'POST',
                            headers: { 'Content-Type': 'application/json' },
                            body: JSON.stringify({ anime_name: animeName })
                        });

                        const data = await response.json();
                        addDebugMessage('🔍 搜索结果', { count: data.length });

                        if (response.ok) {
                            if (data.length === 0) {
                                resultDiv.innerHTML = '<span class="error">❌ 没有找到相关资源</span>';
                            } else {
                                let html = `<span class="success">✅ 找到 ${data.length} 个资源</span><br><br>`;

                                data.forEach((item, index) => {
                                    const sizeMB = (item.size / 1024 / 1024).toFixed(1);
                                    html += `
                                        <div class="anime-card">
                                            <strong>${item.title}</strong><br>
                                            <span class="badge">${sizeMB}MB</span>
                                            <span class="badge success">${item.fansub?.name || '未知字幕组'}</span><br>
                                            <small style="color: #666; word-break: break-all; display: block; margin: 8px 0;">
                                                磁力: ${item.magnet.substring(0, 100)}...
                                            </small>
                                            <button class="button small success" onclick="downloadToCloudPan('${item.magnet.replace(/'/g, "\\'")}', '${item.title.replace(/'/g, "\\'")}')">
                                                📥 下载到PikPak
                                            </button>
                                        </div>
                                    `;
                                });
                                resultDiv.innerHTML = html;
                            }
                        } else {
                            resultDiv.innerHTML = `<span class="error">❌ 搜索失败: ${data.detail}</span>`;
                        }
                    } catch (error) {
                        resultDiv.innerHTML = `<span class="error">❌ 网络错误: ${error.message}</span>`;
                        addDebugMessage('🔍 搜索番剧异常', error.message);
                    }
                }

                async function downloadToCloudPan(magnet, title) {
                    const credentials = getPikPakCredentials();
                    if (!credentials) return;

                    addDebugMessage('📥 开始下载到PikPak', { title: title.substring(0, 50) });

                    try {
                        const response = await fetch('/api/pikpak/download', {
                            method: 'POST',
                            headers: { 'Content-Type': 'application/json' },
                            body: JSON.stringify({
                                magnet: magnet,
                                title: title,
                                credentials: credentials
                            })
                        });

                        const data = await response.json();
                        addDebugMessage('📥 下载结果', data);

                        if (data.success) {
                            alert('✅ ' + data.message + '\\n\\n文件将下载到My Pack文件夹');
                            setTimeout(refreshTasks, 2000);
                        } else {
                            alert('❌ ' + data.message);
                        }

                    } catch (error) {
                        alert('❌ 下载失败: ' + error.message);
                        addDebugMessage('📥 下载异常', error.message);
                    }
                }

                async function refreshTasks() {
                    const credentials = getPikPakCredentials();
                    if (!credentials) return;

                    const tasksList = document.getElementById('tasksList');
                    tasksList.innerHTML = '<span class="loading">🔄 加载任务中...</span>';

                    addDebugMessage('📥 开始刷新下载任务');

                    try {
                        const response = await fetch('/api/pikpak/tasks', {
                            method: 'POST',
                            headers: { 'Content-Type': 'application/json' },
                            body: JSON.stringify(credentials)
                        });

                        const data = await response.json();
                        addDebugMessage('📥 任务列表结果', { 
                            success: data.success, 
                            task_count: data.tasks ? data.tasks.length : 0,
                            message: data.message 
                        });

                        if (data.success) {
                            if (data.tasks.length === 0) {
                                tasksList.innerHTML = '<p style="color: #999; font-size: 12px;">暂无下载任务</p>';
                            } else {
                                let html = '';
                                data.tasks.forEach((task, index) => {
                                    const progress = task.progress || 0;
                                    const isComplete = task.phase === 'PHASE_TYPE_COMPLETE';
                                    const isRunning = task.phase === 'PHASE_TYPE_RUNNING';
                                    const statusText = isComplete ? '✅ 完成' : 
                                                      isRunning ? '⏳ 下载中' : '⏸️ 等待';

                                    const cardClass = isComplete ? 'task-card complete' : 
                                                     isRunning ? 'task-card running' : 'task-card';

                                    html += `
                                        <div class="${cardClass}">
                                            <div style="font-weight: bold; margin-bottom: 5px;">
                                                ${task.name.substring(0, 35)}...
                                            </div>
                                            <div style="color: #666; margin-bottom: 8px;">
                                                ${statusText} | 进度: ${progress}%
                                            </div>
                                            <div class="progress-bar">
                                                <div class="progress-fill" style="width: ${progress}%"></div>
                                            </div>
                                            ${isComplete ? '<button class="button small info" onclick="scanAllFolders()" style="margin-top: 5px;">📁 刷新视频文件</button>' : ''}
                                        </div>
                                    `;
                                });
                                tasksList.innerHTML = html;
                            }
                        } else {
                            tasksList.innerHTML = `<p style="color: #d32f2f; font-size: 12px;">${data.message}</p>`;
                        }

                    } catch (error) {
                        tasksList.innerHTML = '<span class="error">❌ 加载失败</span>';
                        addDebugMessage('📥 刷新任务异常', error.message);
                    }
                }

                async function scanAllFolders() {
                    const credentials = getPikPakCredentials();
                    if (!credentials) return;

                    const videosList = document.getElementById('videosList');
                    videosList.innerHTML = '<span class="loading">📁 递归扫描所有文件夹中...</span>';

                    addDebugMessage('📁 开始递归扫描所有文件夹');

                    try {
                        const response = await fetch('/api/pikpak/scan-all-videos', {
                            method: 'POST',
                            headers: { 'Content-Type': 'application/json' },
                            body: JSON.stringify(credentials)
                        });

                        const data = await response.json();
                        addDebugMessage('📁 文件夹扫描结果', { 
                            success: data.success, 
                            video_count: data.videos ? data.videos.length : 0,
                            message: data.message 
                        });

                        if (data.success) {
                            if (data.videos.length === 0) {
                                videosList.innerHTML = '<p style="color: #999; font-size: 12px;">未找到视频文件</p>';
                            } else {
                                let html = `<div style="margin-bottom: 10px; font-size: 11px; color: #666;">找到 ${data.videos.length} 个视频文件</div>`;

                                data.videos.forEach((video, index) => {
                                    const sizeMB = (video.size / 1024 / 1024).toFixed(1);
                                    const isMyPack = video.folder_path.includes('My Pack');
                                    const cardClass = isMyPack ? 'video-card my-pack' : 'video-card';

                                    html += `
                                        <div class="${cardClass}">
                                            <div class="folder-badge">${video.folder_path}</div>
                                            <div style="font-weight: bold; margin-bottom: 5px; margin-right: 80px;">
                                                ${video.name.substring(0, 25)}...
                                            </div>
                                            <div style="color: #666; margin-bottom: 8px; font-size: 11px;">
                                                📏 ${sizeMB}MB | 🕒 ${video.created_time ? new Date(video.created_time).toLocaleDateString() : '未知'}
                                            </div>
                                            <button class="button small success" onclick="playVideo('${video.id}', '${video.name.replace(/'/g, "\\'")}')">
                                                🎬 在线播放
                                            </button>
                                            <button class="button small info" onclick="openWithIINA('${video.id}', '${video.name.replace(/'/g, "\\'")}')">
                                                📱 IINA播放
                                            </button>
                                        </div>
                                    `;
                                });
                                videosList.innerHTML = html;
                            }
                        } else {
                            videosList.innerHTML = `<p style="color: #d32f2f; font-size: 12px;">${data.message}</p>`;
                        }

                    } catch (error) {
                        videosList.innerHTML = '<span class="error">❌ 扫描失败</span>';
                        addDebugMessage('📁 文件夹扫描异常', error.message);
                    }
                }

                async function scanMyPackFolder() {
                    addDebugMessage('📦 扫描My Pack文件夹');
                    // 现在和扫描所有文件夹功能一样，因为我们已经递归扫描了
                    scanAllFolders();
                }

                async function playVideo(fileId, fileName) {
                    const credentials = getPikPakCredentials();
                    if (!credentials) return;

                    addDebugMessage('🎬 开始在线播放', { file_id: fileId, file_name: fileName });

                    const playerSection = document.getElementById('playerSection');
                    const playerContainer = document.getElementById('playerContainer');

                    playerContainer.innerHTML = '<span class="loading">🎬 获取播放链接中...</span>';
                    playerSection.style.display = 'block';

                    try {
                        const response = await fetch('/api/pikpak/play-url', {
                            method: 'POST',
                            headers: { 'Content-Type': 'application/json' },
                            body: JSON.stringify({
                                file_id: fileId,
                                file_name: fileName,
                                credentials: credentials
                            })
                        });

                        const data = await response.json();
                        addDebugMessage('🎬 播放链接结果', data);

                        if (data.success) {
                            const playUrl = data.play_url;
                            const linkType = data.type === 'streaming' ? '流媒体播放' : '下载播放';
                            const quality = data.quality || 'unknown';
                            const resolution = data.resolution || 'unknown';

                            playerContainer.innerHTML = `
                                <h4 style="color: white; margin-bottom: 15px;">🎬 ${fileName}</h4>
                                <div style="margin-bottom: 15px;">
                                    <span class="badge ${data.type === 'streaming' ? 'success' : 'info'}">${linkType}</span>
                                    ${quality !== 'unknown' ? `<span class="badge info">${quality}</span>` : ''}
                                    ${resolution !== 'unknown' ? `<span class="badge info">${resolution}</span>` : ''}
                                </div>
                                <video class="video-player" controls autoplay>
                                    <source src="${playUrl}" type="video/mp4">
                                    <source src="${playUrl}" type="video/webm">
                                    <source src="${playUrl}" type="video/x-matroska">
                                    您的浏览器不支持视频播放。
                                </video>
                                <div style="margin-top: 15px;">
                                    <a href="${playUrl}" target="_blank" class="button small">🔗 直接访问链接</a>
                                    <button class="button small" onclick="downloadVideo('${playUrl}', '${fileName}')">💾 下载视频</button>
                                    <button class="button small warning" onclick="openWithVLC('${playUrl}')">🎥 VLC播放</button>
                                </div>
                            `;
                        } else {
                            playerContainer.innerHTML = `<span class="error">❌ ${data.message}</span>`;
                        }

                    } catch (error) {
                        playerContainer.innerHTML = `<span class="error">❌ 播放失败: ${error.message}</span>`;
                        addDebugMessage('🎬 播放异常', error.message);
                    }
                }

                async function openWithIINA(fileId, fileName) {
                    const credentials = getPikPakCredentials();
                    if (!credentials) return;

                    addDebugMessage('📱 尝试使用IINA播放', { file_id: fileId, file_name: fileName });

                    try {
                        const response = await fetch('/api/pikpak/play-url', {
                            method: 'POST',
                            headers: { 'Content-Type': 'application/json' },
                            body: JSON.stringify({
                                file_id: fileId,
                                file_name: fileName,
                                credentials: credentials
                            })
                        });

                        const data = await response.json();

                        if (data.success) {
                            const playUrl = data.play_url;
                            // 尝试使用IINA URL scheme
                            const iinaUrl = `iina://weblink?url=${encodeURIComponent(playUrl)}`;

                            addDebugMessage('📱 生成IINA链接', { iina_url: iinaUrl });

                            // 创建一个隐藏的链接并点击
                            const link = document.createElement('a');
                            link.href = iinaUrl;
                            link.style.display = 'none';
                            document.body.appendChild(link);
                            link.click();
                            document.body.removeChild(link);

                            // 显示提示
                            alert(`📱 正在尝试使用IINA播放:\\n\\n文件: ${fileName}\\n\\n如果IINA没有自动打开，请确保已安装IINA播放器。`);
                        } else {
                            alert('❌ 无法获取播放链接: ' + data.message);
                        }

                    } catch (error) {
                        alert('❌ IINA播放失败: ' + error.message);
                        addDebugMessage('📱 IINA播放异常', error.message);
                    }
                }

                function openWithVLC(playUrl) {
                    // 尝试使用VLC URL scheme
                    const vlcUrl = `vlc://${playUrl}`;
                    addDebugMessage('🎥 尝试使用VLC播放', { vlc_url: vlcUrl });

                    const link = document.createElement('a');
                    link.href = vlcUrl;
                    link.style.display = 'none';
                    document.body.appendChild(link);
                    link.click();
                    document.body.removeChild(link);

                    // 同时在新窗口打开，作为备用
                    setTimeout(() => {
                        window.open(playUrl, '_blank');
                    }, 1000);
                }

                function downloadVideo(url, fileName) {
                    addDebugMessage('💾 开始下载视频', { file_name: fileName });
                    const a = document.createElement('a');
                    a.href = url;
                    a.download = fileName;
                    a.target = '_blank';
                    document.body.appendChild(a);
                    a.click();
                    document.body.removeChild(a);
                }

                async function testFolderScan() {
                    addDebugMessage('🧪 开始测试文件夹扫描功能');

                    const credentials = getPikPakCredentials();
                    if (!credentials) {
                        addDebugMessage('🧪 测试中止：缺少PikPak账号信息');
                        return;
                    }

                    // 测试连接
                    addDebugMessage('🧪 测试1: PikPak连接');
                    await testPikPakConnection();

                    await new Promise(resolve => setTimeout(resolve, 1000));

                    // 测试文件夹扫描
                    addDebugMessage('🧪 测试2: 文件夹扫描');
                    await scanAllFolders();

                    addDebugMessage('🧪 文件夹扫描测试完成');
                }
            </script>
        </body>
        </html>
        """


    # API端点
    @app.post("/api/pikpak/test")
    async def test_pikpak(credentials: PikPakCredentials):
        result = await pikpak_service.test_connection(credentials.username, credentials.password)
        return result


    @app.post("/api/search/resources")
    async def search_resources(request: SearchRequest):
        try:
            results = anime_garden_service.search_resources_sync(request.anime_name)
            return results
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))


    @app.post("/api/pikpak/download")
    async def download_to_pikpak(request: DownloadRequest):
        result = await pikpak_service.add_magnet_download(
            request.credentials.username,
            request.credentials.password,
            request.magnet,
            request.title
        )
        return result


    @app.post("/api/pikpak/tasks")
    async def get_pikpak_tasks(credentials: PikPakCredentials):
        result = await pikpak_service.get_download_tasks(credentials.username, credentials.password)
        return result


    @app.post("/api/pikpak/scan-all-videos")
    async def scan_all_videos(credentials: PikPakCredentials):
        result = await pikpak_service.get_all_video_files(credentials.username, credentials.password)
        return result


    @app.post("/api/pikpak/play-url")
    async def get_play_url(request: PlayUrlRequest):
        result = await pikpak_service.get_video_play_url(
            request.credentials.username,
            request.credentials.password,
            request.file_id,
            request.file_name
        )
        return result


    @app.get("/health")
    async def health_check():
        return {
            "status": "ok",
            "pikpak_available": PIKPAK_AVAILABLE,
            "httpx_available": HTTPX_AVAILABLE,
            "message": "Folder Scan Anime Server - 文件夹扫描版"
        }


    def run_server():
        print("📁 启动文件夹扫描版番剧服务器")
        print("=" * 60)
        print("🌐 地址: http://localhost:8000")
        print("🔧 核心功能:")
        print("  📁 递归扫描所有文件夹(包括My Pack)")
        print("  🎬 优化在线播放功能")
        print("  📱 支持IINA外部播放器")
        print("  🎥 支持VLC外部播放器")
        print("  💾 支持视频下载")
        print("=" * 60)
        print("💡 特色:")
        print("  🎯 专门识别My Pack文件夹")
        print("  📊 显示文件所在文件夹")
        print("  🔄 下载完成自动刷新")
        print("=" * 60)

        uvicorn.run(app, host="0.0.0.0", port=8000)

else:
    def run_server():
        print("❌ 需要安装 FastAPI")


def main():
    print("📁 Folder Scan Anime - 文件夹扫描版番剧服务器")
    print("=" * 60)
    print("🎯 专门解决My Pack文件夹视频无法显示的问题")
    print("🔧 递归扫描所有文件夹，包括子文件夹")
    print("🎬 优化播放功能，支持多种播放方式")
    print("=" * 60)

    if FASTAPI_AVAILABLE:
        run_server()
    else:
        print("❌ 无法启动，缺少FastAPI")


if __name__ == '__main__':
    main()