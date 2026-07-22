#!/bin/bash
# ============================================================================
#  SJTU Canvas 视频下载器 —— 一键启动脚本
#  用法：在「访达」中双击本文件即可；或在终端里运行  bash start.command
#  脚本会自动复用项目内的 .venv 虚拟环境，缺依赖/缺 aria2 时自动补齐。
# ============================================================================

# 让 brew 安装的 aria2 / brew 命令能被找到（macOS 上很重要）
export PATH="/opt/homebrew/bin:/usr/local/bin:$PATH"

# 无论在哪里启动，都切到脚本所在的项目根目录
cd "$(dirname "$0")" || exit 1

echo "📂 项目目录: $(pwd)"

# ---------------------------------------------------------------------------
# 1) 选择带 tkinter 的 Python（仅在 .venv 不存在、需要重建时才用到）
# ---------------------------------------------------------------------------
PYTHON_BIN=""
for cand in /usr/local/bin/python3 /opt/homebrew/bin/python3 "$HOME/.workbuddy/binaries/python/versions/3.13.12/bin/python3" python3; do
  if command -v "$cand" >/dev/null 2>&1 && "$cand" -c "import tkinter" >/dev/null 2>&1; then
    PYTHON_BIN="$cand"
    break
  fi
done
if [ -z "$PYTHON_BIN" ]; then
  echo "❌ 未找到带 tkinter 的 Python，请先安装 Python 与 Tk（建议 brew install python-tk）。"
  read -p "按回车退出..."
  exit 1
fi

# ---------------------------------------------------------------------------
# 2) 复用或创建虚拟环境 .venv
# ---------------------------------------------------------------------------
VENV_DIR=".venv"
if [ ! -x "$VENV_DIR/bin/python" ]; then
  echo "🔧 首次运行，正在用 $PYTHON_BIN 创建虚拟环境..."
  "$PYTHON_BIN" -m venv "$VENV_DIR" || {
    echo "❌ 虚拟环境创建失败。"; read -p "按回车退出..."; exit 1
  }
  echo "📦 正在安装运行依赖（beautifulsoup4 / Pillow / requests / websocket-client）..."
  "$VENV_DIR/bin/pip" install --quiet --disable-pip-version-check \
    beautifulsoup4 Pillow requests websocket-client || {
    echo "❌ 依赖安装失败，请检查网络后重试。"; read -p "按回车退出..."; exit 1
  }
else
  echo "✅ 已存在虚拟环境，跳过创建。"
fi
VENV_PYTHON="$VENV_DIR/bin/python"

# ---------------------------------------------------------------------------
# 3) 检查下载引擎 aria2
# ---------------------------------------------------------------------------
if ! command -v aria2c >/dev/null 2>&1; then
  echo "⚠️  未检测到 aria2，尝试用 Homebrew 安装..."
  if command -v brew >/dev/null 2>&1; then
    brew install aria2 || { echo "❌ aria2 安装失败。"; read -p "按回车退出..."; exit 1; }
  else
    echo "❌ 未安装 Homebrew，无法自动安装 aria2，请手动安装后重试。"
    read -p "按回车退出..."; exit 1
  fi
fi
echo "✅ aria2 就绪: $(command -v aria2c)"

# ---------------------------------------------------------------------------
# 4) 启动程序
# ---------------------------------------------------------------------------
echo "🚀 正在启动 SJTU Canvas 视频下载器..."
echo "    （关闭弹出的窗口即可退出程序）"
"$VENV_PYTHON" main.py

echo "👋 程序已退出。"
read -p "按回车关闭此窗口..."
