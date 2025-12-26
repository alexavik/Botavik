# 👑 Premium Admin Dashboard Handler

import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler
from database.db import db
from services.ai_service import ai_service
from config import BotConfig, AIConfig

logger = logging.getLogger(__name__)

# Conversation states
BROADCAST_MESSAGE = 1
ADD_ADMIN_ID = 2
ADD_CHANNEL_ID = 3
CREDIT_AMOUNT = 4
AI_PROMPT = 5
CONTENT_KEY = 6
CONTENT_VALUE = 7


class AdminDashboard:
    """Premium Admin Dashboard Handler"""
    
    @staticmethod
    async def main_dashboard(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """
        Main admin dashboard with statistics and control panels
        """
        user = update.effective_user
        query = update.callback_query
        
        # Check if admin
        is_admin = await db.is_admin(user.id)
        if not is_admin:
            if query:
                await query.answer("❌ You are not an admin!", show_alert=True)
            else:
                await update.message.reply_text("❌ Access denied: Admin only")
            return
        
        # Get statistics
        try:
            stats = await db.get_bot_stats()
            broadcast_stats = await db.get_broadcast_stats()
            
            text = f"""
👑 **PREMIUM ADMIN DASHBOARD**
═══════════════════════════════════════════════════════════════

📊 **Quick Statistics:**
• 👥 Total Users: **{stats['total_users']}**
• 📋 Active Today: **{stats['active_today']}**
• 🎉 New This Week: **{stats['new_users_week']}**
• 💰 Total Revenue: **₹{stats['total_revenue']}**

📢 **Broadcast Info:**
• Total Users: **{broadcast_stats['total_users']}**
• Active Users: **{broadcast_stats['active_users']}**
• Last Broadcast: **{broadcast_stats['last_broadcast']}**
• Success Rate: **{broadcast_stats['success_rate']}%**

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

**📍 Control Panels Below:**
            """
            
            # Build keyboard
            keyboard = [
                [
                    InlineKeyboardButton("🤖 AI Assistant", callback_data="admin_ai"),
                    InlineKeyboardButton("📢 Broadcast", callback_data="admin_broadcast")
                ],
                [
                    InlineKeyboardButton("🚪 Force Join", callback_data="admin_force_join"),
                    InlineKeyboardButton("👥 Users", callback_data="admin_users")
                ],
                [
                    InlineKeyboardButton("💳 Credits", callback_data="admin_credits"),
                    InlineKeyboardButton("👨‍💼 Admins", callback_data="admin_manage_admins")
                ],
                [
                    InlineKeyboardButton("⚙️ Content", callback_data="admin_content"),
                    InlineKeyboardButton("📊 Analytics", callback_data="admin_analytics")
                ],
                [
                    InlineKeyboardButton("🚨 Alerts", callback_data="admin_alerts"),
                    InlineKeyboardButton("🎯 Settings", callback_data="admin_settings")
                ],
                [
                    InlineKeyboardButton("📚 Docs", callback_data="admin_docs"),
                    InlineKeyboardButton("📝 Logs", callback_data="admin_logs")
                ]
            ]
            
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
        
        except Exception as e:
            logger.error(f"❌ Error in main dashboard: {e}")
            error_text = f"😨 **Error Loading Dashboard**\n\n`{str(e)[:200]}`"
            if query:
                await query.answer(❌ An error occurred", show_alert=True)
            else:
                await update.message.reply_text(error_text, parse_mode='Markdown')


async def broadcast_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Broadcast management menu
    """
    query = update.callback_query
    
    text = f"""
📢 **BROADCAST SYSTEM**
═══════════════════════════════════════════════════════════════

📚 **Options:**
• Send Now - Broadcast to all users
• Schedule - Plan for later
• History - View past broadcasts
• Stats - Broadcast performance
• Templates - Ready-made messages
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    """
    
    keyboard = [
        [InlineKeyboardButton("📤 Send Now", callback_data="broadcast_create")],
        [InlineKeyboardButton("⏰ Schedule", callback_data="broadcast_schedule")],
        [InlineKeyboardButton("📄 History", callback_data="broadcast_history")],
        [InlineKeyboardButton("📊 Stats", callback_data="broadcast_stats")],
        [InlineKeyboardButton("📌 Templates", callback_data="broadcast_templates")],
        [InlineKeyboardButton("🔙 Back", callback_data="admin_dashboard")]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(text, reply_markup=reply_markup, parse_mode='Markdown')


async def broadcast_create(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Start broadcast creation
    """
    query = update.callback_query
    
    text = """
📤 **CREATE BROADCAST**
═══════════════════════════════════════════════════════════════

Type your message below:

**Supported:**
✓ Text with Markdown
✓ Emojis and formatting
✓ Links and buttons

**Markdown:**
- **Bold**: **text**
- *Italic*: *text*
- `Code`: `text`
- [Link](https://example.com)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    """
    
    await query.edit_message_text(text, parse_mode='Markdown')
    return BROADCAST_MESSAGE


async def broadcast_received(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Broadcast message received - show preview
    """
    message_text = update.message.text or "(Media message)"
    
    # Store in context
    context.user_data['broadcast_message'] = message_text
    
    text = f"""
🔍 **BROADCAST PREVIEW**
═══════════════════════════════════════════════════════════════

**Your Message:**
{message_text}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
💙 Send to {await db.get_total_users()} users?
    """
    
    keyboard = [
        [InlineKeyboardButton("✅ Yes, Send Now", callback_data="broadcast_send")],
        [InlineKeyboardButton("✍️ Edit", callback_data="broadcast_create")],
        [InlineKeyboardButton("❌ Cancel", callback_data="admin_broadcast")]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(text, reply_markup=reply_markup, parse_mode='Markdown')
    
    return ConversationHandler.END


async def broadcast_send(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Send broadcast to all users
    """
    query = update.callback_query
    message_text = context.user_data.get('broadcast_message')
    user = update.effective_user
    
    if not message_text:
        await query.answer("❌ No message to send", show_alert=True)
        return
    
    # Get all users
    users = await db.get_all_users()
    total_users = len(users)
    
    # Start broadcast
    await query.answer("📣 Starting broadcast...")
    
    status_msg = await query.edit_message_text(
        f"📢 **BROADCASTING**\n\nSending to {total_users} users...\n\n0/{total_users} sent",
        parse_mode='Markdown'
    )
    
    success_count = 0
    failed_count = 0
    
    # Send to each user
    for idx, user_data in enumerate(users):
        try:
            await context.bot.send_message(
                chat_id=user_data['user_id'],
                text=message_text,
                parse_mode='Markdown'
            )
            success_count += 1
        except Exception as e:
            logger.warning(f"❌ Failed to send to {user_data['user_id']}: {e}")
            failed_count += 1
        
        # Update status every 10 messages
        if (idx + 1) % 10 == 0:
            try:
                await status_msg.edit_text(
                    f"📢 **BROADCASTING**\n\nSending to {total_users} users...\n\n{idx + 1}/{total_users} sent",
                    parse_mode='Markdown'
                )
            except:
                pass
    
    # Log broadcast
    await db.log_broadcast({
        'message': message_text[:100],
        'total': total_users,
        'success': success_count,
        'failed': failed_count,
        'blocked': 0,
        'sent_by': user.id
    })
    
    # Final result
    result_text = f"""
✅ **BROADCAST COMPLETE**
═══════════════════════════════════════════════════════════════

📊 **Results:**
• Total Users: {total_users}
• Successfully Sent: {success_count} (✅ {int((success_count/total_users)*100)}%)
• Failed: {failed_count}
• Blocked Bot: 0
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📅 Sent by: @{update.effective_user.username or 'Unknown'}
    """
    
    keyboard = [[InlineKeyboardButton("🔙 Back", callback_data="admin_broadcast")]]
    await status_msg.edit_text(result_text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='Markdown')


async def users_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    User management menu
    """
    query = update.callback_query
    
    try:
        total = await db.get_total_users()
        stats = await db.get_user_stats()
        
        text = f"""
👥 **USER MANAGEMENT**
═══════════════════════════════════════════════════════════════

📊 **Statistics:**
• Total Users: {stats['total']}
• Active (24h): {stats['active_24h']}
• Premium: {stats['premium']}
• Banned: {stats['banned']}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        """
        
        keyboard = [
            [InlineKeyboardButton("📚 View All", callback_data="users_list")],
            [InlineKeyboardButton("🚫 Ban User", callback_data="user_ban")],
            [InlineKeyboardButton("🔙 Back", callback_data="admin_dashboard")]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(text, reply_markup=reply_markup, parse_mode='Markdown')
    
    except Exception as e:
        logger.error(f"❌ Error in users_menu: {e}")
        await query.answer(f"❌ Error: {str(e)[:50]}", show_alert=True)


async def credits_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Credit management menu
    """
    query = update.callback_query
    
    text = """
💳 **CREDIT MANAGEMENT**
═══════════════════════════════════════════════════════════════

**Options:**
• Add Credits
• Deduct Credits
• Bulk Distribute
• History
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    """
    
    keyboard = [
        [InlineKeyboardButton("➕ Add Credits", callback_data="credits_add")],
        [InlineKeyboardButton("➖ Deduct Credits", callback_data="credits_deduct")],
        [InlineKeyboardButton("🎁 Bulk Distribute", callback_data="credits_bulk")],
        [InlineKeyboardButton("📚 History", callback_data="credits_history")],
        [InlineKeyboardButton("🔙 Back", callback_data="admin_dashboard")]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(text, reply_markup=reply_markup, parse_mode='Markdown')


async def force_join_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Force join channel management
    """
    query = update.callback_query
    
    try:
        channels = await db.get_force_join_channels()
        channel_list = ""
        
        for i, ch in enumerate(channels, 1):
            channel_list += f"{i}. @{ch['username']} - {ch['title']}\n"
        
        if not channel_list:
            channel_list = "No channels configured yet"
        
        text = f"""
🚪 **FORCE JOIN MANAGEMENT**
═══════════════════════════════════════════════════════════════

**Active Channels/Groups:**
{channel_list}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        """
        
        keyboard = [
            [InlineKeyboardButton("➕ Add Channel", callback_data="fj_add_channel")],
            [InlineKeyboardButton("➕ Add Group", callback_data="fj_add_group")],
            [InlineKeyboardButton("❌ Remove Channel", callback_data="fj_remove")],
            [InlineKeyboardButton("🔙 Back", callback_data="admin_dashboard")]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(text, reply_markup=reply_markup, parse_mode='Markdown')
    
    except Exception as e:
        logger.error(f"❌ Error in force_join_menu: {e}")
        await query.answer(f"❌ Error: {str(e)[:50]}", show_alert=True)


async def manage_admins_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Admin management menu
    """
    query = update.callback_query
    
    try:
        admins = await db.get_all_admins()
        admin_list = ""
        
        for i, admin in enumerate(admins, 1):
            admin_list += f"{i}. {admin['name']} (ID: {admin['user_id']}) - {admin['role']}\n"
        
        if not admin_list:
            admin_list = "No admins yet"
        
        text = f"""
👨‍💼 **ADMIN MANAGEMENT**
═══════════════════════════════════════════════════════════════

**Current Admins:**
{admin_list}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        """
        
        keyboard = [
            [InlineKeyboardButton("➕ Add Admin", callback_data="admin_add")],
            [InlineKeyboardButton("❌ Remove Admin", callback_data="admin_remove")],
            [InlineKeyboardButton("🔙 Back", callback_data="admin_dashboard")]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(text, reply_markup=reply_markup, parse_mode='Markdown')
    
    except Exception as e:
        logger.error(f"❌ Error in manage_admins_menu: {e}")
        await query.answer(f"❌ Error: {str(e)[:50]}", show_alert=True)


async def content_editor_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Content customization menu
    """
    query = update.callback_query
    
    text = """
⚙️ **CONTENT EDITOR**
═══════════════════════════════════════════════════════════════

**Edit Bot Messages:**
• Welcome Message
• Help Text
• Button Labels
• Pricing Information
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    """
    
    keyboard = [
        [InlineKeyboardButton("📚 View All", callback_data="content_list")],
        [InlineKeyboardButton("✍️ Edit Content", callback_data="content_edit")],
        [InlineKeyboardButton("🔙 Back", callback_data="admin_dashboard")]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(text, reply_markup=reply_markup, parse_mode='Markdown')


async def ai_assistant_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    AI Assistant menu with Gemini 2.0 Flash integration
    """
    query = update.callback_query
    
    # Check if AI is configured
    ai_status = "✅ Connected" if await ai_service.test_connection() else "❌ Not configured"
    
    text = f"""
🤖 **AI ASSISTANT** (Gemini 2.0 Flash)
═══════════════════════════════════════════════════════════════

🔌 **Status:** {ai_status}

**Generation Tools:**
• Course Descriptions
• Promotional Messages
• Broadcast Content
• FAQ Generator
• Email Templates
• Course Ideas
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    """
    
    keyboard = [
        [InlineKeyboardButton("📚 Course Description", callback_data="ai_course_desc")],
        [InlineKeyboardButton("📣 Promo Message", callback_data="ai_promo")],
        [InlineKeyboardButton("📢 Broadcast Content", callback_data="ai_broadcast")],
        [InlineKeyboardButton("📌 FAQ Generator", callback_data="ai_faq")],
        [InlineKeyboardButton("📧 Email Template", callback_data="ai_email")],
        [InlineKeyboardButton("💪 Course Ideas", callback_data="ai_ideas")],
        [InlineKeyboardButton("🔙 Back", callback_data="admin_dashboard")]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    try:
        await query.edit_message_text(text, reply_markup=reply_markup, parse_mode='Markdown')
    except Exception as e:
        logger.error(f"❌ Error in AI menu: {e}")
        await query.answer(f"❌ Error: {str(e)[:50]}", show_alert=True)
