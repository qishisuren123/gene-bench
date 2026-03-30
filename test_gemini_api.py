#!/usr/bin/env python3
"""快速验证 Gemini API 连通性"""

import os
import sys

# 设置代理（如果需要代理访问 Google API，请设置 https_proxy 环境变量）
# os.environ["https_proxy"] = "http://your-proxy:port"
# os.environ["http_proxy"] = "http://your-proxy:port"

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")
if not GEMINI_API_KEY:
    print("ERROR: 请设置环境变量 GEMINI_API_KEY")
    sys.exit(1)

print("=== Gemini API 连通性测试 ===")
print(f"Key: {GEMINI_API_KEY[:10]}...{GEMINI_API_KEY[-4:]}")

try:
    import google.generativeai as genai
    print(f"google-generativeai version: {genai.__version__}")
except ImportError:
    print("ERROR: google-generativeai 未安装，正在安装...")
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "google-generativeai>=0.8"])
    import google.generativeai as genai
    print(f"安装成功，version: {genai.__version__}")

# 测试 1: 基础连接
print("\n--- 测试 1: gemini-2.5-flash 基础调用 ---")
try:
    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel("gemini-2.5-flash")
    resp = model.generate_content(
        "Return exactly: Hello Gene-Bench",
        generation_config=genai.GenerationConfig(max_output_tokens=50, temperature=0.0),
    )
    print(f"  Response: {resp.text[:100]}")
    print(f"  Input tokens: {getattr(resp.usage_metadata, 'prompt_token_count', '?')}")
    print(f"  Output tokens: {getattr(resp.usage_metadata, 'candidates_token_count', '?')}")
    print("  ✓ gemini-2.5-flash OK")
except Exception as e:
    print(f"  ✗ FAILED: {e}")
    sys.exit(1)

# 测试 2: system_instruction
print("\n--- 测试 2: system_instruction (Gene 注入模拟) ---")
try:
    model = genai.GenerativeModel(
        "gemini-2.5-flash",
        system_instruction="You are a Python expert. Use numpy for all numerical operations."
    )
    resp = model.generate_content(
        "Write a Python function that computes the mean of a list of numbers.",
        generation_config=genai.GenerationConfig(max_output_tokens=300, temperature=0.0),
    )
    text = resp.text
    has_code = "```python" in text or "def " in text
    print(f"  Response length: {len(text)} chars")
    print(f"  Contains Python code: {has_code}")
    print("  ✓ system_instruction OK")
except Exception as e:
    print(f"  ✗ FAILED: {e}")

# 测试 3: gemini-3-pro（如果可用）
print("\n--- 测试 3: gemini-3-pro ---")
try:
    model = genai.GenerativeModel("gemini-3-pro")
    resp = model.generate_content(
        "Return exactly: Hello from Pro",
        generation_config=genai.GenerationConfig(max_output_tokens=50, temperature=0.0),
    )
    print(f"  Response: {resp.text[:100]}")
    print("  ✓ gemini-3-pro OK")
except Exception as e:
    print(f"  ✗ FAILED: {e}")
    print("  (gemini-3-pro 可能需要更新 model name)")

print("\n=== 测试完成 ===")
