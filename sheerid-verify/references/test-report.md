# 测试跑通报告（2026-11-15）

## 结论

**`env -u NODE_OPTIONS npm test` → 退出码 0，`62 pass / 0 fail / 8 skipped`，耗时 797 ms。** 与官方 CI（Node 22 / 24 矩阵，不安装浏览器）基线完全一致。

计数口径说明：TAP 顶层 `1..65`（65 个 subtest = 57 pass + 8 skip），汇总区 `# tests 70 / # pass 62 / # skipped 8`（含嵌套层级）。两个数字不是同一口径，别把 5 的差额当成漏测或失败。

## 环境

| 项 | 值 |
|---|---|
| 源码 | codeload ZIP → `{{WORKSPACE}}/_work/sheeridVerify` |
| Node / npm | v22.22.2 / 10.9.7 |
| 依赖 | `npm ci --no-audit --no-fund` → 38 包 / 20 秒 / exit 0 |
| 测试命令 | `node --experimental-test-module-mocks --test` |
| 测试文件 | 9 个 `tests/*.test.js` + 1 个 `tests/fixtures/web-config.js` |

## 五次运行记录

| # | 命令 | 结果 | 耗时 | 判定 |
|---|---|---|---|---|
| 1 | `npm test`（默认环境） | 62 pass / 0 fail / 8 skip | 24.2 s | ✅ 通过 |
| 2 | 安装浏览器后 `npm test` | 59 pass / **3 fail** / 8 skip | 337.9 s | ❌ 环境干扰 |
| 3 | 顺序重跑（无并发） | 1/65 处被 SIGTERM | — | ⚠️ 未完成 |
| 4 | 沙箱外 `--test-concurrency=1` | 51/65 处被 SIGTERM | — | ⚠️ 未完成 |
| 5 | `env -u NODE_OPTIONS npm test` | **62 pass / 0 fail / 8 skip** | **0.8 s** | ✅ 最终结论 |
| 6 | 浏览器安装失败后再次 `env -u NODE_OPTIONS npm test` | **62 pass / 0 fail / 8 skip** | 0.78 s | ✅ 复现确认 |

第 2 轮的 3 个假失败：两个用例各挂约 299.5 秒，报错 `CODEBUDDY_BROKER_TIMEOUT`，堆栈指向 WorkBuddy 的 `broker-ipc-client.cjs`；另 1 个是嵌套 subtest 连带失败。根因是 `NODE_OPTIONS` 注入的 `node-language-shim.cjs` 干扰了 `node:test` 的 mock / IPC 路径。**去掉注入后同一份代码 0.8 秒全绿，不是项目缺陷。**

## 8 个跳过用例（设计如此，非失败）

| 分组 | 用例 | 原因 |
|---|---|---|
| 学校搜索 ×6 | stale school results refresh… / matching school results… / school retry is bounded… / a busy school search… / a user-edited search… / search is not retriggered… | `No installed Camoufox browser for local fixtures` |
| Web UI ×2 | Web UI deletes failed jobs… / Web UI queues multiple IDs… | `No installed Camoufox for local UI fixture` |

官方 CI 注释原文：`Browser tests are skipped without a locally installed Camoufox. Run npm run browser:install and npm test locally for browser coverage.`

**补齐尝试失败（本机）**：`env -u NODE_OPTIONS npm run browser:install` 从 GitHub releases 拉 **1.3 GB** 的 Camoufox 包，代理下只到 3.59 MB、ETA 4h45m，最终 `TypeError: terminated`（exit 1），`~/Library/Caches/camoufox` 为 0 B。因此这 8 项在本机保持 SKIP，判定仍是「通过」。

## 测试覆盖分布（65 个顶层用例）

- `document-continuation` / `document-polling` / `document-source`：材料续传、docUpload 轮询、复审与「响应丢失不重放」等 22 个
- `status-query`：初始分流重试、429 无 Retry-After、停止时取消等待等 5 个
- `school-search`：6 个（全部 SKIP）
- `web` / `web-queue` / `web-public` / `web-ui`：鉴权、并发 FIFO、去重、停止/恢复/删除、409 冲突、日志归属等 32 个（其中 2 个 SKIP）

完整用例名与状态见 `data/tests.json`：`python3 scripts/sheerid.py tests --status skip` 可只列跳过项。

## 安全性核实

`tests/` 里出现的 `my.sheerid.com`、`services.sheerid.com` 全是 `aaaaaaaa…` / `example.com` / `127.0.0.1` 占位符，配合 `t.mock.method(globalThis, 'fetch')` 全量替换网络层；本地起的是临时 HTTP fixture。**没有向任何真实验证接口提交数据，也没有使用任何真实个人或学校资料。**
