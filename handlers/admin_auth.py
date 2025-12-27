# 🔒 Secure Admin Authentication Handler

import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler
from datetime import datetime, timedelta
from database.db import db

logger = logging.getLogger(__name__)

# Security configuration
SECURITY_CODE = "122911"
SECURITY_ANSWER = "avik"  # must be lowercase
SESSION_TIMEOUT = timedelta(minutes=30)  # Session expires after 30 minutes

# Conversation states
AWAIT_CODE = 1
AWAIT_ANSWER = 2


class AdminAuth:
    """Secure admin authentication with code + security question"""
    
    @staticmethod
    async def start_auth(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """
        Start authentication flow - Request security code
        """
        user = update.effective_user
        query = update.callback_query
        
        # Check if user is already authenticated
        if await AdminAuth.is_authenticated(user.id, context):
            # Already authenticated, show admin dashboard
            from handlers.admin_dashboard import AdminDashboard
            return await AdminDashboard.main_dashboard(update, context)
        
        # Check if user is admin in database
        is_admin = await db.is_admin(user.id)
        if not is_admin:
            error_text = """🚫 **ACCESS DENIED**

❌ You are not authorized to access the admin panel.

🔐 This area is restricted to administrators only."""
            
            keyboard = [[InlineKeyboardButton("🏠 Main Menu", callback_data="start")]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            if query:
                await query.answer("❌ Access Denied", show_alert=True)
                await query.edit_message_text(
                    error_text,
                    reply_markup=reply_markup,
                    parse_mode='Markdown'
                )
            else:
                await update.message.reply_text(
                    error_text,
                    reply_markup=reply_markup,
                    parse_mode='Markdown'
                )
            return ConversationHandler.END
        
        # Start authentication - Request code
        text = """🔐 **ADMIN AUTHENTICATION**
═══════════════════════════════════════════════════════════════

**Step 1 of 2:** Security Code Verification

🔑 Please enter the **6-digit security code** to continue.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
⚠️ Only authorized administrators have this code.

💡 Type the code in the chat below."""
        
        keyboard = [[InlineKeyboardButton("❌ Cancel", callback_data="cancel_auth")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        if query:
            await query.edit_message_text(
                text,
                reply_markup=reply_markup,
                parse_mode='Markdown'
            )
        else:
            await update.message.reply_text(
                text,
                reply_markup=reply_markup,
                parse_mode='Markdown'
            )
        
        return AWAIT_CODE
    
    
    @staticmethod
    async def verify_code(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """
        Verify security code (122911)
        """
        user = update.effective_user
        code_input = update.message.text.strip()
        
        # Check if code is correct
        if code_input != SECURITY_CODE:
            # Wrong code
            text = """❌ **INCORRECT CODE**
═══════════════════════════════════════════════════════════════

🚫 The security code you entered is incorrect.

🔄 Please try again or contact the administrator.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
💡 Type the correct 6-digit code."""
            
            keyboard = [[InlineKeyboardButton("❌ Cancel", callback_data="cancel_auth")]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await update.message.reply_text(
                text,
                reply_markup=reply_markup,
                parse_mode='Markdown'
            )
            
            return AWAIT_CODE  # Stay in code verification state
        
        # Code is correct - Move to security question
        text = """✅ **CODE VERIFIED**
═══════════════════════════════════════════════════════════════

**Step 2 of 2:** Security Question

❓ **What is your name?**

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
⚠️ Answer must be in lowercase letters only.

💡 Type your answer in the chat below."""
        
        keyboard = [[InlineKeyboardButton("❌ Cancel", callback_data="cancel_auth")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            text,
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
        
        return AWAIT_ANSWER
    
    
    @staticmethod
    async def verify_answer(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """
        Verify security question answer (avik)
        """
        user = update.effective_user
        answer_input = update.message.text.strip().lower()  # Convert to lowercase
        
        # Check if answer is correct
        if answer_input != SECURITY_ANSWER:
            # Wrong answer
            text = """❌ **INCORRECT ANSWER**
═══════════════════════════════════════════════════════════════

🚫 The security answer you entered is incorrect.

🔄 Please try again.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
💡 Remember: answer must be in lowercase."""
            
            keyboard = [[InlineKeyboardButton("❌ Cancel", callback_data="cancel_auth")]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await update.message.reply_text(
                text,
                reply_markup=reply_markup,
                parse_mode='Markdown'
            )
            
            return AWAIT_ANSWER  # Stay in answer verification state
        
        # Answer is correct - Grant access
        # Store authentication in context
        context.user_data['authenticated'] = True
        context.user_data['auth_time'] = datetime.now()
        context.user_data['auth_user_id'] = user.id
        
        # Success message
        success_text = """🎉 **AUTHENTICATION SUCCESSFUL**
═══════════════════════════════════════════════════════════════

✅ Welcome to the Admin Panel!

🔒 Your session is now active.
⏱️ Session expires in 30 minutes.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
👑 Click below to access the dashboard."""
        
        keyboard = [[InlineKeyboardButton("👑 Open Admin Dashboard", callback_data="admin_dashboard")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            success_text,
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
        
        logger.info(f"✅ Admin authenticated: {user.id} (@{user.username})")
        
        return ConversationHandler.END
    
    
    @staticmethod
    async def cancel_auth(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """
        Cancel authentication flow
        """
        query = update.callback_query
        
        text = """🚫 **AUTHENTICATION CANCELLED**

You have cancelled the authentication process.

🔙 Use the button below to return to the main menu."""
        
        keyboard = [[InlineKeyboardButton("🏠 Main Menu", callback_data="start")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        if query:
            await query.edit_message_text(
                text,
                reply_markup=reply_markup,
                parse_mode='Markdown'
            )
            await query.answer("❌ Cancelled")
        else:
            await update.message.reply_text(
                text,
                reply_markup=reply_markup,
                parse_mode='Markdown'
            )
        
        return ConversationHandler.END
    
    
    @staticmethod
    async def is_authenticated(user_id: int, context: ContextTypes.DEFAULT_TYPE) -> bool:
        """
        Check if user is authenticated and session is valid
        
        Args:
            user_id: Telegram user ID
            context: Bot context
        
        Returns:
            True if authenticated and session valid, False otherwise
        """
        # Check if authenticated flag exists
        if not context.user_data.get('authenticated'):
            return False
        
        # Check if user ID matches
        if context.user_data.get('auth_user_id') != user_id:
            return False
        
        # Check session timeout
        auth_time = context.user_data.get('auth_time')
        if not auth_time:
            return False
        
        # Check if session expired (30 minutes)
        if datetime.now() - auth_time > SESSION_TIMEOUT:
            # Session expired - clear authentication
            context.user_data['authenticated'] = False
            logger.info(f"⏱️ Session expired for user {user_id}")
            return False
        
        return True
    
    
    @staticmethod
    async def logout(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """
        Logout from admin session
        """
        query = update.callback_query
        user = update.effective_user
        
        # Clear authentication
        context.user_data['authenticated'] = False
        context.user_data['auth_time'] = None
        context.user_data['auth_user_id'] = None
        
        text = """👋 **LOGGED OUT**

✅ You have been logged out successfully.

🔒 Your admin session has ended.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🔙 Click below to return to main menu."""
        
        keyboard = [[InlineKeyboardButton("🏠 Main Menu", callback_data="start")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        if query:
            await query.edit_message_text(
                text,
                reply_markup=reply_markup,
                parse_mode='Markdown'
            )
            await query.answer("👋 Logged out")
        
        logger.info(f"👋 Admin logged out: {user.id} (@{user.username})")
        
        return ConversationHandler.END
    
    
    @staticmethod
    async def check_auth_middleware(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """
        Middleware to check authentication before accessing admin features
        Call this at the start of admin dashboard functions
        
        Returns:
            True if authenticated, False otherwise
        """
        user = update.effective_user
        query = update.callback_query
        
        # Check database admin status
        is_db_admin = await db.is_admin(user.id)
        if not is_db_admin:
            error_text = "🚫 **ACCESS DENIED**\n\nYou are not an administrator."
            
            if query:
                await query.answer("❌ Access Denied", show_alert=True)
            else:
                keyboard = [[InlineKeyboardButton("🏠 Main Menu", callback_data="start")]]
                await update.message.reply_text(
                    error_text,
                    reply_markup=InlineKeyboardMarkup(keyboard),
                    parse_mode='Markdown'
                )
            return False
        
        # Check authentication session
        if not await AdminAuth.is_authenticated(user.id, context):
            # Not authenticated - redirect to auth flow
            text = """🔐 **AUTHENTICATION REQUIRED**

⚠️ Your session has expired or you need to authenticate.

🔒 Please authenticate to access the admin panel."""
            
            keyboard = [
                [
                    InlineKeyboardButton("🔑 Authenticate", callback_data="start_admin_auth"),
                    InlineKeyboardButton("❌ Cancel", callback_data="start")
                ]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            if query:
                await query.edit_message_text(
                    text,
                    reply_markup=reply_markup,
                    parse_mode='Markdown'
                )
                await query.answer("🔐 Authentication Required", show_alert=True)
            else:
                await update.message.reply_text(
                    text,
                    reply_markup=reply_markup,
                    parse_mode='Markdown'
                )
            
            return False
        
        return True


# Export for use in other modules
__all__ = ['AdminAuth', 'AWAIT_CODE', 'AWAIT_ANSWER']
