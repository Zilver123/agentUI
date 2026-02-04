"""
AgentUI Backend - FastAPI + WebSocket + Anthropic SDK
"""
import json
import os
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from anthropic import Anthropic

# Load .env from project root
load_dotenv(Path(__file__).resolve().parent.parent / ".env")

from tools import TOOLS_SCHEMA, execute_tool

app = FastAPI(title="AgentUI")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

client = Anthropic()

MODEL = "claude-sonnet-4-20250514"


@app.websocket("/ws/{session_id}")
async def websocket_endpoint(websocket: WebSocket, session_id: str):
    await websocket.accept()

    # Conversation history per session
    messages = []

    try:
        while True:
            # Receive message from client
            data = await websocket.receive_json()
            message_type = data.get("type", "message")

            if message_type == "clear":
                messages = []
                await websocket.send_json({"type": "cleared"})
                continue

            # Build content array (text + optional media)
            content = []

            # Add images first
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

            # Add text
            text = data.get("text", "").strip()
            if text:
                content.append({"type": "text", "text": text})

            if not content:
                continue

            # Add user message to history
            messages.append({"role": "user", "content": content})

            # Send thinking indicator
            await websocket.send_json({"type": "thinking", "status": True})

            try:
                response_text = ""

                # Agent loop - keep going while there are tool calls
                while True:
                    # Stream response from Claude
                    with client.messages.stream(
                        model=MODEL,
                        max_tokens=4096,
                        messages=messages,
                        tools=TOOLS_SCHEMA if TOOLS_SCHEMA else None,
                    ) as stream:
                        assistant_content = []
                        current_tool_use = None

                        for event in stream:
                            if event.type == "content_block_start":
                                if event.content_block.type == "text":
                                    pass  # Will get text in deltas
                                elif event.content_block.type == "tool_use":
                                    current_tool_use = {
                                        "type": "tool_use",
                                        "id": event.content_block.id,
                                        "name": event.content_block.name,
                                        "input": {}
                                    }
                                    await websocket.send_json({
                                        "type": "tool_start",
                                        "tool_id": event.content_block.id,
                                        "name": event.content_block.name
                                    })

                            elif event.type == "content_block_delta":
                                if event.delta.type == "text_delta":
                                    response_text += event.delta.text
                                    await websocket.send_json({
                                        "type": "text_delta",
                                        "text": event.delta.text
                                    })
                                elif event.delta.type == "input_json_delta":
                                    # Accumulate tool input JSON
                                    pass

                            elif event.type == "content_block_stop":
                                if current_tool_use:
                                    assistant_content.append(current_tool_use)
                                    current_tool_use = None

                            elif event.type == "message_stop":
                                pass

                        # Get final message
                        final_message = stream.get_final_message()

                        # Build assistant content from final message
                        assistant_content = []
                        for block in final_message.content:
                            if block.type == "text":
                                assistant_content.append({
                                    "type": "text",
                                    "text": block.text
                                })
                            elif block.type == "tool_use":
                                assistant_content.append({
                                    "type": "tool_use",
                                    "id": block.id,
                                    "name": block.name,
                                    "input": block.input
                                })

                        # Add assistant message to history
                        messages.append({"role": "assistant", "content": assistant_content})

                        # Check if we need to execute tools
                        tool_uses = [b for b in final_message.content if b.type == "tool_use"]

                        if not tool_uses:
                            # No tool calls - we're done
                            break

                        # Execute tools and add results
                        tool_results = []
                        for tool_use in tool_uses:
                            result = await execute_tool(tool_use.name, tool_use.input)
                            tool_results.append({
                                "type": "tool_result",
                                "tool_use_id": tool_use.id,
                                "content": result
                            })
                            await websocket.send_json({
                                "type": "tool_end",
                                "tool_id": tool_use.id,
                                "result": result[:200] if len(result) > 200 else result
                            })

                        # Add tool results to messages
                        messages.append({"role": "user", "content": tool_results})

                        # Continue the loop to get Claude's response to tool results

                # Send completion
                await websocket.send_json({
                    "type": "done",
                    "text": response_text
                })

            except Exception as e:
                import traceback
                traceback.print_exc()
                await websocket.send_json({
                    "type": "error",
                    "message": str(e)
                })

            finally:
                await websocket.send_json({"type": "thinking", "status": False})

    except WebSocketDisconnect:
        print(f"Client {session_id} disconnected")


@app.get("/health")
async def health():
    return {"status": "ok"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
