<template>
  <div class="page">
    <div class="card">
      <h2>后台登录</h2>
      <form @submit.prevent="onSubmit">
        <label>
          用户名
          <input v-model="username" autocomplete="username" placeholder="请输入用户名" />
        </label>
        <label>
          密码
          <input v-model="password" type="password" autocomplete="current-password" placeholder="请输入密码" />
        </label>
        <button type="submit" :disabled="loading">登录</button>
        <p v-if="errorMsg" class="error">{{ errorMsg }}</p>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref } from "vue";
import { useRoute, useRouter } from "vue-router";
import { useAuthStore } from "../stores/auth";

const username = ref("");
const password = ref("");
const errorMsg = ref("");
const loading = ref(false);

const auth = useAuthStore();
const router = useRouter();
const route = useRoute();

const onSubmit = async () => {
  errorMsg.value = "";
  loading.value = true;

  try {
    await auth.login(username.value, password.value);
    const redirect = route.query.redirect || "/admin/articles";
    await router.replace(redirect);
  } catch (err) {
    errorMsg.value = err?.message || "登录失败";
  } finally {
    loading.value = false;
  }
};
</script>

<style scoped>
.page {
  min-height: 100vh;
  display: grid;
  place-items: center;
  background: #f6f7fb;
}
.card {
  width: 360px;
  background: white;
  border: 1px solid #eee;
  border-radius: 12px;
  padding: 20px;
}
h2 {
  margin-bottom: 20px;
}
label {
  display: block;
  margin: 12px 0;
}
input {
  width: 100%;
  padding: 10px;
  border: 1px solid #ddd;
  border-radius: 8px;
  margin-top: 6px;
}
button {
  width: 100%;
  padding: 10px;
  border-radius: 8px;
  border: none;
  background: #1f6feb;
  color: white;
  cursor: pointer;
  margin-top: 12px;
}
button:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}
.error {
  color: #c00;
  margin-top: 10px;
}
</style>