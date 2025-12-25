# 💳 Payment Handler - Verify & Process Payments

import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from models.order import Order
from models.course import Course
from utils.decorators import log_command

logger = logging.getLogger(__name__)


@log_command("verify")
async def verify_payment_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Verify payment by order ID"""
    
    if not context.args:
        await update.message.reply_text(
            "❌ Please provide order ID\n\n"
            "Usage: /verify <order_id>"
        )
        return
    
    try:
        order_id = int(context.args[0])
    except ValueError:
        await update.message.reply_text("❌ Invalid order ID")
        return
    
    # Get order
    order = await Order.get_by_id(order_id)
    
    if not order:
        await update.message.reply_text("❌ Order not found")
        return
    
    if order['user_id'] != update.effective_user.id:
        await update.message.reply_text("❌ This order doesn't belong to you")
        return
    
    # Show payment info
    message = f"""
📦 ORDER DETAILS:

Order ID: {order_id}
User: {order['user_name']}
Status: {order['payment_status'].upper()}

Do you want to complete this payment?
"""
    
    keyboard = [
        [InlineKeyboardButton("✅ Mark as Paid", callback_data=f"pay_verify_{order_id}")],
        [InlineKeyboardButton("❌ Cancel", callback_data="pay_cancel")],
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(message, reply_markup=reply_markup)


async def process_payment_verification(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Process payment verification"""
    query = update.callback_query
    await query.answer()
    
    order_id = int(query.data.split('_')[2])
    user_id = query.from_user.id
    
    # Get order
    order = await Order.get_by_id(order_id)
    
    if not order or order['user_id'] != user_id:
        await query.edit_message_text("❌ Invalid order")
        return
    
    if order['payment_status'] != 'pending':
        await query.edit_message_text(f"❌ Order already {order['payment_status']}")
        return
    
    # Mark as completed
    await Order.mark_completed(order_id, transaction_id=f"manual_{order_id}")
    
    # Get course
    course = await Course.get_by_id(order['course_id'])
    
    # Send access granted message
    message = f"""
✅ PAYMENT VERIFIED!

You now have access to:
📚 {course['title']}

Thank you for your purchase!
You have lifetime access to this course.

Order ID: {order_id}
Access Status: ✅ Active
"""
    
    keyboard = [
        [InlineKeyboardButton("📚 View Course", url=f"https://t.me/{context.bot.username}")],
        [InlineKeyboardButton("🛍️ Browse More", callback_data="browse_courses")],
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(message, reply_markup=reply_markup)
    
    logger.info(f"✅ Payment processed for order {order_id}")


async def cancel_payment(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Cancel payment verification"""
    query = update.callback_query
    await query.answer()
    
    await query.edit_message_text("❌ Verification cancelled")


async def check_payment_status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Check payment status for an order"""
    
    if not context.args:
        await update.message.reply_text(
            "❌ Please provide order ID\n\n"
            "Usage: /status <order_id>"
        )
        return
    
    try:
        order_id = int(context.args[0])
    except ValueError:
        await update.message.reply_text("❌ Invalid order ID")
        return
    
    # Get order
    order = await Order.get_by_id(order_id)
    
    if not order:
        await update.message.reply_text("❌ Order not found")
        return
    
    if order['user_id'] != update.effective_user.id:
        await update.message.reply_text("❌ This order doesn't belong to you")
        return
    
    # Get course
    course = await Course.get_by_id(order['course_id'])
    
    status_map = {
        'pending': '⏳ Pending',
        'completed': '✅ Completed',
        'failed': '❌ Failed'
    }
    
    message = f"""
📦 ORDER STATUS:

Order ID: {order_id}
Course: {course['title']}
Amount: ₹{order['price']}
Status: {status_map.get(order['payment_status'], 'Unknown')}

Created: {order['created_at']}
Updated: {order['updated_at']}
"""
    
    if order['payment_status'] == 'pending':
        message += f"""

Send payment to:
📱 {context.bot.username}

Use command: /verify {order_id}
"""
    
    await update.message.reply_text(message)


async def get_order_info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Get order information"""
    
    if not context.args:
        # Show all orders for this user
        orders = await Order.get_user_orders(update.effective_user.id)
        
        if not orders:
            await update.message.reply_text("You don't have any orders yet")
            return
        
        message = "📦 YOUR ORDERS:\n\n"
        
        for order in orders:
            course = await Course.get_by_id(order['course_id'])
            status = "✅" if order['payment_status'] == 'completed' else "⏳"
            
            message += f"{status} Order #{order['id']}\n"
            message += f"   Course: {course['title']}\n"
            message += f"   Amount: ₹{order['price']}\n"
            message += f"   Status: {order['payment_status']}\n\n"
        
        await update.message.reply_text(message)
    else:
        # Show specific order
        try:
            order_id = int(context.args[0])
        except ValueError:
            await update.message.reply_text("❌ Invalid order ID")
            return
        
        order = await Order.get_by_id(order_id)
        
        if not order or order['user_id'] != update.effective_user.id:
            await update.message.reply_text("❌ Order not found")
            return
        
        course = await Course.get_by_id(order['course_id'])
        
        message = f"""
📦 ORDER DETAILS:

Order ID: {order_id}
Course: {course['title']}
Amount: ₹{order['price']}
Status: {order['payment_status']}
User: {order['user_name']}
Created: {order['created_at']}
"""
        
        await update.message.reply_text(message)
