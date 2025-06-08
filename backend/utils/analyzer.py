import re, os


class Analyzer:
    def __init__(self):
        pass

    def is_include_subtitles(self, title: str) -> bool:
        """判断是否包含字幕"""
        keywords = ["内嵌", "简体", "繁體", "简日双语", "繁日雙語"]
        for k in keywords:
            if k in title:
                return True
        return False

    def is_collection(self, title: str) -> bool:
        """
        判断是否是合集

        Args:
            title (str): 要检测的标题

        Returns:
            bool: 如果是合集返回True，否则返回False
        """

        pattern = r"\d+-\d+"
        return bool(re.search(pattern, title))

    def get_anime_episodes(self, title: str) -> str:
        """
        获取当前动漫的集数并生成简化的文件名 (如: 01.mp4)

        Args:
            title: 原始文件名

        Returns:
            str: 简化的新文件名 (集数.扩展名)，如果无法提取集数则返回原文件名
        """
        # 获取文件扩展名
        name_without_ext, ext = os.path.splitext(title)

        # 提取集数的正则表达式模式（按优先级排序）
        patterns = [
            # 特殊集数类型（最高优先级）
            r"\[(OVA\d*)\]",  # [OVA], [OVA1], [OVA2]
            r"\[剧场版\]",  # [剧场版]
            # 数字集数
            r"\[(\d{1,2})\s*-\s*总第\d+\]",  # [01 - 总第11] - 优先提取前面的集数
            r"第(\d+)[集话]",  # 第11集, 第11话
            r"\[第?(\d+)集?\]",  # [第11集], [11]
            r"[\[\s\-]\s*E(\d+)\s*[\]\s\-]",  # E11, [E11]
            r"[\[\s\-]\s*EP(\d+)\s*[\]\s\-]",  # EP11, [EP11]
            r"[\[\s\-]\s*(\d+)v?\d*\s*[\[\]\s\-]",  # [37], - 37 [, ] 37[, - 37v2 [
            r"[\[\s\-]\s*(\d+)v?\d*\s*$",  # 末尾数字 - 37, -37v2
        ]

        for i, pattern in enumerate(patterns):
            match = re.search(pattern, name_without_ext)
            if match:
                matched_text = match.group(1)

                # 特殊类型，直接返回匹配的文本
                if i < 2:  # OVA 或 剧场版
                    new_filename = f"{matched_text}{ext}"
                    return new_filename
                else:  # 数字集数
                    episode_num = int(matched_text)
                    # 格式化为两位数字 + 扩展名
                    new_filename = f"{episode_num:02d}{ext}"
                    return new_filename

        print(f"❌ 未发现集数信息: {title}")
        return title  # 如果无法提取集数，返回原文件名

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
