"""
链接调度器
"""

import asyncio
from datetime import datetime, timedelta
from typing import Dict
import pytz
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from apscheduler.executors.asyncio import AsyncIOExecutor

from database.pikpak import PikPakDatabase
from api.pikpak import PikPakService
from config.settings import settings


# 全局静态函数避免序列化问题
async def update_anime_task(
    folder_id: str, username: str, password: str, container_id: str, update_hours: int
):
    """更新动漫任务"""
    try:
        anime_db = PikPakDatabase()
        pikpak_service = PikPakService()

        # 获取动漫信息
        anime_detail = anime_db.get_anime_detail(folder_id, container_id)
        if not anime_detail:
            return

        # 获取动漫列表
        db_data = anime_db.load_data()
        anime_data = db_data.get("animes", {}).get(container_id, {}).get(folder_id, {})
        files = anime_data.get("files", [])

        if not files:
            return

        # 获取 PikPak 客户端
        client = await pikpak_service.get_client(username, password)

        # 更新所有视频链接
        success_count = 0
        failed_count = 0

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


async def dynamic_check_task(
    username: str, password: str, container_id: str, update_hours: int
):
    """动态检查任务"""
    try:
        anime_db = PikPakDatabase()

        # 获取所有动漫信息
        folders_info = anime_db.get_all_anime_schedule_info(container_id)

        if not folders_info:
            return

        print(f"动态检查: 找到 {len(folders_info)} 个动漫需要调度")

    except Exception as e:
        print(f"动态检查失败: {e}")


class LinksScheduler:
    def __init__(self, pikpak_username: str, pikpak_password: str):
        self.pikpak_username = pikpak_username
        self.pikpak_password = pikpak_password
        self.pikpak_service = PikPakService()
        self.anime_db = PikPakDatabase()
        self.scheduler = None  # 调度器

        # 配置常量
        self.ANIME_CONTAINER_ID = settings.ANIME_CONTAINER_ID
        self.UPDATE_INTERVAL_HOURS = 20  # 20小时更新间隔

        # 时区配置
        self.timezone = pytz.timezone("Asia/Shanghai")

    def create_scheduler(self):
        """创建调度器"""
        # 任务存储（宕机重启后恢复）
        '''
        这是一个记事本，记录所有的待办事项，使用的是data/scheduler.sqlite数据库
            当程序关闭或者重启，它会打开这个记事本，回忆起所有未完成的任务
        '''
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

            # 下次检查时间
            await self._schedule_next_check()

        except Exception as e:
            print(f"初始化动漫调度任务失败: {e}")

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
                func=update_anime_task, # 时间到时更新该动漫的链接
                trigger="date", # run_date 触发器
                run_date=next_update_time, # 具体的执行时间
                # 传递给 next_update_task 的参数
                args=[
                    folder_id,
                    self.pikpak_username,
                    self.pikpak_password,
                    self.ANIME_CONTAINER_ID,
                    self.UPDATE_INTERVAL_HOURS,
                ],
                id=job_id, # 任务唯一编号
                name=f'更新 {folder_info["title"]}',
                replace_existing=True,
            )

        except Exception as e:
            print(f"安排更新失败: {e}")

    async def _schedule_next_check(self):
        """下次检查时间"""
        try:
            # 获取所有计划任务的执行时间
            scheduled_times = []
            for job in self.scheduler.get_jobs():
                if job.id.startswith("update_folder_") and job.next_run_time:
                    scheduled_times.append(job.next_run_time)

            current_time = datetime.now(self.timezone)

            if not scheduled_times:
                # 没有任务，6小时后检查
                next_check_time = current_time + timedelta(hours=6)
            else:
                # 找最近的任务时间，提前30分钟检查
                next_task_time = min(scheduled_times)
                next_check_time = next_task_time - timedelta(minutes=30)

                # 确保至少10分钟后检查
                min_check_time = current_time + timedelta(minutes=10)
                if next_check_time < min_check_time:
                    next_check_time = min_check_time

            # 移除旧的检查任务
            if self.scheduler.get_job("dynamic_check"):
                self.scheduler.remove_job("dynamic_check")

            # 添加新的检查任务 - 使用全局函数
            self.scheduler.add_job(
                func=dynamic_check_task,
                trigger="date",
                run_date=next_check_time,
                args=[
                    self.pikpak_username,
                    self.pikpak_password,
                    self.ANIME_CONTAINER_ID,
                    self.UPDATE_INTERVAL_HOURS,
                ],
                id="dynamic_check",
                name="动态检查任务",
                replace_existing=True,
            )

        except Exception as e:
            print(f"安排检查失败: {e}")

    async def reinitialize(self):
        """初始化所有调度"""
        try:
            await self._initialize_all_anime()
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

    # 手动调度方法
    async def schedule_anime_now(self, folder_id: str):
        """立即调度某个动漫"""
        try:
            job_id = f"update_folder_{folder_id}"

            # 移除旧任务
            if self.scheduler.get_job(job_id):
                self.scheduler.remove_job(job_id)

            # 添加1分钟后执行的任务
            next_update_time = datetime.now(self.timezone) + timedelta(minutes=1)

            self.scheduler.add_job(
                func=update_anime_task,
                trigger="date",
                run_date=next_update_time,
                args=[
                    folder_id,
                    self.pikpak_username,
                    self.pikpak_password,
                    self.ANIME_CONTAINER_ID,
                    self.UPDATE_INTERVAL_HOURS,
                ],
                id=job_id,
                name=f"手动更新_{folder_id}",
                replace_existing=True,
            )

            return True

        except Exception as e:
            print(f"调度动漫失败: {e}")
            return False
