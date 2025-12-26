# 🔐 Premium Admin Dashboard - Complete Guide

## 📋 Table of Contents
1. [Overview](#overview)
2. [Features](#features)
3. [Setup](#setup)
4. [Using the Dashboard](#using-the-dashboard)
5. [Feature Guides](#feature-guides)
6. [Configuration](#configuration)
7. [Troubleshooting](#troubleshooting)

---

## 🎯 Overview

The Premium Admin Dashboard is a comprehensive control panel that gives you complete control over your Telegram course bot. Manage users, content, broadcasts, and more - all from within Telegram!

**Access Command:** `/admin`

---

## ✨ Features

### 🔹 Core Features

1. **📢 Broadcast System**
   - Send messages to all users
   - Rich text formatting (Bold, Italic, Code)
   - Media support (Photos, Videos, Files)
   - Target specific user groups
   - Schedule broadcasts
   - Real-time delivery stats

2. **👥 User Management**
   - View all users
   - Search users by ID/username
   - Ban/unban users
   - View user activity
   - Export user list
   - User statistics dashboard

3. **💰 Credits Management**
   - Add credits to users
   - Deduct credits from users
   - View credit history
   - Set credit expiry
   - Bulk credit operations
   - Credit statistics

4. **🔒 Force Join System**
   - Add unlimited channels/groups
   - Automatic membership verification
   - Custom join messages
   - Block access until joined
   - Join statistics tracking

5. **👑 Admin Management**
   - Add new admins
   - Remove admins
   - Set admin roles (Super Admin, Admin, Moderator)
   - Manage permissions
   - Activity logs

6. **✏️ Content Editor**
   - Customize welcome message
   - Edit help text
   - Modify course templates
   - Edit payment messages
   - Change button labels
   - Multi-language support

7. **🤖 AI Assistant**
   - Generate course descriptions
   - Create marketing content
   - Write broadcast messages
   - Analyze user behavior
   - Content translation
   - SEO optimization

8. **📊 Analytics**
   - User growth charts
   - Revenue analytics
   - Course popularity
   - Engagement metrics
   - Custom reports

9. **⚙️ Settings**
   - Payment gateway config
   - Bot behavior settings
   - Notification settings
   - Backup/restore

10. **📦 Order Management**
    - View all orders
    - Pending orders
    - Order verification
    - Refund management

---

## 🚀 Setup

### Step 1: Add Your User ID as Admin

```python
# Run this command in your PostgreSQL database:
INSERT INTO admins (user_id, name, role) 
VALUES (YOUR_USER_ID, 'Your Name', 'super_admin');
```

**To get your User ID:**
1. Send any message to your bot
2. Check the logs (`logs/bot.log`)
3. Find your user ID in the logs

### Step 2: Configure Force Join (Optional)

If you want to require users to join channels:

1. Send `/admin` to your bot
2. Click **🔒 Force Join**
3. Click **➕ Add Channel**
4. Send the channel username (e.g., `@yourchannel`)

### Step 3: Test Access

1. Send `/admin` to your bot
2. You should see the admin dashboard
3. Explore all features!

---

## 🎮 Using the Dashboard

### Accessing the Dashboard

Send `/admin` to your bot. You'll see:

```
👑 ADMIN DASHBOARD
═══════════════════════════════════════

📊 Bot Statistics:
   • Total Users: 150
   • Active Today: 45
   • New Users (7d): 23
   • Total Courses: 12
   • Total Revenue: ₹50,000
   • Pending Orders: 3

🕒 Last Updated: 26/12/2025 20:30

═══════════════════════════════════════

Select an option below to manage:

[📢 Broadcast] [👥 Users]
[📚 Courses] [💰 Credits]
[🔒 Force Join] [👑 Admins]
[✏️ Content Editor] [🤖 AI Assistant]
[📊 Analytics] [⚙️ Settings]
[📦 Orders] [🎨 Customize]
[🔄 Refresh Stats]
```

---

## 📖 Feature Guides

### 📢 Broadcast System

**How to Send a Broadcast:**

1. Click **📢 Broadcast**
2. Click **📝 Create Broadcast**
3. Type or send your message
   - Text messages
   - Photos with captions
   - Videos with captions
4. Preview your message
5. Choose target audience:
   - All Users
   - Active Users
   - Premium Users
   - Custom List
6. Click **✅ Send Now** or **⏰ Schedule**

**Formatting Tips:**
- `*bold*` for **bold text**
- `_italic_` for *italic text*
- `` `code` `` for `monospace`
- `[link](URL)` for hyperlinks

**Example Broadcast:**
```
🎉 *NEW COURSE ALERT!*

We just launched our _Advanced Cybersecurity_ course!

💰 Special Price: `₹999` (Limited Time)

[Enroll Now](https://t.me/yourchannel)
```

---

### 👥 User Management

**View All Users:**
1. Click **👥 Users**
2. Click **📋 All Users**

**Search for a User:**
1. Click **👥 Users**
2. Click **🔍 Search User**
3. Enter user ID or username

**Ban a User:**
1. Search for the user
2. Click **🚫 Ban User**
3. Confirm action

**View User Activity:**
1. Click **👥 Users**
2. Click **📊 Activity Log**

---

### 💰 Credits Management

**Add Credits to User:**

1. Click **💰 Credits**
2. Click **➕ Add Credits**
3. Enter user ID
4. Enter amount
5. Enter reason (optional)
6. Confirm

**Deduct Credits:**

1. Click **💰 Credits**
2. Click **➖ Deduct Credits**
3. Follow same steps

**View Credit History:**

1. Click **💰 Credits**
2. Click **📜 Credit History**
3. Filter by user or date

---

### 🔒 Force Join Management

**Add a Required Channel:**

1. Click **🔒 Force Join**
2. Click **➕ Add Channel**
3. Make your bot an admin in the channel
4. Send channel username (e.g., `@yourchannel`)
5. Confirm

**How It Works:**
- When new users send `/start`, they see join buttons
- All features are blocked until they join
- After joining, they click "I Joined - Verify Now"
- Bot automatically verifies membership
- Full access granted after verification

**Remove a Channel:**

1. Click **🔒 Force Join**
2. Click **🗑️ Remove Channel**
3. Select channel to remove

---

### 👑 Admin Management

**Add New Admin:**

1. Click **👑 Admins**
2. Click **➕ Add Admin**
3. Send user ID of new admin
4. Select role:
   - 🔴 Super Admin (Full access)
   - 🟡 Admin (Limited access)
   - 🟢 Moderator (Basic access)
5. Confirm

**Admin Permissions:**

| Permission | Super Admin | Admin | Moderator |
|------------|-------------|-------|----------|
| Broadcast | ✅ | ✅ | ❌ |
| User Management | ✅ | ✅ | ✅ |
| Credits | ✅ | ✅ | ❌ |
| Force Join | ✅ | ❌ | ❌ |
| Admin Management | ✅ | ❌ | ❌ |
| Content Editor | ✅ | ✅ | ❌ |
| AI Assistant | ✅ | ✅ | ✅ |
| Analytics | ✅ | ✅ | ✅ |
| Settings | ✅ | ❌ | ❌ |

---

### ✏️ Content Editor

**Edit Welcome Message:**

1. Click **✏️ Content Editor**
2. Click **📝 Welcome Message**
3. Type new welcome message
4. Preview
5. Save

**Customize Button Labels:**

1. Click **✏️ Content Editor**
2. Click **🔘 Button Labels**
3. Select button to edit
4. Enter new label
5. Save

**Available Customizations:**
- Welcome message
- Help text
- Course templates
- Payment messages
- Success/error messages
- Button labels
- Menu texts

---

### 🤖 AI Assistant

**Generate Course Description:**

1. Click **🤖 AI Assistant**
2. Click **✍️ Generate Content**
3. Select **Course Description**
4. Enter course topic
5. AI generates professional description
6. Edit if needed
7. Use in your bot

**Create Marketing Content:**

1. Click **🤖 AI Assistant**
2. Click **📈 Marketing Ideas**
3. AI suggests promotional strategies

**Translate Content:**

1. Click **🤖 AI Assistant**
2. Click **🌍 Translate**
3. Select source and target language
4. Enter text
5. Get translation

**Custom AI Prompt:**

1. Click **🤖 AI Assistant**
2. Click **📝 Custom Prompt**
3. Type your question or request
4. Get AI response

---

## ⚙️ Configuration

### Database Configuration

Edit `config.py`:

```python
class DatabaseConfig:
    DATABASE_URL = "postgresql://user:pass@host:port/dbname"
```

### Bot Configuration

Edit `config.py`:

```python
class BotConfig:
    TELEGRAM_BOT_TOKEN = "your_bot_token_here"
    ADMIN_IDS = [123456789]  # List of super admin user IDs
```

---

## 🐛 Troubleshooting

### "Access Denied" Error

**Problem:** You can't access the admin dashboard.

**Solution:**
1. Check if your user ID is in the `admins` table
2. Run: `SELECT * FROM admins WHERE user_id = YOUR_ID;`
3. If not found, add yourself manually

### Force Join Not Working

**Problem:** Users can access bot without joining channels.

**Solution:**
1. Make your bot an admin in all required channels
2. Check bot has permission to view members
3. Verify channel IDs are correct in database

### Broadcast Failing

**Problem:** Broadcast messages not delivered.

**Solution:**
1. Check bot token is valid
2. Some users may have blocked the bot
3. Check logs for specific errors
4. Verify database connection

### Credits Not Updating

**Problem:** User credits not changing.

**Solution:**
1. Check database connection
2. Verify credits table exists
3. Check transaction logs
4. Ensure no negative balance

### Database Connection Error

**Problem:** Bot can't connect to database.

**Solution:**
1. Verify `DATABASE_URL` in config
2. Check PostgreSQL is running
3. Verify credentials
4. Check firewall settings

---

## 📞 Support

For issues or questions:

1. Check logs: `logs/bot.log`
2. Review this guide
3. Check GitHub issues
4. Contact: @avikmaji (Telegram)

---

## 🔄 Updates

**Version:** 2.0.0  
**Last Updated:** December 26, 2025  
**Changelog:**
- ✅ Premium admin dashboard
- ✅ Force join system
- ✅ Broadcast system
- ✅ Credits management
- ✅ AI assistant integration
- ✅ Content customization
- ✅ Enhanced analytics

---

## 📜 License

This admin dashboard is part of the Course Pro Bot.  
Built with ❤️ by [Avik Maji](https://github.com/alexavik)

---

**⚠️ Security Note:**
- Never share your bot token
- Never share your database credentials
- Regularly backup your database
- Use strong passwords
- Limit admin access to trusted users

**🎉 Enjoy your Premium Admin Dashboard!**
