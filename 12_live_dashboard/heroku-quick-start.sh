#!/bin/bash

# ╔═══════════════════════════════════════════════════════════════════════╗
# ║  Heroku CLI 安装验证 & 自动部署启动脚本                              ║
# ║  用于修复 GitHub 网络连接问题后的快速部署                            ║
# ╚═══════════════════════════════════════════════════════════════════════╝

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
NC='\033[0m' # 无颜色

echo -e "${BLUE}╔═══════════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║  🚀 Heroku 部署自动启动器（网络修复版）                              ║${NC}"
echo -e "${BLUE}╚═══════════════════════════════════════════════════════════════════════╝${NC}"
echo ""

# 步骤 1: 检查 Heroku CLI
echo -e "${YELLOW}[1/5] 检查 Heroku CLI 安装${NC}..."

if command -v heroku &> /dev/null; then
    HEROKU_VERSION=$(heroku --version 2>&1 | head -1)
    echo -e "${GREEN}   ✅ Heroku CLI 已安装${NC}"
    echo "   $HEROKU_VERSION"
else
    echo -e "${RED}   ❌ Heroku CLI 未安装或不在 PATH 中${NC}"
    echo ""
    echo -e "${YELLOW}   尝试添加 Homebrew 到 PATH...${NC}"
    
    if [ -x "/opt/homebrew/bin/brew" ]; then
        export PATH="/opt/homebrew/bin:$PATH"
        echo 'export PATH="/opt/homebrew/bin:$PATH"' >> ~/.zshrc
        
        if command -v heroku &> /dev/null; then
            echo -e "${GREEN}   ✅ PATH 已更新，Heroku CLI 现已可用${NC}"
        else
            echo -e "${RED}   ❌ 仍然找不到 Heroku CLI${NC}"
            echo -e "${YELLOW}   解决方案：${NC}"
            echo "   1. brew install heroku"
            echo "   2. source ~/.zshrc"
            echo "   3. 重新运行此脚本"
            exit 1
        fi
    else
        echo -e "${RED}   ❌ Homebrew 未找到${NC}"
        exit 1
    fi
fi
echo ""

# 步骤 2: 检查 Heroku 登录状态
echo -e "${YELLOW}[2/5] 检查 Heroku 登录状态${NC}..."

if heroku auth:whoami &> /dev/null 2>&1; then
    HEROKU_USER=$(heroku auth:whoami 2>/dev/null || echo "unknown")
    echo -e "${GREEN}   ✅ 已登录 Heroku${NC}"
    echo "   用户: $HEROKU_USER"
else
    echo -e "${YELLOW}   ⚠️  未登录 Heroku，现在登录...${NC}"
    echo ""
    heroku login
    echo ""
fi
echo ""

# 步骤 3: 验证项目文件
echo -e "${YELLOW}[3/5] 检查项目文件完整性${NC}..."

REQUIRED_FILES=(
    "mev_dashboard.py"
    "requirements.txt"
    "Procfile"
    "runtime.txt"
)

ALL_EXIST=true
for file in "${REQUIRED_FILES[@]}"; do
    if [ -f "$file" ]; then
        echo -e "${GREEN}   ✅ $file${NC}"
    else
        echo -e "${RED}   ❌ $file (缺失)${NC}"
        ALL_EXIST=false
    fi
done

if [ "$ALL_EXIST" = false ]; then
    echo -e "${RED}   错误：某些必需文件缺失${NC}"
    exit 1
fi
echo ""

# 步骤 4: 部署方式选择
echo -e "${YELLOW}[4/5] 选择部署方式${NC}..."
echo ""
echo "   1. ⚡ Git Subtree（推荐）- 与主仓库集成，后续可自动更新"
echo "   2. 📁 独立部署 - 独立的 Heroku 应用，不依赖主仓库"
echo "   3. 🚀 使用自动化脚本（heroku-deploy-cn.sh）"
echo ""
read -p "   请选择 [1-3，默认=3]: " CHOICE
CHOICE=${CHOICE:-3}

echo ""

case $CHOICE in
    1)
        echo -e "${GREEN}✅ 您选择: Git Subtree 方式${NC}"
        echo ""
        echo -e "${YELLOW}步骤：${NC}"
        echo "1. 返回主仓库目录："
        echo "   cd /Users/aileen/Downloads/pamm/solana-pamm-analysis/solana-pamm-MEV-binary-monte-analysis-contagious-pools"
        echo ""
        echo "2. 创建 Heroku 应用："
        echo "   heroku create mev-aileena-dashboard"
        echo ""
        echo "3. 推送代码："
        echo "   git subtree push --prefix 12_live_dashboard heroku main"
        echo ""
        ;;
    2)
        echo -e "${GREEN}✅ 您选择: 独立部署方式${NC}"
        echo ""
        echo -e "${YELLOW}步骤：${NC}"
        echo "1. 创建临时目录："
        echo "   mkdir ~/mev-heroku-deploy"
        echo "   cd ~/mev-heroku-deploy"
        echo ""
        echo "2. 复制文件："
        echo "   cp -r $(pwd)/* ."
        echo ""
        echo "3. 初始化 Git："
        echo "   git init"
        echo "   git add ."
        echo '   git commit -m "Initial MEV dashboard"'
        echo ""
        echo "4. 创建并部署："
        echo "   heroku create mev-aileena-dashboard"
        echo "   git push heroku main"
        echo ""
        ;;
    3|*)
        echo -e "${GREEN}✅ 您选择: 使用自动化脚本${NC}"
        echo ""
        
        if [ -f "heroku-deploy-cn.sh" ]; then
            echo -e "${YELLOW}运行自动化部署脚本...${NC}"
            echo ""
            chmod +x heroku-deploy-cn.sh
            ./heroku-deploy-cn.sh
            exit 0
        else
            echo -e "${RED}❌ heroku-deploy-cn.sh 找不到${NC}"
            echo "   请确保在 12_live_dashboard 目录中运行此脚本"
            exit 1
        fi
        ;;
esac

# 步骤 5: 部署后测试
echo ""
echo -e "${YELLOW}[5/5] 部署后的验证步骤${NC}..."
echo ""
echo -e "${GREEN}部署完成后，运行以下命令查看您的应用：${NC}"
echo ""
echo "   ${YELLOW}heroku open${NC}"
echo ""
echo -e "${GREEN}或手动访问：${NC}"
echo "   ${YELLOW}https://mev-aileena-dashboard.herokuapp.com${NC}"
echo ""
echo -e "${GREEN}查看实时日志：${NC}"
echo "   ${YELLOW}heroku logs --tail${NC}"
echo ""
echo -e "${GREEN}配置自定义域名（可选）：${NC}"
echo "   ${YELLOW}heroku domains:add mev.aileena.xyz${NC}"
echo ""

echo -e "${BLUE}╔═══════════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║  ✨ 所有准备完成！                                                    ║${NC}"
echo -e "${BLUE}╚═══════════════════════════════════════════════════════════════════════╝${NC}"
echo ""

