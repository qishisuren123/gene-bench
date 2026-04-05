import json
import glob
from collections import defaultdict

result_files = glob.glob("/mnt/shared-storage-user/renyiming/projects/gen/results/evomap_gemini/evomap_ex*.jsonl")
results = defaultdict(lambda: defaultdict(lambda: {"pass": 0, "fail": 0, "total": 0}))

for file in result_files:
    with open(file, 'r') as f:
        for line in f:
            try:
                data = json.loads(line)
                exp = data.get("experiment", "unknown")
                cond = data.get("condition", "unknown")
                model = data.get("model", "unknown")
                is_pass = data.get("error_type") == "success"
                
                results[exp][(model, cond)]["total"] += 1
                if is_pass:
                    results[exp][(model, cond)]["pass"] += 1
                else:
                    results[exp][(model, cond)]["fail"] += 1
            except Exception as e:
                pass

for exp, exp_data in sorted(results.items()):
    print(f"\n--- Experiment: {exp} ---")
    for (model, cond), stats in sorted(exp_data.items()):
        pass_rate = stats["pass"] / stats["total"] if stats["total"] > 0 else 0
        print(f"{model:15s} | {cond:30s} | Pass Rate: {pass_rate*100:.1f}% ({stats['pass']}/{stats['total']})")
