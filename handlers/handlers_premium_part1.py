# PREMIUM HANDLERS - Part 1: course_buyer.py

# handlers/course_buyer.py
"""
Course Buyer Handler - Professional purchase & wishlist management
Features: Course details, payment flow, access verification, wishlist
"""

import logging
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes

logger = logging.getLogger(__name__)

class CourseBuyer:
    """Handle course purchases, wishlists, and access"""
    
    @staticmethod
    async def show_course_details(update: Update, context: ContextTypes.DEFAULT_TYPE, course_id: int = None):
        """Display full course details to buyer"""
        
        # If called from deep link
        if course_id is None and update.callback_query:
            query = update.callback_query
            await query.answer()
            course_id = int(query.data.split("_")[1])
        
        # TODO: Fetch from database
        course_details = f"""
📚 COURSE DETAILS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📖 Python for Ethical Hacking

✨ Learn Advanced Python:
✅ Network programming
✅ Socket programming
✅ Packet manipulation
✅ Exploit development
✅ Penetration testing

👨‍🏫 What You'll Get:
📚 50+ hours of content
📺 100+ video tutorials
💻 30+ hands-on projects
🎓 Lifetime access
📜 Completion certificate

⭐ Reviews: 4.9/5 (150+ reviews)

💰 Price: ₹499
🔒 100% Money-back guarantee

Ready to start learning?
        """
        
        keyboard = [
            [InlineKeyboardButton("🛒 Buy Now", callback_data=f"payment_{course_id}")],
            [InlineKeyboardButton("❤️ Add to Wishlist", callback_data=f"wish_{course_id}")],
            [InlineKeyboardButton("« Back", callback_data="back_channel")]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        if update.callback_query:
            await update.callback_query.edit_message_text(course_details, reply_markup=reply_markup)
        else:
            await update.message.reply_text(course_details, reply_markup=reply_markup)
        
        logger.info(f"👤 User {update.effective_user.id} viewing course {course_id}")
    
    @staticmethod
    async def handle_payment(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show payment instructions"""
        query = update.callback_query
        await query.answer()
        
        course_id = int(query.data.split("_")[1])
        user_id = update.effective_user.id
        
        payment_text = f"""
💳 PAYMENT INSTRUCTIONS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🎓 Course: Python for Ethical Hacking
💰 Price: ₹499

📱 SEND PAYMENT VIA UPI:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Copy this UPI ID:
👇 yourname@fampay

⬇️ Or use this link:
upi://pay?pa=yourname@fampay&pn=CourseBot&am=499

⏱️ PAYMENT STEPS:
1. Copy UPI ID: yourname@fampay
2. Open your UPI app
3. Send ₹499 to the UPI ID
4. Note your transaction ID
5. Come back here and verify payment

🔒 100% Secure & Safe
✅ Instant access after payment

⚠️ Important:
After payment, come back to THIS message
and click "✅ Payment Sent!"
        """
        
        keyboard = [
            [InlineKeyboardButton("✅ Payment Sent!", callback_data=f"verify_{course_id}_{user_id}")],
            [InlineKeyboardButton("❌ Cancel", callback_data="back_channel")]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(payment_text, reply_markup=reply_markup)
        
        logger.info(f"💳 User {user_id} viewing payment for course {course_id}")
    
    @staticmethod
    async def verify_payment(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Verify payment and grant access"""
        query = update.callback_query
        await query.answer()
        
        user_id = update.effective_user.id
        course_id = int(query.data.split("_")[1])
        
        verification_text = f"""
⏳ VERIFYING PAYMENT...
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Please wait while we verify your payment...

📊 Details:
├─ User ID: {user_id}
├─ Course ID: {course_id}
├─ Amount: ₹499
└─ Status: Verifying...

This usually takes 1-2 minutes.
        """
        
        await query.edit_message_text(verification_text)
        
        # TODO: Check payment manually
        # For now, auto-verify for demo
        success_text = f"""
✅ PAYMENT VERIFIED!
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🎉 Welcome to the course!

📚 Python for Ethical Hacking
⏱️ Duration: 50+ hours
📺 100+ video tutorials

🔗 ACCESS YOUR COURSE:
/my_courses

📧 Course Details:
├─ Full access to all content
├─ Download materials
├─ Lifetime access
├─ Certificate available
└─ Support: 24/7

🚀 START LEARNING NOW!
/my_courses

Questions? /support
        """
        
        keyboard = [
            [InlineKeyboardButton("🚀 Go to Course", callback_data="my_courses")],
            [InlineKeyboardButton("💬 Support", callback_data="support")]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(success_text, reply_markup=reply_markup)
        
        logger.info(f"✅ Payment verified for user {user_id}, course {course_id}")
    
    @staticmethod
    async def handle_wishlist(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Add/remove from wishlist"""
        query = update.callback_query
        await query.answer()
        
        user_id = update.effective_user.id
        course_id = int(query.data.split("_")[1])
        
        # TODO: Toggle wishlist in database
        
        wishlist_text = f"""
❤️ WISHLIST
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✅ Added to wishlist!

📚 Saved Courses: 1

You'll be notified when:
├─ Price changes
├─ New content added
├─ Special discounts

View all: /wishlist
        """
        
        keyboard = [
            [InlineKeyboardButton("View Wishlist", callback_data="view_wishlist")],
            [InlineKeyboardButton("« Back", callback_data="back_channel")]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(wishlist_text, reply_markup=reply_markup)
        
        logger.info(f"❤️ User {user_id} wishlisted course {course_id}")

# ═════════════════════════════════════════════════════════════════════

# PREMIUM HANDLERS - Part 2: ai_generator.py

# handlers/ai_generator.py
"""
AI Content Generator - OpenRouter Gemini 2.0 Flash Integration
Features: Smart captions, descriptions, marketing copy, emoji enhancement
"""

import logging
import aiohttp
from config import AIConfig

logger = logging.getLogger(__name__)

class AIContentGenerator:
    """Generate course content using OpenRouter Gemini API"""
    
    @staticmethod
    async def generate_course_caption(title: str, description: str, category: str, price: float) -> str:
        """Generate compelling marketing caption using AI"""
        
        prompt = f"""
Generate a compelling, emoji-rich marketing caption for this course in under 150 words.

Course Details:
- Title: {title}
- Description: {description}
- Category: {category}
- Price: ₹{price}

Requirements:
- Use relevant emojis throughout
- Highlight key benefits
- Create urgency
- Be persuasive but honest
- Include call-to-action
- Make it Telegram-friendly

Format:
[Emoji] Main Headline
[Emojis] Key Points (3-5 points)
💰 Price: ₹{price}
[Call to action]
        """
        
        try:
            async with aiohttp.ClientSession() as session:
                headers = {
                    "Authorization": f"Bearer {AIConfig.OPENROUTER_API_KEY}",
                    "HTTP-Referer": "https://github.com/avik",
                    "X-Title": "Telegram Course Bot"
                }
                
                payload = {
                    "model": AIConfig.OPENROUTER_MODEL,
                    "messages": [
                        {"role": "user", "content": prompt}
                    ],
                    "temperature": AIConfig.TEMPERATURE,
                    "max_tokens": AIConfig.MAX_TOKENS
                }
                
                async with session.post(
                    f"{AIConfig.OPENROUTER_BASE_URL}/chat/completions",
                    headers=headers,
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=AIConfig.TIMEOUT)
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        caption = data['choices'][0]['message']['content']
                        logger.info(f"✨ AI caption generated for: {title}")
                        return caption
                    else:
                        logger.error(f"❌ AI API error: {response.status}")
                        return f"📚 {title}\n\n{description}\n\n💰 ₹{price}"
        
        except Exception as e:
            logger.error(f"❌ AI generation failed: {e}")
            # Fallback to basic caption
            return f"📚 {title}\n\n{description}\n\n💰 ₹{price}"
    
    @staticmethod
    async def generate_course_description(title: str, key_points: list) -> str:
        """Generate full course description with key points"""
        
        points_text = "\n".join([f"• {point}" for point in key_points])
        
        prompt = f"""
Write a professional course description based on these details:

Title: {title}
Key Points:
{points_text}

Create a description that:
- Explains what students will learn
- Highlights benefits
- Shows value
- Builds credibility
- Uses emojis strategically
- Is under 500 words

Format:
📖 Introduction
✅ What You'll Learn
📊 Course Contents
💡 Benefits
⭐ Why This Course
        """
        
        try:
            async with aiohttp.ClientSession() as session:
                headers = {
                    "Authorization": f"Bearer {AIConfig.OPENROUTER_API_KEY}",
                    "HTTP-Referer": "https://github.com/avik",
                    "X-Title": "Telegram Course Bot"
                }
                
                payload = {
                    "model": AIConfig.OPENROUTER_MODEL,
                    "messages": [
                        {"role": "user", "content": prompt}
                    ],
                    "temperature": AIConfig.TEMPERATURE,
                    "max_tokens": AIConfig.MAX_TOKENS * 2
                }
                
                async with session.post(
                    f"{AIConfig.OPENROUTER_BASE_URL}/chat/completions",
                    headers=headers,
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=AIConfig.TIMEOUT)
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        description = data['choices'][0]['message']['content']
                        logger.info(f"✨ Full description generated for: {title}")
                        return description
                    else:
                        return None
        
        except Exception as e:
            logger.error(f"❌ Description generation failed: {e}")
            return None
    
    @staticmethod
    async def enhance_with_emojis(text: str) -> str:
        """Enhance text with relevant emojis"""
        
        prompt = f"""
Add relevant emojis to this text to make it more engaging:

{text}

Rules:
- Add 1-3 emojis per line
- Use contextual, meaningful emojis
- Don't overdo it
- Keep text readable
- Maintain professionalism

Return only the enhanced text with emojis.
        """
        
        try:
            async with aiohttp.ClientSession() as session:
                headers = {
                    "Authorization": f"Bearer {AIConfig.OPENROUTER_API_KEY}",
                    "HTTP-Referer": "https://github.com/avik",
                    "X-Title": "Telegram Course Bot"
                }
                
                payload = {
                    "model": AIConfig.OPENROUTER_MODEL,
                    "messages": [
                        {"role": "user", "content": prompt}
                    ],
                    "temperature": 0.5,
                    "max_tokens": AIConfig.MAX_TOKENS
                }
                
                async with session.post(
                    f"{AIConfig.OPENROUTER_BASE_URL}/chat/completions",
                    headers=headers,
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=AIConfig.TIMEOUT)
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        enhanced = data['choices'][0]['message']['content']
                        return enhanced
                    else:
                        return text
        
        except Exception as e:
            logger.error(f"❌ Emoji enhancement failed: {e}")
            return text

# ═════════════════════════════════════════════════════════════════════

# PREMIUM HANDLERS - Part 3: payment_handler.py

# handlers/payment_handler.py
"""
Payment Handler - UPI Payment verification & management
Features: Transaction tracking, verification, refunds, notifications
"""

import logging
from datetime import datetime
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes
from config import PaymentConfig

logger = logging.getLogger(__name__)

class PaymentHandler:
    """Handle payment verification and processing"""
    
    @staticmethod
    async def verify_payment(user_id: int, course_id: int, amount: float, transaction_id: str) -> dict:
        """Verify payment transaction"""
        
        verification_data = {
            'user_id': user_id,
            'course_id': course_id,
            'amount': amount,
            'transaction_id': transaction_id,
            'status': 'verified',
            'timestamp': datetime.now(),
            'payment_method': PaymentConfig.PAYMENT_METHOD
        }
        
        # TODO: Verify with UPI transaction logs
        logger.info(f"💳 Payment verified: User {user_id}, Amount ₹{amount}")
        return verification_data
    
    @staticmethod
    async def process_refund(order_id: int, reason: str) -> bool:
        """Process refund for a purchase"""
        
        # TODO: Handle refund logic
        logger.info(f"💰 Refund processed for order {order_id}: {reason}")
        return True
    
    @staticmethod
    async def send_payment_notification(context: ContextTypes.DEFAULT_TYPE, user_id: int, course_name: str, amount: float):
        """Send payment confirmation notification"""
        
        message = f"""
✅ PAYMENT CONFIRMATION
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📚 Course: {course_name}
💰 Amount: ₹{amount}
⏱️ Date: {datetime.now().strftime('%d/%m/%Y %H:%M')}
✅ Status: Completed

Thank you for your purchase!
Your course is now available.

🚀 Access Course: /my_courses
        """
        
        try:
            await context.bot.send_message(chat_id=user_id, text=message)
        except Exception as e:
            logger.error(f"❌ Failed to send notification: {e}")
