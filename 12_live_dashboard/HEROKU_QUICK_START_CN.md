# Heroku 快速参考 - 3 分钟快速开始

**您的仓库：** https://github.com/lilaclilac09/solana-pamm-MEV-binary-monte-analysis-contagious-pools

---

##  3 步快速部署

### 第 1 步：安装 Heroku CLI

```bash
brew install heroku
heroku login
```

### 第 2 步：选择部署方式

**方式 A - Git Subtree（推荐）** - 与原仓库同步：

```bash
cd /Users/aileen/Downloads/pamm/solana-pamm-analysis/solana-pamm-MEV-binary-monte-analysis-contagious-pools

heroku create mev-aileena-dashboard
git subtree push --prefix 12_live_dashboard heroku main
```

**方式 B - 独立目录** - 简单、一次性：

```bash
mkdir ~/mev-heroku-deploy
cd ~/mev-heroku-deploy
cp -r /Users/aileen/Downloads/pamm/solana-pamm-analysis/solana-pamm-MEV-binary-monte-analysis-contagious-pools/12_live_dashboard/* .
git init
git add .
git commit -m "Initial commit"
heroku create mev-aileena-dashboard
git push heroku main
```

**或使用自动脚本：**

```bash
cd /Users/aileen/Downloads/pamm/solana-pamm-analysis/solana-pamm-MEV-binary-monte-analysis-contagious-pools/12_live_dashboard
./heroku-deploy-cn.sh
```

### 第 3 步：测试

```bash
heroku open
# 或访问：https://mev-aileena-dashboard.herokuapp.com
```

---

##  添加自定义域名（mev.aileena.xyz）

```bash
# 在 Heroku 中添加域名
heroku domains:add mev.aileena.xyz

# 在您的 DNS 提供商中创建 CNAME 记录：
# 名称: mev
# 值: mev-aileena-dashboard.herokuapp.com

# 5-60 分钟后访问：
# https://mev.aileena.xyz
```

---

##  检查状态

```bash
heroku ps              # 查看 dyno 状态
heroku logs --tail     # 实时日志
heroku config          # 环境变量
```

---

##  更新应用

```bash
# 方式 A（Git Subtree - 从主仓库）：
git add .
git commit -m "Update"
git push origin main
git subtree push --prefix 12_live_dashboard heroku main

# 方式 B（独立目录 - 从工作目录）：
cd ~/mev-heroku-deploy
git add .
git commit -m "Update"
git push heroku main
```

---

## ️ 常用命令

```bash
heroku create APP_NAME              # 创建应用
heroku open                         # 打开应用
heroku logs --tail                  # 实时日志
heroku ps                           # Dyno 状态
heroku ps:scale web=1:standard-1x  # 升级到付费 ($7/月)
heroku config:set KEY=VALUE        # 设置环境变量
heroku destroy APP_NAME             # 删除应用
```

---

##  故障排除

**构建失败？**
```bash
heroku logs --tail  # 查看详细错误
```

**检查 requirements.txt：**
```bash
cat requirements.txt | grep -E "dash|plotly|gunicorn"
```

**重新构建：**
```bash
heroku apps:destroy mev-aileena-dashboard --confirm
heroku create mev-aileena-dashboard
git push heroku main  # 或 git subtree push...
```

---

##  Dyno 睡眠

**免费 dyno 每 30 分钟无活动后休眠**

- 首次加载需 5-10 秒
- 解决方案：使用 UptimeRobot（https://uptimerobot.com/）每 5 分钟 ping 一次

---

##  检查清单

- [ ] `heroku login` 已运行
- [ ] `runtime.txt` 包含 `python-3.12`
- [ ] `Procfile` 包含 `web: gunicorn mev_dashboard:server`
- [ ] `requirements.txt` 完整
- [ ] App 已创建
- [ ] 代码已推送
- [ ] dyno 正在运行
- [ ] 应用可访问
- [ ] 域名已添加（可选）

---

##  现在就开始！

**最快的方式：**

```bash
cd /Users/aileen/Downloads/pamm/solana-pamm-analysis/solana-pamm-MEV-binary-monte-analysis-contagious-pools/12_live_dashboard
./heroku-deploy-cn.sh
```

**步骤式指南：** [HEROKU_COMPLETE_GUIDE_CN.md](HEROKU_COMPLETE_GUIDE_CN.md)

---

##  您的 MEV 仪表板

**当前状态：**
-  **Render：** LIVE（mev.aileena.xyz）
-  **Heroku：** 随时可部署

**部署后：**
-  所有 6 种图表类型（柱状、饼图、热力图、散点、网络、表格）
-  8 个交互式标签页
-  完整的 MEV 数据可视化
-  可滚动、可悬停、可缩放

---

**祝部署顺利！**
