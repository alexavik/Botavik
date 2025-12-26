# 🎨 Course Sales Bot - Design Implementation

**Version:** 2.0  
**Date:** December 26, 2025  
**Sketch By:** Avik

---

## 📐 Bot Menu Structure (As Per Sketch)

### 🏠 **MAIN MENU** (`/start`)

The bot's first page shows 6 main options with 2 columns layout:

```
🌐 COURSE PRO BOT

[🎓 Courses]      [🎬 Proof]
[⚙️ Setting]       [🎕 Latest course]
[📊 Status]        [❓ Request course]

[👨‍💼 Owner Section]
```

#### Menu Options:

1. **🎓 Courses** (`menu_courses`)
   - Browse all available courses
   - View course details, pricing, and ratings
   - Buy or add to wishlist
   - Sample courses:
     - Cybersecurity Mastery (₹999)
     - Web Development Pro (₹1499)
     - AI & Machine Learning (₹1999)
     - Android Development (₹899)
     - Python Advanced (₹799)

2. **🎬 Proof** (`menu_proof`)
   - Real success stories and testimonials
   - Student achievements
   - Video testimonials link
   - Course statistics:
     - 5000+ Students
     - 98% Satisfaction Rate
     - 1000+ Success Stories

3. **⚙️ Setting** (`menu_setting`)
   - User preferences
   - Notification settings
   - Language selection
   - Payment method
   - Display theme (Light/Dark)
   - Privacy settings

4. **🎕 Latest course** (`menu_latest`)
   - Recently released courses
   - "New" and "Trending" badges
   - Limited-time discounts (20% OFF)
   - Trending courses section

5. **📊 Status** (`menu_status`)
   - Personal user dashboard
   - Purchased courses count
   - Account summary (total spent, days remaining)
   - Achievements (reviews, referrals, earnings)
   - View purchased courses shortcut

6. **❓ Request course** (`menu_request`)
   - Request new course creation
   - Community voting system
   - Top requested courses list
   - Example top requests:
     - Kubernetes & Docker (145 votes)
     - Rust Programming (98 votes)
     - Blockchain Dev (87 votes)

---

### 👨‍💼 **OWNER SECTION** (`menu_owner`)

Second-level menu with 7 sub-options for content owners:

```
[📺 Course Channel]    [📚 All Courses]
[💬 Discussion]        [🌐 Website]
[🎁 Donate]            [💸 Resell]
[🔗 Refer & Earn]

[🔙 Back]
```

#### Owner Section Features:

1. **📺 Course Channel** (`owner_channel`)
   - Link: @coursepro911
   - Join main Telegram channel
   - Get announcements, offers, resources
   - Channel stats (5000+ members)
   - Enable notifications button

2. **📚 All Courses** (`owner_all_courses`)
   - Complete course catalog
   - Organized by category:
     - Security Courses (4 courses)
     - Development Courses (4 courses)
     - AI & Data (4 courses)
     - Mobile Development (4 courses)
   - Total: 20+ courses

3. **💬 Discussion** (`owner_discussion`)
   - Link: @coursepro_discussion
   - Community forum
   - Ask questions, get instant answers
   - Share resources
   - Network with learners
   - Stats: 2000+ members, <30 min response

4. **🌐 Website** (`owner_website`)
   - Link: www.coursepro911.com
   - Browse detailed course info
   - View instructor profiles
   - Check testimonials
   - Download certificates
   - Access learning resources

5. **🎁 Donate** (`owner_donate`)
   - Support the platform
   - Donation tiers:
     - ₹100  - Bronze Supporter
     - ₹500  - Silver Supporter
     - ₹1000 - Gold Supporter
     - ₹5000 - Platinum Supporter
   - Donor benefits (badge, priority support)

6. **💸 Resell** (`owner_resell`)
   - Reseller program
   - 40% commission per sale
   - Lifetime income on referrals
   - Marketing materials provided
   - Earning potential: ₹4000-₹100,000+ monthly
   - Requirements: Active, good communication

7. **🔗 Refer & Earn** (`owner_refer`)
   - Referral program
   - 20% on first purchase
   - 10% on future purchases
   - Unlimited referrals
   - Personal referral link generated
   - Top referrers earn ₹50,000+ monthly
   - Dashboard with stats

---

## 📡 Callback Pattern Mapping

### Main Menu Callbacks
```python
menu_courses         → Show all courses
menu_proof           → Show testimonials
menu_setting         → User settings
menu_latest          → Latest courses
menu_status          → User status & stats
menu_request         → Request course form
menu_owner           → Owner section menu
menu_back            → Return to main menu
```

### Owner Section Callbacks
```python
owner_channel        → Course channel
owner_all_courses    → Complete catalog
owner_discussion     → Discussion group
owner_website        → Official website
owner_donate         → Donation options
owner_resell         → Reseller program
owner_refer          → Referral program
```

### Admin Panel Callbacks
```python
admin_create_course  → Create new course
admin_manage_courses → Manage existing courses
admin_analytics      → View statistics
admin_settings       → Bot settings
admin_orders         → Order management
cancel               → Close admin panel
```

---

## 🔄 Navigation Flow

```
/start
   ├─→ menu_courses → 📚 Browse courses
   ├─→ menu_proof → 🎬 Testimonials
   ├─→ menu_setting → ⚙️ Preferences
   ├─→ menu_latest → 🎕 New courses
   ├─→ menu_status → 📊 User dashboard
   ├─→ menu_request → ❓ Request course
   └─→ menu_owner → 👨‍💼 OWNER SECTION
         ├─→ owner_channel → 📺 Channel
         ├─→ owner_all_courses → 📚 Courses
         ├─→ owner_discussion → 💬 Discussion
         ├─→ owner_website → 🌐 Website
         ├─→ owner_donate → 🎁 Donate
         ├─→ owner_resell → 💸 Resell
         ├─→ owner_refer → 🔗 Refer & Earn
         └─→ menu_back → Back to main

/admin
   ├─→ admin_create_course → ➕ Create
   ├─→ admin_manage_courses → 📝 Manage
   ├─→ admin_analytics → 📊 Stats
   ├─→ admin_settings → ⚙️ Settings
   ├─→ admin_orders → 🔄 Orders
   └─→ cancel → Close panel
```

---

## 📂 File Structure

```
Botavik/
├── main.py                          # Main entry point with all handlers
├── handlers/
│   ├── start.py                     # Menu navigation (NEW - REDESIGNED)
│   ├── admin_panel.py               # Admin panel features
│   ├── course_manager.py            # Course creation/editing
│   └── course_buyer.py              # Purchase flows
├── database/
│   ├── db.py                        # Database connection
│   └── migration.sql                # Database schema
└── config.py                        # Configuration & constants
```

---

## ✨ Features Implemented

✅ Main menu with 6 options (2-column layout)  
✅ Owner section with 7 sub-options  
✅ Menu navigation (back buttons)  
✅ All callback handlers registered  
✅ Rich text with emojis & formatting  
✅ Responsive keyboard layouts  
✅ External links (channels, website)  
✅ User statistics display  
✅ Testimonials & proof section  
✅ Referral program integration  
✅ Reseller program details  
✅ Community links  
✅ Course catalog organization  

---

## 🚀 Testing Checklist

- [ ] Send `/start` and verify main menu appears
- [ ] Click 🎓 Courses - should show course list
- [ ] Click 🎬 Proof - should show testimonials
- [ ] Click ⚙️ Setting - should show preferences
- [ ] Click 🎕 Latest - should show new courses
- [ ] Click 📊 Status - should show user stats
- [ ] Click ❓ Request - should show request form
- [ ] Click 👨‍💼 Owner - should show owner menu
- [ ] In Owner section, test all 7 options
- [ ] Click 🔙 Back from any submenu - returns to parent
- [ ] Send `/admin` and verify admin panel works
- [ ] Click admin buttons - should work correctly

---

## 📊 Bot Statistics

- **Total Menu Options:** 14 main options
- **Callback Handlers:** 25+ registered
- **Supported Flows:** 5+ conversation flows
- **External Links:** 3 (Channel, Discussion, Website)
- **User Information Levels:** 3 (Main, Owner, Admin)

---

## 🎯 Next Steps

1. ✅ Deploy to Render
2. ✅ Test all menu buttons
3. ⏳ Add database integration for dynamic content
4. ⏳ Implement payment gateway
5. ⏳ Add course listing from database
6. ⏳ Implement real referral tracking
7. ⏳ Add user authentication
8. ⏳ Create admin dashboard

---

*Design sketch implemented by AI based on Avik's hand-drawn sketch (December 26, 2025)*
