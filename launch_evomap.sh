#!/bin/bash
# 启动所有 evomap 实验（多线程并行版）
# 用法: bash launch_evomap.sh [workers]
# 默认 workers=8

set -e

WORKERS=${1:-8}

# 环境配置
source /root/miniconda3/etc/profile.d/conda.sh
conda activate gene-bench
# 设置代理（根据你的网络环境配置，例如需要代理访问 Google API）
# export https_proxy=http://your-proxy:port
# export http_proxy=http://your-proxy:port

GEMINI_KEY="${GEMINI_API_KEY:?请设置环境变量 GEMINI_API_KEY}"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

echo "=== 启动 EvoMap 实验 (workers=$WORKERS) ==="
echo "时间: $(date)"

# 启动 6 个实验（每个后台进程内部 8 线程并行）
for EXP in ex8 ex9 ex10 ex11 ex12 ex13; do
    echo "启动 $EXP ..."
    nohup python run_evomap_experiments.py \
        --experiment "$EXP" \
        --gemini-key "$GEMINI_KEY" \
        --workers "$WORKERS" \
        > "data/evomap_${EXP}.log" 2>&1 &
    echo "  PID: $! -> data/evomap_${EXP}.log"
done

echo ""
echo "=== 6 个实验已启动（每个 ${WORKERS} 并行线程）==="
echo "总计 1110 trials，预计速度 ~${WORKERS}x"
echo ""
echo "监控进度:"
echo "  watch 'wc -l data/evomap_*_results.jsonl 2>/dev/null'"
echo "  tail -f data/evomap_ex8.log"
