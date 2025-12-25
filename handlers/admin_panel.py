# 👑 Admin Panel Handler

import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from utils.decorators import admin_only, log_command
from models.course import Course
from models.order import Order

logger = logging.getLogger(__name__)


@admin_only
@log_command("admin")
async def admin_panel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show admin control panel"""
    
    # Get statistics
    total_courses = await Course.count_all()
    pending_orders = len(await Order.get_pending_orders()) if await Order.get_pending_orders() else 0
    total_revenue = await Order.get_total_revenue()
    
    # Create buttons
    keyboard = [
        [InlineKeyboardButton("📝 Create Course", callback_data="admin_create_course")],
        [InlineKeyboardButton("📚 Manage Courses", callback_data="admin_manage_courses")],
        [InlineKeyboardButton("💰 View Analytics", callback_data="admin_analytics")],
        [InlineKeyboardButton("⚙️ Settings", callback_data="admin_settings")],
        [InlineKeyboardButton("🔄 Orders", callback_data="admin_orders")],
        [InlineKeyboardButton("❌ Cancel", callback_data="cancel")],
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    message = f"""
👑 ADMIN CONTROL PANEL 🎛️

📊 STATISTICS:
├─ 📚 Total Courses: {total_courses}
├─ 📦 Pending Orders: {pending_orders}
└─ 💰 Total Revenue: ₹{total_revenue:,.2f}

Select an action:
"""
    
    await update.message.reply_text(message, reply_markup=reply_markup)


async def admin_create_course_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start course creation process"""
    query = update.callback_query
    await query.answer()
    
    await query.edit_message_text(
        "📝 Let's create a new course!\n\n"
        "Send the course title (5-100 characters):"
    )
    
    # Store state
    context.user_data['admin_state'] = 'waiting_title'


async def admin_manage_courses_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show list of courses to manage"""
    query = update.callback_query
    await query.answer()
    
    courses = await Course.get_all(limit=10)
    
    if not courses:
        await query.edit_message_text("No courses found.")
        return
    
    message = "📚 YOUR COURSES:\n\n"
    
    for i, course in enumerate(courses, 1):
        message += f"{i}. {course['title']}\n"
        message += f"   💰 ₹{course['price']} | ⭐ {course['rating']} ({course['reviews']} reviews)\n"
        message += f"   ID: {course['id']}\n\n"
    
    await query.edit_message_text(message)


async def admin_analytics_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show analytics dashboard"""
    query = update.callback_query
    await query.answer()
    
    total_courses = await Course.count_all()
    total_revenue = await Order.get_total_revenue()
    completed_orders = len(await Order.get_completed_orders()) if await Order.get_completed_orders() else 0
    
    message = f"""
📊 ANALYTICS DASHBOARD

📈 KEY METRICS:
├─ 📚 Total Courses: {total_courses}
├─ 📦 Completed Orders: {completed_orders}
├─ 💰 Total Revenue: ₹{total_revenue:,.2f}
└─ 📊 Avg per Order: ₹{total_revenue / completed_orders if completed_orders > 0 else 0:,.2f}

📅 PERIOD: All Time
🌍 CURRENCY: INR (₹)
"""
    
    await query.edit_message_text(message)


async def admin_settings_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show settings menu"""
    query = update.callback_query
    await query.answer()
    
    keyboard = [
        [InlineKeyboardButton("📱 Bot Settings", callback_data="settings_bot")],
        [InlineKeyboardButton("💳 Payment Settings", callback_data="settings_payment")],
        [InlineKeyboardButton("🎨 Channel Settings", callback_data="settings_channel")],
        [InlineKeyboardButton("🔙 Back", callback_data="admin_back")],
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text("⚙️ SETTINGS MENU:", reply_markup=reply_markup)


async def admin_orders_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show recent orders"""
    query = update.callback_query
    await query.answer()
    
    pending = await Order.get_pending_orders(limit=5)
    completed = await Order.get_completed_orders()
    completed = completed[:5] if completed else []
    
    message = "📦 RECENT ORDERS:\n\n"
    
    message += "⏳ PENDING:\n"
    if pending:
        for order in pending:
            message += f"  • Order #{order['id']}: Course {order['course_id']} - ₹{order['price']}\n"
    else:
        message += "  No pending orders\n"
    
    message += "\n✅ COMPLETED:\n"
    if completed:
        for order in completed:
            message += f"  • Order #{order['id']}: Course {order['course_id']} - ₹{order['price']}\n"
    else:
        message += "  No completed orders\n"
    
    await query.edit_message_text(message)


async def cancel_admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Cancel admin operation"""
    query = update.callback_query
    await query.answer()
    
    context.user_data.pop('admin_state', None)
    
    await query.edit_message_text("❌ Cancelled")
