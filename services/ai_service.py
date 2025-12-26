# 🤖 OpenRouter AI Service - Gemini 2.0 Flash Integration

import aiohttp
import asyncio
import logging
import json
from typing import Optional, Dict
from config import AIConfig
from datetime import datetime

logger = logging.getLogger(__name__)


class AIService:
    """OpenRouter AI Service for Gemini 2.0 Flash"""
    
    def __init__(self):
        self.api_key = AIConfig.OPENROUTER_API_KEY
        self.api_base = AIConfig.OPENROUTER_API_BASE
        self.model = AIConfig.AI_MODEL
        self.enabled = AIConfig.AI_ENABLED
    
    async def generate_course_description(self, course_name: str, topics: str, level: str = "Beginner") -> Optional[str]:
        """
        Generate professional course description using AI
        
        Args:
            course_name: Name of the course
            topics: Comma-separated topics covered
            level: Course level (Beginner/Intermediate/Advanced)
        
        Returns:
            Generated description or None if failed
        """
        if not self.enabled:
            logger.warning("AI features disabled")
            return None
        
        prompt = f"""
You are a professional course creator. Generate an engaging, detailed course description.

Course: {course_name}
Level: {level}
Topics: {topics}

Requirements:
- Make it compelling and highlight key benefits
- Keep it under 200 words
- Include 3-4 key learning outcomes
- Use professional but friendly tone
- Add emojis for visual appeal

Generate only the description, no additional text.
        """
        
        return await self._call_api(prompt)
    
    async def generate_promotional_message(self, course_name: str, price: float, discount: int = 0) -> Optional[str]:
        """
        Generate promotional message for course
        
        Args:
            course_name: Name of the course
            price: Course price in INR
            discount: Discount percentage (0-100)
        
        Returns:
            Generated promotional message or None
        """
        if not self.enabled:
            return None
        
        final_price = price * (1 - discount / 100) if discount > 0 else price
        
        prompt = f"""
Create an engaging promotional message for a course.

Course: {course_name}
Price: ₹{price}
Discount: {discount}% OFF
Final Price: ₹{final_price:.2f}

Requirements:
- Make it catchy and persuasive
- Use relevant emojis
- Include a clear call-to-action
- Keep it concise (150-200 words)
- Highlight the value proposition
- Add urgency (limited time offer)

Generate only the promotional message.
        """
        
        return await self._call_api(prompt)
    
    async def generate_broadcast_message(self, content: str, message_type: str = "general") -> Optional[str]:
        """
        Generate broadcast message for users
        
        Args:
            content: Main content of the broadcast
            message_type: Type of message (announcement/offer/update/etc)
        
        Returns:
            Generated broadcast message or None
        """
        if not self.enabled:
            return None
        
        prompt = f"""
Write a professional broadcast message for Telegram users.

Type: {message_type}
Content: {content}

Requirements:
- Use proper formatting with emojis
- Keep it engaging and clear
- Add a call-to-action button text
- Keep under 300 words
- Make it scannable with headers
- Use Telegram markdown formatting

Generate only the message.
        """
        
        return await self._call_api(prompt)
    
    async def generate_faq(self, course_name: str, topics: str) -> Optional[str]:
        """
        Generate FAQ for a course
        
        Args:
            course_name: Course name
            topics: Course topics
        
        Returns:
            Generated FAQ or None
        """
        if not self.enabled:
            return None
        
        prompt = f"""
Generate 5-7 Frequently Asked Questions for a course.

Course: {course_name}
Topics: {topics}

Requirements:
- Format as Q&A pairs
- Make answers concise but helpful (2-3 sentences each)
- Cover common student concerns
- Include questions about:
  - Prerequisites
  - Duration
  - Support
  - Certificate
  - Refund policy

Format:
Q1: Question?
A: Answer.

Generate only the Q&A content.
        """
        
        return await self._call_api(prompt)
    
    async def generate_email_template(self, purpose: str, recipient: str = "student") -> Optional[str]:
        """
        Generate email template
        
        Args:
            purpose: Email purpose (welcome/confirmation/reminder/etc)
            recipient: Who receives the email
        
        Returns:
            Generated email template or None
        """
        if not self.enabled:
            return None
        
        prompt = f"""
Generate a professional email template.

Purpose: {purpose}
Recipient: {recipient}

Requirements:
- Include Subject: line
- Start with greeting
- Include body with key information
- End with professional signature
- Use clear, concise language
- Keep under 200 words
- Include a call-to-action

Format:
Subject: ...

Dear [Recipient],

[Body]

Best regards,
[Signature]

Generate the complete email template.
        """
        
        return await self._call_api(prompt)
    
    async def brainstorm_course_ideas(self, category: str, target_audience: str = "students") -> Optional[str]:
        """
        Brainstorm course ideas for a category
        
        Args:
            category: Course category
            target_audience: Who the course is for
        
        Returns:
            Brainstorming ideas or None
        """
        if not self.enabled:
            return None
        
        prompt = f"""
Brainstorm 5-7 course ideas in a specific category.

Category: {category}
Target Audience: {target_audience}

Requirements:
- Each idea should be unique and marketable
- Include brief description (1 sentence) for each
- Consider market demand
- Include estimated difficulty level
- Add potential price range

Format:
1. Course Name - Description (Level: Beginner/Intermediate/Advanced, Price: ₹XXX-XXX)

Generate course ideas only.
        """
        
        return await self._call_api(prompt)
    
    async def _call_api(self, prompt: str, max_retries: int = 3) -> Optional[str]:
        """
        Make API call to OpenRouter with retry logic
        
        Args:
            prompt: The prompt to send to AI
            max_retries: Maximum number of retry attempts
        
        Returns:
            Generated content or None if failed
        """
        
        if not self.api_key:
            logger.error("OpenRouter API key not configured")
            return None
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "HTTP-Referer": "https://github.com/alexavik/Botavik",
            "X-Title": "Botavik Course Bot",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": self.model,
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "temperature": AIConfig.TEMPERATURE,
            "top_p": AIConfig.TOP_P,
            "max_tokens": AIConfig.MAX_TOKENS,
            "top_k": 40,
            "frequency_penalty": 0.5,
            "presence_penalty": 0.5
        }
        
        for attempt in range(max_retries):
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.post(
                        f"{self.api_base}/chat/completions",
                        json=payload,
                        headers=headers,
                        timeout=aiohttp.ClientTimeout(total=AIConfig.API_TIMEOUT)
                    ) as response:
                        
                        if response.status == 200:
                            data = await response.json()
                            content = data['choices'][0]['message']['content'].strip()
                            logger.info(f"✅ AI generation successful (model: {self.model})")
                            return content
                        
                        elif response.status == 429:
                            logger.warning(f"⏱️ Rate limited, retrying... (attempt {attempt + 1}/{max_retries})")
                            if attempt < max_retries - 1:
                                await asyncio.sleep(2 ** attempt)  # Exponential backoff
                                continue
                        
                        elif response.status == 401:
                            logger.error("❌ Invalid API key for OpenRouter")
                            return None
                        
                        else:
                            error_text = await response.text()
                            logger.error(f"❌ API error {response.status}: {error_text}")
                            return None
            
            except asyncio.TimeoutError:
                logger.warning(f"⏱️ Request timeout, retrying... (attempt {attempt + 1}/{max_retries})")
                if attempt < max_retries - 1:
                    await asyncio.sleep(2 ** attempt)
                    continue
            
            except aiohttp.ClientError as e:
                logger.error(f"❌ Network error: {e}")
                if attempt < max_retries - 1:
                    await asyncio.sleep(2 ** attempt)
                    continue
            
            except json.JSONDecodeError as e:
                logger.error(f"❌ Invalid JSON response: {e}")
                return None
            
            except Exception as e:
                logger.error(f"❌ Unexpected error in AI generation: {e}")
                return None
        
        logger.error(f"❌ AI generation failed after {max_retries} attempts")
        return None
    
    async def test_connection(self) -> bool:
        """
        Test OpenRouter API connection
        
        Returns:
            True if connection successful, False otherwise
        """
        
        if not self.enabled or not self.api_key:
            return False
        
        test_prompt = "Say 'AI connection test successful' in exactly 5 words."
        result = await self._call_api(test_prompt)
        
        if result:
            logger.info("✅ OpenRouter AI connection verified")
            return True
        else:
            logger.error("❌ OpenRouter AI connection failed")
            return False


# Global AI service instance
ai_service = AIService()
