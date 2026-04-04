#!/bin/bash
# 一键并行运行所有 Gene-Bench 实验 (EX1-27)
# 用法: GEMINI_API_KEY=xxx ./run_all_parallel.sh
#
# 前置要求:
#   1. export GEMINI_API_KEY=your_key
#   2. export https_proxy=http://your-proxy:port  (如果需要代理访问 Google API)
#
# 脚本会自动:
#   - 并行运行 EX1-7 和 EX8-27（按组并行）
#   - 自动 resume 已完成的 trials
#   - 完成后自动 git commit + push 结果

set -e

# 检查 API key
if [ -z "$GEMINI_API_KEY" ]; then
    echo "ERROR: 请设置 GEMINI_API_KEY 环境变量"
    echo "  export GEMINI_API_KEY=your_key"
    exit 1
fi

cd "$(dirname "$0")"
PROJ_DIR=$(pwd)
LOG_DIR="$PROJ_DIR/logs"
mkdir -p "$LOG_DIR"

MODELS="gemini_pro,gemini_flash"
GEMINI_KEY="$GEMINI_API_KEY"

echo "============================================================"
echo " Gene-Bench 全量实验 - 并行运行"
echo " 模型: $MODELS"
echo " 代理: ${https_proxy:-无}"
echo " 开始时间: $(date)"
echo "============================================================"

# === 第一组: EX1-7 (run_gene_bench.py) ===
echo ""
echo "[JOB 1] 启动 EX1-7..."
python -u run_gene_bench.py --experiment all --models "$MODELS" \
    --gemini-key "$GEMINI_KEY" \
    --output results/gene_bench_gemini.jsonl \
    --force > "$LOG_DIR/job_ex1_7.log" 2>&1 &
PID_EX1_7=$!
echo "  PID: $PID_EX1_7, 日志: $LOG_DIR/job_ex1_7.log"

# === 第二组: EX8-27 按小组并行 ===
# 分4组, 每组约1500-1700 trials
GROUPS=(
    "ex8 ex9 ex10 ex11"
    "ex12 ex13 ex14 ex15"
    "ex16 ex17 ex18 ex19"
    "ex20 ex21 ex22 ex23 ex24 ex25 ex26 ex27"
)

PIDS=()
for i in "${!GROUPS[@]}"; do
    group="${GROUPS[$i]}"
    job_name="evomap_group$((i+1))"
    echo ""
    echo "[JOB $((i+2))] 启动 $group..."

    (
        for ex in $group; do
            echo "$(date): Starting $ex"
            python -u run_evomap_experiments.py --experiment "$ex" --models "$MODELS" \
                --gemini-key "$GEMINI_KEY" \
                --output-dir results/evomap_gemini 2>&1
            echo "$(date): Finished $ex"
        done
    ) > "$LOG_DIR/${job_name}.log" 2>&1 &

    PIDS+=($!)
    echo "  PID: ${PIDS[-1]}, 实验: $group, 日志: $LOG_DIR/${job_name}.log"
done

# === 等待所有任务完成 ===
echo ""
echo "============================================================"
echo " 5个并行任务已启动，等待完成..."
echo " 监控: tail -f $LOG_DIR/*.log"
echo "============================================================"

# 等待 EX1-7
wait $PID_EX1_7 2>/dev/null
echo "$(date): [JOB 1] EX1-7 完成 (exit: $?)"

# 等待 EX8-27 各组
for i in "${!PIDS[@]}"; do
    wait ${PIDS[$i]} 2>/dev/null
    echo "$(date): [JOB $((i+2))] 完成 (exit: $?)"
done

echo ""
echo "============================================================"
echo " 所有实验完成! $(date)"
echo "============================================================"

# === 汇报结果 ===
echo ""
echo "=== 结果统计 ==="
echo "EX1-7: $(wc -l < results/gene_bench_gemini.jsonl 2>/dev/null || echo 0) trials"
total_evomap=0
for ex in 8 9 10 11 12 13 14 15 16 17 18 19 20 21 22 23 24 25 26 27; do
    f="results/evomap_gemini/evomap_ex${ex}_results.jsonl"
    n=$(wc -l < "$f" 2>/dev/null || echo 0)
    echo "  EX${ex}: $n"
    total_evomap=$((total_evomap + n))
done
echo "EX8-27 total: $total_evomap trials"

# === 自动同步到 GitHub ===
echo ""
echo "=== 同步到 GitHub ==="
git add results/ && \
git commit -m "Experiment results: $(date +%Y-%m-%d) - all 27 experiments complete

Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>" && \
git push origin main && \
echo "GitHub 同步成功!" || \
echo "WARNING: GitHub 同步失败，请手动推送"

echo ""
echo "全部完成! $(date)"
