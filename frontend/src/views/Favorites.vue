<template>
  <div class="favorites-page">
    <h2 class="page-title">我的收藏</h2>

    <!-- ======== 加载状态 ======== -->
    <div v-if="loading" class="loading-wrapper">
      <el-skeleton :rows="3" animated />
      <div class="card-grid">
        <el-skeleton v-for="i in 8" :key="i" style="width: 100%">
          <template #template>
            <div class="skeleton-card">
              <div class="skeleton-poster"></div>
              <div style="padding: 10px">
                <el-skeleton-item variant="text" style="width: 80%" />
                <el-skeleton-item variant="text" style="width: 50%" />
              </div>
            </div>
          </template>
        </el-skeleton>
      </div>
    </div>

    <!-- ======== 空状态 ======== -->
    <div v-else-if="favoriteIds.length === 0" class="empty-state">
      <el-empty description="还没有收藏电影，去发现页看看吧">
        <el-button type="primary" @click="$router.push('/')">去发现</el-button>
      </el-empty>
    </div>

    <!-- ======== 卡片网格 ======== -->
    <template v-else>
      <p class="hint-text">共收藏 {{ favoriteIds.length }} 部电影</p>
      <div class="card-grid">
        <div
          v-for="movie in movies"
          :key="movie.id"
          class="movie-card"
          @click="goDetail(movie.id)"
        >
          <img
            v-if="movie.poster_path && !failedImages.has(movie.id)"
            :src="getPosterUrl(movie.poster_path, movie.source)"
            :alt="movie.title"
            class="movie-poster"
            loading="lazy"
            referrerpolicy="no-referrer"
            @error="() => failedImages.add(movie.id)"
          />
          <div v-else class="movie-poster-placeholder">
            <el-icon><VideoCamera /></el-icon>
          </div>

          <div class="card-info">
            <div class="card-header">
              <div class="card-title">{{ movie.title }}</div>
              <FavoriteButton :movie-id="movie.id" @toggled="handleUnfav" />
            </div>
            <div class="card-rating">
              <el-rate
                :model-value="toStarRating(movie.vote_average)"
                disabled
                :max="5"
                :colors="['#db2360', '#d2d531', '#21d07a']"
                style="height: 16px"
              />
              <span
                :class="{
                  'score-high': movie.vote_average >= 7.5,
                  'score-mid': movie.vote_average >= 5 && movie.vote_average < 7.5,
                  'score-low': movie.vote_average < 5,
                }"
              >
                {{ movie.vote_average?.toFixed(1) }}
              </span>
            </div>
            <div class="card-genres" v-if="movie.genres?.length">
              <el-tag
                v-for="g in movie.genres.slice(0, 3)"
                :key="g"
                size="small"
                type="info"
                style="margin-right: 4px; margin-top: 4px"
              >
                {{ g }}
              </el-tag>
            </div>
            <div class="card-source">
              <el-tag size="small" style="background:#01b4e4;border-color:#01b4e4;color:#fff">TMDB</el-tag>
            </div>
          </div>
        </div>
      </div>
    </template>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from "vue";
import { useRouter } from "vue-router";
import { VideoCamera } from "@element-plus/icons-vue";
import { fetchMovies } from "../api";
import { getFavorites } from "../utils/favorites";
import { getPosterUrl, toStarRating } from "../utils/movie";
import FavoriteButton from "../components/FavoriteButton.vue";

const router = useRouter();

const movies = ref([]);
const loading = ref(false);
const favoriteIds = ref([]);
const failedImages = reactive(new Set());

async function loadFavorites() {
  const ids = getFavorites();
  favoriteIds.value = ids;

  if (ids.length === 0) {
    movies.value = [];
    return;
  }

  loading.value = true;
  try {
    // 用搜索 API 批量获取收藏的电影（以逗号分隔的 id 不太可能）
    // 此处通过加载较大的 per_page 再前端筛选
    // 更优方案：后端增加按 id 列表查询接口（但 v2 不涉及后端改动）
    const res = await fetchMovies({ per_page: 250, sort: "vote_average" });
    const allMovies = res.data.data;
    const idSet = new Set(ids);
    movies.value = allMovies.filter((m) => idSet.has(m.id));
  } catch {
    // 错误由拦截器处理
  } finally {
    loading.value = false;
  }
}

function handleUnfav() {
  // 取消收藏后刷新列表
  loadFavorites();
}

function goDetail(id) {
  router.push(`/movie/${id}`);
}

onMounted(() => {
  loadFavorites();
});
</script>

<style scoped>
.favorites-page {
  max-width: 1400px;
  margin: 0 auto;
}

.page-title {
  font-size: 22px;
  font-weight: 700;
  margin-bottom: 8px;
}

.hint-text {
  color: #999;
  font-size: 13px;
  margin-bottom: 16px;
}

.card-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 20px;
}

.movie-card {
  background: #fff;
  border-radius: 8px;
  overflow: hidden;
  cursor: pointer;
  transition: transform 0.2s, box-shadow 0.2s;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.08);
}

.movie-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12);
}

.card-info {
  padding: 10px 12px 14px;
}

.card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
  margin-bottom: 4px;
}

.card-title {
  font-size: 14px;
  font-weight: 600;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  flex: 1;
}

.card-rating {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 13px;
}

.card-genres {
  min-height: 24px;
}

/* 加载骨架 */
.loading-wrapper {
  margin-top: 0;
}

.skeleton-card {
  background: #fff;
  border-radius: 8px;
  overflow: hidden;
}

.skeleton-poster {
  width: 100%;
  aspect-ratio: 2 / 3;
  background: #eee;
  animation: pulse 1.5s infinite;
}

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.4; }
}

.empty-state {
  padding: 80px 0;
}

/* 响应式 */
@media (max-width: 1200px) {
  .card-grid {
    grid-template-columns: repeat(3, 1fr);
  }
}
@media (max-width: 900px) {
  .card-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}
@media (max-width: 600px) {
  .card-grid {
    grid-template-columns: 1fr;
  }
}
</style>
