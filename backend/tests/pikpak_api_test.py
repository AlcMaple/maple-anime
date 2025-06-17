"""
PikPak API 测试
测试 pikpak_api.py 中的各个功能
"""

import asyncio
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from apis.pikpak_api import PikPakService


class PikPakApiTester:
    def __init__(self):
        self.service = PikPakService()
        self.username = "hgg13536593830@gmail.com"
        self.password = "123456789ABc"

    def get_credentials(self):
        """获取 pikpak 配置"""
        print("=== PikPak API 测试 ===")
        print("请输入你的 PikPak 账号信息:")
        self.username = input("用户名 (邮箱或手机号): ").strip()
        self.password = input("密码: ").strip()

        if not self.username or not self.password:
            print("❌ 用户名和密码不能为空")
            return False
        return True

    async def test_get_client(self):
        """测试获取客户端"""
        print("\n🔍 测试1: 获取PikPak客户端")
        try:
            client = await self.service.get_client(self.username, self.password)
            print(f"🔑 客户端: {client}")

            # 查看客户端属性
            print(f"🔍 客户端属性:")
            if hasattr(client, "access_token"):
                print(f"  access_token: {client.access_token}")
            if hasattr(client, "token"):
                print(f"  token: {client.token}")
            if hasattr(client, "session_token"):
                print(f"  session_token: {client.session_token}")

            # 查看所有非私有属性
            print(
                f"🔍 所有属性: {[attr for attr in dir(client) if not attr.startswith('_')]}"
            )

            print("✅ 客户端获取成功")
            return client
        except Exception as e:
            print(f"❌ 客户端获取失败: {e}")
            return None

    async def test_create_folder(self, client):
        """测试创建文件夹"""
        print("\n🔍 测试2: 创建动漫文件夹")
        test_folder_name = "药屋少女的呢喃 第二季"

        folder_id = await self.service.create_anime_folder(client, test_folder_name)

        return folder_id

    async def test_download_to_folder(self, client, folder_id):
        """测试下载到文件夹"""
        print("\n🔍 测试3: 下载到指定文件夹")

        test_magnet = "magnet:?xt=urn:btih:CZLV5SFHPB2C3WWS3KMVHV6FMAPEU26H&dn=&tr=http%3A%2F%2F104.143.10.186%3A8000%2Fannounce&tr=udp%3A%2F%2F104.143.10.186%3A8000%2Fannounce&tr=http%3A%2F%2Ftracker.openbittorrent.com%3A80%2Fannounce&tr=http%3A%2F%2Ftracker3.itzmx.com%3A6961%2Fannounce&tr=http%3A%2F%2Ftracker4.itzmx.com%3A2710%2Fannounce&tr=http%3A%2F%2Ftracker.publicbt.com%3A80%2Fannounce&tr=http%3A%2F%2Ftracker.prq.to%2Fannounce&tr=http%3A%2F%2Fopen.acgtracker.com%3A1096%2Fannounce&tr=https%3A%2F%2Ft-115.rhcloud.com%2Fonly_for_ylbud&tr=http%3A%2F%2Ftracker1.itzmx.com%3A8080%2Fannounce&tr=http%3A%2F%2Ftracker2.itzmx.com%3A6961%2Fannounce&tr=udp%3A%2F%2Ftracker1.itzmx.com%3A8080%2Fannounce&tr=udp%3A%2F%2Ftracker2.itzmx.com%3A6961%2Fannounce&tr=udp%3A%2F%2Ftracker3.itzmx.com%3A6961%2Fannounce&tr=udp%3A%2F%2Ftracker4.itzmx.com%3A2710%2Fannounce&tr=http%3A%2F%2Ftr.bangumi.moe%3A6969%2Fannounce&tr=http%3A%2F%2Ft.nyaatracker.com%2Fannounce&tr=http%3A%2F%2Fopen.nyaatorrents.info%3A6544%2Fannounce&tr=http%3A%2F%2Ft2.popgo.org%3A7456%2Fannonce&tr=http%3A%2F%2Fshare.camoe.cn%3A8080%2Fannounce&tr=http%3A%2F%2Fopentracker.acgnx.se%2Fannounce&tr=http%3A%2F%2Ftracker.acgnx.se%2Fannounce&tr=http%3A%2F%2Fnyaa.tracker.wf%3A7777%2Fannounce&tr=http%3A%2F%2Fopen.acgnxtracker.com%3A80%2Fannounce"
        test_title = "[漫猫字幕社&猫恋汉化组][10月新番][药屋少女的呢喃][Kusuriya no Hitorigoto][01-24][1080P][MP4][GB&JP][简日双语]"

        try:
            result = await self.service.download_to_folder(
                client, test_magnet, folder_id, test_title
            )

            print(f"下载结果: {result}")
            if result.get("success"):
                print("✅ 下载任务添加成功")
            else:
                print(f"❌ 下载任务添加失败: {result.get('message')}")

            return result
        except Exception as e:
            print(f"❌ 下载任务异常: {e}")
            return None

    async def test_analyzer_functions(self):
        """测试分析器功能"""
        print("\n🔍 测试5: 分析器功能")

        test_titles = [
            "[晚街与灯][小市民系列 第二季_Shoushimin Series S02][01 - 总第11][WebRip][1080P_AVC_AAC][简日双语内嵌字幕][V2].mp4",
            "[DBD&HKG&X2字幕组][寒蝉鸣泣之时][OVA][猫杀篇][1080P][BDRip][HEVC-10bit][繁体][BIG5][FLAC].mkv",
        ]

        for title in test_titles:
            print(f"\n分析标题: {title}")

            # 测试集数提取
            episode = self.service.analyzer.get_anime_episodes(title)
            print(f"  集数: {episode}")

        # tests_titles = [
        #     "[DBD&HKG&X2字幕组][寒蝉鸣泣之时/Higurashi no Naku Koro ni/ひぐらしのなく顷に][01-26全集+OVA][1080P][BDRip][HEVC-10bit][简体][GB][FLAC][MKV]"
        # ]

        # for title in tests_titles:
        #     print(f"\n分析标题: {title}")

        #     # 测试合集判断
        #     is_anime_collection = self.service.analyzer.is_collection(title)
        #     print(f"  是否是合集: {is_anime_collection}")

    async def test_get_folder_list(self, client):
        """测试获取文件夹列表"""
        result = await self.service.get_folder_list(client)
        print(f"📂 所有文件夹: {result}")

    async def test_get_mypack_folder_list(self, client):
        """测试获取我的My Pack文件夹列表"""
        result = await self.service.get_mypack_folder_list(client)
        print(f"📂 我的My Pack文件夹: {result}")

    async def test_batch_rename_file(self, client, folder_id):
        """测试批量重命名文件"""
        result = await self.service.batch_rename_file(client, folder_id)

        print(f"批量重命名结果: {result['message']}")
        print(f"成功重命名文件数量: {len(result['renamed_files'])}")
        print(f"失败文件数量: {len(result['failed_files'])}")

        # 有失败，提供更详细的信息
        if result["failed_files"]:
            print("失败的文件:")
            for failed_file in result["failed_files"]:
                print(f"  - {failed_file.get('name', 'Unknown')}")

    async def test_batch_download_collection(self, client):
        """测试批量下载合集功能"""
        print("\n🔍 测试4: 批量下载合集")
        print("=" * 50)

        # 测试数据
        anime_list = [
            {
                "id": 177243,
                "magnet": "magnet:?xt=urn:btih:EPZ7JNZHZYKS3S2ILCDDJH2SUTB6K77T",
                "title": "【华盟字幕社＆元古I.G部落】[寒蝉鸣泣之时_礼][Higurashi no Naku Koro ni Rei][OVA][BDRip][1080p][BD全五卷1-5话]",
            }
        ]

        target_folder_name = "寒蝉鸣泣之时第三季"

        print(f"📦 测试动漫合集数量: {len(anime_list)}")
        print(f"📁 目标文件夹名称: {target_folder_name}")
        print(f"🧲 磁力链接: {anime_list[0]['magnet'][:50]}...")
        print(f"📝 动漫标题: {anime_list[0]['title']}")
        print()

        print("\n🚀 开始下载合集...")

        try:
            # 调用批量下载合集方法
            result = await self.service.batch_download_collection(
                client, anime_list, target_folder_name
            )

            print("\n" + "=" * 50)
            print("📊 下载合集结果:")
            print("=" * 50)

            if result.get("success"):
                print("✅ 合集下载任务创建成功!")
                print(f"📄 返回消息: {result.get('message')}")
                print(f"📝 任务ID列表: {result.get('task_id_list')}")
                print(f"📁 重命名文件夹数量: {len(result.get('renamed_folders', []))}")

                # 显示重命名的文件夹详情
                if result.get("renamed_folders"):
                    print("\n📂 重命名文件夹详情:")
                    for i, folder in enumerate(result["renamed_folders"], 1):
                        print(f"  {i}. 原名称: {folder['old_name']}")
                        print(f"     新名称: {folder['new_name']}")
                        print(f"     文件夹ID: {folder['folder_id']}")
                        print()

                print("💡 提示: 文件下载和重命名将在后台进行，请稍等...")
                print("💡 提示: 可以检查你的PikPak网盘查看下载进度")

            else:
                print("❌ 合集下载任务创建失败!")
                print(f"📄 错误消息: {result.get('message')}")

            if result.get("success") and result.get("renamed_folders"):
                print("\n⏳ 等待文件重命名完成...")
                # 等待足够的时间让重命名任务完成
                await asyncio.sleep(10)  # 等待10秒，确保5秒延时任务能完成
                print("✅ 文件重命名任务应该已完成")

            return result

        except Exception as e:
            print(f"❌ 批量下载合集异常: {e}")
            import traceback

            print("详细错误信息:")
            traceback.print_exc()

    async def test_get_folder_files(self, client, folder_id, folder_name):
        """测试获取文件夹内文件列表"""
        print(f"\n🔍 测试: 获取文件夹 '{folder_name}' 内的文件")
        print("=" * 50)

        try:
            result = await self.service.get_folder_files(client, folder_id)

            if result["success"]:
                files = result["files"]
                print(f"✅ 获取成功:")
                print(f"   总文件数: {result['total_files']}")
                print(f"   总项目数: {result['total_items']}")
                print(f"   消息: {result['message']}")

                if files:
                    print(f"\n📋 文件列表:")
                    for i, file in enumerate(files):
                        size_mb = file["size"] / 1024 / 1024
                        video_tag = "🎥" if file["is_video"] else "📄"
                        print(f"  {i+1}. {video_tag} {file['name']}")
                        print(f"      ID: {file['id']}")
                        print(f"      大小: {size_mb:.1f} MB")
                        print(f"      类型: {file['mime_type']}")
                        print(f"      创建时间: {file['created_time']}")
                        print()

                return files
            else:
                print(f"❌ 获取失败: {result['message']}")
                return []

        except Exception as e:
            print(f"❌ 获取文件列表异常: {e}")
            return []

    async def test_delete_file(self, client, file_id):
        """测试删除文件"""
        print(f"\n🔍 测试: 删除文件")
        print("=" * 50)

        try:
            result = await self.service.delete_file(client, file_id)

            if result["success"]:
                print(f"✅ 删除成功: {result['message']}")
                return True
            else:
                print(f"❌ 删除失败: {result['message']}")
                return False

        except Exception as e:
            print(f"❌ 删除文件异常: {e}")
            return False

    async def test_batch_delete_files(self, client, folder_id):
        """测试批量删除文件"""
        print(f"\n🔍 测试: 批量删除文件夹内文件")

        try:
            get_file_list = await self.service.get_folder_files(client, folder_id)
            file_list = get_file_list.get("files")
            if file_list:
                file_ids = [file["id"] for file in file_list]
                result = await self.service.batch_delete_files(client, file_ids)
                if result.get("success"):
                    print(f"✅ 批量删除成功: {result['message']}")
                    return True
                else:
                    print(f"❌ 批量删除失败: {result['message']}")
                    return False
            else:
                print(f"❌ 文件列表为空，无法批量删除")
                return False

        except Exception as e:
            print(f"❌ 批量删除文件异常: {e}")
            return False

    async def run_all_tests(self):
        """运行测试"""
        print("🚀 开始 PikPak API 测试")
        print("=" * 60)

        # # 获取pikpak 配置（已完成测试）
        # if not self.get_credentials():
        #     return

        # 获取客户端（已完成测试）
        client = await self.test_get_client()
        if not client:
            print("❌ 客户端测试失败，停止后续测试")
            return

        # # 创建文件夹（已完成测试）
        # folder_id = await self.test_create_folder(client)

        # # 下载到文件夹（如果文件夹创建成功）（已完成测试）
        # print("文件夹 id：", folder_id)
        # if folder_id:
        #     await self.test_download_to_folder(client, folder_id)

        # # 分析器功能（已完成测试）
        # await self.test_analyzer_functions()

        # # 获取文件夹列表(已完成测试)
        # await self.test_get_folder_list(client)

        # # 批量重命名文件（已完成测试）
        # await self.test_batch_rename_file(client, "VOSDFh8CJSipK9qBIM4ozjvIo2")

        # # 批量下载合集（已完成测试）
        # await self.test_batch_download_collection(client)

        # # 打印 pikpak 的 api 接口
        # print(dir(client))

        # # 测试获取我的My Pack文件夹列表（已完成测试）
        # await self.test_get_mypack_folder_list(client)

        # # 测试获取某个文件夹的文件列表（已完成测试）
        # await self.test_get_folder_files(
        #     client, "VORyss1UmO8p4Iaf_-KanWjgo2", "药屋少女的呢喃 第二季"
        # )

        # # 测试删除文件（已完成测试）
        # await self.test_delete_file(client, "VORyssARClER6__PnjX432lfo2")

        # # 测试批量删除文件（已完成测试）
        # await self.test_batch_delete_files(client, "VORyss1UmO8p4Iaf_-KanWjgo2")

        print("\n" + "=" * 60)
        print("✨ 所有测试完成")


async def main():
    """主函数"""
    tester = PikPakApiTester()
    await tester.run_all_tests()


if __name__ == "__main__":
    asyncio.run(main())
