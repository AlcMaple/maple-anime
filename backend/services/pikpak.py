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
from exceptions import (
    NotFoundException,
    SystemException,
    DuplicateException,
    ValidationException,
)


class PikPakService:
    """PikPakAPI"""

    def __init__(self):
        self.clients = {}  # 客户端连接
        self.my_pack_id = settings.ANIME_CONTAINER_ID
        self.anime_db = PikPakDatabase()
        self.links_scheduler = None

    async def _get_links_scheduler(self):
        """延迟导入并获取链接调度器实例"""
        if self.links_scheduler is None:
            try:
                from scheduler.links_scheduler import LinksScheduler

                self.links_scheduler = LinksScheduler(
                    settings.PIKPAK_USERNAME, settings.PIKPAK_PASSWORD
                )
                # 调度器启动
                if not self.links_scheduler.scheduler:
                    await self.links_scheduler.start()
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
        self, client: PikPakApi, before_folders: List[str], max_retries: int = 30
    ) -> Optional[Dict]:
        """
        在 My Pack 内查找新文件夹

        Args:
            client: PikPak客户端
            before_folders: 下载前的文件夹名称列表
            max_retries: 最大重试次数

        Returns:
            新文件夹信息，如果没找到返回None

        Raises:
            SystemException: 当网络异常或系统错误时抛出
        """
        check_interval = 2  # 检查间隔，单位秒

        for attempt in range(max_retries):
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
                    new_folder_name = new_folders[0]
                    for folder in current_folder_list:
                        if folder["name"] == new_folder_name:
                            logger.debug(
                                f"在 My Pack 内找到新文件夹: {folder['name']} (ID: {folder['id']})"
                            )
                            return folder

                if attempt < max_retries - 1:  # 不是最后一次尝试
                    await asyncio.sleep(check_interval)

            except SystemException:
                # 获取文件夹列表的系统异常
                if attempt == max_retries - 1:  # 最后一次尝试
                    raise
                logger.warning(
                    f"获取文件夹列表失败，{check_interval}秒后重试 (尝试 {attempt + 1}/{max_retries})"
                )
                await asyncio.sleep(check_interval)
            except Exception as e:
                logger.error(f"查找新文件夹时出错: {e}")
                if attempt == max_retries - 1:  # 最后一次尝试
                    raise SystemException(
                        message="查找新文件夹时发生未知错误", original_error=e
                    )
                await asyncio.sleep(check_interval)

        logger.warning("超时未找到新生成的文件夹，可能是下载失败")
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
                logger.info(f"成功重命名动漫: {new_name}")
                return True
            else:
                logger.warning(f"重命名文件夹动漫: {new_name}")
                return False

        except Exception as e:
            logger.error(f"重命名文件夹异常: {e}")
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

    async def batch_download_collection(
        self, client: PikPakApi, anime_list: List[Dict], target_folder_name: str
    ) -> Dict:
        """
        批量下载合集

        Args:
            client: PikPak客户端
            anime_list: 动漫列表,每个对象包含 {id, title, magnet}
            target_folder_name: 目标文件夹名称

        Returns:
            success: 是否成功
            message: 返回信息
            task_id_list: 下载任务ID列表
            renamed_folders: 重命名的文件夹列表
        """
        try:
            # 检查 My Pack 内目标文件夹是否已存在
            logger.debug(f"你当前要下载的动漫数据: {anime_list}")
            existing_folders = await self.get_mypack_folder_list(client)
            for folder in existing_folders:
                if folder["name"] == target_folder_name:
                    logger.warning(
                        f"动漫 '{target_folder_name}' 已存在，如需更改内容请前往'更新'功能"
                    )
                    return {
                        "success": False,
                        "message": f"文件夹 '{target_folder_name}' 已存在",
                    }

            # 获取下载前的文件夹列表
            before_folders = [f["name"] for f in existing_folders]
            logger.debug(f"My Pack 内下载前的文件夹名称列表: {before_folders}")
            renamed_folders = []

            for anime in anime_list:
                title = anime.get("title")
                magnet = anime.get("magnet")

                # 下载到 My Pack
                logger.info(f"开始下载 {title}")
                result = await self.download_to_root(client, magnet, title)
                if result["success"]:
                    # 等待并查找新生成的文件夹
                    new_folder = await self.find_new_folder(client, before_folders)
                    if new_folder:
                        # 重命名文件夹
                        rename_success = await self.rename_folder(
                            client, new_folder["id"], target_folder_name
                        )

                        if rename_success:
                            renamed_folders.append(
                                {
                                    "old_name": new_folder["name"],
                                    "new_name": target_folder_name,
                                    "folder_id": new_folder["id"],
                                }
                            )

                            asyncio.create_task(
                                self.delayed_rename_task(
                                    client, new_folder["id"], delay_seconds=8
                                )
                            )

                            logger.debug(
                                f" 已为文件夹 {target_folder_name} 安排8秒后重命名任务"
                            )

                        # 更新before_folders，避免重复检测
                        before_folders.append(target_folder_name)

            return {
                "success": True,
                "message": f"成功处理{len(renamed_folders)}个合集",
                "renamed_folders": renamed_folders,
            }

        except Exception as e:
            return {"success": False, "message": f"合集下载异常: {str(e)}"}

    async def batch_download(
        self, client: PikPakApi, anime_list: List[Dict], folder_id: str
    ) -> Dict:
        """
        批量下载磁力链接到指定文件夹

        Args:
            client: PikPak客户端
            anime_list: 动漫列表,每个对象包含 {id, title, magnet}
            folder_id: 目标文件夹ID

        Returns:
            task_id_list: 下载任务ID列表
            folder_id: 目标文件夹ID
        """
        try:
            task_id_list = []
            for anime in anime_list:
                title = anime.get("title")
                magnet = anime.get("magnet")
                result = await self.download_to_folder(client, magnet, folder_id, title)
                if result["success"]:
                    task_id_list.append(result["task_id"])

            asyncio.create_task(
                self.delayed_rename_task(client, folder_id, delay_seconds=8)
            )

            return {
                "success": True,
                "message": f"成功添加{len(task_id_list)}个下载任务",
                "task_id_list": task_id_list,
                "folder_id": folder_id,
            }
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
            # 合集和单集处理
            collection_items = []
            single_items = []
            folder_id = None
            for anime in anime_list:
                if is_collection(anime.title):
                    collection_items.append(anime)
                else:
                    single_items.append(anime)

            # 获取下载前的文件夹列表（检测合集下载的新文件夹）
            before_folders = []
            if collection_items:
                try:
                    mypack_folders = await self.get_mypack_folder_list(client)
                    before_folders = [f["name"] for f in mypack_folders]
                    logger.info(f"下载前动漫列表：{before_folders}")
                except SystemException as e:
                    logger.critical(f"获取 My Pack 文件夹列表失败: {e}")
                    raise SystemException(
                        message="获取 My Pack 文件夹列表失败，下载中止",
                        original_error=e.original_error,
                    )

            # 处理合集
            collection_result = None
            if collection_items:
                # 转换AnimeItem对象为字典格式
                collection_items_dict = []
                for item in collection_items:
                    if hasattr(item, "dict"):
                        collection_items_dict.append(item.dict())
                    else:
                        collection_items_dict.append(item)

                # 下载合集
                collection_result = await self.batch_download_collection(
                    client, collection_items_dict, target_folder_name
                )
                if not collection_result["success"]:
                    raise SystemException(
                        message="下载合集失败",
                        original_error=collection_result["message"],
                    )

            # 处理单集
            single_result = None
            if single_items:
                folder_id = await self.create_anime_folder(client, target_folder_name)
                if not folder_id:
                    raise DuplicateException(
                        resource="My Pack", field="folder_id", value=target_folder_name
                    )

                # 转换AnimeItem对象为字典格式
                single_items_dict = []
                for item in single_items:
                    if hasattr(item, "dict"):
                        single_items_dict.append(item.dict())
                    else:
                        single_items_dict.append(item)

                single_result = await self.batch_download(
                    client, single_items_dict, folder_id
                )
                if not single_result["success"]:
                    raise SystemException(
                        message="下载单集失败",
                        original_error=single_result["message"],
                    )

            return {
                "collection_count": len(collection_items),
                "single_count": len(single_items),
            }

        except (SystemException, DuplicateException):
            raise
        except Exception as e:
            logger.critical(f"批量下载异常: {e}")
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
            print("将要重命名的文件 id：", file_id)
            result = await client.file_rename(file_id, new_name)
            logger.debug("rename_result:", result)
            print("rename_result:", result)

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

            # API限流配置
            api_call_count = 0
            api_batch_size = 3  # 每3次API调用后休息
            api_delay = 8  # 休息8秒

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
                api_call_count += 1

                if rename_result:
                    renamed_files.append(file)
                    logger.info(f"成功重命名文件: {original_name} -> {episode_num}")
                else:
                    failed_files.append(file)
                    logger.warning(f"重命名失败: {original_name}")

                # 检查是否需要延时以避免触发API限流
                if api_call_count % api_batch_size == 0:
                    logger.info(
                        f"已调用 {api_call_count} 次重命名API，延时 {api_delay} 秒避免限流..."
                    )
                    await asyncio.sleep(api_delay)

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
            raise SystemException(message="获取云端文件夹列表失败", original_error=e)

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
            logger.warning(f"获取视频播放连接异常: {e}")
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
                    logger.debug(
                        f" 找到 My Pack 文件夹: {folder_name} (ID: {folder['id']})"
                    )
                    return folder["id"]

            logger.debug(" 未找到 My Pack 文件夹")
            return None

        except Exception as e:
            logger.critical(f" 获取 My Pack 文件夹ID异常: {e}")
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
                links_scheduler = await self._get_links_scheduler()
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

            # 启动并初始化调度器
            links_scheduler = await self._get_links_scheduler()
            if links_scheduler:
                # 重新初始化
                await links_scheduler.reinitialize()
            return True
        except Exception as e:
            logger.critical(f"同步数据失败: {e}")
            return False

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
            # 分类处理：合集和单集
            single_items = []

            for anime in anime_list:
                title = anime.get("title", "")
                if is_collection(title):
                    # 更新禁止使用合集
                    raise ValidationException(
                        message="更新动漫集数不支持合集，请使用单集更新"
                    )
                single_items.append(anime)

            # 处理单集
            # 转换 AnimeItem 对象为字典格式
            items = []
            for anime in single_items:
                if hasattr(anime, "dict"):
                    items.append(anime.dict())
                else:
                    items.append(anime)

            # 下载
            result = await self.batch_download(client, items, folder_id)
            if not result["success"]:
                raise SystemException(
                    message="更新单集失败",
                    original_error=result["message"],
                )

            return {
                "single_count": len(single_items),
            }

        except Exception as e:
            logger.critical(f"更新动漫异常: {e}")
            raise SystemException(message="更新动漫失败", original_error=e)
