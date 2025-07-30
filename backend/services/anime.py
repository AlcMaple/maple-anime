import httpx
from typing import Dict, List
from loguru import logger

from exceptions import NotFoundException, SystemException


class AnimeSearch:
    """动漫搜索 API"""

    def __init__(self):
        self.base_url = "https://api.animes.garden"
        self.client = httpx.AsyncClient(timeout=30.0)

    async def search_anime(self, name: str, max_results: int = None) -> List[Dict]:
        """
        搜索动漫

        Args:
            name: 动漫名
            max_results: 最大结果数，默认不限制

        Returns:
            动漫搜索结果列表
        """
        try:
            url = f"{self.base_url}/resources"
            query = {"search": [name]}
            logger.info(f" 搜索 {name}...")

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

                # 检查 HTTP 响应状态码，如果不是 2xx 成功状态，则抛出 HTTPStatusError 异常
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

                logger.debug(f" 第{page}页获取到 {len(resources)} 个结果")

                # 检查是否达到最大结果数限制
                if max_results and len(all_results) >= max_results:
                    all_results = all_results[:max_results]
                    break

                # 如果当前页结果少于页面大小，说明是最后一页
                if len(resources) < page_size:
                    break

                page += 1

            logger.debug(f" 总共获取到 {len(all_results)} 个结果")
            return all_results

        except httpx.HTTPStatusError as e:
            raise SystemException(
                message=f"搜素API请求失败：HTTP {e.response.status_code}",
                original_error=e,
            )
        except httpx.RequestError as e:
            raise SystemException(message="搜索 API 网络请求异常", original_error=e)
        except NotFoundException:
            raise
        except Exception as e:
            raise SystemException(message="搜索动漫时发生未知异常", original_error=e)
