import axios from "axios";

const api = axios.create({
  baseURL: "/api",
  timeout: 15000
});

// 请求拦截器：自动添加 token
api.interceptors.request.use((config) => {
  const token = localStorage.getItem("access_token");
  if (token) {
    config.headers = config.headers || {};
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// 响应拦截器：统一处理响应
api.interceptors.response.use(
  (resp) => resp.data,
  (err) => {
    console.error("API Error:", err);
    return Promise.reject(err);
  }
);

export default api;