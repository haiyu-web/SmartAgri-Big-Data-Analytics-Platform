#!/bin/bash
# ============================================================
# 阿里云 DashScope (通义千问) API Key 环境变量配置脚本
# 执行用户: bigdata
#
# API Key 获取地址:
#   https://help.aliyun.com/zh/model-studio/get-api-key
#
# 使用方式:
#   chmod +x setup_qwen_env.sh
#   ./setup_qwen_env.sh
#   source ~/.bashrc
# ============================================================

set -e

echo "============================================================"
echo "  阿里云 DashScope (通义千问) API Key 配置脚本"
echo "============================================================"
echo ""

BASHRC_FILE="$HOME/.bashrc"

echo "当前用户: $(whoami)"
echo "用户目录: $HOME"
echo "配置文件: $BASHRC_FILE"
echo ""
echo "⚠️  请先到阿里云获取 API Key:"
echo "    https://help.aliyun.com/zh/model-studio/get-api-key"
echo "    (需要阿里云账号，开通 DashScope 灵积模型服务)"
echo ""

echo "请输入你的 DashScope API Key (以 sk- 开头): "
echo "注意: 输入时不会显示内容，这是正常的。"
read -s DASHSCOPE_KEY

echo ""

if [ -z "$DASHSCOPE_KEY" ]; then
    echo "[ERROR] API Key 不能为空"
    exit 1
fi

# 备份原文件
if [ -f "$BASHRC_FILE" ]; then
    cp "$BASHRC_FILE" "$BASHRC_FILE.bak.$(date +%Y%m%d%H%M%S)"
    echo "[OK] 已备份 $BASHRC_FILE"
else
    touch "$BASHRC_FILE"
    echo "[OK] 已创建 $BASHRC_FILE"
fi

# 删除旧配置 (支持清理 DeepSeek 和千问的旧配置)
sed -i '/# DashScope API Key BEGIN/,/# DashScope API Key END/d' "$BASHRC_FILE"
sed -i '/# DeepSeek API Key BEGIN/,/# DeepSeek API Key END/d' "$BASHRC_FILE"
sed -i '/export DEEPSEEK_API_KEY/d' "$BASHRC_FILE"

# 写入新配置
cat >> "$BASHRC_FILE" <<EOF

# DashScope API Key BEGIN
export DASHSCOPE_API_KEY="$DASHSCOPE_KEY"
# DashScope API Key END
EOF

# 当前终端立即生效
export DASHSCOPE_API_KEY="$DASHSCOPE_KEY"

echo ""
echo "============================================================"
echo "  配置完成"
echo "============================================================"

if [ -n "$DASHSCOPE_API_KEY" ]; then
    echo "[OK] 当前终端 DASHSCOPE_API_KEY 已生效"
    echo "Key 前 8 位预览: ${DASHSCOPE_API_KEY:0:8}********"
else
    echo "[ERROR] 当前终端 DASHSCOPE_API_KEY 未生效"
fi

echo ""
echo "--- 后续步骤 ---"
echo ""
echo "1. 让环境变量永久生效:"
echo "   source ~/.bashrc"
echo ""
echo "2. 验证 Key 是否配置成功:"
echo "   python3 -c \"import os; print('千问 Key 已配置' if os.getenv('DASHSCOPE_API_KEY') else '千问 Key 未配置')\""
echo ""
echo "3. 运行 AI 报告生成:"
echo "   cd /opt/project/agri-ai && python3 spark/06_qwen_ai_report.py"
echo ""
