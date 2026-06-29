# Module 02 — LLMs, Reasoning, and Context Engineering

## What this module covers
- How large language models work (just enough theory to reason about them)
- Context windows, token budgeting, and why they matter for cost
- Building a provider-agnostic LLM client that every future module reuses
- Comparing models on quality, speed, and cost for the same prompt

## What to do in this module

### Step 1 — Setup
```bash
git clone https://github.com/ZS4MLDL/enterprise-agentic-ai-systems.git
cd enterprise-agentic-ai-systems
git checkout module/02
python -m venv .venv
.venv\Scripts\activate          # Windows
pip install -r requirements.txt
cp .env.example .env
# Open .env and set OPENROUTER_API_KEY=sk-or-...
```

### Step 2 — Compare three models
```bash
python scripts/compare_models.py
```
You will see the same prompt sent to GPT-4o Mini, GPT-4o, and Claude Sonnet.
Output shows the response, token count, estimated cost, and response time for each.

Try your own prompt:
```bash
python scripts/compare_models.py --prompt "What is retrieval-augmented generation?"
```

### Step 3 — Run the tests
```bash
pytest tests/unit/ -v
```
All 11 tests should pass. No API calls are made — responses are mocked.

### Step 4 — Read the key files
```
app/config/settings.py          — central config, MODE switch, all env vars
app/config/model_registry.py    — model tiers (cheap / default / powerful)
app/common/llm_client.py        — the LLM wrapper every module uses
app/common/cost_tracker.py      — token and cost logging per call
```

## What changed from Module 01
- `app/common/llm_client.py` is now a real working client, not a placeholder
- `app/common/cost_tracker.py` is new — tracks tokens and estimated cost per call
- `scripts/compare_models.py` is new — the main demo script for this module
- Unit tests now cover retry logic, auth failure, and cost estimation

## Failure scenarios to test
| Scenario | How to trigger | Expected behaviour |
|---|---|---|
| Invalid API key | Set a wrong key in .env | Clear error: "Invalid API key — check OPENROUTER_API_KEY" |
| Rate limit (429) | Covered in unit tests | Retries up to 3 times with backoff, then raises RuntimeError |

## Cost to watch
Running `compare_models.py` once costs roughly $0.002 to $0.005 USD total
across all three models. Safe to run many times during the session.

## Key files introduced this module
| File | Purpose |
|---|---|
| `app/common/llm_client.py` | Single entry point for all LLM calls — imported by every later module |
| `app/common/cost_tracker.py` | Logs token usage and estimated cost per call |
| `app/config/settings.py` | Reads all env vars, exposes MODE switch |
| `app/config/model_registry.py` | Maps cheap/default/powerful tiers to model IDs |
| `scripts/compare_models.py` | Side-by-side model comparison demo |

## Diagram (see PowerPoint slides)
- How a transformer processes a prompt (simplified)
- Context window diagram — what fits, what gets cut
- Token cost comparison across the three models
- llm_client.py call flow with retry and cost logging

## Discussion questions
1. Why use a model tier (cheap/default/powerful) instead of calling a specific model by name everywhere?
2. If GPT-4o Mini gives an acceptable answer for 95% of questions, what would you use the powerful tier for?
3. The cost tracker estimates cost — it does not call the provider billing API. What could go wrong with this approach at scale?
