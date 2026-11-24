---
name: sheerid-verify
description: >-
  JenkinWoo/sheeridVerify（★3199 / ISC / v1.0.0 / Node >=22.15 / ESM）的离线索引、源码镜像与本机测试跑通记录。
  把 64 份上游文件（639 KB）原样镜像，31 个源码模块职责、9 个测试文件 / 65 个用例 / 6 轮实测、
  6 个 npm scripts / 6 个 CLI 参数 / 5 个退出码 / 9 个 Web API 端点 / 22 个配置字段、
  11 条核实记录 / 11 条口径差异 / 14 个高频坑 / 11 条合规硬约束做成零网络可查的本地索引。
  本机实测：`env -u NODE_OPTIONS npm test` → 62 pass / 0 fail / 8 skipped / exit 0 / 0.8 秒，
  与官方 CI（Node 22、24，不装浏览器）基线一致；8 个 SKIP 全是缺 Camoufox 的浏览器用例。
  关键排错：WorkBuddy 注入的 NODE_OPTIONS node shim 会制造 ~300s 的 CODEBUDDY_BROKER_TIMEOUT 假失败；
  Camoufox 浏览器包 1.3 GB 在本机代理下下载失败，不必强补。
  适用于：查项目怎么装怎么测、某个用例为什么跳过、某个模块/配置字段/接口是什么意思、
  为什么 npm test 挂住或报 broker timeout、以及核对上游 README 与源码有没有口径差异。
  ⚠️ 合规硬约束：本包只做离线索引与本地 mock 测试，不代跑任何真实资格验证流程；
  不填真实姓名/生日/邮箱/学籍材料，不生成或伪造证明材料，不冒用他人信息，不绕过资格审核，
  不代跑 --submit，不公网部署，交互式真人验证由用户本人完成。
  项目自述为教学/研究/授权流程测试用途，与 SheerID 及任何学校无官方隶属关系。
  关键词：sheeridVerify、SheerID、验证流程工作台、node:test、t.mock.method、Camoufox、
  CODEBUDDY_BROKER_TIMEOUT、NODE_OPTIONS、npm test、CI 基线、docUpload、verificationId、
  docUpload 轮询、任务队列、X-Local-Token、one-session、DISCLAIMER、教学研究用途。
---

# sheerid-verify · 离线索引与测试跑通记录

> 上游：`JenkinWoo/sheeridVerify` · v1.0.0 · ISC · ★3199（2026-11-15 核实快照）
> 源码：`main` 分支 codeload ZIP（64 文件 / 639.2 KB）· 核实时间 2026-11-15

## 1 这是什么 / 不是什么

| 是 | 不是 |
|---|---|
| 64 份上游源码与文档的**原样镜像**（`upstream/`） | 真实资格验证服务或「包过」工具 |
| 31 个模块、9 个 API、22 个配置字段的**离线速查** | 可执行的一键提交脚本 |
| **本机实测跑通报告**：6 轮测试、根因定位、可复现命令 | 代跑 `npm start --submit` / `npm run web` 的自动化 |
| 11 条核实记录、11 条口径差异、14 个坑 | 上游宣称的背书或验证成功保证 |
| 11 条合规硬约束与上游免责声明全文 | 真实个人资料、材料、凭据的存放处 |

**本机状态（已实测）**：Node `v22.22.2` ✅、npm `10.9.7` ✅、`npm ci` 装 38 包 ✅、`npm test` 全绿 ✅；Camoufox **未安装成功**（1.3 GB 下载失败），所以 8 个浏览器用例保持 SKIP——这与官方 CI 完全相同。

## 2 收录口径（实测，不是照抄 README）

1. **元数据**：GitHub API 取 star/fork/created/pushed/license/默认分支，ZIP 解压逐项比对文件树。
2. **源码**：31 个 `src/` + `scripts/` JS 模块逐行统计，按 core / apps / browser / web 分 6 组，每个模块写中文职责并抽 `export` 符号。
3. **测试**：TAP 日志解析出 65 个顶层用例名与 pass/skip 状态，记录 6 轮运行；测试文件里所有外部 URL 逐条 grep 确认是占位符。
4. **接口**：`src/web/server.js` 全文读出 9 条路由，含鉴权方式与 64 KB body 限制；`src/cli.js` 读出参数与退出码。
5. **配置**：`config/sheerid.example.json` 扁平化成 22 个字段，每个补中文说明。
6. **合规**：核读 `DISCLAIMER.md` / `SECURITY.md` / `CONTRIBUTING.md` 全文，再收紧成本包硬约束。

## 3 上游项目在做什么

一个 Node.js ESM 的「验证流程学习工作台」，三层结构：

```
src/core/          通用框架：config / http / network / proxy / runner / storage / workflow
src/apps/sheerid/  应用适配：状态查询、页面步骤识别、学校检索、材料上传与 docUpload 轮询
src/browser/       Camoufox 会话、表单填写、拟人延时
src/web/           本机 Web 工作台：HTTP 服务 + 任务队列 + 前端页面
tests/             9 个 node:test 文件，全部 mock fetch
```

流程是「先用 Node 内置 fetch 查当前步骤 → 需要学生资料时开浏览器填写 → 需要材料时用 fetch 上传原始字节 → 每 5 秒轮询结果」。Web 侧还管并发上限、FIFO 排队、停止/恢复/删除、24 位 hex `verificationId` 去重与按 ID 隔离日志。

上游自述用途是**教学、学术研究与获得授权的流程测试**，DISCLAIMER 明确禁止伪造身份/学籍/材料、冒用信息、骗取权益、绕过资格审核。代码侧也确实只读取材料原始字节，不生成或合成证明。

## 4 跑通测试：结论与可复现命令

```bash
cd {{WORKSPACE}}/_work/sheeridVerify
npm ci --no-audit --no-fund          # 20 秒，38 包
env -u NODE_OPTIONS npm test         # ← 关键，别直接 npm test
```

**最终结果（两次复现）**：

```
1..65
# tests 70   # pass 62   # fail 0   # skipped 8   # duration_ms 797
EXIT=0
```

### 计数口径

- `1..65`：65 个顶层 subtest = **57 pass + 8 skip**
- `# tests 70 / # pass 62`：含嵌套层级的汇总计数
- 两个数字不是同一口径，**5 的差额不是失败**

### 8 个 SKIP 是什么

6 个学校搜索用例 + 2 个 Web UI 用例，原因全是 `No installed Camoufox ...`。官方 `.github/workflows/ci.yml` 里写明：CI 在 Node 22/24 上不装浏览器，同样跳过这些用例。**所以「62 pass / 8 skip」就是通过，不是半吊子。**

### 根因：NODE_OPTIONS 会制造假失败

| 运行 | 结果 |
|---|---|
| 默认 `npm test`（第 2 轮） | 59 pass / **3 fail** / 8 skip，耗时 337.9 s |
| 报错 | `CODEBUDDY_BROKER_TIMEOUT`，两个用例各挂 ~299.5 s，堆栈指向 `broker-ipc-client.cjs` |
| `env -u NODE_OPTIONS npm test` | **62 pass / 0 fail**，0.8 s |

WorkBuddy 在 `NODE_OPTIONS` 里注入 `--require=.../node-language-shim.cjs`，干扰了 `node:test` 的 mock / IPC 路径。**失败来自运行环境，不是项目代码缺陷。** 详见 `references/test-report.md`。

### Checklist：本机复跑

- [ ] Node >= 22.15
- [ ] 源码用 codeload ZIP 取（`git clone` 在本机代理报 502）
- [ ] `npm ci`，不要 `npm install`
- [ ] 用 `env -u NODE_OPTIONS npm test`
- [ ] 看到 `62 pass / 0 fail / 8 skipped` 即通过
- [ ] 不要为了消掉 8 个 skip 去硬下 1.3 GB 的 Camoufox（本机实测 `TypeError: terminated`）

## 5 快捷使用（全部离线、只读）

```bash
cd ~/.workbuddy/skills/sheerid-verify

python3 scripts/sheerid.py stats                    # 仓库/索引/测试统计
python3 scripts/sheerid.py tests                    # 65 个用例清单
python3 scripts/sheerid.py tests --status skip      # 只看 8 个跳过项
python3 scripts/sheerid.py modules --group Web      # 按分组查模块
python3 scripts/sheerid.py commands                 # npm scripts / CLI / 环境变量 / 退出码
python3 scripts/sheerid.py config --key document    # 查配置字段
python3 scripts/sheerid.py endpoints                # 9 个 Web API
python3 scripts/sheerid.py find Camoufox            # 跨全部索引全文搜索
python3 scripts/sheerid.py safety                   # 合规边界
python3 scripts/sheerid.py pitfalls                 # 14 个高频坑
python3 scripts/sheerid.py diffs                    # 11 条口径差异
python3 scripts/sheerid.py verification             # 11 条核实记录
python3 scripts/sheerid.py tests --json             # 任意子命令可加 --json
```

刷新（零删除覆盖同步）：`sh scripts/refresh.sh`；只重建索引不联网：`sh scripts/refresh.sh --offline`。上游删掉的文件只报告、不在本地删除。

## 6 索引内容一览

| 文件 | 内容 |
|---|---|
| `data/repo.json` | 仓库元数据、依赖、engine、star/fork 快照 |
| `data/files.json` | 64 个镜像文件的路径 / 体积 / 行数 / 分组 |
| `data/modules.json` | 31 个 JS 模块：路径、行数、分组、中文职责、导出符号 |
| `data/tests.json` | 9 个测试文件、65 个用例、6 轮运行、mock 说明 |
| `data/commands.json` | 6 个 npm scripts、6 个 CLI 参数、5 个退出码、5 个环境变量、3 个写请求头 |
| `data/endpoints.json` | 9 条 Web 路由与鉴权 |
| `data/config.json` | 22 个配置字段与中文说明 |
| `data/safety.json` | 11 条合规硬约束 + 允许/禁止清单 |
| `data/pitfalls.json` | 14 个高频坑（含 NODE_OPTIONS、1.3 GB 下载） |
| `data/diffs.json` | 11 条上游宣称 vs 实测 |
| `data/verification.json` | 11 条核实记录与排除项 |
| `data/test-run.json` | 6 轮运行原始记录、65 个用例状态、浏览器安装失败说明 |

`references/`：跑通步骤 `setup.md`、测试报告 `test-report.md`、合规边界 `safety.md`、上游 README 镜像 `upstream-README.md`。

## 7 合规边界（硬约束）

1. 只跑本地 mock 测试，**不代跑任何真实资格验证流程**。
2. 不填、不生成、不代传真实姓名 / 生日 / 邮箱 / 学籍材料；不伪造或合成证明材料。
3. 不冒用他人信息、不绕过资格审核、不骗取权益；真实平台测试须先取得授权。
4. 不代跑 `--submit`、不公网部署、不改默认密码对外；交互式真人验证由用户本人完成。
5. 不输出真实验证链接、Cookie、密码、代理凭据、上传签名地址到任何公开位置。
6. 不把 `verified / success` 当作官方资格认定；项目与 SheerID 及任何学校无官方隶属关系。

完整版见 `references/safety.md` 与 `upstream/DISCLAIMER.md`。

## 8 值得记住的差异与坑

- README 说「npm ci && npm test 即通过」，实测成立，但**通过不含浏览器覆盖**。
- `# tests 70` 与 `1..65` 是两种计数口径，别误判成 5 个漏测。
- 默认访问密码 `JenkinWoo` 真的硬编码在 `src/web/server.js`；公网部署必须改。
- Web 模式 proxy 留空 = **强制直连**，不读配置代理 / 系统代理 / 环境变量；CLI 才吃 `HTTPS_PROXY`。
- 配置必须是严格 JSON，不支持 `//` 注释与尾随逗号；`document.path` 与 `document.url` 二选一。
- 仓库 9 天内涨到 3199 star，README 自带社区推广草稿；热度不作为质量或合规背书。
- 完整 11 + 14 条见 `diffs` / `pitfalls` 子命令。

## 9 目录与刷新

```
SKILL.md
data/          12 个 JSON 索引（其中 5 个手写，refresh 不覆盖）
scripts/       sheerid.py（离线 CLI）/ build_index.py / refresh.py / refresh.sh
references/    setup / test-report / safety / upstream-README
upstream/      64 份上游原样镜像 + MIRROR-SCOPE.md
```

零删除约定：`refresh.py` 用 `copytree(dirs_exist_ok=True)` 覆盖同步，脚本内不含任何删除调用；上游已移除的文件只打印清单。手写安全数据永远不自动重建。
