#!/bin/bash
# 流萤手机版一键打包脚本（百度AI Studio适配版）
# 使用方法：bash build_apk.sh

echo "=========================================="
echo "  流萤手机版 APK 一键打包工具"
echo "  （百度AI Studio适配版）"
echo "=========================================="

# 设置工作目录
WORK_DIR="/home/aistudio/liuying_mobile"
cd $WORK_DIR

# 第1步：检查系统依赖（百度AI Studio已有大部分，跳过apt安装）
echo ""
echo "[1/5] 检查系统依赖..."
which python3 && echo "✅ python3 已安装" || echo "❌ python3 未安装"
which pip3 && echo "✅ pip3 已安装" || echo "❌ pip3 未安装"
which git && echo "✅ git 已安装" || echo "❌ git 未安装"
which java && echo "✅ java 已安装" || echo "⚠️  java 未安装，尝试安装..."
which zip && echo "✅ zip 已安装" || echo "❌ zip 未安装"
which unzip && echo "✅ unzip 已安装" || echo "❌ unzip 未安装"
which wget && echo "✅ wget 已安装" || echo "❌ wget 未安装"

# 检查Java，如果没有就尝试用conda安装
if ! which java; then
    echo "尝试用conda安装Java..."
    conda install -y -c conda-forge openjdk=17 2>/dev/null || echo "conda安装Java失败，继续尝试..."
fi

echo "✅ 系统依赖检查完成"

# 第2步：安装Python依赖
echo ""
echo "[2/5] 安装Python依赖..."
pip3 install --upgrade pip buildozer cython virtualenv 2>&1 | tail -5
echo "✅ Python依赖安装完成"

# 第3步：配置Android SDK
echo ""
echo "[3/5] 配置Android SDK（下载中，约3-5分钟）..."
export ANDROIDSDK=/home/aistudio/android-sdk
export ANDROIDNDK=/home/aistudio/android-ndk
export ANDROIDAPI=33
export NDKAPI=21

mkdir -p $ANDROIDSDK/cmdline-tools
cd /tmp

# 下载Android command line tools
wget -q https://dl.google.com/android/repository/commandlinetools-linux-9477386_latest.zip -O cmdline-tools.zip
unzip -q -o cmdline-tools.zip -d $ANDROIDSDK/cmdline-tools/
mv $ANDROIDSDK/cmdline-tools/cmdline-tools $ANDROIDSDK/cmdline-tools/latest

# 接受许可并安装SDK组件
yes | $ANDROIDSDK/cmdline-tools/latest/bin/sdkmanager --licenses 2>/dev/null
$ANDROIDSDK/cmdline-tools/latest/bin/sdkmanager "platform-tools" "platforms;android-33" "build-tools;33.0.2" 2>&1 | tail -3

# 下载NDK
wget -q https://dl.google.com/android/repository/android-ndk-r25b-linux.zip -O ndk.zip
unzip -q -o ndk.zip -d /home/aistudio/
mv /home/aistudio/android-ndk-r25b $ANDROIDNDK

echo "✅ Android SDK配置完成"

# 第4步：开始打包
echo ""
echo "[4/5] 开始打包APK（这一步最久，约15-30分钟）..."
cd $WORK_DIR
export ANDROIDSDK=/home/aistudio/android-sdk
export ANDROIDNDK=/home/aistudio/android-ndk
export ANDROIDAPI=33
export NDKAPI=21

# 修改buildozer.spec中的路径
sed -i 's|/content/|/home/aistudio/|g' buildozer.spec

# 运行buildozer
buildozer android debug 2>&1 | tail -100
echo "✅ 打包命令执行完成"

# 第5步：检查结果
echo ""
echo "[5/5] 检查打包结果..."
cd $WORK_DIR
if ls bin/*.apk 1> /dev/null 2>&1; then
    APK_FILE=$(ls bin/*.apk | head -1)
    APK_SIZE=$(du -h "$APK_FILE" | cut -f1)
    echo ""
    echo "=========================================="
    echo "  ✅ 打包成功！"
    echo "=========================================="
    echo "  APK文件: $APK_FILE"
    echo "  文件大小: $APK_SIZE"
    echo ""
    echo "  下载方法："
    echo "  1. 点击左侧「文件」图标"
    echo "  2. 进入 liuying_mobile/bin/ 目录"
    echo "  3. 右键 .apk 文件，选择「下载」"
    echo "=========================================="
else
    echo ""
    echo "❌ 打包失败，请查看上面的错误日志"
    echo ""
    echo "常见问题："
    echo "  - 网络问题：重新运行此脚本"
    echo "  - 内存不足：使用更高配置的运行环境（GPU版）"
    echo "  - Java未安装：手动安装 openjdk-17"
    echo "  - 依赖缺失：查看错误信息，手动安装缺失的包"
    echo ""
    echo "如果是Java问题，尝试运行："
    echo "  conda install -y -c conda-forge openjdk=17"
fi
