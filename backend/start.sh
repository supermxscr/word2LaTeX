#!/usr/bin/env bash
# 启动 Word→LaTeX 后端服务（无 venv 时会自动创建并安装依赖）

set -e
cd "$(dirname "$0")"

VENV_DIR="venv"
if [ -d ".venv" ]; then
  VENV_DIR=".venv"
fi

if [ ! -d "$VENV_DIR" ]; then
  echo "未找到虚拟环境，正在创建 $VENV_DIR 并安装依赖..."
  python3 -m venv "$VENV_DIR"
  source "$VENV_DIR/bin/activate"
  pip install -r requirements.txt -q
  echo "依赖安装完成。"
else
  source "$VENV_DIR/bin/activate"
fi

if ! command -v uvicorn &> /dev/null; then
  echo "正在安装依赖..."
  pip install -r requirements.txt -q
fi

echo "启动后端 http://127.0.0.1:8005"
PORT="${PORT:-8005}"
echo "启动后端 http://127.0.0.1:${PORT}"
exec uvicorn main:app --reload --host 0.0.0.0 --port "${PORT}"
