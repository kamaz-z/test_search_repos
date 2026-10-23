import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

// В Docker бекенд доступний за іменем сервісу "backend", локально за 127.0.0.1
const apiTarget = process.env.VITE_API_PROXY_TARGET || "http://127.0.0.1:8000";

export default defineConfig({
  plugins: [react()],
  server: {
    host: true, // слухати всі інтерфейси, потрібно для Docker
    proxy: {
      "/api": apiTarget,
    },
  },
});