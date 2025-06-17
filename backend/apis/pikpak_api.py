import re
import asyncio
from typing import Dict, List, Any, Optional
from pikpakapi import PikPakApi
from utils.analyzer import Analyzer
import time
from pathlib import Path
import json


class PikPakService:
    """PikPakAPI"""

    def __init__(self):
        self.clients = {}  # 客户端连接
        self.analyzer = Analyzer()
        # self._back_mask = {}  # 后台任务
        self.my_pack_id = "VOQqzYAEiKo3JmMhSvj6UYvto2"

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
                    print(f"动漫 '{folder_name}' 已存在，如需更改内容请前往'更新'功能")
                    return None

            # 在 My Pack 内创建新文件夹
            result = await client.create_folder(folder_name, parent_id=self.my_pack_id)
            print("创建文件夹响应信息：", result["file"]["id"])

            if result and "file" in result and "id" in result["file"]:
                print(f"成功在 My Pack 内创建文件夹: {folder_name}")
                return result["file"]["id"]
            else:
                print(f"创建文件夹失败: {folder_name}")
                return None

        except Exception as e:
            print(f"创建文件夹异常: {e}")
            return None

    async def download_to_root(
        self, client: PikPakApi, magnet: str, title: str
    ) -> Dict:
        """
        下载磁力链接到 My Pack
        """
        try:
            result = await client.offline_download(magnet)
            print("=" * 60)
            print("离线下载响应信息：", result)
            print("=" * 60)

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
                print(f"My Pack 内当前文件夹名称列表: {current_folder_names}")

                # 找出新增的文件夹
                new_folders = [
                    f for f in current_folder_names if f not in before_folders
                ]

                if new_folders:
                    # 找到新文件夹，返回第一个（通常合集只生成一个文件夹）
                    new_folder = new_folders[0]
                    for folder in current_folder_list:
                        if folder["name"] == new_folder:
                            print(
                                f"✅ 在 My Pack 内找到新文件夹: {folder['name']} (ID: {folder['id']})"
                            )
                            return folder

                await asyncio.sleep(check_interval)

            except Exception as e:
                print(f"查找新文件夹时出错: {e}")
                await asyncio.sleep(check_interval)

        print("该磁链下载超时，可能是p2p 种子下载失败")
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
            existing_folders = await self.get_mypack_folder_list(client)
            for folder in existing_folders:
                if folder["name"] == target_folder_name:
                    print(
                        f"动漫 '{target_folder_name}' 已存在，如需更改内容请前往'更新'功能"
                    )
                    return {
                        "success": False,
                        "message": f"文件夹 '{target_folder_name}' 已存在",
                    }

            # 获取下载前的文件夹列表
            before_folders = [f["name"] for f in existing_folders]
            print(f"My Pack 内下载前的文件夹名称列表: {before_folders}")

            # task_id_list = []
            renamed_folders = []

            for anime in anime_list:
                title = anime.get("title")
                magnet = anime.get("magnet")

                # 下载到 My Pack
                result = await self.download_to_root(client, magnet, title)
                if result["success"]:
                    # task_id_list.append(result["task_id"])

                    # 等待并查找新生成的文件夹
                    new_folder = await self.find_new_folder(client, before_folders)
                    # print(f"新文件夹Id ---- 用于后续重命名文件: {new_folder}")

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

                            # back_task_id = (
                            #     f"rename_{new_folder['id']}_{int(time.time())}"
                            # )

                            # asyncio.create_task(
                            #     self._back_download_monitor(
                            #         client, task_id_list, new_folder["id"], back_task_id
                            #     )
                            # )

                            asyncio.create_task(
                                self.delayed_rename_task(
                                    client, new_folder["id"], delay_seconds=5
                                )
                            )

                            print(
                                f"📝 已为文件夹 {target_folder_name} 安排5秒后重命名任务"
                            )

                        # 更新before_folders，避免重复检测
                        before_folders.append(target_folder_name)

            return {
                "success": True,
                "message": f"成功处理{len(renamed_folders)}个合集",
                # "task_id_list": task_id_list,
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

            # back_task_id = f"rename_{folder_id}_{int(time.time())}"

            # # 启动后台任务
            # asyncio.create_task(
            #     self._back_download_monitor(
            #         client, task_id_list, folder_id, back_task_id
            #     )
            # )

            asyncio.create_task(
                self.delayed_rename_task(client, folder_id, delay_seconds=5)
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
        self, client: PikPakApi, anime_list: List[Dict], target_folder_name: str
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
            collection_items = []  # 合集资源
            single_items = []  # 单集资源

            for anime in anime_list:
                title = anime.get("title")
                if self.analyzer.is_collection(title):
                    collection_items.append(anime)
                else:
                    single_items.append(anime)

            results = []

            # 处理合集资源
            if collection_items:
                print(f"发现 {len(collection_items)} 个合集资源，使用合集处理模式")
                collection_result = await self.batch_download_collection(
                    client, collection_items, target_folder_name
                )
                results.append(collection_result)

            # 处理单集资源
            if single_items:
                print(f"发现 {len(single_items)} 个单集资源，使用普通处理模式")
                # 在 My Pack 内创建文件夹
                folder_id = await self.create_anime_folder(client, target_folder_name)
                if folder_id:
                    single_result = await self.batch_download(
                        client, single_items, folder_id
                    )
                    results.append(single_result)
                else:
                    results.append(
                        {
                            "success": False,
                            "message": f"为单集资源创建文件夹失败: {target_folder_name}",
                        }
                    )

            # 处理响应
            success_count = sum(1 for r in results if r.get("success"))
            total_tasks = sum(len(r.get("task_id_list", [])) for r in results)

            return {
                "success": success_count > 0,
                "message": f"下载完成，共处理 {total_tasks} 个任务",
                "collection_count": len(collection_items),
                "single_count": len(single_items),
                "results": results,
            }

        except Exception as e:
            return {"success": False, "message": f"下载异常: {str(e)}"}

    """

    async def _back_download_monitor(
        self,
        client: PikPakApi,
        task_id_list: List[str],
        folder_id: str,
        back_task_id: str,
    ):
        '''
        后台监控下载进度
        '''
        try:
            self._back_mask[back_task_id] = {
                "status": "monitoring",
                "folder_id": folder_id,
                "total_tasks": len(task_id_list),
                "completed_tasks": 0,
            }

            # 等待下载完成
            completed_tasks = await self._wait_for_downloads_complete(
                client, folder_id, back_task_id
            )

            if completed_tasks:
                # 状态更新
                self._back_mask[back_task_id]["status"] = "renaming"
                self._back_mask[back_task_id]["completed_tasks"] = len(completed_tasks)

                # 重命名文件
                rename_result = await self.batch_rename_file(client, folder_id)

                # 状态更新
                self._back_mask[back_task_id]["status"] = "completed"
                self._back_mask[back_task_id]["rename_result"] = rename_result
            else:
                print(f"⚠️ {folder_id}: 没有文件下载完成")
                self._back_mask[back_task_id]["status"] = "no_files_completed"

        except Exception as e:
            print(f"❌ 后台任务异常 {back_task_id}: {e}")
            self._back_mask[back_task_id]["status"] = "error"
            self._back_mask[back_task_id]["error"] = str(e)

    async def _wait_for_downloads_complete(
        self,
        client: PikPakApi,
        folder_id: str,
        back_task_id: str,
    ) -> List[str]:
        '''
        等待下载完成

        Args:
            client: PikPak客户端
            folder_id: 目标文件夹ID
            back_task_id: 后台任务ID（用于状态更新）

        Returns:
            List[str]: 下载完成的文件ID列表

        工作原理：
        1. 定时检查目标文件夹中的文件
        2. 监控文件的下载状态（phase字段）
        3. 当文件状态为 PHASE_TYPE_COMPLETE 时表示下载完成
        '''
        start_time = time.time()
        check_interval = 2  # 检查间隔, 单位秒
        timeout = 60  # 超时时间，单位秒

        while (time.time() - start_time) < timeout:
            try:
                # 获取文件列表
                file_list = await client.file_list(parent_id=folder_id)
                if not file_list or "files" not in file_list:
                    print("⚠️ 无法获取文件列表，继续等待...")
                    await asyncio.sleep(check_interval)
                    continue
                current_file_count = len(file_list["files"])

                # 文件下载状态
                completed_files = []  # 本次检查中已完成的文件
                downloading_files = []  # 正在下载的文件
                pending_files = []  # 等待下载的文件

                files = file_list["files"]
                for file in files:
                    phase = file.get("phase", "")
                    file_name = file.get("name", "Unknown")
                    file_id = file.get("id")

                    if phase == "PHASE_TYPE_COMPLETE":
                        # 文件下载完成
                        completed_files.append(file_id)
                    elif phase == "PHASE_TYPE_RUNNING":
                        # 文件正在下载
                        downloading_files.append(file_name)
                    elif phase == "PHASE_TYPE_PENDING":
                        # 文件等待下载
                        pending_files.append(file_name)
                    else:
                        # 其他状态（可能是错误状态）
                        print(f"⚠️ 文件 {file_name} 状态异常: {phase}")

                # 更新任务状态
                if back_task_id in self._back_mask:
                    self._back_mask[back_task_id]["completed_tasks"] = len(
                        completed_files
                    )
                    self._back_mask[back_task_id]["downloading_files"] = len(
                        downloading_files
                    )
                    self._back_mask[back_task_id]["pending_files"] = len(pending_files)
                    self._back_mask[back_task_id]["progress_percentage"] = (
                        len(completed_files) / max(current_file_count, 1)
                    ) * 100

                # 下载完成，结束监控
                print("完成的文件数: ", len(completed_files))
                print("当前文件数: ", current_file_count)
                if (
                    len(completed_files) == current_file_count
                    and current_file_count > 0
                ):
                    print(f"✅ {folder_id}: 全部文件下载完成")
                    return completed_files

            except Exception as e:
                print(f"🔍 检查下载状态时出错: {e}")

            # 等待下次检查
            await asyncio.sleep(check_interval)

        # 超时处理
        print(f"⏰ 监控超时({timeout//60}分钟)")
        return []

    """

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
            result = await client.file_rename(file_id, new_name)

            if result and isinstance(result, dict) and "id" in result:
                return True
            else:
                return False

        except Exception as e:
            print(f"重命名文件异常: {e}")
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
            # print("将重命名文件的文件夹：", folder_id)
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
                episode_num = self.analyzer.get_anime_episodes(original_name)
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

            print(
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
        self, client: PikPakApi, folder_id: str, delay_seconds: int = 5
    ):
        """
        延时重命名任务

        Args:
            client: PikPak客户端
            folder_id: 文件夹ID
            delay_seconds: 延时秒数，默认5秒
        """
        try:
            print(
                f"🕐 将在 {delay_seconds} 秒后开始重命名文件夹 {folder_id} 中的文件..."
            )
            await asyncio.sleep(delay_seconds)

            print(f"🚀 开始重命名文件夹 {folder_id} 中的文件...")
            rename_result = await self.batch_rename_file(client, folder_id)

            if rename_result["success"]:
                print(f"✅ 文件夹 {folder_id} 重命名完成: {rename_result['message']}")
            else:
                print(f"❌ 文件夹 {folder_id} 重命名失败: {rename_result['message']}")

        except Exception as e:
            print(f"❌ 延时重命名任务异常: {e}")

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
            print(f"获取 My Pack 文件夹列表异常: {e}")
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
            print(f"📁 获取文件夹 {folder_id} 内的文件列表...")

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

            print(f"✅ 获取到 {len(file_list)} 个文件（共 {len(files)} 个项目）")

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
            print(f"❌ 获取文件夹文件列表失败: {e}")
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
                print(f"✅ 文件删除成功")
                return {"success": True, "message": "文件删除成功"}
            else:
                print(f"❌ 文件删除失败")
                return {"success": False, "message": "文件删除失败"}

        except Exception as e:
            print(f"❌ 删除文件异常: {e}")
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
            print(f"🗑️ 批量删除 {len(file_ids)} 个文件...")

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
                    print(f"❌ 删除文件 {file_id} 失败: {e}")
                    failed_count += 1

            print(f"✅ 批量删除完成: 成功 {deleted_count} 个，失败 {failed_count} 个")

            return {
                "success": deleted_count > 0,
                "message": f"批量删除完成: 成功 {deleted_count} 个，失败 {failed_count} 个",
                "deleted_count": deleted_count,
                "failed_count": failed_count,
            }

        except Exception as e:
            print(f"❌ 批量删除异常: {e}")
            return {
                "success": False,
                "message": f"批量删除失败: {str(e)}",
                "deleted_count": 0,
                "failed_count": len(file_ids),
            }
