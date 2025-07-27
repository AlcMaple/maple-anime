import httpx
import json
from typing import Dict, List, Any, Optional
from datetime import datetime

from exceptions import NotFoundException, SystemException, DatabaseException


class BangumiApi:
    """Bangumi API"""

    def __init__(self):
        self.base_url = "https://api.bgm.tv"
        self.client = httpx.AsyncClient(timeout=30.0)
        # 当季新番数据库
        self.news_data = "data/news.json"

    async def get_calendar(self) -> Dict[str, Any]:
        """
        获取番剧每日放送表

        Returns:
            包含番剧每日放送表的字典
        """
        url = f"{self.base_url}/calendar"
        try:
            response = await self.client.get(url)
            response.raise_for_status()

            data = response.json()
            print(f" 成功获取番剧每日放送表，共 {len(data)} 天")

            # 保存数据
            self.save_calendar_data(data)

            return {
                "data": data,
                "last_update": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "success": True,
            }

        except Exception as e:
            print(f" 番剧每日放送表获取失败：{e}")
            return {"data": [], "last_update": "", "success": False}

    def save_calendar_data(self, data: Dict[str, Any]) -> bool:
        """保存番剧每日放送表数据"""
        try:
            # 重新写入数据
            with open(self.news_data, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=4)

            print(f" 成功保存番剧每日放送表数据")
            return True

        except Exception as e:
            print(f" 番剧每日放送表数据保存失败：{e}")
            return False

    async def load_calendar_data(self) -> Optional[List[Dict[str, Any]]]:
        """加载番剧每日放送表数据"""
        try:
            with open(self.news_data, "r", encoding="utf-8") as f:
                data = json.load(f)

            # 统计总的番剧数量
            total_items = sum(
                len(day.get("items", [])) for day in data if isinstance(day, dict)
            )

            print(
                f" 成功加载番剧每日放送表数据，共 {len(data)} 天，{total_items} 部番剧"
            )
            return {"data": data, "success": True}

        except Exception as e:
            print(f" 番剧每日放送表数据加载失败：{e}")
            return {"data": [], "success": False}

    async def get_subject_detail(self, subject_id: int) -> Dict[str, Any]:
        """
        获取动漫详情

        Args:
            subject_id: 动漫ID

        Returns:
            包含动漫详细信息的字典
        """
        url = f"{self.base_url}/v0/subjects/{subject_id}"

        try:
            response = await self.client.get(url)
            response.raise_for_status()

            data = response.json()
            print(f"✅ 成功获取动漫详情: {data.get('name', 'Unknown')}")

            return {"data": data, "success": True, "message": "获取动漫详情成功"}

        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                print(f"❌ 动漫不存在: {subject_id}")
                return {
                    "data": {},
                    "success": False,
                    "message": f"动漫 {subject_id} 不存在",
                }
            else:
                print(f"❌ 获取动漫详情失败: HTTP {e.response.status_code}")
                return {
                    "data": {},
                    "success": False,
                    "message": f"HTTP错误: {e.response.status_code}",
                }
        except Exception as e:
            print(f"❌ 获取动漫详情异常: {e}")
            return {"data": {}, "success": False, "message": f"获取失败: {str(e)}"}

    async def search_subjects(
        self,
        keyword: str,
        type: int = 2,  # 2 表示动画
        limit: int = 10,
        offset: int = 0,
    ) -> Dict[str, Any]:
        """
        搜索动漫

        Args:
            keyword: 搜索关键词
            type: 条目类型 (1=书籍, 2=动画, 3=音乐, 4=游戏, 6=三次元)
            limit: 返回数量限制
            offset: 偏移量

        Returns:
            包含搜索结果的字典
        """
        url = f"{self.base_url}/v0/search/subjects"

        # 查询参数
        params = {"limit": limit, "offset": offset}

        # 请求体
        payload = {
            "keyword": keyword,
            "sort": "rank",  # 按排名排序
            "filter": {"type": [type]},  # 数组格式
        }

        headers = {"Content-Type": "application/json"}

        try:
            response = await self.client.post(
                url, params=params, json=payload, headers=headers
            )
            response.raise_for_status()

            data = response.json()
            total = data.get("total", 0)
            results = data.get("data", [])

            print(f"✅ 搜索成功: '{keyword}' 找到 {total} 个结果")

            return {
                "data": results,
                "total": total,
                "keyword": keyword,
                "success": True,
                "message": f"找到 {total} 个相关结果",
            }

        except Exception as e:
            print(f"❌ 搜索失败: {e}")
            return {
                "data": [],
                "total": 0,
                "keyword": keyword,
                "success": False,
                "message": f"搜索失败: {str(e)}",
            }

    async def get_anime_info_by_name(self, anime_name: str) -> Dict[str, Any]:
        """
        通过动漫名称获取详细信息

        Args:
            anime_name: 动漫名称，如 "药屋少女的呢喃"

        Returns:
            包含动漫详细信息的字典
        """
        print(f"🔍 正在搜索动漫: {anime_name}")

        # 先搜索获取ID
        search_result = await self.search_subjects(anime_name, limit=5)
        print("=" * 60)
        print("搜索ID结果：", search_result)
        print("=" * 60)

        if not search_result["success"] or not search_result["data"]:
            return {
                "data": {},
                "success": False,
                "message": f"未找到动漫: {anime_name}",
            }

        # 取第一个最匹配的结果
        first_result = search_result["data"][0]
        subject_id = first_result["id"]

        print(
            f"📺 找到匹配项: {first_result.get('name', 'Unknown')} (ID: {subject_id})"
        )

        # 获取详细信息
        detail_result = await self.get_subject_detail(subject_id)
        print("=" * 60)
        print("获取动漫详情成功：", detail_result)
        print("=" * 60)

        if detail_result["success"]:
            # 合并搜索结果和详细信息
            return {
                "data": detail_result["data"],
                "search_info": {
                    "total_found": search_result["total"],
                    "search_keyword": anime_name,
                },
                "success": True,
                "message": f"成功获取 {anime_name} 的详细信息",
            }
        else:
            return detail_result

    async def search_anime_by_title(
        self, title: str, max_results: int = 50
    ) -> Dict[str, Any]:
        """
        根据标题搜索动漫，返回所有包含该标题的结果

        Args:
            title: 动漫标题关键词
            max_results: 最大返回结果数

        Returns:
            包含所有匹配结果的字典
        """
        print(f" 搜索包含 '{title}' 的所有动漫...")

        all_results = []
        offset = 0
        limit = 25  # 每次请求的数量

        try:
            while len(all_results) < max_results:
                # 搜索动漫
                search_result = await self.search_subjects(
                    keyword=title, type=2, limit=limit, offset=offset  # 动画类型
                )

                if not search_result["success"] or not search_result["data"]:
                    break

                current_results = search_result["data"]

                # 只保留标题中包含搜索关键词的动漫
                filtered_results = []
                for anime in current_results:
                    anime_name = anime.get("name", "")
                    anime_name_cn = anime.get("name_cn", "")

                    # 检查中文名或日文名是否包含关键词
                    if (
                        title.lower() in anime_name.lower()
                        or title.lower() in anime_name_cn.lower()
                        or title in anime_name
                        or title in anime_name_cn
                    ):

                        filtered_results.append(
                            {
                                "id": anime.get("id"),
                                "name": anime_name,
                                "name_cn": anime_name_cn,
                                "summary": anime.get("summary", ""),
                                "images": anime.get("images", {}),
                                "air_date": anime.get("air_date", ""),
                                "eps_count": anime.get("eps_count", 0),
                                "rating": anime.get("rating", {}),
                                "tags": anime.get("tags", []),
                            }
                        )

                all_results.extend(filtered_results)
                print(
                    f" 第{offset//limit + 1}页: 获取{len(current_results)}个，过滤后{len(filtered_results)}个"
                )

                # 没有更多数据了
                if len(current_results) < limit:
                    break

                offset += limit

                # 防止无限循环
                if offset > 200:  # 最多搜索8页
                    break

            # 限制最终结果数量
            if len(all_results) > max_results:
                all_results = all_results[:max_results]

            print(f" 搜索完成: 找到 {len(all_results)} 个包含 '{title}' 的动漫")

            return all_results

        except Exception as e:
            raise SystemException(message="搜索 banguni 动漫信息失败", original_error=e)
