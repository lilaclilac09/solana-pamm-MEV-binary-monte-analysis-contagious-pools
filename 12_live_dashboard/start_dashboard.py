#!/usr/bin/env python3
"""
🚀 Solana MEV Dashboard - 启动脚本
用法: python3 start_dashboard.py
"""

import sys
import os
import subprocess

def check_python():
    """检查 Python 版本"""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 9):
        print(f"❌ 需要 Python 3.9+，您的版本: {version.major}.{version.minor}")
        sys.exit(1)
    print(f"✅ Python {version.major}.{version.minor} 就绪")

def install_requirements():
    """安装依赖"""
    print("📦 安装依赖...")
    try:
        subprocess.run([
            sys.executable, '-m', 'pip', 'install', '-q',
            'dash==4.0.0',
            'plotly==6.5.2', 
            'pandas>=3.0.1',
            'networkx==3.6.1',
            'requests==2.31.0'
        ], check=True)
        print("✅ 依赖已安装")
    except subprocess.CalledProcessError:
        print("⚠️ 某些依赖安装可能失败，继续即是...")

def check_dashboard_file():
    """检查仪表板文件"""
    if not os.path.exists('mev_dashboard.py'):
        print("❌ 未找到 mev_dashboard.py")
        sys.exit(1)
    print("✅ 仪表板文件就绪")

def start_dashboard():
    """启动仪表板"""
    print("\n" + "="*70)
    print("🚀 启动 Solana pAMM MEV Intelligence Dashboard")
    print("="*70 + "\n")
    
    print("📊 访问仪表板:")
    print("   🔗 http://127.0.0.1:8050")
    print("   🌐 http://0.0.0.0:8050 (局域网)\n")
    
    print("✨ 仪表板功能:")
    print("   ✓ 📊 MEV 分布分析")
    print("   ✓ 🎯 顶级攻击者")
    print("   ✓ 🔗 协议传染分析")
    print("   ✓ ⚡ 验证器行为")
    print("   ✓ 🔮 预言机分析")
    print("   ✓ 🎲 代币对风险")
    print("   ✓ 🤖 机器学习模型")
    print("   ✓ 📈 蒙特卡洛风险")
    print("   ✓ 📑 案例研究\n")
    
    print("⏹️ 停止服务: 按 Ctrl+C\n")
    print("="*70 + "\n")
    
    # 启动应用
    os.system('python3 mev_dashboard.py')

def main():
    """主函数"""
    print("\n🔷 Solana MEV 仪表板启动器\n")
    
    check_python()
    install_requirements()
    check_dashboard_file()
    start_dashboard()

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 仪表板已停止")
        sys.exit(0)
