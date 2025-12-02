# Multi-Agent AI System with Streamlit UI

A powerful multi-agent system built with LangGraph featuring a Supervisor that coordinates Researcher and Copywriter agents.

## Features

- 🚀 **Multi-Agent Architecture**: Supervisor coordinates specialized agents
- 🔬 **Researcher Agent**: Gathers information and conducts research
- ✍️ **Copywriter Agent**: Creates high-quality content
- 💬 **Real-time Streaming**: Watch agents work in real-time
- 🎨 **Beautiful UI**: Clean, modern Streamlit interface
- 📝 **Chat History**: Maintains conversation context
- ⚙️ **Configurable**: Adjust thread ID and recursion limits

## Agents

### 🎯 Supervisor
- Coordinates tasks between agents
- Decides which agent to use for each task
- Manages the workflow

### 🔬 Researcher
- Gathers information from various sources
- Conducts thorough research
- Provides data-driven insights

### ✍️ Copywriter
- Creates engaging content
- Writes professional copy
- Formats content appropriately

## Installation

1. **Clone the repository** (if not already done)
   ```bash
   cd MultiAgent
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**
   
   Create a `.env` file in the `MultiAgent` directory with your API keys:
   ```env
   OPENAI_API_KEY=your_openai_api_key_here
   TAVILY_API_KEY=your_tavily_api_key_here  # Optional, for research capabilities
   ```

## Running the Application

### Streamlit UI (Recommended)

Run the Streamlit app:
```bash
streamlit run streamlit_app.py
```

The app will open in your default browser at `http://localhost:8501`

### Console Version (Original)

Run the console version:
```bash
python main.py
```

## Usage

### Streamlit UI

1. **Start the app** using the command above
2. **Enter your query** in the chat input at the bottom
3. **Watch the agents work** in real-time
4. **View responses** with color-coded agent indicators
5. **Use example prompts** from the sidebar for quick testing

### Example Prompts

- "Write a LinkedIn post on the top AI tools for small businesses"
- "Research the latest trends in AI automation"
- "Create a blog post about productivity tips for entrepreneurs"
- "Analyze the impact of AI on the job market"

### Configuration Options

**Thread ID**: Unique identifier for conversation threads. Change this to start a new conversation.

**Recursion Limit**: Maximum number of agent interactions allowed (default: 50)

## Features Comparison

| Feature | Console UI | Streamlit UI |
|---------|-----------|--------------|
| Chat Interface | ✗ | ✓ |
| Real-time Streaming | ✓ | ✓ |
| Agent Visualization | Basic | Enhanced |
| Chat History | ✗ | ✓ |
| Configuration | Fixed | Interactive |
| Example Prompts | Comments | Sidebar Buttons |
| User Experience | Terminal | Web Browser |

## Project Structure

```
MultiAgent/
├── streamlit_app.py       # Streamlit UI (NEW)
├── main.py                # Console version (Original)
├── supervisor.py          # Supervisor agent logic
├── researcher.py          # Researcher agent logic
├── copywriter.py          # Copywriter agent logic
├── requirements.txt       # Python dependencies
├── .env                   # Environment variables (create this)
├── README.md             # This file
└── prompts/              # Agent prompts
    ├── supervisor.md
    ├── researcher.md
    └── copywriter.md
```

## Troubleshooting

### Common Issues

1. **Module not found errors**
   ```bash
   pip install -r requirements.txt
   ```

2. **API key errors**
   - Ensure your `.env` file is in the `MultiAgent` directory
   - Check that your API keys are valid
   - Verify the `.env` file format

3. **Streamlit not opening**
   - Check if port 8501 is available
   - Try specifying a different port:
     ```bash
     streamlit run streamlit_app.py --server.port 8502
     ```

4. **Async errors**
   - The app handles async operations automatically
   - If issues persist, restart the Streamlit server

## Development

### Adding New Agents

1. Create a new agent file (e.g., `editor.py`)
2. Define the agent logic and tools
3. Update the supervisor to include the new agent
4. Add styling in `AGENT_STYLES` dictionary in `streamlit_app.py`

### Customizing the UI

- Modify `AGENT_STYLES` for different colors/emojis
- Adjust page configuration in `st.set_page_config()`
- Customize sidebar content in the `with st.sidebar:` block

## Dependencies

Key dependencies:
- `streamlit` - Web UI framework
- `langchain` - LLM framework
- `langgraph` - Agent orchestration
- `langchain-openai` - OpenAI integration
- `python-dotenv` - Environment management

See `requirements.txt` for complete list.

## License

[Add your license information here]

## Support

For issues or questions:
- Check the troubleshooting section above
- Review the code comments
- Check LangGraph documentation: https://langchain-ai.github.io/langgraph/

## Acknowledgments

Built with:
- [LangGraph](https://github.com/langchain-ai/langgraph)
- [Streamlit](https://streamlit.io/)
- [LangChain](https://github.com/langchain-ai/langchain)
