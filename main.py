# Main entry point for the Telegram Course Sales Bot
# This is the core file that ties everything together

import logging
import os
from pathlib import Path
from telegram.ext import (
    Application, CommandHandler, ConversationHandler,
    CallbackQueryHandler, MessageHandler, filters
)
from config import BotConfig
from handlers.admin_panel import admin_panel
from handlers.course_manager import start_course_creation
from handlers.course_buyer import browse_courses

# Create logs directory if it doesn't exist
Path('logs').mkdir(parents=True, exist_ok=True)

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/bot.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Course creation conversation states
COURSE_TITLE = 1
COURSE_DESCRIPTION = 2
COURSE_CATEGORY = 3
COURSE_PRICE = 4
COURSE_DEMO_VIDEO = 5
CONFIRM_POST = 6

async def start(update, context):
    """Handle /start command and deep links"""
    user = update.effective_user
    args = context.args
    
    if args and len(args) > 0:
        param = args[0]  # e.g., "buy_123" or "wish_456"
        
        if param.startswith("buy_"):
            course_id = int(param.split("_")[1])
            await show_course_details(update, context, course_id)
            return
        
        elif param.startswith("wish_"):
            course_id = int(param.split("_")[1])
            await handle_wishlist(update, context, course_id)
            return
    
    # Normal /start without params
    welcome = f"""
👋 Welcome to Course Sales Bot! 👋
═══════════════════════════════════════════════════════════════

Hi {user.first_name}! 🙂

🎓 Learn amazing courses
💰 100% secure payments
❤️ Save favorites to wishlist

📚 Browse courses: [Open Channel]
📧 Need help? /support
👑 Admin? /admin

What would you like to do?
    """
    
    buttons = [
        [{"text": "📚 Browse Courses", "url": f"https://t.me/{BotConfig.BOT_USERNAME}"}],
        [{"text": "❤️ My Wishlist", "callback_data": "view_wishlist"}],
        [{"text": "🎓 My Courses", "callback_data": "my_courses"}]
    ]
    
    await update.message.reply_text(welcome, parse_mode='Markdown')
    logger.info(f"✅ User {user.id} started bot")

async def help_command(update, context):
    """Show help menu"""
    help_text = """
❓ HELP & SUPPORT
═══════════════════════════════════════════════════════════════

📚 COURSES:
/start - Welcome
/courses - Browse all courses
/wishlist - View wishlist
/my_courses - Your purchased courses

💰 PAYMENTS:
All payments via UPI (FamPay)
✅ Instant verification
✅ Lifetime access after payment

👑 ADMIN:
/admin - Admin panel (authorized users only)

📧 SUPPORT:
/support - Contact us
/feedback - Send feedback
/report - Report issue

❓ FAQ:
Q: How do I buy a course?
A: Click "🛒 Buy Now" in the channel post

Q: How do I get access?
A: After payment, you get instant access

Q: Can I get a refund?
A: Contact /support for refund requests

Q: How long is my access?
A: Lifetime access!

Need more help? /support
    """
    
    await update.message.reply_text(help_text, parse_mode='Markdown')

# Build conversation handler for course creation
course_conv_handler = ConversationHandler(
    entry_points=[
        CallbackQueryHandler(start_course_creation, pattern='^create_course$'),
        CommandHandler('create', start_course_creation)
    ],
    states={
        COURSE_TITLE: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, lambda u, c: None)
        ],
        COURSE_DESCRIPTION: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, lambda u, c: None)
        ],
        COURSE_CATEGORY: [
            CallbackQueryHandler(lambda u, c: None, pattern='^cat_')
        ],
        COURSE_PRICE: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, lambda u, c: None)
        ],
        COURSE_DEMO_VIDEO: [
            MessageHandler(filters.VIDEO, lambda u, c: None)
        ],
        CONFIRM_POST: [
            CallbackQueryHandler(lambda u, c: None, pattern='^confirm_post_')
        ]
    },
    fallbacks=[CommandHandler('cancel', lambda u, c: None)],
    name='course_creation'
)

def main():
    """Start the bot"""
    # Create application
    application = Application.builder().token(BotConfig.TELEGRAM_BOT_TOKEN).build()
    
    # Core commands
    application.add_handler(CommandHandler('start', start))
    application.add_handler(CommandHandler('help', help_command))
    application.add_handler(CommandHandler('admin', admin_panel))
    
    # Course creation conversation
    application.add_handler(course_conv_handler)
    
    # Buyer handlers
    application.add_handler(CallbackQueryHandler(browse_courses, pattern=r'^buy_\d+$'))
    
    # Start bot
    logger.info("🤖 Bot starting...")
    application.run_polling(allowed_updates=['message', 'callback_query'])

if __name__ == '__main__':
    main()