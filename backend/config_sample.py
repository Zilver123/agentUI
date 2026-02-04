"""
Agent configuration.
Copy this file to config.py and customize for your agent.

    cp config_sample.py config.py

config.py is gitignored so your custom config stays private.
"""

# Model to use
MODEL = "claude-sonnet-4-20250514"

# Agent display name
AGENT_NAME = "Agent"

# System prompt - customize this for your agent's persona
SYSTEM_PROMPT = """You are a helpful assistant with access to tools.

When you generate images using the generate_image tool, always display the resulting
image to the user by including it in your response using markdown image syntax:
![description](url)

When a user uploads images, you will be told the image URLs that are available
for use with image generation and editing tools. Pass these URLs in the image_urls
parameter when calling tools that need them.
"""
