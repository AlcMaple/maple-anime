import httpx
import json
import re
from typing import Dict, List, Any, Optional, Set
from dataclasses import dataclass
from datetime import datetime
import asyncio


class AnimeSearch:
    """动漫搜索 API"""

    def __init__(self):
        self.base_url = "https://api.animes.garden"
        self.client = httpx.AsyncClient(timeout=30.0)

    async def main(self):
        """主函数"""
        anime_name = input("请输入要搜索的动漫名称：")
        result = await self.search_anime(anime_name)
        if not result:
            print("没有找到相关的动漫")
            return

        # 筛选动漫
        anime_data = self.process_anime_data(result)
        if not anime_data:
            print("没有找到符合条件的动漫")
            return

        return anime_data

    async def search_anime(self, name: str) -> List[Dict]:
        """搜索动漫"""
        try:
            url = f"{self.base_url}/resources"
            query = {"search": [name]}
            print(f"🔍 搜索 {name}...")

            response = await self.client.post(
                url,
                json=query,
                headers={"Content-Type": "application/json"},
            )
            response.raise_for_status()

            data = response.json()
            resources = data.get("resources", [])

            results = []
            for resource in resources:
                row_data = {
                    "id": resource.get("id"),
                    "title": resource.get("title", ""),
                    "magnet": resource.get("magnet", ""),
                }
                results.append(row_data)

            # print("search_anime result: ", results)
            return results

        except Exception as e:
            print(f"❌ 搜索动漫失败: {e}")
            return []

    def get_anime_seasons(self, data: List[Dict], name: str) -> Set[str]:
        """获取动漫季度类型"""
        print(f"🔍 扫描 {name} 的季度信息...")

        seasons = set()
        all_seasons = ["第一季", "第二季", "第三季", "剧场版"]

        for resource in data:
            title = resource.get("title", "")

            # 查找季度
            for season in all_seasons:
                if season in title:
                    seasons.add(season)
                    print(f"✅ 发现: {season}")

                    if len(seasons) >= len(all_seasons):
                        return seasons

        # 只有单季或电影
        if not seasons:
            print(f"📺 未发现季度标识，判定为单季动漫")
            return seasons

        print(f"📋 发现的季度: {', '.join(seasons)}")
        return seasons

    def is_include_subtitles(self, title: str) -> bool:
        """判断是否包含字幕"""
        keywords = ["内嵌", "内封"]
        for k in keywords:
            if k in title:
                return True
        return False

    def get_anime_episodes(self, title: str) -> int:
        """获取当前动漫的集数"""
        patterns = [
            r"[\s\-\]]\s*(\d+)v?\d*\s*[\[\s]",  # - 37 [, ] 37[, - 37v2 [
            r"[\[\s]\s*(\d+)v?\d*\s*[\]\s]",  # [37], [ 37 ]
            r"[\s\-]\s*(\d+)v?\d*\s*$",  # 末尾数字 - 37, -37v2
            r"[\[\]]\s*(\d+)v?\d*\s*[\[\]]",  # [37], ]37[
        ]

        for pattern in patterns:
            match = re.search(pattern, title)
            if match:
                episodes = int(match.group(1))
                return episodes

        print(f"❌ 未发现集数信息")
        return -1

    def process_anime_data(self, data: Dict) -> Dict:
        """筛选动漫"""
        result = []
        episodes = set()
        for d in data:
            title = d.get("title", "")
            if "1080" not in title or not self.is_include_subtitles(title):
                continue

            # 判断是否有季度信息
            if re.search(r"第\d+季", title):
                continue

            # 获取集数
            episode = self.get_anime_episodes(title)
            if episode == -1 or episode > 100:
                continue

            if episode in episodes:
                continue
            episodes.add(episode)
            resource = {
                "id": d.get("id"),
                "title": d.get("title", ""),
                "magnet": d.get("magnet", ""),
                "episodes": episode,
            }
            result.append(resource)

        # 按集数排序
        result = sorted(result, key=lambda x: x["episodes"])

        print("process_anime_data result: ", result)

        return result


if __name__ == "__main__":
    asyncio.run(AnimeSearch().main())
