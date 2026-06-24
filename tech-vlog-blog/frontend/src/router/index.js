import { createRouter, createWebHistory } from "vue-router";
import { useAuthStore } from "../stores/auth";

import ArticleList from "../views/front/ArticleList.vue";
import ArticleDetail from "../views/front/ArticleDetail.vue";
import LoginView from "../views/LoginView.vue";
import AdminLayout from "../views/AdminLayout.vue";
import ArticleManage from "../views/ArticleManage.vue";
import CommentManage from "../views/CommentManage.vue";

const router = createRouter({
  history: createWebHistory(),
  routes: [
    // ===== 前台 =====
    { path: "/", name: "home", component: ArticleList },
    {
      path: "/article/:id",
      name: "articleDetail",
      component: ArticleDetail,
      alias: ["/articles/:id"]
    },

    // ===== 后台登录 =====
    { path: "/admin", name: "adminLogin", component: LoginView, alias: ["/login"] },

    // ===== 后台（需登录）=====
    {
      path: "/admin/articles",
      component: AdminLayout,
      meta: { requiresAuth: true },
      children: [{ path: "", name: "adminArticles", component: ArticleManage }]
    },
    // ✅ 添加评论管理路由
    {
      path: "/admin/comments",
      component: AdminLayout,
      meta: { requiresAuth: true },
      children: [{ path: "", name: "adminComments", component: CommentManage }]
    }
  ]
});

router.beforeEach((to) => {
  const needAuth = to.matched.some((r) => r.meta.requiresAuth);
  if (!needAuth) return true;
  const auth = useAuthStore();
  if (auth.isAuthed) return true;
  return { name: "adminLogin", query: { redirect: to.fullPath } };
});

export default router;