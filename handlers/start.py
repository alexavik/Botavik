# Start command and main menu handlers

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import ContextTypes
import logging

logger = logging.getLogger(__name__)

def get_reply_keyboard():
    """Get the persistent reply keyboard (bottom menu)"""
    keyboard = [
        [KeyboardButton("👨‍💼 Owner"), KeyboardButton("📺 Course Channel")],
        [KeyboardButton("💬 Discussion"), KeyboardButton("📚 All Courses")],
        [KeyboardButton("🌐 Website"), KeyboardButton("🎁 Donate")],
        [KeyboardButton("💸 Resell")]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True, persistent=True)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /start command - Show main menu with both keyboards"""
    user = update.effective_user
    
    welcome = f"""
🌐 𝐂𝐎𝐔𝐑𝐒𝐄 𝐏𝐑𝐎 𝐁𝐎𝐓
═══════════════════════════════════════════════════════════════

👋 Welcome {user.first_name}!

🎓 Learn amazing courses from industry experts
💰 100% secure & instant payment verification
❤️ Save favorites to your wishlist
🎁 Get exclusive discounts & referral rewards

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📋 Use the buttons below to navigate:
    """
    
    # Inline keyboard for main menu
    inline_keyboard = [
        [
            InlineKeyboardButton("📚 Courses", callback_data="menu_courses"),
            InlineKeyboardButton("🎬 Proof", callback_data="menu_proof")
        ],
        [
            InlineKeyboardButton("⚙️ Settings", callback_data="menu_settings"),
            InlineKeyboardButton("🆕 Latest Course", callback_data="menu_latest")
        ],
        [
            InlineKeyboardButton("📊 Statistics", callback_data="menu_statistics"),
            InlineKeyboardButton("❓ Request Course", callback_data="menu_request")
        ]
    ]
    
    inline_markup = InlineKeyboardMarkup(inline_keyboard)
    reply_markup = get_reply_keyboard()
    
    await update.message.reply_text(
        welcome, 
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )
    
    # Send inline menu as separate message
    await update.message.reply_text(
        "🎯 **Quick Actions:**\n\nSelect what you want to do:",
        reply_markup=inline_markup,
        parse_mode='Markdown'
    )
    
    logger.info(f"✅ User {user.id} ({user.username}) started bot")

# ==================== INLINE KEYBOARD HANDLERS ====================

async def menu_courses(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show all courses (inline button)"""
    query = update.callback_query
    await query.answer()
    
    text = """
📚 COURSES
═════════════════════════════════════════════════════════════════

🎓 All available courses:

1. 🔐 Cybersecurity Mastery
   └─ Learn ethical hacking & penetration testing
   └─ ₹999 | ⭐⭐⭐⭐⭐ (250+ reviews)

2. 💻 Web Development Pro
   └─ Master full-stack development
   └─ ₹1499 | ⭐⭐⭐⭐ (180+ reviews)

3. 🤖 AI & Machine Learning
   └─ Build intelligent applications
   └─ ₹1999 | ⭐⭐⭐⭐⭐ (150+ reviews)

4. 📱 Android Development
   └─ Create professional Android apps
   └─ ₹899 | ⭐⭐⭐⭐ (120+ reviews)

5. 🐍 Python Advanced
   └─ Master Python programming
   └─ ₹799 | ⭐⭐⭐⭐ (300+ reviews)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

💡 Tip: Click on any course to buy or add to wishlist!
    """
    
    keyboard = [
        [InlineKeyboardButton("🔙 Back to Menu", callback_data="back_to_menu")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(text, reply_markup=reply_markup, parse_mode='Markdown')

async def menu_proof(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show proof/testimonials (inline button)"""
    query = update.callback_query
    await query.answer()
    
    text = """
🎬 PROOF & TESTIMONIALS
═════════════════════════════════════════════════════════════════

✅ Real Success Stories:

👤 Rahul Kumar
   "This course changed my career! Got promoted within 3 months."
   ⭐⭐⭐⭐⭐

👤 Priya Sharma  
   "Best investment for my cybersecurity learning journey."
   ⭐⭐⭐⭐⭐

👤 Vikram Singh
   "Excellent content, lifetime access is amazing!"
   ⭐⭐⭐⭐⭐

📺 Video Testimonials:
   [Link to YouTube Channel]

📊 Course Stats:
   ✅ 5000+ Students
   ✅ 98% Satisfaction Rate
   ✅ 1000+ Success Stories
   ✅ Lifetime Access Guaranteed

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    """
    
    keyboard = [
        [InlineKeyboardButton("🔙 Back to Menu", callback_data="back_to_menu")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(text, reply_markup=reply_markup, parse_mode='Markdown')

async def menu_settings(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """User settings (inline button)"""
    query = update.callback_query
    await query.answer()
    
    text = """
⚙️ SETTINGS
═════════════════════════════════════════════════════════════════

🔧 Preferences:

✅ Notifications
   [Enabled]

✅ Language
   [English]

✅ Payment Method
   [UPI/FamPay]

✅ Display Theme
   [Light/Dark Mode]

✅ Privacy Settings
   [View Profile]

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

❓ Need Help?
/help - View all commands
/support - Contact support team
    """
    
    keyboard = [
        [InlineKeyboardButton("🔙 Back to Menu", callback_data="back_to_menu")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(text, reply_markup=reply_markup, parse_mode='Markdown')

async def menu_latest(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show latest courses (inline button)"""
    query = update.callback_query
    await query.answer()
    
    text = """
🆕 LATEST COURSES
═════════════════════════════════════════════════════════════════

🔥 Just Released:

1. 🛡️ Advanced Cybersecurity
   └─ Released: 2 days ago
   └─ ₹1299 | 🔥 Trending

2. 🤖 ChatGPT & AI Integration
   └─ Released: 5 days ago
   └─ ₹999 | 🆕 New

3. 📊 Data Science with Python
   └─ Released: 1 week ago
   └─ ₹1599 | ⭐ Popular

4. ☁️ Cloud Computing (AWS)
   └─ Released: 2 weeks ago
   └─ ₹1899 | ⭐⭐ Bestseller

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

💡 Limited Time: Get 20% OFF on all new courses!
    """
    
    keyboard = [
        [InlineKeyboardButton("🔙 Back to Menu", callback_data="back_to_menu")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(text, reply_markup=reply_markup, parse_mode='Markdown')

async def menu_statistics(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show user statistics (inline button)"""
    query = update.callback_query
    await query.answer()
    user = query.from_user
    
    text = f"""
📊 YOUR STATISTICS
═════════════════════════════════════════════════════════════════

👤 User Info:
   Name: {user.first_name}
   ID: {user.id}
   Username: @{user.username if user.username else 'Not set'}

📚 Your Courses:
   ✅ Total Purchased: 2 courses
   ✅ In Progress: 1 course
   ✅ Completed: 1 course

💰 Account Summary:
   Total Spent: ₹2498
   Active Subscriptions: 2
   Days Remaining: 365 days

⭐ Achievements:
   ✅ 5 Reviews Written
   ✅ Referred 3 Friends
   ✅ Earned ₹500 Referral Bonus

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📖 View your purchased courses: /mycourses
    """
    
    keyboard = [
        [InlineKeyboardButton("🔙 Back to Menu", callback_data="back_to_menu")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(text, reply_markup=reply_markup, parse_mode='Markdown')

async def menu_request(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Request a course (inline button)"""
    query = update.callback_query
    await query.answer()
    
    text = """
❓ REQUEST A COURSE
═════════════════════════════════════════════════════════════════

📝 Don't see your desired course?

We listen to our community! Request a new course and if it gets
enough votes, we'll create it for you!

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

How to Request:

1️⃣ Click the button below
2️⃣ Type the course name
3️⃣ Describe what you want to learn
4️⃣ Share your industry/experience level

📊 Top Requested Courses:
   1. Kubernetes & Docker - 145 votes
   2. Rust Programming - 98 votes
   3. Blockchain Dev - 87 votes
   4. GraphQL Mastery - 65 votes
   5. Microservices - 54 votes

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    """
    
    keyboard = [
        [InlineKeyboardButton("✉️ Send Request", callback_data="send_request")],
        [InlineKeyboardButton("🔙 Back to Menu", callback_data="back_to_menu")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(text, reply_markup=reply_markup, parse_mode='Markdown')

async def back_to_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Go back to main inline menu"""
    query = update.callback_query
    await query.answer()
    
    # Inline keyboard for main menu
    inline_keyboard = [
        [
            InlineKeyboardButton("📚 Courses", callback_data="menu_courses"),
            InlineKeyboardButton("🎬 Proof", callback_data="menu_proof")
        ],
        [
            InlineKeyboardButton("⚙️ Settings", callback_data="menu_settings"),
            InlineKeyboardButton("🆕 Latest Course", callback_data="menu_latest")
        ],
        [
            InlineKeyboardButton("📊 Statistics", callback_data="menu_statistics"),
            InlineKeyboardButton("❓ Request Course", callback_data="menu_request")
        ]
    ]
    
    inline_markup = InlineKeyboardMarkup(inline_keyboard)
    
    await query.edit_message_text(
        "🎯 **Quick Actions:**\n\nSelect what you want to do:",
        reply_markup=inline_markup,
        parse_mode='Markdown'
    )

# ==================== REPLY KEYBOARD HANDLERS ====================

async def handle_owner(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle Owner button (reply keyboard)"""
    text = """
👨‍💼 OWNER SECTION
═════════════════════════════════════════════════════════════════

🎯 Owner Control Panel

Welcome to the Owner Section! Here you can manage all aspects of your course business.

Use the buttons at the bottom to navigate:
📺 Course Channel - Main announcement channel
💬 Discussion - Community discussion group
📚 All Courses - Complete course catalog
🌐 Website - Official website
🎁 Donate - Support us
💸 Resell - Reseller program

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

💡 Tap any button below to get started!
    """
    
    await update.message.reply_text(text, parse_mode='Markdown')

async def handle_course_channel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle Course Channel button (reply keyboard)"""
    text = """
📺 COURSE CHANNEL
═════════════════════════════════════════════════════════════════

🎥 Join Our Telegram Channel:

@coursepro911 - Main Course Channel
   ✅ Latest course announcements
   ✅ Exclusive offers & discounts
   ✅ Learning tips & resources
   ✅ Community discussions

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📊 Channel Stats:
   Members: 5000+
   Posts: 500+
   Engagement: High

🔔 Enable Notifications to never miss updates!

🔗 Join here: https://t.me/coursepro911
    """
    
    keyboard = [
        [InlineKeyboardButton("🔗 Join Channel", url="https://t.me/coursepro911")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(text, reply_markup=reply_markup, parse_mode='Markdown')

async def handle_discussion(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle Discussion button (reply keyboard)"""
    text = """
💬 DISCUSSION COMMUNITY
═════════════════════════════════════════════════════════════════

🗣️ Join Our Discussion Community:

@coursepro_discussion - Main Discussion Group
   ✅ Ask questions & get instant answers
   ✅ Share resources & tips
   ✅ Discuss course content
   ✅ Network with fellow learners
   ✅ Get expert guidance

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

👥 Community Stats:
   Active Members: 2000+
   Daily Discussions: 50+
   Response Time: < 30 minutes

💡 Benefits:
   ✅ Free expert support
   ✅ Peer learning
   ✅ Job opportunities
   ✅ Exclusive networking

🔗 Join here: https://t.me/coursepro_discussion
    """
    
    keyboard = [
        [InlineKeyboardButton("💬 Join Discussion", url="https://t.me/coursepro_discussion")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(text, reply_markup=reply_markup, parse_mode='Markdown')

async def handle_all_courses(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle All Courses button (reply keyboard)"""
    text = """
📚 ALL COURSES
═════════════════════════════════════════════════════════════════

🎓 Complete Course Catalog:

🔐 Security Courses:
   • Cybersecurity Mastery
   • Ethical Hacking 101
   • Network Security Pro
   • Bug Bounty Hunting

💻 Development Courses:
   • Web Development Pro
   • Mobile App Development
   • Full Stack Mastery
   • DevOps Engineering

🤖 AI & Data:
   • AI & Machine Learning
   • Data Science Pro
   • Deep Learning
   • ChatGPT Integration

📱 Mobile Development:
   • Android Development
   • iOS Development
   • Flutter Mastery
   • React Native

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📊 Total: 20+ Courses | 10000+ Students | 98% Satisfaction
    """
    
    await update.message.reply_text(text, parse_mode='Markdown')

async def handle_website(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle Website button (reply keyboard)"""
    text = """
🌐 OFFICIAL WEBSITE
═════════════════════════════════════════════════════════════════

🏢 Visit Our Website:

www.coursepro911.com
   ✅ Browse all courses
   ✅ Read detailed course info
   ✅ Check instructor profiles
   ✅ View student testimonials
   ✅ Access learning resources
   ✅ Download certificates

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🔥 Website Features:
   ✅ Mobile friendly
   ✅ Live chat support
   ✅ Secure payment
   ✅ Progress tracking
   ✅ Certificate downloads
   ✅ Course forums

🔗 Visit: https://www.coursepro911.com
    """
    
    keyboard = [
        [InlineKeyboardButton("🌐 Visit Website", url="https://www.coursepro911.com")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(text, reply_markup=reply_markup, parse_mode='Markdown')

async def handle_donate(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle Donate button (reply keyboard)"""
    text = """
🎁 SUPPORT US - DONATE
═════════════════════════════════════════════════════════════════

❤️ Help Us Create Better Content:

Your donation helps us:
   ✅ Create more quality courses
   ✅ Improve platform features
   ✅ Provide better support
   ✅ Offer more scholarships
   ✅ Maintain free resources

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

💰 Donation Options:

   ₹100  - Bronze Supporter
   ₹500  - Silver Supporter  
   ₹1000 - Gold Supporter
   ₹5000 - Platinum Supporter

🎁 Donor Benefits:
   ✅ Special badge in community
   ✅ Priority support
   ✅ Exclusive resources
   ✅ Our gratitude email

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

❓ Alternative: Buy a course (best way to support us!) 💚
    """
    
    keyboard = [
        [InlineKeyboardButton("💚 Donate Now", callback_data="donate_now")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(text, reply_markup=reply_markup, parse_mode='Markdown')

async def handle_resell(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle Resell button (reply keyboard)"""
    text = """
💸 RESELL PROGRAM
═════════════════════════════════════════════════════════════════

🚀 Become a Reseller:

Earn money by reselling our courses!
   ✅ 40% commission on each sale
   ✅ Lifetime income on referrals
   ✅ Marketing materials provided
   ✅ Dedicated support
   ✅ Real-time analytics

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

💰 Earning Example:

   Course: ₹1000
   Your Commission (40%): ₹400
   Sell 10 courses/month: ₹4000 income
   Sell 100 courses/month: ₹40000 income!

✅ Top Resellers earn ₹100,000+ monthly!

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🎯 Requirements:
   ✅ Active in community
   ✅ Good communication skills
   ✅ Willingness to promote
   ✅ Commitment to quality

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    """
    
    keyboard = [
        [InlineKeyboardButton("📝 Apply Now", callback_data="resell_apply")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(text, reply_markup=reply_markup, parse_mode='Markdown')

# Handler mapping for remaining callbacks
async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle remaining callbacks"""
    query = update.callback_query
    callback_data = query.data
    
    # Simple responses for unimplemented features
    responses = {
        "send_request": "📝 Please describe the course you'd like us to create...",
        "donate_now": "💚 Thank you for your generosity! Donation link coming soon...",
        "resell_apply": "📝 Please fill out the reseller application form...",
    }
    
    if callback_data in responses:
        await query.answer()
        await query.edit_message_text(responses[callback_data])
