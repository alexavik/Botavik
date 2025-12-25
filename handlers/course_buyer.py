# 🛒 Course Buyer Handler - Purchases & Wishlist

import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from utils.decorators import log_command
from models.course import Course
from models.order import Order
from models.wishlist import Wishlist
from config import BotConfig, PaymentConfig

logger = logging.getLogger(__name__)


async def browse_courses(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show available courses"""
    
    courses = await Course.get_all(limit=10)
    
    if not courses:
        await update.message.reply_text("❌ No courses available yet")
        return
    
    for course in courses:
        is_wishlisted = await Wishlist.is_wishlisted(update.effective_user.id, course['id'])
        
        message = f"""
🎓 {course['title']}

{course['description'][:200]}...

💰 Price: ₹{course['price']}
⭐ Rating: {course['rating']} ({course['reviews']} reviews)
"""
        
        keyboard = [
            [InlineKeyboardButton("🛒 Buy Now", callback_data=f"buy_{course['id']}")],
            [InlineKeyboardButton(
                f"{'❤️ Remove' if is_wishlisted else '🤍 Add to Wishlist'}", 
                callback_data=f"wish_{course['id']}"
            )],
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        if course['demo_video_id']:
            await update.message.reply_video(
                video=course['demo_video_id'],
                caption=message,
                reply_markup=reply_markup
            )
        else:
            await update.message.reply_text(message, reply_markup=reply_markup)


async def handle_buy_course(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle buy button click"""
    query = update.callback_query
    await query.answer()
    
    course_id = int(query.data.split('_')[1])
    user_id = query.from_user.id
    
    # Check if already purchased
    existing_order = await Order.get_user_course_purchase(user_id, course_id)
    if existing_order:
        await query.edit_message_text("✅ You already own this course!")
        return
    
    # Get course details
    course = await Course.get_by_id(course_id)
    if not course:
        await query.edit_message_text("❌ Course not found")
        return
    
    # Create pending order
    order_id = await Order.create(
        user_id=user_id,
        course_id=course_id,
        price=course['price'],
        user_name=query.from_user.full_name
    )
    
    # Show payment details
    payment_message = f"""
💳 PAYMENT DETAILS

Course: {course['title']}
Price: ₹{course['price']}

Send payment to:
📱 {PaymentConfig.FAMPAY_UPI_ID}

After payment, send:
/verify {order_id}

Note: Store your order ID: {order_id}
"""
    
    keyboard = [
        [InlineKeyboardButton("✅ I've Paid", callback_data=f"verify_{order_id}")],
        [InlineKeyboardButton("❌ Cancel", callback_data=f"cancel_order_{order_id}")],
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(payment_message, reply_markup=reply_markup)


async def verify_payment(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Verify payment and grant access"""
    query = update.callback_query
    await query.answer()
    
    order_id = int(query.data.split('_')[1])
    
    # Get order
    order = await Order.get_by_id(order_id)
    if not order:
        await query.edit_message_text("❌ Order not found")
        return
    
    # Mark as completed
    await Order.mark_completed(order_id, transaction_id=f"upi_{order_id}")
    
    # Get course
    course = await Course.get_by_id(order['course_id'])
    
    access_message = f"""
✅ PAYMENT VERIFIED!

You now have access to:
📚 {course['title']}

You can now access all course materials.
Thank you for purchasing!

Course ID: {course['id']}
Access expires: Never (Lifetime access)
"""
    
    await query.edit_message_text(access_message)
    
    logger.info(f"✅ Payment verified for order {order_id}")


async def cancel_order(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Cancel an order"""
    query = update.callback_query
    await query.answer()
    
    order_id = int(query.data.split('_')[2])
    
    # Delete pending order
    await Order.delete_pending(order_id)
    
    await query.edit_message_text("❌ Order cancelled")
    
    logger.info(f"✅ Order {order_id} cancelled")


async def handle_wishlist(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle wishlist toggle"""
    query = update.callback_query
    await query.answer()
    
    course_id = int(query.data.split('_')[1])
    user_id = query.from_user.id
    
    # Toggle wishlist
    result = await Wishlist.toggle(user_id, course_id)
    
    if result:
        await query.answer("❤️ Added to wishlist", show_alert=True)
    else:
        await query.answer("🤍 Removed from wishlist", show_alert=True)


async def view_wishlist(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show user's wishlist"""
    
    wishlist = await Wishlist.get_user_wishlist(update.effective_user.id)
    
    if not wishlist:
        await update.message.reply_text("Your wishlist is empty")
        return
    
    message = "❤️ YOUR WISHLIST:\n\n"
    
    for course in wishlist:
        message += f"📚 {course['title']}\n"
        message += f"   💰 ₹{course['price']}\n\n"
    
    keyboard = [
        [InlineKeyboardButton("🛍️ Browse All Courses", callback_data="browse_courses")],
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(message, reply_markup=reply_markup)


async def view_my_courses(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show courses user has purchased"""
    
    user_id = update.effective_user.id
    
    # Get all orders for user
    orders = await Order.get_user_orders(user_id)
    completed_orders = [o for o in orders if o['payment_status'] == 'completed']
    
    if not completed_orders:
        await update.message.reply_text("You haven't purchased any courses yet")
        return
    
    message = "📚 YOUR COURSES:\n\n"
    
    for order in completed_orders:
        course = await Course.get_by_id(order['course_id'])
        if course:
            message += f"✅ {course['title']}\n"
            message += f"   💰 Paid: ₹{order['price']}\n"
            message += f"   📅 Purchased: {order['created_at']}\n\n"
    
    await update.message.reply_text(message)
