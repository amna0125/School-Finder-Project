import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

// DuckDB-WASM ships its own workers and .wasm files; Vite serves them as static assets.
export default defineConfig({
  plugins: [react()],
  base: "./",
  optimizeDeps: { exclude: ["@duckdb/duckdb-wasm", "maplibre-gl"] },
  server: { port: 5173 },
  worker: { format: "es" },
  build: { chunkSizeWarningLimit: 2000 },
});
