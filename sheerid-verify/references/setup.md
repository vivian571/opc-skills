# 本机跑通测试：可复现步骤

> 2026-11-15 在 macOS（Apple M4）/ Node v22.22.2 / npm 10.9.7 实测。全程只跑本地 mock 测试，不连接任何真实验证接口。

## 1 取源码（本环境必须走 ZIP）

```bash
mkdir -p {{WORKSPACE}}/_work
cd {{WORKSPACE}}/_work
curl -sL --retry 3 -o sheeridVerify.zip \
  https://codeload.github.com/JenkinWoo/sheeridVerify/zip/refs/heads/main
unzip -q -o sheeridVerify.zip
mv sheeridVerify-main sheeridVerify
cd sheeridVerify
```

`git clone` 在本机代理下会报 `CONNECT tunnel failed, response 502`，别在它上面耗时间。ZIP 约 419 KB，64 个文件。

## 2 装依赖

```bash
npm ci --no-audit --no-fund     # 20 秒，38 个包
```

不要顺手 `npm install` 改 lockfile。Node 必须 >= 22.15，因为测试脚本用了 `--experimental-test-module-mocks`。

## 3 跑测试（关键：去掉 NODE_OPTIONS）

```bash
env -u NODE_OPTIONS npm test
```

预期输出：

```
1..65
# tests 70
# pass 62
# fail 0
# skipped 8
# duration_ms 797
```

退出码 0。**62 pass / 0 fail / 8 skipped 就是官方 CI 基线**（`.github/workflows/ci.yml` 在 Node 22/24 上明确不装浏览器）。

### 为什么必须 `env -u NODE_OPTIONS`

WorkBuddy 会在 `NODE_OPTIONS` 里注入 `--require=.../node-language-shim.cjs`。这个 shim 会拦截 node:test 的部分 mock/IPC 路径，导致个别用例各挂 ~299.5 秒并报 `CODEBUDDY_BROKER_TIMEOUT`，最终出现 3 个假失败、整轮耗时 337 秒。去掉注入后同一套测试 0.8 秒全绿——**失败是运行环境造成的，不是项目代码缺陷**。

直接用 `npm test`（不带 `env -u`）有时也能过（第一次 24.2 秒通过），但不稳定。要可复现就固定用上面的命令。

## 4 可选：补齐 8 个浏览器用例

```bash
env -u NODE_OPTIONS npm run browser:install   # 从 GitHub releases 下载 Camoufox
env -u NODE_OPTIONS npm test
```

未装成功时这 8 个用例会明确 `# SKIP No installed Camoufox ...`。

**本机 2026-11-15 实测：装不上。** Camoufox 浏览器包 **1.3 GB**，本机代理下只下到 3.59 MB，进度条显示 ETA 4h45m，最终 `TypeError: terminated`（退出码 1），缓存目录 `~/Library/Caches/camoufox` 仍为 0 B。示例配置 `browser.headless=false` 另外还需要可用桌面。因此本机保持官方 CI 基线（62 pass / 8 skip），不必强行补浏览器覆盖；要跑满请在带宽/代理稳定的环境里先把浏览器装好。

## 5 不做的操作

- 不执行 `npm start -- --submit` / `npm run submit` / `npm run web`（会连真实平台或起工作台）。
- 不创建 `config/sheerid.local.json`、不填真实姓名/生日/邮箱/学校/材料。
- 不做公网部署、不改默认密码对外。
- 交互式的真人验证只能由用户本人完成。

需要真实平台测试时，先自行取得平台与数据主体授权，再看 `upstream/DISCLAIMER.md`、`SECURITY.md`、`CONTRIBUTING.md` 全文。
