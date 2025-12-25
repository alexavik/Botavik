# Main entry point for the Telegram Course Sales Bot
# This is the core file that ties everything together

import logging
import os
from telegram.ext import (
    Application, CommandHandler, ConversationHandler,
    CallbackQueryHandler, MessageHandler, filters
)
from config import BotConfig
from handlers.admin_panel import admin_panel
from handlers.course_manager import CourseManager
from handlers.course_buyer import CourseBuyer

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
            await CourseBuyer.show_course_details(update, context, course_id)
            return
        
        elif param.startswith("wish_"):
            course_id = int(param.split("_")[1])
            await CourseBuyer.handle_wishlist(update, context, course_id)
            return
    
    # Normal /start without params
    welcome = f"""
ðŸ‘‹ Welcome to Course Sales Bot! ðŸ‘‹
â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”

Hi {user.first_name}! ðŸ‘¤

ðŸŽ“ Learn amazing courses
ðŸ’° 100% secure payments
â¤ï¸ Save favorites to wishlist

ðŸ“š Browse courses: [Open Channel]
ðŸ“§ Need help? /support
ðŸ‘‘ Admin? /admin

What would you like to do?
    """
    
    buttons = [
        [{"text": "ðŸ“š Browse Courses", "url": f"https://t.me/{BotConfig.BOT_USERNAME}"}],
        [{"text": "â¤ï¸ My Wishlist", "callback_data": "view_wishlist"}],
        [{"text": "ðŸŽ“ My Courses", "callback_data": "my_courses"}]
    ]
    
    await update.message.reply_text(welcome, parse_mode='Markdown')
    logger.info(f"âœ… User {user.id} started bot")

async def help_command(update, context):
    """Show help menu"""
    help_text = """
â“ HELP & SUPPORT
â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”

ðŸ“š COURSES:
/start - Welcome
/courses - Browse all courses
/wishlist - View wishlist
/my_courses - Your purchased courses

ðŸ’° PAYMENTS:
All payments via UPI (FamPay)
âœ… Instant verification
âœ… Lifetime access after payment

ðŸ‘‘ ADMIN:
/admin - Admin panel (authorized users only)

ðŸ“§ SUPPORT:
/support - Contact us
/feedback - Send feedback
/report - Report issue

â“ FAQ:
Q: How do I buy a course?
A: Click "ðŸ›’ Buy Now" in the channel post

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
        CallbackQueryHandler(CourseManager.start_create_course, pattern='^create_course$'),
        CommandHandler('create', CourseManager.start_create_course)
    ],
    states={
        COURSE_TITLE: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, CourseManager.collect_title)
        ],
        COURSE_DESCRIPTION: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, CourseManager.collect_description)
        ],
        COURSE_CATEGORY: [
            CallbackQueryHandler(CourseManager.collect_category, pattern='^cat_')
        ],
        COURSE_PRICE: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, CourseManager.collect_price)
        ],
        COURSE_DEMO_VIDEO: [
            MessageHandler(filters.VIDEO, CourseManager.collect_demo_video)
        ],
        CONFIRM_POST: [
            CallbackQueryHandler(CourseManager.confirm_post, pattern='^confirm_post_')
        ]
    },
    fallbacks=[CommandHandler('cancel', CourseManager.cancel_creation)],
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
    application.add_handler(CallbackQueryHandler(CourseBuyer.show_course_details, pattern=r'^buy_\d+$'))
    application.add_handler(CallbackQueryHandler(CourseBuyer.handle_payment, pattern=r'^payment_\d+$'))
    application.add_handler(CallbackQueryHandler(CourseBuyer.verify_payment, pattern=r'^verify_\d+$'))
    application.add_handler(CallbackQueryHandler(CourseBuyer.handle_wishlist, pattern=r'^wish_\d+$'))
    
    # Start bot
    logger.info("ðŸ¤– Bot starting...")
    application.run_polling(allowed_updates=['message', 'callback_query'])

if __name__ == '__main__':
    main()
