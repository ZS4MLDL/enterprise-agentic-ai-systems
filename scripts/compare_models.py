"""
Module 02 — Model comparison script.

Sends the same prompt to three models and prints a side-by-side comparison
of the response, token usage, and estimated cost.

Run:
    python scripts/compare_models.py
    python scripts/compare_models.py --prompt "Explain RAG in one sentence"
"""
import argparse
import sys
import time
from pathlib import Path

# Allow running from project root without installing the package
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.common.cost_tracker import estimate_cost
from app.common.llm_client import chat
from app.config.settings import get_settings

DEFAULT_PROMPT = "Explain what a large language model is in exactly two sentences."

MODELS = [
    ("openai/gpt-4o-mini",          "GPT-4o Mini   (cheap tier) "),
    ("openai/gpt-4o",               "GPT-4o        (default tier)"),
    ("anthropic/claude-sonnet-4-6", "Claude Sonnet (powerful tier)"),
]


def run_comparison(prompt: str) -> None:
    s = get_settings()
    if not s.OPENROUTER_API_KEY:
        print("ERROR: OPENROUTER_API_KEY is not set in your .env file.")
        sys.exit(1)

    print("\n" + "=" * 70)
    print(f"  PROMPT: {prompt}")
    print("=" * 70)

    results = []
    for model_id, label in MODELS:
        print(f"\n  Calling {label.strip()} ...", end=" ", flush=True)
        t0 = time.perf_counter()

        try:
            response = chat(
                [{"role": "user", "content": prompt}],
                model=model_id,
                temperature=0.3,
                max_tokens=256,
            )
            elapsed = time.perf_counter() - t0
            reply = response.choices[0].message.content.strip()
            usage = response.usage
            cost = estimate_cost(model_id, usage.prompt_tokens, usage.completion_tokens)
            results.append((label, reply, usage, cost, elapsed, None))
            print(f"done ({elapsed:.1f}s)")

        except Exception as e:
            elapsed = time.perf_counter() - t0
            results.append((label, None, None, None, elapsed, str(e)))
            print(f"FAILED ({e})")

    print("\n" + "=" * 70)
    print("  RESULTS")
    print("=" * 70)

    total_cost = 0.0
    for label, reply, usage, cost, elapsed, error in results:
        print(f"\n  [{label}]")
        if error:
            print(f"    ERROR: {error}")
            continue
        print(f"    Response : {reply}")
        print(f"    Tokens   : {usage.prompt_tokens} in + {usage.completion_tokens} out = {usage.total_tokens} total")
        print(f"    Cost     : ${cost:.6f} USD")
        print(f"    Time     : {elapsed:.1f}s")
        total_cost += cost

    print("\n" + "-" * 70)
    print(f"  Total estimated cost for this comparison: ${total_cost:.6f} USD")
    print("=" * 70 + "\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Compare three LLM models on the same prompt.")
    parser.add_argument("--prompt", default=DEFAULT_PROMPT, help="Prompt to send to all models")
    args = parser.parse_args()
    run_comparison(args.prompt)
