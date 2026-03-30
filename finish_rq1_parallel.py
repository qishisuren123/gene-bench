#!/usr/bin/env python3
"""快速并行补完 RQ1 剩余 trials"""
import json, os, sys, time, threading
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import asdict

sys.path.insert(0, str(Path(__file__).parent))
from run_gene_bench import (
    MODEL_REGISTRY, SCENARIOS_DIR, GENES_DIR, DATA_DIR,
    call_llm, extract_python_code, evaluate_code,
    generate_rq1_trials, load_gene_for_trial, prepare_system_prompt,
    RQ1_SCENARIOS, GENE_LEVELS,
)

OUTPUT = DATA_DIR / "rq1_results.jsonl"
GEMINI_KEY = os.environ.get("GEMINI_API_KEY", "")
WORKERS = 8

_lock = threading.Lock()

def process_trial(trial):
    scenario_dir = SCENARIOS_DIR / trial.scenario_id
    task_path = scenario_dir / "task.md"
    if not task_path.exists():
        return "skip"

    task_desc = task_path.read_text().strip()
    task_desc += "\n\nWrite a complete, self-contained Python solution. Output ONLY the code inside a single ```python code block. Do not include explanations outside the code block."

    gene = load_gene_for_trial(trial)
    system_prompt = prepare_system_prompt(trial, gene)

    try:
        api_result = call_llm(trial.model, task_desc, system_prompt, "", GEMINI_KEY)
    except Exception as e:
        result = {
            "trial_key": trial.trial_key,
            "trial_config": asdict(trial),
            "eval": {"passed": False, "n_pass": 0, "n_total": 0,
                     "pass_rate": 0, "error_type": f"api_error: {e}"},
            "code_length": 0, "gene_tokens": len(system_prompt)//4,
            "input_tokens": 0, "output_tokens": 0, "cost": 0,
        }
        with _lock:
            with open(OUTPUT, "a") as f:
                f.write(json.dumps(result, default=str) + "\n")
        return "error"

    code = extract_python_code(api_result["response"])
    if not code:
        result = {
            "trial_key": trial.trial_key,
            "trial_config": asdict(trial),
            "eval": {"passed": False, "n_pass": 0, "n_total": 0,
                     "pass_rate": 0, "error_type": "format_error"},
            "code_length": 0, "gene_tokens": len(system_prompt)//4,
            "input_tokens": api_result.get("input_tokens", 0),
            "output_tokens": api_result.get("output_tokens", 0), "cost": 0,
        }
        with _lock:
            with open(OUTPUT, "a") as f:
                f.write(json.dumps(result, default=str) + "\n")
        return "no_code"

    eval_result = evaluate_code(code, scenario_dir)
    result = {
        "trial_key": trial.trial_key,
        "trial_config": asdict(trial),
        "eval": eval_result,
        "code_length": len(code), "gene_tokens": len(system_prompt)//4,
        "input_tokens": api_result.get("input_tokens", 0),
        "output_tokens": api_result.get("output_tokens", 0), "cost": 0,
    }
    with _lock:
        with open(OUTPUT, "a") as f:
            f.write(json.dumps(result, default=str) + "\n")
    return "pass" if eval_result["passed"] else "fail"

def main():
    models = ["gemini_31_pro", "gemini_31_flash"]
    trials = generate_rq1_trials(models, RQ1_SCENARIOS)

    # 加载已完成
    completed = set()
    if OUTPUT.exists():
        for line in OUTPUT.read_text().strip().split("\n"):
            if line:
                try: completed.add(json.loads(line)["trial_key"])
                except: pass

    pending = [t for t in trials if t.trial_key not in completed]
    print(f"RQ1 并行补完: {len(pending)} pending / {len(trials)} total, workers={WORKERS}")

    if not pending:
        print("All done!")
        return

    done = 0
    t0 = time.time()
    with ThreadPoolExecutor(max_workers=WORKERS) as ex:
        futures = {ex.submit(process_trial, t): t for t in pending}
        for fut in as_completed(futures):
            trial = futures[fut]
            done += 1
            try:
                status = fut.result()
                rate = done / (time.time() - t0) * 60
                print(f"  [{done}/{len(pending)}] {trial.model:16s} {trial.scenario_id:28s} "
                      f"{trial.condition:12s} {status:8s} ({rate:.1f}/min)")
            except Exception as e:
                print(f"  [{done}/{len(pending)}] EXCEPTION: {e}")

    print(f"\nDone in {time.time()-t0:.0f}s")

if __name__ == "__main__":
    main()
