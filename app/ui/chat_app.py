"""
Streamlit chat UI (Module 03).
Streams responses token by token from /api/v1/chat/stream.
Run: streamlit run app/ui/chat_app.py
"""
import uuid
import requests
import streamlit as st

API_BASE = "http://localhost:8000/api/v1"

st.set_page_config(page_title="Enterprise AI Assistant", layout="wide")
st.title("Enterprise Research and Knowledge Assistant")
st.caption("Module 03 — Stateful streaming agent")

if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())
if "messages" not in st.session_state:
    st.session_state.messages = []

with st.sidebar:
    st.markdown("### Session")
    st.code(st.session_state.session_id[:8] + "...", language=None)
    if st.button("New session"):
        st.session_state.session_id = str(uuid.uuid4())
        st.session_state.messages = []
        st.rerun()

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if prompt := st.chat_input("Ask anything..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        reply_box = st.empty()
        full_reply = ""
        try:
            with requests.post(
                f"{API_BASE}/chat/stream",
                json={"session_id": st.session_state.session_id, "message": prompt},
                stream=True,
                timeout=60,
            ) as resp:
                for chunk in resp.iter_content(chunk_size=None, decode_unicode=True):
                    if chunk:
                        full_reply += chunk
                        reply_box.markdown(full_reply + "▌")
            reply_box.markdown(full_reply)
        except Exception as e:
            full_reply = f"[error connecting to API: {e}]"
            reply_box.markdown(full_reply)

    st.session_state.messages.append({"role": "assistant", "content": full_reply})
