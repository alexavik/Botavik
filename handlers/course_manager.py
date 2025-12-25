# 📚 Course Manager Handler - Create & Post Courses

import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler
from telegram.constants import ParseMode
from utils.decorators import admin_only, log_command
from utils.validators import Validator
from models.course import Course
from handlers.ai_generator import generate_caption
from config import BotConfig

logger = logging.getLogger(__name__)

# Conversation states
TITLE, DESCRIPTION, PRICE, CATEGORY, DEMO_VIDEO, CONFIRM = range(6)


@admin_only
@log_command("create")
async def start_course_creation(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start course creation conversation"""
    await update.message.reply_text(
        "📏 Let's create a new course!\n\n"
        "Step 1/6: Send the course title (5-100 characters)"
    )
    return TITLE


async def get_title(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Get course title"""
    title = update.message.text
    
    is_valid, msg = Validator.validate_course_title(title)
    if not is_valid:
        await update.message.reply_text(f"❌ {msg}\n\nPlease try again:")
        return TITLE
    
    context.user_data['course_title'] = title
    
    await update.message.reply_text(
        "✅ Title saved!\n\n"
        "Step 2/6: Send the course description (50-1000 characters)"
    )
    return DESCRIPTION


async def get_description(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Get course description"""
    description = update.message.text
    
    is_valid, msg = Validator.validate_description(description)
    if not is_valid:
        await update.message.reply_text(f"❌ {msg}\n\nPlease try again:")
        return DESCRIPTION
    
    context.user_data['course_description'] = description
    
    await update.message.reply_text(
        "✅ Description saved!\n\n"
        "Step 3/6: Send the course price (₹ 99 - ₹ 99,999)"
    )
    return PRICE


async def get_price(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Get course price"""
    price_text = update.message.text
    
    is_valid, msg = Validator.validate_price(price_text)
    if not is_valid:
        await update.message.reply_text(f"❌ {msg}\n\nPlease try again:")
        return PRICE
    
    context.user_data['course_price'] = float(price_text)
    
    keyboard = [
        [InlineKeyboardButton("💻 Programming", callback_data="cat_programming")],
        [InlineKeyboardButton("🔐 Cybersecurity", callback_data="cat_cybersecurity")],
        [InlineKeyboardButton("🌐 Web Dev", callback_data="cat_web")],
        [InlineKeyboardButton("📱 Mobile Dev", callback_data="cat_mobile")],
        [InlineKeyboardButton("📚 Other", callback_data="cat_other")],
        [InlineKeyboardButton("⏭️ Skip", callback_data="cat_skip")],
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        f"✅ Price ₹{context.user_data['course_price']} saved!\n\n"
        "Step 4/6: Select a category:",
        reply_markup=reply_markup
    )
    return CATEGORY


async def get_category(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Get course category"""
    query = update.callback_query
    await query.answer()
    
    category_data = {
        'cat_programming': '💻 Programming',
        'cat_cybersecurity': '🔐 Cybersecurity',
        'cat_web': '🌐 Web Dev',
        'cat_mobile': '📱 Mobile Dev',
        'cat_other': '📚 Other',
        'cat_skip': None
    }
    
    category = category_data.get(query.data)
    context.user_data['course_category'] = category
    
    await query.edit_message_text(
        f"{"✅ Category saved!" if category else "⏭️ Skipped category"}\n\n"
        "Step 5/6: Send the demo video (optional)\n\n"
        "Forward a video or send /skip"
    )
    
    return DEMO_VIDEO


async def get_demo_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Get demo video"""
    if update.message.video:
        video_id = update.message.video.file_id
        context.user_data['course_demo_video'] = video_id
        
        await update.message.reply_text("✅ Demo video saved!")
    elif update.message.text == '/skip':
        context.user_data['course_demo_video'] = None
        await update.message.reply_text("⏭️ Skipped demo video")
    else:
        await update.message.reply_text("❌ Please send a video or /skip")
        return DEMO_VIDEO
    
    # Proceed to confirmation
    await confirm_course(update, context)
    return CONFIRM


async def confirm_course(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Confirm course details before creation"""
    data = context.user_data
    
    message = f"""
📋 COURSE DETAILS REVIEW:

📏 Title: {data.get('course_title')}
📚 Description: {data.get('course_description')[:100]}...
💰 Price: ₹{data.get('course_price')}
🏗️ Category: {data.get('course_category') or 'Not set'}
🎥 Demo Video: {'✅ Yes' if data.get('course_demo_video') else '❌ No'}

Does everything look correct?
"""
    
    keyboard = [
        [InlineKeyboardButton("✅ Create Course", callback_data="confirm_create")],
        [InlineKeyboardButton("❌ Cancel", callback_data="confirm_cancel")],
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    if update.callback_query:
        await update.callback_query.edit_message_text(message, reply_markup=reply_markup)
    else:
        await update.message.reply_text(message, reply_markup=reply_markup)


async def create_and_post_course(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Create course and post to channel"""
    query = update.callback_query
    await query.answer()
    
    data = context.user_data
    
    try:
        await query.edit_message_text("⏳ Creating course...")
        
        # Create course
        course_id = await Course.create(
            title=data['course_title'],
            description=data['course_description'],
            price=data['course_price'],
            category=data.get('course_category'),
            demo_video_id=data.get('course_demo_video')
        )
        
        # Generate AI caption
        caption = await generate_caption(
            title=data['course_title'],
            description=data['course_description'],
            price=data['course_price']
        )
        
        await Course.update_caption(course_id, caption)
        
        # Post to channel
        message_text = f"""
{data['course_title']} ✨

{caption}

💰 Price: ₹{data['course_price']}
"""
        
        keyboard = [
            [InlineKeyboardButton("🛒 Buy Now", url=f"https://t.me/{BotConfig.BOT_USERNAME}?start=buy_{course_id}")],
            [InlineKeyboardButton("❤️ Add to Wishlist", url=f"https://t.me/{BotConfig.BOT_USERNAME}?start=wish_{course_id}")],
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        # Send to channel
        if data.get('course_demo_video'):
            channel_msg = await context.bot.send_video(
                chat_id=BotConfig.PUBLISHING_CHANNEL_ID,
                video=data['course_demo_video'],
                caption=message_text,
                parse_mode=ParseMode.HTML,
                reply_markup=reply_markup
            )
        else:
            channel_msg = await context.bot.send_message(
                chat_id=BotConfig.PUBLISHING_CHANNEL_ID,
                text=message_text,
                parse_mode=ParseMode.HTML,
                reply_markup=reply_markup
            )
        
        # Save channel post ID
        await Course.update_channel_post(course_id, channel_msg.message_id)
        
        # Clear data
        context.user_data.clear()
        
        await query.edit_message_text(
            f"✅ Course created successfully!\n\n"
            f"Course ID: {course_id}\n"
            f"Posted to channel!\n\n"
            f"📚 View your course in the channel!"
        )
        
        logger.info(f"✅ Course {course_id} created and posted to channel")
        return ConversationHandler.END
        
    except Exception as e:
        logger.error(f"❌ Error creating course: {e}")
        await query.edit_message_text(f"❌ Error creating course: {e}")
        return ConversationHandler.END