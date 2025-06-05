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
        # print("请输入你的 PikPak 账号信息:")
        # self.username = input("用户名 (邮箱或手机号): ").strip()
        # self.password = input("密码: ").strip()

        if not self.username or not self.password:
            print("❌ 用户名和密码不能为空")
            return False
        return True

    async def test_get_client(self):
        """测试获取客户端"""
        print("\n🔍 测试1: 获取PikPak客户端")
        try:
            client = await self.service.get_client(self.username, self.password)
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

    async def test_batch_download(self):
        """测试批量下载功能"""
        print("\n🔍 测试4: 批量下载动漫")

        # 模拟动漫数据
        test_anime_list = [
            {
                "id": 714354,
                "title": "【喵萌奶茶屋】★01月新番★[药师少女的独语 / 药屋少女的呢喃 / Kusuriya no Hitorigoto][25][1080p][简日双语]",
                "magnet": "magnet:?xt=urn:btih:EYZEWWJCBRDB2YZN22K72Z2EMSTJG6GZ",
            },
            {
                "id": 715666,
                "title": "[北宇治字幕组] 药屋少女的呢喃 / 药屋少女的独语 / Kusuriya no Hitorigoto [26][WebRip][HEVC_AAC][简日内嵌]",
                "magnet": "magnet:?xt=urn:btih:ab182c11ecc856744c9a7e501e6a8391222b6a6e",
            },
            {
                "id": 720101,
                "title": "【喵萌奶茶屋】★01月新番★[药师少女的独语 / 药屋少女的呢喃 / Kusuriya no Hitorigoto][27][1080p][简日双语]",
                "magnet": "magnet:?xt=urn:btih:SUKBWWDST5LV6YVFJYM777HWSZLLKGJE",
            },
        ]

        try:
            result = await self.service.batch_download_anime(
                self.username, self.password, test_anime_list
            )

            print(f"批量下载结果:")
            print(f"  成功: {result.get('success')}")
            print(f"  消息: {result.get('message')}")

            if result.get("success") and "summary" in result:
                summary = result["summary"]
                print(f"  统计信息:")
                print(f"    总动漫数: {summary.get('total_anime')}")
                print(f"    成功动漫数: {summary.get('successful_anime')}")
                print(f"    总集数: {summary.get('total_episodes')}")
                print(f"    成功集数: {summary.get('successful_episodes')}")

                if "details" in result:
                    print(f"  详细信息:")
                    for detail in result["details"]:
                        print(
                            f"    - {detail.get('anime_title')}: {detail.get('success')}"
                        )

            return result
        except Exception as e:
            print(f"❌ 批量下载异常: {e}")
            return None

    async def test_analyzer_functions(self):
        """测试分析器功能"""
        print("\n🔍 测试5: 分析器功能")

        test_titles = [
            "【喵萌奶茶屋】★01月新番★[药师少女的独语 / 药屋少女的呢喃 / Kusuriya no Hitorigoto][25][1080p][简日双语]",
            "[北宇治字幕组] 药屋少女的呢喃 / 药屋少女的独语 / Kusuriya no Hitorigoto [26][WebRip][HEVC_AAC][简日内嵌]",
            "【喵萌奶茶屋】★01月新番★[药师少女的独语 / 药屋少女的呢喃 / Kusuriya no Hitorigoto][27][1080p][简日双语]",
            "[NAOKI-Raws] sola BD-BOX 1-13+SP (BDRip x264 DTS-HDMA Chap)（2007年）",
            "[Moozzi2] Sola 1-13+EX+SP BD-BOX (BD 1920x1080 x.264 FLACx2)（2007年）",
        ]

        for title in test_titles:
            print(f"\n分析标题: {title}")

            # 测试集数提取
            episode = self.service.analyzer.get_anime_episodes(title)
            print(f"  集数: {episode}")

    async def run_all_tests(self):
        """运行测试"""
        print("🚀 开始 PikPak API 测试")
        print("=" * 60)

        # # 获取pikpak 配置（已完成测试）
        # if not self.get_credentials():
        #     return

        # # 测试1: 获取客户端（已完成测试）
        # client = await self.test_get_client()
        # if not client:
        #     print("❌ 客户端测试失败，停止后续测试")
        #     return

        # # 测试2: 创建文件夹（已完成测试）
        # folder_id = await self.test_create_folder(client)

        # # 测试3: 下载到文件夹（如果文件夹创建成功）（已完成测试）
        # print("文件夹 id：", folder_id)
        # if folder_id:
        #     await self.test_download_to_folder(client, folder_id)

        # 测试5: 分析器功能
        await self.test_analyzer_functions()

        print("\n" + "=" * 60)
        print("✨ 所有测试完成")


async def main():
    """主函数"""
    tester = PikPakApiTester()
    await tester.run_all_tests()


if __name__ == "__main__":
    asyncio.run(main())
