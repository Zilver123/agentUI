"""
Custom tools for the agent.
Add your own tools here.
"""
from datetime import datetime
import ast
import operator


# Tool schemas for Claude API
TOOLS_SCHEMA = [
    {
        "name": "get_current_time",
        "description": "Get the current date and time",
        "input_schema": {
            "type": "object",
            "properties": {},
            "required": []
        }
    },
    {
        "name": "calculator",
        "description": "Perform basic math calculations. Supports +, -, *, /, and ** (power)",
        "input_schema": {
            "type": "object",
            "properties": {
                "expression": {
                    "type": "string",
                    "description": "The math expression to evaluate, e.g. '2 + 2' or '10 * 5'"
                }
            },
            "required": ["expression"]
        }
    },
    {
        "name": "web_search",
        "description": "Search the web for information",
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "The search query"
                }
            },
            "required": ["query"]
        }
    }
]


# Tool implementations
async def get_current_time_impl(args: dict) -> str:
    """Returns the current date and time."""
    now = datetime.now()
    return now.strftime("%Y-%m-%d %H:%M:%S")


async def calculator_impl(args: dict) -> str:
    """Safely evaluate a math expression."""
    ops = {
        ast.Add: operator.add,
        ast.Sub: operator.sub,
        ast.Mult: operator.mul,
        ast.Div: operator.truediv,
        ast.Pow: operator.pow,
    }

    def eval_expr(node):
        if isinstance(node, ast.Num):
            return node.n
        elif isinstance(node, ast.Constant):
            return node.value
        elif isinstance(node, ast.BinOp):
            return ops[type(node.op)](eval_expr(node.left), eval_expr(node.right))
        elif isinstance(node, ast.UnaryOp) and isinstance(node.op, ast.USub):
            return -eval_expr(node.operand)
        else:
            raise ValueError("Unsupported expression")

    try:
        tree = ast.parse(args["expression"], mode="eval")
        result = eval_expr(tree.body)
        return str(result)
    except Exception as e:
        return f"Error: {str(e)}"


async def web_search_impl(args: dict) -> str:
    """Simulated web search - replace with real implementation."""
    query = args["query"]
    # TODO: Integrate with a real search API (e.g., Tavily, SerpAPI)
    return f"[Simulated search results for: {query}]\n\nTo enable real web search, integrate with Tavily or another search API."


# Tool dispatcher
TOOL_HANDLERS = {
    "get_current_time": get_current_time_impl,
    "calculator": calculator_impl,
    "web_search": web_search_impl,
}


async def execute_tool(name: str, args: dict) -> str:
    """Execute a tool by name and return the result."""
    handler = TOOL_HANDLERS.get(name)
    if handler:
        return await handler(args)
    return f"Unknown tool: {name}"
