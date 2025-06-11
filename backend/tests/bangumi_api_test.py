"""
bangumi api 测试
测试bangumi_api.py文件中的功能
"""

import sys, os
import asyncio
from typing import Dict, List, Any, Optional

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from apis.bangumi_api import BangumiApi


class BangumiApiTest:
    def __init__(self):
        self.bangumi = BangumiApi()

    async def test_get_calendar(self) -> Dict[str, Any]:
        calendar = await self.bangumi.get_calendar()
        # print("test_get_calendar:", calendar)
        return calendar

    async def test_save_calendar_data(self, data: Dict[str, Any]):
        result = self.bangumi.save_calendar_data(data)
        print("test_save_calendar_data:", result)

    async def test_load_calendar_data(self) -> Optional[Dict[str, Any]]:
        """数据太多，返回的数据将不打印"""
        data = self.bangumi.load_calendar_data()

    async def test_get_subject_detail(self):
        """测试获取动漫详情"""
        print("\n🔍 测试: 获取动漫详情")
        print("=" * 50)

        # 测试莉可丽丝的ID
        test_subject_id = 364450

        result = await self.bangumi.get_subject_detail(test_subject_id)

        if result["success"]:
            data = result["data"]
            print(f"✅ 获取成功:")
            print(f"   ID: {data.get('id', 'Unknown')}")
            print(f"   名称: {data.get('name', 'Unknown')}")
            print(f"   中文名: {data.get('name_cn', 'Unknown')}")
            print(f"   简介: {data.get('summary', 'No summary')[:100]}...")
            print(f"   类型: {data.get('type', 'Unknown')}")
            if "rating" in data and data["rating"]:
                print(f"   评分: {data['rating'].get('score', 'No rating')}")
        else:
            print(f"❌ 获取失败: {result['message']}")

    async def test_search_subjects(self):
        """测试搜索动漫"""
        print("\n🔍 搜索动漫")
        print("=" * 50)

        # 使用不同的搜索词进行测试
        test_keywords = [
            "药屋少女的呢喃",  # 药屋少女
            "小市民系列",  # 小市民系列
            "间谍过家家",  # 间谍过家家
        ]

        for keyword in test_keywords:
            print(f"\n🔎 搜索关键词: '{keyword}'")
            result = await self.bangumi.search_subjects(keyword, limit=3)

            if result["success"]:
                total = result.get("total", 0)
                data = result.get("data", [])
                print(f"✅ 搜索成功，总共找到 {total} 个结果")

                for i, item in enumerate(data, 1):
                    name = item.get("name", "Unknown")
                    name_cn = item.get("name_cn", "")
                    item_id = item.get("id", "Unknown")

                    display_name = name_cn if name_cn else name
                    print(f"   {i}. {display_name} (ID: {item_id})")

                    # 显示评分
                    if "rating" in item and item["rating"]:
                        score = item["rating"].get("score", 0)
                        total_votes = item["rating"].get("total", 0)
                        if score > 0:
                            print(f"      评分: {score}/10 ({total_votes}人评价)")
            else:
                print(f"❌ 搜索失败: {result['message']}")

    async def test_anime_by_name_comprehensive(self):
        """测试通过名称获取动漫详细信息"""
        print("\n🔍 测试3: 通过名称获取详细信息")
        print("=" * 50)

        # 测试多个动漫名称
        test_anime_names = [
            # "药屋少女的呢喃第一季",  # 药屋少女
            # "药屋少女的呢喃第二季",  # 药屋少女
            # "小市民系列",  # 小市民系列
            "莉可丽丝"
        ]

        for anime_name in test_anime_names:
            print(f"\n📺 获取动漫详情: '{anime_name}'")
            result = await self.bangumi.get_anime_info_by_name(anime_name)

            if result["success"]:
                data = result["data"]
                search_info = result.get("search_info", {})

                print(f"✅ 获取成功:")
                print(f"   搜索关键词: {search_info.get('search_keyword', 'Unknown')}")
                print(f"   搜索结果数: {search_info.get('total_found', 0)}")
                print(f"   ID: {data.get('id', 'Unknown')}")
                print(f"   名称: {data.get('name', 'Unknown')}")
                print(f"   中文名: {data.get('name_cn', 'Unknown')}")
                print(f"   简介: {data.get('summary', 'No summary')[:100]}...")

                # 显示简介
                summary = data.get("summary", "")
                if summary:
                    print(f"   简介: {summary[:150]}...")

                # 显示封面
                images = data.get("images", {})
                if images:
                    print(f"   封面URL:")
                    if images.get("large"):
                        print(f"     large: {images['large']}")

                # 显示评分
                rating = data.get("rating", {})
                if rating and rating.get("score"):
                    score = rating.get("score", 0)
                    total = rating.get("total", 0)
                    print(f"   评分: {score}/10 ({total}人评价)")

                # 显示放送日期
                if data.get("date"):
                    print(f"   放送日期: {data['date']}")

            else:
                print(f"❌ 获取失败: {result['message']}")

    async def test_search_anime_by_title(self, title: str) -> Dict[str, Any]:
        """测试通过标题搜索动漫"""
        print("\n🔍 通过标题搜索动漫")
        print("=" * 50)
        # 测试搜索词
        test_title = title
        result = await self.bangumi.search_anime_by_title(test_title)
        if result["success"]:
            data = result["data"]
            print(f"✅ 搜索成功，总共找到 {len(data)} 个结果")
            print("=" * 50)
            print("具体的数据：", data)
            print("=" * 50)
            for i, item in enumerate(data, 1):
                name = item.get("name", "Unknown")
                name_cn = item.get("name_cn", "")
                item_id = item.get("id", "Unknown")
                print(f"   {i}. {name_cn if name_cn else name} (ID: {item_id})")
        else:
            print(f"❌ 搜索失败: {result['message']}")

    async def run_all_tests(self):
        print("=" * 60)
        print("开始测试BangumiApi")
        print("=" * 60)
        # data = await self.test_get_calendar()
        # if data and data.get("data"):
        #     r = await self.test_save_calendar_data(data["data"])

        # await self.test_load_calendar_data()

        # # 获取动漫详情
        # await self.test_get_subject_detail()

        # # 搜索动漫
        # await self.test_search_subjects()

        # # 通过名称获取详细信息
        # await self.test_anime_by_name_comprehensive()

        # 通过标题搜索动漫
        await self.test_search_anime_by_title("药屋少女的呢喃")

        print("=" * 60)
        print("BangumiApi测试结束")
        print("=" * 60)


async def main():
    test = BangumiApiTest()
    await test.run_all_tests()


if __name__ == "__main__":
    asyncio.run(main())
