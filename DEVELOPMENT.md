# MovieInsight — 开发文档

> 全栈电影数据发现与分析平台  
> 版本：v1.1 MVP  
> 审核状态：✅ 已审核

---

## 一、技术选型

### 1.1 技术栈

| 层 | 技术 | 版本 | 选型理由 |
|----|------|------|----------|
| 前端框架 | Vue 3 (Composition API) | 3.5 | 用户已有 Vue 3 基础（OfferRadar 前端） |
| 构建工具 | Vite | 6.x | 快速 HMR，Vue 官方推荐 |
| UI 组件库 | Element Plus | 2.9 | 表格/分页/筛选/标签等开箱即用 |
| 图表库 | ECharts | 5.5 | 国内最主流，文档丰富，暗色主题支持 |
| HTTP 客户端 | Axios | 1.7 | 拦截器 + 代理配置 |
| 后端框架 | Flask | 3.1 | 轻量，用户 Python 脚本经验可迁移 |
| ORM | SQLAlchemy | 2.0 | Flask 生态标配 |
| 数据库 | SQLite | — | 零配置，自动建表，clone 即跑 |
| 测试框架 | pytest + pytest-flask | 8.x | Python 生态主流 |
| HTML 解析 | BeautifulSoup4 + lxml | 4.x + 5.x | 豆瓣页面解析 |
| 环境管理 | python-dotenv | 1.x | .env 文件管理 TMDB API Key |

### 1.2 不使用的技术（及原因）

| 技术 | 不使用的原因 |
|------|-------------|
| MySQL/PostgreSQL | SQLite 对 300 条数据绰绰有余，零配置体验更好 |
| Redis | 数据量小，SQLite 直查足够快 |
| Celery | 种子数据用独立脚本，无需异步任务队列 |
| Docker | MVP 阶段本地运行即可，不上云部署 |
| TypeScript | 增加学习成本，MVP 用纯 JavaScript |
| Pinia | 数据来自 API 实时请求，无需全局状态管理 |
| Vue Router 嵌套路由 | 4 个平级页面，不需要嵌套 |

---

## 二、项目结构

```
当前文件夹/
├── README.md                 # 项目说明（中英文）
├── REQUIREMENTS.md           # 需求文档
├── DEVELOPMENT.md            # 开发文档（本文件）
├── .gitignore
├── backend/
│   ├── app.py                # Flask 应用入口 + 工厂函数
│   ├── config.py             # 配置类（TMDB Key, SQLite 路径, 类型映射表）
│   ├── requirements.txt      # Python 依赖
│   ├── .env.example          # 环境变量模板
│   ├── seed.py               # 数据初始化脚本（独立运行）
│   ├── models/
│   │   ├── __init__.py
│   │   └── database.py       # Movie + Credit 模型（SQLAlchemy）
│   ├── services/
│   │   ├── __init__.py
│   │   ├── tmdb_service.py   # TMDB API 封装类
│   │   └── douban_service.py # 豆瓣 Top 250 爬虫
│   ├── api/
│   │   ├── __init__.py
│   │   ├── movies.py         # /api/movies, /api/genres, /api/years, /api/countries
│   │   ├── stats.py          # /api/stats 聚合统计
│   │   └── health.py         # /api/health 健康检查
│   └── tests/
│       ├── __init__.py
│       ├── conftest.py       # Fixtures（内存 SQLite + 种子数据）
│       └── test_api.py       # API 集成测试
├── frontend/
│   ├── package.json          # Vue 3 + Vite + Element Plus + ECharts + Axios
│   ├── vite.config.js        # 开发服务器 + /api 代理到 Flask
│   ├── index.html
│   └── src/
│       ├── main.js           # Vue 初始化（App + Router + Element Plus）
│       ├── App.vue           # 根组件（侧边栏 + 路由视图）
│       ├── api/
│       │   └── index.js      # Axios 封装 + 所有 API 函数
│       ├── router/
│       │   └── index.js      # 路由配置（3 个路由 + 懒加载）
│       ├── assets/
│       │   └── main.css      # 全局样式 + CSS 变量 + TMDB 配色
│       └── views/
│           ├── Discover.vue  # 发现页（卡片网格 + 筛选 + 分页）
│           ├── Dashboard.vue # 数据分析页（3 张图表）
│           └── MovieDetail.vue # 电影详情页（海报 + 演职表）
```

---

## 三、数据库设计

### 3.1 表结构

**movies（电影主表）**

```sql
CREATE TABLE movies (
    id                  INTEGER PRIMARY KEY AUTOINCREMENT,
    source              VARCHAR(16) DEFAULT 'tmdb',  -- 'tmdb' | 'douban'
    tmdb_id             INTEGER,                     -- TMDB 唯一标识（豆瓣数据为 NULL）
    douban_id           INTEGER,                     -- 豆瓣电影 ID（TMDB 数据为 NULL）
    title               VARCHAR(255) NOT NULL,       -- 中文标题
    original_title      VARCHAR(255) DEFAULT '',     -- 原始标题
    overview            TEXT DEFAULT '',             -- 中文剧情简介
    poster_path         VARCHAR(255) DEFAULT '',     -- 海报路径
    backdrop_path       VARCHAR(255) DEFAULT '',     -- 背景图路径
    release_date        VARCHAR(10) DEFAULT '',      -- YYYY-MM-DD
    runtime             INTEGER,                     -- 片长（分钟）
    vote_average        REAL DEFAULT 0.0,            -- TMDB/豆瓣 10分制评分
    douban_rating       REAL,                        -- 豆瓣评分（仅豆瓣数据源有值）
    vote_count          INTEGER DEFAULT 0,
    popularity          REAL DEFAULT 0.0,
    budget              INTEGER,                     -- 美元
    revenue             INTEGER,                     -- 美元
    original_language   VARCHAR(10) DEFAULT '',
    tagline             VARCHAR(500) DEFAULT '',
    genres              VARCHAR(255) DEFAULT '',     -- "动作,犯罪,剧情"
    production_countries VARCHAR(255) DEFAULT '',    -- "美国,英国"
    created_at          DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

**credits（演职人员表）**

```sql
CREATE TABLE credits (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    movie_id      INTEGER NOT NULL REFERENCES movies(id) ON DELETE CASCADE,
    person_id     INTEGER NOT NULL,              -- TMDB 人物 ID
    name          VARCHAR(255) NOT NULL,
    profile_path  VARCHAR(255) DEFAULT '',
    role          VARCHAR(255) DEFAULT '',       -- 角色名（cast）/ 职位名（crew）
    credit_type   VARCHAR(16) DEFAULT 'cast',    -- 'cast' | 'crew'
    department    VARCHAR(64) DEFAULT '',        -- 'Directing' | 'Writing' | ...
    popularity    REAL DEFAULT 0.0,
    "order"       INTEGER DEFAULT 0              -- 排序（SQLite 保留字用引号）
);
```

### 3.2 索引

- `movies.tmdb_id` — TMDB 去重查询
- `movies.douban_id` — 豆瓣去重查询
- `credits.movie_id` — 查询电影演职表时走索引

### 3.3 为什么用 SQLite

- 零配置，`db.create_all()` 自动建表
- clone 下来 `python app.py` 就能跑
- ~450 条数据 + ~4000 条演职记录，SQLite 查全表 < 10ms
- 不需要安装 MySQL 服务

---

## 四、API 设计

### 4.1 完整端点列表

| Method | Endpoint | 说明 | Query Params |
|--------|----------|------|-------------|
| GET | `/api/health` | 系统健康 + 数据概览 | — |
| GET | `/api/movies` | 电影列表（分页+筛选+排序+搜索） | page, per_page, genre, year_start, year_end, country, sort, order, search |
| GET | `/api/movies/<id>` | 电影详情 + 演职表 | — |
| GET | `/api/stats` | 看板统计数据 | — |
| GET | `/api/genres` | 类型列表 + 电影数量 | — |
| GET | `/api/years` | 年份列表 + 电影数量 | — |
| GET | `/api/countries` | 国家列表 + 电影数量 | — |

### 4.2 关键端点详细设计

#### GET /api/movies

**Query Params**:

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| page | int | 1 | 页码 |
| per_page | int | 20 | 每页数量（最大 100） |
| genre | str | — | 类型名，如"动作"，匹配 genres LIKE '%动作%' |
| year_start | int | — | 起始年份（含） |
| year_end | int | — | 结束年份（含） |
| country | str | — | 国家名，如"美国"，匹配 production_countries LIKE '%美国%' |
| sort | str | popularity | popularity / vote_average / revenue / release_date |
| order | str | desc | asc / desc |
| search | str | — | 搜索 title 或 original_title |

**业务逻辑**：
1. 组装 SQLAlchemy query，按参数添加 filter
2. `sort` 映射到对应列：
   - popularity → Movie.popularity
   - vote_average → Movie.vote_average（辅助排序 vote_count，避免 1 人评满分排第一）
   - revenue → Movie.revenue
   - release_date → Movie.release_date
3. 分页查询
4. 每条 movie 调用 `to_dict(include_overview=False)` 省略简介字段

#### GET /api/movies/<id>

**业务逻辑**：
1. `Movie.query.get_or_404(id)`
2. 查询该电影 Top 10 演员（credit_type='cast', order ASC）
3. 查询该电影 crew（credit_type='crew'）
4. 组装返回

#### GET /api/stats

**返回的数据**（v1.1 更新）：

1. **rating_distribution**：评分分布
   - `SELECT ROUND(vote_average, 1), COUNT(*) FROM movies WHERE vote_count > 0 GROUP BY ROUND(vote_average, 1) ORDER BY ROUND(vote_average, 1)`
   - 前端画直方图

2. **genre_distribution**：类型分布
   - 遍历所有 movies 的 genres 字段，split 后计数
   - 不用 SQL 聚合（genres 是逗号分隔字符串）

3. **yearly_trend**：年代趋势
   - `SELECT SUBSTR(release_date, 1, 4), COUNT(*), AVG(vote_average) FROM movies WHERE release_date != '' GROUP BY SUBSTR(release_date, 1, 4) ORDER BY SUBSTR(release_date, 1, 4)`
   - 前端画折线图（X 轴年份，Y 轴电影数量）

4. **source_distribution**：数据来源占比（v1.1 新增）
   - `SELECT source, COUNT(*) FROM movies GROUP BY source`
   - Dashboard 展示 TMDB / 豆瓣数据量占比

#### GET /api/genres, /api/years, /api/countries

- 用于填充前端筛选下拉框
- 返回 `[{name, count}, ...]` 格式，按 count 降序排列

---

## 五、关键业务逻辑

### 5.1 TMDB 10 分制 → 5 星制转换

```python
def to_star_rating(vote_average: float) -> float:
    """8.5 → 4.25"""
    return round(vote_average / 2, 2)
```

前端渲染时：
- 满星 ★ 填满比例
- 显示 "4.3/5"

### 5.2 片长格式化

```python
def format_runtime(minutes: int | None) -> str:
    """152 → '2h 32min'"""
    if not minutes:
        return ""
    h, m = divmod(minutes, 60)
    if h > 0:
        return f"{h}h {m}min" if m > 0 else f"{h}h"
    return f"{m}min"
```

### 5.3 金额缩写

```python
def format_money(amount: int | None) -> str:
    """185000000 → '$185M' / 1004558444 → '$1.0B'"""
    if not amount:
        return "—"
    if amount >= 1_000_000_000:
        return f"${amount / 1_000_000_000:.1f}B"
    if amount >= 1_000_000:
        return f"${amount / 1_000_000:.0f}M"
    return f"${amount:,}"
```

### 5.4 海报 URL 拼接

```python
# 数据库存：poster_path = "/qJ2tW6WMUDux911BytEM69y6o.jpg"
# 前端拼接：https://image.tmdb.org/t/p/w500/qJ2tW6WMUDux911BytEM69y6o.jpg
# 尺寸选项：w92 / w185 / w342 / w500 / w780 / original
```

---

## 六、数据初始化脚本

### 6.1 seed.py 设计

```python
"""
Usage: python seed.py

流程：
1. 从 .env 读取 TMDB_API_KEY
2. 调用 TMDB API 获取流行电影 8 页 + 高分电影 5 页
3. 爬取豆瓣 Top 250（10 页 × 25 部）
4. TMDB 内部去重（按 tmdb_id），豆瓣内部去重（按 douban_id）
5. 两源合并去重（按标题相似度匹配）
6. 逐部获取 TMDB 完整详情（含 credits）
7. 豆瓣数据直接写入（无演职人员信息）
8. 写入 SQLite
9. 打印统计结果
"""
```

**TMDB 关键细节**：
- 每两次 API 调用间隔 0.3 秒（避免触发速率限制）
- 已存在的 tmdb_id 跳过（幂等，可重复执行）
- 异常不中断流程（某部电影详情获取失败则跳过，记录日志）

**豆瓣爬虫关键细节**：
- 请求间隔 2 秒（避免触发反爬机制）
- 设置 User-Agent 模拟浏览器访问
- 解析每部电影的：标题、原名、评分、评价人数、简介、类型、海报 URL
- 豆瓣无演职人员数据（仅 TMDB 电影有 credits）
- 豆瓣数据 source='douban'，tmdb_id 为 NULL

**去重策略**：
- 同源去重：tmdb_id / douban_id
- 跨源去重：标题相似度 > 90% 视为同一部电影，优先保留 TMDB 数据（字段更全）
- 预计最终数据量：400-480 部

**预计耗时**：
- TMDB 部分：~260 部 × 0.6 秒 ≈ 2.6 分钟
- 豆瓣部分：250 部 × 2 秒 ≈ 8.3 分钟
- 总计约 **10-12 分钟**

---

## 七、前端数据流

### 7.1 组件树

```
App.vue
├── 侧边栏 (el-menu)
│   ├── 发现页 (/) → Discover.vue
│   ├── 数据分析 (/dashboard) → Dashboard.vue
│   └── (详情页 /movie/:id 不显示在菜单中)
├── 路由视图 (router-view)
│   ├── Discover.vue
│   │   ├── 筛选栏 (搜索框 + 下拉选择器 + 年份滑块)
│   │   ├── 卡片网格 (v-for, 懒加载, 骨架屏)
│   │   └── 分页器 (el-pagination)
│   ├── Dashboard.vue
│   │   └── 3 张 ECharts 图表
│   └── MovieDetail.vue
│       ├── 海报大图
│       ├── 信息面板 (el-descriptions)
│       └── 演职表 (el-table)
└── 页脚 (TMDB attribution)
```

### 7.2 API 调用策略

| 页面 | 触发时机 | 调用 |
|------|----------|------|
| 发现页 | mounted + 筛选条件变化 | `fetchMovies(params)` + `fetchGenres()` + `fetchYears()` + `fetchCountries()` |
| 详情页 | mounted + route.params.id 变化 | `fetchMovie(id)` |
| 分析页 | mounted | `fetchStats()` |

**说明**：不使用 Pinia/Vuex，因为数据来自 API 实时请求，没有跨页面共享状态的需求。筛选条件用 Discover.vue 的 reactive state 管理。

### 7.4 数据来源标识（v1.1 新增）

电影卡片和详情页显示数据来源标签：
- TMDB 来源：蓝色标签 "TMDB"
- 豆瓣来源：绿色标签 "豆瓣"
- 双源合并：两个标签并排显示
- 豆瓣电影无演职人员信息，详情页演职表区域显示"暂无演职人员数据"

### 7.3 海报懒加载

使用浏览器原生 `loading="lazy"` 属性：

```html
<img :src="posterUrl" loading="lazy" />
```

加载失败时显示骨架屏（Element Plus `<el-skeleton>`）。

---

## 八、测试策略

### 8.1 测试类型

**API 集成测试**（pytest + conftest 内存 SQLite）

### 8.2 测试用例

| 编号 | 测试内容 | 断言 |
|------|----------|------|
| T1 | GET /api/movies 返回列表 | status=200, data 长度=3 |
| T2 | 分页：per_page=1 | data 长度=1, pages=3 |
| T3 | 筛选：genre=动作 | data 长度=1, title="黑暗骑士" |
| T4 | 筛选：year_start=1994, year_end=1994 | data 长度=1, title="低俗小说" |
| T5 | 筛选：country=美国 | data 长度>=2 |
| T6 | 搜索：search=搏击 | data 长度=1 |
| T7 | 排序：sort=vote_average, order=asc | data[0] 评分 <= data[-1] 评分 |
| T8 | GET /api/movies/1 返回详情 | title + overview + cast + crew |
| T9 | GET /api/movies/99999 返回 404 | status=404 |
| T10 | GET /api/stats 返回统计 | total_movies=3, avg_rating>0 |
| T11 | GET /api/genres 返回类型 | 包含"剧情" |
| T12 | GET /api/years 返年份 | 包含"2008" |
| T13 | GET /api/countries 返回国家 | 包含"美国" |
| T14 | GET /api/health 返回健康 | status="healthy", total_movies=3 |

### 8.3 测试数据

conftest.py 预置 3 部电影（内存 SQLite）：
- 搏击俱乐部（1999，剧情/惊悚，美国，8.4 分）
- 低俗小说（1994，犯罪/剧情，美国，8.5 分）
- 黑暗骑士（2008，动作/犯罪/剧情，美国，8.5 分）

---

## 九、开发计划

### Flask 骨架 + 数据库模型
- [ ] 创建 Flask app + config
- [ ] 定义 Movie + Credit 模型
- [ ] `db.create_all()` 自动建表
- [ ] GET /api/health 返回 OK
- **验收**：`python app.py` → `curl localhost:5000/api/health` 返回 `{"ok":true}`

### TMDB Service + 种子脚本
- [ ] 实现 TMDBService 类（get_popular_movies, get_movie_detail, get_movie_credits）
- [ ] 实现 seed.py 脚本
- [ ] 测试拉取数据
- **验收**：`python seed.py` 成功入库约 200-260 部电影

### Movies API
- [ ] GET /api/movies（分页 + 筛选 + 排序 + 搜索）
- [ ] GET /api/movies/<id>（详情 + 演职表）
- [ ] GET /api/genres, /api/years, /api/countries
- **验收**：Postman/curl 测试所有筛选条件

### Stats API
- [ ] GET /api/stats（评分分布 + 类型分布 + 年代趋势）
- [ ] 数据校验和测试
- **验收**：curl /api/stats 返回正确统计数据

### pytest 测试
- [ ] conftest.py fixtures
- [ ] 14 条测试用例
- **验收**：`pytest tests/ -v` 全部通过

### Vue 3 脚手架 + 发现页
- [ ] Vite + Vue 3 + Element Plus 初始化
- [ ] Axios 封装 + API 代理
- [ ] 侧边栏布局 + 页脚
- [ ] 筛选栏（搜索框 + 类型下拉 + 年份滑块 + 国家下拉 + 排序下拉）
- [ ] 卡片网格（4 列，海报 + 标题 + 5 星评分 + 类型标签）
- [ ] 分页器
- **验收**：发现页能加载/筛选/搜索/翻页

### 数据分析页
- [ ] 3 张 ECharts 图表（暗色主题）
- [ ] 评分分布直方图
- [ ] 类型分布饼图
- [ ] 年代趋势折线图
- **验收**：3 张图表正确渲染

### 电影详情页
- [ ] 海报大图 + 信息面板
- [ ] 评分星级渲染 + 片长/预算/票房格式化
- [ ] 演职表（导演 + Top 10 演员）
- **验收**：从发现页点卡片跳转到详情页，信息完整

### UI 打磨
- [ ] 海报懒加载 + 骨架屏
- [ ] 空状态提示
- [ ] 错误处理（ElMessage）
- [ ] CSS 微调
- **验收**：整体体验流畅，无肉眼 bug

### 文档 + Git
- [ ] README.md（中英文，截图/gif + 安装步骤 + API 表格）
- [ ] .gitignore
- [ ] 分步 Git commit
- **验收**：GitHub 仓库完整可展示

---

## 十、Git 提交计划

| Commit | 内容 | 消息示例 |
|--------|------|----------|
| 1 | Flask 骨架 + 模型 + health API | `feat: init Flask app with SQLite models and health check` |
| 2 | TMDB service + seed 脚本 | `feat: add TMDB API wrapper and seed script` |
| 3 | Movies API（CRUD + 筛选） | `feat: add movies API with pagination, filtering and search` |
| 4 | Stats API | `feat: add stats API with rating/genre/yearly aggregations` |
| 5 | pytest 测试 | `test: add API integration tests with pytest` |
| 6 | Vue 3 脚手架 + 发现页 | `feat: add Vue 3 frontend with discover page` |
| 7 | 数据分析页 + ECharts | `feat: add dashboard page with ECharts visualizations` |
| 8 | 电影详情页 | `feat: add movie detail page with cast table` |
| 9 | UI 打磨 + 错误处理 | `style: polish UI, add skeletons and error handling` |
| 10 | README + 文档 | `docs: add bilingual README and project documentation` |

---

## 十一、风险与应对

| 风险 | 可能性 | 应对 |
|------|--------|------|
| TMDB API 在中国大陆被墙 | 高 | 需要科学上网环境，README 中说明 |
| 豆瓣反爬虫封 IP | 中 | 请求间隔 2 秒 + User-Agent 模拟浏览器 + 异常重试 |
| 豆瓣页面结构变更 | 中 | 选择器用 class + 层级组合，避免绝对路径 |
| API Key 注册需要手机验证 | 中 | 可能需要 Google 账号，提前确认 |
| 种子脚本运行太慢 | 低 | 总计约 10-12 分钟，可接受 |
| Element Plus 版本不兼容 | 低 | 锁定 package.json 版本号 |
| ECharts 暗色主题位移 | 低 | 手动配置颜色，不依赖默认主题 |

---

> **审核确认后立即开始 Flask 骨架 + 数据库模型。**
