import streamlit as st
import openai
from openai import OpenAI
import json
import time

# --- Utility: token estimation ---
_tokenizer = None

def estimate_tokens(text: str) -> int:
    """Estimate token count for a given text.
    Tries tiktoken if available, otherwise falls back to simple heuristics.
    """
    global _tokenizer
    if not text:
        return 0
    if _tokenizer is None:
        try:
            import tiktoken  # type: ignore
            _tokenizer = tiktoken.get_encoding("cl100k_base")
        except Exception:
            _tokenizer = False  # sentinel for fallback
    if _tokenizer and _tokenizer is not False:
        try:
            return len(_tokenizer.encode(text))
        except Exception:
            pass
    # Fallback: rough estimate (split on whitespace or chars/4)
    words = text.strip().split()
    if words:
        return len(words)
    return max(1, len(text) // 4)

# Page configuration
st.set_page_config(
    page_title="Playground",
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
        placeholder="Enter your API token/key",
        help="Your provider API key/token"
    )

    # Base URL configuration
    use_default_url = st.checkbox("Use sample base URL (/v1)", value=False, help="Uses a common /v1-style base URL (e.g., local runtimes)")

    if use_default_url:
        base_url = "http://localhost:11434/v1"
        st.info("Using sample /v1 base URL (localhost)")
    else:
        base_url = st.text_input(
            "Base URL",
            placeholder="e.g., http://localhost:11434/v1 or https://your-provider.example.com/v1",
            help="Set your provider's base URL"
        )

    # Validate API configuration (token optional)
    if base_url:
        st.session_state.api_configured = True
        if api_token:
            st.success("✅ API configured")
        else:
            st.info("ℹ️ Base URL set. API token is optional for some providers.")
    else:
        st.session_state.api_configured = False
        st.warning("⚠️ Please configure API settings")

    st.divider()

    # Chat Completion Parameters
    st.header("⚙️ Model Parameters")

    model = st.text_input(
        "Model name",
        value="",
        placeholder="e.g., llama3.1, gpt-4o-mini, mixtral-8x7b, qwen2.5",
        help="Enter the exact model identifier expected by your provider"
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
        max_value=32768,
        value=1024,
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
        value="You are a helpful assistant.",
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
st.title("🤖 Playground")
st.markdown("### Interactive chat interface with custom parameters")

# Check if API is configured
if not st.session_state.api_configured:
    st.error("❌ Please configure your API settings in the sidebar first.")
    st.stop()

# Initialize API client
try:
    client_kwargs = {"base_url": base_url}
    if api_token:
        client_kwargs["api_key"] = api_token
    client = OpenAI(**client_kwargs)
except (openai.APIError, openai.APIConnectionError, openai.AuthenticationError, openai.RateLimitError, ValueError) as e:
    st.error(f"❌ Failed to initialize API client: {str(e)}")
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

    # Validate model
    if not model.strip():
        with st.chat_message("assistant"):
            st.error("Please enter a model name in the sidebar.")
        st.stop()

    # Generate assistant response with streaming
    with st.chat_message("assistant"):
        stats_placeholder = st.empty()
        message_placeholder = st.empty()
        full_response = ""
        tokens_so_far = 0
        request_start = time.perf_counter()
        first_token_time = None

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
                    piece = chunk.choices[0].delta.content
                    # TTFT
                    if first_token_time is None:
                        first_token_time = time.perf_counter()
                    # Accumulate
                    full_response += piece
                    tokens_so_far += estimate_tokens(piece)
                    # Update content
                    message_placeholder.markdown(full_response + "▌")
                    # Update live stats
                    if first_token_time is not None:
                        gen_elapsed = max(1e-6, time.perf_counter() - first_token_time)
                        avg_tps = tokens_so_far / gen_elapsed
                        ttft_ms = (first_token_time - request_start) * 1000.0
                        stats_placeholder.markdown(
                            f"⏱ TTFT: {ttft_ms:.0f} ms | 🔢 tokens: {tokens_so_far} | ⚡ avg TPS: {avg_tps:.2f}"
                        )

            # Final display without cursor
            message_placeholder.markdown(full_response)
            # Final metrics
            end_time = time.perf_counter()
            if first_token_time is not None:
                gen_elapsed = max(1e-6, end_time - first_token_time)
                final_tps = tokens_so_far / gen_elapsed
                ttft_s = first_token_time - request_start
                stats_placeholder.markdown(
                    f"⏱ TTFT: {ttft_s*1000.0:.0f} ms | 🔢 tokens: {tokens_so_far} | ⚡ avg TPS: {final_tps:.2f}"
                )
                # Save metrics to session
                st.session_state["last_ttft_s"] = ttft_s
                st.session_state["last_tokens"] = tokens_so_far
                st.session_state["last_tps"] = final_tps
                st.session_state["last_gen_seconds"] = gen_elapsed
            else:
                # No content received
                st.session_state["last_ttft_s"] = None
                st.session_state["last_tokens"] = 0
                st.session_state["last_tps"] = 0.0
                st.session_state["last_gen_seconds"] = 0.0

        except (openai.APIError, openai.APIConnectionError, openai.AuthenticationError, openai.RateLimitError, ValueError) as e:
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

# Performance metrics summary
if st.session_state.get("last_ttft_s") is not None:
    st.subheader("⚡ Performance (last response)")
    m1, m2, m3, m4 = st.columns(4)
    with m1:
        st.metric("TTFT", f"{st.session_state['last_ttft_s']*1000.0:.0f} ms")
    with m2:
        st.metric("Avg TPS", f"{st.session_state['last_tps']:.2f}")
    with m3:
        st.metric("Tokens", st.session_state.get("last_tokens", 0))
    with m4:
        st.metric("Gen Time", f"{st.session_state.get('last_gen_seconds', 0.0):.2f} s")

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
