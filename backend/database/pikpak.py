import json
import os
from typing import Dict, List, Any
from datetime import datetime, timedelta

from exceptions import NotFoundException, SystemException


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

    def get_anime_detail(self, anime_id: str, my_pack_id: str) -> Dict[str, Any]:
        """获取动漫详细信息"""
        data = self.load_data()
        anime_info = data.get("animes", {}).get(my_pack_id, {}).get(anime_id, {})

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
        self, anime_id: str, update_data: Dict[str, Any], my_pack_id: str
    ) -> bool:
        """
        更新动漫信息
        """
        try:
            # print("将要更新的动漫信息：", update_data)
            # 加载现有数据
            db_data = self.load_data()
            anime_info = db_data.get("animes", {}).get(my_pack_id, {})

            # 检查动漫是否存在
            if anime_id not in anime_info:
                print(f"动漫 {anime_id} 不存在")
                return False

            # 获取现有动漫信息
            info = anime_info.get(anime_id, {})
            # print("更新前的动漫信息：", anime_info)

            # 只更新传入的字段
            updatable_fields = ["title", "status", "summary", "cover_url"]

            for field in updatable_fields:
                if field in update_data:
                    info[field] = update_data[field]

            # 更新时间戳
            info["updated_at"] = datetime.now().isoformat()

            # print("更新后的动漫信息：", anime_info)

            # 保存数据
            return self.save_data(db_data)

        except Exception as e:
            print(f"更新动漫信息失败: {e}")
            return False

    async def del_anime_files(
        self, folder_id: str, file_ids: List[str], my_pack_id: str
    ) -> bool:
        """
        更新动漫文件列表
        """
        try:
            # 加载现有数据
            db_data = self.load_data()
            anime_data = (
                db_data.get("animes", {}).get(my_pack_id, {}).get(folder_id, {})
            )

            if not anime_data:
                print(f"数据库不存在该动漫，需要同步数据")
                return False

            files = anime_data.get("files", [])

            # 删除 files_id 对应的文件
            files["files"] = [f for f in files if f.get("id") not in file_ids]

            # 保存数据
            return self.save_data(db_data)

        except Exception as e:
            print(f"删除动漫文件失败: {e}")
            return False

    async def rename_anime_file(
        self, file_id: str, new_name: str, my_pack_id: str, folder_id: str
    ) -> bool:
        """
        更新动漫文件名称
        """
        try:
            # 加载现有数据
            db_data = self.load_data()
            anime_data = (
                db_data.get("animes", {}).get(my_pack_id, {}).get(folder_id, {})
            )

            if not anime_data:
                print(f"数据库不存在该动漫，需要同步数据")
                return False

            files = anime_data.get("files", [])
            # 找到文件并更新名称
            for file in files:
                if file.get("id") == file_id:
                    file["name"] = new_name
                    break

            # 保存数据
            return self.save_data(db_data)

        except Exception as e:
            print(f"更新动漫文件名称失败: {e}")
            return False

    async def update_anime_file_link(
        self, file_id: str, play_url: str, my_pack_id: str, folder_id: str
    ) -> dict:
        """
        更新动漫文件播放链接
        """
        try:
            # 加载现有数据
            db_data = self.load_data()
            anime_data = (
                db_data.get("animes", {}).get(my_pack_id, {}).get(folder_id, {})
            )

            if not anime_data:
                print(f"数据库不存在该动漫，需要同步数据")
                return False

            files = anime_data.get("files", [])
            update_time = datetime.now().isoformat()
            file_found = False
            # 找到文件并更新播放链接
            for file in files:
                if file.get("id") == file_id:
                    file["play_url"] = play_url
                    file["update_time"] = update_time
                    file_found = True
                    break

            if not file_found:
                return {
                    "success": False,
                    "message": f"未找到文件ID: {file_id}",
                    "data": {},
                }

            # 保存数据
            save_success = self.save_data(db_data)

            if save_success:
                return {
                    "success": True,
                    "message": "更新成功",
                    "data": {
                        "file_id": file_id,
                        "play_url": play_url,
                        "updated_time": update_time,
                    },
                }
            else:
                print("保存数据失败")
                return {"success": False, "message": "保存数据失败", "data": {}}

        except Exception as e:
            print(f"更新动漫文件播放链接失败: {e}")
            return {"success": False, "message": f"更新失败: {str(e)}", "data": {}}

    async def search_anime_by_title(self, title: str) -> Dict:
        """
        搜索动漫
        """
        try:
            # 加载现有数据
            db_data = self.load_data()
            anime_list = []

            # 遍历animes对象下的所有动漫分组
            for anime_group_id, anime_group in db_data.get("animes", {}).items():
                # 遍历每个分组下的具体动漫信息
                for anime_id, anime_info in anime_group.items():
                    anime_title = anime_info.get("title", "")
                    # 使用模糊匹配，检查title是否包含在anime_title中
                    if title.lower() in anime_title.lower():
                        anime_list.append(
                            {
                                "group_id": anime_group_id,  # 分组ID
                                "id": anime_id,
                                "title": anime_title,
                                "status": anime_info.get("status", "连载"),
                                "summary": anime_info.get("summary", ""),
                                "cover_url": anime_info.get("cover_url", ""),
                                "updated_at": anime_info.get("updated_at", ""),
                                "files_count": len(
                                    anime_info.get("files", [])
                                ),  # 文件数量
                            }
                        )

            return {
                "success": True,
                "message": "搜索成功",
                "data": anime_list,
                "total": len(anime_list),
                "keyword": title,
            }

        except Exception as e:
            print(f"搜索动漫失败: {e}")
            return {
                "success": False,
                "message": f"搜索失败: {str(e)}",
                "data": [],
                "total": 0,
                "keyword": title,
            }

    async def get_anime_all(self, folder_id, my_pack_id):
        """
        获取动漫全部信息
        """
        try:
            # 加载现有数据
            db_data = self.load_data()
            anime_data = (
                db_data.get("animes", {}).get(my_pack_id, {}).get(folder_id, {})
            )

            if not anime_data:
                print(f"数据库不存在该动漫，需要同步数据")
                return False

            # 数据处理
            files = anime_data.get("files", [])
            for file in files:
                file_name = file.get("name", "")
                file_name = file_name.split(".")[0]
                file["name"] = file_name

            return anime_data

        except Exception as e:
            print(f"获取动漫全部信息失败: {e}")
            return {}

    async def update_folder_video_links_time(
        self, folder_id: str, my_pack_id: str, update_time: str = None
    ) -> bool:
        """
        更新动漫文件夹的视频链接的更新时间
        """
        try:
            # 加载现有数据
            db_data = self.load_data()
            anime_data = (
                db_data.get("animes", {}).get(my_pack_id, {}).get(folder_id, {})
            )

            if not anime_data:
                print(f"数据库不存在该动漫，需要同步数据")
                return False

            # 设置视频链接更新时间
            if update_time is None:
                update_time = datetime.now().isoformat()

            anime_data["last_video_update_time"] = update_time

            # 保存数据
            return self.save_data(db_data)

        except Exception as e:
            print(f"更新动漫文件夹的视频链接的更新时间失败: {e}")
            return False

    def get_all_anime_schedule_info(self, my_pack_id: str) -> List[Dict]:
        """
        获取所有动漫的调度信息
        """
        try:
            # 加载现有数据
            db_data = self.load_data()
            anime_folders = db_data.get("animes", {}).get(my_pack_id, {})
            folders_info = []
            current_time = datetime.now()

            for folder_id, anime_info in anime_folders.items():
                files = anime_info.get("files", [])
                if not files:
                    continue

                # 获取最后更新时间
                last_update = anime_info.get("last_video_update_time", "")
                last_update_time = None

                if last_update:
                    try:
                        last_update_time = datetime.fromisoformat(last_update)
                    except ValueError:
                        pass

                # 计算下次更新时间
                if last_update_time:
                    next_update_time = last_update_time + timedelta(hours=20)
                else:
                    # 从未更新，立即更新
                    next_update_time = current_time + timedelta(minutes=1)

                folders_info.append(
                    {
                        "folder_id": folder_id,
                        "title": anime_info.get("title", ""),
                        "file_count": len(files),
                        "last_update_time": last_update_time,
                        "next_update_time": next_update_time,
                        "file_ids": [f["id"] for f in files],
                    }
                )

            return folders_info

        except Exception as e:
            print(f"获取所有文件夹的调度信息失败: {e}")
            return []
