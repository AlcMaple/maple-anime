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
            # 先检查文件夹是否已存在
            file_list = await client.file_list()
            existing_folders = file_list.get("files", [])

            for folder in existing_folders:
                if (
                    folder.get("kind") == "drive#folder"
                    and folder.get("name") == folder_name
                ):
                    print(f"文件夹 '{folder_name}' 已存在，使用现有文件夹")
                    return folder.get("id")

            # 创建新文件夹
            result = await client.create_folder(folder_name)

            if result and "id" in result:
                print(f"成功创建文件夹: {folder_name}")
                return result["id"]
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

    async def batch_download_anime(
        self, username: str, password: str, anime_list: List[Dict]
    ) -> Dict:
        """
        批量下载动漫

        Args:
            username: PikPak用户名
            password: PikPak密码
            anime_list: 动漫列表，每个元素包含id、title、magnet
        """
        try:
            # 获取PikPak客户端
            client = await self.get_client(username, password)

            # 按动漫标题分组
            anime_groups = {}
            for anime in anime_list:
                title = anime.get("title", "")
                magnet = anime.get("magnet", "")

                # 提取主标题
                main_title = self.analyzer.extract_anime_title(title)

                if main_title not in anime_groups:
                    anime_groups[main_title] = []

                anime_groups[main_title].append(
                    {"original_title": title, "magnet": magnet}
                )

            results = []

            # 为每个动漫创建文件夹并下载
            for main_title, episodes in anime_groups.items():
                print(f"处理动漫: {main_title} ({len(episodes)} 个资源)")

                # 创建文件夹
                folder_id = await self.create_anime_folder(client, main_title)

                if not folder_id:
                    results.append(
                        {
                            "anime_title": main_title,
                            "success": False,
                            "message": "创建文件夹失败",
                            "episodes": [],
                        }
                    )
                    continue

                # 下载各集到文件夹
                episode_results = []
                for episode in episodes:
                    download_result = await self.download_to_folder(
                        client, episode["magnet"], folder_id, episode["original_title"]
                    )
                    episode_results.append(download_result)

                results.append(
                    {
                        "anime_title": main_title,
                        "success": True,
                        "folder_id": folder_id,
                        "episodes": episode_results,
                        "total_episodes": len(episodes),
                    }
                )

            # 统计结果
            total_anime = len(anime_groups)
            successful_anime = len([r for r in results if r["success"]])
            total_episodes = sum([r["total_episodes"] for r in results if r["success"]])
            successful_episodes = sum(
                [
                    len([e for e in r["episodes"] if e.get("success", False)])
                    for r in results
                    if r["success"]
                ]
            )

            return {
                "success": True,
                "message": "批量下载完成",
                "summary": {
                    "total_anime": total_anime,
                    "successful_anime": successful_anime,
                    "total_episodes": total_episodes,
                    "successful_episodes": successful_episodes,
                },
                "details": results,
            }

        except Exception as e:
            return {"success": False, "message": f"批量下载失败: {str(e)}"}