# AgentUI

A simple Claude clone with custom tool support using the Anthropic SDK.

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
# 1. Add schema to TOOLS_SCHEMA list
TOOLS_SCHEMA.append({
    "name": "my_tool",
    "description": "Description of what it does",
    "input_schema": {
        "type": "object",
        "properties": {
            "param1": {"type": "string", "description": "First param"},
            "param2": {"type": "integer", "description": "Second param"}
        },
        "required": ["param1"]
    }
})

# 2. Add implementation
async def my_tool_impl(args: dict) -> str:
    result = do_something(args["param1"], args["param2"])
    return str(result)

# 3. Register in TOOL_HANDLERS
TOOL_HANDLERS["my_tool"] = my_tool_impl
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
