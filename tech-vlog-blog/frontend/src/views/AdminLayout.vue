<template>
  <div class="layout">
    <header class="header">
      <div>后台管理</div>
      <div class="actions">
        <button @click="goHome">前台</button>
        <button @click="onLogout">退出</button>
      </div>
    </header>
    <div class="body">
      <aside class="aside">
        <router-link class="nav" to="/admin/articles">文章管理</router-link>
        <router-link class="nav" to="/admin/comments">评论管理</router-link>
      </aside>
      <main class="main">
        <router-view />
      </main>
    </div>
  </div>
</template>

<script setup>
import { useRouter } from "vue-router";
import { useAuthStore } from "../stores/auth";

const router = useRouter();
const auth = useAuthStore();

const onLogout = () => {
  auth.logout();
  router.push('/admin');
};

const goHome = () => router.push({ name: "home" });
</script>

<style scoped>
.layout {
  min-height: 100vh;
}
.header {
  height: 56px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 16px;
  background: #0b1220;
  color: #fff;
}
.actions button {
  margin-left: 8px;
}
.body {
  display: grid;
  grid-template-columns: 180px 1fr;
  min-height: calc(100vh - 56px);
}
.aside {
  border-right: 1px solid #eee;
  padding: 12px;
}
.nav {
  display: block;
  padding: 10px 12px;
  border-radius: 8px;
  color: #111;
  text-decoration: none;
}
.nav.router-link-active {
  background: #f0f6ff;
  color: #1f6feb;
}
.main {
  padding: 16px;
}
</style>