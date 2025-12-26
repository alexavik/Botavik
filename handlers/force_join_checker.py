# Force Join Checker Middleware
# Ensures users join required channels before accessing bot

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from telegram.error import TelegramError
from database.db import db
import logging

logger = logging.getLogger(__name__)

class ForceJoinChecker:
    """Middleware to check force join requirements"""
    
    @staticmethod
    async def check_membership(user_id: int, context: ContextTypes.DEFAULT_TYPE) -> tuple[bool, list]:
        """
        Check if user has joined all required channels
        Returns: (is_member, list_of_not_joined_channels)
        """
        try:
            # Get all force join channels from database
            required_channels = await db.get_force_join_channels()
            
            if not required_channels:
                return True, []
            
            not_joined = []
            
            for channel in required_channels:
                try:
                    # Check membership status
                    member = await context.bot.get_chat_member(
                        chat_id=channel['channel_id'],
                        user_id=user_id
                    )
                    
                    # User must be member, administrator, or creator
                    if member.status not in ['member', 'administrator', 'creator']:
                        not_joined.append(channel)
                        
                except TelegramError as e:
                    logger.error(f"Error checking membership for channel {channel['channel_id']}: {e}")
                    not_joined.append(channel)
            
            return len(not_joined) == 0, not_joined
            
        except Exception as e:
            logger.error(f"Error in force join check: {e}")
            # If error, allow access (fail-safe)
            return True, []
    
    @staticmethod
    async def show_force_join_message(update: Update, context: ContextTypes.DEFAULT_TYPE, channels: list) -> None:
        """
        Show force join message with channel buttons
        """
        user = update.effective_user
        
        # Build channel buttons
        keyboard = []
        for channel in channels:
            keyboard.append([
                InlineKeyboardButton(
                    f"📺 Join {channel['title']}",
                    url=f"https://t.me/{channel['username']}"
                )
            ])
        
        # Add verification button
        keyboard.append([
            InlineKeyboardButton("✅ I Joined - Verify Now", callback_data="verify_force_join")
        ])
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        text = f"""
🔒 **ACCESS REQUIRED**
═════════════════════════════════════════════════════

Hello {user.first_name}! 👋

To use this bot, you must join our official channels first.

**Why Join?**
   ✅ Get latest course updates
   ✅ Exclusive offers & discounts
   ✅ Free learning resources
   ✅ Community support

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

**Required Channels ({len(channels)}):**

Please click the buttons below to join all channels, then click **"I Joined - Verify Now"**

⚠️ **Note:** All features are locked until you join!
        """
        
        if update.callback_query:
            await update.callback_query.answer("Please join all channels first!")
            await update.callback_query.edit_message_text(
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

async def verify_force_join(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle force join verification"""
    query = update.callback_query
    user_id = query.from_user.id
    
    await query.answer("Verifying your membership...")
    
    # Check membership
    is_member, not_joined = await ForceJoinChecker.check_membership(user_id, context)
    
    if is_member:
        # User has joined all channels
        success_text = """
✅ **VERIFICATION SUCCESSFUL**
═════════════════════════════════════════════════════

Thank you for joining! 🎉

You now have full access to the bot.

Use /start to begin exploring!

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        """
        
        keyboard = [[InlineKeyboardButton("🚀 Start Using Bot", callback_data="start")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            success_text,
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
        
        # Mark user as verified in database
        await db.mark_user_verified(user_id)
        
    else:
        # Still not joined all channels
        await ForceJoinChecker.show_force_join_message(update, context, not_joined)

async def force_join_middleware(update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
    """
    Middleware function to check force join before processing commands
    Returns True if user can proceed, False if blocked
    """
    user_id = update.effective_user.id
    
    # Skip for admins
    from handlers.admin_dashboard import AdminDashboard
    if await AdminDashboard.check_admin(user_id):
        return True
    
    # Check if user is verified
    is_verified = await db.is_user_verified(user_id)
    if is_verified:
        return True
    
    # Check membership
    is_member, not_joined = await ForceJoinChecker.check_membership(user_id, context)
    
    if not is_member:
        # Show force join message
        await ForceJoinChecker.show_force_join_message(update, context, not_joined)
        return False
    else:
        # Mark as verified for future
        await db.mark_user_verified(user_id)
        return True

# Export
__all__ = ['ForceJoinChecker', 'verify_force_join', 'force_join_middleware']
