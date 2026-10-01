#!/usr/bin/env bash
set -euo pipefail
git init -q -b main
cat > package.json <<'JSON'
{ "name": "shop-api", "version": "1.0.0", "type": "module",
  "scripts": { "test": "node --test" } }
JSON
mkdir -p src test
cat > src/server.js <<'JS'
import http from "node:http";

export function handler(req, res) {
  if (req.url === "/products") {
    res.writeHead(200, { "content-type": "application/json" });
    return res.end(JSON.stringify([{ id: 1, name: "Lamp" }]));
  }
  res.writeHead(404);
  res.end();
}

export const server = http.createServer(handler);
JS
cat > test/server.test.js <<'JS'
import { test } from "node:test";
import assert from "node:assert/strict";
import { handler } from "../src/server.js";

test("GET /products returns the catalog", () => {
  let status, body;
  const res = { writeHead: (s) => (status = s), end: (b) => (body = b) };
  handler({ url: "/products" }, res);
  assert.equal(status, 200);
  assert.equal(JSON.parse(body)[0].name, "Lamp");
});
JS
cat > CLAUDE.md <<'MD'
# shop-api

## SDD config
- Tracker: none
- PR base branch: develop
- Test command: npm test
MD
git add -A && git -c user.email=eval@example.com -c user.name=eval commit -qm "init"
