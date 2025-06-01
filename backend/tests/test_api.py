"""
AnimeGarden API 测试：获取动漫资源数据
"""

import httpx
import json
from typing import Dict, List, Any


class AnimeGardenAPI:
    def __init__(self):
        self.base_url = "https://api.animes.garden"
        self.client = httpx.Client(timeout=30.0)

    def get_resources(self, page: int = 1, page_size: int = 10) -> Dict[str, Any]:
        """
        获取动漫资源列表
        """
        try:
            url = f"{self.base_url}/resources"
            params = {"page": page, "pageSize": page_size}

            print(f"请求URL: {url}")
            print(f"请求参数: {params}")

            response = self.client.get(url, params=params)
            response.raise_for_status()

            data = response.json()
            print(f"响应状态码: {response.status_code}")
            print(f"响应数据类型: {type(data)}")

            return data

        except httpx.HTTPError as e:
            print(f"HTTP请求错误: {e}")
            return {"error": str(e)}
        except json.JSONDecodeError as e:
            print(f"JSON解析错误: {e}")
            return {"error": "JSON解析失败"}
        except Exception as e:
            print(f"未知错误: {e}")
            return {"error": str(e)}

    def analyze_response(self, data: Dict[str, Any]) -> None:
        """
        分析响应数据结构
        """
        if "error" in data:
            print(f"❌ 获取数据失败: {data['error']}")
            return

        print("✅ 数据获取成功")
        print("\n=== 数据结构分析 ===")

        # 显示顶层键
        print(f"顶层键: {list(data.keys())}")

        # 如果有resources字段，分析第一个资源
        if "resources" in data and len(data["resources"]) > 0:
            first_resource = data["resources"][0]
            print(f"\n第一个资源的字段: {list(first_resource.keys())}")
            print(f"\n第一个资源详情:")
            for key, value in first_resource.items():
                print(f"  {key}: {value}")

        # 如果有data字段，分析第一个数据
        elif "data" in data and len(data["data"]) > 0:
            first_item = data["data"][0]
            print(f"\n第一个数据项的字段: {list(first_item.keys())}")
            print(f"\n第一个数据项详情:")
            for key, value in first_item.items():
                print(f"  {key}: {value}")

        # 显示完整数据（限制长度）
        print(f"\n=== 完整响应数据 ===")
        print(
            json.dumps(data, ensure_ascii=False, indent=2)[:2000] + "..."
            if len(str(data)) > 2000
            else json.dumps(data, ensure_ascii=False, indent=2)
        )


def main():
    print("🌸 AnimeGarden API 测试开始")
    print("=" * 50)

    api = AnimeGardenAPI()

    # 测试获取资源列表
    print("\n📡 正在获取动漫资源列表...")
    data = api.get_resources(page=1, page_size=5)

    # 分析响应数据
    api.analyze_response(data)

    print("\n" + "=" * 50)
    print("✨ 测试完成")


if __name__ == "__main__":
    main()
