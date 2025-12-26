# Premium Admin Dashboard for Course Pro Bot
# Professional admin control panel with AI assistance

import logging
import asyncio
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler
from database.db import db

logger = logging.getLogger(__name__)

# Conversation states
(BROADCAST_MESSAGE, ADD_ADMIN, REMOVE_ADMIN, ADD_CHANNEL, REMOVE_CHANNEL,
 SET_CREDITS, ADD_CREDITS, REMOVE_CREDITS, AI_PROMPT, EDIT_CONTENT,
 SCHEDULE_BROADCAST) = range(11)

# ==================== MAIN ADMIN DASHBOARD ====================

async def admin_dashboard(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show premium admin dashboard"""
    query = update.callback_query
    user = update.effective_user if query else update.message.from_user
    
    # Check if user is admin
    is_admin = await db.is_admin(user.id)
    
    if not is_admin:
        text = "❌ **Access Denied**\n\nYou are not authorized to access the admin panel."
        if query:
            await query.answer("Access Denied!", show_alert=True)
            await query.edit_message_text(text, parse_mode='Markdown')
        else:
            await update.message.reply_text(text, parse_mode='Markdown')
        return
    
    # Get stats
    stats = await db.get_admin_stats()
    
    text = f"""
👑 **PREMIUM ADMIN DASHBOARD**
═══════════════════════════════════════════════════════════════

📊 **Quick Stats:**
• Total Users: **{stats.get('total_users', 0):,}**
• Active Today: **{stats.get('active_today', 0):,}**
• Total Courses: **{stats.get('total_courses', 0)}**
• Revenue (Month): **₹{stats.get('monthly_revenue', 0):,}**
• Pending Orders: **{stats.get('pending_orders', 0)}**

🔒 **Access Level:** Super Admin
📅 **Last Login:** {datetime.now().strftime('%d %b %Y, %I:%M %p')}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📝 Select an option to manage:
    """
    
    keyboard = [
        [
            InlineKeyboardButton("🤖 AI Assistant", callback_data="admin_ai"),
            InlineKeyboardButton("📢 Broadcast", callback_data="admin_broadcast")
        ],
        [
            InlineKeyboardButton("🚪 Force Join", callback_data="admin_force_join"),
            InlineKeyboardButton("👥 Manage Users", callback_data="admin_users")
        ],
        [
            InlineKeyboardButton("💳 Credits System", callback_data="admin_credits"),
            InlineKeyboardButton("👨‍💼 Manage Admins", callback_data="admin_manage_admins")
        ],
        [
            InlineKeyboardButton("⚙️ Content Editor", callback_data="admin_content"),
            InlineKeyboardButton("📊 Analytics", callback_data="admin_analytics_dashboard")
        ],
        [
            InlineKeyboardButton("📚 Courses", callback_data="admin_courses_panel"),
            InlineKeyboardButton("📝 Orders", callback_data="admin_orders_panel")
        ],
        [
            InlineKeyboardButton("🎨 Customize Bot", callback_data="admin_customize"),
            InlineKeyboardButton("🛠️ Settings", callback_data="admin_settings_panel")
        ],
        [
            InlineKeyboardButton("📄 Export Data", callback_data="admin_export"),
            InlineKeyboardButton("📊 Logs", callback_data="admin_logs")
        ],
        [
            InlineKeyboardButton("🔙 Close", callback_data="admin_close")
        ]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    if query:
        await query.answer()
        await query.edit_message_text(text, reply_markup=reply_markup, parse_mode='Markdown')
    else:
        await update.message.reply_text(text, reply_markup=reply_markup, parse_mode='Markdown')

# ==================== AI ASSISTANT ====================

async def admin_ai_assistant(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """AI-powered admin assistant"""
    query = update.callback_query
    await query.answer()
    
    text = """
🤖 **AI ADMIN ASSISTANT**
═══════════════════════════════════════════════════════════════

💡 **What can I help you with?**

• Generate course descriptions
• Create promotional messages
• Write email templates
• Generate social media posts
• Create FAQ answers
• Draft announcement messages
• Write course outlines
• Generate pricing suggestions

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📝 Type your request or choose a template:
    """
    
    keyboard = [
        [
            InlineKeyboardButton("📚 Generate Course Description", callback_data="ai_course_desc"),
        ],
        [
            InlineKeyboardButton("📣 Promotional Message", callback_data="ai_promo"),
            InlineKeyboardButton("📧 Email Template", callback_data="ai_email")
        ],
        [
            InlineKeyboardButton("📱 Social Media Post", callback_data="ai_social"),
            InlineKeyboardButton("❓ FAQ Answer", callback_data="ai_faq")
        ],
        [
            InlineKeyboardButton("🔙 Back to Dashboard", callback_data="admin_dashboard")
        ]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(text, reply_markup=reply_markup, parse_mode='Markdown')
    
    return AI_PROMPT

# ==================== BROADCAST SYSTEM ====================

async def admin_broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Broadcast message to all users"""
    query = update.callback_query
    await query.answer()
    
    stats = await db.get_broadcast_stats()
    
    text = f"""
📢 **BROADCAST SYSTEM**
═══════════════════════════════════════════════════════════════

📊 **Broadcast Stats:**
• Total Users: **{stats.get('total_users', 0):,}**
• Active Users: **{stats.get('active_users', 0):,}**
• Last Broadcast: **{stats.get('last_broadcast', 'Never')}**
• Success Rate: **{stats.get('success_rate', 0)}%**

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📝 **Choose broadcast type:**
    """
    
    keyboard = [
        [
            InlineKeyboardButton("📤 Send Now", callback_data="broadcast_now"),
            InlineKeyboardButton("⏰ Schedule", callback_data="broadcast_schedule")
        ],
        [
            InlineKeyboardButton("🎯 Target Active Users", callback_data="broadcast_active"),
            InlineKeyboardButton("📅 Target Inactive", callback_data="broadcast_inactive")
        ],
        [
            InlineKeyboardButton("📊 View History", callback_data="broadcast_history"),
            InlineKeyboardButton("🤖 AI Generate", callback_data="broadcast_ai")
        ],
        [
            InlineKeyboardButton("🔙 Back to Dashboard", callback_data="admin_dashboard")
        ]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(text, reply_markup=reply_markup, parse_mode='Markdown')
    
    return ConversationHandler.END

async def broadcast_now(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Send broadcast message now"""
    query = update.callback_query
    await query.answer()
    
    text = """
📝 **COMPOSE BROADCAST MESSAGE**
═══════════════════════════════════════════════════════════════

✏️ Type your broadcast message below:

• You can use Markdown formatting
• Add emojis for better engagement
• Keep it clear and concise
• Include a call-to-action

❗ Type /cancel to abort
    """
    
    await query.edit_message_text(text, parse_mode='Markdown')
    return BROADCAST_MESSAGE

async def broadcast_send(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Process and send broadcast"""
    message_text = update.message.text
    
    # Confirm broadcast
    text = f"""
✅ **CONFIRM BROADCAST**
═══════════════════════════════════════════════════════════════

📝 **Preview:**

{message_text}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

⚠️ This will be sent to all users. Continue?
    """
    
    keyboard = [
        [
            InlineKeyboardButton("✅ Yes, Send Now", callback_data=f"broadcast_confirm_{message_text[:50]}"),
            InlineKeyboardButton("❌ Cancel", callback_data="admin_broadcast")
        ]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(text, reply_markup=reply_markup, parse_mode='Markdown')
    
    # Store message in context
    context.user_data['broadcast_message'] = message_text
    
    return ConversationHandler.END

async def broadcast_confirm(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Execute broadcast to all users"""
    query = update.callback_query
    await query.answer("📤 Sending broadcast...")
    
    message_text = context.user_data.get('broadcast_message', '')
    
    # Get all users
    users = await db.get_all_users()
    
    success_count = 0
    failed_count = 0
    blocked_count = 0
    
    progress_msg = await query.edit_message_text(
        f"📤 **Broadcasting...**\n\nProgress: 0/{len(users)}",
        parse_mode='Markdown'
    )
    
    for index, user in enumerate(users, 1):
        try:
            await context.bot.send_message(
                chat_id=user['user_id'],
                text=message_text,
                parse_mode='Markdown'
            )
            success_count += 1
            
            # Update progress every 10 users
            if index % 10 == 0:
                await progress_msg.edit_text(
                    f"📤 **Broadcasting...**\n\nProgress: {index}/{len(users)}\n✅ Sent: {success_count}\n❌ Failed: {failed_count}",
                    parse_mode='Markdown'
                )
            
            # Rate limiting
            await asyncio.sleep(0.05)
            
        except Exception as e:
            if "blocked" in str(e).lower():
                blocked_count += 1
            failed_count += 1
            logger.error(f"Broadcast failed for user {user['user_id']}: {e}")
    
    # Final report
    await progress_msg.edit_text(
        f"""
✅ **BROADCAST COMPLETE**
═══════════════════════════════════════════════════════════════

📊 **Results:**
• Total Users: **{len(users)}**
• Successfully Sent: **{success_count}** ({success_count*100//len(users) if users else 0}%)
• Failed: **{failed_count}**
• Blocked Bot: **{blocked_count}**

📅 Completed at: {datetime.now().strftime('%I:%M %p')}
        """,
        parse_mode='Markdown'
    )
    
    # Log broadcast
    await db.log_broadcast({
        'message': message_text[:100],
        'total': len(users),
        'success': success_count,
        'failed': failed_count,
        'blocked': blocked_count,
        'timestamp': datetime.now()
    })

# ==================== FORCE JOIN MANAGEMENT ====================

async def admin_force_join(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Manage force join channels/groups"""
    query = update.callback_query
    await query.answer()
    
    channels = await db.get_force_join_channels()
    
    channels_text = ""
    if channels:
        for idx, ch in enumerate(channels, 1):
            channels_text += f"{idx}. **{ch['title']}** (`{ch['username']}`)
   Type: {ch['type'].title()}
   Status: {'\u2705 Active' if ch['active'] else '\u274c Inactive'}\n\n"
    else:
        channels_text = "_No channels/groups configured_"
    
    text = f"""
🚪 **FORCE JOIN MANAGEMENT**
═══════════════════════════════════════════════════════════════

📊 **Configured Channels/Groups:**

{channels_text}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📝 **Manage:**
    """
    
    keyboard = [
        [
            InlineKeyboardButton("➕ Add Channel", callback_data="force_add_channel"),
            InlineKeyboardButton("➕ Add Group", callback_data="force_add_group")
        ],
        [
            InlineKeyboardButton("❌ Remove Channel", callback_data="force_remove"),
            InlineKeyboardButton("🔄 Toggle Status", callback_data="force_toggle")
        ],
        [
            InlineKeyboardButton("📊 Test Force Join", callback_data="force_test"),
            InlineKeyboardButton("🔙 Back", callback_data="admin_dashboard")
        ]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(text, reply_markup=reply_markup, parse_mode='Markdown')

# ==================== USER CREDIT MANAGEMENT ====================

async def admin_credits(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Manage user credits"""
    query = update.callback_query
    await query.answer()
    
    text = """
💳 **CREDIT MANAGEMENT SYSTEM**
═══════════════════════════════════════════════════════════════

📊 **System Overview:**
• Users can use credits to buy courses
• 1 Credit = ₹1
• Credits are non-refundable

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📝 **Choose action:**
    """
    
    keyboard = [
        [
            InlineKeyboardButton("➕ Add Credits", callback_data="credits_add"),
            InlineKeyboardButton("➖ Remove Credits", callback_data="credits_remove")
        ],
        [
            InlineKeyboardButton("🎯 Set Credits", callback_data="credits_set"),
            InlineKeyboardButton("📊 View User Credits", callback_data="credits_view")
        ],
        [
            InlineKeyboardButton("🎁 Bulk Credit Award", callback_data="credits_bulk"),
            InlineKeyboardButton("📊 Leaderboard", callback_data="credits_leaderboard")
        ],
        [
            InlineKeyboardButton("🔙 Back to Dashboard", callback_data="admin_dashboard")
        ]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(text, reply_markup=reply_markup, parse_mode='Markdown')

# ==================== ADMIN MANAGEMENT ====================

async def admin_manage_admins(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Manage admin users"""
    query = update.callback_query
    await query.answer()
    
    admins = await db.get_all_admins()
    
    admins_text = ""
    for admin in admins:
        status = "🟢 Active" if admin.get('active') else "🔴 Inactive"
        admins_text += f"• **{admin['name']}** (`{admin['user_id']}`)
  Level: {admin.get('level', 'Admin').title()} | {status}\n\n"
    
    text = f"""
👨‍💼 **ADMIN MANAGEMENT**
═══════════════════════════════════════════════════════════════

📈 **Current Admins:** ({len(admins)})

{admins_text}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📝 **Manage:**
    """
    
    keyboard = [
        [
            InlineKeyboardButton("➕ Add Admin", callback_data="admins_add"),
            InlineKeyboardButton("❌ Remove Admin", callback_data="admins_remove")
        ],
        [
            InlineKeyboardButton("⚙️ Change Level", callback_data="admins_level"),
            InlineKeyboardButton("🔒 Toggle Status", callback_data="admins_toggle")
        ],
        [
            InlineKeyboardButton("🔙 Back to Dashboard", callback_data="admin_dashboard")
        ]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(text, reply_markup=reply_markup, parse_mode='Markdown')

# ==================== HELPER FUNCTIONS ====================

async def admin_close(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Close admin panel"""
    query = update.callback_query
    await query.answer("Admin panel closed")
    await query.delete_message()

async def cancel_action(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Cancel current action"""
    await update.message.reply_text("❌ Action cancelled.")
    return ConversationHandler.END
