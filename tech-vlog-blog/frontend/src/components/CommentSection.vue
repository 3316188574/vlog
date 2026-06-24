<template>
  <div class="comment-section">
    <div class="comment-header">
      <h3>评论 <span v-if="commentCount > 0">({{ commentCount }})</span></h3>
    </div>

    <!-- 评论列表 - 添加安全检查 -->
    <div v-if="comments && comments.length > 0" class="comment-list">
      <div v-for="comment in comments" :key="comment.id" class="comment-item">
        <div class="comment-avatar">
          <div class="avatar-placeholder">
            {{ comment.author_name.charAt(0).toUpperCase() }}
          </div>
        </div>
        <div class="comment-body">
          <div class="comment-meta">
            <span class="author-name">{{ comment.author_name }}</span>
            <span class="comment-time">{{ formatDate(comment.created_at) }}</span>
          </div>
          <div class="comment-content">{{ comment.content }}</div>
          <div class="comment-footer">
            <button @click="likeComment(comment)" class="btn-like" :class="{ liked: comment.user_liked }">
              👍 {{ comment.like_count || 0 }}
            </button>
          </div>
        </div>
      </div>
    </div>

    <div v-else class="no-comments">
      <p>🤔 暂无评论，来说两句吧~</p>
    </div>

    <div class="comment-form-wrapper">
      <h4>发表评论</h4>
      <form @submit.prevent="submitComment" class="comment-form">
        <div class="form-row">
          <div class="form-group">
            <input
              v-model="form.author_name"
              type="text"
              placeholder="昵称 *"
              required
              :disabled="submitting"
            >
          </div>
          <div class="form-group">
            <input
              v-model="form.author_email"
              type="email"
              placeholder="邮箱（可选）"
              :disabled="submitting"
            >
          </div>
        </div>
        <div class="form-group">
          <textarea
            v-model="form.content"
            placeholder="写下你的评论... *"
            rows="4"
            required
            :disabled="submitting"
          ></textarea>
        </div>
        <div class="form-actions">
          <button type="submit" :disabled="submitting" class="btn-submit">
            <span v-if="submitting">提交中...</span>
            <span v-else>提交评论</span>
          </button>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import api from '../api'

const props = defineProps({
  articleId: {
    type: Number,
    required: true
  }
})

const comments = ref([])
const commentCount = ref(0)
const submitting = ref(false)
const form = ref({
  author_name: '',
  author_email: '',
  content: ''
})

// 获取评论列表
const fetchComments = async () => {
  try {
    const response = await api.get(`/comments/article/${props.articleId}`)
    comments.value = Array.isArray(response) ? response : []

    for (const comment of comments.value) {
      try {
        const likeRes = await api.get(`/comments/${comment.id}/like-count`)
        comment.like_count = likeRes.like_count || 0
        comment.user_liked = false
      } catch (e) {
        comment.like_count = 0
        comment.user_liked = false
      }
    }
  } catch (error) {
    console.error('获取评论失败：', error)
    comments.value = []
  }
}

// 获取评论数量
const fetchCommentCount = async () => {
  try {
    const response = await api.get(`/comments/article/${props.articleId}/count`)
    commentCount.value = response?.count || 0
  } catch (error) {
    console.error('获取评论数量失败：', error)
    commentCount.value = 0
  }
}

// 提交评论
const submitComment = async () => {
  if (!form.value.author_name.trim()) {
    alert('请输入昵称')
    return
  }
  if (!form.value.content.trim()) {
    alert('请输入评论内容')
    return
  }

  submitting.value = true
  try {
    await api.post('/comments/', {
      article_id: props.articleId,
      author_name: form.value.author_name.trim(),
      author_email: form.value.author_email.trim() || null,
      content: form.value.content.trim()
    })

    form.value = {
      author_name: '',
      author_email: '',
      content: ''
    }

    await Promise.all([fetchComments(), fetchCommentCount()])
    alert('评论提交成功！')
  } catch (error) {
    console.error('提交评论失败：', error)
    alert(error.response?.data?.detail || '提交失败，请重试')
  } finally {
    submitting.value = false
  }
}

// 点赞评论
const likeComment = async (comment) => {
  try {
    const res = await api.post(`/comments/${comment.id}/like`)
    comment.like_count = res.like_count || 0
    comment.user_liked = res.liked || false
  } catch (error) {
    console.error('点赞失败：', error)
  }
}

// 格式化日期（强制转换为北京时间 UTC+8）
const formatDate = (date) => {
  if (!date) return '刚刚'

  // 将 UTC 时间加上8小时转为北京时间
  const d = new Date(date)
  const beijingTime = new Date(d.getTime() + 8 * 60 * 60 * 1000)
  const now = new Date()

  const diff = now - beijingTime

  const minutes = Math.floor(diff / 60000)
  const hours = Math.floor(diff / 3600000)
  const days = Math.floor(diff / 86400000)

  if (minutes < 1) return '刚刚'
  if (minutes < 60) return `${minutes}分钟前`
  if (hours < 24) return `${hours}小时前`
  if (days < 7) return `${days}天前`

  // 超过7天显示具体日期时间
  const year = beijingTime.getFullYear()
  const month = String(beijingTime.getMonth() + 1).padStart(2, '0')
  const day = String(beijingTime.getDate()).padStart(2, '0')
  const hour = String(beijingTime.getHours()).padStart(2, '0')
  const minute = String(beijingTime.getMinutes()).padStart(2, '0')

  return `${year}-${month}-${day} ${hour}:${minute}`
}

onMounted(() => {
  fetchComments()
  fetchCommentCount()
})
</script>

<style scoped>
.comment-section {
  margin-top: 48px;
  padding-top: 32px;
  border-top: 1px solid #eaecef;
}

.comment-header h3 {
  font-size: 20px;
  font-weight: 600;
  color: #2c3e50;
  margin-bottom: 24px;
}

.comment-list {
  margin-bottom: 32px;
}

.comment-item {
  display: flex;
  gap: 16px;
  padding: 20px 0;
  border-bottom: 1px solid #f0f0f0;
}

.comment-avatar {
  flex-shrink: 0;
}

.avatar-placeholder {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 600;
  font-size: 18px;
}

.comment-body {
  flex: 1;
}

.comment-meta {
  margin-bottom: 8px;
}

.author-name {
  font-weight: 600;
  color: #2c3e50;
  margin-right: 12px;
}

.comment-time {
  font-size: 12px;
  color: #99a2ad;
}

.comment-content {
  color: #4a5568;
  line-height: 1.6;
  word-break: break-word;
}

.comment-footer {
  margin-top: 8px;
}

.btn-like {
  background: none;
  border: none;
  font-size: 13px;
  cursor: pointer;
  padding: 4px 10px;
  border-radius: 20px;
  transition: all 0.3s;
  color: #666;
}

.btn-like:hover {
  background: #f0f0f0;
}

.btn-like.liked {
  color: #42b983;
}

.no-comments {
  text-align: center;
  padding: 48px 20px;
  background: #f8f9fa;
  border-radius: 12px;
  margin-bottom: 32px;
}

.comment-form-wrapper {
  background: #f8f9fa;
  padding: 24px;
  border-radius: 12px;
}

.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
  margin-bottom: 16px;
}

.form-group {
  display: flex;
  flex-direction: column;
}

.form-group input,
.form-group textarea {
  padding: 12px;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  font-size: 14px;
  font-family: inherit;
}

.form-group input:focus,
.form-group textarea:focus {
  outline: none;
  border-color: #42b983;
}

.form-actions {
  display: flex;
  justify-content: flex-end;
  margin-top: 16px;
}

.btn-submit {
  background: #42b983;
  color: white;
  border: none;
  padding: 10px 24px;
  border-radius: 8px;
  cursor: pointer;
}

.btn-submit:disabled {
  background: #ccc;
}
</style>