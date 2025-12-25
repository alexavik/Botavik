# handlers/course_manager.py
"""
Course Manager Handler - Professional course creation & management
Features: Multi-step form, AI captions, channel posting, validation
"""

import logging
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes, ConversationHandler
from config import BotConfig, CourseConfig, ValidationRules
from utils.validators import validate_title, validate_description, validate_price
from handlers.ai_generator import AIContentGenerator

logger = logging.getLogger(__name__)

# Conversation states
COURSE_TITLE = 1
COURSE_DESCRIPTION = 2
COURSE_CATEGORY = 3
COURSE_PRICE = 4
COURSE_DEMO_VIDEO = 5
CONFIRM_POST = 6

class CourseManager:
    """Professional course creation and management"""
    
    @staticmethod
    async def start_create_course(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Begin course creation flow"""
        user = update.effective_user
        
        intro_text = """
📚 CREATE NEW COURSE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Let's create an amazing course! 🚀

I'll guide you through 5 simple steps:
1️⃣ Course Title
2️⃣ Description
3️⃣ Category
4️⃣ Price
5️⃣ Demo Video

⏱️ This will take about 2 minutes

Let's start! What's your course title?
(Min 5, Max 100 characters)
        """
        
        await update.effective_message.reply_text(intro_text)
        logger.info(f"👤 User {user.id} starting course creation")
        return COURSE_TITLE
    
    @staticmethod
    async def collect_title(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Collect and validate course title"""
        title = update.message.text
        
        # Validate
        is_valid, error_msg = validate_title(title)
        if not is_valid:
            await update.message.reply_text(f"❌ {error_msg}")
            return COURSE_TITLE
        
        context.user_data['course_title'] = title
        
        response = f"""
✅ Title saved: "{title}"

Now tell me about your course.
📝 Write a compelling description:

Examples:
- What will students learn?
- What problems does it solve?
- Why is it unique?

(Min 20, Max 1000 characters)
        """
        
        await update.message.reply_text(response)
        return COURSE_DESCRIPTION
    
    @staticmethod
    async def collect_description(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Collect and validate course description"""
        description = update.message.text
        
        # Validate
        is_valid, error_msg = validate_description(description)
        if not is_valid:
            await update.message.reply_text(f"❌ {error_msg}")
            return COURSE_DESCRIPTION
        
        context.user_data['course_description'] = description
        
        category_text = """
✅ Description saved!

Now select a category for your course:
        """
        
        # Build category buttons
        keyboard = []
        for key, label in CourseConfig.CATEGORIES.items():
            keyboard.append([InlineKeyboardButton(label, callback_data=f"cat_{key}")])
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(category_text, reply_markup=reply_markup)
        
        return COURSE_CATEGORY
    
    @staticmethod
    async def collect_category(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Collect course category"""
        query = update.callback_query
        await query.answer()
        
        category_key = query.data.split("_")[1]
        category_label = CourseConfig.CATEGORIES.get(category_key, "Other")
        
        context.user_data['course_category'] = category_key
        
        price_text = f"""
✅ Category selected: {category_label}

Now set the price for your course:
💰 Enter price in ₹ (min ₹100, max ₹100,000)

Examples:
- Beginner course: ₹299
- Intermediate: ₹499
- Advanced: ₹999
        """
        
        await query.edit_message_text(price_text)
        return COURSE_PRICE
    
    @staticmethod
    async def collect_price(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Collect and validate price"""
        try:
            price = float(update.message.text)
        except ValueError:
            await update.message.reply_text("❌ Please enter a valid number")
            return COURSE_PRICE
        
        # Validate
        is_valid, error_msg = validate_price(price)
        if not is_valid:
            await update.message.reply_text(f"❌ {error_msg}")
            return COURSE_PRICE
        
        context.user_data['course_price'] = price
        
        video_text = f"""
✅ Price set: ₹{price}

Now upload a demo video! 🎬
This will be shown to buyers before purchase.

📹 Requirements:
- Format: MP4, WebM, or Telegram video
- Duration: 10-60 seconds recommended
- Size: Max 20MB
- Quality: At least 720p

Send your demo video now:
        """
        
        await update.message.reply_text(video_text)
        return COURSE_DEMO_VIDEO
    
    @staticmethod
    async def collect_demo_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Collect demo video"""
        video = update.message.video
        
        if not video:
            await update.message.reply_text("❌ Please send a valid video")
            return COURSE_DEMO_VIDEO
        
        # Validate video size
        if video.file_size > CourseConfig.MAX_VIDEO_SIZE:
            await update.message.reply_text(f"❌ Video too large. Max size: 20MB")
            return COURSE_DEMO_VIDEO
        
        context.user_data['demo_video_id'] = video.file_id
        context.user_data['demo_video_file_size'] = video.file_size
        
        # Show preview and generate AI caption
        preview_text = """
✅ Demo video uploaded!

⏳ Generating AI marketing caption...
(Using Gemini 2.0 Flash - Free!)

Please wait...
        """
        
        await update.message.reply_text(preview_text)
        
        # Generate AI caption
        title = context.user_data['course_title']
        description = context.user_data['course_description']
        category = context.user_data['course_category']
        price = context.user_data['course_price']
        
        ai_caption = await AIContentGenerator.generate_course_caption(
            title, description, category, price
        )
        
        context.user_data['ai_caption'] = ai_caption
        
        # Show confirmation
        confirmation_text = f"""
📚 COURSE PREVIEW
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

{ai_caption}

💰 Price: ₹{price}

───────────────────────────────────

Does everything look good? 
        """
        
        keyboard = [
            [
                InlineKeyboardButton("✅ Post to Channel", callback_data="confirm_post_yes"),
                InlineKeyboardButton("❌ Cancel", callback_data="confirm_post_no")
            ]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(confirmation_text, reply_markup=reply_markup)
        
        return CONFIRM_POST
    
    @staticmethod
    async def confirm_post(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Confirm and post course to channel"""
        query = update.callback_query
        await query.answer()
        
        if "no" in query.data:
            await query.edit_message_text("❌ Course creation cancelled. Start over with /create")
            return ConversationHandler.END
        
        # Get course data from context
        title = context.user_data.get('course_title')
        description = context.user_data.get('course_description')
        category = context.user_data.get('course_category')
        price = context.user_data.get('course_price')
        video_id = context.user_data.get('demo_video_id')
        caption = context.user_data.get('ai_caption')
        
        # Create channel post
        channel_caption = f"""
{caption}

💰 Price: ₹{price}

────────────────────────────────
        """
        
        keyboard = [
            [
                InlineKeyboardButton("🛒 Buy Now", callback_data=f"buy_temp"),
                InlineKeyboardButton("❤️ Wishlist", callback_data=f"wish_temp")
            ]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        try:
            # Post to channel (TODO: Save to DB and get ID)
            message = await context.bot.send_video(
                chat_id=BotConfig.PUBLISHING_CHANNEL_ID,
                video=video_id,
                caption=channel_caption,
                reply_markup=reply_markup,
                parse_mode='HTML'
            )
            
            success_text = f"""
✅ COURSE PUBLISHED!
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📚 Course: {title}
💰 Price: ₹{price}
📱 Posted to channel
🔗 Share link: [Channel Link]

🎉 Your course is now live!
Buyers can see it in the channel.

Create another course? /create
View analytics? /admin
            """
            
            await query.edit_message_text(success_text)
            logger.info(f"✅ Course '{title}' published (ID: {message.message_id})")
            
        except Exception as e:
            logger.error(f"❌ Failed to post course: {e}")
            await query.edit_message_text(f"❌ Error posting to channel: {str(e)}")
        
        return ConversationHandler.END
    
    @staticmethod
    async def cancel_creation(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Cancel course creation"""
        await update.message.reply_text("❌ Course creation cancelled.")
        return ConversationHandler.END
