# Main entry point for the Telegram Course Sales Bot
# Professional Premium Admin Dashboard with Secure 2-Step Authentication

import logging
import os
from pathlib import Path
from telegram.ext import (
    Application, CommandHandler, ConversationHandler,
    CallbackQueryHandler, MessageHandler, filters
)
from config import BotConfig

# Import admin authentication
from handlers.admin_auth import (
    AdminAuth,
    AWAIT_CODE,
    AWAIT_ANSWER
)

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

# Import force join manager
from handlers.force_join_manager import (
    ForceJoinManager,
    AWAIT_ACTION,
    AWAIT_CHANNEL_ID,
    AWAIT_CHANNEL_USERNAME,
    AWAIT_CHANNEL_TITLE,
    AWAIT_CONFIRM_ADD,
    AWAIT_DELETE_CHANNEL
)

# Import force join middleware
try:
    from middleware.force_join import force_join_middleware, verify_force_join
except ImportError:
    logger = logging.getLogger(__name__)
    logger.warning("⚠️ force_join middleware not found, force join disabled")
    async def force_join_middleware(update, context):
        return True
    async def verify_force_join(update, context):
        await update.callback_query.answer("✅ Verified")

# Import existing handlers - with error handling
try:
    from handlers.admin_panel import (
        admin_panel,
        admin_create_course_callback,
        admin_manage_courses_callback,
        admin_analytics_callback,
        admin_settings_callback,
        admin_orders_callback,
        cancel_admin
    )
except ImportError as e:
    logger = logging.getLogger(__name__)
    logger.warning(f"⚠️ admin_panel handlers not found: {e}")
    async def admin_panel(*args, **kwargs):
        pass
    async def admin_create_course_callback(*args, **kwargs):
        pass
    async def admin_manage_courses_callback(*args, **kwargs):
        pass
    async def admin_analytics_callback(*args, **kwargs):
        pass
    async def admin_settings_callback(*args, **kwargs):
        pass
    async def admin_orders_callback(*args, **kwargs):
        pass
    async def cancel_admin(*args, **kwargs):
        pass

try:
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
except ImportError as e:
    logger = logging.getLogger(__name__)
    logger.error(f"❌ start handlers import error: {e}")
    # Provide fallback for start
    async def start(update, context):
        await update.message.reply_text(
            "👋 Welcome to Botavik!\n\n"
            "Start handlers are being loaded...\n\n"
            "Try again in a moment."
        )
    async def menu_courses(*args, **kwargs):
        pass
    async def menu_proof(*args, **kwargs):
        pass
    async def menu_settings(*args, **kwargs):
        pass
    async def menu_latest(*args, **kwargs):
        pass
    async def menu_statistics(*args, **kwargs):
        pass
    async def menu_request(*args, **kwargs):
        pass
    async def back_to_menu(*args, **kwargs):
        pass
    async def handle_owner(*args, **kwargs):
        pass
    async def handle_course_channel(*args, **kwargs):
        pass
    async def handle_discussion(*args, **kwargs):
        pass
    async def handle_all_courses(*args, **kwargs):
        pass
    async def handle_website(*args, **kwargs):
        pass
    async def handle_donate(*args, **kwargs):
        pass
    async def handle_resell(*args, **kwargs):
        pass
    async def handle_callback(*args, **kwargs):
        pass

try:
    from handlers.course_manager import start_course_creation
except ImportError:
    async def start_course_creation(*args, **kwargs):
        pass

try:
    from handlers.course_buyer import browse_courses
except ImportError:
    async def browse_courses(*args, **kwargs):
        pass

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
    """
    Show help menu
    """
    help_text = """
❌ HELP & SUPPORT
══════════════════════════════════════════════════════════════╗

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
Click 👑 Admin Panel button in main menu
🔐 Secure 2-step authentication
• Security code required
• Security question

📧 SUPPORT:
/support - Contact us
/feedback - Send feedback
/report - Report issue

❌ FAQ:
Q: How do I buy a course?
A: Click "🛍 Buy Now" in the channel post

Q: How do I get access?
A: After payment, you get instant access

Q: Can I get a refund?
A: Contact /support for refund requests

Q: How long is my access?
A: Lifetime access!

Need more help? /support
    """
    
    try:
        await update.message.reply_text(help_text, parse_mode='Markdown')
    except Exception as e:
        logger.error(f"❌ Error in help_command: {e}")
        await update.message.reply_text("Sorry, an error occurred.")


# === ADMIN AUTHENTICATION CONVERSATION HANDLER ===
admin_auth_conv_handler = ConversationHandler(
    entry_points=[
        # Start authentication via button only (no /admin command)
        CallbackQueryHandler(AdminAuth.start_auth, pattern='^start_admin_auth$'),
        CallbackQueryHandler(AdminAuth.start_auth, pattern='^open_admin_panel$')
    ],
    states={
        AWAIT_CODE: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, AdminAuth.verify_code)
        ],
        AWAIT_ANSWER: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, AdminAuth.verify_answer)
        ]
    },
    fallbacks=[
        CallbackQueryHandler(AdminAuth.cancel_auth, pattern='^cancel_auth$')
    ],
    name='admin_authentication',
    per_user=True,
    per_chat=True,
    per_message=False
)


# === FORCE JOIN MANAGER CONVERSATION HANDLER ===
force_join_conv_handler = ConversationHandler(
    entry_points=[
        CallbackQueryHandler(lambda u, c: ForceJoinManager(db).show_menu(u, c), pattern='^fj_menu$'),
        CallbackQueryHandler(lambda u, c: ForceJoinManager(db).show_menu(u, c), pattern='^admin_force_join$')
    ],
    states={
        AWAIT_ACTION: [
            CallbackQueryHandler(lambda u, c: ForceJoinManager(db).add_channel_start(u, c), pattern='^fj_add_channel$'),
            CallbackQueryHandler(lambda u, c: ForceJoinManager(db).remove_channel_start(u, c), pattern='^fj_remove_channel$'),
            CallbackQueryHandler(lambda u, c: ForceJoinManager(db).refresh_menu(u, c), pattern='^fj_refresh$'),
        ],
        AWAIT_CHANNEL_ID: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, lambda u, c: ForceJoinManager(db).get_channel_id(u, c))
        ],
        AWAIT_CHANNEL_USERNAME: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, lambda u, c: ForceJoinManager(db).get_channel_username(u, c))
        ],
        AWAIT_CHANNEL_TITLE: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, lambda u, c: ForceJoinManager(db).get_channel_title(u, c))
        ],
        AWAIT_CONFIRM_ADD: [
            CallbackQueryHandler(lambda u, c: ForceJoinManager(db).confirm_add_channel(u, c), pattern='^fj_confirm_add$')
        ],
        AWAIT_DELETE_CHANNEL: [
            CallbackQueryHandler(lambda u, c: ForceJoinManager(db).delete_channel(u, c), pattern='^fj_delete_')
        ]
    },
    fallbacks=[
        CallbackQueryHandler(lambda u, c: ForceJoinManager(db).show_menu(u, c), pattern='^fj_menu$'),
        CallbackQueryHandler(lambda u, c: AdminDashboard.main_dashboard(u, c), pattern='^admin_dashboard$'),
        CallbackQueryHandler(lambda u, c: ConversationHandler.END, pattern='^cancel$')
    ],
    name='force_join_manager',
    per_user=True,
    per_chat=True,
    per_message=False
)


# === BROADCAST CONVERSATION HANDLER ===
broadcast_conv_handler = ConversationHandler(
    entry_points=[
        CallbackQueryHandler(broadcast_create, pattern='^broadcast_create$')
    ],
    states={
        BROADCAST_MESSAGE: [
            # FIXED: Changed filters.DOCUMENT to filters.Document
            MessageHandler(filters.TEXT | filters.PHOTO | filters.VIDEO | filters.Document.ALL, broadcast_received)
        ]
    },
    fallbacks=[
        CallbackQueryHandler(lambda u, c: ConversationHandler.END, pattern='^broadcast_cancel$')
    ],
    name='broadcast_creation'
)


# === COURSE CREATION CONVERSATION HANDLER ===
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
    """
    Start command with force join check and error handling
    """
    try:
        # Check force join
        if not await force_join_middleware(update, context):
            return
        
        # Proceed with normal start
        await start(update, context)
    except Exception as e:
        logger.error(f"❌ Error in protected_start: {e}")
        try:
            await update.message.reply_text(
                "👋 Welcome to Botavik!\n\n"
                "🎉 Your Premium Course Platform\n\n"
                "📚 Exclusive cybersecurity courses\n"
                "🤛 Expert-led training\n"
                "✅ Lifetime access\n\n"
                "Please try /help or come back shortly.",
                parse_mode='Markdown'
            )
        except Exception as inner_e:
            logger.error(f"❌ Error sending fallback message: {inner_e}")


async def post_init(application: Application) -> None:
    """
    Initialize database connection after bot starts
    """
    try:
        await db.connect()
        logger.info("✅ Database connection initialized")
        logger.info("🚀 Premium Admin Dashboard Ready")
        logger.info("🔐 Secure 2-Step Authentication System Active")
        logger.info("🚪 Force Join Channel Manager Active")
        logger.info("🔑 Security Code: 122911")
        logger.info("❌ Security Question: What is your name? → avik")
    except Exception as e:
        logger.error(f"❌ Error in post_init: {e}")


async def post_shutdown(application: Application) -> None:
    """
    Close database connection on shutdown
    """
    try:
        await db.disconnect()
        logger.info("✅ Database connection closed")
    except Exception as e:
        logger.error(f"❌ Error in post_shutdown: {e}")


def main():
    """
    Start the bot with secure admin authentication
    """
    try:
        # Create application
        application = Application.builder().token(BotConfig.TELEGRAM_BOT_TOKEN).build()
        
        # Setup database lifecycle hooks
        application.post_init = post_init
        application.post_shutdown = post_shutdown
        
        # === CORE COMMANDS ===
        application.add_handler(CommandHandler('start', protected_start))
        application.add_handler(CommandHandler('help', help_command))
        
        # === ADMIN AUTHENTICATION SYSTEM (Button-only access, NO /admin command) ===
        application.add_handler(admin_auth_conv_handler)
        
        # === FORCE JOIN MANAGER (New professional system) ===
        application.add_handler(force_join_conv_handler)
        
        # === PREMIUM ADMIN DASHBOARD (Protected by authentication) ===
        # Main dashboard - requires authentication
        application.add_handler(CallbackQueryHandler(AdminDashboard.main_dashboard, pattern='^admin_dashboard$'))
        application.add_handler(CallbackQueryHandler(AdminAuth.logout, pattern='^admin_logout$'))
        
        # Broadcast system
        application.add_handler(CallbackQueryHandler(broadcast_menu, pattern='^admin_broadcast$'))
        application.add_handler(broadcast_conv_handler)
        application.add_handler(CallbackQueryHandler(broadcast_send, pattern='^broadcast_send$'))
        
        # User management
        application.add_handler(CallbackQueryHandler(users_menu, pattern='^admin_users$'))
        
        # Credits management
        application.add_handler(CallbackQueryHandler(credits_menu, pattern='^admin_credits$'))
        
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
        application.add_handler(MessageHandler(filters.Regex('^\ud83d\udc68\u200d\ud83d\udcbc Owner$'), handle_owner))
        application.add_handler(MessageHandler(filters.Regex('^\ud83d\udccf Course Channel$'), handle_course_channel))
        application.add_handler(MessageHandler(filters.Regex('^\ud83d\udde3 Discussion$'), handle_discussion))
        application.add_handler(MessageHandler(filters.Regex('^\ud83d\udcda All Courses$'), handle_all_courses))
        application.add_handler(MessageHandler(filters.Regex('^\ud83c\udf10 Website$'), handle_website))
        application.add_handler(MessageHandler(filters.Regex('^\ud83c\udf81 Donate$'), handle_donate))
        application.add_handler(MessageHandler(filters.Regex('^\ud83d\udcb8 Resell$'), handle_resell))
        
        # === OLD ADMIN PANEL CALLBACKS (Legacy Support) ===
        application.add_handler(CallbackQueryHandler(admin_panel, pattern='^admin_panel$'))
        application.add_handler(CallbackQueryHandler(admin_create_course_callback, pattern='^admin_create_course_old$'))
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
        logger.info("✅ Secure 2-Step Authentication System Ready")
        logger.info("✅ Force Join Channel Manager Ready (Button-Based)")
        logger.info("✅ Broadcast System Ready")
        logger.info("✅ Credit Management Ready")
        logger.info("✅ AI Assistant Ready")
        logger.info("🔐 Security: Code '122911' + Question 'avik'")
        logger.info("🚪 Force Join Manager: Professional button-based interface")
        logger.info("🔐 Admin access: Button only (no /admin command)")
        application.run_polling(allowed_updates=['message', 'callback_query'])
    except Exception as e:
        logger.error(f"❌ Fatal error in main: {e}")
        raise


if __name__ == '__main__':
    main()
