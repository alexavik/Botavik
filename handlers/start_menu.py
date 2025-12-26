# Start Menu Handler - Main user entry point
# Shows two options: Owner Menu and Admin Menu

import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from utils.decorators import log_user_action

logger = logging.getLogger(__name__)

@log_user_action
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show main menu with Owner and Admin options"""
    user = update.effective_user
    
    welcome_text = f"""
🌐 Welcome to Course Pro911 Bot! 🌐
{'═' * 60}

Hi {user.first_name}! 👋

Choose what you want to do:

👤 **Owner Mode** - Browse & Buy Courses
👑 **Admin Mode** - Manage Courses & Settings
"""
    
    keyboard = [
        [
            InlineKeyboardButton("👤 Owner Mode", callback_data='owner_menu'),
            InlineKeyboardButton("👑 Admin Mode", callback_data='admin_menu')
        ]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        welcome_text,
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )
    logger.info(f"✅ User {user.id} accessed start menu")

# ═════════════════════════════════════════════════════════════════════════════
# OWNER MENU - User/Buyer Functions
# ═════════════════════════════════════════════════════════════════════════════

async def owner_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show Owner menu with options to browse courses, refer, donate, etc."""
    query = update.callback_query
    await query.answer()
    
    owner_text = """
👤 OWNER MODE
═══════════════════════════════════════════════════════════════

What would you like to do?

📚 **Courses** - Browse all available courses
🏢 **Course Channel** - Visit our main course channel
💬 **Discussion** - Join course discussions
🌐 **Website** - Visit our website
💰 **Refer & Earn** - Earn money by referring friends
❤️ **Donate** - Support us
🔄 **Resell** - Become a reseller
"""
    
    keyboard = [
        [InlineKeyboardButton("📚 All Courses", callback_data='owner_courses')],
        [InlineKeyboardButton("🏢 Course Channel", callback_data='owner_channel')],
        [InlineKeyboardButton("💬 Discussion", callback_data='owner_discussion')],
        [InlineKeyboardButton("🌐 Website", callback_data='owner_website')],
        [InlineKeyboardButton("💰 Refer & Earn", callback_data='owner_refer')],
        [InlineKeyboardButton("❤️ Donate", callback_data='owner_donate')],
        [InlineKeyboardButton("🔄 Resell", callback_data='owner_resell')],
        [InlineKeyboardButton("◀️ Back", callback_data='back_start')]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        owner_text,
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

# ═════════════════════════════════════════════════════════════════════════════
# ADMIN MENU - Admin/Owner Functions
# ═════════════════════════════════════════════════════════════════════════════

async def admin_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show Admin menu with course management options"""
    query = update.callback_query
    await query.answer()
    
    # Check if user is admin
    admin_id = context.bot_data.get('admin_id')
    user_id = update.effective_user.id
    
    if user_id != admin_id:
        await query.edit_message_text(
            "❌ You are not authorized to access admin menu.\n\nContact @unknownwarrior911 for access."
        )
        return
    
    admin_text = """
👑 ADMIN CONTROL PANEL
═══════════════════════════════════════════════════════════════

Manage your course platform:

📚 **Courses** - Create, edit, delete courses
✅ **Proof** - Manage course proof/screenshots
⚙️ **Settings** - Bot settings & configuration
🆕 **Latest Course** - Show latest course posted
📊 **Statistics** - View analytics & data
📬 **Request Course** - Manage course requests
"""
    
    keyboard = [
        [InlineKeyboardButton("📚 Courses", callback_data='admin_courses')],
        [InlineKeyboardButton("✅ Proof", callback_data='admin_proof')],
        [InlineKeyboardButton("⚙️ Settings", callback_data='admin_settings')],
        [InlineKeyboardButton("🆕 Latest Course", callback_data='admin_latest')],
        [InlineKeyboardButton("📊 Statistics", callback_data='admin_stats')],
        [InlineKeyboardButton("📬 Requests", callback_data='admin_requests')],
        [InlineKeyboardButton("◀️ Back", callback_data='back_start')]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        admin_text,
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

# ═════════════════════════════════════════════════════════════════════════════
# BACK BUTTON - Return to main menu
# ═════════════════════════════════════════════════════════════════════════════

async def back_to_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Go back to start menu"""
    query = update.callback_query
    await query.answer()
    await start(update, context)
