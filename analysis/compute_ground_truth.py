"""从 JSONL 原始数据计算所有实验的 ground truth"""
import json
import glob
from collections import defaultdict

def analyze_file(filepath, ex_prefix=None):
    """分析一个 JSONL 文件，返回按 (condition, model) 分组的统计"""
    groups = defaultdict(lambda: {'scores': [], 'passes': 0, 'total': 0})
    
    with open(filepath) as f:
        for line in f:
            t = json.loads(line)
            
            # 从 gene_bench 格式提取
            if 'trial_config' in t:
                cfg = t['trial_config']
                model = 'Pro' if cfg['model'] == 'gemini_pro' else 'Flash'
                cond = cfg['condition']
            else:
                # gene_bench_gemini.jsonl 格式
                key = t.get('trial_key', '')
                parts = key.split('__')
                if len(parts) < 4:
                    continue
                model = 'Pro' if 'gemini_pro' in key else 'Flash'
                # 过滤到特定实验
                if ex_prefix and not any(p.startswith(ex_prefix) for p in parts):
                    continue
                # condition 在不同实验中位置不同
                # 格式: scenario__model__exN__condition__rN
                cond = parts[3] if len(parts) >= 5 else parts[2]
            
            ev = t.get('eval', {})
            score = ev.get('pass_rate', 0)
            passed = ev.get('passed', False)
            
            groups[(cond, model)]['scores'].append(score)
            groups[(cond, model)]['total'] += 1
            if passed:
                groups[(cond, model)]['passes'] += 1
    
    return groups

def print_table(groups, title=""):
    """打印格式化表格"""
    conditions = sorted(set(k[0] for k in groups.keys()))
    
    print(f"\n{'='*80}")
    print(f"  {title}")
    print(f"{'='*80}")
    print(f"{'Condition':<28} {'Pro avg':>8} {'Pro P/T':>8} {'Fla avg':>8} {'Fla P/T':>8} {'Comb':>8}")
    print('-'*80)
    
    # 找 baseline
    baseline_comb = None
    for cond in ['none', 'no_context', 'baseline', 'G0']:
        pro = groups.get((cond, 'Pro'))
        flash = groups.get((cond, 'Flash'))
        if pro and flash:
            pa = sum(pro['scores'])/len(pro['scores'])*100
            fa = sum(flash['scores'])/len(flash['scores'])*100
            baseline_comb = (pa + fa) / 2
            break
    
    results = []
    for cond in conditions:
        pro = groups.get((cond, 'Pro'), {'scores': [], 'passes': 0, 'total': 0})
        flash = groups.get((cond, 'Flash'), {'scores': [], 'passes': 0, 'total': 0})
        pro_avg = sum(pro['scores'])/len(pro['scores'])*100 if pro['scores'] else 0
        flash_avg = sum(flash['scores'])/len(flash['scores'])*100 if flash['scores'] else 0
        comb = (pro_avg + flash_avg) / 2
        delta = f"{comb - baseline_comb:+.1f}pp" if baseline_comb is not None else "—"
        
        results.append((cond, pro_avg, pro['passes'], pro['total'], 
                        flash_avg, flash['passes'], flash['total'], comb, delta))
    
    # 按 Combined 降序
    results.sort(key=lambda x: x[7], reverse=True)
    
    for r in results:
        cond, pa, pp, pt, fa, fp, ft, comb, delta = r
        print(f"{cond:<28} {pa:>7.1f}% {pp:>3}/{pt:<3}  {fa:>7.1f}% {fp:>3}/{ft:<3}  {comb:>7.1f}% {delta:>8}")

# EX1-7 from gene_bench
gb_file = 'results/gene_bench_gemini.jsonl'
all_gb = defaultdict(lambda: defaultdict(lambda: {'scores': [], 'passes': 0, 'total': 0}))

with open(gb_file) as f:
    for line in f:
        t = json.loads(line)
        key = t.get('trial_key', '')
        parts = key.split('__')
        if len(parts) < 4:
            continue
        model = 'Pro' if 'gemini_pro' in key else 'Flash'
        ex = parts[2]  # ex1, ex2, etc
        cond = parts[3]
        
        ev = t.get('eval', {})
        score = ev.get('pass_rate', 0)
        passed = ev.get('passed', False)
        
        all_gb[ex][(cond, model)]['scores'].append(score)
        all_gb[ex][(cond, model)]['total'] += 1
        if passed:
            all_gb[ex][(cond, model)]['passes'] += 1

for ex in sorted(all_gb.keys(), key=lambda x: int(x.replace('ex',''))):
    print_table(all_gb[ex], f"EX{ex.replace('ex','')} (gene_bench)")

# EX8-27 from evomap
for fn in sorted(glob.glob('results/evomap_gemini/evomap_ex*_results.jsonl'), 
                 key=lambda x: int(x.split('ex')[1].split('_')[0])):
    ex_num = fn.split('ex')[1].split('_')[0]
    groups = analyze_file(fn)
    print_table(groups, f"EX{ex_num} (evomap)")

