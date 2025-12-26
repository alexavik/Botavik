# Owner Mode Handlers - Browse, Refer, Donate, Resell

import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from config import BotConfig

logger = logging.getLogger(__name__)

# COURSE BROWSING
async def owner_courses(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show all available courses"""
    query = update.callback_query
    await query.answer()
    
    courses_text = """
📚 ALL COURSES
═══════════════════════════════════════════════════════════════

Fetching all available courses...

Courses will be displayed here:
📚 **Course Name**
💰 Price: ₹X,XXX
⭐ Rating: 4.8/5 (120 reviews)

_Click on course name to buy or view details_
"""
    
    keyboard = [
        [InlineKeyboardButton("🔄 Refresh", callback_data='owner_courses')],
        [InlineKeyboardButton("◀️ Back", callback_data='owner_menu')]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        courses_text,
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )
    logger.info(f"📚 User {update.effective_user.id} viewed all courses")

# COURSE CHANNEL
async def owner_channel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show course channel link"""
    query = update.callback_query
    await query.answer()
    
    channel_link = getattr(BotConfig, 'COURSE_CHANNEL_LINK', 'https://t.me/course_pro911')
    channel_text = f"""
🏢 COURSE CHANNEL
═══════════════════════════════════════════════════════════════

👋 Welcome to our main course channel!

**Course Pro911** is where all new courses are posted.

✓ New course updates
✓ Flash sales & discounts  
✓ Course announcements
✓ Special offers

Join now to stay updated!
"""
    
    keyboard = [
        [InlineKeyboardButton("🔗 Open Channel", url=channel_link)],
        [InlineKeyboardButton("◀️ Back", callback_data='owner_menu')]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        channel_text,
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

# DISCUSSION
async def owner_discussion(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show discussion/community link"""
    query = update.callback_query
    await query.answer()
    
    discussion_link = getattr(BotConfig, 'DISCUSSION_LINK', 'https://t.me/course_pro911_discussion')
    discussion_text = f"""
💬 COURSE DISCUSSIONS
═══════════════════════════════════════════════════════════════

🤛 Join our community to discuss courses!

**Features:**
✔️ Ask course-related questions
✔️ Share your learning experience
✔️ Get tips & tricks from other students
✔️ Connect with course creators
✔️ Group study opportunities

Community Guidelines: Be respectful and helpful! ⚠️
"""
    
    keyboard = [
        [InlineKeyboardButton("🔗 Join Discussion", url=discussion_link)],
        [InlineKeyboardButton("◀️ Back", callback_data='owner_menu')]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        discussion_text,
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

# WEBSITE
async def owner_website(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show website link"""
    query = update.callback_query
    await query.answer()
    
    website_link = getattr(BotConfig, 'WEBSITE_URL', 'https://coursepro911.com')
    website_text = f"""
🌐 OUR WEBSITE
═══════════════════════════════════════════════════════════════

Visit our website to learn more!

📚 Browse all courses
💰 View pricing details
📄 Read blog posts & tutorials
🎤 Watch video previews
👥 Meet our instructors
"""
    
    keyboard = [
        [InlineKeyboardButton("🔗 Visit Website", url=website_link)],
        [InlineKeyboardButton("◀️ Back", callback_data='owner_menu')]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        website_text,
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

# REFER & EARN
async def owner_refer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show referral program"""
    query = update.callback_query
    await query.answer()
    user = update.effective_user
    
    refer_text = f"""
💰 REFER & EARN
═══════════════════════════════════════════════════════════════

🎉 Earn money by referring your friends!

**How it works:**
1. Share your referral link
2. Friend purchases a course
3. You get 20% commission! 💵

**Your Referral Link:**
```
https://t.me/coursepro911_bot?start=ref_{user.id}
```

**Earnings:**
✔️ Unlimited referrals
✔️ 20% commission per sale
✔️ Instant payment after 30 days
✔️ No minimum threshold

_Use your link to share with friends!_
"""
    
    keyboard = [
        [InlineKeyboardButton("📈 View My Earnings", callback_data='refer_earnings')],
        [InlineKeyboardButton("◀️ Back", callback_data='owner_menu')]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        refer_text,
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

# DONATE
async def owner_donate(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show donation options"""
    query = update.callback_query
    await query.answer()
    
    donate_text = """
❤️ SUPPORT US
═══════════════════════════════════════════════════════════════

Your support helps us create better courses!

**Donation Options:**
💳 UPI: coursepro911@upi
💳 Bank Transfer: Contact support
💳 Paytm: 9123456789

**Benefits of donating:**
✔️ Get exclusive course discounts
✔️ Priority support
✔️ Early access to new courses
✔️ Special thank you badge

Thank you for your generosity! 🙋
"""
    
    keyboard = [
        [InlineKeyboardButton("📧 Contact for Donation", callback_data='donate_contact')],
        [InlineKeyboardButton("◀️ Back", callback_data='owner_menu')]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        donate_text,
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

# RESELL PROGRAM
async def owner_resell(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show reseller program details"""
    query = update.callback_query
    await query.answer()
    
    resell_text = """
🔄 RESELLER PROGRAM
═══════════════════════════════════════════════════════════════

🎧 Become a reseller and earn passive income!

**What is reselling?**
Buy courses at wholesale price and resell them with your markup!

**Reseller Benefits:**
✅ 50% wholesale discount on all courses
✅ Create your own course bundles
✅ White-label options available
✅ Marketing materials provided
✅ Dedicated reseller support
✅ Monthly bonus for top sellers

**Requirements:**
📄 Complete application form
📄 Minimum order: ₹10,000
📄 Valid business registration (optional)
📄 Bank account for payments

_Interested in becoming a reseller?_
"""
    
    keyboard = [
        [InlineKeyboardButton("📄 Apply Now", callback_data='reseller_apply')],
        [InlineKeyboardButton("📧 Email us", callback_data='reseller_contact')],
        [InlineKeyboardButton("◀️ Back", callback_data='owner_menu')]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        resell_text,
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )
