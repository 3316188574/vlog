<template>
  <div class="page">
    <h2>文章详情（占位）</h2>
    <p>文章 ID：{{ id }}</p>
    <button @click="load">请求 /api/articles/{{ id }}</button>
    <pre v-if="resp">{{ resp }}</pre>
  </div>
</template>
<template>
  <div class="page">
    <!-- 加载状态 -->
    <div v-if="loading" class="loading">
      <div class="loading-spinner"></div>
      <p>加载中...</p>
    </div>

    <!-- 错误状态 -->
    <div v-else-if="error" class="error">
      <p>{{ error }}</p>
      <button @click="loadArticle" class="btn-retry">重试</button>
    </div>

    <!-- 文章内容 -->
    <article v-else-if="article" class="article-container">
      <div class="article-header">
        <h1 class="article-title">{{ article.title }}</h1>
        <div class="article-meta">
          <span>📅 {{ formatDate(article.created_at) }}</span>
          <span v-if="article.tags">🏷️ {{ article.tags }}</span>
          <span>👁️ {{ article.views || 0 }} 阅读</span>
        </div>
      </div>

      <div class="article-content" v-html="renderedContent"></div>

      <div class="article-footer">
        <button @click="goBack" class="btn-back">← 返回列表</button>
      </div>

      <!-- 评论组件 -->
      <CommentSection :article-id="article.id" />
    </article>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import api from '../../api'
import MarkdownIt from 'markdown-it'
import CommentSection from '../../components/CommentSection.vue'

const route = useRoute()
const router = useRouter()
const article = ref(null)
const loading = ref(false)
const error = ref(null)

const md = new MarkdownIt({
  html: true,
  linkify: true,
  typographer: true
})

const renderedContent = computed(() => {
  return article.value ? md.render(article.value.content || '') : ''
})

const formatDate = (date) => {
  if (!date) return ''
  return new Date(date).toLocaleDateString('zh-CN')
}

const goBack = () => {
  router.push('/')
}

const loadArticle = async () => {
  const id = route.params.id
  if (!id) return

  loading.value = true
  error.value = null

  try {
    const res = await api.get(`/articles/${id}`)
    article.value = res
  } catch (e) {
    console.error('获取文章失败：', e)
    error.value = e.response?.data?.message || '加载文章失败，请重试'
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  loadArticle()
})
</script>

<style scoped>
.page {
  max-width: 900px;
  margin: 0 auto;
  padding: 24px 20px;
}

.loading {
  text-align: center;
  padding: 60px 20px;
}

.loading-spinner {
  width: 40px;
  height: 40px;
  margin: 0 auto 16px;
  border: 3px solid #e2e8f0;
  border-top-color: #42b983;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.error {
  text-align: center;
  padding: 60px 20px;
  color: #e74c3c;
}

.btn-retry {
  background: #42b983;
  color: white;
  border: none;
  padding: 8px 20px;
  border-radius: 6px;
  cursor: pointer;
  margin-top: 16px;
}

.btn-retry:hover {
  background: #359268;
}

.article-container {
  background: white;
  border-radius: 12px;
  overflow: hidden;
}

.article-header {
  margin-bottom: 28px;
  padding-bottom: 20px;
  border-bottom: 1px solid #eaecef;
}

.article-title {
  font-size: 32px;
  font-weight: 700;
  color: #2c3e50;
  margin-bottom: 16px;
  line-height: 1.3;
}

.article-meta {
  display: flex;
  gap: 20px;
  font-size: 14px;
  color: #7f8c8d;
  flex-wrap: wrap;
}

.article-content {
  font-size: 16px;
  line-height: 1.8;
  color: #2c3e50;
}

.article-content :deep(h2) {
  margin-top: 32px;
  margin-bottom: 16px;
  padding-bottom: 8px;
  border-bottom: 1px solid #eaecef;
}

.article-content :deep(h3) {
  margin-top: 24px;
  margin-bottom: 12px;
}

.article-content :deep(p) {
  margin-bottom: 16px;
}

.article-content :deep(img) {
  max-width: 100%;
  border-radius: 8px;
  margin: 20px 0;
}

.article-content :deep(pre) {
  background: #282c34;
  color: #abb2bf;
  padding: 16px;
  border-radius: 8px;
  overflow-x: auto;
  margin: 20px 0;
}

.article-content :deep(code) {
  font-family: 'Fira Code', monospace;
  font-size: 14px;
}

.article-content :deep(blockquote) {
  border-left: 4px solid #42b983;
  padding-left: 20px;
  margin: 20px 0;
  color: #6a737d;
}

.article-footer {
  margin-top: 40px;
  padding-top: 24px;
  border-top: 1px solid #eaecef;
}

.btn-back {
  background: none;
  border: 1px solid #ddd;
  padding: 8px 20px;
  border-radius: 6px;
  cursor: pointer;
  font-size: 14px;
  transition: all 0.3s;
}

.btn-back:hover {
  background: #f5f5f5;
  border-color: #42b983;
}
</style>
<script setup>
import { computed, ref } from "vue";
import { useRoute } from "vue-router";
import api from "../api";

const route = useRoute();
const id = computed(() => route.params.id);
const resp = ref("");

const load = async () => {
  resp.value = "";
  try {
    const res = await api.get(`/articles/${id.value}`);
    resp.value = JSON.stringify(res, null, 2);
  } catch (e) {
    resp.value = String(e);
  }
};
</script>

<style scoped>
.page {
  padding: 16px;
}
pre {
  margin-top: 12px;
  background: #0b1220;
  color: #fff;
  padding: 12px;
  border-radius: 8px;
  overflow: auto;
}
</style>

