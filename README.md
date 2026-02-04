# Agent UI

A simple Claude clone with custom tool support using the Claude Agent SDK.

## Quick Start

### 1. Set your API key

```bash
export ANTHROPIC_API_KEY=your-key-here
```

### 2. Start the backend

```bash
cd backend
pip install -r requirements.txt
python main.py
```

### 3. Start the frontend

```bash
cd frontend
npm install
npm run dev
```

Open http://localhost:3000

## Adding Custom Tools

Edit `backend/tools.py`:

```python
from claude_agent_sdk import tool

@tool("my_tool", "Description of what it does", {
    "param1": str,
    "param2": int
})
async def my_tool(args):
    result = do_something(args["param1"], args["param2"])
    return {
        "content": [{"type": "text", "text": str(result)}]
    }

# Add to the list
ALL_TOOLS = [
    # ... existing tools
    my_tool,
]
```

Restart the backend after adding tools.

## Built-in Tools

- `get_current_time` - Returns current date/time
- `calculator` - Basic math operations
- `web_search` - Simulated search (add real API integration)

## Features

- Mobile-first responsive design
- Image and video upload support
- Real-time streaming responses
- Tool call visualization
- Markdown rendering
