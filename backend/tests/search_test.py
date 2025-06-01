#!/usr/bin/env python3
"""
正确的 AnimeGarden 搜索测试
基于官方API文档的POST搜索方法
"""

import httpx
import json
import asyncio
from typing import Dict, List, Any, Optional


class CorrectAnimeGardenSearch:
    def __init__(self):
        self.base_url = "https://api.animes.garden"
        self.client = httpx.AsyncClient(timeout=30.0)

    async def search_anime(self, anime_name: str = "药屋少女") -> Dict[str, Any]:
        """搜索指定动漫的所有相关资源"""
        print(f"🔍 搜索动漫: {anime_name}")
        print("=" * 60)

        search_methods = [
            {
                "name": "include 搜索",
                "payload": {"include": [anime_name]},
                "description": "包含关键词搜索",
            },
            {
                "name": "search 全文搜索",
                "payload": {"search": [anime_name]},
                "description": "全文索引搜索",
            },
            {
                "name": "动画类型 + include",
                "payload": {"include": [anime_name]},
                "params": {"type": "動畫"},
                "description": "限定动画类型的包含搜索",
            },
            {
                "name": "动画类型 + search",
                "payload": {"search": [anime_name]},
                "params": {"type": "動畫"},
                "description": "限定动画类型的全文搜索",
            },
            {
                "name": "多关键词搜索",
                "payload": {"include": [anime_name, "药师"], "keywords": ["1080"]},
                "params": {"type": "動畫"},
                "description": "多关键词组合搜索",
            },
        ]

        all_results = {}

        for method in search_methods:
            print(f"\n🧪 测试: {method['name']}")
            print(f"   描述: {method['description']}")

            try:
                # 准备请求
                url = f"{self.base_url}/resources"
                params = method.get("params", {})
                headers = {"Content-Type": "application/json"}

                print(f"   URL: {url}")
                print(f"   参数: {params}")
                print(f"   请求体: {method['payload']}")

                # 发送POST请求
                response = await self.client.post(
                    url, params=params, json=method["payload"], headers=headers
                )

                print(f"   状态码: {response.status_code}")

                if response.status_code == 200:
                    data = response.json()
                    resources = data.get("resources", [])

                    print(f"   ✅ 找到 {len(resources)} 个结果")

                    # 分析匹配度
                    exact_matches = []
                    partial_matches = []

                    for resource in resources:
                        title = resource.get("title", "")
                        if anime_name in title:
                            exact_matches.append(resource)
                        elif any(char in title for char in anime_name):
                            partial_matches.append(resource)

                    print(f"   📊 精确匹配: {len(exact_matches)} 个")
                    print(f"   📊 部分匹配: {len(partial_matches)} 个")

                    # 显示匹配结果
                    if exact_matches:
                        print(f"   🎯 精确匹配结果:")
                        for i, resource in enumerate(exact_matches[:3]):
                            title = resource.get("title", "")
                            size_mb = resource.get("size", 0) / 1024 / 1024
                            fansub = resource.get("fansub", {}).get("name", "未知")
                            print(f"      {i+1}. {title[:70]}...")
                            print(f"         大小: {size_mb:.1f}MB | 字幕组: {fansub}")

                    # 保存结果
                    all_results[method["name"]] = {
                        "total": len(resources),
                        "exact_matches": exact_matches,
                        "partial_matches": partial_matches,
                        "method": method,
                    }

                else:
                    print(f"   ❌ 请求失败: {response.status_code}")
                    if response.text:
                        print(f"   错误信息: {response.text[:200]}")

            except Exception as e:
                print(f"   ❌ 异常: {e}")

        return all_results

    async def get_detailed_anime_info(
        self, search_results: Dict[str, Any], anime_name: str
    ):
        """获取动漫的详细信息"""
        print(f"\n" + "=" * 60)
        print(f"📋 {anime_name} 详细信息汇总")
        print("=" * 60)

        # 找到最佳搜索结果
        best_method = None
        max_matches = 0

        for method_name, result in search_results.items():
            exact_count = len(result["exact_matches"])
            if exact_count > max_matches:
                max_matches = exact_count
                best_method = result

        if not best_method or max_matches == 0:
            print("❌ 没有找到相关动漫资源")
            return []

        print(f"✅ 使用最佳搜索方法，找到 {max_matches} 个相关资源")

        anime_resources = []
        for i, resource in enumerate(best_method["exact_matches"]):
            print(f"\n📺 资源 {i+1}:")
            print(f"   标题: {resource.get('title', '')}")
            print(f"   类型: {resource.get('type', '')}")
            print(f"   大小: {resource.get('size', 0) / 1024 / 1024:.1f} MB")
            print(f"   发布时间: {resource.get('createdAt', '')}")
            print(f"   字幕组: {resource.get('fansub', {}).get('name', '未知')}")
            print(f"   发布者: {resource.get('publisher', {}).get('name', '未知')}")
            print(f"   磁力链接: {resource.get('magnet', '')}")
            print(f"   详情链接: {resource.get('href', '')}")

            anime_resources.append(resource)

        return anime_resources

    async def close(self):
        """关闭客户端"""
        await self.client.aclose()


async def main():
    search_client = CorrectAnimeGardenSearch()

    try:
        print("🌸 AnimeGarden 正确搜索测试")
        print("=" * 60)

        # 获取用户输入
        anime_name = input("请输入要搜索的动漫名称 (默认: 药屋少女): ").strip()
        if not anime_name:
            anime_name = "药屋少女"

        # 执行搜索
        search_results = await search_client.search_anime(anime_name)

        # 获取详细信息
        anime_resources = await search_client.get_detailed_anime_info(
            search_results, anime_name
        )

        # 总结
        print(f"\n" + "=" * 60)
        print("🎉 搜索完成!")
        print(f"总共找到 {len(anime_resources)} 个 {anime_name} 相关资源")

        if anime_resources:
            print("\n💡 接下来可以:")
            print("1. 复制磁力链接到 PikPak 下载")
            print("2. 集成到网站的前端搜索功能")
            print("3. 实现自动下载到 PikPak 的功能")

            # 询问是否要测试下载
            test_download = (
                input("\n是否要测试将第一个资源下载到 PikPak? (y/n): ").strip().lower()
            )
            if test_download == "y":
                print("🔄 准备集成 PikPak 下载测试...")
                # 这里可以调用之前的 PikPak 下载功能

    finally:
        await search_client.close()


if __name__ == "__main__":
    asyncio.run(main())
