"""
备份数据 & 调整数据结构
"""

import sys
import os
import json
from datetime import datetime
import shutil

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.pikpak import PikPakDatabase


def upgrade_anime_database():
    """调整 anime.json 数据结构"""
    print("🔧 开始调整 anime.json 数据结构")
    print("=" * 40)

    db = PikPakDatabase()

    # 加载现有数据
    print("📂 加载现有数据...")
    original_data = db.load_data()

    print(f"✅ 加载完成，共 {len(original_data.get('animes', {}))} 个动漫")

    # 备份文件
    backup_filename = (
        f"data/anime_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    )
    print(f"💾 备份到 {backup_filename}...")
    shutil.copy2("data/anime.json", backup_filename)
    print("✅ 备份完成")

    # 调用调整结构方法
    print("🚀 开始数据结构升级...")
    upgraded_data = db._upgrade_data_structure(original_data)
    print("✅ 数据结构升级完成")

    # 重新写入原文件
    print("💾 写入升级后的数据...")
    db.save_data(upgraded_data)
    print("✅ 写入完成")

    # 验证结果
    print("\n📊 验证升级结果:")
    first_anime_id = list(upgraded_data["animes"].keys())[0]
    first_anime = upgraded_data["animes"][first_anime_id]

    print(f"   动漫数量: {len(upgraded_data['animes'])}")
    print(f"   示例动漫字段: {list(first_anime.keys())}")
    print(f"   summary 字段: {'✅ 已添加' if 'summary' in first_anime else '❌ 缺失'}")
    print(
        f"   cover_url 字段: {'✅ 已添加' if 'cover_url' in first_anime else '❌ 缺失'}"
    )

    print(f"\n🎉 升级完成！")
    print(f"   原始文件已备份到: {backup_filename}")
    print(f"   升级后文件: data/anime.json")


if __name__ == "__main__":
    print("=" * 60)

    if upgrade_anime_database():
        print("✨ 备份数据 & 调整数据结构成功!")

    print("\n" + "=" * 60)
    print("✨ 备份数据 & 调整数据结构完成")
