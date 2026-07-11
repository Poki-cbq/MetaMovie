<template>
  <div class="dashboard-page">
    <h2 class="page-title">数据分析</h2>

    <!-- ======== 加载状态 ======== -->
    <template v-if="loading">
      <div class="stat-cards">
        <el-skeleton v-for="i in 2" :key="i" style="width: 200px" animated>
          <template #template>
            <el-skeleton-item variant="text" style="width: 60%" />
            <el-skeleton-item variant="text" style="width: 40%" />
          </template>
        </el-skeleton>
      </div>
      <div class="charts-grid">
        <el-skeleton v-for="i in 3" :key="i" style="height: 360px" animated>
          <template #template>
            <el-skeleton-item variant="rect" style="height: 100%" />
          </template>
        </el-skeleton>
      </div>
    </template>

    <!-- ======== 空状态 ======== -->
    <el-empty
      v-else-if="!stats"
      description="暂无统计数据"
    />

    <!-- ======== 数据展示 ======== -->
    <template v-else>
      <!-- 统计卡片 -->
      <div class="stat-cards">
        <div class="stat-card">
          <div class="stat-value">{{ stats.total_movies }}</div>
          <div class="stat-label">电影总数</div>
        </div>
        <div class="stat-card">
          <div class="stat-value">{{ stats.avg_rating }}</div>
          <div class="stat-label">平均评分</div>
        </div>
        <div class="stat-card stat-card--tmdb">
          <div class="stat-value">{{ tmdbCount }}</div>
          <div class="stat-label">TMDB 来源</div>
        </div>
        <div class="stat-card stat-card--douban">
          <div class="stat-value">{{ doubanCount }}</div>
          <div class="stat-label">豆瓣 来源</div>
        </div>
      </div>

      <!-- 图表 -->
      <div class="charts-grid">
        <div class="chart-card">
          <div class="chart-header">评分分布</div>
          <div ref="ratingChartRef" class="chart-body"></div>
        </div>
        <div class="chart-card">
          <div class="chart-header">类型分布</div>
          <div ref="genreChartRef" class="chart-body"></div>
        </div>
        <div class="chart-card chart-card--wide">
          <div class="chart-header">年代趋势</div>
          <div ref="yearChartRef" class="chart-body"></div>
        </div>
        <div class="chart-card">
          <div class="chart-header">预算 × 票房</div>
          <div ref="budgetRevChartRef" class="chart-body"></div>
        </div>
        <div class="chart-card">
          <div class="chart-header">片长分布</div>
          <div ref="runtimeChartRef" class="chart-body"></div>
        </div>
        <div class="chart-card">
          <div class="chart-header">国家 / 地区排行</div>
          <div ref="countryChartRef" class="chart-body"></div>
        </div>
        <div class="chart-card">
          <div class="chart-header">评分 × 热度</div>
          <div ref="ratingPopChartRef" class="chart-body"></div>
        </div>
        <div class="chart-card">
          <div class="chart-header">数据来源</div>
          <div ref="sourceChartRef" class="chart-body"></div>
        </div>
      </div>
    </template>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onBeforeUnmount, nextTick } from "vue";
import * as echarts from "echarts";
import { fetchStats } from "../api";
import { formatMoney } from "../utils/movie";

// ---------------------------------------------------------------------------
// 数据
// ---------------------------------------------------------------------------
const stats = ref(null);
const loading = ref(true);

// 图表容器引用
const ratingChartRef = ref(null);
const genreChartRef = ref(null);
const yearChartRef = ref(null);
const sourceChartRef = ref(null);
const budgetRevChartRef = ref(null);
const runtimeChartRef = ref(null);
const countryChartRef = ref(null);
const ratingPopChartRef = ref(null);

let ratingChart = null;
let genreChart = null;
let yearChart = null;
let sourceChart = null;
let budgetRevChart = null;
let runtimeChart = null;
let countryChart = null;
let ratingPopChart = null;

// 数据来源统计
const tmdbCount = computed(() => {
  if (!stats.value?.source_distribution) return 0;
  const item = stats.value.source_distribution.find((s) => s.source === "tmdb");
  return item ? item.count : 0;
});

const doubanCount = computed(() => {
  if (!stats.value?.source_distribution) return 0;
  const item = stats.value.source_distribution.find((s) => s.source === "douban");
  return item ? item.count : 0;
});

// ---------------------------------------------------------------------------
// 暗色主题默认色板
// ---------------------------------------------------------------------------
const DARK_COLORS = [
  "#01b4e4", "#90cea1", "#21d07a", "#d2d531", "#db2360",
  "#ff6b6b", "#4ecdc4", "#45b7d1", "#f9ca24", "#6c5ce7",
  "#a29bfe", "#fd79a8", "#00cec9", "#fab1a0", "#81ecec",
  "#ffeaa7", "#dfe6e9", "#74b9ff", "#55efc4", "#e17055",
];

// ---------------------------------------------------------------------------
// ECharts 初始化工具
// ---------------------------------------------------------------------------
function makeChart(domRef) {
  if (!domRef) return null;
  const chart = echarts.init(domRef, "dark");
  chart.setOption({
    backgroundColor: "#1a1a2e",
    textStyle: { color: "#ccc" },
  });
  return chart;
}

function buildRatingChart(data) {
  if (!ratingChart || !data?.length) return;
  ratingChart.setOption({
    tooltip: {
      trigger: "axis",
      formatter: (p) => `评分 ${p[0].axisValue}<br/>电影数 ${p[0].value}`,
    },
    xAxis: {
      type: "category",
      data: data.map((d) => d.score.toFixed(1)),
      name: "评分",
      axisLabel: { interval: 4, rotate: 0 },
    },
    yAxis: { type: "value", name: "电影数" },
    series: [
      {
        type: "bar",
        data: data.map((d) => d.count),
        itemStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: "#01b4e4" },
            { offset: 1, color: "#0d253f" },
          ]),
          borderRadius: [4, 4, 0, 0],
        },
      },
    ],
    grid: { top: 20, right: 20, bottom: 40, left: 50 },
  });
}

function buildGenreChart(data) {
  if (!genreChart || !data?.length) return;
  const top12 = data.slice(0, 12);
  genreChart.setOption({
    tooltip: {
      trigger: "item",
      formatter: (p) => `${p.name}<br/>${p.value} 部 · 均分 ${top12[p.dataIndex].avg_rating}`,
    },
    series: [
      {
        type: "pie",
        radius: ["40%", "72%"],
        center: ["50%", "55%"],
        avoidLabelOverlap: false,
        itemStyle: { borderRadius: 6, borderColor: "#1a1a2e", borderWidth: 3 },
        label: { show: true, formatter: "{b}\n{d}%" },
        emphasis: {
          label: { fontSize: 16, fontWeight: "bold" },
        },
        data: top12.map((g, i) => ({
          name: g.name,
          value: g.count,
          itemStyle: { color: DARK_COLORS[i % DARK_COLORS.length] },
        })),
      },
    ],
  });
}

function buildSourceChart(data) {
  if (!sourceChart || !data?.length) return;
  sourceChart.setOption({
    tooltip: {
      trigger: "item",
      formatter: (p) => `${p.name}<br/>${p.value} 部 (${p.percent}%)`,
    },
    series: [
      {
        type: "pie",
        radius: ["45%", "72%"],
        center: ["50%", "55%"],
        avoidLabelOverlap: false,
        itemStyle: { borderRadius: 4, borderColor: "#1a1a2e", borderWidth: 3 },
        label: { show: true, formatter: "{b}\n{d}%" },
        emphasis: {
          label: { fontSize: 16, fontWeight: "bold" },
        },
        data: data.map((s) => ({
          name: s.source === "tmdb" ? "TMDB" : "豆瓣",
          value: s.count,
          itemStyle: { color: s.source === "tmdb" ? "#01b4e4" : "#21d07a" },
        })),
      },
    ],
  });
}

// ---------------------------------------------------------------------------
// 新增 4 个图表
// ---------------------------------------------------------------------------

function buildBudgetRevenueChart(data) {
  if (!budgetRevChart || !data?.length) return;

  // 计算对角线范围
  const maxVal = Math.max(
    ...data.map((d) => Math.max(d.budget, d.revenue))
  );

  budgetRevChart.setOption({
    tooltip: {
      trigger: "item",
      formatter: (p) => {
        const d = data[p.dataIndex];
        return `<b>${d.title}</b><br/>预算 ${formatMoney(d.budget)}<br/>票房 ${formatMoney(d.revenue)}`;
      },
    },
    xAxis: {
      type: "value",
      name: "预算 (USD)",
      nameLocation: "middle",
      nameGap: 30,
      axisLabel: { formatter: (v) => (v >= 1e9 ? `$${(v / 1e9).toFixed(1)}B` : `$${Math.round(v / 1e6)}M`) },
      splitLine: { lineStyle: { color: "rgba(255,255,255,0.06)" } },
    },
    yAxis: {
      type: "value",
      name: "票房 (USD)",
      axisLabel: { formatter: (v) => (v >= 1e9 ? `$${(v / 1e9).toFixed(1)}B` : `$${Math.round(v / 1e6)}M`) },
      splitLine: { lineStyle: { color: "rgba(255,255,255,0.06)" } },
    },
    series: [
      // 对角线（回本线）
      {
        type: "line",
        markLine: {
          silent: true,
          symbol: "none",
          lineStyle: { color: "rgba(255,255,255,0.2)", type: "dashed" },
          data: [
            [
              { coord: [0, 0] },
              { coord: [maxVal, maxVal] },
            ],
          ],
        },
      },
      // 散点
      {
        type: "scatter",
        data: data.map((d) => [d.budget, d.revenue]),
        symbolSize: 8,
        itemStyle: {
          color: new echarts.graphic.RadialGradient(0.4, 0.3, 1, [
            { offset: 0, color: "#01b4e4" },
            { offset: 1, color: "#0d253f" },
          ]),
          borderColor: "rgba(1,180,228,0.4)",
          borderWidth: 1,
        },
        emphasis: {
          itemStyle: { borderWidth: 2, borderColor: "#f9ca24" },
          scale: 1.5,
        },
      },
    ],
    grid: { top: 20, right: 50, bottom: 50, left: 70 },
  });
}

function buildRuntimeChart(data) {
  if (!runtimeChart || !data?.length) return;
  runtimeChart.setOption({
    tooltip: {
      trigger: "axis",
      formatter: (p) => `${p[0].axisValue}<br/>${p[0].value} 部`,
    },
    xAxis: {
      type: "category",
      data: data.map((d) => d.range),
      axisLabel: { rotate: 0, interval: 1, fontSize: 10 },
    },
    yAxis: {
      type: "value",
      name: "电影数",
      splitLine: { lineStyle: { color: "rgba(255,255,255,0.06)" } },
    },
    series: [
      {
        type: "bar",
        data: data.map((d) => d.count),
        itemStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: "#d2d531" },
            { offset: 1, color: "#0d253f" },
          ]),
          borderRadius: [4, 4, 0, 0],
        },
        barMaxWidth: 30,
      },
    ],
    grid: { top: 20, right: 20, bottom: 50, left: 50 },
  });
}

function buildCountryChart(data) {
  if (!countryChart || !data?.length) return;
  // 反转使排行从上到下
  const reversed = [...data].reverse();
  countryChart.setOption({
    tooltip: {
      trigger: "axis",
      formatter: (p) => `${p[0].name}<br/>${p[0].value} 部`,
    },
    xAxis: {
      type: "value",
      name: "电影数",
      splitLine: { lineStyle: { color: "rgba(255,255,255,0.06)" } },
    },
    yAxis: {
      type: "category",
      data: reversed.map((d) => d.name),
      axisLabel: { fontSize: 11 },
    },
    series: [
      {
        type: "bar",
        data: reversed.map((d) => d.count),
        itemStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 1, 0, [
            { offset: 0, color: "#0d253f" },
            { offset: 1, color: "#90cea1" },
          ]),
          borderRadius: [0, 4, 4, 0],
        },
        barMaxWidth: 20,
      },
    ],
    grid: { top: 10, right: 20, bottom: 20, left: 80 },
  });
}

function buildRatingPopularityChart(data) {
  if (!ratingPopChart || !data?.length) return;
  ratingPopChart.setOption({
    tooltip: {
      trigger: "item",
      formatter: (p) => {
        const d = data[p.dataIndex];
        return `<b>${d.title}</b><br/>评分 ${d.vote_average}<br/>热度 ${d.popularity.toFixed(1)}`;
      },
    },
    xAxis: {
      type: "value",
      name: "评分",
      nameLocation: "middle",
      nameGap: 30,
      min: 0,
      max: 10,
      splitLine: { lineStyle: { color: "rgba(255,255,255,0.06)" } },
    },
    yAxis: {
      type: "value",
      name: "热度",
      splitLine: { lineStyle: { color: "rgba(255,255,255,0.06)" } },
    },
    series: [
      {
        type: "scatter",
        data: data.map((d) => [d.vote_average, d.popularity]),
        symbolSize: 7,
        itemStyle: {
          color: new echarts.graphic.RadialGradient(0.4, 0.3, 1, [
            { offset: 0, color: "#21d07a" },
            { offset: 1, color: "#0d253f" },
          ]),
          borderColor: "rgba(33,208,122,0.4)",
          borderWidth: 1,
        },
        emphasis: {
          itemStyle: { borderWidth: 2, borderColor: "#f9ca24" },
          scale: 1.5,
        },
      },
    ],
    grid: { top: 20, right: 30, bottom: 50, left: 60 },
  });
}

function buildYearChart(data) {
  if (!yearChart || !data?.length) return;
  yearChart.setOption({
    tooltip: {
      trigger: "axis",
      formatter: (p) => {
        const item = p[0];
        const avg = data[item.dataIndex]?.avg_rating ?? "-";
        return `${item.axisValue} 年<br/>${item.value} 部 · 均分 ${avg}`;
      },
    },
    xAxis: {
      type: "category",
      data: data.map((d) => d.year),
      name: "年份",
      axisLabel: { interval: 9, rotate: 0 },
    },
    yAxis: [
      {
        type: "value",
        name: "电影数",
        splitLine: { lineStyle: { color: "rgba(255,255,255,0.06)" } },
      },
      {
        type: "value",
        name: "均分",
        min: 0,
        max: 10,
        splitLine: { show: false },
      },
    ],
    series: [
      {
        type: "bar",
        data: data.map((d) => d.count),
        itemStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: "#90cea1" },
            { offset: 1, color: "#0d253f" },
          ]),
          borderRadius: [3, 3, 0, 0],
        },
        barMaxWidth: 20,
      },
      {
        type: "line",
        yAxisIndex: 1,
        data: data.map((d) => d.avg_rating),
        smooth: true,
        symbol: "none",
        lineStyle: { color: "#f9ca24", width: 2 },
        itemStyle: { color: "#f9ca24" },
      },
    ],
    grid: { top: 20, right: 50, bottom: 40, left: 50 },
    legend: {
      data: ["电影数", "均分"],
      bottom: 0,
      textStyle: { color: "#aaa" },
    },
  });
}

// ---------------------------------------------------------------------------
// 数据加载
// ---------------------------------------------------------------------------
async function loadStats() {
  loading.value = true;
  try {
    const res = await fetchStats();
    stats.value = res.data.data;
    // 必须先结束 loading，让 v-else 分支渲染出图表 DOM，再初始化 ECharts
    loading.value = false;
    await nextTick();
    initCharts();
  } catch {
    loading.value = false;
    // 错误提示由 axios 拦截器统一处理
  }
}

function initCharts() {
  if (!stats.value) return;

  // 销毁旧图表
  [
    ratingChart, genreChart, yearChart, sourceChart,
    budgetRevChart, runtimeChart, countryChart, ratingPopChart,
  ].forEach((c) => c?.dispose());

  ratingChart = makeChart(ratingChartRef.value);
  genreChart = makeChart(genreChartRef.value);
  yearChart = makeChart(yearChartRef.value);
  sourceChart = makeChart(sourceChartRef.value);
  budgetRevChart = makeChart(budgetRevChartRef.value);
  runtimeChart = makeChart(runtimeChartRef.value);
  countryChart = makeChart(countryChartRef.value);
  ratingPopChart = makeChart(ratingPopChartRef.value);

  buildGenreChart(stats.value.genre_distribution);
  buildYearChart(stats.value.yearly_trend);
  buildRatingChart(stats.value.rating_distribution);
  buildSourceChart(stats.value.source_distribution);
  buildBudgetRevenueChart(stats.value.budget_revenue);
  buildRuntimeChart(stats.value.runtime_distribution);
  buildCountryChart(stats.value.country_top15);
  buildRatingPopularityChart(stats.value.rating_popularity);
}

function handleResize() {
  ratingChart?.resize();
  genreChart?.resize();
  yearChart?.resize();
  sourceChart?.resize();
  budgetRevChart?.resize();
  runtimeChart?.resize();
  countryChart?.resize();
  ratingPopChart?.resize();
}

// ---------------------------------------------------------------------------
// 生命周期
// ---------------------------------------------------------------------------
onMounted(() => {
  loadStats();
  window.addEventListener("resize", handleResize);
});

onBeforeUnmount(() => {
  window.removeEventListener("resize", handleResize);
  [
    ratingChart, genreChart, yearChart, sourceChart,
    budgetRevChart, runtimeChart, countryChart, ratingPopChart,
  ].forEach((c) => c?.dispose());
});
</script>

<style scoped>
.dashboard-page {
  max-width: 1400px;
  margin: 0 auto;
}

.page-title {
  font-size: 22px;
  font-weight: 700;
  margin-bottom: 24px;
}

/* 统计卡片 */
.stat-cards {
  display: flex;
  gap: 20px;
  margin-bottom: 24px;
}

.stat-card {
  background: #fff;
  border-radius: 10px;
  padding: 24px 32px;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.06);
  text-align: center;
  min-width: 160px;
}

.stat-value {
  font-size: 36px;
  font-weight: 800;
  color: var(--tmdb-dark-blue);
}

.stat-label {
  font-size: 13px;
  color: #999;
  margin-top: 4px;
}

.stat-card--tmdb {
  border-top: 3px solid #01b4e4;
}

.stat-card--douban {
  border-top: 3px solid #21d07a;
}

/* 图表网格 */
.charts-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
}

.chart-card {
  background: #1a1a2e;
  border-radius: 10px;
  overflow: hidden;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
}

.chart-card--wide {
  grid-column: 1 / -1;
}

.chart-header {
  padding: 14px 20px;
  font-size: 15px;
  font-weight: 600;
  color: #ddd;
  border-bottom: 1px solid rgba(255, 255, 255, 0.08);
}

.chart-body {
  width: 100%;
  height: 360px;
}
</style>
