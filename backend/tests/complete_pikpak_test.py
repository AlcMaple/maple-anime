"""
完整的 PikPak + AnimeGarden 自动化测试
包含实际下载功能
"""

import asyncio
import httpx
import json
import webbrowser
import os
from typing import Dict, List, Any, Optional
from pikpakapi import PikPakApi


class CompleteAnimeAutoPipeline:
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
            print(f"🧲 磁力链接: {magnet_link}")

            # 添加离线下载任务
            result = await self.pikpak_client.offline_download(magnet_link)

            print(f"🔍 下载结果: {result}")

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
            tasks = result.get("tasks", [])
            print(f"📋 当前有 {len(tasks)} 个下载任务")

            # 显示下载任务详情
            for i, task in enumerate(tasks):
                print(
                    f"  {i+1}. {task.get('name', '未知')} - 状态: {task.get('phase', '未知')}"
                )
                print(f"     进度: {task.get('progress', 0)}%")

            return tasks
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

            # 显示文件详情
            for i, file in enumerate(files):
                print(
                    f"  {i+1}. {file.get('name', '未知')} ({file.get('kind', '未知')})"
                )
                if file.get("size"):
                    size_mb = int(file["size"]) / 1024 / 1024
                    print(f"     大小: {size_mb:.1f} MB")

            return files
        except Exception as e:
            print(f"❌ 获取文件列表失败: {e}")
            return []

    async def get_video_play_url(self, file_id: str, file_name: str) -> Optional[str]:
        """获取视频播放链接"""
        try:
            print(f"🎬 获取视频播放链接: {file_name}")

            # 方法1：尝试获取流媒体播放链接
            print("🔍 尝试获取流媒体播放链接...")
            try:
                # 获取文件详情
                file_info = await self.pikpak_client.get_file_info(file_id)
                print(f"📋 文件信息: {file_info}")

                # 检查是否有媒体链接
                if file_info and "medias" in file_info:
                    medias = file_info["medias"]
                    print(f"🎥 找到 {len(medias)} 个媒体链接")

                    for i, media in enumerate(medias):
                        print(f"  媒体 {i+1}: {media}")
                        if "link" in media and media.get("is_visible", True):
                            streaming_url = media["link"]["url"]
                            print(f"✅ 找到流媒体链接: {streaming_url}")
                            return streaming_url

            except Exception as e:
                print(f"⚠️ 获取流媒体链接失败: {e}")

            # 方法2：获取下载链接（备用）
            print("🔍 尝试获取下载链接...")
            result = await self.pikpak_client.get_download_url(file_id)
            print(f"📋 下载链接结果: {result}")

            if result and "web_content_link" in result:
                download_url = result["web_content_link"]
                print(f"📥 获取下载链接: {download_url}")
                return download_url
            else:
                print(f"❌ 无法获取任何播放链接")
                return None

        except Exception as e:
            print(f"❌ 获取播放链接失败: {e}")
            return None

    async def complete_workflow(self, should_download: bool = False):
        """完整工作流程"""
        print("🚀 启动完整动漫自动化流水线")
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
        resource = resources[0]  # 只处理第一个
        print("\n📺 当前动漫资源:")
        print(f"  标题: {resource['title']}")
        print(f"  大小: {resource['size'] / 1024 / 1024:.1f} MB")
        print(f"  字幕组: {resource.get('fansub', {}).get('name', '未知')}")
        print(f"  磁力链接: {resource['magnet']}")

        # 4. 决定是否下载
        if should_download:
            print("\n⬇️ 开始下载到 PikPak...")
            success = await self.download_to_pikpak(
                resource["magnet"], resource["title"]
            )

            if success:
                print("✅ 下载任务创建成功，等待PikPak处理...")
                print("💡 提示: 下载可能需要几分钟时间，请稍后查看云盘文件")
            else:
                print("❌ 下载失败")
        else:
            print("\n⏭️  跳过下载，直接查看现有文件...")

        # 5. 获取当前下载任务状态
        print("\n" + "=" * 40)
        await self.get_download_list()

        # 6. 获取云盘文件列表
        print("\n" + "=" * 40)
        files = await self.get_file_list()

        # 7. 查找视频文件并获取播放链接
        video_files = [
            f
            for f in files
            if f.get("kind") == "drive#file"
            and any(
                ext in f.get("name", "").lower()
                for ext in [".mp4", ".mkv", ".avi", ".mov", ".m4v"]
            )
        ]

        if video_files:
            print(f"\n🎬 找到 {len(video_files)} 个视频文件:")

            for video in video_files[:2]:  # 只处理前2个
                print(f"\n📹 正在处理: {video['name']}")
                play_url = await self.get_video_play_url(video["id"], video["name"])

                if play_url:
                    print(f"🎯 播放链接: {play_url}")

                    # 判断链接类型
                    if "download" in play_url:
                        print("📥 这是下载链接，适合直接下载")
                    else:
                        print("🎬 这是流媒体链接，适合在线播放")

                    # 询问是否测试播放
                    print("\n❓ 选择测试方式:")
                    print("  1. 在浏览器中打开测试")
                    print("  2. 生成HTML测试文件")
                    print("  3. 跳过测试")

                    try:
                        choice = input("请选择 (1/2/3): ").strip()

                        if choice == "1":
                            print("🌐 正在打开浏览器...")
                            webbrowser.open(play_url)
                            print("✅ 已在浏览器中打开")

                        elif choice == "2":
                            # 生成HTML测试文件
                            html_content = f"""
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>PikPak 视频播放测试</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        .container {{ max-width: 800px; margin: 0 auto; }}
        video {{ width: 100%; max-width: 720px; height: auto; }}
        .info {{ background: #f5f5f5; padding: 15px; margin: 20px 0; border-radius: 5px; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>🎬 PikPak 视频播放测试</h1>
        
        <div class="info">
            <h3>视频信息</h3>
            <p><strong>文件名:</strong> {video['name']}</p>
            <p><strong>链接类型:</strong> {'下载链接' if 'download' in play_url else '流媒体链接'}</p>
            <p><strong>播放URL:</strong> <a href="{play_url}" target="_blank">{play_url[:100]}...</a></p>
        </div>
        
        <h3>在线播放测试</h3>
        <video controls preload="metadata">
            <source src="{play_url}" type="video/mp4">
            <source src="{play_url}" type="video/webm">
            <source src="{play_url}" type="video/ogg">
            您的浏览器不支持 HTML5 视频播放。
            <p>请尝试使用现代浏览器，如 Chrome、Firefox 或 Safari。</p>
        </video>
        
        <div class="info">
            <h3>测试说明</h3>
            <ul>
                <li>如果视频能正常播放，说明链接可用于网站集成</li>
                <li>如果提示下载，说明需要处理 CORS 或使用代理</li>
                <li>如果无法播放，可能需要用户登录验证</li>
            </ul>
        </div>
        
        <h3>备用测试链接</h3>
        <p><a href="{play_url}" target="_blank">直接访问播放链接</a></p>
    </div>
</body>
</html>
"""

                            test_file = f"pikpak_video_test_{video['id'][:8]}.html"
                            with open(test_file, "w", encoding="utf-8") as f:
                                f.write(html_content)

                            print(f"✅ 已生成测试文件: {test_file}")
                            print("🌐 正在打开测试文件...")
                            webbrowser.open(f"file://{os.path.abspath(test_file)}")

                    except:
                        pass
        else:
            print("\n❌ 云盘中未找到视频文件")
            print("💡 提示: 如果刚才添加了下载任务，请等待下载完成后再次运行程序")

        print("\n" + "=" * 60)
        print("✨ 完整流程测试完成")


async def main():
    print("请输入你的 PikPak 账号信息:")
    username = input("用户名 (邮箱或手机号): ").strip()
    password = input("密码: ").strip()

    if not username or not password:
        print("❌ 用户名和密码不能为空")
        return

    print("\n选择测试模式:")
    print("1. 只查看现有文件和播放链接 (推荐)")
    print("2. 下载新的动漫到PikPak + 查看播放链接")

    choice = input("请选择 (1 或 2): ").strip()
    should_download = choice == "2"

    if should_download:
        confirm = input("⚠️  确定要下载吗？这会消耗你的下载次数 (y/n): ").strip().lower()
        should_download = confirm == "y"

    # 创建自动化流水线
    pipeline = CompleteAnimeAutoPipeline(username, password)

    # 运行完整流程
    await pipeline.complete_workflow(should_download)


if __name__ == "__main__":
    asyncio.run(main())
