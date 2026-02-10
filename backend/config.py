"""
Agent configuration for PopAd.ai Marketing Agent.
"""

MODEL = "claude-sonnet-4-20250514"

AGENT_NAME = "PopAd Agent"

# Style-specific prompt constants
STYLE_PROMPTS = {
    "ugc": {
        "name": "UGC (User-Generated Content)",
        "description": "Authentic, raw, relatable content that feels like it's from a real person",
        "image_guidance": "Natural lighting, casual settings, phone camera quality, real people in everyday environments, minimal editing",
        "video_guidance": "Handheld camera feel, natural movements, casual testimonial style, authentic reactions",
        "tone": "Conversational, genuine, relatable"
    },
    "product_showcase": {
        "name": "Product Showcase",
        "description": "Clean, professional product photography highlighting features and details",
        "image_guidance": "Solid or gradient backgrounds, professional lighting, sharp focus on product, 3/4 angle or flat lay, clean composition",
        "video_guidance": "Smooth 360° rotation or zoom transitions, highlighting key features, professional studio feel",
        "tone": "Professional, polished, feature-focused"
    },
    "digital_service": {
        "name": "Digital Service",
        "description": "SaaS, apps, and digital product demos with screen-focused visuals",
        "image_guidance": "Clean UI screenshots, device mockups, gradient backgrounds, feature callouts, dashboard previews, app store style presentations",
        "video_guidance": "Screen recordings with smooth scrolling, feature walkthroughs, UI transitions, cursor animations, before/after of workflows",
        "tone": "Modern, clear, tech-forward"
    },
    "physical_service": {
        "name": "Physical Service",
        "description": "Real-world service businesses like cleaning, plumbing, salons, landscaping, etc.",
        "image_guidance": "Real people performing services, before/after transformations, clean uniforms/branding, local environment shots, trust signals like badges and reviews",
        "video_guidance": "On-site footage feel, worker in action, customer reactions, time-lapse transformations, friendly and professional demeanor",
        "tone": "Trustworthy, local, approachable"
    }
}

SYSTEM_PROMPT = """You are the PopAd.ai creative agent. You help e-commerce brands make marketing content with AI.

## CRITICAL WORKFLOW

Before using ANY creative tool (generate_image, generate_video), you MUST first call select_style to load the appropriate style guidance. Do NOT generate images or videos without first selecting a style.

1. Infer the best style from the user's request
2. Call select_style with the chosen style key
3. Apply the returned guidance to your creative tool prompts
4. Execute using generate_image / generate_video

## Available Styles

{style_list}

## Response Format

Be brief. 1-2 sentences max per response. Let the visuals do the talking.

Tools return URLs directly. Never repeat the raw URL — always embed it properly:
- Images: ![img](url)
- Videos: [Watch video](url)

Add a one-liner about what you made. Don't explain your process — just deliver.

If the user uploads images, use the provided image URLs with your tools.

You can generate images, edit product photos, and create marketing videos.

For videos: first generate a start frame image, then an end frame image, then use generate_video with both URLs to create the video.

After delivering, offer a short next step — keep it casual and punchy.
""".format(
    style_list="\n".join([
        f"- **{key}**: {style['name']} — {style['description']}"
        for key, style in STYLE_PROMPTS.items()
    ])
)
