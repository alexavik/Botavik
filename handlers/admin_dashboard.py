# Professional Premium Admin Dashboard
# Complete admin control panel with advanced features

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler
from telegram.constants import ParseMode
from database.db import db
import logging
from datetime import datetime
from config import BotConfig

logger = logging.getLogger(__name__)

# Conversation states
BROADCAST_MESSAGE = 1
ADD_ADMIN = 2
ADD_FORCE_JOIN = 3
EDIT_WELCOME = 4
MANAGE_CREDITS = 5
AI_PROMPT = 6

class AdminDashboard:
    """Premium Admin Dashboard Controller"""
    
    @staticmethod
    async def check_admin(user_id: int) -> bool:
        """Check if user is admin"""
        try:
            admin = await db.get_admin(user_id)
            return admin is not None
        except Exception as e:
            logger.error(f"Error checking admin: {e}")
            return False
    
    @staticmethod
    async def main_dashboard(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Show main admin dashboard"""
        query = update.callback_query
        user_id = query.from_user.id if query else update.effective_user.id
        
        # Check admin access
        if not await AdminDashboard.check_admin(user_id):
            text = "⛔ **ACCESS DENIED**\n\nYou don't have admin privileges."
            if query:
                await query.answer("Access Denied!", show_alert=True)
                await query.edit_message_text(text, parse_mode='Markdown')
            else:
                await update.message.reply_text(text, parse_mode='Markdown')
            return
        
        # Get stats
        stats = await db.get_bot_stats()
        
        text = f"""
👑 **ADMIN DASHBOARD**
═════════════════════════════════════════════════════

📊 **Bot Statistics:**
   • Total Users: {stats.get('total_users', 0)}
   • Active Today: {stats.get('active_today', 0)}
   • New Users (7d): {stats.get('new_users_week', 0)}
   • Total Courses: {stats.get('total_courses', 0)}
   • Total Revenue: ₹{stats.get('total_revenue', 0)}
   • Pending Orders: {stats.get('pending_orders', 0)}

🕒 **Last Updated:** {datetime.now().strftime('%d/%m/%Y %H:%M')}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Select an option below to manage:
        """
        
        keyboard = [
            [
                InlineKeyboardButton("📢 Broadcast", callback_data="admin_broadcast"),
                InlineKeyboardButton("👥 Users", callback_data="admin_users")
            ],
            [
                InlineKeyboardButton("📚 Courses", callback_data="admin_courses"),
                InlineKeyboardButton("💰 Credits", callback_data="admin_credits")
            ],
            [
                InlineKeyboardButton("🔒 Force Join", callback_data="admin_force_join"),
                InlineKeyboardButton("👑 Admins", callback_data="admin_manage_admins")
            ],
            [
                InlineKeyboardButton("✏️ Content Editor", callback_data="admin_content"),
                InlineKeyboardButton("🤖 AI Assistant", callback_data="admin_ai")
            ],
            [
                InlineKeyboardButton("📊 Analytics", callback_data="admin_analytics"),
                InlineKeyboardButton("⚙️ Settings", callback_data="admin_settings")
            ],
            [
                InlineKeyboardButton("📦 Orders", callback_data="admin_orders"),
                InlineKeyboardButton("🎨 Customize", callback_data="admin_customize")
            ],
            [
                InlineKeyboardButton("🔄 Refresh Stats", callback_data="admin_dashboard")
            ]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        if query:
            await query.answer()
            await query.edit_message_text(text, reply_markup=reply_markup, parse_mode='Markdown')
        else:
            await update.message.reply_text(text, reply_markup=reply_markup, parse_mode='Markdown')

# ==================== BROADCAST SYSTEM ====================

async def broadcast_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show broadcast menu"""
    query = update.callback_query
    await query.answer()
    
    text = """
📢 **BROADCAST SYSTEM**
═════════════════════════════════════════════════════

Send messages to all bot users instantly!

**Features:**
   ✅ Rich text formatting (Bold, Italic, Code)
   ✅ Media support (Photos, Videos, Files)
   ✅ Button attachments
   ✅ Preview before sending
   ✅ Send to specific groups
   ✅ Schedule broadcasts

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

**Target Options:**
   • All Users
   • Active Users (7 days)
   • Premium Users Only
   • Free Users Only
   • Custom List

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    """
    
    keyboard = [
        [
            InlineKeyboardButton("📝 Create Broadcast", callback_data="broadcast_create"),
            InlineKeyboardButton("📜 History", callback_data="broadcast_history")
        ],
        [
            InlineKeyboardButton("📊 Statistics", callback_data="broadcast_stats"),
            InlineKeyboardButton("⏰ Scheduled", callback_data="broadcast_scheduled")
        ],
        [
            InlineKeyboardButton("🔙 Back to Dashboard", callback_data="admin_dashboard")
        ]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(text, reply_markup=reply_markup, parse_mode='Markdown')

async def broadcast_create(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Start broadcast creation"""
    query = update.callback_query
    await query.answer()
    
    text = """
📝 **CREATE BROADCAST**
═════════════════════════════════════════════════════

Please send your broadcast message now.

**Formatting Tips:**
   • `*bold*` for **bold text**
   • `_italic_` for _italic text_
   • `` `code` `` for `monospace`
   • `[link text](URL)` for hyperlinks

**You can also send:**
   • Photos with captions
   • Videos with captions
   • Documents

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Type your message or /cancel to abort:
    """
    
    await query.edit_message_text(text, parse_mode='Markdown')
    return BROADCAST_MESSAGE

async def broadcast_received(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Receive broadcast message and show preview"""
    message = update.message
    
    # Store message details in context
    context.user_data['broadcast_message'] = message.text or message.caption
    context.user_data['broadcast_media'] = None
    
    if message.photo:
        context.user_data['broadcast_media'] = ('photo', message.photo[-1].file_id)
    elif message.video:
        context.user_data['broadcast_media'] = ('video', message.video.file_id)
    elif message.document:
        context.user_data['broadcast_media'] = ('document', message.document.file_id)
    
    # Show preview
    text = f"""
👁️ **BROADCAST PREVIEW**
═════════════════════════════════════════════════════

**Your Message:**
{context.user_data['broadcast_message']}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

**Target Audience:** All Users
**Estimated Reach:** {await db.get_total_users()} users

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Confirm to send broadcast?
    """
    
    keyboard = [
        [
            InlineKeyboardButton("✅ Send Now", callback_data="broadcast_send"),
            InlineKeyboardButton("🎯 Choose Target", callback_data="broadcast_target")
        ],
        [
            InlineKeyboardButton("⏰ Schedule", callback_data="broadcast_schedule"),
            InlineKeyboardButton("❌ Cancel", callback_data="broadcast_cancel")
        ]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    await message.reply_text(text, reply_markup=reply_markup, parse_mode='Markdown')
    
    return ConversationHandler.END

async def broadcast_send(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send broadcast to all users"""
    query = update.callback_query
    await query.answer("Starting broadcast...")
    
    message_text = context.user_data.get('broadcast_message')
    media = context.user_data.get('broadcast_media')
    
    # Get all users
    users = await db.get_all_users()
    
    success_count = 0
    failed_count = 0
    
    await query.edit_message_text(
        f"📤 **Broadcasting...**\n\nSending to {len(users)} users...",
        parse_mode='Markdown'
    )
    
    for user in users:
        try:
            if media:
                media_type, file_id = media
                if media_type == 'photo':
                    await context.bot.send_photo(
                        chat_id=user['user_id'],
                        photo=file_id,
                        caption=message_text,
                        parse_mode='Markdown'
                    )
                elif media_type == 'video':
                    await context.bot.send_video(
                        chat_id=user['user_id'],
                        video=file_id,
                        caption=message_text,
                        parse_mode='Markdown'
                    )
                elif media_type == 'document':
                    await context.bot.send_document(
                        chat_id=user['user_id'],
                        document=file_id,
                        caption=message_text,
                        parse_mode='Markdown'
                    )
            else:
                await context.bot.send_message(
                    chat_id=user['user_id'],
                    text=message_text,
                    parse_mode='Markdown'
                )
            success_count += 1
        except Exception as e:
            failed_count += 1
            logger.error(f"Broadcast failed for user {user['user_id']}: {e}")
    
    # Save broadcast stats
    await db.save_broadcast_stats(message_text, success_count, failed_count)
    
    result_text = f"""
✅ **BROADCAST COMPLETED**
═════════════════════════════════════════════════════

📊 **Results:**
   • Successfully Sent: {success_count}
   • Failed: {failed_count}
   • Total Attempted: {len(users)}
   • Success Rate: {(success_count/len(users)*100):.1f}%

🕒 **Completed:** {datetime.now().strftime('%d/%m/%Y %H:%M')}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    """
    
    keyboard = [[InlineKeyboardButton("🔙 Back to Dashboard", callback_data="admin_dashboard")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(result_text, reply_markup=reply_markup, parse_mode='Markdown')

# ==================== USER MANAGEMENT ====================

async def users_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show users management menu"""
    query = update.callback_query
    await query.answer()
    
    stats = await db.get_user_stats()
    
    text = f"""
👥 **USER MANAGEMENT**
═════════════════════════════════════════════════════

📊 **Statistics:**
   • Total Users: {stats.get('total', 0)}
   • Active (24h): {stats.get('active_24h', 0)}
   • Premium Users: {stats.get('premium', 0)}
   • Banned Users: {stats.get('banned', 0)}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

**Actions Available:**
   • Search users by ID/username
   • Ban/Unban users
   • View user activity
   • Export user list
   • Manage user credits

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    """
    
    keyboard = [
        [
            InlineKeyboardButton("🔍 Search User", callback_data="user_search"),
            InlineKeyboardButton("📋 All Users", callback_data="user_list")
        ],
        [
            InlineKeyboardButton("🚫 Banned Users", callback_data="user_banned"),
            InlineKeyboardButton("⭐ Premium Users", callback_data="user_premium")
        ],
        [
            InlineKeyboardButton("📊 Activity Log", callback_data="user_activity"),
            InlineKeyboardButton("📥 Export Data", callback_data="user_export")
        ],
        [
            InlineKeyboardButton("🔙 Back to Dashboard", callback_data="admin_dashboard")
        ]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(text, reply_markup=reply_markup, parse_mode='Markdown')

# ==================== CREDITS MANAGEMENT ====================

async def credits_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show credits management menu"""
    query = update.callback_query
    await query.answer()
    
    text = """
💰 **CREDITS MANAGEMENT**
═════════════════════════════════════════════════════

Manage user credits and wallet balance.

**Features:**
   • Add credits to users
   • Deduct credits from users
   • View credit history
   • Set credit expiry
   • Bulk credit operations

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

**Quick Actions:**
    """
    
    keyboard = [
        [
            InlineKeyboardButton("➕ Add Credits", callback_data="credits_add"),
            InlineKeyboardButton("➖ Deduct Credits", callback_data="credits_deduct")
        ],
        [
            InlineKeyboardButton("📜 Credit History", callback_data="credits_history"),
            InlineKeyboardButton("📊 Statistics", callback_data="credits_stats")
        ],
        [
            InlineKeyboardButton("🎁 Bonus Credits", callback_data="credits_bonus"),
            InlineKeyboardButton("⏰ Expiry Settings", callback_data="credits_expiry")
        ],
        [
            InlineKeyboardButton("🔙 Back to Dashboard", callback_data="admin_dashboard")
        ]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(text, reply_markup=reply_markup, parse_mode='Markdown')

# ==================== FORCE JOIN MANAGEMENT ====================

async def force_join_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show force join management menu"""
    query = update.callback_query
    await query.answer()
    
    channels = await db.get_force_join_channels()
    
    channels_list = "\n".join([
        f"   • {ch['title']} (@{ch['username']})" 
        for ch in channels
    ]) if channels else "   No channels added yet"
    
    text = f"""
🔒 **FORCE JOIN MANAGEMENT**
═════════════════════════════════════════════════════

Force users to join specific channels/groups before using the bot.

**Current Force Join Channels:**
{channels_list}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

**Features:**
   ✅ Add unlimited channels/groups
   ✅ Automatic membership verification
   ✅ Custom join messages
   ✅ Redirect after joining
   ✅ Statistics tracking

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    """
    
    keyboard = [
        [
            InlineKeyboardButton("➕ Add Channel", callback_data="force_join_add"),
            InlineKeyboardButton("🗑️ Remove Channel", callback_data="force_join_remove")
        ],
        [
            InlineKeyboardButton("✏️ Edit Message", callback_data="force_join_edit_msg"),
            InlineKeyboardButton("📊 Statistics", callback_data="force_join_stats")
        ],
        [
            InlineKeyboardButton("🔙 Back to Dashboard", callback_data="admin_dashboard")
        ]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(text, reply_markup=reply_markup, parse_mode='Markdown')

# ==================== ADMIN MANAGEMENT ====================

async def manage_admins_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show admin management menu"""
    query = update.callback_query
    await query.answer()
    
    admins = await db.get_all_admins()
    
    admins_list = "\n".join([
        f"   • {admin['name']} (ID: {admin['user_id']}) - {admin['role']}"
        for admin in admins
    ])
    
    text = f"""
👑 **ADMIN MANAGEMENT**
═════════════════════════════════════════════════════

**Current Admins ({len(admins)}):**
{admins_list}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

**Admin Roles:**
   🔴 Super Admin - Full access
   🟡 Admin - Limited access
   🟢 Moderator - Basic access

**Permissions:**
   • Broadcast messages
   • Manage users
   • Manage content
   • View analytics
   • Manage courses

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    """
    
    keyboard = [
        [
            InlineKeyboardButton("➕ Add Admin", callback_data="admin_add"),
            InlineKeyboardButton("➖ Remove Admin", callback_data="admin_remove")
        ],
        [
            InlineKeyboardButton("✏️ Edit Permissions", callback_data="admin_edit_perms"),
            InlineKeyboardButton("📜 Activity Log", callback_data="admin_log")
        ],
        [
            InlineKeyboardButton("🔙 Back to Dashboard", callback_data="admin_dashboard")
        ]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(text, reply_markup=reply_markup, parse_mode='Markdown')

# ==================== CONTENT EDITOR ====================

async def content_editor_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show content editor menu"""
    query = update.callback_query
    await query.answer()
    
    text = """
✏️ **CONTENT EDITOR**
═════════════════════════════════════════════════════

Customize every text and button in your bot!

**Editable Content:**
   📝 Welcome Message
   📝 Help Text
   📝 Course Templates
   📝 Payment Messages
   📝 Success/Error Messages
   📝 Button Labels
   📝 Menu Texts

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

**Features:**
   ✅ Live preview
   ✅ Markdown support
   ✅ Emoji picker
   ✅ Template variables
   ✅ Multi-language support

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    """
    
    keyboard = [
        [
            InlineKeyboardButton("📝 Welcome Message", callback_data="edit_welcome"),
            InlineKeyboardButton("❓ Help Text", callback_data="edit_help")
        ],
        [
            InlineKeyboardButton("🎓 Course Template", callback_data="edit_course"),
            InlineKeyboardButton("💳 Payment Messages", callback_data="edit_payment")
        ],
        [
            InlineKeyboardButton("🔘 Button Labels", callback_data="edit_buttons"),
            InlineKeyboardButton("🌐 Language", callback_data="edit_language")
        ],
        [
            InlineKeyboardButton("👁️ Preview Changes", callback_data="content_preview"),
            InlineKeyboardButton("💾 Save All", callback_data="content_save")
        ],
        [
            InlineKeyboardButton("🔙 Back to Dashboard", callback_data="admin_dashboard")
        ]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(text, reply_markup=reply_markup, parse_mode='Markdown')

# ==================== AI ASSISTANT ====================

async def ai_assistant_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show AI assistant menu"""
    query = update.callback_query
    await query.answer()
    
    text = """
🤖 **AI ASSISTANT**
═════════════════════════════════════════════════════

Your intelligent admin helper powered by AI!

**What I Can Do:**
   ✨ Generate course descriptions
   ✨ Create marketing content
   ✨ Write broadcast messages
   ✨ Suggest pricing strategies
   ✨ Analyze user behavior
   ✨ Generate reports
   ✨ Content translation
   ✨ SEO optimization

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

**Quick Actions:**
    """
    
    keyboard = [
        [
            InlineKeyboardButton("✍️ Generate Content", callback_data="ai_generate"),
            InlineKeyboardButton("📊 Analyze Data", callback_data="ai_analyze")
        ],
        [
            InlineKeyboardButton("💡 Get Suggestions", callback_data="ai_suggest"),
            InlineKeyboardButton("🌍 Translate", callback_data="ai_translate")
        ],
        [
            InlineKeyboardButton("📈 Marketing Ideas", callback_data="ai_marketing"),
            InlineKeyboardButton("🎯 Optimize", callback_data="ai_optimize")
        ],
        [
            InlineKeyboardButton("💬 Ask AI", callback_data="ai_ask"),
            InlineKeyboardButton("📝 Custom Prompt", callback_data="ai_custom")
        ],
        [
            InlineKeyboardButton("🔙 Back to Dashboard", callback_data="admin_dashboard")
        ]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(text, reply_markup=reply_markup, parse_mode='Markdown')

# Export handler functions
__all__ = [
    'AdminDashboard',
    'broadcast_menu',
    'broadcast_create',
    'broadcast_received',
    'broadcast_send',
    'users_menu',
    'credits_menu',
    'force_join_menu',
    'manage_admins_menu',
    'content_editor_menu',
    'ai_assistant_menu'
]
