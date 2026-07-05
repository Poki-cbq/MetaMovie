import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    """Flask 应用配置"""
    SECRET_KEY = os.getenv("SECRET_KEY", "movie-insight-dev-key")
    TMDB_API_KEY = os.getenv("TMDB_API_KEY", "")
    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URL",
        "sqlite:///" + os.path.join(os.path.dirname(os.path.abspath(__file__)), "movies.db")
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # TMDB API 配置
    TMDB_BASE_URL = "https://api.themoviedb.org/3"
    TMDB_IMAGE_BASE_URL = "https://image.tmdb.org/t/p"


# 类型 ID → 中文名映射表（种子脚本用）
GENRE_MAP = {
    28: "动作", 12: "冒险", 16: "动画", 35: "喜剧", 80: "犯罪",
    99: "纪录", 18: "剧情", 10751: "家庭", 14: "奇幻", 36: "历史",
    27: "恐怖", 10402: "音乐", 9648: "悬疑", 10749: "爱情",
    878: "科幻", 10770: "电视电影", 53: "惊悚", 10752: "战争", 37: "西部",
}

# ISO 639-1 → 中文名映射表
LANGUAGE_MAP = {
    "en": "英语", "zh": "中文", "ja": "日语", "ko": "韩语", "fr": "法语",
    "de": "德语", "it": "意大利语", "es": "西班牙语", "pt": "葡萄牙语",
    "ru": "俄语", "hi": "印地语", "ar": "阿拉伯语",
}

# ISO 3166-1 → 中文名映射表
COUNTRY_MAP = {
    "US": "美国", "GB": "英国", "CN": "中国", "HK": "中国香港",
    "TW": "中国台湾", "JP": "日本", "KR": "韩国", "FR": "法国",
    "DE": "德国", "IT": "意大利", "CA": "加拿大", "AU": "澳大利亚",
    "IN": "印度", "RU": "俄罗斯", "ES": "西班牙", "BR": "巴西",
}

# 海报尺寸
POSTER_SIZES = ["w92", "w185", "w342", "w500", "w780", "original"]
