from flask import Blueprint, jsonify
from models.database import Movie, Credit

health_bp = Blueprint("health", __name__)


@health_bp.route("/api/health", methods=["GET"])
def health_check():
    """健康检查 + 数据概览"""
    movie_count = Movie.query.count()
    credit_count = Credit.query.count()

    return jsonify({
        "status": "healthy",
        "total_movies": movie_count,
        "total_credits": credit_count,
    })
