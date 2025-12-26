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
from handlers.admin_panel import (
    admin_panel,
    admin_create_course_callback,
    admin_manage_courses_callback,
    admin_analytics_callback,
    admin_settings_callback,
    admin_orders_callback,
    cancel_admin
)
from handlers.start import (
    start,
    menu_courses,
    menu_proof,
    menu_setting,
    menu_latest,
    menu_status,
    menu_request,
    menu_owner,
    owner_channel,
    owner_all_courses,
    owner_discussion,
    owner_website,
    owner_donate,
    owner_resell,
    owner_refer,
    menu_back,
    handle_callback
)
from handlers.course_manager import start_course_creation
from handlers.course_buyer import browse_courses
from database.db import db

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
        CallbackQueryHandler(start_course_creation, pattern='^admin_create_course$'),
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

async def post_init(application: Application) -> None:
    """Initialize database connection after bot starts"""
    await db.connect()
    logger.info("✅ Database connection initialized")

async def post_shutdown(application: Application) -> None:
    """Close database connection on shutdown"""
    await db.disconnect()
    logger.info("✅ Database connection closed")

def main():
    """Start the bot"""
    # Create application
    application = Application.builder().token(BotConfig.TELEGRAM_BOT_TOKEN).build()
    
    # Setup database lifecycle hooks
    application.post_init = post_init
    application.post_shutdown = post_shutdown
    
    # === CORE COMMANDS ===
    application.add_handler(CommandHandler('start', start))
    application.add_handler(CommandHandler('help', help_command))
    application.add_handler(CommandHandler('admin', admin_panel))
    
    # === MAIN MENU CALLBACKS ===
    application.add_handler(CallbackQueryHandler(menu_courses, pattern='^menu_courses$'))
    application.add_handler(CallbackQueryHandler(menu_proof, pattern='^menu_proof$'))
    application.add_handler(CallbackQueryHandler(menu_setting, pattern='^menu_setting$'))
    application.add_handler(CallbackQueryHandler(menu_latest, pattern='^menu_latest$'))
    application.add_handler(CallbackQueryHandler(menu_status, pattern='^menu_status$'))
    application.add_handler(CallbackQueryHandler(menu_request, pattern='^menu_request$'))
    application.add_handler(CallbackQueryHandler(menu_owner, pattern='^menu_owner$'))
    application.add_handler(CallbackQueryHandler(menu_back, pattern='^menu_back$'))
    
    # === OWNER SECTION CALLBACKS ===
    application.add_handler(CallbackQueryHandler(owner_channel, pattern='^owner_channel$'))
    application.add_handler(CallbackQueryHandler(owner_all_courses, pattern='^owner_all_courses$'))
    application.add_handler(CallbackQueryHandler(owner_discussion, pattern='^owner_discussion$'))
    application.add_handler(CallbackQueryHandler(owner_website, pattern='^owner_website$'))
    application.add_handler(CallbackQueryHandler(owner_donate, pattern='^owner_donate$'))
    application.add_handler(CallbackQueryHandler(owner_resell, pattern='^owner_resell$'))
    application.add_handler(CallbackQueryHandler(owner_refer, pattern='^owner_refer$'))
    
    # === ADMIN PANEL CALLBACKS ===
    application.add_handler(CallbackQueryHandler(admin_create_course_callback, pattern='^admin_create_course$'))
    application.add_handler(CallbackQueryHandler(admin_manage_courses_callback, pattern='^admin_manage_courses$'))
    application.add_handler(CallbackQueryHandler(admin_analytics_callback, pattern='^admin_analytics$'))
    application.add_handler(CallbackQueryHandler(admin_settings_callback, pattern='^admin_settings$'))
    application.add_handler(CallbackQueryHandler(admin_orders_callback, pattern='^admin_orders$'))
    application.add_handler(CallbackQueryHandler(cancel_admin, pattern='^cancel$'))
    
    # === GENERIC CALLBACKS (for remaining actions) ===
    application.add_handler(CallbackQueryHandler(handle_callback, pattern='^(send_request|donate_now|resell_apply|refer_dashboard)$'))
    
    # === COURSE CREATION CONVERSATION ===
    application.add_handler(course_conv_handler)
    
    # === BUYER HANDLERS ===
    application.add_handler(CallbackQueryHandler(browse_courses, pattern=r'^buy_\d+$'))
    
    # Start bot
    logger.info("🤖 Bot starting...")
    application.run_polling(allowed_updates=['message', 'callback_query'])

if __name__ == '__main__':
    main()