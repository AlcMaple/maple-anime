"""
链接调度器
"""

import asyncio
from datetime import datetime, timedelta
from typing import Dict, List
import pytz
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from apscheduler.executors.asyncio import AsyncIOExecutor

from database.pikpak import PikPakDatabase
from api.pikpak import PikPakService
from config.settings import settings


# 信号量管理器
class SemaphoreManager:
    _instance = None
    _semaphore = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    @classmethod
    def get_api_semaphore(cls):
        if cls._semaphore is None:
            cls._semaphore = asyncio.Semaphore(1)
        return cls._semaphore


async def update_anime_task(
    folder_id: str, username: str, password: str, container_id: str, update_hours: int
):
    """更新动漫任务的静态函数"""
    # 使用全局信号量管理器
    semaphore = SemaphoreManager.get_api_semaphore()

    async with semaphore:
        print(f"获取到 API 锁，开始更新动漫: {folder_id}")
        try:
            anime_db = PikPakDatabase()
            pikpak_service = PikPakService()

            # 获取动漫信息
            anime_detail = anime_db.get_anime_detail(folder_id, container_id)
            if not anime_detail:
                return

            # 获取动漫列表
            db_data = anime_db.load_data()
            anime_data = (
                db_data.get("animes", {}).get(container_id, {}).get(folder_id, {})
            )
            files = anime_data.get("files", [])

            if not files:
                return

            # 获取 PikPak 客户端
            client = await pikpak_service.get_client(username, password)

            success_count = 0
            failed_count = 0

            # 更新所有视频链接
            for file_info in files:
                try:
                    file_id = file_info["id"]
                    play_url = await pikpak_service.get_video_play_url(file_id, client)

                    if play_url:
                        # 更新数据库
                        res = await anime_db.update_anime_file_link(
                            file_id, play_url, container_id, folder_id
                        )

                        if res["success"]:
                            success_count += 1
                        else:
                            failed_count += 1
                    else:
                        failed_count += 1

                    # API 限流
                    await asyncio.sleep(8)

                except Exception as e:
                    failed_count += 1

            # 更新时间记录
            if success_count > 0:
                await anime_db.update_folder_video_links_time(folder_id, container_id)
                await anime_db.update_anime_info(folder_id, {}, container_id)

            print(
                f"更新完成: {anime_detail.get('title', '未知')} 成功 {success_count}, 失败 {failed_count}"
            )

        except Exception as e:
            print(f"更新失败: {e}")
        finally:
            print(f"释放 API 锁，更新动漫: {folder_id} 完成")


class LinksScheduler:
    def __init__(self, pikpak_username: str, pikpak_password: str):
        self.pikpak_username = pikpak_username
        self.pikpak_password = pikpak_password
        self.anime_db = PikPakDatabase()
        self.scheduler = None  # 调度器

        # 配置常量
        self.ANIME_CONTAINER_ID = settings.ANIME_CONTAINER_ID
        self.UPDATE_INTERVAL_HOURS = 20  # 20小时更新间隔

        # 时区配置
        self.timezone = pytz.timezone("Asia/Shanghai")

        # 不再在实例中保存不可序列化的对象

    def create_scheduler(self):
        """创建调度器"""
        # 任务存储（宕机重启后恢复）
        """
        这是一个记事本，记录所有的待办事项，使用的是data/scheduler.sqlite数据库
            当程序关闭或者重启，它会打开这个记事本，回忆起所有未完成的任务
        """
        jobstores = {
            "default": SQLAlchemyJobStore(url="sqlite:///data/scheduler.sqlite")
        }

        # 异步执行器，用于异步等待 pikpak 服务器响应
        executors = {"default": AsyncIOExecutor()}

        # 调度器配置
        job_defaults = {"coalesce": False, "max_instances": 1}

        # 默认任务参数---不合并、单实例
        self.scheduler = AsyncIOScheduler(
            jobstores=jobstores,
            executors=executors,
            job_defaults=job_defaults,
            timezone="Asia/Shanghai",
        )

    async def start(self):
        """启动调度器"""
        if not self.scheduler:
            self.create_scheduler()

        self.scheduler.start()

        # 初始化所有动漫的调度
        await self._initialize_all_anime()

    async def stop(self):
        """停止调度器"""
        if self.scheduler:
            self.scheduler.shutdown()

    async def _initialize_all_anime(self):
        """初始化所有动漫的调度任务"""
        try:
            # 获取所有动漫信息
            folders_info = self.anime_db.get_all_anime_schedule_info(
                self.ANIME_CONTAINER_ID
            )

            if not folders_info:
                return

            # 为每个动漫安排更新任务
            for folder_info in folders_info:
                await self._schedule_anime_update(folder_info)

            # 清除不存在的动漫的调度任务
            folder_ids = [folder_info["folder_id"] for folder_info in folders_info]
            await self._clear_del_scheduled_jobs(folder_ids)

        except Exception as e:
            print(f"初始化动漫调度任务失败: {e}")

    async def _clear_del_scheduled_jobs(self, folder_ids: List[str]):
        """
        清除不存在的动漫的调度任务
        """
        try:
            # 获取所有当前调度的任务
            all_jobs = self.scheduler.get_jobs()

            for job in all_jobs:
                if job.id.startswith("update_folder_"):
                    folder_id = job.id.split("_")[-1]

                    # 如果该动漫不在给定的 folder_ids 中，移除该任务
                    if folder_id not in folder_ids:
                        self.scheduler.remove_job(job.id)
                        print(f"移除不存在的动漫调度任务: {job.name}")

        except Exception as e:
            print(f"清除不存在的动漫调度任务失败: {e}")

    def remove_anime_schedule(self, folder_id: str):
        """移除指定动漫的调度任务"""
        job_id = f"update_folder_{folder_id}"
        if self.scheduler and self.scheduler.get_job(job_id):
            try:
                self.scheduler.remove_job(job_id)
                print(f"已移除不存在的动漫任务: {job_id}")
            except Exception as e:
                print(f"移除动漫任务失败 {job_id}: {e}")

    async def _schedule_anime_update(self, folder_info: Dict):
        """为动漫安排更新任务"""
        try:
            folder_id = folder_info["folder_id"]
            next_update_time = folder_info["next_update_time"]

            # 如果更新时间已过，设置为1分钟后
            current_time = datetime.now(self.timezone)

            # 确保next_update_time有时区信息
            if next_update_time.tzinfo is None:
                next_update_time = self.timezone.localize(next_update_time)

            if next_update_time <= current_time:
                next_update_time = current_time + timedelta(minutes=1)

            job_id = f"update_folder_{folder_id}"

            # 移除可能存在的旧任务
            if self.scheduler.get_job(job_id):
                self.scheduler.remove_job(job_id)

            # 添加新任务（给记事本添加待办事项）
            self.scheduler.add_job(
                func=update_anime_task,  # 使用静态函数避免序列化问题
                trigger="date",  # run_date 触发器
                run_date=next_update_time,  # 具体的执行时间
                # 传递给静态函数的参数
                args=[
                    folder_id,
                    self.pikpak_username,
                    self.pikpak_password,
                    self.ANIME_CONTAINER_ID,
                    self.UPDATE_INTERVAL_HOURS,
                ],
                id=job_id,  # 任务唯一编号
                name=f'更新 {folder_info["title"]}',
                replace_existing=True,
            )

        except Exception as e:
            print(f"安排更新失败: {e}")

    async def reinitialize(self):
        """初始化所有调度"""
        try:
            await self._initialize_all_anime()
        except Exception as e:
            print(f"链接调度初始化失败: {e}")

    # 原有的实例方法已被静态函数替代，避免序列化问题
