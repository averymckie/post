import { defineConfig } from "vite";

// Preview only. The generated artifacts themselves have no server dependency.
export default defineConfig({
  root: "proofs/out/augmentation",
  server: { host: "0.0.0.0", port: 4173, strictPort: true, allowedHosts: ["terminal.local"] },
  plugins: [{
    name: "workbench-entry",
    configureServer(server) {
      server.middlewares.use((req, _res, next) => {
        if (req.url === "/") req.url = "/workbench.html";
        next();
      });
    },
  }],
});
