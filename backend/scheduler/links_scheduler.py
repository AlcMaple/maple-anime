"""
链接调度器
"""

import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from apscheduler.executors.asyncio import AsyncIOExecutor

from database.pikpak import PikPakDatabase
from apis.pikpak_api import PikPakService


class LinksScheduler:
    def __init__(self, pikpak_username: str, pikpak_password: str):
        self.pikpak_username = pikpak_username
        self.pikpak_password = pikpak_password
        self.pikpak_service = PikPakService()
        self.anime_db = PikPakDatabase()
        self.scheduler = None  # 调度器

        # 配置常量
        self.ANIME_CONTAINER_ID = "VOQqzYAEiKo3JmMhSvj6UYvto2"
        self.UPDATE_INTERVAL_HOURS = 20  # 20小时更新间隔

    def create_scheduler(self):
        """创建调度器"""
        # 任务存储（宕机重启后恢复）
        jobstores = {
            "default": SQLAlchemyJobStore(url="sqlite:///data/scheduler.sqlite")
        }

        # 异步执行器
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

        # 初始化所有文件夹的调度
        await self._initialize_all_folders()

    async def stop(self):
        """停止调度器"""
        if self.scheduler:
            self.scheduler.shutdown()

    async def _initialize_all_folders(self):
        """初始化所有文件夹的调度任务"""
        try:
            # 获取所有文件夹信息
            folders_info = self.anime_db.get_all_folders_schedule_info(
                self.ANIME_CONTAINER_ID
            )

            if not folders_info:
                return

            # 为每个文件夹安排更新任务
            for folder_info in folders_info:
                await self._schedule_folder_update(folder_info)

            # 下次检查时间
            await self._schedule_next_check()

        except Exception as e:
            print(f"初始化文件夹失败: {e}")

    async def _schedule_folder_update(self, folder_info: Dict):
        """为文件夹安排更新任务"""
        try:
            folder_id = folder_info["folder_id"]
            next_update_time = folder_info["next_update_time"]

            # 如果更新时间已过，设置为1分钟后
            current_time = datetime.now()
            if next_update_time <= current_time:
                next_update_time = current_time + timedelta(minutes=1)

            job_id = f"update_folder_{folder_id}"

            # 移除可能存在的旧任务
            if self.scheduler.get_job(job_id):
                self.scheduler.remove_job(job_id)

            # 添加新任务
            self.scheduler.add_job(
                func=self._update_folder,
                trigger="date",  # 指定精准触发时间
                run_date=next_update_time,
                args=[folder_id],
                id=job_id,
                name=f'更新 {folder_info["title"]}',
                replace_existing=True,
            )

        except Exception as e:
            print(f"安排更新失败: {e}")

    async def _update_folder(self, folder_id: str):
        """更新单个文件夹的视频链接"""
        try:
            # 获取文件夹信息
            anime_detail = self.anime_db.get_anime_detail(
                folder_id, self.ANIME_CONTAINER_ID
            )
            if not anime_detail:
                return

            # 获取文件列表
            db_data = self.anime_db.load_data()
            anime_data = (
                db_data.get("animes", {})
                .get(self.ANIME_CONTAINER_ID, {})
                .get(folder_id, {})
            )
            files = anime_data.get("files", [])

            if not files:
                return

            # 获取 PikPak 客户端
            client = await self.pikpak_service.get_client(
                self.pikpak_username, self.pikpak_password
            )

            # 更新所有视频链接
            success_count = 0
            failed_count = 0

            for file_info in files:
                try:
                    file_id = file_info["id"]
                    play_url = await self.pikpak_service.get_video_play_url(
                        file_id, client
                    )

                    if play_url:
                        # 更新数据库
                        res = await self.anime_db.update_anime_file_link(
                            file_id, play_url, self.ANIME_CONTAINER_ID, folder_id
                        )

                        if res["success"]:
                            success_count += 1
                        else:
                            failed_count += 1
                    else:
                        failed_count += 1

                    # API 限流
                    await asyncio.sleep(2)

                except Exception as e:
                    failed_count += 1

            # 更新时间记录
            if success_count > 0:
                await self.anime_db.update_folder_video_links_time(
                    folder_id, self.ANIME_CONTAINER_ID
                )
                await self.anime_db.update_anime_info(
                    folder_id, {}, self.ANIME_CONTAINER_ID
                )

            # 安排下次更新
            next_update_time = datetime.now() + timedelta(
                hours=self.UPDATE_INTERVAL_HOURS
            )
            job_id = f"update_folder_{folder_id}"

            self.scheduler.add_job(
                func=self._update_folder,
                trigger="date",
                run_date=next_update_time,
                args=[folder_id],
                id=job_id,
                name=f'更新 {anime_detail.get("title", "未知")}',
                replace_existing=True,
            )

            # 重新计算下次检查时间
            await self._schedule_next_check()

        except Exception as e:
            print(f"更新失败: {e}")

    async def _schedule_next_check(self):
        """下次检查时间"""
        try:
            # 获取所有计划任务的执行时间
            scheduled_times = []
            for job in self.scheduler.get_jobs():
                if job.id.startswith("update_folder_") and job.next_run_time:
                    scheduled_times.append(job.next_run_time)

            if not scheduled_times:
                # 没有任务，6小时后检查
                next_check_time = datetime.now() + timedelta(hours=6)
            else:
                # 找最近的任务时间，提前30分钟检查
                next_task_time = min(scheduled_times)
                next_check_time = next_task_time - timedelta(minutes=30)

                # 确保至少10分钟后检查
                min_check_time = datetime.now() + timedelta(minutes=10)
                if next_check_time < min_check_time:
                    next_check_time = min_check_time

            # 移除旧的检查任务
            if self.scheduler.get_job("dynamic_check"):
                self.scheduler.remove_job("dynamic_check")

            # 添加新的检查任务
            self.scheduler.add_job(
                func=self._dynamic_check,
                trigger="date",
                run_date=next_check_time,
                id="dynamic_check",
                name="动态检查任务",
                replace_existing=True,
            )

        except Exception as e:
            print(f"安排检查失败: {e}")

    async def _dynamic_check(self):
        """检查任务"""
        try:
            # 重新初始化所有文件夹
            await self._initialize_all_folders()

        except Exception as e:
            print(f"动态检查失败: {e}")

    async def reinitialize(self):
        """初始化所有调度"""
        try:
            await self._initialize_all_folders()
        except Exception as e:
            print(f"链接调度初始化失败: {e}")

    def get_status(self) -> Dict:
        """获取调度器状态和所有任务的下次执行时间"""
        if not self.scheduler:
            return {"status": "stopped", "jobs": []}

        jobs = []
        for job in self.scheduler.get_jobs():
            jobs.append(
                {
                    "id": job.id,
                    "name": job.name,
                    "next_run_time": (
                        job.next_run_time.isoformat() if job.next_run_time else None
                    ),
                }
            )

        # 按执行时间排序
        jobs.sort(key=lambda x: x["next_run_time"] or "9999")

        return {"status": "running", "total_jobs": len(jobs), "jobs": jobs}
