# 🎬 MetaMovie

> 全栈电影数据发现与分析平台 — 基于 TMDB API + 豆瓣 Top 250 的 Vue 3 + Flask 全栈项目

[![Vue 3](https://img.shields.io/badge/Vue-3.5-4FC08D?logo=vue.js)](https://vuejs.org/)
[![Flask](https://img.shields.io/badge/Flask-3.1-000000?logo=flask)](https://flask.palletsprojects.com/)
[![ECharts](https://img.shields.io/badge/ECharts-5.5-AA344D)](https://echarts.apache.org/)
[![Element Plus](https://img.shields.io/badge/Element_Plus-2.9-409EFF)](https://element-plus.org/)
[![Docker](https://img.shields.io/badge/Docker-✓-2496ED?logo=docker)](https://www.docker.com/)
[![CI](https://img.shields.io/badge/CI-GitHub_Actions-2088FF?logo=githubactions)](.github/workflows/ci.yml)
[![License](https://img.shields.io/badge/license-MIT-blue)](LICENSE)

## 📸 预览

- **发现页** — 多维度筛选 + 卡片网格 + 分页 + ⭐ 收藏
- **详情页** — 海报 + 演职表 + 预算票房 + 收藏按钮
- **我的收藏** — localStorage 持久化收藏列表
- **数据分析** — 8 组 ECharts 图表：评分分布、类型占比、年代趋势、预算×票房散点、片长分布、国家排行、评分×热度、数据来源

## ✨ 功能

| 功能 | 描述 |
|------|------|
| 🔍 电影发现 | 按类型/年份/国家/评分/热度筛选，关键词搜索，TMDB/豆瓣双源标识 |
| ⭐ 我的收藏 | localStorage 持久化，支持卡片/详情页一键收藏，侧边栏入口 |
| 📊 数据分析 | 8 组数据看板：评分分布 + 类型饼图 + 年代趋势 + 预算×票房散点 + 片长分布 + 国家排行 + 评分×热度散点 + 数据来源 |
| 🎥 电影详情 | 海报大图 + 基本信息 + 剧情简介 + 演职表（豆瓣数据标注豆瓣评分） |
| 📄 双数据源 | TMDB 热门+高分电影 + 豆瓣 Top 250，跨源去重合并 400+ 部 |
| 🎨 TMDB 风格 | TMDB 深蓝/浅蓝配色，暗色数据看板 |
| 🐳 一键部署 | Docker Compose 一键启动前后端 + SQLite 数据持久化 |
| 🧪 自动化测试 | pytest 16 条 + Vitest 34 条 + GitHub Actions CI |

## 🚀 快速开始

### Docker 一键部署（推荐）

```bash
# 1. 配置环境变量
cp backend/.env.example backend/.env
# 编辑 backend/.env，填入 TMDB_API_KEY

# 2. 启动
docker compose up -d

# 3. 初始化数据
docker compose exec backend python seed.py

# 4. 打开浏览器
# http://localhost — 前端 SPA
# http://localhost:5000/api/health — 后端 API
```

### 本地开发

#### 环境要求

- Python 3.10+
- Node.js 18+
- TMDB API Key（[免费注册](https://www.themoviedb.org/settings/api)）

#### 1. 克隆项目

```bash
git clone https://github.com/Poki-cbq/MetaMovie.git
cd MetaMovie
```

#### 2. 后端

```bash
cd backend

# 创建虚拟环境
python -m venv venv
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt

# 配置环境变量
cp .env.example .env
# 编辑 .env，填入你的 TMDB_API_KEY

# 初始化数据（TMDB ~260 部 + 豆瓣 250 部，跨源去重后约 400-480 部，约 10-12 分钟）
python seed.py

# 启动后端（默认 http://localhost:5000）
python app.py
```

#### 3. 前端

```bash
cd frontend

# 安装依赖
npm install

# 启动开发服务器（默认 http://localhost:5173）
npm run dev
```

#### 4. 打开浏览器

访问 **http://localhost:5173**

## 🛠 技术栈

| 层 | 技术 |
|----|------|
| 前端框架 | Vue 3 (Composition API) |
| 构建工具 | Vite 6 |
| UI 组件库 | Element Plus 2.9 |
| 图表 | ECharts 5.5 |
| 后端框架 | Flask 3.1 |
| ORM | SQLAlchemy 2.0 |
| 数据库 | SQLite |
| 爬虫 | BeautifulSoup4 + lxml |
| 后端测试 | pytest + pytest-flask |
| 前端测试 | Vitest + jsdom + Vue Test Utils |
| CI/CD | GitHub Actions |
| 容器化 | Docker + Docker Compose + Nginx |

## 📡 API

| Method | Endpoint | 说明 |
|--------|----------|------|
| GET | `/api/health` | 健康检查 |
| GET | `/api/movies` | 电影列表（分页+筛选+排序+搜索） |
| GET | `/api/movies/<id>` | 电影详情 + 演职表 |
| GET | `/api/stats` | 看板统计数据（含 8 个图表维度） |
| GET | `/api/genres` | 类型列表 |
| GET | `/api/years` | 年份列表 |
| GET | `/api/countries` | 国家列表 |

### 筛选参数 (`/api/movies`)

| 参数 | 类型 | 说明 |
|------|------|------|
| page | int | 页码（默认 1） |
| per_page | int | 每页数量（默认 20） |
| genre | str | 类型名，如"动作" |
| year_start | int | 起始年份 |
| year_end | int | 结束年份 |
| country | str | 国家名，如"美国" |
| sort | str | 排序字段：popularity / vote_average / release_date / revenue |
| order | str | asc / desc |
| search | str | 搜索标题 |

## 📁 项目结构

```
MetaMovie/
├── .github/workflows/ci.yml         ← GitHub Actions CI
├── docker-compose.yml               ← Docker 一键部署
├── Dockerfile.backend
├── Dockerfile.frontend
├── nginx.conf
├── ROADMAP_V2.md                    ← v2.0 路线图
├── README.md
├── backend/
│   ├── app.py                       ← Flask 入口
│   ├── config.py                    ← 配置 + 启动校验
│   ├── seed.py                      ← 数据初始化脚本
│   ├── requirements.txt
│   ├── models/database.py           ← SQLAlchemy 模型
│   ├── services/
│   │   ├── tmdb_service.py           ← TMDB API 封装
│   │   └── douban_service.py         ← 豆瓣 Top 250 爬虫
│   ├── api/                         ← API 蓝图
│   │   ├── movies.py
│   │   ├── stats.py
│   │   └── health.py
│   └── tests/                       ← pytest 测试（16 条）
└── frontend/
    ├── public/favicon.svg
    ├── vitest.config.js
    ├── src/
    │   ├── App.vue                  ← 根组件（侧边栏 + 路由）
    │   ├── router/index.js
    │   ├── api/index.js             ← Axios 封装
    │   ├── utils/
    │   │   ├── movie.js             ← 海报/评分/片长工具
    │   │   └── favorites.js         ← localStorage 收藏
    │   ├── components/
    │   │   └── FavoriteButton.vue   ← 收藏按钮
    │   └── views/
    │       ├── Discover.vue         ← 电影发现
    │       ├── Dashboard.vue        ← 8 组图表看板
    │       ├── MovieDetail.vue      ← 电影详情
    │       ├── Favorites.vue        ← 我的收藏
    │       └── NotFound.vue         ← 404
    └── tests/
        ├── utils/movie.test.js      ← 工具函数测试（28 条）
        └── views/Discover.test.js   ← 组件测试（6 条）
```

## 🧪 测试

```bash
# 后端
cd backend
pytest tests/ -v

# 前端
cd frontend
npm test
```

## 📄 数据来源

电影数据来自 [TMDB](https://www.themoviedb.org/) API 和 [豆瓣 Top 250](https://movie.douban.com/top250)。本项目仅用于学习与作品展示目的。

## 📝 License

MIT
