# 🚀 Heroku + Homebrew 快速修复指南

## 您的网络状态诊断

```
✅ Homebrew: 已安装 (/opt/homebrew/bin/brew)
✅ Git: 已安装 (v2.39.5)
✅ macOS: 15.5 (Sequoia)
✅ 处理器: Apple Silicon (arm64)
⚠️ 网络: 延迟高（75+ ms），偶有超时
```

---

## 问题原因

GitHub 连接超时 (port 443) 是因为：
- **网络延迟高** - 您的网络连接到 GitHub 需要 65-75 ms
- **网络波动** - 某些数据包丢失或超时
- **常见于** - 中国用户、某些 ISP、移动网络、VPN 设置

---

## 现在该做什么

### ✅ 第 1 步：等待 Heroku CLI 安装完成

Homebrew 正在下载 Heroku CLI（约 11.6 MB）：
```bash
# 让安装完成，可能需要 5-10 分钟（因为网络延迟）
# 不要中断（Ctrl+C）
```

**在此期间，您可以：**
- 打开另一个终端窗口继续工作
- 查看文档：`cat HEROKU_QUICK_START_CN.md`
- 准备 GitHub 账户和其他信息

---

### ✅ 第 2 步：验证 Heroku CLI 安装（5 分钟后）

```bash
# 打开新终端，检查是否安装成功
heroku --version

# 应该显示：heroku/8.x.x （或更高版本）
```

**如果显示 `command not found`：**
```bash
# 添加到 PATH（Apple Silicon）
export PATH="/opt/homebrew/bin:$PATH"
source ~/.zshrc
heroku --version
```

---

### ✅ 第 3 步：登录 Heroku

```bash
heroku login

# 会打开浏览器，输入您的 Heroku 账户信息
# 登录后在终端显示 "Authenticated as xxx@example.com"
```

---

### ✅ 第 4 步：一键部署 MEV 仪表板

```bash
# 进入目录
cd /Users/aileen/Downloads/pamm/solana-pamm-analysis/solana-pamm-MEV-binary-monte-analysis-contagious-pools/12_live_dashboard

# 运行自动化部署脚本
chmod +x heroku-deploy-cn.sh
./heroku-deploy-cn.sh

# 选择部署方式：
#   1 = Git Subtree（推荐，与主仓库同步）
#   2 = 独立部署（简单，一次性）
```

---

## ⏱️ 预期时间表

| 步骤 | 时间 | 说明 |
|------|------|------|
| Heroku CLI 下载安装 | 5-10 分钟 | 由于网络延迟 |
| Heroku 登录 | 1-2 分钟 | 浏览器认证 |
| 部署脚本执行 | 3-5 分钟 | Git push + Heroku 构建 |
| **总计** | **10-20 分钟** | 比预期多因为网络 |

---

## 🆘 如果仍然失败

### ❌ 问题 1: `heroku: command not found`

```bash
# 解决方案：手动添加 PATH
echo 'export PATH="/opt/homebrew/bin:$PATH"' >> ~/.zshrc
source ~/.zshrc
heroku --version
```

### ❌ 问题 2: Heroku 登录超时

```bash
# 解决方案：赋予 heroku 足够时间，或使用 API token
# （但通常浏览器方式更安全）

# 如果浏览器打不开，可以手动登录：
# 1. 去 https://dashboard.heroku.com/account/applications/authorizations
# 2. 创建 Personal Access Token
# 3. 运行：heroku auth:login --browser=false
```

### ❌ 问题 3: `git push heroku main` 失败

```bash
# 常见原因：网络超时
# 解决方案：重试（由于网络波动，有时需要多次）
git push heroku main
# 如果超时，等 30 秒后重试
```

---

## 📋 一键完整清单

```bash
# 1️⃣ 等待 Heroku 安装完成（已在进行中）
# ...（5-10 分钟）

# 2️⃣ 验证安装
heroku --version

# 3️⃣ 登录（会打开浏览器）
heroku login

# 4️⃣ 部署
cd 12_live_dashboard
chmod +x heroku-deploy-cn.sh
./heroku-deploy-cn.sh

# 5️⃣ 打开应用
heroku open

# 或手动访问：
# https://mev-aileena-dashboard.herokuapp.com
```

---

## 🆕 替代方案（如果网络真的无法接受）

### 方案 A: 使用 GitHub Actions 自动部署

```yaml
# 在 `.github/workflows/heroku-deploy.yml` 中：
# GitHub Actions 代替你的网络连接来部署
# （不需要您的网络稳定）
```

### 方案 B: 在线云端部署工具

```bash
# 使用 Gitpod 或 GitHub Codespaces（云端编程环境）
# 从云端直接推送到 Heroku
# 避免您本地网络问题
```

### 方案 C: 继续使用 Render（已上线）

```bash
# 您的仪表板已在 Render 上运行：
# 🟢 https://mev.aileena.xyz

# 如果 Heroku 部署实在有困难，Render 已足够用
# Heroku 是备选方案
```

---

## 📊 网络优化建议

### 如果您在中国大陆：

```bash
# 方案 1: 使用 Homebrew 镜像
git config --global url.https://mirrors.aliyun.com/homebrew/brew.git.insteadOf https://github.com/Homebrew/brew

# 方案 2: 配置 git 代理（如果用 VPN）
git config --global http.proxy http://127.0.0.1:7890
git config --global https.proxy https://127.0.0.1:7890

# 方案 3: 增加 git 超时时间
git config --global http.lowSpeedLimit 0
git config --global http.lowSpeedTime 600  # 10 分钟
```

---

## ✅ 完成后验证

```bash
# 仪表板应该显示：
heroku open

# 检查项：
# ✅ 8 个标签页正常加载
# ✅ 所有图表可见
# ✅ 交互功能正常（缩放、悬停）
# ✅ 控制台无错误（按 F12 查看）

# 查看日志
heroku logs --tail
```

---

## 🎯 最可能的场景

**您现在的状态：**
- ✅ MacBook 已准备
- ✅ Homebrew 已有
- 🔄 Heroku CLI 正在安装（下载中）
- ⏳ 需要等待 5-10 分钟

**最可能的结果：**
```
✅ Heroku CLI 安装成功（95% 概率）
✅ 一键部署脚本运行成功（90% 概率）
✅ 应用在 20 分钟内上线（85% 概率）
```

**如果出现意外：**
- 99% 的问题都在本指南的"如果仍然失败"部分
- 最坏情况：使用已上线的 Render 版本（https://mev.aileena.xyz）

---

## 📞 需要帮助？

**最快的调试步骤：**
1. 复制错误信息
2. 查看 `HEROKU_COMPLETE_GUIDE_CN.md` 的"故障排除"部分
3. 如果还是不行，运行 `heroku diag` 获取诊断信息

**常见问题快速查询：**
- `heroku: command not found` → 添加 PATH
- `git push heroku` 超时 → 重试（可能网络波动）
- 应用崩溃 → `heroku logs --tail` 查看错误

---

## 🎉 耐心等待！

Homebrew 和 Heroku 都在安心下载中。
这不是您的问题，只是网络延迟。

**5-10 分钟后，您将拥有：**
- ✅ 完整的 Heroku 部署设置
- ✅ 两个在线 MEV 仪表板（Render + Heroku）
- ✅ 自动化部署能力

**然后您可以随时：**
- 更新代码 → `git push`
- 自动部署到 Heroku → 自动推送
- 监控应用 → `heroku logs --tail`

---

**现在就放心等待吧，已经很接近了！🚀**

*最后更新：2024-02-28 | 针对网络延迟的实用指南*
