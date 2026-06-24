<template>
  <div class="page">
    <div v-if="loading" class="loading">加载中…</div>

    <div v-else-if="errorMsg" class="errorBox">
      <p class="errorTitle">加载失败</p>
      <p class="errorMsg">{{ errorMsg }}</p>
      <button class="btn" @click="load">重试</button>
      <button class="btn" @click="goBack">返回列表</button>
    </div>

    <div v-else class="article">
      <h1 class="title">{{ article?.title }}</h1>

      <div class="meta">
        <span>发布时间：{{ formatDate(article?.published_at) }}</span>
        <span>阅读量：{{ article?.views || 0 }}</span>
      </div>

      <div v-if="parseTags(article?.tags).length" class="tags">
        <span v-for="t in parseTags(article?.tags)" :key="t" class="tag">{{ t }}</span>
      </div>

      <div class="content" v-html="renderedHtml"></div>

      <div class="footer">
        <button class="btn primary" @click="goBack">返回列表</button>
      </div>

      <CommentSection v-if="article" :article-id="article.id" />
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted, ref, watch } from "vue";
import { useRoute, useRouter } from "vue-router";
import MarkdownIt from "markdown-it";
import DOMPurify from "dompurify";
import hljs from "highlight.js";
import "highlight.js/styles/github-dark.css";

import api from "../../api";
import CommentSection from "../../components/CommentSection.vue";

const route = useRoute();
const router = useRouter();

const loading = ref(false);
const errorMsg = ref("");
const article = ref(null);

const md = new MarkdownIt({
  html: true,
  linkify: true,
  breaks: true,
  highlight: (str, lang) => {
    try {
      if (lang && hljs.getLanguage(lang)) {
        return `<pre class="hljs"><code>${hljs.highlight(str, {
          language: lang,
          ignoreIllegals: true
        }).value}</code></pre>`;
      }
      return `<pre class="hljs"><code>${hljs.highlightAuto(str).value}</code></pre>`;
    } catch (e) {
      return `<pre class="hljs"><code>${md.utils.escapeHtml(str)}</code></pre>`;
    }
  }
});

const articleId = computed(() => route.params.id);

const renderedHtml = computed(() => {
  const raw = article.value?.content_md || "";
  try {
    const unsafe = md.render(raw);
    return DOMPurify.sanitize(unsafe);
  } catch (e) {
    return "<p>Markdown 渲染失败</p>";
  }
});

const formatDate = (iso) => {
  if (!iso) return "-";
  const d = new Date(iso);
  if (isNaN(d.getTime())) return String(iso);
  const beijingTime = new Date(d.getTime() + 8 * 60 * 60 * 1000);
  return beijingTime.toLocaleString();
};

const parseTags = (tags) => {
  if (!tags) return [];
  return String(tags)
    .split(",")
    .map((s) => s.trim())
    .filter(Boolean);
};

const load = async () => {
  const id = articleId.value;
  if (!id) return;

  loading.value = true;
  errorMsg.value = "";
  article.value = null;
  try {
    const res = await api.get(`/articles/${id}`);
    if (res.code !== 0) throw new Error(res.message || "加载失败");
    article.value = res.data;
  } catch (e) {
    errorMsg.value = e?.message || String(e);
  } finally {
    loading.value = false;
  }
};

const goBack = () => {
  router.push({ name: "home" });
};

onMounted(load);
watch(articleId, load);
</script>

<style scoped>
.page {
  padding: 16px;
  max-width: 980px;
  margin: 0 auto;
}
.loading {
  padding: 18px;
  border: 1px solid #eee;
  border-radius: 12px;
  color: #666;
  background: #fafafa;
}
.errorBox {
  padding: 18px;
  border: 1px solid #ffd6d6;
  border-radius: 12px;
  background: #fff6f6;
}
.errorTitle {
  margin: 0 0 8px 0;
  font-weight: 700;
  color: #b30000;
}
.errorMsg {
  margin: 0 0 12px 0;
  color: #b30000;
}
.article .title {
  margin: 0 0 10px 0;
  font-size: 26px;
}
.meta {
  display: flex;
  gap: 14px;
  flex-wrap: wrap;
  color: #666;
  font-size: 13px;
  margin-bottom: 10px;
}
.tags {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-bottom: 14px;
}
.tag {
  font-size: 12px;
  padding: 2px 8px;
  border-radius: 999px;
  background: #f0f6ff;
  color: #1f6feb;
  border: 1px solid #dbeafe;
}
.content :deep(pre) {
  background: #0b1220;
  color: #fff;
  padding: 12px;
  border-radius: 10px;
  overflow: auto;
}
.content :deep(code) {
  font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", "Courier New",
    monospace;
}
.content :deep(img) {
  max-width: 100%;
}
.footer {
  margin-top: 18px;
}
.btn {
  padding: 8px 12px;
  border: 1px solid #ddd;
  border-radius: 8px;
  background: #fff;
  cursor: pointer;
  margin-right: 10px;
}
.primary {
  background: #1f6feb;
  border-color: #1f6feb;
  color: #fff;
}
</style>