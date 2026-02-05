"""
Custom tools for the PopAd.ai marketing agent.
This file is gitignored - edit freely.
"""
import logging
import os
from datetime import datetime
import ast
import operator

import httpx

logger = logging.getLogger(__name__)


# Aspect ratio mapping for Fal AI
ASPECT_RATIOS = {
    "square": "1:1",
    "landscape": "16:9",
    "portrait": "9:16",
}


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
        "name": "generate_image",
        "description": "Generate or edit images using AI. Can create new images from text prompts, or edit/transform existing images. When editing, pass the image URLs provided by the system. Returns the URL of the generated image.",
        "input_schema": {
            "type": "object",
            "properties": {
                "prompt": {
                    "type": "string",
                    "description": "Text description of the image to generate, or instructions for how to edit/transform the input images"
                },
                "image_urls": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Optional. URLs of 1-3 existing images to edit or use as reference. Use the URLs provided by the system when the user uploads images."
                },
                "aspect_ratio": {
                    "type": "string",
                    "enum": ["square", "landscape", "portrait"],
                    "description": "Aspect ratio for the output image. Defaults to 'square'. Use 'landscape' for 16:9, 'portrait' for 9:16."
                }
            },
            "required": ["prompt"]
        }
    },
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


async def generate_image_impl(args: dict) -> str:
    """Generate or edit an image using Fal AI's nano-banana-pro model."""
    fal_key = os.environ.get("FAL_KEY")
    if not fal_key:
        return "Error: FAL_KEY not configured. Add it to your .env file."

    prompt = args.get("prompt", "")
    image_urls = args.get("image_urls", [])
    aspect_ratio = ASPECT_RATIOS.get(args.get("aspect_ratio", "square"), "square")

    # Choose endpoint based on whether we're editing existing images or generating new
    if image_urls:
        url = "https://fal.run/fal-ai/nano-banana-pro/edit"
        payload = {
            "prompt": prompt,
            "image_urls": image_urls[:3],  # Max 3 input images
            "num_images": 1,
            "aspect_ratio": aspect_ratio,
            "output_format": "png",
        }
    else:
        url = "https://fal.run/fal-ai/nano-banana-pro"
        payload = {
            "prompt": prompt,
            "num_images": 1,
            "aspect_ratio": aspect_ratio,
            "output_format": "png",
        }

    headers = {
        "Authorization": f"Key {fal_key}",
        "Content-Type": "application/json",
    }

    try:
        async with httpx.AsyncClient(timeout=120.0) as http_client:
            response = await http_client.post(url, json=payload, headers=headers)
            response.raise_for_status()
            data = response.json()

        images = data.get("images", [])
        if not images:
            return "Error: No images returned from the API."

        image_url = images[0].get("url", "")
        if not image_url:
            return "Error: Image URL missing from API response."

        return f"Image generated successfully.\n\nURL: {image_url}"

    except httpx.TimeoutException:
        return "Error: Image generation timed out (120s). Try a simpler prompt or try again."
    except httpx.HTTPStatusError as e:
        error_detail = ""
        try:
            error_detail = e.response.json().get("detail", e.response.text[:200])
        except Exception:
            error_detail = e.response.text[:200]
        logger.error(f"Fal API error: {e.response.status_code} - {error_detail}")
        return f"Error: Fal API returned status {e.response.status_code}. {error_detail}"
    except Exception as e:
        logger.error(f"Image generation error: {e}")
        return f"Error generating image: {str(e)}"


# Tool dispatcher
TOOL_HANDLERS = {
    "get_current_time": get_current_time_impl,
    "calculator": calculator_impl,
    "generate_image": generate_image_impl,
}


async def execute_tool(name: str, args: dict) -> str:
    """Execute a tool by name and return the result."""
    handler = TOOL_HANDLERS.get(name)
    if handler:
        return await handler(args)
    return f"Unknown tool: {name}"
