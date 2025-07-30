import asyncio
from typing import Dict, List, Any, Optional
from pikpakapi import PikPakApi
import time
from loguru import logger

from database.pikpak import PikPakDatabase
from datetime import datetime
from config import settings
from utils import (
    is_collection,
    get_anime_episodes,
)
from exceptions import NotFoundException, SystemException, DuplicateException


class PikPakService:
    """PikPakAPI"""

    def __init__(self):
        self.clients = {}  # 客户端连接
        self.my_pack_id = settings.ANIME_CONTAINER_ID
        self.anime_db = PikPakDatabase()
        self.links_scheduler = None

    def _get_links_scheduler(self):
        """延迟导入并获取链接调度器实例"""
        if self.links_scheduler is None:
            try:
                from scheduler.links_scheduler import LinksScheduler

                self.links_scheduler = LinksScheduler(
                    settings.PIKPAK_USERNAME, settings.PIKPAK_PASSWORD
                )
            except ImportError:
                pass
        return self.links_scheduler

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
            # 检查 My Pack 内是否已存在同名文件夹
            existing_folders = await self.get_mypack_folder_list(client)

            for folder in existing_folders:
                if folder.get("name") == folder_name:
                    logger.warning(
                        f"动漫 '{folder_name}' 已存在，如需更改内容请前往'更新'功能"
                    )
                    return None

            # 在 My Pack 内创建新文件夹
            result = await client.create_folder(folder_name, parent_id=self.my_pack_id)
            logger.debug("创建文件夹响应信息：", result["file"]["id"])

            if result and "file" in result and "id" in result["file"]:
                logger.debug(f"成功在 My Pack 内创建文件夹: {folder_name}")
                return result["file"]["id"]  # 创建文件夹成功，返回文件夹 ID
            else:
                logger.error(f"创建文件夹失败: {folder_name}")
                return None

        except Exception as e:
            logger.critical(f"创建文件夹异常: {e}")
            return None

    async def download_to_root(
        self, client: PikPakApi, magnet: str, title: str
    ) -> Dict:
        """
        下载磁力链接到 My Pack
        """
        try:
            result = await client.offline_download(magnet)
            logger.info("=" * 60)
            logger.debug("离线下载响应信息：", result)
            logger.info("=" * 60)

            if result and "task" in result and result["task"]:
                return {
                    "success": True,
                    "message": f"成功添加下载任务: {title}",
                    "task_id": result["task"]["id"],
                }
            else:
                return {"success": False, "message": f"添加下载任务失败: {title}"}

        except Exception as e:
            return {"success": False, "message": f"下载异常: {str(e)}"}

    async def find_new_folder(
        self, client: PikPakApi, before_folders: List[str]
    ) -> Optional[Dict]:
        """
        在 My Pack 内查找新文件夹

        Args:
            client: PikPak客户端
            before_folders: 下载前的文件夹列表

        Returns:
            新文件夹信息，如果没找到返回None
        """
        start_time = time.time()
        check_interval = 2  # 检查间隔, 单位秒
        timeout = 60  # 超时时间，单位秒

        while (time.time() - start_time) < timeout:
            try:
                # 获取 My Pack 内当前文件夹列表
                current_folder_list = await self.get_mypack_folder_list(client)
                current_folder_names = [f["name"] for f in current_folder_list]
                logger.debug(f"My Pack 内当前文件夹名称列表: {current_folder_names}")

                # 找出新增的文件夹
                new_folders = [
                    f for f in current_folder_names if f not in before_folders
                ]

                if new_folders:
                    # 找到新文件夹，返回第一个（通常合集只生成一个文件夹）
                    new_folder = new_folders[0]
                    for folder in current_folder_list:
                        if folder["name"] == new_folder:
                            logger.debug(
                                f" 在 My Pack 内找到新文件夹: {folder['name']} (ID: {folder['id']})"
                            )
                            return folder

                await asyncio.sleep(check_interval)

            except Exception as e:
                logger.error(f"查找新文件夹时出错: {e}")
                await asyncio.sleep(check_interval)

        logger.warning("该磁链下载超时，可能是p2p 种子下载失败")
        return None

    async def rename_folder(
        self, client: PikPakApi, folder_id: str, new_name: str
    ) -> bool:
        """
        重命名文件夹

        Args:
            client: PikPak客户端
            folder_id: 文件夹ID
            new_name: 新名称

        Returns:
            是否成功
        """
        try:
            result = await client.file_rename(folder_id, new_name)

            if result and isinstance(result, dict) and "id" in result:
                print(f"成功重命名文件夹: {new_name}")
                return True
            else:
                print(f"重命名文件夹失败: {new_name}")
                return False

        except Exception as e:
            print(f"重命名文件夹异常: {e}")
            return False

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

    async def batch_download_selected(
        self, client: PikPakApi, anime_list: List[Any], target_folder_name: str
    ) -> Dict:
        """
        批量下载选择

        Args:
            client: PikPak客户端
            anime_list: 动漫列表,每个对象包含 {id, title, magnet}
            target_folder_name: 目标文件夹名称

        Returns:
            success: 是否成功
            message: 返回信息
            collection_count: 合集数量
            single_count: 单集数量
            results: 下载结果列表
        """
        try:
            # 创建或获取目标文件夹ID
            folder_id = await self.create_anime_folder(client, target_folder_name)
            if not folder_id:
                raise DuplicateException(
                    resource="My Pack", field="folder_id", value=target_folder_name
                )

            # 合集和单集处理
            collection_items = []
            single_items = []
            for anime in anime_list:
                if is_collection(anime.title):
                    collection_items.append(anime)
                else:
                    single_items.append(anime)

            added_count = 0
            failed_count = 0
            failed_episodes = []

            # 获取下载前的文件夹列表（检测合集下载的新文件夹）
            before_folders = []
            if collection_items:
                mypack_folders = await self.get_mypack_folder_list(client)
                before_folders = [f["name"] for f in mypack_folders]

            # 处理合集
            for anime in collection_items:
                title = anime.title
                magnet = anime.magnet
                try:
                    # 下载合集到 My Pack 根目录
                    result = await self.download_to_root(client, magnet, title)
                    if result["success"]:
                        # 等待并查找新生成的文件夹
                        new_folder = await self.find_new_folder(client, before_folders)
                        if new_folder:
                            # 将合集文件夹内容移动到目标文件夹
                            move_result = await self.move_folder_contents(
                                client, new_folder["id"], folder_id
                            )
                            if move_result["success"]:
                                added_count += 1
                                # 删除空的合集文件夹
                                try:
                                    await client.delete_to_trash(ids=[new_folder["id"]])
                                except Exception:
                                    pass  # Ignore error
                                before_folders.append(new_folder["name"])
                            else:
                                failed_count += 1
                                failed_episodes.append(
                                    {"title": title, "reason": move_result["message"]}
                                )
                        else:
                            failed_count += 1
                            failed_episodes.append(
                                {"title": title, "reason": "未找到新生成的合集文件夹"}
                            )
                    else:
                        failed_count += 1
                        failed_episodes.append(
                            {"title": title, "reason": result["message"]}
                        )
                except Exception as e:
                    failed_count += 1
                    failed_episodes.append({"title": title, "reason": str(e)})

            # 处理单集
            for anime in single_items:
                title = anime.title
                magnet = anime.magnet
                try:
                    # 直接下载到指定文件夹
                    result = await self.download_to_folder(
                        client, magnet, folder_id, title
                    )
                    if result["success"]:
                        added_count += 1
                    else:
                        failed_count += 1
                        failed_episodes.append(
                            {"title": title, "reason": result["message"]}
                        )
                except Exception as e:
                    failed_count += 1
                    failed_episodes.append({"title": title, "reason": str(e)})

            # 延时重命名和同步
            if added_count > 0:
                asyncio.create_task(
                    self.delayed_rename_task(client, folder_id, delay_seconds=8)
                )

            if failed_count > 0:
                logger.error(f"失败详情：{failed_episodes}")

            return {
                "collection_count": len(collection_items),
                "single_count": len(single_items),
                "folder_id": folder_id,
            }

        except Exception as e:
            raise SystemException(message="批量下载选择异常", original_error=e)

    async def rename_single_file(
        self, client: PikPakApi, file_id: str, new_name: str
    ) -> bool:
        """
        重命名单个文件

        Args:
            client: PikPak客户端
            file_id: 文件ID
            new_name: 新文件名

        Returns:
            success: 是否成功
        """
        try:
            # 调用PikPak重命名API
            logger.debug("将要重命名的文件 id：", file_id)
            result = await client.file_rename(file_id, new_name)
            logger.debug("rename_result:", result)

            if result and isinstance(result, dict) and "id" in result:
                return True
            else:
                return False

        except Exception as e:
            logger.error(f"重命名文件异常: {e}")
            return False

    async def batch_rename_file(self, client: PikPakApi, folder_id: str) -> Dict:
        """
        批量重命名文件

        Args:
            client: PikPak客户端
            folder_id: 文件夹ID

        Returns:
            success: 是否成功
            message: 信息
            renamed_files: 重命名的文件列表
            failed_files: 失败的文件列表
        """
        try:
            file_list = await client.file_list(parent_id=folder_id)
            if not file_list or "files" not in file_list:
                return {"success": False, "message": "文件列表为空或不存在"}

            files = file_list["files"]
            renamed_files = []
            failed_files = []

            for file in files:
                # 跳过文件夹
                if file.get("kind") == "drive#folder":
                    continue

                file_id = file.get("id")
                original_name = file.get("name")

                if not original_name or not file_id:
                    failed_files.append(file)
                    continue

                # 获取新文件名
                episode_num = get_anime_episodes(original_name)
                if episode_num == original_name:
                    # 无法获取新的文件名
                    failed_files.append(file)
                    continue

                # 重命名文件
                rename_result = await self.rename_single_file(
                    client, file_id, episode_num
                )
                if rename_result:
                    renamed_files.append(file)
                else:
                    failed_files.append(file)

            logger.info(
                f"重命名 {len(renamed_files)} 个文件，失败 {len(failed_files)} 个文件"
            )

            return {
                "success": True,
                "message": f"成功重命名{len(renamed_files)}个文件",
                "renamed_files": renamed_files,
                "failed_files": failed_files,
            }
        except Exception as e:
            return {"success": False, "message": f"重命名异常: {str(e)}"}

    async def delayed_rename_task(
        self, client: PikPakApi, folder_id: str, delay_seconds: int = 8
    ):
        """
        延时重命名任务

        Args:
            client: PikPak客户端
            folder_id: 文件夹ID
            delay_seconds: 延时秒数，默认8秒
        """
        try:
            logger.debug(
                f"将在 {delay_seconds} 秒后开始重命名文件夹 {folder_id} 中的文件..."
            )
            await asyncio.sleep(delay_seconds)

            logger.debug(f"开始重命名文件夹 {folder_id} 中的文件...")
            rename_result = await self.batch_rename_file(client, folder_id)

            if rename_result["success"]:
                logger.debug(
                    f" 文件夹 {folder_id} 重命名完成: {rename_result['message']}"
                )
                # 重命名完成后，启动延时同步数据任务
                asyncio.create_task(
                    self.delayed_sync_data_task(client, delay_seconds=8)
                )
                logger.info(f"已安排8秒后同步数据任务")
            else:
                logger.debug(
                    f"文件夹 {folder_id} 重命名失败: {rename_result['message']}"
                )

        except Exception as e:
            logger.error(f"延时重命名任务异常: {e}")

    async def delayed_sync_data_task(self, client: PikPakApi, delay_seconds: int = 8):
        """
        延时同步数据任务

        Args:
            client: PikPak客户端
            delay_seconds: 延时秒数，默认8秒
        """
        try:
            print(f"将在 {delay_seconds} 秒后开始同步数据...")
            await asyncio.sleep(delay_seconds)

            print(f"开始同步数据...")
            sync_result = await self.sync_data(client)

            if sync_result:
                print(f"数据同步完成")
            else:
                print(f"数据同步失败")

        except Exception as e:
            print(f"延时同步数据任务异常: {e}")

    async def get_folder_list(self, client: PikPakApi) -> List[Dict]:
        """
        获取根目录文件夹列表

        Args:
            client: PikPak客户端

        Returns:
            包含文件夹信息的列表，每个元素是包含name和id的字典
        """
        try:
            # 获取根目录文件列表
            file_list = await client.file_list()

            if not file_list or "files" not in file_list:
                return []

            # 筛选出文件夹
            folders = [
                {"name": f["name"], "id": f["id"]}
                for f in file_list["files"]
                if f.get("kind") == "drive#folder"
            ]

            return folders

        except Exception as e:
            print(f"获取文件夹列表异常: {e}")
            return []

    async def get_mypack_folder_list(self, client: PikPakApi) -> List[Dict]:
        """
        获取 My Pack 内的文件夹列表

        Args:
            client: PikPak客户端

        Returns:
            包含文件夹信息的列表，每个元素是包含name和id的字典
        """
        try:
            # 获取 My Pack 内的文件列表
            file_list = await client.file_list(parent_id=self.my_pack_id)

            if not file_list or "files" not in file_list:
                return []

            # 筛选出文件夹
            folders = [
                {"name": f["name"], "id": f["id"]}
                for f in file_list["files"]
                if f.get("kind") == "drive#folder"
            ]

            return folders

        except Exception as e:
            logger.critical(f"获取 My Pack 文件夹列表异常: {e}")
            return []

    async def get_folder_files(self, client: PikPakApi, folder_id: str) -> Dict:
        """
        获取指定文件夹内的所有文件

        Args:
            client: PikPak客户端
            folder_id: 文件夹ID

        Returns:
            success: 是否成功
            files: 文件列表
            message: 信息
        """
        try:
            logger.debug(f" 获取文件夹 {folder_id} 内的文件列表...")

            # 获取文件夹内容
            result = await client.file_list(parent_id=folder_id)

            if not result or "files" not in result:
                return {"success": False, "files": [], "message": "无法获取文件夹内容"}

            files = result["files"]

            # 过滤出文件（排除文件夹）
            file_list = []
            video_extensions = [
                ".mp4",
                ".mkv",
                ".avi",
                ".mov",
                ".m4v",
                ".webm",
                ".flv",
                ".rmvb",
                ".wmv",
            ]

            for file in files:
                file_kind = file.get("kind", "")
                file_type = file.get("type", "")
                file_name = file.get("name", "")

                # 只保留文件，排除文件夹
                is_file = file_kind == "drive#file" or file_type == "file"

                if is_file:
                    # 判断是否为视频文件
                    is_video = any(ext in file_name.lower() for ext in video_extensions)

                    formatted_file = {
                        "id": file.get("id", ""),
                        "name": file_name,
                        "size": int(file.get("size", 0)),
                        "kind": file_kind,
                        "created_time": file.get(
                            "created_time", file.get("created_at", "")
                        ),
                        "mime_type": file.get("mime_type", ""),
                        "thumbnail": file.get("thumbnail", ""),
                        "hash": file.get("hash", ""),
                        "is_video": is_video,
                    }
                    file_list.append(formatted_file)

            logger.debug(f" 获取到 {len(file_list)} 个文件（共 {len(files)} 个项目）")

            # 按文件名排序
            file_list.sort(key=lambda x: x.get("name", ""))

            return {
                "success": True,
                "files": file_list,
                "total_files": len(file_list),
                "total_items": len(files),
                "message": f"获取到 {len(file_list)} 个文件",
            }

        except Exception as e:
            logger.error(f" 获取文件夹文件列表失败: {e}")
            return {
                "success": False,
                "files": [],
                "message": f"获取文件列表失败: {str(e)}",
            }

    async def delete_file(self, client: PikPakApi, file_id: str) -> Dict:
        """
        删除指定文件

        Args:
            client: PikPak客户端
            file_id: 文件ID
            file_name: 文件名

        Returns:
            success: 是否成功
            message: 信息
        """
        try:
            # 调用PikPak删除文件API
            result = await client.delete_to_trash(ids=[file_id])

            if result:
                logger.debug(f" 文件删除成功")
                return {"success": True, "message": "文件删除成功"}
            else:
                logger.error(f" 文件删除失败")
                return {"success": False, "message": "文件删除失败"}

        except Exception as e:
            logger.critical(f" 删除文件异常: {e}")
            return {"success": False, "message": f"删除文件失败: {str(e)}"}

    async def batch_delete_files(self, client: PikPakApi, file_ids: List[str]) -> Dict:
        """
        批量删除文件

        Args:
            client: PikPak客户端
            file_ids: 文件ID列表

        Returns:
            success: 是否成功
            message: 信息
            deleted_count: 成功删除的文件数量
            failed_count: 删除失败的文件数量
        """
        try:
            logger.debug(f" 批量删除 {len(file_ids)} 个文件...")

            deleted_count = 0
            failed_count = 0

            for file_id in file_ids:
                try:
                    result = await self.delete_file(client, file_id)
                    if result:
                        deleted_count += 1
                    else:
                        failed_count += 1
                except Exception as e:
                    logger.error(f" 删除文件 {file_id} 失败: {e}")
                    failed_count += 1

            logger.info(
                f" 批量删除完成: 成功 {deleted_count} 个，失败 {failed_count} 个"
            )

            return {
                "success": deleted_count > 0,
                "message": f"批量删除完成: 成功 {deleted_count} 个，失败 {failed_count} 个",
                "deleted_count": deleted_count,
                "failed_count": failed_count,
            }

        except Exception as e:
            logger.critical(f" 批量删除异常: {e}")
            return {
                "success": False,
                "message": f"批量删除失败: {str(e)}",
                "deleted_count": 0,
                "failed_count": len(file_ids),
            }

    async def get_video_play_url(
        self, file_id: str, client: PikPakApi
    ) -> Optional[str]:
        """获取视频播放连接"""
        try:
            # 调用PikPak获取视频播放连接API
            result = await client.get_download_url(file_id)
            if result and "web_content_link" in result:
                return result["web_content_link"]
            else:
                return None
        except Exception as e:
            print(f"获取视频播放连接异常: {e}")
            return None

    async def get_mypack_folder_id(self, client: PikPakApi) -> Optional[str]:
        """
        获取 My Pack 文件夹 ID

        Args:
            client: PikPak客户端

        Returns:
            My Pack 文件夹ID，如果找不到返回None
        """
        try:
            # 获取根目录文件夹列表
            folders = await self.get_folder_list(client)

            mypack_names = ["My Pack", "MyPack", "我的收藏", "mypack"]

            for folder in folders:
                folder_name = folder.get("name", "")
                if folder_name in mypack_names:
                    print(f"✅ 找到 My Pack 文件夹: {folder_name} (ID: {folder['id']})")
                    return folder["id"]

            print("❌ 未找到 My Pack 文件夹")
            return None

        except Exception as e:
            print(f"❌ 获取 My Pack 文件夹ID异常: {e}")
            return None

    async def sync_data(self, client: PikPakApi, blocking_wait: bool = False) -> bool:
        """
        同步数据
        """
        try:
            # 加载数据
            data = self.anime_db.load_data()
            if "animes" not in data:
                logger.debug("数据格式错误，缺少animes字段")
                return

            # 获取mypack_id
            mypack_id = list(data["animes"].keys())[0]
            anime_folders = data["animes"][mypack_id]

            # api 调用计数
            api_call_count = 0
            api_batch_size = 3
            api_delay = 8

            logger.info(f"开始同步数据")

            # 获取云端 mypack的所有文件夹 id
            # { id:id_value,name:name_value }
            cloud_folders = await self.get_mypack_folder_list(client)
            # 建立云端文件夹映射
            cloud_folder_map = {folder["id"]: folder for folder in cloud_folders}
            cloud_folder_ids = set(cloud_folder_map.keys())

            # 获取本地已有的文件列表，建立ID到播放链接的映射
            local_folder_ids = set(anime_folders.keys())

            # 计算差异
            new_folder_ids = cloud_folder_ids - local_folder_ids  # 云端有，本地没有
            del_folder_ids = local_folder_ids - cloud_folder_ids  # 云端没有，本地有

            # 删除本地多余的
            for folder_id in del_folder_ids:
                folder_name = anime_folders[folder_id].get("title", "未知")
                logger.debug(f"  删除本地多余的 {folder_name} 文件夹")
                del anime_folders[folder_id]
                links_scheduler = self._get_links_scheduler()
                if links_scheduler:
                    # 如果有链接调度器，删除对应的调度任务
                    links_scheduler.remove_anime_schedule(folder_id)

            # 处理新增的文件夹
            for folder_id in new_folder_ids:
                folder_name = cloud_folder_map[folder_id]["name"]
                logger.debug(f"  新增 {folder_name} 文件夹")
                anime_folders[folder_id] = {
                    "title": folder_name,
                    "status": "连载",
                    "files": [],
                    "updated_at": datetime.now().isoformat(),
                    "summary": "",
                    "cover_url": "",
                }

            # 处理相同的文件夹
            for folder_id, anime_info in anime_folders.items():

                # 获取本地已有的文件列表，建立ID到播放链接的映射
                existing_files = anime_info.get("files", [])
                existing_file_map = {}
                for existing_file in existing_files:
                    file_id = existing_file.get("id")
                    play_url = existing_file.get("play_url")
                    if file_id and play_url:
                        existing_file_map[file_id] = existing_file

                # 获取文件夹内的文件
                folder_result = await self.get_folder_files(client, folder_id)

                if not folder_result["success"]:
                    logger.debug(f"  获取文件夹内容失败: {folder_result['message']}")
                    continue

                files = folder_result["files"]

                if not files:
                    logger.debug(f"  文件夹为空")
                    continue

                logger.debug(f"  找到 {len(files)} 个文件")
                result = []

                # 为每个文件夹获取播放连接
                for file in files:
                    if file["id"] in existing_file_map:
                        original_file = existing_file_map[file["id"]]
                        file_data = {
                            "id": file["id"],
                            "name": file["name"],
                            "play_url": original_file["play_url"],
                            "update_time": datetime.now().isoformat(),
                        }
                    else:
                        # 获取播放连接
                        play_url = await self.get_video_play_url(file["id"], client)
                        api_call_count += 1

                        # 检查是否需要延时
                        if api_call_count % api_batch_size == 0:
                            logger.info(
                                f"      已调用 {api_call_count} 次API，延时 {api_delay} 秒..."
                            )
                            if blocking_wait:
                                time.sleep(api_delay)
                            else:
                                await asyncio.sleep(api_delay)

                        file_data = {
                            "id": file["id"],
                            "name": file["name"],
                            "play_url": play_url,
                            "update_time": datetime.now().isoformat(),
                        }
                    result.append(file_data)

                # 更新数据
                anime_info["files"] = result

            # 保存数据
            data["metadata"]["last_updated"] = datetime.now().isoformat()
            self.anime_db.save_data(data)
            logger.info("同步成功")

            # 初始化调度器
            links_scheduler = self._get_links_scheduler()
            if links_scheduler:
                await links_scheduler.reinitialize()
            return True
        except Exception as e:
            logger.critical(f"同步数据失败: {e}")
            return False

    async def move_folder_contents(
        self, client: PikPakApi, source_folder_id: str, target_folder_id: str
    ) -> Dict:
        """
        将源文件夹内的所有文件移动到目标文件夹

        Args:
            client: PikPak客户端
            source_folder_id: 源文件夹ID
            target_folder_id: 目标文件夹ID

        Returns:
            success: 是否成功
            message: 信息
            moved_count: 移动的文件数量
        """
        try:
            # 获取源文件夹内的所有文件
            source_files_result = await self.get_folder_files(client, source_folder_id)
            if not source_files_result["success"]:
                return {
                    "success": False,
                    "message": f"获取源文件夹内容失败: {source_files_result['message']}",
                    "moved_count": 0,
                }

            files = source_files_result["files"]
            if not files:
                return {
                    "success": True,
                    "message": "源文件夹为空，无需移动",
                    "moved_count": 0,
                }

            moved_count = 0
            failed_count = 0

            # 移动每个文件
            for file in files:
                file_id = file["id"]
                file_name = file["name"]
                try:
                    # 调用 PikPak 移动文件 API
                    result = await client.file_move(file_id, target_folder_id)
                    if result:
                        moved_count += 1
                        logger.debug(f"     移动文件成功: {file_name}")
                    else:
                        failed_count += 1
                        logger.error(f"     移动文件失败: {file_name}")
                except Exception as e:
                    failed_count += 1
                    logger.error(f"     移动文件异常: {file_name} - {str(e)}")

            success = moved_count > 0
            if success:
                if failed_count == 0:
                    message = f"成功移动 {moved_count} 个文件"
                else:
                    message = f"移动完成: 成功 {moved_count} 个，失败 {failed_count} 个"
            else:
                message = f"所有 {len(files)} 个文件都移动失败"

            return {
                "success": success,
                "message": message,
                "moved_count": moved_count,
            }

        except Exception as e:
            logger.error(f" 移动文件夹内容异常: {e}")
            return {
                "success": False,
                "message": f"移动文件夹内容失败: {str(e)}",
                "moved_count": 0,
            }

    async def update_anime_episodes(
        self, client: PikPakApi, anime_list: List[Dict], folder_id: str
    ) -> Dict:
        """
        更新动漫集数

        Args:
            client: PikPak客户端
            anime_list: 动漫列表,每个对象包含 {id, title, magnet}
            folder_id: 目标文件夹ID

        Returns:
            success: 是否成功
            message: 信息
            added_count: 成功添加的集数
            failed_count: 失败的集数
        """
        try:
            added_count = 0
            failed_count = 0
            failed_episodes = []

            # 分类处理：合集和单集
            collection_items = []
            single_items = []

            for anime in anime_list:
                title = anime.get("title", "")
                if is_collection(title):
                    collection_items.append(anime)
                else:
                    single_items.append(anime)

            # 获取下载前的文件夹列表（用于检测合集下载的新文件夹）
            before_folders = []
            if collection_items:
                mypack_folders = await self.get_mypack_folder_list(client)
                before_folders = [f["name"] for f in mypack_folders]

            # 处理合集
            for anime in collection_items:
                title = anime.get("title", "")
                magnet = anime.get("magnet", "")

                try:
                    logger.info(f"处理合集: {title}")

                    # 下载合集到 My Pack 根目录
                    result = await self.download_to_root(client, magnet, title)
                    if result["success"]:
                        logger.info(f"    合集下载任务添加成功")

                        # 等待并查找新生成的文件夹
                        new_folder = await self.find_new_folder(client, before_folders)
                        if new_folder:
                            logger.info(f"    找到新合集文件夹: {new_folder['name']}")

                            # 将合集文件夹内容移动到目标文件夹
                            move_result = await self.move_folder_contents(
                                client, new_folder["id"], folder_id
                            )

                            if move_result["success"]:
                                added_count += 1
                                print(f"    合集内容移动成功: {move_result['message']}")

                                # 删除空的合集文件夹
                                try:
                                    await client.delete_to_trash(ids=[new_folder["id"]])
                                    print(f"    删除空合集文件夹: {new_folder['name']}")
                                except Exception as e:
                                    print(f"    删除空合集文件夹失败: {str(e)}")

                                # 更新 before_folders 以避免重复检测
                                before_folders.append(new_folder["name"])
                            else:
                                failed_count += 1
                                failed_episodes.append(
                                    {"title": title, "reason": move_result["message"]}
                                )
                                print(f"    合集内容移动失败: {move_result['message']}")
                        else:
                            failed_count += 1
                            failed_episodes.append(
                                {"title": title, "reason": "未找到新生成的合集文件夹"}
                            )
                            print(f"    未找到新生成的合集文件夹")
                    else:
                        failed_count += 1
                        failed_episodes.append(
                            {"title": title, "reason": result["message"]}
                        )
                        print(f"    合集下载任务添加失败: {result['message']}")

                except Exception as e:
                    failed_count += 1
                    failed_episodes.append({"title": title, "reason": str(e)})
                    print(f"    合集处理异常: {str(e)}")

            # 处理单集
            for i, anime in enumerate(single_items, 1):
                title = anime.get("title") or f"集数_{i}"
                magnet = anime.get("magnet", "")

                try:
                    print(f"处理单集: {title}")

                    # 直接下载到指定文件夹
                    result = await self.download_to_folder(
                        client, magnet, folder_id, title
                    )

                    if result["success"]:
                        added_count += 1
                        print(f"    单集下载任务添加成功")
                    else:
                        failed_count += 1
                        failed_episodes.append(
                            {"title": title, "reason": result["message"]}
                        )
                        print(f"    单集下载任务添加失败: {result['message']}")

                except Exception as e:
                    failed_count += 1
                    failed_episodes.append({"title": title, "reason": str(e)})
                    print(f"    单集下载异常: {str(e)}")

            # 成功添加至少一个集数才算成功
            success = added_count > 0

            if success:
                if failed_count == 0:
                    message = f"成功添加 {added_count} 个新集数"
                else:
                    message = f"添加完成: 成功 {added_count} 个，失败 {failed_count} 个"
            else:
                message = f"所有 {failed_count} 个集数都添加失败"

            # 如果有成功的下载，延时启动重命名任务
            if added_count > 0:
                print(f"安排8秒后为文件夹 {folder_id} 执行重命名任务")
                asyncio.create_task(
                    self.delayed_rename_task(client, folder_id, delay_seconds=8)
                )

            return {
                "success": success,
                "message": message,
                "added_count": added_count,
                "failed_count": failed_count,
                "failed_episodes": failed_episodes,
            }

        except Exception as e:
            print(f"更新动漫异常: {e}")
            return {
                "success": False,
                "message": f"更新动漫失败: {str(e)}",
                "added_count": 0,
                "failed_count": len(anime_list),
            }
