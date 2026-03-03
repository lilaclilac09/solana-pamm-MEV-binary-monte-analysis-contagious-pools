# Heroku 完整部署指南 - MEV 仪表板

**基于您的 GitHub 仓库:** https://github.com/lilaclilac09/solana-pamm-MEV-binary-monte-analysis-contagious-pools

---

##  前置条件检查

您的项目已完全准备好部署：

-  `mev_dashboard.py` - 已配置 `server = app.server`（用于部署）
-  `requirements.txt` - 包含所有依赖：dash、plotly、pandas、gunicorn
-  `Procfile` - 已配置：`web: gunicorn mev_dashboard:server`
-  `runtime.txt` - 指定 Python 3.12（与 numpy 1.26 兼容）
-  GitHub 仓库 - 代码已提交

---

##  Heroku 部署步骤

### 第1步：安装 Heroku CLI

#### macOS（推荐用 Homebrew）：
```bash
brew install heroku
```

#### 或直接下载：
https://devcenter.heroku.com/articles/heroku-cli

验证安装：
```bash
heroku --version
```

---

### 第2步：Heroku 账户和登录

1. **创建账户**（如果没有）：https://www.heroku.com/
2. **登录**：
```bash
heroku login
# 打开浏览器进行身份验证
```

---

### 第3步：处理子目录问题（关键）

由于 `12_live_dashboard` 是子文件夹，不能直接从主仓库推送。有两种方法：

#### 方法 A：使用 Git Subtree（推荐 - 与原仓库保持同步）

```bash
# 1. 进入您的主仓库目录
cd /Users/aileen/Downloads/pamm/solana-pamm-analysis/solana-pamm-MEV-binary-monte-analysis-contagious-pools

# 2. 创建 Heroku app
heroku create mev-aileena-dashboard

# 3. 添加 Heroku remote（如果没自动添加）
heroku git:remote -a mev-aileena-dashboard

# 4. 使用 git subtree 推送子目录
git subtree push --prefix 12_live_dashboard heroku main
```

#### 方法 B：创建独立目录（简单 - 一次性部署）

```bash
# 1. 创建工作目录
mkdir ~/mev-heroku-deploy
cd ~/mev-heroku-deploy

# 2. 初始化 Git
git init

# 3. 复制 12_live_dashboard 的所有文件
cp -r /Users/aileen/Downloads/pamm/solana-pamm-analysis/solana-pamm-MEV-binary-monte-analysis-contagious-pools/12_live_dashboard/* .

# 4. 提交文件
git add .
git commit -m "Initial commit for Heroku deployment"

# 5. 创建 Heroku app
heroku create mev-aileena-dashboard

# 6. 推送到 Heroku
git push heroku main
```

**推荐选择方法 A**（git subtree）- 可与原仓库同步更新。

---

### 第4步：验证 Python 版本

确认 `runtime.txt` 已创建：

```bash
# 在 12_live_dashboard 文件夹中
cat runtime.txt
# 应该显示：python-3.12
```

如果没有：
```bash
echo "python-3.12" > runtime.txt
git add runtime.txt
git commit -m "Add Python runtime"
```

---

### 第5步：推送代码到 Heroku

```bash
# 如果使用方法 A（从主仓库）：
git subtree push --prefix 12_live_dashboard heroku main

# 如果使用方法 B（独立目录）：
git push heroku main
```

**监控构建过程**：
```bash
heroku logs --tail
```

日志应该显示：
```
-----> Building on the Heroku-20 stack
-----> Using buildpack: heroku/python
-----> Installing Python 3.12.x
-----> Installing dependencies...
       Collecting dash==4.0.0
       Collecting plotly==6.5.2
       ...
       Successfully installed gunicorn
-----> Compressing cache
-----> Launching...
       Released v1
       https://mev-aileena-dashboard.herokuapp.com released
```

---

### 第6步：自定义域名设置（mev.aileena.xyz）

#### 在 Heroku Dashboard 中添加域名：

1. 访问：https://dashboard.heroku.com/apps/mev-aileena-dashboard/settings
2. Domains 部分 → **Add Domain**
3. 输入：`mev.aileena.xyz`
4. Heroku 返回 DNS 目标（如 `mev-aileena-dashboard.herokuapp.com`）

#### 在您的 DNS 提供商（如 Cloudflare、Namecheap）中：

1. 登录 DNS 提供商
2. 找到 `aileena.xyz` 的 DNS 记录
3. 创建或更新 CNAME 记录：
   - **名称**：`mev`
   - **值**：Heroku 提供的目标（如 `mev-aileena-dashboard.herokuapp.com`）
   - **TTL**：自动或 3600

4. 保存

**SSL 证书**：Heroku 自动提供免费 SSL（HTTPS）

**验证域名**：5-60 分钟内生效，然后访问 https://mev.aileena.xyz

---

### 第7步：测试和启动

#### 临时 URL 测试：
```bash
heroku open
# 打开 https://mev-aileena-dashboard.herokuapp.com
```

#### 检查仪表板是否完全加载：
-  Tab 1：**概览** - 关键统计表格
-  Tab 2：**MEV 分布** - 3 个柱状图 + 1 个饼图
-  Tab 3：**顶级攻击者** - 柱状图 + 数据表
-  Tab 4：**传染网络** - 热力图 + 网络图
-  Tab 5：**验证者行为** - 柱状图
-  Tab 6：**Oracle 分析** - 2 个柱状图
-  Tab 7：**ML 模型** - 柱状图 + 表格
-  Tab 8：**关键发现** - 策略表格

#### 一旦域名生效，访问：
```
https://mev.aileena.xyz
```

#### 检查 dyno 状态：
```bash
heroku ps
# 应该显示：web.1 up
```

---

## ️ 环境变量（如果使用）

如果您的应用使用环境变量（来自 `.env.template`）：

```bash
# 在 Heroku Dashboard 或命令行添加
heroku config:set SOLANA_RPC_URL=https://api.mainnet-beta.solana.com
heroku config:set API_KEY=your_key_here

# 查看所有环境变量
heroku config
```

---

##  更新您的应用

每次修改代码后：

#### 方法 A（使用 git subtree）：
```bash
# 在主仓库中
cd /Users/aileen/Downloads/pamm/solana-pamm-analysis/solana-pamm-MEV-binary-monte-analysis-contagious-pools

# 修改代码
# ...编辑 12_live_dashboard/mev_dashboard.py

# 提交到主仓库
git add .
git commit -m "Update dashboard"
git push origin main

# 推送到 Heroku
git subtree push --prefix 12_live_dashboard heroku main
```

#### 方法 B（独立目录）：
```bash
cd ~/mev-heroku-deploy

# 修改代码
# ...编辑 mev_dashboard.py

# 提交并推送
git add .
git commit -m "Update dashboard"
git push heroku main
```

---

##  故障排除

### 构建失败

**错误：ModuleNotFoundError**
```
ModuleNotFoundError: No module named 'dash'
```

**解决方案**：
1. 确保 `requirements.txt` 包含所有依赖
2. 重新构建：
```bash
heroku apps:destroy mev-aileena-dashboard --confirm
heroku create mev-aileena-dashboard
git push heroku main
```

### dyno 休眠

**问题**：免费 dyno 30 分钟无活动后休眠，首次加载需 5-10 秒

**解决方案**：
1. 使用免费服务定期 ping：https://uptimerobot.com/
   - 每 5 分钟 ping 一次 `https://mev.aileena.xyz`
   
2. 升级到 Hobby dyno（$7/月）：
```bash
heroku ps:scale web=1:standard-1x
```

### Python 版本不兼容

**错误**：numpy 或其他包的兼容性问题

**解决方案**：
确保 `runtime.txt` 包含：
```
python-3.12
```

Heroku 会用最新的 3.12 patch（如 3.12.7）

---

##  部署架构比较

| 平台 | 状态 | URL | 优点 | 缺点 |
|------|------|-----|------|------|
| **Render** |  LIVE | mev.aileena.xyz | Auto-deploy、稳定 | 已部署 |
| **Heroku** |  新部署 | mev-aileena.herokuapp.com | 免费、易用 | Dyno 休眠 |
| **Localhost** | 24/7 | :8050 | 完全控制 | 仅本地 |

---

##  Heroku 计费和限制

### 免费层：
-  无需付款方式
- ⏸️ 每月 550 dyno 小时（~22 天）
-  512 MB RAM
-  1 dyno

### Hobby 层（$7/月）：
-  常开（无休眠）
-  512 MB RAM
-  更快性能

### 检查使用情况：
```bash
heroku ps
heroku dyno-types
```

---

##  检查清单

部署前：
- [ ] Heroku CLI 已安装
- [ ] 已登录 Heroku (`heroku login`)
- [ ] Git 已初始化（方法 B）或在主仓库中（方法 A）
- [ ] `runtime.txt` 包含 `python-3.12`
- [ ] `Procfile` 包含 `web: gunicorn mev_dashboard:server`
- [ ] `requirements.txt` 包含所有依赖

部署中：
- [ ] App 已创建 (`heroku create mev-aileena-dashboard`)
- [ ] 代码已推送 (`git push heroku main`)
- [ ] 构建成功（检查日志）
- [ ] Dyno 正在运行 (`heroku ps`)

部署后：
- [ ] 临时 URL 可访问 (https://mev-aileena-dashboard.herokuapp.com)
- [ ] 所有 8 个 tab 都加载
- [ ] 图表正确显示
- [ ] 域名已添加到 Heroku
- [ ] DNS 记录已更新
- [ ] HTTPS 工作正常 (https://mev.aileena.xyz)

---

##  成功！

您的 MEV 仪表板现在在 Heroku 上运行！

**访问您的应用**：
```
https://mev.aileena.xyz
```

**查看日志**：
```bash
heroku logs --tail
```

**管理应用**：
```bash
https://dashboard.heroku.com/apps/mev-aileena-dashboard
```

---

##  有用的 Heroku 命令

```bash
heroku create APP_NAME          # 创建应用
heroku open                      # 在浏览器中打开
heroku logs --tail              # 实时日志
heroku config                   # 查看环境变量
heroku config:set KEY=VALUE     # 设置环境变量
heroku ps                        # 查看 dyno 状态
heroku ps:scale web=1           # 启动 dyno
heroku ps:scale web=0           # 停止 dyno
heroku ps:type web=standard-1x  # 升级到付费 dyno
heroku destroy APP_NAME         # 删除应用
git push heroku main            # 部署新版本
```

---

##  下一步

1. **部署到 Heroku**（按上述步骤）
2. **配置自定义域名**（mev.aileena.xyz）
3. **监控应用**（heroku logs）
4. **考虑升级**（如果需要常开）

**有问题？** 

检查日志：
```bash
heroku logs --tail
```

或查看 Heroku 文档：
https://devcenter.heroku.com/articles/deploying-python

---

**祝您部署顺利！**
