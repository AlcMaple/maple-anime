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

        # # 筛选动漫
        # anime_data = self.process_anime_data(result, anime_name)
        # if not anime_data:
        #     print("没有找到符合条件的动漫")
        #     return

        # return anime_data

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
            # print("search_anime result number: ", len(results))
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
        keywords = ["内嵌", "内封", "简体", "繁體", "简日双语", "繁日雙語"]
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

    def filter_low_quality(self, title: str) -> bool:
        """过滤低质量资源"""
        """
            低于 1080p 的资源过滤
            过滤案例：
            1. 480p，720p
            2. 1280X720，800X450
        """
        patterns = [
            r"480p|720p|360p|240p|144p",
            r"800[xX×]450|1280[xX×]720|640[xX×]480",
            r"标清|[Ss][Dd]",  # 标清标识
            r"HDTV.*480|HDTV.*720(?!0)",  # HDTV但非1080
        ]
        for p in patterns:
            if re.search(p, title):
                return True
        return False

    def process_anime_data(self, data: Dict, name: str) -> Dict:
        """筛选动漫"""
        result = []
        episodes = set()
        for d in data:
            title = d.get("title", "")
            if self.filter_low_quality(title) or not self.is_include_subtitles(title):
                continue

            # # 判断是否有季度信息
            # if re.search(r"第\d+季", title):
            #     continue

            # 获取集数
            episode = self.get_anime_episodes(title)
            if episode == -1 or episode > 100:
                continue

            if episode in episodes:
                continue
            episodes.add(episode)
            print(f"✅ 发现: {name} {episode}集")
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


# if __name__ == "__main__":
#     asyncio.run(AnimeSearch().main())
