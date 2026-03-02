#!/bin/bash

# ╔═══════════════════════════════════════════════════════════════════════╗
# ║  🚀 Solana MEV Dashboard - 一键启动脚本                              ║
# ║  用法：./RUN_DASHBOARD.sh                                             ║
# ╚═══════════════════════════════════════════════════════════════════════╝

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
NC='\033[0m' # 无颜色

# Banner
echo -e "${BLUE}╔═══════════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║  🚀 Solana pAMM MEV Intelligence Dashboard                           ║${NC}"
echo -e "${BLUE}║  一键启动本地开发服务器                                              ║${NC}"
echo -e "${BLUE}╚═══════════════════════════════════════════════════════════════════════╝${NC}"
echo ""

# 步骤 1: 检查 Python
echo -e "${YELLOW}[1/4] 检查 Python 环境...${NC}"
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ 错误：未找到 Python 3${NC}"
    echo "请安装 Python 3.11+: https://www.python.org/downloads/"
    exit 1
fi
PYTHON_VERSION=$(python3 --version 2>&1)
echo -e "${GREEN}✅ $PYTHON_VERSION${NC}"
echo ""

# 步骤 2: 检查依赖
echo -e "${YELLOW}[2/4] 检查并安装依赖...${NC}"
if [ -f "requirements.txt" ]; then
    echo "📦 从 requirements.txt 安装依赖..."
    python3 -m pip install -q -r requirements.txt 2>&1 | grep -E "(Successfully|error)" || echo "   依赖安装中..."
    echo -e "${GREEN}✅ 依赖已安装${NC}"
else
    echo -e "${RED}❌ 未找到 requirements.txt${NC}"
    exit 1
fi
echo ""

# 步骤 3: 验证应用文件
echo -e "${YELLOW}[3/4] 验证应用文件...${NC}"
if [ ! -f "mev_dashboard.py" ]; then
    echo -e "${RED}❌ 未找到 mev_dashboard.py${NC}"
    exit 1
fi
echo -e "${GREEN}✅ mev_dashboard.py 找到${NC}"
echo ""

# 步骤 4: 启动服务器
echo -e "${YELLOW}[4/4] 启动 Dash 服务器...${NC}"
echo ""
echo -e "${BLUE}═══════════════════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}🌐 仪表板已启动！${NC}"
echo ""
echo -e "   📊 访问：${YELLOW}http://127.0.0.1:8050${NC}"
echo -e "   🔗 或使用网络访问：${YELLOW}http://0.0.0.0:8050${NC}"
echo ""
echo -e "   🎯 看到这些功能？${NC}"
echo "      ✓ 📊 MEV Distribution"
echo "      ✓ 🎯 Top Attackers"
echo "      ✓ 🔗 Contagion Analysis"
echo "      ✓ ⚡ Validator Behavior"
echo "      ✓ 🔮 Oracle Analysis"
echo "      ✓ 🎲 Token Pair Risk"
echo "      ✓ 🤖 ML Models"
echo "      ✓ 📈 Monte Carlo Risk"
echo ""
echo -e "   ⏹️  停止服务器：按 ${YELLOW}Ctrl+C${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════════════════════${NC}"
echo ""

# 启动应用
python3 mev_dashboard.py
