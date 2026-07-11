<template>
  <el-tooltip :content="isFav ? '取消收藏' : '加入收藏'" placement="top" :show-after="400">
    <span class="fav-btn" @click.stop="handleToggle">
      <el-icon :size="size === 'large' ? 22 : 16">
        <StarFilled v-if="isFav" style="color: #f9ca24" />
        <Star v-else style="color: #999" />
      </el-icon>
    </span>
  </el-tooltip>
</template>

<script setup>
import { ref, watch } from "vue";
import { Star, StarFilled } from "@element-plus/icons-vue";
import { isFavorite, toggleFavorite } from "../utils/favorites";

const props = defineProps({
  movieId: { type: Number, required: true },
  size: { type: String, default: "default" }, // "default" | "large"
});

const isFav = ref(isFavorite(props.movieId));

// 外部可能通过其他按钮切换同一电影的收藏状态
watch(
  () => props.movieId,
  (newId) => {
    isFav.value = isFavorite(newId);
  }
);

function handleToggle() {
  const result = toggleFavorite(props.movieId);
  isFav.value = result;
}
</script>

<style scoped>
.fav-btn {
  cursor: pointer;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  transition: transform 0.15s;
  user-select: none;
}
.fav-btn:hover {
  transform: scale(1.2);
}
</style>
