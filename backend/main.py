"""
AgentUI Backend - FastAPI + WebSocket + Anthropic SDK
"""
from __future__ import annotations

import asyncio
import base64
import logging
import os
import traceback
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from anthropic import Anthropic

from tools import TOOLS_SCHEMA, execute_tool
from config import SYSTEM_PROMPT, MODEL

# Load .env from project root
load_dotenv(Path(__file__).resolve().parent.parent / ".env")

logger = logging.getLogger(__name__)

app = FastAPI(title="AgentUI")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

client = Anthropic()

MAX_TOOL_CALLS = 5


async def upload_base64_to_fal(base64_data: str, media_type: str) -> str | None:
    """Upload a base64 image to Fal CDN and return the public URL."""
    fal_key = os.environ.get("FAL_KEY")
    if not fal_key:
        return None

    import fal_client

    image_bytes = base64.b64decode(base64_data)

    try:
        url = await asyncio.to_thread(
            fal_client.upload, image_bytes, content_type=media_type
        )
        return url
    except Exception as e:
        logger.warning(f"Fal CDN upload failed: {e}")
        return None


@app.websocket("/ws/{session_id}")
async def websocket_endpoint(websocket: WebSocket, session_id: str):
    await websocket.accept()
    messages = []  # Conversation history

    try:
        while True:
            data = await websocket.receive_json()

            # Handle clear command
            if data.get("type") == "clear":
                messages = []
                await websocket.send_json({"type": "cleared"})
                continue

            # Build message content
            content = []
            uploaded_image_urls = []

            # Process media attachments
            for media in data.get("media", []):
                if media["type"] == "image":
                    content.append({
                        "type": "image",
                        "source": {
                            "type": "base64",
                            "media_type": media["media_type"],
                            "data": media["data"]
                        }
                    })
                    # Upload to Fal CDN for tool access
                    fal_url = await upload_base64_to_fal(media["data"], media["media_type"])
                    if fal_url:
                        uploaded_image_urls.append(fal_url)

            # Add text content
            text = data.get("text", "").strip()
            if text:
                content.append({"type": "text", "text": text})

            # Append image URLs for tools
            if uploaded_image_urls:
                content.append({
                    "type": "text",
                    "text": f"[System: User uploaded images. URLs for tools: {', '.join(uploaded_image_urls)}]"
                })

            if not content:
                continue

            messages.append({"role": "user", "content": content})
            await websocket.send_json({"type": "thinking", "status": True})

            try:
                await run_agent_loop(websocket, messages)
            except Exception as e:
                traceback.print_exc()
                await websocket.send_json({"type": "error", "message": str(e)})
            finally:
                await websocket.send_json({"type": "thinking", "status": False})

    except WebSocketDisconnect:
        logger.info(f"Client {session_id} disconnected")


async def run_agent_loop(websocket: WebSocket, messages: list):
    """Run the agent loop: stream response, execute tools, repeat until done."""
    tool_call_count = 0

    while True:
        # Stream Claude's response
        with client.messages.stream(
            model=MODEL,
            max_tokens=4096,
            system=SYSTEM_PROMPT,
            messages=messages,
            tools=TOOLS_SCHEMA or None,
        ) as stream:
            # Stream text deltas and tool starts to frontend
            for event in stream:
                if event.type == "content_block_start":
                    if event.content_block.type == "tool_use":
                        await websocket.send_json({
                            "type": "tool_start",
                            "tool_id": event.content_block.id,
                            "name": event.content_block.name
                        })
                elif event.type == "content_block_delta":
                    if event.delta.type == "text_delta":
                        await websocket.send_json({
                            "type": "text_delta",
                            "text": event.delta.text
                        })

            # Get complete message
            final_message = stream.get_final_message()

        # Build assistant content for history
        assistant_content = []
        for block in final_message.content:
            if block.type == "text":
                assistant_content.append({"type": "text", "text": block.text})
            elif block.type == "tool_use":
                assistant_content.append({
                    "type": "tool_use",
                    "id": block.id,
                    "name": block.name,
                    "input": block.input
                })

        messages.append({"role": "assistant", "content": assistant_content})

        # Check for tool calls
        tool_uses = [b for b in final_message.content if b.type == "tool_use"]

        if not tool_uses:
            break  # No tools, we're done

        # Enforce tool call limit
        tool_call_count += len(tool_uses)
        if tool_call_count > MAX_TOOL_CALLS:
            logger.warning(f"Tool call limit ({MAX_TOOL_CALLS}) reached")
            break

        # Execute tools
        tool_results = []
        for tool_use in tool_uses:
            result = await execute_tool(tool_use.name, tool_use.input)
            tool_results.append({
                "type": "tool_result",
                "tool_use_id": tool_use.id,
                "content": result
            })
            await websocket.send_json({"type": "tool_end", "tool_id": tool_use.id})

        messages.append({"role": "user", "content": tool_results})

        # Signal new turn for frontend
        await websocket.send_json({"type": "new_turn"})

    await websocket.send_json({"type": "done"})


@app.get("/health")
async def health():
    return {"status": "ok"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
