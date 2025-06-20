#!/usr/bin/env node

import fs from "fs";
import path from "path";
import { homedir } from "os";

// Configuration paths
const CONFIG_DIR = path.join(homedir(), ".codex");
const CONFIG_FILE = path.join(CONFIG_DIR, "config.json");

// Ensure config directory exists
if (!fs.existsSync(CONFIG_DIR)) {
  fs.mkdirSync(CONFIG_DIR, { recursive: true });
}

// Local middleware configuration
const localConfig = {
  model: "gpt-4", // The model name LM Studio is configured to use
  provider: "local",
  approvalMode: "suggest",
  notify: false,
  disableResponseStorage: false,
  providers: {
    local: {
      name: "Local Middleware",
      baseURL: "http://localhost:1234/v1",
      envKey: "LOCAL_API_KEY",
    },
  },
};

// Load existing config if it exists
let existingConfig = {};
if (fs.existsSync(CONFIG_FILE)) {
  try {
    const configContent = fs.readFileSync(CONFIG_FILE, "utf8");
    existingConfig = JSON.parse(configContent);
    console.log("📄 Found existing config, merging with local settings...");
  } catch (error) {
    console.log(
      "⚠️  Could not parse existing config, creating fresh config...",
    );
  }
}

// Merge configurations
const mergedConfig = { ...existingConfig, ...localConfig };

// Write the configuration
fs.writeFileSync(CONFIG_FILE, JSON.stringify(mergedConfig, null, 2));

console.log("✅ Codex CLI configured for local middleware!");
console.log("📋 Configuration saved to:", CONFIG_FILE);
console.log("");
console.log("🚀 Quick Start:");
console.log(
  "1. Make sure your middleware is running: cd ../task-manager-client && uv run openai_middleware.py ../task-manager-server/task-manager.py",
);
console.log('2. Set the API key: export LOCAL_API_KEY="dummy-key-for-local"');
console.log('3. Test the CLI: pnpm build && ./dist/cli.js "get current tasks"');
console.log("");
console.log("🔧 Configuration:");
console.log("- Provider:", mergedConfig.provider);
console.log("- Model:", mergedConfig.model);
console.log("- Base URL:", mergedConfig.providers.local.baseURL);
