# Module 03 — Building Agents as Stateful Systems + Docker

## What this module covers
- What makes an agent stateful — conversation history, session identity, and turn tracking
- How LangGraph builds a graph of nodes that each read and write to a shared state
- How checkpointers persist agent state so conversations survive process restarts
- Streaming responses token by token from a FastAPI endpoint to a Streamlit UI
- Containerising the application with Docker

## What to do in this module

### Step 1 — Setup
```bash
git clone https://github.com/ZS4MLDL/enterprise-agentic-ai-systems.git
cd enterprise-agentic-ai-systems
git checkout module/03
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
# add OPENROUTER_API_KEY to .env
# if you get ModuleNotFoundError, run this first:
$env:PYTHONPATH="."
python scripts/init_db.py
```

### Step 2 — Start the API server
```bash
uvicorn app.main:app --reload
```
API is now live at http://localhost:8000. Test it:
```bash
curl -X POST http://localhost:8000/api/v1/chat \
  -H "Content-Type: application/json" \
  -d "{\"session_id\": \"test-1\", \"message\": \"What is LangGraph?\"}"
```

### Step 3 — Start the Streamlit UI (new terminal)
```bash
streamlit run app/ui/chat_app.py
```
Open http://localhost:8501. Chat with the agent. Click "New session" in the sidebar to start a fresh conversation.

### Step 4 — Test resume after interrupt
1. Send a message — note the session ID shown in the sidebar
2. Stop the API server (Ctrl+C)
3. Restart the server (`uvicorn app.main:app --reload`)
4. Send another message in the same session — the agent remembers the previous conversation

### Step 5 — Run the tests
```bash
pytest tests/unit/ -v
```
18 tests, all green. No real API or database calls are made.

---

## All files in this module

| Status | File | What to explain to students |
|---|---|---|
| NEW | `app/agents/state.py` | Defines `AgentState` — the TypedDict that flows through every LangGraph node. `messages` uses `add_messages` so each node appends rather than replaces. |
| NEW | `app/agents/checkpointer.py` | Returns `SqliteSaver` in student mode, `PostgresSaver` in enterprise mode. One function, one MODE check — this is the dual-mode pattern in action. |
| NEW | `app/agents/research_agent.py` | The stateful agent. One node (`call_llm`) reads state, calls the LLM, returns updated state. `run()` and `stream()` are the two public entry points. |
| UPDATED | `app/api/v1/chat.py` | Now wired to `research_agent.run()` and `research_agent.stream()`. Added `/chat/stream` endpoint that returns a `StreamingResponse`. |
| UPDATED | `app/ui/chat_app.py` | Now streams responses chunk by chunk using `requests` streaming. The `▌` cursor shows the response is still arriving. |
| NEW | `tests/unit/test_agent.py` | Tests for `call_llm` node, `run()`, resume simulation, and all three FastAPI endpoint scenarios (success, 401, 503). |
| EXISTS | `app/agents/base.py` | `BaseAgent` ABC — not used by `research_agent` directly yet, but all specialist agents in later modules will inherit from it. |
| EXISTS | `docker/Dockerfile` | Containerises the FastAPI app. Build: `docker build -f docker/Dockerfile -t enterprise-ai .` |
| EXISTS | `app/common/llm_client.py` | Called inside `call_llm` node — this is the integration point from Module 02. |

---

## What changed from Module 02
- The platform can now hold a stateful multi-turn conversation, not just answer one question
- State is persisted to SQLite — conversations survive a server restart
- The API has a streaming endpoint in addition to the standard JSON one
- The Streamlit UI is now a real streaming chat interface

## Failure scenarios to test
| Scenario | How to trigger | Expected behaviour |
|---|---|---|
| LLM timeout | Set a very short timeout in llm_client.py or use a bad model name | RuntimeError after 3 retries — API returns 503 |
| Invalid API key | Wrong key in .env | ValueError — API returns 401 with a clear message |
| DB not initialised | Skip `python scripts/init_db.py` | SqliteSaver creates the file automatically on first call |

## Cost to watch
Each conversation turn costs one LLM call. With `MODEL_DEFAULT` (GPT-4o) and a short prompt, expect roughly $0.001 to $0.005 per turn. Use `MODEL_CHEAP` in `.env` during development to reduce cost.

## Diagram (see PowerPoint slides)
- LangGraph state machine — nodes, edges, state TypedDict
- Checkpointer flow — how state is saved and loaded per thread_id
- Request flow — Streamlit → FastAPI → Agent → LLM → back
- Docker container diagram — what runs inside, what ports are exposed

## Discussion questions
1. The agent uses `thread_id` to identify a conversation. What happens if two users accidentally share the same session ID?
2. Why does `add_messages` matter in the state schema? What would happen if you used a plain list instead?
3. In student mode the checkpointer writes to SQLite. What breaks first if 50 students run the same app on the same SQLite file?
