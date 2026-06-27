"""
Streamlit chat UI (Module 03 thin shell — grows through the course).
Run: streamlit run app/ui/chat_app.py
"""
import uuid
import streamlit as st
import requests

API_BASE = "http://localhost:8000/api/v1"

st.set_page_config(page_title="Enterprise AI Assistant", layout="wide")
st.title("Enterprise Research and Knowledge Assistant")

if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())
if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if prompt := st.chat_input("Ask anything..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                resp = requests.post(
                    f"{API_BASE}/chat",
                    json={"session_id": st.session_state.session_id, "message": prompt},
                    timeout=60,
                )
                reply = resp.json().get("reply", "[no reply]")
            except Exception as e:
                reply = f"[error: {e}]"
        st.markdown(reply)
        st.session_state.messages.append({"role": "assistant", "content": reply})
