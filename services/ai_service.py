# 🤖 OpenRouter AI Service - Gemini 2.0 Flash Integration with Vision

import aiohttp
import asyncio
import logging
import json
from typing import Optional, Dict, List, AsyncIterator
from config import AIConfig
from datetime import datetime

logger = logging.getLogger(__name__)


class AIService:
    """OpenRouter AI Service for Gemini 2.0 Flash with Vision Support"""
    
    def __init__(self):
        self.api_key = AIConfig.OPENROUTER_API_KEY
        self.api_base = AIConfig.OPENROUTER_API_BASE
        self.model = AIConfig.AI_MODEL  # google/gemini-2.0-flash-exp:free
        self.enabled = AIConfig.AI_ENABLED
    
    async def analyze_image(self, image_url: str, question: str = "What is in this image?") -> Optional[str]:
        """
        Analyze image using Gemini 2.0 Flash Vision
        
        Args:
            image_url: URL of the image to analyze
            question: Question to ask about the image
        
        Returns:
            AI analysis of the image or None if failed
        """
        if not self.enabled:
            logger.warning("AI features disabled")
            return None
        
        logger.info(f"🖼️ Analyzing image: {image_url[:50]}...")
        
        return await self._call_vision_api(
            text=question,
            image_url=image_url
        )
    
    async def analyze_course_thumbnail(self, image_url: str, course_name: str) -> Optional[str]:
        """
        Analyze course thumbnail and provide feedback
        
        Args:
            image_url: URL of the course thumbnail
            course_name: Name of the course
        
        Returns:
            Analysis and suggestions for improvement
        """
        if not self.enabled:
            return None
        
        prompt = f"""
Analyze this course thumbnail for "{course_name}".

Provide:
1. What elements are visible
2. Design quality rating (1-10)
3. Does it look professional?
4. Suggestions for improvement
5. Does it match the course topic?

Keep response under 200 words.
        """
        
        return await self._call_vision_api(
            text=prompt,
            image_url=image_url
        )
    
    async def analyze_payment_proof(self, image_url: str) -> Optional[Dict[str, any]]:
        """
        Analyze payment proof screenshot
        
        Args:
            image_url: URL of the payment screenshot
        
        Returns:
            Dictionary with verification details or None
        """
        if not self.enabled:
            return None
        
        prompt = """
Analyze this payment screenshot.

Extract and verify:
1. Payment method (UPI/FamPay/etc)
2. Transaction ID (if visible)
3. Amount paid (in ₹)
4. Payment status (Success/Pending/Failed)
5. Timestamp (if visible)
6. Is this a valid payment proof?

Respond in JSON format:
{
  "valid": true/false,
  "method": "UPI/FamPay/etc",
  "amount": "₹XXX",
  "transaction_id": "xxx or null",
  "status": "Success/Pending/Failed",
  "timestamp": "date or null",
  "confidence": "High/Medium/Low",
  "notes": "any additional observations"
}
        """
        
        result = await self._call_vision_api(
            text=prompt,
            image_url=image_url
        )
        
        if result:
            try:
                # Try to parse JSON response
                return json.loads(result)
            except json.JSONDecodeError:
                logger.warning("AI response not in JSON format, returning raw text")
                return {"raw_response": result, "valid": False}
        
        return None
    
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
    
    async def _call_vision_api(self, text: str, image_url: str, stream: bool = False) -> Optional[str]:
        """
        Make vision API call to OpenRouter (text + image)
        
        Args:
            text: Text prompt/question
            image_url: URL of the image
            stream: Whether to stream the response
        
        Returns:
            AI response or None if failed
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
        
        # Multimodal payload (text + image)
        payload = {
            "model": self.model,  # google/gemini-2.0-flash-exp:free supports vision
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": text
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": image_url
                            }
                        }
                    ]
                }
            ],
            "stream": stream
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.api_base}/chat/completions",
                    json=payload,
                    headers=headers,
                    timeout=aiohttp.ClientTimeout(total=60)  # Vision takes longer
                ) as response:
                    
                    if response.status == 200:
                        if stream:
                            # Handle streaming response
                            full_content = ""
                            async for line in response.content:
                                if line:
                                    try:
                                        line_text = line.decode('utf-8').strip()
                                        if line_text.startswith('data: '):
                                            json_str = line_text[6:]
                                            if json_str != '[DONE]':
                                                chunk = json.loads(json_str)
                                                content = chunk.get('choices', [{}])[0].get('delta', {}).get('content', '')
                                                if content:
                                                    full_content += content
                                    except Exception as e:
                                        continue
                            logger.info(f"✅ Vision AI analysis successful (streaming)")
                            return full_content.strip()
                        else:
                            # Handle non-streaming response
                            data = await response.json()
                            content = data['choices'][0]['message']['content'].strip()
                            logger.info(f"✅ Vision AI analysis successful")
                            return content
                    
                    elif response.status == 429:
                        logger.warning("⏱️ Rate limited on vision API")
                        return None
                    
                    elif response.status == 401:
                        logger.error("❌ Invalid API key for OpenRouter")
                        return None
                    
                    else:
                        error_text = await response.text()
                        logger.error(f"❌ Vision API error {response.status}: {error_text}")
                        return None
        
        except asyncio.TimeoutError:
            logger.error("⏱️ Vision API request timeout")
            return None
        
        except aiohttp.ClientError as e:
            logger.error(f"❌ Network error in vision API: {e}")
            return None
        
        except Exception as e:
            logger.error(f"❌ Unexpected error in vision API: {e}")
            return None
    
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
    
    async def test_vision(self, test_image_url: str = "https://upload.wikimedia.org/wikipedia/commons/thumb/d/dd/Gfp-wisconsin-madison-the-nature-boardwalk.jpg/2560px-Gfp-wisconsin-madison-the-nature-boardwalk.jpg") -> bool:
        """
        Test vision API with a sample image
        
        Args:
            test_image_url: URL of test image
        
        Returns:
            True if vision works, False otherwise
        """
        if not self.enabled or not self.api_key:
            return False
        
        result = await self.analyze_image(test_image_url, "Describe this image in one sentence.")
        
        if result:
            logger.info(f"✅ Vision API test successful: {result[:100]}...")
            return True
        else:
            logger.error("❌ Vision API test failed")
            return False


# Global AI service instance
ai_service = AIService()
