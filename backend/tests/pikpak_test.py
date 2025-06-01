"""
PikPak + AnimeGarden 自动化测试
流程：获取动漫 -> 下载到PikPak -> 获取播放链接
"""

import asyncio
import httpx
import json
from typing import Dict, List, Any, Optional
from pikpakapi import PikPakApi


class AnimeAutoPipeline:
    def __init__(self, pikpak_username: str, pikpak_password: str):
        # PikPak 客户端
        self.pikpak_client = PikPakApi(
            username=pikpak_username,
            password=pikpak_password,
        )

        # AnimeGarden API 客户端
        self.anime_client = httpx.AsyncClient(timeout=30.0)
        self.anime_base_url = "https://api.animes.garden"

    async def init_pikpak(self):
        """初始化 PikPak 连接"""
        try:
            print("🔐 正在登录 PikPak...")
            await self.pikpak_client.login()
            print("✅ PikPak 登录成功")
            return True
        except Exception as e:
            print(f"❌ PikPak 登录失败: {e}")
            return False

    async def get_anime_resources(
        self, page: int = 1, page_size: int = 1
    ) -> Dict[str, Any]:
        """获取动漫资源列表"""
        try:
            url = f"{self.anime_base_url}/resources"
            params = {"page": page, "pageSize": page_size}

            response = await self.anime_client.get(url, params=params)
            response.raise_for_status()

            data = response.json()
            print(f"📡 获取到 {len(data.get('resources', []))} 个动漫资源")
            return data

        except Exception as e:
            print(f"❌ 获取动漫资源失败: {e}")
            return {"error": str(e)}

    async def download_to_pikpak(self, magnet_link: str, title: str) -> bool:
        """将磁力链接下载到 PikPak"""
        try:
            print(f"⬇️ 正在添加下载任务: {title[:50]}...")

            result = await self.pikpak_client.offline_download(magnet_link)

            if result:
                print(f"✅ 下载任务添加成功")
                return True
            else:
                print(f"❌ 下载任务添加失败")
                return False

        except Exception as e:
            print(f"❌ 添加下载任务出错: {e}")
            return False

    async def get_download_list(self) -> List[Dict]:
        """获取下载任务列表"""
        try:
            print("📋 获取下载任务列表...")
            result = await self.pikpak_client.offline_list()
            print(f"📋 当前有 {len(result.get('tasks', []))} 个下载任务")
            return result.get("tasks", [])
        except Exception as e:
            print(f"❌ 获取下载列表失败: {e}")
            return []

    async def get_file_list(self, parent_id: str = "") -> List[Dict]:
        """获取文件列表"""
        try:
            print("📁 获取云盘文件列表...")
            result = await self.pikpak_client.file_list(parent_id=parent_id)
            files = result.get("files", [])
            print(f"📁 找到 {len(files)} 个文件")
            return files
        except Exception as e:
            print(f"❌ 获取文件列表失败: {e}")
            return []

    async def get_video_play_url(self, file_id: str) -> Optional[str]:
        """获取视频播放链接"""
        try:
            print(f"🎬 获取视频播放链接: {file_id}")

            # 获取文件详情和播放链接
            result = await self.pikpak_client.get_download_url(file_id)

            if result and "web_content_link" in result:
                play_url = result["web_content_link"]
                print(f"✅ 获取播放链接成功")
                return play_url
            else:
                print(f"❌ 无法获取播放链接")
                return None

        except Exception as e:
            print(f"❌ 获取播放链接失败: {e}")
            return None

    async def demo_workflow(self):
        """演示完整工作流程"""
        print("🚀 启动动漫自动化流水线演示")
        print("=" * 60)

        # 1. 初始化 PikPak
        if not await self.init_pikpak():
            return

        # 2. 获取动漫资源
        anime_data = await self.get_anime_resources(page=1, page_size=1)
        if "error" in anime_data:
            return

        resources = anime_data.get("resources", [])

        if not resources:
            print("❌ 没有找到动漫资源")
            return

        # 3. 显示可用资源
        print("\n📺 可用动漫资源:")
        for i, resource in enumerate(resources):
            print(f"  {i+1}. {resource['title'][:80]}...")
            print(f"     大小: {resource['size'] / 1024 / 1024:.1f} MB")
            print(f"     字幕组: {resource.get('fansub', {}).get('name', '未知')}")
            print()

        # 4. 获取当前下载列表
        await self.get_download_list()

        # 5. 获取云盘文件列表
        files = await self.get_file_list()

        # 6. 查找视频文件并获取播放链接
        video_files = [
            f
            for f in files
            if f.get("kind") == "drive#file"
            and any(
                ext in f.get("name", "").lower()
                for ext in [".mp4", ".mkv", ".avi", ".mov"]
            )
        ]

        if video_files:
            print(f"\n🎬 找到 {len(video_files)} 个视频文件:")
            for video in video_files[:3]:  # 只显示前3个
                print(f"  📹 {video['name']}")
                play_url = await self.get_video_play_url(video["id"])
                if play_url:
                    print(f"     播放链接: {play_url}")
                print()

        print("=" * 60)
        print("✨ 演示完成")


async def main():
    # PikPak 账号信息
    print("请输入你的 PikPak 账号信息:")
    username = input("用户名 (邮箱或手机号): ").strip()
    password = input("密码: ").strip()

    if not username or not password:
        print("❌ 用户名和密码不能为空")
        return

    # 创建自动化流水线
    pipeline = AnimeAutoPipeline(username, password)

    # 运行演示
    await pipeline.demo_workflow()


if __name__ == "__main__":
    asyncio.run(main())
