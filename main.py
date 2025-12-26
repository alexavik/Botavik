# Main entry point for the Telegram Course Sales Bot
# Professional Premium Admin Dashboard Integration

import logging
import os
from pathlib import Path
from telegram.ext import (
    Application, CommandHandler, ConversationHandler,
    CallbackQueryHandler, MessageHandler, filters
)
from config import BotConfig

# Import admin dashboard
from handlers.admin_dashboard import (
    AdminDashboard,
    broadcast_menu,
    broadcast_create,
    broadcast_received,
    broadcast_send,
    users_menu,
    credits_menu,
    force_join_menu,
    manage_admins_menu,
    content_editor_menu,
    ai_assistant_menu,
    BROADCAST_MESSAGE
)

# Import force join checker
from handlers.force_join_checker import (
    verify_force_join,
    force_join_middleware
)

# Import existing handlers
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
    menu_settings,
    menu_latest,
    menu_statistics,
    menu_request,
    back_to_menu,
    handle_owner,
    handle_course_channel,
    handle_discussion,
    handle_all_courses,
    handle_website,
    handle_donate,
    handle_resell,
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
A: Click "🛍️ Buy Now" in the channel post

Q: How do I get access?
A: After payment, you get instant access

Q: Can I get a refund?
A: Contact /support for refund requests

Q: How long is my access?
A: Lifetime access!

Need more help? /support
    """
    
    await update.message.reply_text(help_text, parse_mode='Markdown')

# Build conversation handler for broadcast
broadcast_conv_handler = ConversationHandler(
    entry_points=[
        CallbackQueryHandler(broadcast_create, pattern='^broadcast_create$')
    ],
    states={
        BROADCAST_MESSAGE: [
            MessageHandler(filters.TEXT | filters.PHOTO | filters.VIDEO | filters.DOCUMENT, broadcast_received)
        ]
    },
    fallbacks=[
        CallbackQueryHandler(lambda u, c: ConversationHandler.END, pattern='^broadcast_cancel$')
    ],
    name='broadcast_creation'
)

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

async def protected_start(update, context):
    """Start command with force join check"""
    # Check force join
    if not await force_join_middleware(update, context):
        return
    
    # Proceed with normal start
    await start(update, context)

async def post_init(application: Application) -> None:
    """Initialize database connection after bot starts"""
    await db.connect()
    logger.info("✅ Database connection initialized")
    logger.info("🚀 Premium Admin Dashboard Ready")

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
    application.add_handler(CommandHandler('start', protected_start))
    application.add_handler(CommandHandler('help', help_command))
    application.add_handler(CommandHandler('admin', AdminDashboard.main_dashboard))
    
    # === PREMIUM ADMIN DASHBOARD ===
    # Main dashboard
    application.add_handler(CallbackQueryHandler(AdminDashboard.main_dashboard, pattern='^admin_dashboard$'))
    
    # Broadcast system
    application.add_handler(CallbackQueryHandler(broadcast_menu, pattern='^admin_broadcast$'))
    application.add_handler(broadcast_conv_handler)
    application.add_handler(CallbackQueryHandler(broadcast_send, pattern='^broadcast_send$'))
    
    # User management
    application.add_handler(CallbackQueryHandler(users_menu, pattern='^admin_users$'))
    
    # Credits management
    application.add_handler(CallbackQueryHandler(credits_menu, pattern='^admin_credits$'))
    
    # Force join management
    application.add_handler(CallbackQueryHandler(force_join_menu, pattern='^admin_force_join$'))
    application.add_handler(CallbackQueryHandler(verify_force_join, pattern='^verify_force_join$'))
    
    # Admin management
    application.add_handler(CallbackQueryHandler(manage_admins_menu, pattern='^admin_manage_admins$'))
    
    # Content editor
    application.add_handler(CallbackQueryHandler(content_editor_menu, pattern='^admin_content$'))
    
    # AI assistant
    application.add_handler(CallbackQueryHandler(ai_assistant_menu, pattern='^admin_ai$'))
    
    # === INLINE KEYBOARD HANDLERS (Main Menu) ===
    application.add_handler(CallbackQueryHandler(menu_courses, pattern='^menu_courses$'))
    application.add_handler(CallbackQueryHandler(menu_proof, pattern='^menu_proof$'))
    application.add_handler(CallbackQueryHandler(menu_settings, pattern='^menu_settings$'))
    application.add_handler(CallbackQueryHandler(menu_latest, pattern='^menu_latest$'))
    application.add_handler(CallbackQueryHandler(menu_statistics, pattern='^menu_statistics$'))
    application.add_handler(CallbackQueryHandler(menu_request, pattern='^menu_request$'))
    application.add_handler(CallbackQueryHandler(back_to_menu, pattern='^back_to_menu$'))
    
    # === REPLY KEYBOARD HANDLERS (Bottom Menu) ===
    application.add_handler(MessageHandler(filters.Regex('^👨‍💼 Owner$'), handle_owner))
    application.add_handler(MessageHandler(filters.Regex('^📺 Course Channel$'), handle_course_channel))
    application.add_handler(MessageHandler(filters.Regex('^💬 Discussion$'), handle_discussion))
    application.add_handler(MessageHandler(filters.Regex('^📚 All Courses$'), handle_all_courses))
    application.add_handler(MessageHandler(filters.Regex('^🌐 Website$'), handle_website))
    application.add_handler(MessageHandler(filters.Regex('^🎁 Donate$'), handle_donate))
    application.add_handler(MessageHandler(filters.Regex('^💸 Resell$'), handle_resell))
    
    # === OLD ADMIN PANEL CALLBACKS (Legacy Support) ===
    application.add_handler(CallbackQueryHandler(admin_panel, pattern='^admin_panel$'))
    application.add_handler(CallbackQueryHandler(admin_create_course_callback, pattern='^admin_create_course$'))
    application.add_handler(CallbackQueryHandler(admin_manage_courses_callback, pattern='^admin_manage_courses$'))
    application.add_handler(CallbackQueryHandler(admin_analytics_callback, pattern='^admin_analytics$'))
    application.add_handler(CallbackQueryHandler(admin_settings_callback, pattern='^admin_settings$'))
    application.add_handler(CallbackQueryHandler(admin_orders_callback, pattern='^admin_orders$'))
    application.add_handler(CallbackQueryHandler(cancel_admin, pattern='^cancel$'))
    
    # === GENERIC CALLBACKS (for remaining actions) ===
    application.add_handler(CallbackQueryHandler(handle_callback, pattern='^(send_request|donate_now|resell_apply)$'))
    
    # === COURSE CREATION CONVERSATION ===
    application.add_handler(course_conv_handler)
    
    # === BUYER HANDLERS ===
    application.add_handler(CallbackQueryHandler(browse_courses, pattern=r'^buy_\d+$'))
    
    # Start bot
    logger.info("🤖 Bot starting with Premium Admin Dashboard...")
    logger.info("✅ Force Join Middleware Active")
    logger.info("✅ Broadcast System Ready")
    logger.info("✅ Credit Management Ready")
    logger.info("✅ AI Assistant Ready")
    application.run_polling(allowed_updates=['message', 'callback_query'])

if __name__ == '__main__':
    main()
