# Module 03 — Building Agents as Stateful Systems + Docker

## What this module covers
- What makes an agent stateful — conversation history, session identity, and turn tracking
- How LangGraph builds a graph of nodes that each read and write to a shared state
- How checkpointers persist agent state so conversations survive process restarts
- Streaming responses token by token from a FastAPI endpoint to a Streamlit UI
- Containerising the application with Docker

---

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

## What happens inside SQLite (explain to students)

Every time the agent completes a turn, LangGraph's `SqliteSaver` writes the full conversation state to a local SQLite file at `data/app.db`. The database has one table: `checkpoints`.

Each row stores:
- `thread_id` — the session ID (identifies which conversation this belongs to)
- `checkpoint` — the full serialised state (all messages, turn count, metadata)
- `metadata` — LangGraph version info and step number

When the same `thread_id` is used again (next message, or after a server restart), LangGraph reads the latest checkpoint for that thread and resumes from there. The agent never loses context as long as the SQLite file exists.

**Student mode vs Enterprise mode:**
```
Student:    data/app.db          (local file, single process)
Enterprise: PostgreSQL table     (shared DB, survives container restarts, multi-process safe)
```

You can inspect the SQLite database directly:
```bash
# Windows — open with DB Browser for SQLite (free tool)
# Or via Python:
python -c "import sqlite3; conn = sqlite3.connect('data/app.db'); print(conn.execute('SELECT thread_id, checkpoint_ns FROM checkpoints').fetchall())"
```

---

## Full request flow (explain to students)

```
Student types a message in Streamlit UI
        │
        ▼
Streamlit sends POST /api/v1/chat/stream
  { session_id: "uuid", message: "What is LangGraph?" }
        │
        ▼
FastAPI chat.py receives the request
  → calls research_agent.stream(session_id, message)
        │
        ▼
research_agent.py calls get_graph()
  → get_graph() calls build_graph() on first request only
  → build_graph() calls get_checkpointer()
  → checkpointer loads last saved state for this session_id from SQLite
        │
        ▼
LangGraph runs the graph (one node: call_llm)
  → call_llm reads state.messages (full history)
  → builds messages list: [system prompt] + [all prior turns] + [new message]
  → calls llm_client.chat() → OpenRouter API → LLM responds
  → returns updated state with new assistant message appended
        │
        ▼
LangGraph checkpointer saves updated state back to SQLite
        │
        ▼
FastAPI StreamingResponse yields reply chunks back to Streamlit
        │
        ▼
Streamlit renders chunks as they arrive (▌ cursor effect)
```

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

## Code walkthrough — what to explain line by line

### app/agents/state.py
```python
class AgentState(TypedDict):
    messages: Annotated[list, add_messages]  # add_messages means APPEND not REPLACE
    session_id: str                           # identifies the conversation
    turn_count: int                           # tracks how many exchanges have happened
```
Key point: `add_messages` is what makes LangGraph accumulate history instead of overwriting it.

### app/agents/checkpointer.py
```python
conn = sqlite3.connect(str(db_path), check_same_thread=False)
return SqliteSaver(conn)
```
Key point: we pass a raw sqlite3 connection — not the context manager — because the connection must stay open for the lifetime of the app.

### app/agents/research_agent.py
```python
def call_llm(state: AgentState) -> dict:
    # rebuilds the full message history from state every single turn
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    for msg in state["messages"]:
        ...
    response = chat(messages, tier=ModelTier.DEFAULT)
    return {
        "messages": [{"role": "assistant", "content": reply}],
        "turn_count": state.get("turn_count", 0) + 1,
    }
```
Key point: the node receives the full accumulated state and returns only what changed. LangGraph merges the return value back into state automatically.

---

## What changed from Module 02
- The platform can now hold a stateful multi-turn conversation, not just answer one question
- State is persisted to SQLite — conversations survive a server restart
- The API has a streaming endpoint in addition to the standard JSON one
- The Streamlit UI is now a real streaming chat interface

## Failure scenarios to test
| Scenario | How to trigger | Expected behaviour |
|---|---|---|
| LLM timeout | Use a bad model name in .env | RuntimeError after 3 retries — API returns 503 |
| Invalid API key | Wrong key in .env | ValueError — API returns 401 with a clear message |
| ModuleNotFoundError on init_db | PYTHONPATH not set | Run `$env:PYTHONPATH="."` then retry |

## Cost to watch
Each conversation turn costs one LLM call. With `MODEL_DEFAULT` (GPT-4o) and a short prompt, expect roughly $0.001 to $0.005 per turn. Use `MODEL_CHEAP` in `.env` during development to reduce cost.

## Diagram (see PowerPoint slides)
- LangGraph state machine — nodes, edges, state TypedDict
- Checkpointer flow — how state is saved and loaded per thread_id
- Full request flow — Streamlit → FastAPI → Agent → LangGraph → SQLite → LLM → back
- What gets stored in SQLite — thread_id, checkpoint, message history
- Docker container diagram — what runs inside, what ports are exposed

## Discussion questions
1. The agent uses `thread_id` to identify a conversation. What happens if two users accidentally share the same session ID?
2. Why does `add_messages` matter in the state schema? What would happen if you used a plain list instead?
3. In student mode the checkpointer writes to SQLite. What breaks first if 50 students run the same app on the same SQLite file?
