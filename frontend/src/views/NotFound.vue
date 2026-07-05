<template>
  <div class="not-found-page">
    <el-empty description="页面不存在">
      <template #image>
        <div class="error-code">404</div>
      </template>
      <el-button type="primary" @click="$router.push('/')">返回首页</el-button>
    </el-empty>
  </div>
</template>

<script setup>
</script>

<style scoped>
.not-found-page {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 60vh;
}

.error-code {
  font-size: 72px;
  font-weight: 800;
  color: #dcdfe6;
  letter-spacing: 4px;
}
</style>
