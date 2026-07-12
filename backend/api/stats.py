"""Stats API — Dashboard 图表数据"""

from collections import Counter, defaultdict

from flask import Blueprint, jsonify
from sqlalchemy import func

from models import db
from models.database import Movie

stats_bp = Blueprint("stats", __name__)


@stats_bp.route("/api/stats", methods=["GET"])
def get_stats():
    """Dashboard 汇总数据：总数、均分、评分分布、类型分布、年代趋势。"""

    # ------------------------------------------------------------------
    # 基础汇总
    # ------------------------------------------------------------------
    total_movies = Movie.query.count()

    avg_rating_row = (
        Movie.query.with_entities(func.avg(Movie.vote_average))
        .filter(Movie.vote_average > 0)
        .first()
    )
    avg_rating = round(avg_rating_row[0], 1) if avg_rating_row[0] else 0.0

    # ------------------------------------------------------------------
    # 1. 评分分布 — SQL 按 ROUND(vote_average, 1) 分组
    # ------------------------------------------------------------------
    rating_rows = (
        Movie.query.with_entities(
            func.round(Movie.vote_average, 1).label("score"),
            func.count(Movie.id).label("count"),
        )
        .filter(Movie.vote_average > 0)
        .group_by("score")
        .order_by("score")
        .all()
    )
    rating_distribution = [
        {"score": float(row.score), "count": row.count} for row in rating_rows
    ]

    # ------------------------------------------------------------------
    # 2. 年代趋势 — SQL 按 SUBSTR(release_date, 1, 4) 分组
    # ------------------------------------------------------------------
    yearly_rows = (
        Movie.query.with_entities(
            func.substr(Movie.release_date, 1, 4).label("year"),
            func.count(Movie.id).label("count"),
            func.avg(Movie.vote_average).label("avg_rating"),
        )
        .filter(Movie.release_date != "")
        .group_by("year")
        .order_by("year")
        .all()
    )
    yearly_trend = [
        {
            "year": int(row.year),
            "count": row.count,
            "avg_rating": round(row.avg_rating, 1) if row.avg_rating else 0.0,
        }
        for row in yearly_rows
    ]

    # ------------------------------------------------------------------
    # 3. 类型分布 — Python 端拆分 + Counter + 每个类型的平均评分
    # ------------------------------------------------------------------
    all_movies = Movie.query.with_entities(
        Movie.genres, Movie.vote_average
    ).all()

    genre_counter = Counter()
    # 记录每个类型的所有评分，用于算均分
    genre_ratings = defaultdict(list)

    for genres_str, vote_avg in all_movies:
        if not genres_str:
            continue
        for g in genres_str.split(","):
            g = g.strip()
            if not g:
                continue
            genre_counter[g] += 1
            if vote_avg and vote_avg > 0:
                genre_ratings[g].append(vote_avg)

    genre_distribution = [
        {
            "name": genre,
            "count": count,
            "avg_rating": round(sum(genre_ratings[genre]) / len(genre_ratings[genre]), 1)
            if genre_ratings[genre]
            else 0.0,
        }
        for genre, count in genre_counter.most_common()
    ]

    # ------------------------------------------------------------------
    # 4. 数据来源分布
    # ------------------------------------------------------------------
    source_rows = (
        Movie.query.with_entities(Movie.source, func.count(Movie.id))
        .group_by(Movie.source)
        .all()
    )
    source_distribution = [
        {"source": row[0], "count": row[1]} for row in source_rows
    ]

    # ------------------------------------------------------------------
    # 5. 预算 vs 票房散点图数据
    # ------------------------------------------------------------------
    br_rows = (
        Movie.query.with_entities(
            Movie.title, Movie.budget, Movie.revenue
        )
        .filter(Movie.budget > 0, Movie.revenue > 0)
        .order_by(Movie.budget.desc())
        .limit(200)
        .all()
    )
    budget_revenue = [
        {"title": row.title, "budget": row.budget, "revenue": row.revenue}
        for row in br_rows
    ]

    # ------------------------------------------------------------------
    # 6. 片长分布（每 30 分钟一个桶）
    # ------------------------------------------------------------------
    runtime_rows = (
        Movie.query.with_entities(Movie.runtime)
        .filter(Movie.runtime > 0, Movie.runtime <= 300)
        .all()
    )
    runtime_buckets = defaultdict(int)
    for (rt,) in runtime_rows:
        bucket = (rt // 30) * 30  # 0, 30, 60, 90, ...
        label = f"{bucket}-{bucket + 29}min"
        runtime_buckets[label] += 1
    runtime_distribution = [
        {"range": k, "count": v}
        for k, v in sorted(
            runtime_buckets.items(),
            key=lambda x: int(x[0].split("-")[0])
        )
    ]

    # ------------------------------------------------------------------
    # 7. 评分 vs 热度散点图数据
    # ------------------------------------------------------------------
    rp_rows = (
        Movie.query.with_entities(
            Movie.title, Movie.vote_average, Movie.popularity
        )
        .filter(Movie.vote_average > 0, Movie.popularity > 0)
        .order_by(Movie.popularity.desc())
        .limit(200)
        .all()
    )
    rating_popularity = [
        {"title": row.title, "vote_average": float(row.vote_average), "popularity": float(row.popularity)}
        for row in rp_rows
    ]

    # ------------------------------------------------------------------
    # 8. 国家/地区产量 Top 15
    # ------------------------------------------------------------------
    all_movies_countries = Movie.query.with_entities(
        Movie.production_countries
    ).all()
    country_counter = Counter()
    for (cs,) in all_movies_countries:
        if not cs:
            continue
        for c in cs.split(","):
            c = c.strip()
            if c:
                country_counter[c] += 1
    country_top15 = [
        {"name": name, "count": count}
        for name, count in country_counter.most_common(15)
    ]

    # ------------------------------------------------------------------
    # 组装响应
    # ------------------------------------------------------------------
    return jsonify(
        {
            "data": {
                "total_movies": total_movies,
                "avg_rating": avg_rating,
                "rating_distribution": rating_distribution,
                "genre_distribution": genre_distribution,
                "yearly_trend": yearly_trend,
                "source_distribution": source_distribution,
                "budget_revenue": budget_revenue,
                "runtime_distribution": runtime_distribution,
                "rating_popularity": rating_popularity,
                "country_top15": country_top15,
            }
        }
    )
