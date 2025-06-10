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
                    "version": "1.0",
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

    def get_anime_status(self, anime_id: str) -> str:
        """获取动漫状态"""
        data = self.load_data()
        anime_info = data["animes"].get(anime_id, {})
        return anime_info.get("status", "连载")

    def set_anime_status(self, anime_id: str, title: str, status: str) -> bool:
        """设置动漫状态"""
        data = self.load_data()

        if anime_id not in data["animes"]:
            data["animes"][anime_id] = {}

        data["animes"][anime_id].update(
            {"title": title, "status": status, "updated_at": datetime.now().isoformat()}
        )

        return self.save_data(data)

    def sync_with_pikpak_folders(self, pikpak_folders: List[Dict]) -> List[Dict]:
        """
        同步 pikpak 数据

        Args:
            pikpak_folders: PikPak 文件夹列表 [{"name": "动漫名", "id": "文件夹ID"}]

        Returns:
            合并后的动漫列表 [{"id": "ID", "title": "标题", "status": "状态"}]
        """
        data = self.load_data()
        result = []

        # 处理 PikPak 中的文件夹
        for folder in pikpak_folders:
            folder_id = folder["id"]
            folder_name = folder["name"]

            # 获取已保存的状态，如果没有则默认为"连载"
            status = self.get_anime_status(folder_id)

            # 如果是新动漫，保存到数据库
            if folder_id not in data["animes"]:
                self.set_anime_status(folder_id, folder_name, "连载")
                status = "连载"

            result.append({"id": folder_id, "title": folder_name, "status": status})

        print(f"同步完成，共 {len(result)} 个动漫")
        return result

    def update_anime_status(self, anime_id: str, status: str) -> bool:
        """更新动漫状态"""
        data = self.load_data()

        if anime_id not in data["animes"]:
            print(f"动漫 ID {anime_id} 不存在")
            return False

        data["animes"][anime_id]["status"] = status
        data["animes"][anime_id]["updated_at"] = datetime.now().isoformat()

        return self.save_data(data)

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
                }
            )

        return result
