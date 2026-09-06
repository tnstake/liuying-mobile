#!/data/data/com.termux/files/usr/bin/bash
# 流萤 Termux版 一键安装脚本
# 使用方法: bash install.sh

echo "╔══════════════════════════════════════╗"
echo "║    ⚡ 流萤 Termux版 一键安装脚本      ║"
echo "╚══════════════════════════════════════╝"
echo ""

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 第1步：更新Termux
echo -e "${BLUE}[1/5] 更新Termux软件包...${NC}"
pkg update -y
pkg upgrade -y
echo -e "${GREEN}✅ Termux更新完成${NC}"
echo ""

# 第2步：安装Python和依赖
echo -e "${BLUE}[2/5] 安装Python和系统依赖...${NC}"
pkg install -y python
pkg install -y git
pkg install -y wget
pkg install -y openssl
echo -e "${GREEN}✅ Python和系统依赖安装完成${NC}"
echo ""

# 第3步：安装Python库
echo -e "${BLUE}[3/5] 安装Python库...${NC}"
pip install --upgrade pip
pip install requests
echo -e "${GREEN}✅ Python库安装完成${NC}"
echo ""

# 第4步：配置存储权限
echo -e "${BLUE}[4/5] 配置存储权限...${NC}"
if [ ! -d ~/storage ]; then
    echo -e "${YELLOW}⚠️  需要授予存储权限，请在弹出的对话框中选择'允许'${NC}"
    termux-setup-storage
    sleep 2
fi
echo -e "${GREEN}✅ 存储权限配置完成${NC}"
echo ""

# 第5步：创建启动脚本
echo -e "${BLUE}[5/5] 创建启动脚本...${NC}"
cat > ~/liuying.sh << 'EOF'
#!/data/data/com.termux/files/usr/bin/bash
cd ~/liuying_termux
python main.py
EOF
chmod +x ~/liuying.sh
echo -e "${GREEN}✅ 启动脚本创建完成${NC}"
echo ""

# 安装完成
echo "╔══════════════════════════════════════╗"
echo -e "║      ${GREEN}✅ 流萤安装完成！${NC}                 ║"
echo "╠══════════════════════════════════════╣"
echo "║  启动流萤:                            ║"
echo "║    bash ~/liuying.sh                 ║"
echo "║                                      ║"
echo "║  或进入目录后运行:                    ║"
echo "║    cd ~/liuying_termux              ║"
echo "║    python main.py                    ║"
echo "╠══════════════════════════════════════╣"
echo "║  配置说明:                            ║"
echo "║  编辑 config.json 配置:              ║"
echo "║  - 智谱API Key（云端模型）           ║"
echo "║  - 本地模型名称                       ║"
echo "║  - 系统提示词                         ║"
echo "╠══════════════════════════════════════╣"
echo "║  安装本地Ollama（可选）:             ║"
echo "║  请在手机上安装 Ollama Android 版    ║"
echo "║  然后下载模型:                        ║"
echo "║  ollama pull qwen2.5:1.5b          ║"
echo "╚══════════════════════════════════════╝"
echo ""
echo -e "${YELLOW}💡 提示: 即使不安装本地Ollama，配置云端API Key后也可以正常使用！${NC}"
echo ""
