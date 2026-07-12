"""
MetaMovie 数据初始化脚本

用法：
    cd backend
    python seed.py

说明：
    - 从 TMDB API 拉取热门 + 高分电影
    - TMDB 内部去重
    - 逐部获取 TMDB 完整详情（含 credits）
    - 可重复执行（已存在的 id 自动跳过）
    - 预计耗时约 5-6 分钟
"""
import time
import sys
from app import create_app
from config import Config
from models import db
from models.database import Movie, Credit
from services.tmdb_service import TMDBService


def main():
    # 检查 API Key
    if not Config.TMDB_API_KEY or Config.TMDB_API_KEY == "your_api_key_here":
        print("错误：请先在 .env 文件中配置 TMDB_API_KEY")
        sys.exit(1)

    print("=" * 50)
    print("  MetaMovie — 数据初始化")
    print("  TMDB 数据源")
    print("=" * 50)

    app = create_app()
    tmdb = TMDBService(Config.TMDB_API_KEY)

    # ==================================================================
    # [1/4] 获取 TMDB 电影列表
    # ==================================================================
    print("\n[1/4] 获取 TMDB 电影列表...")
    all_tmdb = []

    # 热门电影 8 页
    for page in range(1, 9):
        movies = tmdb.get_popular_movies(page)
        all_tmdb.extend(movies)
        print(f"  热门 第{page}页 → {len(movies)} 部")

    # 高分电影 5 页
    for page in range(1, 6):
        movies = tmdb.get_top_rated_movies(page)
        all_tmdb.extend(movies)
        print(f"  高分 第{page}页 → {len(movies)} 部")

    # TMDB 内部去重
    seen_tmdb = set()
    unique_tmdb = []
    for m in all_tmdb:
        tid = m.get("id")
        if tid and tid not in seen_tmdb:
            seen_tmdb.add(tid)
            unique_tmdb.append(m)

    print(f"  TMDB 去重后共 {len(unique_tmdb)} 部")

    # ==================================================================
    # [2/4] 检查已入库数据
    # ==================================================================
    print("\n[2/4] 检查已入库数据...")
    with app.app_context():
        existing_tmdb_ids = set()
        for row in db.session.query(Movie.tmdb_id).all():
            if row[0]:
                existing_tmdb_ids.add(row[0])

    print(f"  已存在 TMDB: {len(existing_tmdb_ids)} 部")

    # ==================================================================
    # [3/4] 写库
    # ==================================================================
    print("\n[3/4] 获取详情并写入数据库...")
    new_tmdb = 0
    new_credits = 0
    skipped = 0
    errors = 0

    with app.app_context():
        total_tmdb = len(unique_tmdb)
        for i, m in enumerate(unique_tmdb):
            tmdb_id = m.get("id")
            if not tmdb_id:
                continue

            if tmdb_id in existing_tmdb_ids:
                skipped += 1
                continue

            # 获取详情
            detail = tmdb.get_movie_detail(tmdb_id)
            if not detail:
                errors += 1
                continue

            # 获取演职人员
            credits_data = tmdb.get_movie_credits(tmdb_id)

            # 写入电影
            detail["source"] = "tmdb"
            movie = Movie(**detail)
            db.session.add(movie)
            db.session.flush()

            # 写入演职人员
            if credits_data:
                for d in credits_data.get("directors", []):
                    db.session.add(Credit(movie_id=movie.id, **d))
                    new_credits += 1
                for a in credits_data.get("actors", []):
                    db.session.add(Credit(movie_id=movie.id, **a))
                    new_credits += 1

            db.session.commit()
            new_tmdb += 1

            if (i + 1) % 10 == 0:
                print(f"  TMDB: {i+1}/{total_tmdb}  "
                      f"({new_tmdb} 新, {errors} 失败)")

    # ==================================================================
    # [4/4] 统计
    # ==================================================================
    print("\n[4/4] 完成！")
    print("-" * 50)
    with app.app_context():
        total_movies = Movie.query.count()
        total_credits = Credit.query.count()

    print(f"  电影总数: {total_movies}")
    print(f"  演职记录: {total_credits}")
    print(f"  本次新增: {new_tmdb} 部")
    print(f"  TMDB API 调用: {tmdb.request_count} 次")
    print(f"  跳过(已存在): {skipped} 部")
    print(f"  失败: {errors} 部")
    print("=" * 50)


if __name__ == "__main__":
    start = time.time()
    main()
    elapsed = time.time() - start
    print(f"\n总耗时: {elapsed:.1f} 秒 ({elapsed / 60:.1f} 分钟)")
