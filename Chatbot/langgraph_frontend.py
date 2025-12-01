import uuid
import streamlit as st
from langchain_core.messages import HumanMessage, AIMessage
from langgraph_backend import (
    chatbot,
    ingest_pdf,
    retrieve_all_threads,
    thread_document_metadata,
)

# **************************************** Utility Functions *************************

def generate_thread_id():
    return uuid.uuid4()

def reset_chat():
    thread_id = generate_thread_id()
    st.session_state['thread_id'] = thread_id
    add_thread(thread_id)
    st.session_state['message_history'] = []

def add_thread(thread_id):
    if thread_id not in st.session_state['chat_threads']:
        st.session_state['chat_threads'].append(thread_id)

def load_conversation(thread_id):
    state = chatbot.get_state(config={'configurable': {'thread_id': thread_id}})
    return state.values.get('messages', [])

def get_thread_title(thread_id):
    """Return a nice title to show in sidebar for this thread."""
    messages = load_conversation(thread_id)

    # default title if no user messages exist yet
    title = "New chat"

    for msg in messages:
        if isinstance(msg, HumanMessage):
            # Use the first user message as title
            raw = msg.content.strip()
            if not raw:
                break
            # truncate for cleanliness
            max_len = 40
            title = raw if len(raw) <= max_len else raw[:max_len] + "..."
            break

    return title

# **************************************** Session Setup ******************************

if 'message_history' not in st.session_state:
    st.session_state['message_history'] = []

if 'thread_id' not in st.session_state:
    st.session_state['thread_id'] = generate_thread_id()

if 'chat_threads' not in st.session_state:
    st.session_state['chat_threads'] = retrieve_all_threads()

if 'ingested_docs' not in st.session_state:
    st.session_state['ingested_docs'] = {}

add_thread(st.session_state['thread_id'])

# **************************************** Sidebar UI *********************************

st.sidebar.title('LangGraph Chatbot')

if st.sidebar.button('New Chat'):
    reset_chat()

st.sidebar.header('My Conversations')

for thread_id in st.session_state['chat_threads'][::-1]:
    label = get_thread_title(thread_id)
    if st.sidebar.button(label=label, key=str(thread_id)):
        st.session_state['thread_id'] = thread_id
        messages = load_conversation(thread_id)

        temp_messages = []

        for msg in messages:
            if isinstance(msg, HumanMessage):
                role = 'user'
            else:
                role = 'assistant'
            temp_messages.append({'role': role, 'content': msg.content})

        st.session_state['message_history'] = temp_messages

# **************************************** Main UI ************************************

st.title("💬 LangGraph Chatbot")

# PDF uploader at the top
uploaded_pdf = st.file_uploader(
    label="📄 Upload a PDF document",
    type=["pdf"],
    accept_multiple_files=False,
    help="Upload a PDF to enable document-based Q&A"
)

if uploaded_pdf:
    thread_key = str(st.session_state['thread_id'])
    thread_docs = st.session_state['ingested_docs'].setdefault(thread_key, {})
    
    # Only process if this file hasn't been indexed for this thread yet
    if uploaded_pdf.name not in thread_docs:
        with st.spinner(f"📚 Indexing {uploaded_pdf.name}..."):
            summary = ingest_pdf(
                uploaded_pdf.getvalue(),
                thread_id=thread_key,
                filename=uploaded_pdf.name
            )
            thread_docs[uploaded_pdf.name] = summary
            st.success(f"✅ {uploaded_pdf.name} indexed successfully!")
            st.rerun()

# Display indexed documents for current thread
thread_key = str(st.session_state['thread_id'])
if thread_key in st.session_state['ingested_docs'] and st.session_state['ingested_docs'][thread_key]:
    with st.expander("📚 Indexed Documents"):
        for filename, meta in st.session_state['ingested_docs'][thread_key].items():
            st.write(f"**{filename}** - {meta.get('documents', 0)} pages, {meta.get('chunks', 0)} chunks")

st.divider()

# Display chat messages container
chat_container = st.container()

with chat_container:
    # Check if message_history is empty and add welcome message
    if len(st.session_state['message_history']) == 0:
        st.session_state['message_history'].append({
            'role': 'assistant', 
            'content': "Hello! How may I assist you today? You can ask me questions, search the web, get stock prices, or upload a PDF to ask questions about it."
        })
    
    # Display conversation history
    for message in st.session_state['message_history']:
        with st.chat_message(message['role']):
            st.markdown(message['content'])

# Chat input at the bottom
user_input = st.chat_input("Type your message here...")

if user_input:
    # Add user message to history
    st.session_state['message_history'].append({'role': 'user', 'content': user_input})
    
    # Display user message
    with chat_container:
        with st.chat_message('user'):
            st.markdown(user_input)
    
    # Generate AI response
    CONFIG = {
        'configurable': {'thread_id': str(st.session_state['thread_id'])},
        'metadata': {'thread_id': str(st.session_state['thread_id'])},
        'run_name': "chat_run"
    }
    
    with chat_container:
        with st.chat_message("assistant"):
            def ai_only_stream():
                for message_chunk, metadata in chatbot.stream(
                    {"messages": [HumanMessage(content=user_input)]},
                    config=CONFIG,
                    stream_mode="messages"
                ):
                    if isinstance(message_chunk, AIMessage):
                        yield message_chunk.content
            
            ai_message = st.write_stream(ai_only_stream())
    
    # Add assistant message to history
    st.session_state['message_history'].append({'role': 'assistant', 'content': ai_message})
    
    # Rerun to update the display
    st.rerun()
