# 🚀 Solana MEV Dashboard - 快速启动指南

## ⚡ 30 秒启动

```bash
cd /Users/aileen/Downloads/pamm/solana-pamm-analysis/solana-pamm-MEV-binary-monte-analysis-contagious-pools/12_live_dashboard

# 方式 1️⃣: Python 脚本（推荐）
python3 start_dashboard.py

# 方式 2️⃣: Bash 脚本
bash RUN_DASHBOARD.sh

# 方式 3️⃣: 直接运行
python3 mev_dashboard.py
```

## 🌐 浏览器访问

启动后，在浏览器中打开：

```
http://127.0.0.1:8050
```

或在其他设备上访问：

```
http://YOUR_IP:8050
```

## ✨ 您会看到这些功能

**9 个交互式标签页：**

1. 📊 **Overview** - 关键统计数据展示
2. 💰 **MEV Distribution** - MEV 利润分布（柱状图、饼图、攻击计数）
3. 🎯 **Top Attackers** - 排名前 5 的攻击者及详情
4. 🔗 **Contagion Analysis** - 协议间攻击者重叠热力图 + 网络拓扑
5. ⚡ **Validator Behavior** - 验证器 Bot 活动比例分析
6. 🔮 **Oracle Analysis** - 预言机延迟和更新频率
7. 🎲 **Token Pair Risk** - 代币对脆弱性分析
8. 🤖 **ML Models** - 机器学习模型性能对比
9. 📈 **Monte Carlo Risk** - 蒙特卡洛模拟风险评估

## 🎯 所有图表类型

✓ 柱状图（Bar Charts）× 6  
✓ 饼图（Pie Charts）× 1  
✓ 热力图（Heatmap）× 1  
✓ 散点图（Scatter Plot）× 2  
✓ 交互式网络图（Network Graph）× 1  
✓ 数据表格（Data Tables）× 5

## ⏹️ 停止服务

按 `Ctrl+C` 停止服务器

## 🆘 故障排除

### ❌ "ModuleNotFoundError: No module named 'dash'"

```bash
# 安装依赖
python3 -m pip install -r requirements.txt
```

### ❌ "Address already in use"

```bash
# 端口 8050 被占用，用其他端口
python3 -c "
import sys
sys.path.insert(0, '.')
import mev_dashboard as m
m.app.run(port=8051)
"
```

### ❌ "Permission denied" (bash 脚本)

```bash
# 添加执行权限
chmod +x RUN_DASHBOARD.sh RUN_DASHBOARD.py
```

## 📊 部署这个应用

一旦本地测试成功，部署到云端：

**选项 1️⃣: Vercel**
```bash
# 已配置 vercel.json
vercel
```

**选项 2️⃣: Render**
```bash
# 已配置 Procfile + runtime.txt
# 通过网页部署: https://render.com
```

**选项 3️⃣: Heroku**
```bash
# 已配置 Procfile + runtime.txt
heroku login
heroku create mev-aileena-dashboard
git push heroku main
```

## 🔧 配置文件已齐全

```
✅ mev_dashboard.py      (主应用，748 行)
✅ requirements.txt      (Python 依赖)
✅ Procfile             (部署启动命令)
✅ runtime.txt          (Python 3.11.7)
✅ vercel.json          (Vercel 配置)
✅ RUN_DASHBOARD.sh     (Bash 启动脚本)
✅ start_dashboard.py   (Python 启动脚本)
```

## 📝 生成数据来源

所有数据来自：
- Solana pAMM MEV 研究分析
- HumidiFi、BisonFi、GoonFi 等协议
- 时间序列事件，验证器分析
- 机器学习分类（XGBoost, SVM, LR）
- 蒙特卡洛模拟（10,000 次迭代）

## 💡 提示

- 仪表板完全交互式：可缩放、悬停、导出为 PNG
- 适用于学术研究、投资分析、安全审计
- 实时更新：修改 `mev_dashboard.py` → 刷新浏览器 → 看到变化

## 🎓 代码结构

```python
# 数据准备（第 1-150 行）
protocols_data = {...}
attackers_data = {...}
contagion_matrix = {...}

# 应用初始化（第 172-173 行）
app = dash.Dash(__name__)
server = app.server  # ← 重要（WSGI）

# 布局（第 180-680 行）
app.layout = html.Div([
    dcc.Tabs(children=[...])  # 9 个标签页
])

# 回调（第 685-740 行）
@app.callback(...)
def update_network(_):  # 网络图

# 启动（第 748 行）
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8050)
```

---

**现在就启动吧！** 🚀

```bash
python3 start_dashboard.py
```

访问 http://127.0.0.1:8050 享受您的 Solana MEV 分析仪表板！
