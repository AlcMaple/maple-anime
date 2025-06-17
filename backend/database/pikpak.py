import json
import os
from typing import Dict, List, Any, Optional
from datetime import datetime


class PikPakDatabase:
    """PikPak 数据库管理"""

    def __init__(self, db_path: str = "data/anime.json"):
        self.db_path = db_path
        self.ensure_db_exists()

    def ensure_db_exists(self):
        """确保数据库文件存在"""
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)

        if not os.path.exists(self.db_path):
            # 创建空的数据库结构
            initial_data = {
                "animes": {},
                "metadata": {
                    "created_at": datetime.now().isoformat(),
                    "last_updated": datetime.now().isoformat(),
                },
            }
            self.save_data(initial_data)

    def load_data(self) -> Dict[str, Any]:
        """加载数据库数据"""
        try:
            with open(self.db_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            print(f"加载数据库失败: {e}")
            return {"animes": {}, "metadata": {}}

    def _upgrade_data_structure(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """调整数据结构"""
        upgraded_animes = {}

        for folder_id, anime_info in data.get("animes", {}).items():
            # 数据结构
            upgraded_animes[folder_id] = {
                "folder_name": anime_info.get("title", ""),
                "files": [
                    # 文件列表结构示例
                    # {
                    #     "file_name": "第01话.mp4",
                    #     "file_id": "file123",
                    #     "play_url": "https://example.com/play/file123"
                    # }
                ],
                "cover_url": anime_info.get("cover_url", ""),
                "status": anime_info.get("status", "连载"),
                "summary": anime_info.get("summary", ""),
            }

        return {
            "animes": upgraded_animes,
            "metadata": {
                "created_at": data.get("metadata", {}).get(
                    "created_at", datetime.now().isoformat()
                ),
                "last_updated": datetime.now().isoformat(),
            },
        }

    def save_data(self, data: Dict[str, Any]) -> bool:
        """保存数据到数据库"""
        try:
            data["metadata"]["last_updated"] = datetime.now().isoformat()
            with open(self.db_path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            print(f"保存数据库失败: {e}")
            return False

    def get_anime_detail(self, anime_id: str) -> Dict[str, Any]:
        """获取动漫详细信息"""
        data = self.load_data()
        anime_info = data["animes"].get(anime_id, {})

        if not anime_info:
            return {}

        return {
            "id": anime_id,
            "title": anime_info.get("title", ""),
            "status": anime_info.get("status", "连载"),
            "summary": anime_info.get("summary", ""),
            "cover_url": anime_info.get("cover_url", ""),
            "updated_at": anime_info.get("updated_at", ""),
        }

    def get_anime_status(self, anime_id: str) -> str:
        """获取动漫状态"""
        data = self.load_data()
        anime_info = data["animes"].get(anime_id, {})
        return anime_info.get("status", "连载")

    def sync_with_pikpak_folders(self, pikpak_folders: List[Dict]) -> List[Dict]:
        """
        同步 pikpak 数据

        Args:
            pikpak_folders: PikPak 文件夹列表 [{"name": "动漫名", "id": "文件夹ID"}]

        Returns:
            合并后的动漫列表
        """
        result = []

        # 处理 PikPak 中的文件夹
        for folder in pikpak_folders:
            folder_id = folder["id"]
            folder_name = folder["name"]

            # 获取动漫详细信息
            anime_detail = self.get_anime_detail(folder_id)

            # 新动漫
            if not anime_detail:
                anime_detail = {
                    "id": folder_id,
                    "title": folder_name,
                    "status": "连载",
                    "summary": "",
                    "cover_url": "",
                    "updated_at": datetime.now().isoformat(),
                }

            result.append(
                {
                    "id": folder_id,
                    "title": anime_detail.get("title", folder_name),
                    "status": anime_detail.get("status", "连载"),
                    "summary": anime_detail.get("summary", ""),
                    "cover_url": anime_detail.get("cover_url", ""),
                    "updated_at": anime_detail.get("updated_at", ""),
                }
            )

        print(f"同步完成，共 {len(result)} 个动漫")
        return result

    def get_all_animes(self) -> List[Dict]:
        """获取所有动漫列表"""
        data = self.load_data()
        result = []

        for anime_id, anime_info in data["animes"].items():
            result.append(
                {
                    "id": anime_id,
                    "title": anime_info.get("title", ""),
                    "status": anime_info.get("status", "连载"),
                    "summary": anime_info.get("summary", ""),
                    "cover_url": anime_info.get("cover_url", ""),
                    "updated_at": anime_info.get("updated_at", ""),
                }
            )

        return result

    async def update_anime_info(
        self, anime_id: str, update_data: Dict[str, Any]
    ) -> bool:
        """
        更新动漫信息
        """
        try:
            # print("将要更新的动漫信息：", update_data)
            # 加载现有数据
            db_data = self.load_data()

            # 检查动漫是否存在
            if anime_id not in db_data["animes"]:
                print(f"动漫 {anime_id} 不存在")
                return False

            # 获取现有动漫信息
            anime_info = db_data["animes"][anime_id]
            # print("更新前的动漫信息：", anime_info)

            # 只更新传入的字段
            updatable_fields = ["title", "status", "summary", "cover_url"]

            for field in updatable_fields:
                if field in update_data:
                    anime_info[field] = update_data[field]

            # 更新时间戳
            anime_info["updated_at"] = datetime.now().isoformat()

            # print("更新后的动漫信息：", anime_info)

            # 保存数据
            return self.save_data(db_data)

        except Exception as e:
            print(f"更新动漫信息失败: {e}")
            return False
