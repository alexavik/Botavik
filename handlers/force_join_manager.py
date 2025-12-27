# Force Join Channel Manager Handler
# Manage force join channels through admin panel with buttons

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler
from telegram.error import TelegramError
import logging

logger = logging.getLogger(__name__)

# Conversation states
AWAIT_ACTION = 1
AWAIT_CHANNEL_ID = 2
AWAIT_CHANNEL_USERNAME = 3
AWAIT_CHANNEL_TITLE = 4
AWAIT_CONFIRM_ADD = 5
AWAIT_DELETE_CHANNEL = 6


class ForceJoinManager:
    """Manage force join channels through admin panel"""
    
    def __init__(self, db):
        self.db = db
    
    async def show_menu(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Show force join management menu"""
        query = update.callback_query
        await query.answer()
        
        # Get current force join channels
        channels = self.db.get_force_join_channels()
        
        text = """🚪 FORCE JOIN CHANNEL MANAGER
═══════════════════════════════════════════════════════════════

📊 Current Force Join Channels: {}

{}─ What would you like to do?
        """.format(
            len(channels),
            "\n".join([f"✅ @{ch['username']} (ID: {ch['channel_id']})" for ch in channels]) if channels else "📭No channels added yet\n"
        )
        
        keyboard = [
            [InlineKeyboardButton("➕ Add Channel", callback_data="fj_add_channel")],
            [InlineKeyboardButton("❌ Remove Channel", callback_data="fj_remove_channel")],
            [InlineKeyboardButton("🔄 Refresh List", callback_data="fj_refresh")],
            [InlineKeyboardButton("🔙 Back to Admin", callback_data="admin_dashboard")]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(text, reply_markup=reply_markup, parse_mode='Markdown')
        return AWAIT_ACTION
    
    async def add_channel_start(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Start adding a new force join channel"""
        query = update.callback_query
        await query.answer()
        
        text = """➕ ADD NEW FORCE JOIN CHANNEL
═══════════════════════════════════════════════════════════════

📝 Step 1/3: Send Channel ID

💡 How to get channel ID:
1. Forward a message from the channel to @userinfobot
2. Bot will show you the channel ID (negative number like -1001234567890)
3. Copy and send that ID

⚠️ Important:
- Channel must be public
- Bot must be admin in the channel
- You'll be asked to verify bot admin status
        """
        
        keyboard = [
            [InlineKeyboardButton("❌ Cancel", callback_data="fj_menu")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(text, reply_markup=reply_markup, parse_mode='Markdown')
        context.user_data['fj_step'] = 1
        return AWAIT_CHANNEL_ID
    
    async def get_channel_id(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Get channel ID from user"""
        try:
            channel_id = int(update.message.text.strip())
        except ValueError:
            await update.message.reply_text(
                "❌ Invalid channel ID!\n\n"
                "Channel ID must be a number (like -1001234567890)\n\n"
                "Try again:"
            )
            return AWAIT_CHANNEL_ID
        
        # Validate channel ID format
        if not str(channel_id).startswith('-100'):
            await update.message.reply_text(
                "⚠️ Channel ID seems incorrect.\n\n"
                "Valid channel ID should start with -100 (like -1001234567890)\n\n"
                "Try again:"
            )
            return AWAIT_CHANNEL_ID
        
        # Check if already added
        existing = self.db.get_force_join_channel(channel_id)
        if existing:
            await update.message.reply_text(
                "✅ This channel is already in force join list!\n\n"
                "Use 'Remove Channel' if you want to remove it."
            )
            return ConversationHandler.END
        
        context.user_data['fj_channel_id'] = channel_id
        
        text = """📝 Step 2/3: Send Channel Username
═══════════════════════════════════════════════════════════════

💡 Channel username format:
- Without @: coursepro911
- Or with @: @coursepro911
- Both formats work!

⚠️ Important:
- Must be a PUBLIC channel
- Anyone must be able to join by username
- Private channels don't work

Send channel username:
        """
        
        keyboard = [
            [InlineKeyboardButton("❌ Cancel", callback_data="fj_menu")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(text, reply_markup=reply_markup, parse_mode='Markdown')
        return AWAIT_CHANNEL_USERNAME
    
    async def get_channel_username(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Get channel username from user"""
        username = update.message.text.strip().replace('@', '').lower()
        
        # Validate username
        if not username or len(username) < 3:
            await update.message.reply_text(
                "❌ Invalid username!\n\n"
                "Channel username must be at least 3 characters.\n\n"
                "Try again:"
            )
            return AWAIT_CHANNEL_USERNAME
        
        context.user_data['fj_username'] = username
        
        text = """📝 Step 3/3: Send Channel Title
═══════════════════════════════════════════════════════════════

💡 Examples:
- "Cybersecurity Mastery Course"
- "Course Updates & Announcements"
- "Premium Content Channel"

Send a short, descriptive title for this channel:
        """
        
        keyboard = [
            [InlineKeyboardButton("❌ Cancel", callback_data="fj_menu")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(text, reply_markup=reply_markup, parse_mode='Markdown')
        return AWAIT_CHANNEL_TITLE
    
    async def get_channel_title(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Get channel title and show confirmation"""
        title = update.message.text.strip()
        
        if not title or len(title) < 3:
            await update.message.reply_text(
                "❌ Title too short!\n\n"
                "Please provide a descriptive title (at least 3 characters).\n\n"
                "Try again:"
            )
            return AWAIT_CHANNEL_TITLE
        
        if len(title) > 100:
            await update.message.reply_text(
                "❌ Title too long!\n\n"
                "Please keep it under 100 characters.\n\n"
                "Try again:"
            )
            return AWAIT_CHANNEL_TITLE
        
        context.user_data['fj_title'] = title
        
        # Show confirmation
        channel_id = context.user_data['fj_channel_id']
        username = context.user_data['fj_username']
        
        text = f"""✅ VERIFY CHANNEL DETAILS
═══════════════════════════════════════════════════════════════

📋 Channel Information:

🆔 Channel ID: `{channel_id}`
👤 Username: `@{username}`
📌 Title: `{title}`

──────────────────────────────────────────────────────────────

⚠️ IMPORTANT - Bot Admin Requirements:

Before confirming, make sure:
✅ Bot is admin in the channel
✅ Bot has permission to delete messages
✅ Channel is PUBLIC (not private)
✅ Username is correct

──────────────────────────────────────────────────────────────
        """
        
        keyboard = [
            [InlineKeyboardButton("✅ Confirm & Add", callback_data="fj_confirm_add")],
            [InlineKeyboardButton("❌ Cancel", callback_data="fj_menu")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(text, reply_markup=reply_markup, parse_mode='Markdown')
        return AWAIT_CONFIRM_ADD
    
    async def confirm_add_channel(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Confirm and add the force join channel to database"""
        query = update.callback_query
        await query.answer()
        
        channel_id = context.user_data.get('fj_channel_id')
        username = context.user_data.get('fj_username')
        title = context.user_data.get('fj_title')
        
        if not all([channel_id, username, title]):
            await query.edit_message_text(
                "❌ Error: Missing data. Please start again.\n\n"
                "Click 'Force Join Manager' to retry."
            )
            return ConversationHandler.END
        
        try:
            # Add to database
            self.db.add_force_join_channel(channel_id, username, title)
            
            text = f"""✅ CHANNEL ADDED SUCCESSFULLY!
═══════════════════════════════════════════════════════════════

🎉 Force join channel added to the system!

📋 Details:
🆔 Channel ID: `{channel_id}`
👤 Username: `@{username}`
📌 Title: `{title}`

──────────────────────────────────────────────────────────────

✅ What happens now:

1. 🔄 All users will see "Join Required" message
2. 👥 They'll need to join @{username} to use the bot
3. ✅ Bot will auto-verify membership
4. 📊 You can remove it anytime from admin panel

──────────────────────────────────────────────────────────────
            """
            
            keyboard = [
                [InlineKeyboardButton("🚪 Back to Manager", callback_data="fj_menu")],
                [InlineKeyboardButton("🔙 Back to Admin", callback_data="admin_dashboard")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await query.edit_message_text(text, reply_markup=reply_markup, parse_mode='Markdown')
            
            # Clear temporary data
            context.user_data.pop('fj_channel_id', None)
            context.user_data.pop('fj_username', None)
            context.user_data.pop('fj_title', None)
            
            return ConversationHandler.END
            
        except Exception as e:
            logger.error(f"Error adding force join channel: {e}")
            await query.edit_message_text(
                f"❌ Error adding channel: {str(e)}\n\n"
                "Please try again or contact support."
            )
            return ConversationHandler.END
    
    async def remove_channel_start(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Start removing a force join channel"""
        query = update.callback_query
        await query.answer()
        
        # Get current force join channels
        channels = self.db.get_force_join_channels()
        
        if not channels:
            await query.edit_message_text(
                "📭 No force join channels to remove!\n\n"
                "Use 'Add Channel' to add one first.",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("🔙 Back", callback_data="fj_menu")]
                ])
            )
            return ConversationHandler.END
        
        text = """❌ REMOVE FORCE JOIN CHANNEL
═══════════════════════════════════════════════════════════════

👇 Select a channel to remove:

        """
        
        keyboard = []
        for ch in channels:
            keyboard.append([
                InlineKeyboardButton(
                    f"❌ @{ch['username']} ({ch['title']})",
                    callback_data=f"fj_delete_{ch['channel_id']}"
                )
            ])
        
        keyboard.append([InlineKeyboardButton("🔙 Cancel", callback_data="fj_menu")])
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(text, reply_markup=reply_markup, parse_mode='Markdown')
        return AWAIT_DELETE_CHANNEL
    
    async def delete_channel(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Delete a force join channel"""
        query = update.callback_query
        
        # Extract channel ID from callback data
        channel_id = int(query.data.split('_')[2])
        
        await query.answer()
        
        try:
            channel = self.db.get_force_join_channel(channel_id)
            
            if not channel:
                await query.edit_message_text(
                    "❌ Channel not found!\n\n"
                    "It may have been already removed."
                )
                return ConversationHandler.END
            
            # Delete from database
            self.db.remove_force_join_channel(channel_id)
            
            text = f"""✅ CHANNEL REMOVED!
═══════════════════════════════════════════════════════════════

✅ Force join channel has been removed!

📋 Removed Channel:
👤 @{channel['username']}
📌 {channel['title']}

──────────────────────────────────────────────────────────────

✅ What happens now:

1. Users will no longer see "Join Required" message
2. They can use the bot normally
3. No verification needed anymore

──────────────────────────────────────────────────────────────
            """
            
            keyboard = [
                [InlineKeyboardButton("🚪 Back to Manager", callback_data="fj_menu")],
                [InlineKeyboardButton("🔙 Back to Admin", callback_data="admin_dashboard")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await query.edit_message_text(text, reply_markup=reply_markup, parse_mode='Markdown')
            return ConversationHandler.END
            
        except Exception as e:
            logger.error(f"Error removing force join channel: {e}")
            await query.edit_message_text(
                f"❌ Error removing channel: {str(e)}\n\n"
                "Please try again or contact support."
            )
            return ConversationHandler.END
    
    async def refresh_menu(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Refresh the force join channels list"""
        return await self.show_menu(update, context)
    
    async def cancel(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Cancel operation"""
        if update.callback_query:
            query = update.callback_query
            await query.answer()
        
        return ConversationHandler.END
