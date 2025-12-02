import streamlit as st
import asyncio
from dotenv import load_dotenv
from langgraph.types import RunnableConfig
from supervisor import graph as supervisor_graph, SupervisorState
from langchain_core.messages import HumanMessage, AIMessageChunk

load_dotenv()

# Page configuration
st.set_page_config(
    page_title="Multi-Agent AI System",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Agent styling configuration
AGENT_STYLES = {
    'researcher': {'color': '#00CED1', 'emoji': '🔬', 'name': 'Researcher'},
    'copywriter': {'color': '#FF1493', 'emoji': '✍️', 'name': 'Copywriter'},
    'supervisor': {'color': '#32CD32', 'emoji': '🎯', 'name': 'Supervisor'},
}

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []
if "thread_id" not in st.session_state:
    st.session_state.thread_id = "1"
if "is_processing" not in st.session_state:
    st.session_state.is_processing = False
if "pending_query" not in st.session_state:
    st.session_state.pending_query = None

async def stream_graph_responses_to_streamlit(
    input_state: SupervisorState,
    graph,
    placeholder,
    status_placeholder,
    **kwargs
):
    """Stream graph responses to Streamlit with agent-specific formatting."""
    
    # Track current AI message source to detect transitions
    current_ai_source = None
    current_content = ""
    current_tool_name = ""
    agent_responses = []
    
    async for chunk in graph.astream(
        input=input_state,
        stream_mode="messages",
        subgraphs=True,
        **kwargs
    ):
        # When subgraphs=True, the structure is (namespace, (message_chunk, metadata))
        namespace, (message_chunk, _) = chunk
        
        if isinstance(message_chunk, AIMessageChunk):
            # Determine the source of this AI message from namespace
            if namespace:
                namespace_str = str(namespace)
                if "call_researcher" in namespace_str:
                    ai_source = "researcher"
                elif "call_copywriter" in namespace_str:
                    ai_source = "copywriter"
                else:
                    ai_source = "researcher"
            else:
                ai_source = "supervisor"
            
            # Check if we're transitioning between different AI sources
            if current_ai_source != ai_source:
                # Save previous agent's content
                if current_content.strip() and current_ai_source:
                    agent_responses.append({
                        'agent': current_ai_source,
                        'content': current_content.strip()
                    })
                
                # Start new agent
                current_ai_source = ai_source
                current_content = ""
                
                # Update status indicator when agent changes
                style = AGENT_STYLES[ai_source]
                with status_placeholder.container():
                    st.info(f"🔄 **{style['emoji']} {style['name']} is working...**")
            elif current_ai_source is None:
                current_ai_source = ai_source
                current_content = ""
                
                # Show initial status
                style = AGENT_STYLES[ai_source]
                with status_placeholder.container():
                    st.info(f"🔄 **{style['emoji']} {style['name']} is working...**")
            
            # Handle tool calls
            if message_chunk.tool_call_chunks:
                tool_chunk = message_chunk.tool_call_chunks[0]
                tool_name = tool_chunk.get("name", "")
                
                if tool_name and tool_name != current_tool_name:
                    current_tool_name = tool_name
                    # Add tool call indicator to content
                    current_content += f"\n\n🔧 *Using tool: {tool_name}*\n\n"
                    
                    # Update status with tool information
                    style = AGENT_STYLES[current_ai_source]
                    tool_description = ""
                    if "search" in tool_name.lower():
                        tool_description = "Searching the web for information..."
                    elif "extract" in tool_name.lower():
                        tool_description = "Extracting content from webpages..."
                    elif "generate_research" in tool_name.lower():
                        tool_description = "Generating research report..."
                    elif "handoff" in tool_name.lower():
                        tool_description = "Delegating task to agent..."
                    else:
                        tool_description = f"Using tool: {tool_name}..."
                    
                    with status_placeholder.container():
                        st.info(f"🔄 **{style['emoji']} {style['name']}**: {tool_description}")
            
            # Accumulate content
            if message_chunk.content:
                current_content += message_chunk.content
                
                # Update display in real-time
                with placeholder.container():
                    # Display all previous agent responses
                    for response in agent_responses:
                        style = AGENT_STYLES[response['agent']]
                        st.markdown(
                            f"<div style='background-color: {style['color']}20; padding: 15px; border-radius: 10px; border-left: 4px solid {style['color']}; margin-bottom: 10px;'>"
                            f"<strong>{style['emoji']} {style['name']}</strong><br><br>"
                            f"{response['content']}"
                            f"</div>",
                            unsafe_allow_html=True
                        )
                    
                    # Display current agent's content with typing indicator
                    if current_content.strip() and current_ai_source:
                        style = AGENT_STYLES[current_ai_source]
                        st.markdown(
                            f"<div style='background-color: {style['color']}20; padding: 15px; border-radius: 10px; border-left: 4px solid {style['color']}; margin-bottom: 10px;'>"
                            f"<strong>{style['emoji']} {style['name']}</strong> <span style='color: {style['color']};'>● typing...</span><br><br>"
                            f"{current_content}"
                            f"</div>",
                            unsafe_allow_html=True
                        )
    
    # Save final agent's content
    if current_content.strip() and current_ai_source:
        agent_responses.append({
            'agent': current_ai_source,
            'content': current_content.strip()
        })
    
    # Clear status when done
    with status_placeholder.container():
        st.success("✅ **Task completed!**")
    
    # Return all agent responses
    return agent_responses

def display_agent_response(agent_responses):
    """Display formatted agent responses."""
    for response in agent_responses:
        style = AGENT_STYLES[response['agent']]
        st.markdown(
            f"<div style='background-color: {style['color']}20; padding: 15px; border-radius: 10px; border-left: 4px solid {style['color']}; margin-bottom: 10px;'>"
            f"<strong>{style['emoji']} {style['name']}</strong><br><br>"
            f"{response['content']}"
            f"</div>",
            unsafe_allow_html=True
        )

def main():
    """Main Streamlit app."""
    
    # Header
    st.title("🚀 Multi-Agent AI System")
    st.markdown("*Powered by LangGraph - Supervisor with Researcher & Copywriter Agents*")
    st.markdown("---")
    
    # Sidebar
    with st.sidebar:
        st.header("⚙️ Configuration")
        st.session_state.thread_id = st.text_input(
            "Thread ID",
            value=st.session_state.thread_id,
            help="Unique identifier for the conversation thread"
        )
        
        recursion_limit = st.slider(
            "Recursion Limit",
            min_value=10,
            max_value=100,
            value=50,
            help="Maximum number of agent interactions"
        )
        
        st.markdown("---")
        st.header("📝 Example Prompts")
        
        example_prompts = [
            "Write a LinkedIn post on the top AI tools for small businesses",
            "Research the latest trends in AI automation",
            "Create a blog post about productivity tips for entrepreneurs",
            "Analyze the impact of AI on the job market"
        ]
        
        for prompt in example_prompts:
            if st.button(prompt, key=prompt, use_container_width=True, disabled=st.session_state.is_processing):
                st.session_state.selected_prompt = prompt
        
        st.markdown("---")
        if st.button("🗑️ Clear Chat History", use_container_width=True, disabled=st.session_state.is_processing):
            st.session_state.messages = []
            st.rerun()
        
        st.markdown("---")
        st.markdown("### 👥 Agents")
        st.markdown("🔬 **Researcher** - Gathers information")
        st.markdown("✍️ **Copywriter** - Creates content")
        st.markdown("🎯 **Supervisor** - Coordinates tasks")
    
    # Display chat messages
    for message in st.session_state.messages:
        if message["role"] == "user":
            with st.chat_message("user", avatar="👤"):
                st.markdown(message["content"])
        else:
            with st.chat_message("assistant", avatar="🤖"):
                display_agent_response(message["content"])
    
    # Show processing status if active
    if st.session_state.is_processing:
        st.info("⏳ **Processing your request...** Please wait until the task is complete before submitting another query.")
    
    # Check if there's a pending query to process
    if st.session_state.pending_query:
        # Display user message
        with st.chat_message("user", avatar="👤"):
            st.markdown(st.session_state.pending_query)
        
        # Status indicator placeholder
        status_placeholder = st.empty()
        
        # Display assistant response with streaming
        with st.chat_message("assistant", avatar="🤖"):
            placeholder = st.empty()
            
            # Configure graph
            config = RunnableConfig(
                configurable={
                    "thread_id": st.session_state.thread_id,
                    "recursion_limit": recursion_limit,
                }
            )
            
            # Create graph input
            graph_input = SupervisorState(
                messages=[HumanMessage(content=st.session_state.pending_query)]
            )
            
            # Stream responses
            try:
                agent_responses = asyncio.run(
                    stream_graph_responses_to_streamlit(
                        graph_input,
                        supervisor_graph,
                        placeholder,
                        status_placeholder,
                        config=config
                    )
                )
                
                # Save assistant response to chat history
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": agent_responses
                })
                
            except Exception as e:
                st.error(f"❌ Error: {type(e).__name__}: {str(e)}")
                st.exception(e)
            finally:
                # Reset processing flag and clear pending query
                st.session_state.pending_query = None
                st.session_state.is_processing = False
                st.rerun()
    
    # Handle selected prompt from sidebar
    if "selected_prompt" in st.session_state and not st.session_state.is_processing:
        user_input = st.session_state.selected_prompt
        del st.session_state.selected_prompt
        # Set pending query and trigger processing
        st.session_state.pending_query = user_input
        st.session_state.is_processing = True
        st.session_state.messages.append({"role": "user", "content": user_input})
        st.rerun()
    else:
        # Disable input during processing
        user_input = st.chat_input(
            "Ask me anything... (e.g., 'Write a LinkedIn post about AI tools')",
            disabled=st.session_state.is_processing
        )
        
        # If user submitted input, set pending query and trigger rerun
        if user_input:
            st.session_state.pending_query = user_input
            st.session_state.is_processing = True
            st.session_state.messages.append({"role": "user", "content": user_input})
            st.rerun()

if __name__ == "__main__":
    main()
