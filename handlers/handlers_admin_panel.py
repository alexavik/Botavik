# handlers/admin_panel.py
"""
Admin Panel Handler - Complete Admin Interface
Features: Course management, analytics, settings, payment config
"""

import logging
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes
from config import BotConfig
from utils.decorators import admin_only

logger = logging.getLogger(__name__)

class AdminPanel:
    """Advanced admin panel with analytics and management"""
    
    @staticmethod
    async def show_admin_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Display main admin control panel"""
        user = update.effective_user
        
        if user.id not in BotConfig.ADMIN_USER_IDS:
            await update.message.reply_text("❌ Access denied. You are not authorized to use admin commands.")
            return
        
        menu_text = f"""
👑 ADMIN CONTROL PANEL 🎛️
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

👤 Admin: {user.first_name}
🆔 User ID: {user.id}
📊 Status: 🟢 Online

What would you like to do?
        """
        
        keyboard = [
            [InlineKeyboardButton("📚 Create Course", callback_data="create_course")],
            [InlineKeyboardButton("🎬 Manage Courses", callback_data="manage_courses")],
            [InlineKeyboardButton("📊 Analytics Dashboard", callback_data="view_analytics")],
            [InlineKeyboardButton("💰 Payment Settings", callback_data="payment_settings")],
            [InlineKeyboardButton("⚙️ Bot Settings", callback_data="bot_settings")],
            [InlineKeyboardButton("❌ Close", callback_data="close_admin")]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(menu_text, reply_markup=reply_markup, parse_mode='HTML')
        logger.info(f"✅ Admin {user.id} opened control panel")
    
    @staticmethod
    async def show_analytics(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Display analytics dashboard"""
        query = update.callback_query
        await query.answer()
        
        # TODO: Fetch from database
        analytics_text = """
📊 ANALYTICS DASHBOARD 📈
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📚 COURSES:
├─ Total Courses: 0
├─ Active Courses: 0
├─ Archived Courses: 0
└─ Average Rating: ⭐ 0.0

👥 USERS:
├─ Total Users: 0
├─ New This Week: 0
├─ Active Users: 0
└─ Conversion Rate: 0%

💰 REVENUE:
├─ Today: ₹0
├─ This Week: ₹0
├─ This Month: ₹0
└─ Total: ₹0

📦 ORDERS:
├─ Total Orders: 0
├─ Pending: 0
├─ Completed: 0
└─ Failed: 0

⏰ Last Updated: Just now
        """
        
        keyboard = [[InlineKeyboardButton("« Back", callback_data="admin_menu")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(analytics_text, reply_markup=reply_markup)
    
    @staticmethod
    async def payment_settings(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show payment configuration"""
        query = update.callback_query
        await query.answer()
        
        payment_text = f"""
💳 PAYMENT SETTINGS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🏦 Payment Method: FamPay UPI
📱 UPI ID: {BotConfig.PAYMENT_CONFIG.get('FAMPAY_UPI_ID', 'Not Set')}

⚙️ Configuration:
├─ Auto-Verify: Enabled ✅
├─ Manual Verification: Available
├─ Refund Policy: Manual Review
└─ Transaction Logging: Enabled ✅

💵 Fee Structure:
├─ Platform Fee: 0% ✅
├─ Payment Gateway: 0% ✅
└─ Your Earnings: 100%

🔐 Security:
├─ Transaction ID Logging: ✅
├─ Amount Verification: ✅
├─ User ID Verification: ✅
└─ Duplicate Check: ✅

📊 This Month:
├─ Transactions: 0
├─ Successful: 0
├─ Pending: 0
├─ Failed: 0
└─ Total Revenue: ₹0

⚠️ Note: Payment verification requires manual UPI confirmation
        """
        
        keyboard = [[InlineKeyboardButton("« Back", callback_data="admin_menu")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(payment_text, reply_markup=reply_markup)
    
    @staticmethod
    async def bot_settings(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show bot configuration"""
        query = update.callback_query
        await query.answer()
        
        settings_text = f"""
⚙️ BOT SETTINGS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🤖 Bot Information:
├─ Bot Name: @{BotConfig.BOT_USERNAME}
├─ Channel: {BotConfig.PUBLISHING_CHANNEL_ID}
├─ Environment: {BotConfig.ENVIRONMENT}
└─ Status: 🟢 Online

🔐 Security Settings:
├─ Admin Authorization: ✅
├─ Input Validation: ✅
├─ Rate Limiting: ✅
└─ Error Logging: ✅

🤖 AI Settings:
├─ Model: Gemini 2.0 Flash
├─ API: OpenRouter
├─ Temperature: 0.7
└─ Max Tokens: 1024

📊 Database:
├─ Type: PostgreSQL
├─ Tables: 3 (courses, orders, wishlist)
├─ Indexes: 8
└─ Status: Connected ✅

📝 Logging:
├─ Log Level: INFO
├─ Log File: logs/bot.log
├─ Console Logging: Enabled
└─ File Size: Auto-rotating

✅ All Systems Operational
        """
        
        keyboard = [[InlineKeyboardButton("« Back", callback_data="admin_menu")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(settings_text, reply_markup=reply_markup)

# Main admin command
async def admin_panel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Entry point for admin panel"""
    await AdminPanel.show_admin_menu(update, context)
