import re
import asyncio
from typing import Dict, List, Any, Optional
from pikpakapi import PikPakApi
from utils.analyzer import Analyzer


class PikPakService:
    """PikPak 云盘服务"""

    def __init__(self):
        self.clients = {}  # 客户端连接
        self.analyzer = Analyzer()

    async def get_client(self, username: str, password: str) -> PikPakApi:
        """获取或创建PikPak客户端"""
        client_key = f"{username}:{password}"

        if client_key not in self.clients:
            client = PikPakApi(username=username, password=password)
            await client.login()
            self.clients[client_key] = client

        return self.clients[client_key]

    async def create_anime_folder(
        self, client: PikPakApi, folder_name: str
    ) -> Optional[str]:
        """
        创建动漫文件夹

        Args:
            client: PikPak客户端
            folder_name: 文件夹名称

        Returns:
            文件夹ID，创建失败返回None
        """
        try:
            # 检查文件夹是否已存在
            file_list = await client.file_list()
            existing_folders = file_list.get("files", [])

            for folder in existing_folders:
                if (
                    folder.get("kind") == "drive#folder"
                    and folder.get("name") == folder_name
                ):
                    print(f"动漫 '{folder_name}' 已存在，如需更改内容请前往“更新”功能")
                    return None

            # 创建新文件夹
            result = await client.create_folder(folder_name)
            print("=" * 60)
            print("创建文件夹响应信息：", result)
            print("=" * 60)

            if result and "file" in result and "id" in result["file"]:
                print(f"成功创建文件夹: {folder_name}")
                return result["file"]["id"]
            else:
                print(f"创建文件夹失败: {folder_name}")
                return None

        except Exception as e:
            print(f"创建文件夹异常: {e}")
            return None

    async def download_to_folder(
        self, client: PikPakApi, magnet: str, folder_id: str, title: str
    ) -> Dict:
        """
        下载磁力链接到指定文件夹

        Args:
            client: PikPak客户端
            magnet: 磁力链接
            folder_id: 目标文件夹ID
            title: 文件标题

        Returns:
            task_id: 下载任务ID
            folder_id: 目标文件夹ID
        """
        try:
            # 添加离线下载任务到指定文件夹
            result = await client.offline_download(magnet, parent_id=folder_id)

            if result:
                return {
                    "success": True,
                    "message": f"成功添加下载任务: {title}",
                    "task_id": result.get("id"),
                    "folder_id": folder_id,
                }
            else:
                return {"success": False, "message": f"添加下载任务失败: {title}"}

        except Exception as e:
            return {"success": False, "message": f"下载异常: {str(e)}"}