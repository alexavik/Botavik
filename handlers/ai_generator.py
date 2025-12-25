# 🤖 AI Caption Generator Handler

import logging
import aiohttp
from config import AIConfig

logger = logging.getLogger(__name__)


async def generate_caption(title: str, description: str, price: float) -> str:
    """Generate marketing caption using OpenRouter Gemini 2.0 Flash"""
    
    try:
        prompt = f"""
You are a marketing expert. Create a compelling, short marketing caption (max 200 words) for this course:

Title: {title}
Description: {description}
Price: ₹{price}

Make it engaging, highlight key benefits, use relevant emojis, and make people want to buy it.
Keep it concise and impactful.
"""
        
        async with aiohttp.ClientSession() as session:
            async with session.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {AIConfig.OPENROUTER_API_KEY}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": AIConfig.MODEL_NAME,
                    "messages": [
                        {"role": "user", "content": prompt}
                    ],
                    "temperature": 0.7,
                    "max_tokens": 300,
                },
                timeout=aiohttp.ClientTimeout(total=AIConfig.TIMEOUT)
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    caption = data['choices'][0]['message']['content'].strip()
                    logger.info("✅ Caption generated successfully")
                    return caption
                else:
                    logger.error(f"❌ API Error: {response.status}")
                    return f"🎓 {title}\n\n{description}\n\nPrice: ₹{price}"
                    
    except Exception as e:
        logger.error(f"❌ Error generating caption: {e}")
        # Fallback caption
        return f"🎓 {title}\n\n{description}\n\nPrice: ₹{price}"


async def get_ai_response(prompt: str) -> str:
    """Get response from AI (generic)"""
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {AIConfig.OPENROUTER_API_KEY}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": AIConfig.MODEL_NAME,
                    "messages": [
                        {"role": "user", "content": prompt}
                    ],
                    "temperature": 0.7,
                    "max_tokens": AIConfig.MAX_TOKENS,
                },
                timeout=aiohttp.ClientTimeout(total=AIConfig.TIMEOUT)
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    return data['choices'][0]['message']['content'].strip()
                else:
                    return "❌ Error getting AI response"
                    
    except Exception as e:
        logger.error(f"❌ Error: {e}")
        return "❌ Error getting AI response"
