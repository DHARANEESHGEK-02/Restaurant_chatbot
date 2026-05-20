# chatbot/memory.py
# Handles conversation memory so the bot remembers previous messages

import streamlit as st


def init_memory():
    """
    Initialize chat memory in Streamlit session state.
    Call this once at the start of the app.
    """
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []


def add_message(role: str, content: str):
    """
    Add a message to chat history.
    
    Args:
        role: "user" or "assistant"
        content: The message text
    """
    st.session_state.chat_history.append({
        "role": role,
        "content": content
    })


def get_chat_history() -> list:
    """
    Return the full chat history list.
    """
    return st.session_state.chat_history


def format_history_for_prompt(max_turns: int = 10) -> str:
    """
    Format recent chat history into a string for the LLM prompt.
    Keeps only the last `max_turns` exchanges to avoid token overflow.
    
    Args:
        max_turns: Max number of conversation turns to include
        
    Returns:
        Formatted string of chat history
    """
    history = st.session_state.get("chat_history", [])
    
    # Take only recent messages (2 messages per turn: user + assistant)
    recent = history[-(max_turns * 2):]
    
    if not recent:
        return "No previous conversation."
    
    formatted = []
    for msg in recent:
        label = "Customer" if msg["role"] == "user" else "Bistro AI"
        formatted.append(f"{label}: {msg['content']}")
    
    return "\n".join(formatted)


def clear_memory():
    """
    Wipe all chat history (used on session reset).
    """
    st.session_state.chat_history = []
