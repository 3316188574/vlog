import { defineStore } from "pinia";
import api from "../api";

export const useAuthStore = defineStore("auth", {
  state: () => ({
    token: localStorage.getItem("access_token") || ""
  }),
  getters: {
    isAuthed: (state) => !!state.token
  },
  actions: {
    async login(username, password) {
      const formData = new URLSearchParams();
      formData.append("username", username);
      formData.append("password", password);

      const res = await api.post("/auth/login", formData, {
        headers: { "Content-Type": "application/x-www-form-urlencoded" }
      });

      if (res.code !== 0) throw new Error(res.message || "登录失败");

      this.token = res.data.access_token;
      localStorage.setItem("access_token", this.token);
    },
    logout() {
      this.token = "";
      localStorage.removeItem("access_token");
    }
  }
});