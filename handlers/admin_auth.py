# 🔐 Secure Admin Authentication System

import logging
from datetime import datetime, timedelta
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler
from database.db import db

logger = logging.getLogger(__name__)

# Conversation states
SECURITY_CODE = 1
SECURITY_QUESTION = 2

# Security credentials
SECURITY_CODE_CORRECT = "122911"
SECURITY_ANSWER_CORRECT = "avik"

# Session management (stores authenticated admin sessions)
admin_sessions = {}
SESSION_TIMEOUT_MINUTES = 5


class AdminAuth:
    """Secure Admin Authentication Handler"""
    
    @staticmethod
    def is_session_valid(user_id: int) -> bool:
        """
        Check if user has valid authenticated session
        
        Args:
            user_id: Telegram user ID
        
        Returns:
            True if session valid, False otherwise
        """
        if user_id not in admin_sessions:
            return False
        
        session_time = admin_sessions[user_id]
        time_diff = datetime.now() - session_time
        
        # Session expires after 5 minutes of inactivity
        if time_diff > timedelta(minutes=SESSION_TIMEOUT_MINUTES):
            del admin_sessions[user_id]
            return False
        
        # Refresh session time
        admin_sessions[user_id] = datetime.now()
        return True
    
    @staticmethod
    def create_session(user_id: int):
        """Create authenticated session for user"""
        admin_sessions[user_id] = datetime.now()
        logger.info(f"✅ Admin session created for user {user_id}")
    
    @staticmethod
    def destroy_session(user_id: int):
        """Destroy user session"""
        if user_id in admin_sessions:
            del admin_sessions[user_id]
            logger.info(f"🚪 Admin session destroyed for user {user_id}")
    
    @staticmethod
    async def start_auth(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """
        Start admin authentication process
        """
        query = update.callback_query
        user = update.effective_user
        
        # Check if user is already admin in database
        is_admin = await db.is_admin(user.id)
        if not is_admin:
            await query.answer("❌ Access Denied: Not authorized", show_alert=True)
            return ConversationHandler.END
        
        # Check if already authenticated
        if AdminAuth.is_session_valid(user.id):
            # Already authenticated, go to dashboard
            from handlers.admin_dashboard import AdminDashboard
            await AdminDashboard.main_dashboard(update, context)
            return ConversationHandler.END
        
        # Start authentication
        text = """
🔐 **ADMIN AUTHENTICATION**
══════════════════════════════════════════════════════════════════════════════

⚠️ **SECURE ACCESS REQUIRED**

🔑 To access the admin panel, please verify your identity.

**Step 1 of 2: Enter Security Code**

Please type the 6-digit security code:

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
⏱️ You have 2 minutes to complete authentication
        """
        
        keyboard = [
            [InlineKeyboardButton("❌ Cancel", callback_data="auth_cancel")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            text,
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
        
        # Store attempt tracking
        context.user_data['auth_attempts'] = 0
        context.user_data['auth_start_time'] = datetime.now()
        
        return SECURITY_CODE


async def security_code_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Handle security code input
    """
    user = update.effective_user
    code_input = update.message.text.strip()
    
    # Check timeout (2 minutes)
    auth_start = context.user_data.get('auth_start_time')
    if auth_start:
        time_diff = datetime.now() - auth_start
        if time_diff > timedelta(minutes=2):
            await update.message.reply_text(
                "⏱️ **Authentication Timeout**\n\nPlease start again.",
                parse_mode='Markdown'
            )
            return ConversationHandler.END
    
    # Check code
    if code_input == SECURITY_CODE_CORRECT:
        # Code correct, ask security question
        text = """
✅ **CODE VERIFIED**
══════════════════════════════════════════════════════════════════════════════

**Step 2 of 2: Security Question**

🔐 What is your name? (lowercase only)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
💡 Hint: First name, all lowercase letters
        """
        
        keyboard = [
            [InlineKeyboardButton("❌ Cancel", callback_data="auth_cancel")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            text,
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
        
        return SECURITY_QUESTION
    
    else:
        # Wrong code
        attempts = context.user_data.get('auth_attempts', 0) + 1
        context.user_data['auth_attempts'] = attempts
        
        if attempts >= 3:
            # Max attempts reached
            await update.message.reply_text(
                """❌ **AUTHENTICATION FAILED**
══════════════════════════════════════════════════════════════════════════════

🚫 Maximum attempts exceeded.

⏱️ Please wait 5 minutes before trying again.
                """,
                parse_mode='Markdown'
            )
            return ConversationHandler.END
        
        remaining = 3 - attempts
        await update.message.reply_text(
            f"""❌ **INCORRECT CODE**
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

⚠️ Invalid security code.

🔄 Remaining attempts: **{remaining}**

Please try again:
            """,
            parse_mode='Markdown'
        )
        
        return SECURITY_CODE


async def security_question_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Handle security question answer
    """
    user = update.effective_user
    answer_input = update.message.text.strip().lower()
    
    # Check timeout
    auth_start = context.user_data.get('auth_start_time')
    if auth_start:
        time_diff = datetime.now() - auth_start
        if time_diff > timedelta(minutes=2):
            await update.message.reply_text(
                "⏱️ **Authentication Timeout**\n\nPlease start again.",
                parse_mode='Markdown'
            )
            return ConversationHandler.END
    
    # Check answer
    if answer_input == SECURITY_ANSWER_CORRECT:
        # Authentication successful!
        AdminAuth.create_session(user.id)
        
        success_text = """
✅ **AUTHENTICATION SUCCESSFUL**
══════════════════════════════════════════════════════════════════════════════

🎉 Welcome, Avik!

🔓 Access granted to Admin Dashboard

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
⏱️ Session valid for 5 minutes

Opening admin panel...
        """
        
        keyboard = [
            [InlineKeyboardButton("👑 Open Admin Dashboard", callback_data="admin_dashboard")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            success_text,
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
        
        return ConversationHandler.END
    
    else:
        # Wrong answer
        attempts = context.user_data.get('auth_attempts', 0) + 1
        context.user_data['auth_attempts'] = attempts
        
        if attempts >= 3:
            await update.message.reply_text(
                """❌ **AUTHENTICATION FAILED**
══════════════════════════════════════════════════════════════════════════════

🚫 Maximum attempts exceeded.

⏱️ Please wait 5 minutes before trying again.
                """,
                parse_mode='Markdown'
            )
            return ConversationHandler.END
        
        remaining = 3 - attempts
        await update.message.reply_text(
            f"""❌ **INCORRECT ANSWER**
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

⚠️ Invalid answer.

🔄 Remaining attempts: **{remaining}**

Please try again (lowercase only):
            """,
            parse_mode='Markdown'
        )
        
        return SECURITY_QUESTION


async def auth_cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Cancel authentication process
    """
    query = update.callback_query
    
    await query.answer("Authentication cancelled")
    await query.edit_message_text(
        """❌ **AUTHENTICATION CANCELLED**
══════════════════════════════════════════════════════════════════════════════

🔙 Returning to main menu...
        """,
        parse_mode='Markdown'
    )
    
    return ConversationHandler.END


async def check_auth_and_open_dashboard(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Check authentication before opening dashboard
    This is called when user clicks admin panel button
    """
    query = update.callback_query
    user = update.effective_user
    
    # First check if user is admin in database
    is_admin = await db.is_admin(user.id)
    if not is_admin:
        await query.answer("❌ Access Denied: Not authorized", show_alert=True)
        return
    
    # Check if session is valid
    if AdminAuth.is_session_valid(user.id):
        # Already authenticated, open dashboard
        from handlers.admin_dashboard import AdminDashboard
        await AdminDashboard.main_dashboard(update, context)
    else:
        # Need authentication
        await AdminAuth.start_auth(update, context)


async def logout_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Logout from admin panel
    """
    query = update.callback_query
    user = update.effective_user
    
    AdminAuth.destroy_session(user.id)
    
    await query.answer("Logged out successfully")
    await query.edit_message_text(
        """🚪 **LOGGED OUT**
══════════════════════════════════════════════════════════════════════════════

✅ You have been logged out from admin panel.

🔐 Session destroyed for security.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
To access again, you will need to re-authenticate.
        """,
        parse_mode='Markdown'
    )
