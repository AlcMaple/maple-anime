import httpx
import json
import os
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta


class BangumiApi:
    """Bangumi API"""

    def __init__(self):
        self.base_url = "https://api.bgm.tv"
        self.client = httpx.AsyncClient(timeout=30.0)
        # 当季新番数据库
        self.news_data = "data/news.json"

    async def get_calendar(self) -> Dict[str, Any]:
        """获取番剧每日放送表"""
        url = f"{self.base_url}/calendar"
        try:
            response = await self.client.get(url)
            response.raise_for_status()

            data = response.json()
            print(f"✅ 成功获取番剧每日放送表，共 {len(data)} 天")

            # 保存数据
            self.save_calendar_data(data)

            return {
                "data": data,
                "last_update": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            }

        except Exception as e:
            print(f"❌ 番剧每日放送表获取失败：{e}")
            return {"data": [], "last_update": ""}

    def save_calendar_data(self, data: Dict[str, Any]) -> bool:
        """保存番剧每日放送表数据"""
        try:
            # 重新写入数据
            with open(self.news_data, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=4)

            print(f"✅ 成功保存番剧每日放送表数据")
            return True

        except Exception as e:
            print(f"❌ 番剧每日放送表数据保存失败：{e}")
            return False

    def load_calendar_data(self) -> Optional[List[Dict[str, Any]]]:
        """加载番剧每日放送表数据"""
        try:
            with open(self.news_data, "r", encoding="utf-8") as f:
                data = json.load(f)

            # 统计总的番剧数量
            total_items = sum(
                len(day.get("items", [])) for day in data if isinstance(day, dict)
            )

            print(
                f"✅ 成功加载番剧每日放送表数据，共 {len(data)} 天，{total_items} 部番剧"
            )
            return data

        except Exception as e:
            print(f"❌ 番剧每日放送表数据加载失败：{e}")
            return None
