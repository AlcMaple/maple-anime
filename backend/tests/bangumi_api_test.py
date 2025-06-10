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

    async def run_all_tests(self):
        print("=" * 60)
        print("开始测试BangumiApi")
        print("=" * 60)
        # data = await self.test_get_calendar()
        # if data and data.get("data"):
        #     r = await self.test_save_calendar_data(data["data"])

        await self.test_load_calendar_data()
        print("=" * 60)
        print("BangumiApi测试结束")
        print("=" * 60)


async def main():
    test = BangumiApiTest()
    await test.run_all_tests()


if __name__ == "__main__":
    asyncio.run(main())
