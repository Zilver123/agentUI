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
        "image_guidance": (
            "Place the product into realistic, casual scenes as if captured by everyday content creators.\n"
            "Everything must feel natural, candid, and unpolished — never professional or staged.\n\n"
            "CAMERA KEYWORDS (always use): unremarkable amateur iPhone photo, reddit image, snapchat video, "
            "casual iPhone selfie, slightly uneven framing, slightly blurry, amateur quality phone photo.\n\n"
            "SCENE PRINCIPLES:\n"
            "- Everyday realism with authentic, relatable settings\n"
            "- Slightly imperfect framing and lighting\n"
            "- Candid poses and genuine expressions\n"
            "- Visible imperfections (blemishes, messy hair, uneven skin)\n"
            "- Environments left as-is (clutter, busy backgrounds)\n\n"
            "CHARACTER DEFAULTS: Age 21-38 unless specified. Ensure diversity in gender, ethnicity, and hair color.\n\n"
            "PROMPT STRUCTURE — build your image prompt with these fields:\n"
            "- action: What the character is doing\n"
            "- character: Age, appearance, clothing, natural features\n"
            "- setting: Location, time of day, environmental details\n"
            "- camera: iPhone/amateur quality keywords from above\n"
            "- style: Casual, candid, unposed, authentic\n\n"
            "IMPORTANT: Depict the product ACCURATELY — all text, sizing, and details must be faithful to the reference. "
            "Do NOT use double quotes in prompts."
        ),
        "video_guidance": (
            "Create casual, candid video content as if filmed by a real person on their phone.\n\n"
            "CAMERA KEYWORDS (always use): amateur quality iPhone video, handheld, natural daylight, "
            "steady but imperfect framing, slightly shaky.\n\n"
            "DIALOGUE RULES:\n"
            "- Keep dialogue under 20 words, casual and conversational\n"
            "- Speak as if talking naturally to a friend about the product\n"
            "- Use ... to indicate pauses\n"
            "- Avoid special characters like em dashes or hyphens\n"
            "- Avoid overly formal or sales-like language\n"
            "- Only mention brand name once at most\n"
            "- Focus on the product benefit (taste for drinks, design for bags, features for tech, etc.)\n\n"
            "PROMPT STRUCTURE — build your video prompt with these fields:\n"
            "- dialogue: What the character says (under 20 words)\n"
            "- action: What the character does while speaking\n"
            "- camera: Amateur iPhone video keywords from above\n"
            "- emotion: Genuine feeling (happy, excited, surprised, etc.)\n\n"
            "DEFAULT BEHAVIOR: Character shows product to camera and talks about it. "
            "Do NOT have them open, eat, or use the product unless the user asks. "
            "Do NOT use double quotes in prompts."
        ),
        "tone": "Conversational, genuine, relatable, spontaneous"
    },
    "product_showcase": {
        "name": "Product Showcase",
        "description": "Clean, professional product photography highlighting features and details",
        "image_guidance": (
            "Create polished, studio-quality product visuals that highlight form, features, and craftsmanship.\n"
            "Everything must feel premium, intentional, and magazine-worthy.\n\n"
            "CAMERA KEYWORDS (always use): professional product photography, studio lighting, sharp focus, "
            "high resolution, commercial quality, clean composition, 3/4 angle.\n\n"
            "SCENE PRINCIPLES:\n"
            "- Solid, gradient, or minimalist backgrounds (white, marble, concrete, linen)\n"
            "- Professional three-point lighting with soft shadows\n"
            "- Product is the hero — nothing competes for attention\n"
            "- Multiple angles: 3/4 view, flat lay, close-up detail shots\n"
            "- Lifestyle context only if it elevates the product (e.g., coffee cup on a designer desk)\n\n"
            "COMPOSITION DEFAULTS: Rule of thirds, generous negative space, product fills 40-60% of frame.\n\n"
            "PROMPT STRUCTURE — build your image prompt with these fields:\n"
            "- product: Exact description of the product, all text/branding visible\n"
            "- angle: Camera angle (3/4, top-down flat lay, eye-level, macro detail)\n"
            "- background: Surface and backdrop description\n"
            "- lighting: Studio lighting setup (softbox, rim light, natural window)\n"
            "- props: Minimal complementary items if any (keep focus on product)\n"
            "- style: Commercial, editorial, premium, clean\n\n"
            "IMPORTANT: Depict the product ACCURATELY — all text, logos, sizing, colors, and details must be faithful to the reference. "
            "Do NOT use double quotes in prompts."
        ),
        "video_guidance": (
            "Create smooth, polished video content that showcases the product like a premium commercial.\n\n"
            "CAMERA KEYWORDS (always use): smooth dolly movement, professional studio video, "
            "controlled lighting, steady tracking shot, commercial quality.\n\n"
            "MOTION PRINCIPLES:\n"
            "- Smooth 360° rotation or gentle orbiting around the product\n"
            "- Slow zoom into key features and details\n"
            "- Elegant transitions between angles\n"
            "- Controlled, deliberate camera movement — never handheld\n\n"
            "PROMPT STRUCTURE — build your video prompt with these fields:\n"
            "- action: Camera movement and product interaction (rotation, zoom, reveal)\n"
            "- camera: Smooth professional movement keywords from above\n"
            "- lighting: Studio lighting description\n"
            "- mood: Premium, aspirational, clean\n\n"
            "DEFAULT BEHAVIOR: Product rotates or camera orbits to reveal features. "
            "No people unless the user requests it. Focus purely on the product. "
            "Do NOT use double quotes in prompts."
        ),
        "tone": "Professional, polished, feature-focused, premium"
    },
    "digital_service": {
        "name": "Digital Service",
        "description": "SaaS, apps, and digital product demos with screen-focused visuals",
        "image_guidance": (
            "Create modern, tech-forward visuals that showcase digital products, apps, and SaaS platforms.\n"
            "Everything must feel sleek, innovative, and trustworthy.\n\n"
            "CAMERA KEYWORDS (always use): clean UI mockup, device screenshot, modern tech aesthetic, "
            "gradient background, sharp rendering, app store quality.\n\n"
            "SCENE PRINCIPLES:\n"
            "- Device mockups (iPhone, MacBook, iPad) showing the UI in context\n"
            "- Gradient or abstract geometric backgrounds (blues, purples, dark mode aesthetics)\n"
            "- Feature callouts with clean typography\n"
            "- Dashboard previews and key screens highlighted\n"
            "- Floating UI elements or glassmorphism effects for depth\n\n"
            "DEVICE DEFAULTS: Latest iPhone or MacBook unless specified. Screen content must be clearly legible.\n\n"
            "PROMPT STRUCTURE — build your image prompt with these fields:\n"
            "- device: Which device(s) to show the product on\n"
            "- screen_content: What the UI/dashboard displays\n"
            "- background: Gradient colors, abstract shapes, or contextual setting\n"
            "- callouts: Key features or metrics to highlight\n"
            "- style: Modern, minimal, tech-forward, SaaS marketing\n\n"
            "IMPORTANT: UI text and interface elements must be legible and realistic. "
            "Do NOT use double quotes in prompts."
        ),
        "video_guidance": (
            "Create sleek demo-style video content that walks through the digital product experience.\n\n"
            "CAMERA KEYWORDS (always use): smooth screen recording style, UI animation, "
            "clean transitions, modern motion graphics, tech demo.\n\n"
            "MOTION PRINCIPLES:\n"
            "- Smooth scrolling through the interface\n"
            "- Cursor or touch interactions highlighting features\n"
            "- Before/after workflow comparisons\n"
            "- Zoom into key UI elements and metrics\n"
            "- Clean fade or slide transitions between screens\n\n"
            "PROMPT STRUCTURE — build your video prompt with these fields:\n"
            "- action: UI interaction flow (scrolling, clicking, typing, navigating)\n"
            "- screen_content: What screens and features are shown\n"
            "- camera: Smooth tech demo movement keywords from above\n"
            "- transitions: How scenes connect (fade, slide, zoom)\n\n"
            "DEFAULT BEHAVIOR: Walkthrough of the product interface showing key value propositions. "
            "No narration unless the user requests it. Let the UI speak for itself. "
            "Do NOT use double quotes in prompts."
        ),
        "tone": "Modern, clear, tech-forward, innovative"
    },
    "physical_service": {
        "name": "Physical Service",
        "description": "Real-world service businesses like cleaning, plumbing, salons, landscaping, etc.",
        "image_guidance": (
            "Create trustworthy, approachable visuals that showcase real-world service businesses in action.\n"
            "Everything must feel professional yet local and relatable — like a top-rated business on Google.\n\n"
            "CAMERA KEYWORDS (always use): professional local business photo, clean and bright, "
            "real environment, natural lighting, trust-building imagery.\n\n"
            "SCENE PRINCIPLES:\n"
            "- Real people actively performing the service (cleaning, cutting hair, fixing pipes)\n"
            "- Before/after transformation shots to show results\n"
            "- Clean uniforms or branded workwear visible\n"
            "- Real job sites and local environments (homes, shops, yards)\n"
            "- Trust signals: badges, certifications, five-star review overlays, branded vehicles\n\n"
            "CHARACTER DEFAULTS: Age 25-45 unless specified. Friendly, competent demeanor. "
            "Ensure diversity in gender and ethnicity.\n\n"
            "PROMPT STRUCTURE — build your image prompt with these fields:\n"
            "- action: Service being performed or result being shown\n"
            "- worker: Appearance, uniform/branded clothing, tools in hand\n"
            "- setting: Real job site (kitchen, bathroom, garden, salon chair)\n"
            "- camera: Bright, clean local business photography keywords from above\n"
            "- trust_elements: Badges, branded items, clean equipment, satisfied customer\n"
            "- style: Professional, approachable, local business marketing\n\n"
            "IMPORTANT: Show the SERVICE and RESULTS clearly. Before/after is the most powerful format. "
            "Do NOT use double quotes in prompts."
        ),
        "video_guidance": (
            "Create warm, trust-building video content that shows the service in action and the results.\n\n"
            "CAMERA KEYWORDS (always use): clean handheld video, bright natural lighting, "
            "on-site footage, local business promo, steady and friendly.\n\n"
            "MOTION PRINCIPLES:\n"
            "- Worker arriving and getting started (builds trust)\n"
            "- Time-lapse of the transformation in progress\n"
            "- Reveal of the finished result with a satisfied customer\n"
            "- Slow pan across the completed work\n\n"
            "DIALOGUE RULES:\n"
            "- Keep dialogue under 20 words if included\n"
            "- Worker or customer speaks naturally about the service\n"
            "- Focus on reliability, quality, and results\n"
            "- Use ... to indicate pauses\n"
            "- Avoid special characters like em dashes or hyphens\n\n"
            "PROMPT STRUCTURE — build your video prompt with these fields:\n"
            "- action: Service being performed or before/after reveal\n"
            "- camera: On-site footage keywords from above\n"
            "- emotion: Pride in work, satisfaction, trust\n"
            "- dialogue: Optional short line from worker or customer\n\n"
            "DEFAULT BEHAVIOR: Show the transformation — messy to clean, broken to fixed, overgrown to manicured. "
            "The result is the hero. "
            "Do NOT use double quotes in prompts."
        ),
        "tone": "Trustworthy, local, approachable, results-driven"
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
