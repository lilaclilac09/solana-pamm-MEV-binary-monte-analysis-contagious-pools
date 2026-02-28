#!/bin/bash

# Heroku 自动部署脚本 - MEV 仪表板
# 支持两种部署方式：Git Subtree 或独立目录

echo "🚀 Heroku MEV 仪表板部署脚本"
echo "======================================"
echo ""

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 检查 Heroku CLI
if ! command -v heroku &> /dev/null; then
    echo -e "${RED}❌ Heroku CLI 未找到${NC}"
    echo ""
    echo "安装: brew install heroku"
    echo "或下载: https://devcenter.heroku.com/articles/heroku-cli"
    exit 1
fi

echo -e "${GREEN}✅ Heroku CLI 已安装${NC}"
echo ""

# 检查 Git CLI
if ! command -v git &> /dev/null; then
    echo -e "${RED}❌ Git 未找到${NC}"
    exit 1
fi

# 检查 Heroku 登录状态
if ! heroku auth:whoami &> /dev/null; then
    echo -e "${YELLOW}🔐 需要登录 Heroku${NC}"
    heroku login
fi

echo -e "${GREEN}✅ 已登录到 Heroku${NC}"
echo ""

# 选择部署方式
echo "选择部署方式："
echo "1) Git Subtree（推荐 - 与原仓库同步）"
echo "2) 独立目录（简单 - 一次性部署）"
echo ""
read -p "选择 (1 或 2): " DEPLOY_METHOD

if [ "$DEPLOY_METHOD" == "1" ]; then
    echo ""
    echo -e "${YELLOW}使用 Git Subtree 方式...${NC}"
    echo ""
    
    # 检查是否在主仓库中
    if [ ! -d "12_live_dashboard" ]; then
        echo -e "${RED}❌ 未找到 12_live_dashboard 文件夹${NC}"
        echo "请在主仓库目录中运行此脚本"
        exit 1
    fi
    
    echo "输入 Heroku app 名称 (默认: mev-aileena-dashboard)："
    read -p "App 名称: " APP_NAME
    APP_NAME=${APP_NAME:-mev-aileena-dashboard}
    
    echo ""
    echo "🔧 创建 Heroku app: $APP_NAME"
    heroku create "$APP_NAME" 2>/dev/null || echo "⚠️  App 可能已存在"
    
    echo ""
    echo "🔧 设置 Heroku remote"
    heroku git:remote -a "$APP_NAME" 2>/dev/null || true
    
    echo ""
    echo "🚀 推送代码..."
    git subtree push --prefix 12_live_dashboard heroku main
    
    echo ""
    echo -e "${GREEN}✅ 部署完成！${NC}"
    echo ""
    echo "应用 URL: https://$APP_NAME.herokuapp.com"
    echo ""
    
elif [ "$DEPLOY_METHOD" == "2" ]; then
    echo ""
    echo -e "${YELLOW}使用独立目录方式...${NC}"
    echo ""
    
    # 检查源目录
    REPO_PATH="/Users/aileen/Downloads/pamm/solana-pamm-analysis/solana-pamm-MEV-binary-monte-analysis-contagious-pools/12_live_dashboard"
    if [ ! -d "$REPO_PATH" ]; then
        echo -e "${RED}❌ 源目录未找到${NC}"
        exit 1
    fi
    
    # 创建工作目录
    WORK_DIR="$HOME/mev-heroku-deploy"
    echo "📁 创建工作目录: $WORK_DIR"
    mkdir -p "$WORK_DIR"
    cd "$WORK_DIR"
    
    # 清理旧文件
    if [ -f .git/config ]; then
        echo "清理旧 Git 历史..."
        rm -rf .git
    fi
    
    # 复制文件
    echo "📋 复制文件..."
    cp -r "$REPO_PATH"/* .
    
    # 初始化 Git
    echo "📦 初始化 Git..."
    git init
    git add .
    git commit -m "Initial commit for Heroku deployment"
    
    # 获取 app 名称
    echo ""
    echo "输入 Heroku app 名称 (默认: mev-aileena-dashboard):"
    read -p "App 名称: " APP_NAME
    APP_NAME=${APP_NAME:-mev-aileena-dashboard}
    
    # 创建 Heroku app
    echo ""
    echo "🔧 创建 Heroku app: $APP_NAME"
    heroku create "$APP_NAME"
    
    # 推送代码
    echo ""
    echo "🚀 推送代码..."
    git push heroku main
    
    echo ""
    echo -e "${GREEN}✅ 部署完成！${NC}"
    echo ""
    echo "应用目录: $WORK_DIR"
    echo "应用 URL: https://$APP_NAME.herokuapp.com"
    echo ""
    
else
    echo -e "${RED}❌ 无效选择${NC}"
    exit 1
fi

# 显示后续步骤
echo "📚 后续步骤："
echo ""
echo "1. 查看日志："
echo "   heroku logs --tail"
echo ""
echo "2. 打开应用："
echo "   heroku open"
echo ""
echo "3. 添加自定义域名 (mev.aileena.xyz):"
echo "   heroku domains:add mev.aileena.xyz"
echo "   然后在 DNS 提供商中添加 CNAME 记录"
echo ""
echo "4. 检查 dyno 状态："
echo "   heroku ps"
echo ""
echo "5. 更新代码："
echo "   git add ."
echo "   git commit -m 'Update'"
echo "   git push heroku main"
echo ""

# 可选：打开应用
read -p "现在打开应用? (y/n): " OPEN_APP
if [ "$OPEN_APP" == "y" ] || [ "$OPEN_APP" == "Y" ]; then
    heroku open
fi

echo ""
echo -e "${GREEN}🎉 部署脚本完成！${NC}"
echo ""
