<template>
  <div class="page">
    <div class="toolbar">
      <h2>文章管理</h2>
      <div class="right">
        <select v-model="statusFilter" @change="load">
          <option value="">全部</option>
          <option value="draft">草稿</option>
          <option value="published">已发布</option>
        </select>
        <button @click="openCreate">新增文章</button>
      </div>
    </div>

    <div class="table">
      <div class="tr th">
        <div class="td id">ID</div>
        <div class="td title">标题</div>
        <div class="td status">状态</div>
        <div class="td time">更新时间</div>
        <div class="td ops">操作</div>
      </div>
      <div v-if="loading" class="empty">加载中…</div>
      <div v-else-if="items.length === 0" class="empty">暂无数据</div>
      <div v-else v-for="row in items" :key="row.id" class="tr">
        <div class="td id">{{ row.id }}</div>
        <div class="td title">{{ row.title }}</div>
        <div class="td status">
          <span :class="['pill', row.status]">{{ row.status }}</span>
        </div>
        <div class="td time">{{ row.updated_at || "-" }}</div>
        <div class="td ops">
          <button class="link" @click="openEdit(row)">编辑</button>
          <button class="link danger" @click="onDelete(row)">删除</button>
        </div>
      </div>
    </div>

    <!-- 弹窗：新增/编辑 -->
    <div v-if="modalOpen" class="modalMask" @click.self="closeModal">
      <div class="modal">
        <div class="modalHeader">
          <h3>{{ form.id ? "编辑文章" : "新增文章" }}</h3>
          <button class="x" @click="closeModal">×</button>
        </div>
        <div class="modalBody">
          <label>
            标题
            <input v-model="form.title" />
          </label>

          <label>
            摘要（可选）
            <input v-model="form.summary" />
          </label>

          <!-- 封面图上传 -->
          <label>
            封面图（可选）
            <div class="upload-area">
              <input
                type="file"
                accept="image/jpeg,image/png,image/gif,image/webp"
                @change="uploadCover"
                :disabled="uploading"
                ref="fileInput"
              />
              <div v-if="form.cover_image_url" class="cover-preview">
                <img :src="form.cover_image_url" alt="封面预览" />
                <button type="button" class="remove-cover" @click="removeCover">删除</button>
              </div>
              <div v-else class="upload-placeholder">
                <span>📷 点击选择图片</span>
                <small>支持 jpg、png、gif、webp，最大 5MB</small>
              </div>
            </div>
            <div v-if="uploading" class="uploading">上传中...</div>
          </label>

          <label>
            分类
            <select v-model="form.category_id">
              <option :value="null">无所属</option>
              <option v-for="c in categories" :key="c.id" :value="c.id">
                {{ c.name }}
              </option>
            </select>
          </label>

          <label>
            标签（逗号分隔，可选）
            <input v-model="form.tags" placeholder="例如：FastAPI,Vue,SQLite" />
          </label>

          <label>
            状态
            <select v-model="form.status">
              <option value="draft">draft（草稿）</option>
              <option value="published">published（已发布）</option>
            </select>
          </label>

          <label>
            内容（Markdown）
            <textarea v-model="form.content_md" rows="10" />
          </label>
        </div>
        <div class="modalFooter">
          <button @click="closeModal">取消</button>
          <button class="primary" @click="onSubmit" :disabled="saving">
            {{ saving ? "保存中…" : "保存" }}
          </button>
        </div>
        <p v-if="errorMsg" class="error">{{ errorMsg }}</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { onMounted, reactive, ref } from "vue";
import api from "../api";

const loading = ref(false);
const saving = ref(false);
const uploading = ref(false);
const errorMsg = ref("");
const fileInput = ref(null);

const items = ref([]);
const statusFilter = ref("");
const categories = ref([]);

const modalOpen = ref(false);
const form = reactive({
  id: null,
  title: "",
  summary: "",
  tags: "",
  status: "draft",
  content_md: "",
  category_id: null,
  cover_image_url: null
});

const resetForm = () => {
  form.id = null;
  form.title = "";
  form.summary = "";
  form.tags = "";
  form.status = "draft";
  form.content_md = "";
  form.category_id = null;
  form.cover_image_url = null;
};

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

const load = async () => {
  loading.value = true;
  errorMsg.value = "";
  try {
    const res = await api.get("/admin/articles", {
      params: statusFilter.value ? { status: statusFilter.value } : {}
    });
    if (res.code !== 0) throw new Error(res.message || "加载失败");
    items.value = res.data.items || [];
  } catch (e) {
    errorMsg.value = e?.message || String(e);
  } finally {
    loading.value = false;
  }
};

const openCreate = () => {
  resetForm();
  modalOpen.value = true;
};

const openEdit = (row) => {
  errorMsg.value = "";
  form.id = row.id;
  form.title = row.title || "";
  form.summary = row.summary || "";
  form.tags = row.tags || "";
  form.status = row.status || "draft";
  form.content_md = row.content_md || "";
  form.category_id = row.category_id || null;
  form.cover_image_url = row.cover_image_url || null;
  modalOpen.value = true;
};

const closeModal = () => {
  modalOpen.value = false;
};

// 上传封面图
const uploadCover = async (event) => {
  const file = event.target.files[0];
  if (!file) return;

  // 验证文件类型
  if (!file.type.startsWith('image/')) {
    alert('请选择图片文件');
    return;
  }

  // 验证文件大小（5MB）
  if (file.size > 5 * 1024 * 1024) {
    alert('文件不能超过 5MB');
    return;
  }

  const formData = new FormData();
  formData.append('file', file);

  uploading.value = true;
  try {
    const res = await api.post('/upload/image', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    });
    if (res.code === 0) {
      form.cover_image_url = res.data.url;
    } else {
      alert('上传失败: ' + res.message);
    }
  } catch (e) {
    console.error('上传失败:', e);
    alert('上传失败，请重试');
  } finally {
    uploading.value = false;
    // 清空 input，允许重新上传同一个文件
    if (fileInput.value) {
      fileInput.value.value = '';
    }
  }
};

// 删除封面图
const removeCover = () => {
  form.cover_image_url = null;
};

const onSubmit = async () => {
  if (!form.title.trim()) {
    errorMsg.value = "标题不能为空";
    return;
  }
  if (!form.content_md.trim()) {
    errorMsg.value = "内容不能为空";
    return;
  }

  saving.value = true;
  errorMsg.value = "";
  const payload = {
    title: form.title,
    summary: form.summary || null,
    tags: form.tags || null,
    status: form.status,
    content_md: form.content_md,
    cover_image_url: form.cover_image_url,
    category_id: form.category_id
  };

  try {
    const res = form.id
      ? await api.put(`/admin/articles/${form.id}`, payload)
      : await api.post("/admin/articles", payload);
    if (res.code !== 0) throw new Error(res.message || "保存失败");
    closeModal();
    await load();
  } catch (e) {
    errorMsg.value = e?.message || String(e);
  } finally {
    saving.value = false;
  }
};

const onDelete = async (row) => {
  const ok = window.confirm(`确认删除文章「${row.title}」？`);
  if (!ok) return;
  try {
    const res = await api.delete(`/admin/articles/${row.id}`);
    if (res.code !== 0) throw new Error(res.message || "删除失败");
    await load();
  } catch (e) {
    window.alert(e?.message || String(e));
  }
};

onMounted(() => {
  load();
  fetchCategories();
});
</script>

<style scoped>
.toolbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 12px;
}
.toolbar .right {
  display: flex;
  gap: 8px;
  align-items: center;
}
.table {
  border: 1px solid #eee;
  border-radius: 12px;
  overflow: hidden;
}
.tr {
  display: grid;
  grid-template-columns: 80px 1fr 120px 200px 160px;
  border-top: 1px solid #f0f0f0;
}
.tr.th {
  background: #fafafa;
  border-top: none;
  font-weight: 600;
}
.td {
  padding: 10px 12px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.empty {
  padding: 16px;
  color: #666;
}
.pill {
  display: inline-block;
  padding: 2px 8px;
  border-radius: 999px;
  font-size: 12px;
  border: 1px solid #ddd;
}
.pill.draft {
  background: #fff7e6;
  border-color: #ffd591;
  color: #ad6800;
}
.pill.published {
  background: #f6ffed;
  border-color: #b7eb8f;
  color: #237804;
}
.link {
  background: transparent;
  border: none;
  cursor: pointer;
  color: #1f6feb;
  padding: 0;
  margin-right: 10px;
}
.link.danger {
  color: #c00;
}

.modalMask {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.4);
  display: grid;
  place-items: center;
  z-index: 1000;
}
.modal {
  width: min(720px, 92vw);
  background: white;
  border-radius: 12px;
  border: 1px solid #eee;
  padding: 14px;
  max-height: 80vh;
  overflow-y: auto;
}
.modalHeader {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 8px;
}
.x {
  border: none;
  background: transparent;
  font-size: 20px;
  cursor: pointer;
}
.modalBody label {
  display: block;
  margin: 10px 0;
}
.modalBody input,
.modalBody select,
.modalBody textarea {
  width: 100%;
  padding: 10px;
  border: 1px solid #ddd;
  border-radius: 8px;
  margin-top: 6px;
}

/* 图片上传样式 */
.upload-area {
  border: 2px dashed #ddd;
  border-radius: 8px;
  padding: 16px;
  text-align: center;
  cursor: pointer;
  transition: all 0.3s;
  margin-top: 6px;
}
.upload-area:hover {
  border-color: #1f6feb;
}
.upload-area input {
  display: none;
}
.upload-placeholder {
  display: flex;
  flex-direction: column;
  gap: 8px;
  color: #999;
}
.upload-placeholder span {
  font-size: 16px;
}
.upload-placeholder small {
  font-size: 12px;
}
.cover-preview {
  position: relative;
  display: inline-block;
}
.cover-preview img {
  max-width: 200px;
  max-height: 150px;
  border-radius: 8px;
  border: 1px solid #ddd;
}
.remove-cover {
  position: absolute;
  top: -10px;
  right: -10px;
  background: #f44336;
  color: white;
  border: none;
  border-radius: 50%;
  width: 24px;
  height: 24px;
  cursor: pointer;
  font-size: 12px;
}
.uploading {
  font-size: 12px;
  color: #1f6feb;
  margin-top: 4px;
}

.modalFooter {
  display: flex;
  justify-content: flex-end;
  gap: 8px;
  margin-top: 10px;
}
.primary {
  background: #1f6feb;
  color: white;
  border: none;
  border-radius: 8px;
  padding: 10px 14px;
  cursor: pointer;
}
.error {
  color: #c00;
  margin-top: 10px;
}
</style>