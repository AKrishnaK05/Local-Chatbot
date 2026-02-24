import streamlit as st
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
import torch
import os
import sheets_service

# --- Page Configuration ---
st.set_page_config(page_title="Local AI Chatbot", page_icon="🤖")

# Check for Google Sheets credentials
if not os.path.exists("service_account.json"):
    st.sidebar.warning("⚠️ `service_account.json` not found. Google Sheets logging is disabled.")
else:
    st.sidebar.success("✅ Google Sheets logging is active.")

st.markdown("""
<style>
    .stChatFloatingInputContainer {
        padding-bottom: 20px;
    }
</style>
""", unsafe_allow_html=True)

st.title("🤖 Local AI Chatbot")
st.caption("Powered by google/flan-t5-base | Running locally on CPU")

# --- Model Loading (Cached) ---
@st.cache_resource
def load_chatbot():
    """Loads the Flan-T5 model and tokenizer once and caches them."""
    model_name = "google/flan-t5-base"
    
    # Using AutoModel and AutoTokenizer for better reliability across library versions
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForSeq2SeqLM.from_pretrained(model_name)
    
    return {"model": model, "tokenizer": tokenizer}

# Initialize the model and tokenizer
chatbot_components = load_chatbot()
model = chatbot_components["model"]
tokenizer = chatbot_components["tokenizer"]

# --- Session State Management ---
if "messages" not in st.session_state:
    st.session_state.messages = []

# --- Helper Functions ---
def generate_response(user_input, chat_history):
    """
    Generates a response from the model using refined instruction-style prompting 
    and short-term memory cleaning.
    """
    # Maintain short-term memory (last 3 turns = 6 messages)
    context_window = chat_history[-6:]
    
    # Refined prompt for Flan-T5
    prompt = "Answer the following question as a helpful AI assistant content. "
    prompt += "Keep the response concise and friendly.\n\n"
    
    for msg in context_window:
        role = "Human" if msg["role"] == "user" else "Assistant"
        prompt += f"{role}: {msg['content']}\n"
    
    prompt += f"Human: {user_input}\nAssistant:"
    
    # Tokenize input
    inputs = tokenizer(prompt, return_tensors="pt")
    
    # Generate response with slightly tuned parameters
    with torch.no_grad():
        outputs = model.generate(
            **inputs, 
            max_new_tokens=100, # Concise responses
            do_sample=True, 
            temperature=0.4,    # Lower temperature for more factual/focused output
            top_p=0.9,
            repetition_penalty=1.2 # Prevent repetitive behavior seen in screenshot
        )
    
    # Decode
    response = tokenizer.decode(outputs[0], skip_special_tokens=True)
    
    # Post-processing: Strip "Assistant:" or "Human:" if the model hallucinated them
    if response.lower().startswith("assistant:"):
        response = response[len("assistant:"):].strip()
    if response.lower().startswith("human:"):
        response = response[len("human:"):].strip()
        
    return response

# --- UI Components ---

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# User input handled by chat_input
with st.container():
    col1, col2 = st.columns([0.85, 0.15])
    with col1:
        user_input = st.text_input("Type your message...", placeholder="Hello!", label_visibility="collapsed", key="user_input_box")
    with col2:
        send_button = st.button("Send", use_container_width=True)

if send_button and user_input:
    # Add user message to state
    st.session_state.messages.append({"role": "user", "content": user_input})
    
    # Display user message immediately
    with st.chat_message("user"):
        st.markdown(user_input)
    
    # Generate and display assistant response
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            ai_response = generate_response(user_input, st.session_state.messages[:-1])
            st.markdown(ai_response)
    
    # Add assistant response to state
    st.session_state.messages.append({"role": "assistant", "content": ai_response})
    
    # Save to Google Sheets
    sheets_service.append_chat(user_input, ai_response)
    
    st.rerun()

# Information for the user
with st.sidebar:
    st.header("About")
    st.info("""
    This chatbot runs entirely on your local machine.
    - **Language**: Python
    - **Framework**: Streamlit
    - **Model**: google/flan-t5-base
    - **Storage**: Logged to Google Sheets
    """)
    if st.button("Clear Chat"):
        st.session_state.messages = []
        st.rerun()
