from pathlib import Path
import sys

# Ensure repo root is on PYTHONPATH so `import app...` works in Streamlit pages
_repo_root = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(_repo_root))
import streamlit as st
from openai import OpenAI

SYSTEM_PROMPTS = {
    "Cybersecurity": (
        "You are a cybersecurity expert assistant. "
        "Analyze incidents, threats, and provide technical guidance."
    ),
    "IT Operations": (
        "You are an IT operations expert assistant. "
        "Help troubleshoot issues, optimize systems, and manage tickets."
    ),
}


# STEP 0: Domain selection (default domain)
st.session_state.setdefault("domain", "Cybersecurity")


# Page configuration 
st.set_page_config(
    page_title="ChatGPT Assistant",
    page_icon="💬",
    layout="wide",
)

# Create client 
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# Page title
st.title("💬 ChatGPT - OpenAI API")
st.caption("Powered by GPT-4o")

# STEP 1: Initialize session state 
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "system", "content": SYSTEM_PROMPTS[st.session_state.domain]}
    ]

# Sidebar controls
with st.sidebar:
    st.title("💬 Chat Controls")

    # Show message count
    message_count = len([m for m in st.session_state.messages if m["role"] != "system"])
    st.metric("Messages", message_count)

    # Clear chat button
    if st.button("🗑️ Clear Chat", use_container_width=True):
        st.session_state.messages = [
            {"role": "system", "content": SYSTEM_PROMPTS[st.session_state.domain]}
        ]
        st.rerun()

    # Model selection
    model = st.selectbox(
        "Model",
        ["gpt-4o", "gpt-4o-mini"],
        index=0,
    )

    # Temperature slider
    temperature = st.slider(
        "Temperature",
        min_value=0.0,
        max_value=2.0,
        value=1.0,
        step=0.1,
        help="Higher values make output more random",
    )

    # Domain selection
    st.selectbox(
        "Domain",
        ["Cybersecurity", "IT Operations"],
        key="domain",
    )

# If the domain changes, reset the conversation to the correct system prompt
if st.session_state.get("current_domain") != st.session_state.domain:
    st.session_state.current_domain = st.session_state.domain
    st.session_state.messages = [
        {"role": "system", "content": SYSTEM_PROMPTS[st.session_state.domain]}
    ]
    st.rerun()

# STEP 2: Display chat history
for message in st.session_state.messages:
    if message["role"] != "system":
        with st.chat_message(message["role"]):
            st.write(message["content"])


# STEP 3: User input
user_input = st.chat_input("Type your message...")


if user_input:
    # Show user message
    with st.chat_message("user"):
        st.markdown(user_input)

    st.session_state.messages.append({"role": "user", "content": user_input})

    # STEP 4: Get AI response with streaming
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""

        try:
            with st.spinner("Thinking..."):
                response = client.chat.completions.create(
                    model=model,
                    messages=st.session_state.messages,
                    temperature=temperature,
                    stream=True,
                )

            for chunk in response:
                delta = chunk.choices[0].delta
                if delta and delta.content is not None:
                    full_response += delta.content
                    message_placeholder.markdown(full_response + "▌")

            # Final render (remove cursor)
            message_placeholder.markdown(full_response)

        except Exception as e:
            st.error(f"OpenAI API error: {type(e).__name__}: {e}")

    # STEP 5: Save assistant message (only if we got content)
    if full_response.strip():
        st.session_state.messages.append({"role": "assistant", "content": full_response})