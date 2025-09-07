import streamlit as st
import openai
from openai import OpenAI
import json
import time

# Page configuration
st.set_page_config(
    page_title="Simple Playground",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []
if "api_configured" not in st.session_state:
    st.session_state.api_configured = False

# Sidebar for API configuration and parameters
with st.sidebar:
    st.header("🔧 API Configuration")

    # API Token
    api_token = st.text_input(
        "API Token",
        type="password",
        placeholder="Enter your OpenAI API token",
        help="Your OpenAI API key"
    )

    # Base URL configuration
    use_default_url = st.checkbox("Use OpenAI default URL", value=False)

    if use_default_url:
        base_url = "https://api.openai.com/v1"
        st.info("Using default OpenAI URL")
    else:
        base_url = st.text_input(
            "Base URL",
            placeholder="https://api.openai.com/v1",
            help="Custom API base URL"
        )

    # Validate API configuration
    if api_token and base_url:
        st.session_state.api_configured = True
        st.success("✅ API configured")
    else:
        st.session_state.api_configured = False
        st.warning("⚠️ Please configure API settings")

    st.divider()

    # Chat Completion Parameters
    st.header("⚙️ Model Parameters")

    model = st.selectbox(
        "Model",
        ["gpt-4o", "gpt-4o-mini", "gpt-4-turbo",
            "gpt-3.5-turbo", "gpt-4", "gpt-4-32k"],
        index=0,
        help="Choose the OpenAI model"
    )

    temperature = st.slider(
        "Temperature",
        min_value=0.0,
        max_value=2.0,
        value=0.7,
        step=0.1,
        help="Controls randomness in responses"
    )

    max_tokens = st.number_input(
        "Max Tokens",
        min_value=1,
        max_value=8192,
        value=1000,
        help="Maximum number of tokens in response"
    )

    top_p = st.slider(
        "Top P",
        min_value=0.0,
        max_value=1.0,
        value=1.0,
        step=0.1,
        help="Nucleus sampling parameter"
    )

    frequency_penalty = st.slider(
        "Frequency Penalty",
        min_value=-2.0,
        max_value=2.0,
        value=0.0,
        step=0.1,
        help="Penalizes repeated tokens"
    )

    presence_penalty = st.slider(
        "Presence Penalty",
        min_value=-2.0,
        max_value=2.0,
        value=0.0,
        step=0.1,
        help="Penalizes tokens based on presence"
    )

    # System message
    st.subheader("System Message")
    system_message = st.text_area(
        "System Prompt",
        value="You are a helpful AI assistant.",
        height=100,
        help="System message to set the AI's behavior"
    )

    st.divider()

    # Chat management
    st.header("💬 Chat Management")

    if st.button("🗑️ Clear All Messages", type="secondary", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

# Main chat interface
st.title("🤖 OpenAI Playground")
st.markdown("### Interactive ChatGPT Interface with Custom Parameters")

# Check if API is configured
if not st.session_state.api_configured:
    st.error("❌ Please configure your API settings in the sidebar first.")
    st.stop()

# Initialize OpenAI client
try:
    client = OpenAI(
        api_key=api_token,
        base_url=base_url
    )
except Exception as e:
    st.error(f"❌ Failed to initialize OpenAI client: {str(e)}")
    st.stop()

# Display chat messages
chat_container = st.container()

with chat_container:
    for i, message in enumerate(st.session_state.messages):
        with st.chat_message(message["role"]):
            col1, col2 = st.columns([0.95, 0.05])

            with col1:
                st.markdown(message["content"])

            with col2:
                if st.button("🗑️", key=f"delete_{i}", help="Delete this message"):
                    st.session_state.messages.pop(i)
                    st.rerun()

# Chat input
if prompt := st.chat_input("Type your message here...", disabled=not st.session_state.api_configured):
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})

    # Display user message
    with st.chat_message("user"):
        st.markdown(prompt)

    # Prepare messages for API call
    api_messages = []

    # Add system message if provided
    if system_message.strip():
        api_messages.append({"role": "system", "content": system_message})

    # Add chat history
    api_messages.extend(st.session_state.messages)

    # Generate assistant response with streaming
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""

        try:
            # Create streaming response
            stream = client.chat.completions.create(
                model=model,
                messages=api_messages,
                temperature=temperature,
                max_tokens=max_tokens,
                top_p=top_p,
                frequency_penalty=frequency_penalty,
                presence_penalty=presence_penalty,
                stream=True
            )

            # Stream the response
            for chunk in stream:
                if chunk.choices[0].delta.content is not None:
                    full_response += chunk.choices[0].delta.content
                    message_placeholder.markdown(full_response + "▌")

            # Final display without cursor
            message_placeholder.markdown(full_response)

        except Exception as e:
            error_msg = f"❌ Error: {str(e)}"
            message_placeholder.markdown(error_msg)
            full_response = error_msg

    # Add assistant response to chat history
    st.session_state.messages.append(
        {"role": "assistant", "content": full_response})

# Footer with information
st.divider()
col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Total Messages", len(st.session_state.messages))

with col2:
    if st.session_state.messages:
        total_chars = sum(len(msg["content"])
                          for msg in st.session_state.messages)
        st.metric("Total Characters", total_chars)

with col3:
    st.metric("Model", model)

# Export chat functionality
if st.session_state.messages:
    st.subheader("📥 Export Chat")

    col1, col2 = st.columns(2)

    with col1:
        # Export as JSON
        chat_json = json.dumps(st.session_state.messages, indent=2)
        st.download_button(
            label="📄 Download as JSON",
            data=chat_json,
            file_name="chat_history.json",
            mime="application/json"
        )

    with col2:
        # Export as text
        chat_text = ""
        for msg in st.session_state.messages:
            role = msg["role"].upper()
            content = msg["content"]
            chat_text += f"{role}: {content}\n\n"

        st.download_button(
            label="📝 Download as Text",
            data=chat_text,
            file_name="chat_history.txt",
            mime="text/plain"
        )
