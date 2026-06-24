<template>
  <div class="comment-manage">
    <div class="header">
      <h2>评论管理</h2>
      <div class="filters">
        <select v-model="statusFilter" @change="fetchComments">
          <option value="all">全部</option>
          <option value="visible">已显示</option>
          <option value="hidden">已隐藏</option>
        </select>
      </div>
    </div>

    <div v-if="loading" class="loading">加载中...</div>

    <div v-else-if="!comments || comments.length === 0" class="empty">
      <p>暂无评论</p>
    </div>

    <div v-else class="comment-list">
      <div v-for="comment in comments" :key="comment?.id" class="comment-card">
        <div class="comment-header">
          <div class="user-info">
            <span class="author">{{ comment?.author_name || '匿名' }}</span>
            <span class="email">{{ comment?.author_email || '无邮箱' }}</span>
          </div>
          <div class="status-badge" :class="comment?.status">
            {{ comment?.status === 'visible' ? '已显示' : '已隐藏' }}
          </div>
        </div>

        <div class="article-info">
          文章ID: {{ comment?.article_id }} | 发表于: {{ formatDate(comment?.created_at) }}
        </div>

        <div class="comment-content">{{ comment?.content }}</div>

        <div class="comment-actions">
          <button
            v-if="comment?.status === 'visible'"
            @click="toggleStatus(comment)"
            class="btn-hide"
          >
            隐藏
          </button>
          <button
            v-else
            @click="toggleStatus(comment)"
            class="btn-show"
          >
            显示
          </button>
          <button @click="deleteComment(comment)" class="btn-delete">删除</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import api from '../api'

const comments = ref([])
const loading = ref(false)
const statusFilter = ref('all')

const fetchComments = async () => {
  loading.value = true
  try {
    let url = '/comments/admin/all'
    if (statusFilter.value !== 'all') {
      url += `?status=${statusFilter.value}`
    }
    const res = await api.get(url)
    if (Array.isArray(res)) {
      comments.value = res.filter(c => c && c.id)
    } else {
      comments.value = []
    }
    console.log('加载评论数量:', comments.value.length)
  } catch (error) {
    console.error('获取评论失败：', error)
    alert('获取评论失败: ' + (error.response?.data?.detail || error.message))
  } finally {
    loading.value = false
  }
}

const toggleStatus = async (comment) => {
  if (!comment || !comment.id) return
  try {
    await api.post(`/comments/admin/${comment.id}/toggle-status`)
    comment.status = comment.status === 'visible' ? 'hidden' : 'visible'
    alert(`评论已${comment.status === 'visible' ? '显示' : '隐藏'}`)
  } catch (error) {
    console.error('切换状态失败：', error)
    alert('操作失败')
  }
}

const deleteComment = async (comment) => {
  if (!comment || !comment.id) return
  if (!confirm('确定要删除这条评论吗？')) return

  try {
    await api.delete(`/comments/admin/${comment.id}`)
    comments.value = comments.value.filter(c => c && c.id !== comment.id)
    alert('删除成功')
  } catch (error) {
    console.error('删除失败：', error)
    alert('删除失败')
  }
}

// 格式化日期（转换为北京时间 UTC+8）
const formatDate = (date) => {
  if (!date) return '-'
  const d = new Date(date)
  // 加上8小时转为北京时间
  const beijingTime = new Date(d.getTime() + 8 * 60 * 60 * 1000)
  return beijingTime.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit'
  })
}

onMounted(() => {
  fetchComments()
})
</script>

<style scoped>
.comment-manage {
  padding: 20px;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  flex-wrap: wrap;
  gap: 16px;
}

.header h2 {
  margin: 0;
}

.filters select {
  padding: 8px 12px;
  border: 1px solid #ddd;
  border-radius: 8px;
  font-size: 14px;
}

.loading, .empty {
  text-align: center;
  padding: 60px;
  color: #666;
}

.comment-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.comment-card {
  background: #fff;
  border: 1px solid #eee;
  border-radius: 12px;
  padding: 16px;
}

.comment-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
  flex-wrap: wrap;
  gap: 8px;
}

.user-info {
  display: flex;
  gap: 12px;
  align-items: center;
}

.author {
  font-weight: 600;
  color: #2c3e50;
}

.email {
  font-size: 12px;
  color: #999;
}

.status-badge {
  font-size: 12px;
  padding: 2px 8px;
  border-radius: 999px;
}

.status-badge.visible {
  background: #e8f5e9;
  color: #2e7d32;
}

.status-badge.hidden {
  background: #ffebee;
  color: #c62828;
}

.article-info {
  font-size: 12px;
  color: #666;
  margin-bottom: 12px;
}

.comment-content {
  background: #f8f9fa;
  padding: 12px;
  border-radius: 8px;
  margin-bottom: 12px;
  line-height: 1.6;
}

.comment-actions {
  display: flex;
  gap: 12px;
}

.comment-actions button {
  padding: 6px 12px;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 13px;
}

.btn-hide {
  background: #ff9800;
  color: white;
}

.btn-show {
  background: #4caf50;
  color: white;
}

.btn-delete {
  background: #f44336;
  color: white;
}
</style>
