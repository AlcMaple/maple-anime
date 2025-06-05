import re


class Analyzer:
    def __init__(self):
        pass

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