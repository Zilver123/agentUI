"""
Custom tools for the PopAd.ai marketing agent.
"""
import ast
import logging
import operator
import os
from datetime import datetime

import httpx

logger = logging.getLogger(__name__)

# Aspect ratio mappings for Fal AI
IMAGE_ASPECT_RATIOS = {"square": "1:1", "landscape": "16:9", "portrait": "9:16"}
VIDEO_ASPECT_RATIOS = {"auto": "auto", "landscape": "16:9", "portrait": "9:16"}

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
    {
        "name": "generate_video",
        "description": "Generate a video from start and end frame images using AI (Veo 3.1). Takes two image URLs (first frame and last frame) and creates a smooth video transition between them. Use this after generating start/end frame images with generate_image. Returns the URL of the generated video.",
        "input_schema": {
            "type": "object",
            "properties": {
                "prompt": {
                    "type": "string",
                    "description": "Text describing the video motion/transition between the start and end frames"
                },
                "first_frame_url": {
                    "type": "string",
                    "description": "URL of the video's opening frame image"
                },
                "last_frame_url": {
                    "type": "string",
                    "description": "URL of the video's closing frame image"
                },
                "aspect_ratio": {
                    "type": "string",
                    "enum": ["auto", "landscape", "portrait"],
                    "description": "Video aspect ratio. 'landscape' = 16:9, 'portrait' = 9:16. Defaults to 'auto'."
                },
                "duration": {
                    "type": "string",
                    "enum": ["4s", "6s", "8s"],
                    "description": "Video duration. Defaults to '8s'."
                }
            },
            "required": ["prompt", "first_frame_url", "last_frame_url"]
        }
    },
]


# Tool implementations

async def get_current_time_impl(_args: dict) -> str:
    """Returns the current date and time."""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


async def calculator_impl(args: dict) -> str:
    """Safely evaluate a math expression."""
    ops = {
        ast.Add: operator.add,
        ast.Sub: operator.sub,
        ast.Mult: operator.mul,
        ast.Div: operator.truediv,
        ast.Pow: operator.pow,
    }

    def eval_node(node):
        if isinstance(node, ast.Constant):
            return node.value
        if isinstance(node, ast.Num):  # Python 3.7 compat
            return node.n
        if isinstance(node, ast.BinOp):
            return ops[type(node.op)](eval_node(node.left), eval_node(node.right))
        if isinstance(node, ast.UnaryOp) and isinstance(node.op, ast.USub):
            return -eval_node(node.operand)
        raise ValueError("Unsupported expression")

    try:
        tree = ast.parse(args["expression"], mode="eval")
        return str(eval_node(tree.body))
    except Exception as e:
        return f"Error: {e}"


async def generate_image_impl(args: dict) -> str:
    """Generate or edit an image using Fal AI's nano-banana-pro model."""
    fal_key = os.environ.get("FAL_KEY")
    if not fal_key:
        return "Error: FAL_KEY not configured"

    prompt = args.get("prompt", "")
    image_urls = args.get("image_urls", [])
    aspect_ratio = IMAGE_ASPECT_RATIOS.get(args.get("aspect_ratio", "square"), "1:1")

    # Choose endpoint based on whether we're editing or generating
    if image_urls:
        url = "https://fal.run/fal-ai/nano-banana-pro/edit"
        payload = {
            "prompt": prompt,
            "image_urls": image_urls[:3],
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
        async with httpx.AsyncClient(timeout=120.0) as client:
            response = await client.post(url, json=payload, headers=headers)
            response.raise_for_status()
            data = response.json()

        images = data.get("images", [])
        if not images or not images[0].get("url"):
            return "Error: No image URL in response"

        return images[0]["url"]

    except httpx.TimeoutException:
        return "Error: Image generation timed out (120s)"
    except httpx.HTTPStatusError as e:
        detail = _extract_error_detail(e)
        logger.error(f"Fal API error: {e.response.status_code} - {detail}")
        return f"Error: Fal API {e.response.status_code}. {detail}"
    except Exception as e:
        logger.error(f"Image generation error: {e}")
        return f"Error: {e}"


async def generate_video_impl(args: dict) -> str:
    """Generate a video from start and end frame images using Fal AI's Veo 3.1."""
    fal_key = os.environ.get("FAL_KEY")
    if not fal_key:
        return "Error: FAL_KEY not configured"

    first_frame = args.get("first_frame_url", "")
    last_frame = args.get("last_frame_url", "")

    if not first_frame or not last_frame:
        return "Error: Both first_frame_url and last_frame_url are required"

    payload = {
        "prompt": args.get("prompt", ""),
        "first_frame_url": first_frame,
        "last_frame_url": last_frame,
        "aspect_ratio": VIDEO_ASPECT_RATIOS.get(args.get("aspect_ratio", "auto"), "auto"),
        "duration": args.get("duration", "8s"),
        "generate_audio": True,
    }

    headers = {
        "Authorization": f"Key {fal_key}",
        "Content-Type": "application/json",
    }

    try:
        async with httpx.AsyncClient(timeout=300.0) as client:
            response = await client.post(
                "https://fal.run/fal-ai/veo3.1/fast/first-last-frame-to-video",
                json=payload,
                headers=headers
            )
            response.raise_for_status()
            data = response.json()

        video_url = data.get("video", {}).get("url")
        if not video_url:
            return "Error: No video URL in response"

        return video_url

    except httpx.TimeoutException:
        return "Error: Video generation timed out (5 min)"
    except httpx.HTTPStatusError as e:
        detail = _extract_error_detail(e)
        logger.error(f"Fal API error: {e.response.status_code} - {detail}")
        return f"Error: Fal API {e.response.status_code}. {detail}"
    except Exception as e:
        logger.error(f"Video generation error: {e}")
        return f"Error: {e}"


def _extract_error_detail(error: httpx.HTTPStatusError) -> str:
    """Extract error detail from Fal API response."""
    try:
        return error.response.json().get("detail", error.response.text[:200])
    except Exception:
        return error.response.text[:200]


# Tool dispatcher
TOOL_HANDLERS = {
    "get_current_time": get_current_time_impl,
    "calculator": calculator_impl,
    "generate_image": generate_image_impl,
    "generate_video": generate_video_impl,
}


async def execute_tool(name: str, args: dict) -> str:
    """Execute a tool by name and return the result."""
    handler = TOOL_HANDLERS.get(name)
    if handler:
        return await handler(args)
    return f"Unknown tool: {name}"
