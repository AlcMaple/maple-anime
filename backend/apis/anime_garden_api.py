import httpx
import json
import re
from typing import Dict, List, Any, Optional, Set
from dataclasses import dataclass
from datetime import datetime
import asyncio

# import sys
# import os

# sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.analyzer import Analyzer


class AnimeSearch:
    """动漫搜索 API"""

    def __init__(self):
        self.base_url = "https://api.animes.garden"
        self.client = httpx.AsyncClient(timeout=30.0)
        self.analyzer = Analyzer()

    async def main(self):
        """主函数"""
        anime_name = input("请输入要搜索的动漫名称：")
        result = await self.search_anime(anime_name)
        if not result:
            print("没有找到相关的动漫")
            return

    async def search_anime(self, name: str, max_results: int = None) -> List[Dict]:
        """搜索动漫"""
        try:
            url = f"{self.base_url}/resources"
            query = {"search": [name]}
            print(f"🔍 搜索 {name}...")

            all_results = []
            page = 1
            page_size = 100

            while True:
                params = {"page": page, "pageSize": page_size}

                response = await self.client.post(
                    url,
                    json=query,
                    params=params,
                    headers={"Content-Type": "application/json"},
                )
                response.raise_for_status()

                data = response.json()
                resources = data.get("resources", [])

                if not resources:
                    break  # 没有更多数据了

                # 处理当前页数据
                for resource in resources:
                    row_data = {
                        "id": resource.get("id"),
                        "title": resource.get("title", ""),
                        "magnet": resource.get("magnet", ""),
                    }
                    all_results.append(row_data)

                print(f"📄 第{page}页获取到 {len(resources)} 个结果")

                # 检查是否达到最大结果数限制
                if max_results and len(all_results) >= max_results:
                    all_results = all_results[:max_results]
                    break

                # 如果当前页结果少于页面大小，说明是最后一页
                if len(resources) < page_size:
                    break

                page += 1

            print(f"✅ 总共获取到 {len(all_results)} 个结果")
            return all_results

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

    def process_anime_data(self, data: Dict, name: str) -> Dict:
        """筛选动漫"""
        result = []
        episodes = set()
        for d in data:
            title = d.get("title", "")
            if self.analyzer.filter_low_quality(
                title
            ) or not self.analyzer.is_include_subtitles(title):
                continue

            # # 判断是否有季度信息
            # if re.search(r"第\d+季", title):
            #     continue

            # 获取集数
            episode = self.analyzer.get_anime_episodes(title)
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
