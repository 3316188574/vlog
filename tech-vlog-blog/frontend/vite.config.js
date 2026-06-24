import { defineConfig } from "vite";
import vue from "@vitejs/plugin-vue";

export default defineConfig({
  plugins: [vue()],
  server: {
    proxy: {
      "/api": {
        target: "http://127.0.0.1:8000",
        // target: "https://xxxx-xxxx-xxxx.loca.lt",  // 外网穿透时用这个（注释掉）
        changeOrigin: true
      }
    }
  }
});

