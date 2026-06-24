<template>
  <div class="page">
    <div class="topbar">
      <h1 class="title">技术文章</h1>

      <router-link class="adminLink" to="/admin">管理员入口</router-link>

      <div class="filters">
        <label class="filterItem">
          <span>分类</span>
          <select v-model="category" @change="onFilterChange">
            <option value="">全部</option>
            <option v-for="c in categories" :key="c.id" :value="c.id">
              {{ c.name }}
            </option>
          </select>
        </label>

        <!-- 归档下拉框 -->
        <label class="filterItem">
          <span>归档</span>
          <select v-model="yearMonth" @change="onArchiveChange">
            <option value="">全部时间</option>
            <option v-for="ym in archiveList" :key="ym" :value="ym">
              {{ ym }}
            </option>
          </select>
        </label>

        <!-- 搜索框 -->
        <div class="searchBox">
          <input
            type="text"
            v-model="keyword"
            placeholder="搜索文章..."
            @keyup.enter="onSearch"
          />
          <button @click="onSearch">搜索</button>
          <button v-if="keyword" @click="clearSearch" class="clearBtn">清除</button>
        </div>
      </div>
    </div>

    <div v-if="loading" class="loading">加载中…</div>

    <div v-else>
      <div v-if="items.length === 0" class="empty">
        {{ keyword ? '没有找到相关文章' : '暂无文章' }}
      </div>

      <div v-else class="list">
        <article v-for="a in items" :key="a.id" class="card">
          <div v-if="a.cover_image_url" class="coverWrap">
            <img class="cover" :src="a.cover_image_url" :alt="a.title" />
          </div>

          <div class="content">
            <router-link class="cardTitle" :to="`/article/${a.id}`">
              {{ a.title }}
            </router-link>

            <p v-if="a.summary" class="summary">{{ a.summary }}</p>

            <div class="meta">
              <span class="metaItem">
                发布时间：{{ formatDate(a.published_at) }}
              </span>
            </div>

            <div v-if="parseTags(a.tags).length" class="tags">
              <span v-for="t in parseTags(a.tags)" :key="t" class="tag">
                {{ t }}
              </span>
            </div>
          </div>
        </article>
      </div>

      <div class="pager">
        <button class="btn" :disabled="page <= 1" @click="prevPage">上一页</button>
        <span class="pageInfo">
          第 {{ page }} 页 / 共 {{ totalPages }} 页（{{ total }} 篇）
        </span>
        <button class="btn" :disabled="page >= totalPages" @click="nextPage">下一页</button>
      </div>
    </div>

    <p v-if="errorMsg" class="error">{{ errorMsg }}</p>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from "vue";
import api from "../../api";

const loading = ref(false);
const errorMsg = ref("");

const items = ref([]);
const total = ref(0);

const page = ref(1);
const pageSize = ref(10);
const category = ref("");
const categories = ref([]);
const keyword = ref("");
const yearMonth = ref("");
const archiveList = ref([]);

const totalPages = computed(() => Math.max(1, Math.ceil(total.value / pageSize.value)));

// 获取分类列表
const fetchCategories = async () => {
  try {
    const res = await api.get("/categories");
    if (res.code === 0) {
      categories.value = res.data || [];
    }
  } catch (e) {
    console.error("获取分类失败:", e);
  }
};

// 获取归档列表
const fetchArchiveList = async () => {
  try {
    const res = await api.get("/articles/archives");
    if (res.code === 0) {
      archiveList.value = res.data || [];
    }
  } catch (e) {
    console.error("获取归档列表失败:", e);
    // 如果后端没有归档接口，从前端数据中提取
    extractArchiveFromArticles();
  }
};

// 从当前文章列表中提取年月
const extractArchiveFromArticles = () => {
  const years = new Set();
  items.value.forEach(article => {
    if (article.published_at) {
      const date = new Date(article.published_at);
      const ym = `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}`;
      years.add(ym);
    }
  });
  archiveList.value = Array.from(years).sort().reverse();
};

const fetchList = async () => {
  loading.value = true;
  errorMsg.value = "";
  try {
    const params = {
      page: page.value,
      page_size: pageSize.value
    };
    if (category.value) params.category = category.value;
    if (keyword.value) params.search = keyword.value;
    if (yearMonth.value) params.year_month = yearMonth.value;

    const res = await api.get("/articles", { params });
    if (res.code !== 0) throw new Error(res.message || "加载失败");

    items.value = res.data.items || [];
    total.value = res.data.total || 0;

    // 提取归档列表
    extractArchiveFromArticles();
  } catch (e) {
    errorMsg.value = e?.message || String(e);
    items.value = [];
    total.value = 0;
  } finally {
    loading.value = false;
  }
};

// 搜索
const onSearch = async () => {
  page.value = 1;
  await fetchList();
};

// 清除搜索
const clearSearch = async () => {
  keyword.value = "";
  page.value = 1;
  await fetchList();
};

// 分类筛选（同时清空搜索和归档）
const onFilterChange = async () => {
  page.value = 1;
  keyword.value = "";
  yearMonth.value = "";
  await fetchList();
};

// 归档筛选
const onArchiveChange = async () => {
  page.value = 1;
  await fetchList();
};

const prevPage = async () => {
  if (page.value <= 1) return;
  page.value -= 1;
  await fetchList();
};

const nextPage = async () => {
  if (page.value >= totalPages.value) return;
  page.value += 1;
  await fetchList();
};

const parseTags = (tags) => {
  if (!tags) return [];
  return String(tags)
    .split(",")
    .map((s) => s.trim())
    .filter(Boolean);
};

const formatDate = (iso) => {
  if (!iso) return "-";
  const d = new Date(iso);
  if (Number.isNaN(d.getTime())) return String(iso);
  const beijingTime = new Date(d.getTime() + 8 * 60 * 60 * 1000);
  return beijingTime.toLocaleString();
};

onMounted(() => {
  fetchCategories();
  fetchArchiveList();
  fetchList();
});
</script>

<style scoped>
.page {
  padding: 16px;
  max-width: 980px;
  margin: 0 auto;
}
.topbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  margin-bottom: 12px;
  flex-wrap: wrap;
}
.title {
  font-size: 22px;
  margin: 0;
}
.adminLink {
  padding: 8px 10px;
  border: 1px solid #ddd;
  border-radius: 8px;
  text-decoration: none;
  color: #111;
  font-size: 14px;
}
.adminLink:hover {
  border-color: #1f6feb;
  color: #1f6feb;
}
.filters {
  display: flex;
  gap: 10px;
  align-items: center;
  flex-wrap: wrap;
}
.filterItem {
  display: inline-flex;
  gap: 8px;
  align-items: center;
  font-size: 14px;
  color: #333;
}
select {
  padding: 8px 10px;
  border: 1px solid #ddd;
  border-radius: 8px;
  background: #fff;
}

/* 搜索框样式 */
.searchBox {
  display: flex;
  gap: 8px;
  align-items: center;
}
.searchBox input {
  padding: 8px 12px;
  border: 1px solid #ddd;
  border-radius: 8px;
  font-size: 14px;
  width: 200px;
}
.searchBox input:focus {
  outline: none;
  border-color: #1f6feb;
}
.searchBox button {
  padding: 8px 16px;
  border: 1px solid #ddd;
  border-radius: 8px;
  background: #fff;
  cursor: pointer;
  font-size: 14px;
}
.searchBox button:hover {
  background: #f0f0f0;
}
.clearBtn {
  color: #666;
}

.loading,
.empty {
  padding: 18px;
  border: 1px solid #eee;
  border-radius: 12px;
  color: #666;
  background: #fafafa;
}

.list {
  display: grid;
  gap: 12px;
}
.card {
  display: grid;
  grid-template-columns: 180px 1fr;
  gap: 12px;
  border: 1px solid #eee;
  border-radius: 12px;
  overflow: hidden;
  background: #fff;
}
.coverWrap {
  background: #f6f7fb;
}
.cover {
  width: 100%;
  height: 100%;
  object-fit: cover;
  display: block;
}
.content {
  padding: 12px 12px 14px;
}
.cardTitle {
  display: inline-block;
  font-size: 18px;
  font-weight: 700;
  color: #111;
  text-decoration: none;
  margin-bottom: 6px;
}
.cardTitle:hover {
  text-decoration: underline;
}
.summary {
  margin: 0 0 10px 0;
  color: #444;
  line-height: 1.6;
}
.meta {
  color: #666;
  font-size: 13px;
}
.tags {
  margin-top: 10px;
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}
.tag {
  font-size: 12px;
  padding: 2px 8px;
  border-radius: 999px;
  background: #f0f6ff;
  color: #1f6feb;
  border: 1px solid #dbeafe;
}

.pager {
  margin-top: 14px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12px;
}
.btn {
  padding: 8px 12px;
  border: 1px solid #ddd;
  border-radius: 8px;
  background: #fff;
  cursor: pointer;
}
.btn:disabled {
  cursor: not-allowed;
  opacity: 0.5;
}
.pageInfo {
  color: #444;
  font-size: 13px;
}

.error {
  margin-top: 12px;
  color: #c00;
}

@media (max-width: 720px) {
  .card {
    grid-template-columns: 1fr;
  }
  .coverWrap {
    height: 180px;
  }
  .searchBox input {
    width: 150px;
  }
}
</style>