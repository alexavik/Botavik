# Force Join Middleware - Restrict bot access until user joins required channels

import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from telegram.error import TelegramError
from database.db import db

logger = logging.getLogger(__name__)

class ForceJoinMiddleware:
    """Middleware to enforce channel/group membership"""
    
    @staticmethod
    async def check_membership(update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
        """
        Check if user is member of all required channels/groups
        Returns True if user can access bot, False otherwise
        """
        
        # Get user
        user = update.effective_user
        if not user:
            return False
        
        # Check if user is admin (admins bypass force join)
        admin = await db.get_admin(user.id)
        if admin:
            return True
        
        # Get all force join channels
        channels = await db.get_force_join_channels()
        
        # If no channels configured, allow access
        if not channels:
            return True
        
        # Check membership for each channel
        not_joined = []
        
        for channel in channels:
            try:
                member = await context.bot.get_chat_member(
                    chat_id=channel['channel_id'],
                    user_id=user.id
                )
                
                # Check if user is member (not left or kicked)
                if member.status in ['left', 'kicked']:
                    not_joined.append(channel)
                    
            except TelegramError as e:
                logger.error(f"Error checking membership for channel {channel['channel_id']}: {e}")
                # If channel is deleted or bot removed, skip it
                continue
        
        # If user hasn't joined all channels, show force join message
        if not_joined:
            await ForceJoinMiddleware.show_force_join_message(update, context, not_joined)
            return False
        
        return True
    
    @staticmethod
    async def show_force_join_message(update: Update, context: ContextTypes.DEFAULT_TYPE, channels: list):
        """Show message with buttons to join required channels"""
        
        # Build channel list text
        channels_text = ""
        for idx, channel in enumerate(channels, 1):
            channels_text += f"{idx}. **{channel['title']}** (@{channel['username']})\n"
        
        text = f"""
🚪 **JOIN REQUIRED CHANNELS**
═══════════════════════════════════════════════════════════════

⚠️ **To use this bot, you must join these channels first:**

{channels_text}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

👇 Click the buttons below to join:
        """
        
        # Create join buttons
        keyboard = []
        for channel in channels:
            keyboard.append([
                InlineKeyboardButton(
                    f"🔗 Join {channel['title']}",
                    url=f"https://t.me/{channel['username']}"
                )
            ])
        
        # Add verify button
        keyboard.append([
            InlineKeyboardButton("✅ I've Joined, Verify Me", callback_data="verify_membership")
        ])
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        # Send or edit message
        if update.callback_query:
            await update.callback_query.answer("⚠️ Please join all channels first!")
            await update.callback_query.edit_message_text(
                text,
                reply_markup=reply_markup,
                parse_mode='Markdown'
            )
        elif update.message:
            await update.message.reply_text(
                text,
                reply_markup=reply_markup,
                parse_mode='Markdown'
            )

async def verify_membership_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle membership verification when user clicks verify button"""
    query = update.callback_query
    await query.answer("Checking your membership...")
    
    # Check membership
    is_member = await ForceJoinMiddleware.check_membership(update, context)
    
    if is_member:
        # Mark user as verified
        await db.mark_user_verified(query.from_user.id)
        
        text = """
✅ **VERIFICATION SUCCESSFUL**
═══════════════════════════════════════════════════════════════

🎉 Welcome! You can now use all bot features.

Send /start to begin!
        """
        
        await query.edit_message_text(text, parse_mode='Markdown')
    else:
        # User still hasn't joined all channels
        await query.answer("❌ You haven't joined all channels yet!", show_alert=True)
