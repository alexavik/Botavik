# Premium Admin Dashboard
# Complete admin control panel with all bot management features

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler
import logging
from database.db import db
from config import BotConfig

logger = logging.getLogger(__name__)

# Conversation states
ADD_ADMIN, BROADCAST_MSG, EDIT_CONTENT, ADD_FORCE_JOIN, ADJUST_CREDITS = range(5)

# ==================== MAIN ADMIN DASHBOARD ====================

async def admin_dashboard(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Main premium admin dashboard"""
    user_id = update.effective_user.id
    
    # Check if user is admin
    is_admin = await db.is_admin(user_id)
    if not is_admin:
        await update.message.reply_text("❌ You don't have permission to access admin panel.")
        return
    
    # Get admin stats
    stats = await db.get_admin_stats()
    
    text = f"""
👑 **PREMIUM ADMIN DASHBOARD**
═════════════════════════════════════════════════════════════════

📊 **Quick Stats:**
👥 Total Users: {stats.get('total_users', 0)}
📚 Total Courses: {stats.get('total_courses', 0)}
💰 Total Revenue: ₹{stats.get('total_revenue', 0)}
📨 Pending Orders: {stats.get('pending_orders', 0)}
👤 Active Admins: {stats.get('active_admins', 0)}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🎯 Select Management Option:
    """
    
    keyboard = [
        [
            InlineKeyboardButton("📝 Content Manager", callback_data="admin_content"),
            InlineKeyboardButton("👥 User Manager", callback_data="admin_users")
        ],
        [
            InlineKeyboardButton("📢 Broadcast", callback_data="admin_broadcast"),
            InlineKeyboardButton("🔒 Force Join", callback_data="admin_forcejoin")
        ],
        [
            InlineKeyboardButton("👑 Admin Manager", callback_data="admin_admins"),
            InlineKeyboardButton("📊 Analytics", callback_data="admin_analytics")
        ],
        [
            InlineKeyboardButton("🤖 AI Assistant", callback_data="admin_ai"),
            InlineKeyboardButton("⚙️ Settings", callback_data="admin_settings")
        ],
        [
            InlineKeyboardButton("🔙 Close", callback_data="admin_close")
        ]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    if update.callback_query:
        await update.callback_query.edit_message_text(text, reply_markup=reply_markup, parse_mode='Markdown')
    else:
        await update.message.reply_text(text, reply_markup=reply_markup, parse_mode='Markdown')
    
    logger.info(f"✅ Admin {user_id} accessed dashboard")

# ==================== CONTENT MANAGER ====================

async def admin_content_manager(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Content management system"""
    query = update.callback_query
    await query.answer()
    
    text = """
📝 **CONTENT MANAGER**
═════════════════════════════════════════════════════════════════

Manage all bot content and messages:

• Edit welcome messages
• Customize button labels
• Update course descriptions
• Modify help text
• Change success/error messages
• Configure payment instructions

Select what you want to edit:
    """
    
    keyboard = [
        [
            InlineKeyboardButton("👋 Welcome Message", callback_data="edit_welcome"),
            InlineKeyboardButton("📚 Course Messages", callback_data="edit_courses")
        ],
        [
            InlineKeyboardButton("🔘 Button Labels", callback_data="edit_buttons"),
            InlineKeyboardButton("❓ Help Text", callback_data="edit_help")
        ],
        [
            InlineKeyboardButton("💰 Payment Messages", callback_data="edit_payment"),
            InlineKeyboardButton("🎉 Success Messages", callback_data="edit_success")
        ],
        [
            InlineKeyboardButton("🔙 Back to Dashboard", callback_data="admin_dashboard")
        ]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(text, reply_markup=reply_markup, parse_mode='Markdown')

# ==================== USER MANAGER ====================

async def admin_user_manager(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """User management system"""
    query = update.callback_query
    await query.answer()
    
    # Get user statistics
    user_stats = await db.get_user_statistics()
    
    text = f"""
👥 **USER MANAGER**
═════════════════════════════════════════════════════════════════

📊 **User Statistics:**
👥 Total Users: {user_stats.get('total', 0)}
✅ Active Users: {user_stats.get('active', 0)}
🚫 Banned Users: {user_stats.get('banned', 0)}
🆕 New Today: {user_stats.get('new_today', 0)}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Manage user accounts and permissions:
    """
    
    keyboard = [
        [
            InlineKeyboardButton("🔍 Search User", callback_data="search_user"),
            InlineKeyboardButton("💳 Adjust Credits", callback_data="adjust_credits")
        ],
        [
            InlineKeyboardButton("🚫 Ban User", callback_data="ban_user"),
            InlineKeyboardButton("✅ Unban User", callback_data="unban_user")
        ],
        [
            InlineKeyboardButton("📊 View All Users", callback_data="view_all_users"),
            InlineKeyboardButton("📧 Export Users", callback_data="export_users")
        ],
        [
            InlineKeyboardButton("🔙 Back to Dashboard", callback_data="admin_dashboard")
        ]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(text, reply_markup=reply_markup, parse_mode='Markdown')

# ==================== BROADCAST SYSTEM ====================

async def admin_broadcast_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Broadcast message system"""
    query = update.callback_query
    await query.answer()
    
    text = """
📢 **BROADCAST SYSTEM**
═════════════════════════════════════════════════════════════════

Send messages to all or specific users:

🎯 **Features:**
• Send to all users or specific groups
• Text, photo, video, document support
• Markdown formatting
• Button attachments
• Schedule broadcasts
• Progress tracking

📊 **Statistics:**
Last broadcast: Never
Total sent: 0 messages
Success rate: N/A

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Select broadcast type:
    """
    
    keyboard = [
        [
            InlineKeyboardButton("📢 Text Message", callback_data="broadcast_text"),
            InlineKeyboardButton("🖼️ Photo Message", callback_data="broadcast_photo")
        ],
        [
            InlineKeyboardButton("🎥 Video Message", callback_data="broadcast_video"),
            InlineKeyboardButton("📄 Document", callback_data="broadcast_doc")
        ],
        [
            InlineKeyboardButton("👥 Target Specific Users", callback_data="broadcast_target"),
            InlineKeyboardButton("📊 View History", callback_data="broadcast_history")
        ],
        [
            InlineKeyboardButton("🔙 Back to Dashboard", callback_data="admin_dashboard")
        ]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(text, reply_markup=reply_markup, parse_mode='Markdown')

async def start_broadcast_text(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Start text broadcast"""
    query = update.callback_query
    await query.answer()
    
    text = """
✏️ **CREATE TEXT BROADCAST**
═════════════════════════════════════════════════════════════════

Send your broadcast message below.

🎨 **Formatting Tips:**
\*bold\* - **bold text**
\_italic\_ - _italic text_
`code` - `code block`

Type your message or /cancel to abort:
    """
    
    await query.edit_message_text(text, parse_mode='Markdown')
    return BROADCAST_MSG

# ==================== FORCE JOIN MANAGER ====================

async def admin_forcejoin_manager(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Force join channels/groups manager"""
    query = update.callback_query
    await query.answer()
    
    # Get current force join channels
    force_joins = await db.get_force_join_channels()
    
    channels_text = "\n".join([
        f"{i+1}. {ch['title']} (@{ch['username']}) - {'✅ Active' if ch['active'] else '❌ Inactive'}"
        for i, ch in enumerate(force_joins)
    ]) if force_joins else "No channels configured"
    
    text = f"""
🔒 **FORCE JOIN MANAGER**
═════════════════════════════════════════════════════════════════

Force users to join channels before using bot.

📊 **Current Channels:**
{channels_text}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

⚠️ **How it works:**
1. Add channel/group username
2. Bot checks membership on /start
3. Users must join to continue
4. Automatic verification

Manage force join channels:
    """
    
    keyboard = [
        [
            InlineKeyboardButton("➕ Add Channel", callback_data="forcejoin_add"),
            InlineKeyboardButton("❌ Remove Channel", callback_data="forcejoin_remove")
        ],
        [
            InlineKeyboardButton("✅ Enable All", callback_data="forcejoin_enable"),
            InlineKeyboardButton("🚫 Disable All", callback_data="forcejoin_disable")
        ],
        [
            InlineKeyboardButton("📊 Test Check", callback_data="forcejoin_test"),
            InlineKeyboardButton("📝 Edit Message", callback_data="forcejoin_message")
        ],
        [
            InlineKeyboardButton("🔙 Back to Dashboard", callback_data="admin_dashboard")
        ]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(text, reply_markup=reply_markup, parse_mode='Markdown')

# ==================== ADMIN MANAGER ====================

async def admin_admins_manager(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Admin users management"""
    query = update.callback_query
    await query.answer()
    
    # Get all admins
    admins_list = await db.get_all_admins()
    
    admins_text = "\n".join([
        f"{i+1}. {admin['name']} (ID: {admin['user_id']}) - {admin['role']}"
        for i, admin in enumerate(admins_list)
    ]) if admins_list else "No admins found"
    
    text = f"""
👑 **ADMIN MANAGER**
═════════════════════════════════════════════════════════════════

Manage admin users and permissions.

👥 **Current Admins:**
{admins_text}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🎯 **Admin Roles:**
• **Super Admin** - Full access
• **Admin** - Most features
• **Moderator** - Limited access

Manage administrators:
    """
    
    keyboard = [
        [
            InlineKeyboardButton("➕ Add Admin", callback_data="add_admin"),
            InlineKeyboardButton("❌ Remove Admin", callback_data="remove_admin")
        ],
        [
            InlineKeyboardButton("📝 Edit Permissions", callback_data="edit_permissions"),
            InlineKeyboardButton("📊 View Logs", callback_data="view_admin_logs")
        ],
        [
            InlineKeyboardButton("🔙 Back to Dashboard", callback_data="admin_dashboard")
        ]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(text, reply_markup=reply_markup, parse_mode='Markdown')

# ==================== AI ASSISTANT ====================

async def admin_ai_assistant(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """AI assistant for admins"""
    query = update.callback_query
    await query.answer()
    
    text = """
🤖 **AI ASSISTANT**
═════════════════════════════════════════════════════════════════

AI-powered content generation and assistance.

🎨 **AI Can Help You:**
• Generate course descriptions
• Write marketing messages
• Create broadcast content
• Improve existing text
• Translate messages
• Generate FAQs
• Write testimonials
• Create promotional content

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Choose AI task:
    """
    
    keyboard = [
        [
            InlineKeyboardButton("📚 Generate Course", callback_data="ai_course"),
            InlineKeyboardButton("📢 Create Broadcast", callback_data="ai_broadcast")
        ],
        [
            InlineKeyboardButton("✏️ Improve Text", callback_data="ai_improve"),
            InlineKeyboardButton("🌐 Translate", callback_data="ai_translate")
        ],
        [
            InlineKeyboardButton("💡 Generate Ideas", callback_data="ai_ideas"),
            InlineKeyboardButton("❓ Create FAQ", callback_data="ai_faq")
        ],
        [
            InlineKeyboardButton("🔙 Back to Dashboard", callback_data="admin_dashboard")
        ]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(text, reply_markup=reply_markup, parse_mode='Markdown')

# ==================== ANALYTICS ====================

async def admin_analytics(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Advanced analytics dashboard"""
    query = update.callback_query
    await query.answer()
    
    # Get analytics data
    analytics = await db.get_analytics_data()
    
    text = f"""
📊 **ANALYTICS DASHBOARD**
═════════════════════════════════════════════════════════════════

👥 **User Metrics:**
Total Users: {analytics.get('total_users', 0)}
Active Today: {analytics.get('active_today', 0)}
New This Week: {analytics.get('new_week', 0)}
Growth Rate: {analytics.get('growth_rate', 0)}%

📚 **Course Metrics:**
Total Courses: {analytics.get('total_courses', 0)}
Total Sales: {analytics.get('total_sales', 0)}
Revenue: ₹{analytics.get('revenue', 0)}
Avg Price: ₹{analytics.get('avg_price', 0)}

📢 **Engagement:**
Messages Sent: {analytics.get('messages', 0)}
Broadcasts: {analytics.get('broadcasts', 0)}
Button Clicks: {analytics.get('clicks', 0)}
Conversion: {analytics.get('conversion', 0)}%

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

View detailed reports:
    """
    
    keyboard = [
        [
            InlineKeyboardButton("📈 User Growth", callback_data="analytics_users"),
            InlineKeyboardButton("💰 Revenue Report", callback_data="analytics_revenue")
        ],
        [
            InlineKeyboardButton("📚 Course Performance", callback_data="analytics_courses"),
            InlineKeyboardButton("📢 Engagement Stats", callback_data="analytics_engagement")
        ],
        [
            InlineKeyboardButton("📊 Export Data", callback_data="analytics_export"),
            InlineKeyboardButton("📝 Custom Report", callback_data="analytics_custom")
        ],
        [
            InlineKeyboardButton("🔙 Back to Dashboard", callback_data="admin_dashboard")
        ]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(text, reply_markup=reply_markup, parse_mode='Markdown')

# ==================== CLOSE ADMIN PANEL ====================

async def close_admin_panel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Close admin panel"""
    query = update.callback_query
    await query.answer()
    
    await query.edit_message_text(
        "✅ Admin panel closed. Use /admin to reopen.",
        parse_mode='Markdown'
    )
    
    logger.info(f"✅ Admin panel closed by {query.from_user.id}")
