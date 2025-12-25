# PREMIUM MODELS & UTILITIES

# ════════════════════════════════════════════════════════════════════

# models/course.py
"""Professional course database model with advanced features"""

from datetime import datetime

class Course:
    """Course database model with ORM-like operations"""
    
    def __init__(self, id=None, title=None, description=None, category=None, 
                 price=None, demo_video_id=None, ai_caption=None, 
                 channel_post_id=None, rating=5.0, reviews=0):
        self.id = id
        self.title = title
        self.description = description
        self.category = category
        self.price = price
        self.demo_video_id = demo_video_id
        self.ai_caption = ai_caption
        self.channel_post_id = channel_post_id
        self.rating = rating
        self.reviews = reviews
        self.created_at = datetime.now()
        self.updated_at = datetime.now()
        self.deleted_at = None
    
    async def save(self, db):
        """Save course to database"""
        if self.id:
            # Update existing
            query = """
            UPDATE courses SET title=$2, description=$3, category=$4,
            price=$5, demo_video_id=$6, ai_caption=$7, channel_post_id=$8,
            updated_at=NOW() WHERE id=$1
            """
            await db.execute(query, self.id, self.title, self.description,
                           self.category, self.price, self.demo_video_id,
                           self.ai_caption, self.channel_post_id)
        else:
            # Create new
            query = """
            INSERT INTO courses (title, description, category, price,
            demo_video_id, ai_caption, channel_post_id)
            VALUES ($1, $2, $3, $4, $5, $6, $7)
            RETURNING id
            """
            self.id = await db.fetchval(query, self.title, self.description,
                                       self.category, self.price, 
                                       self.demo_video_id, self.ai_caption,
                                       self.channel_post_id)
        return self.id
    
    @classmethod
    async def get_by_id(cls, db, course_id: int):
        """Fetch course by ID"""
        query = "SELECT * FROM courses WHERE id=$1 AND deleted_at IS NULL"
        row = await db.fetchrow(query, course_id)
        if row:
            return cls(**dict(row))
        return None
    
    @classmethod
    async def get_all(cls, db, limit=50, offset=0):
        """Fetch all active courses"""
        query = """
        SELECT * FROM courses 
        WHERE deleted_at IS NULL 
        ORDER BY created_at DESC 
        LIMIT $1 OFFSET $2
        """
        rows = await db.fetch(query, limit, offset)
        return [cls(**dict(row)) for row in rows]
    
    async def delete(self, db):
        """Soft delete course"""
        query = "UPDATE courses SET deleted_at=NOW() WHERE id=$1"
        await db.execute(query, self.id)

# ════════════════════════════════════════════════════════════════════

# models/order.py
"""Professional order database model"""

from datetime import datetime

class Order:
    """Order/Purchase database model"""
    
    def __init__(self, id=None, user_id=None, user_name=None, course_id=None,
                 price=None, payment_status='pending', transaction_id=None):
        self.id = id
        self.user_id = user_id
        self.user_name = user_name
        self.course_id = course_id
        self.price = price
        self.payment_status = payment_status  # pending, completed, failed
        self.transaction_id = transaction_id
        self.created_at = datetime.now()
        self.updated_at = datetime.now()
    
    async def save(self, db):
        """Save order to database"""
        if self.id:
            query = """
            UPDATE orders SET payment_status=$2, updated_at=NOW()
            WHERE id=$1
            """
            await db.execute(query, self.id, self.payment_status)
        else:
            query = """
            INSERT INTO orders (user_id, user_name, course_id, price, 
            payment_status, transaction_id)
            VALUES ($1, $2, $3, $4, $5, $6)
            RETURNING id
            """
            self.id = await db.fetchval(query, self.user_id, self.user_name,
                                       self.course_id, self.price,
                                       self.payment_status, self.transaction_id)
        return self.id
    
    @classmethod
    async def get_by_user_and_course(cls, db, user_id: int, course_id: int):
        """Check if user already bought course"""
        query = """
        SELECT * FROM orders 
        WHERE user_id=$1 AND course_id=$2 AND payment_status='completed'
        """
        row = await db.fetchrow(query, user_id, course_id)
        return cls(**dict(row)) if row else None
    
    @classmethod
    async def get_user_orders(cls, db, user_id: int):
        """Get all user purchases"""
        query = """
        SELECT * FROM orders 
        WHERE user_id=$1 AND payment_status='completed'
        ORDER BY created_at DESC
        """
        rows = await db.fetch(query, user_id)
        return [cls(**dict(row)) for row in rows]

# ════════════════════════════════════════════════════════════════════

# models/wishlist.py
"""Professional wishlist database model"""

class Wishlist:
    """User wishlist model"""
    
    def __init__(self, id=None, user_id=None, course_id=None):
        self.id = id
        self.user_id = user_id
        self.course_id = course_id
    
    async def add(self, db):
        """Add course to wishlist"""
        query = """
        INSERT INTO wishlist (user_id, course_id)
        VALUES ($1, $2)
        ON CONFLICT (user_id, course_id) DO NOTHING
        RETURNING id
        """
        self.id = await db.fetchval(query, self.user_id, self.course_id)
        return self.id
    
    async def remove(self, db):
        """Remove from wishlist"""
        query = "DELETE FROM wishlist WHERE user_id=$1 AND course_id=$2"
        await db.execute(query, self.user_id, self.course_id)
    
    @classmethod
    async def is_wishlisted(cls, db, user_id: int, course_id: int):
        """Check if course in wishlist"""
        query = """
        SELECT id FROM wishlist 
        WHERE user_id=$1 AND course_id=$2
        """
        return await db.fetchval(query, user_id, course_id)
    
    @classmethod
    async def get_user_wishlist(cls, db, user_id: int):
        """Get all user wishlist items"""
        query = """
        SELECT * FROM wishlist 
        WHERE user_id=$1 
        ORDER BY created_at DESC
        """
        rows = await db.fetch(query, user_id)
        return [cls(**dict(row)) for row in rows]

# ════════════════════════════════════════════════════════════════════

# database/db.py
"""Professional database connection pool management"""

import asyncpg
import logging
from config import DatabaseConfig

logger = logging.getLogger(__name__)

class Database:
    """Async PostgreSQL database connection pool"""
    
    _pool = None
    
    @classmethod
    async def initialize(cls):
        """Initialize connection pool"""
        if cls._pool is None:
            try:
                cls._pool = await asyncpg.create_pool(
                    DatabaseConfig.DATABASE_URL,
                    min_size=DatabaseConfig.MIN_CONNECTIONS,
                    max_size=DatabaseConfig.MAX_CONNECTIONS,
                    command_timeout=DatabaseConfig.COMMAND_TIMEOUT
                )
                logger.info("✅ Database connection pool initialized")
            except Exception as e:
                logger.error(f"❌ Database connection failed: {e}")
                raise
    
    @classmethod
    async def close(cls):
        """Close connection pool"""
        if cls._pool:
            await cls._pool.close()
            cls._pool = None
            logger.info("✅ Database connection pool closed")
    
    @classmethod
    async def execute(cls, query, *args):
        """Execute query without returning results"""
        async with cls._pool.acquire() as connection:
            await connection.execute(query, *args)
    
    @classmethod
    async def fetch(cls, query, *args):
        """Fetch multiple rows"""
        async with cls._pool.acquire() as connection:
            return await connection.fetch(query, *args)
    
    @classmethod
    async def fetchrow(cls, query, *args):
        """Fetch single row"""
        async with cls._pool.acquire() as connection:
            return await connection.fetchrow(query, *args)
    
    @classmethod
    async def fetchval(cls, query, *args):
        """Fetch single value"""
        async with cls._pool.acquire() as connection:
            return await connection.fetchval(query, *args)

# ════════════════════════════════════════════════════════════════════

# utils/decorators.py
"""Advanced decorators for admin checks and rate limiting"""

import logging
from functools import wraps
from telegram.ext import ContextTypes
from config import BotConfig

logger = logging.getLogger(__name__)

def admin_only(func):
    """Decorator to check admin authorization"""
    @wraps(func)
    async def wrapper(update, context: ContextTypes.DEFAULT_TYPE, *args, **kwargs):
        user_id = update.effective_user.id
        
        if user_id not in BotConfig.ADMIN_USER_IDS:
            logger.warning(f"⚠️ Unauthorized access attempt by user {user_id}")
            if update.message:
                await update.message.reply_text("❌ You don't have permission to use this command.")
            return
        
        logger.info(f"✅ Admin {user_id} executed: {func.__name__}")
        return await func(update, context, *args, **kwargs)
    
    return wrapper

def rate_limit(max_calls: int = 5, time_window: int = 60):
    """Decorator to rate limit function calls"""
    def decorator(func):
        user_calls = {}
        
        @wraps(func)
        async def wrapper(update, context: ContextTypes.DEFAULT_TYPE, *args, **kwargs):
            user_id = update.effective_user.id
            now = asyncio.get_event_loop().time()
            
            if user_id not in user_calls:
                user_calls[user_id] = []
            
            # Remove old calls outside time window
            user_calls[user_id] = [t for t in user_calls[user_id] if now - t < time_window]
            
            if len(user_calls[user_id]) >= max_calls:
                logger.warning(f"⚠️ Rate limit exceeded for user {user_id}")
                await update.message.reply_text(f"⏳ Too many requests. Please wait {time_window}s before trying again.")
                return
            
            user_calls[user_id].append(now)
            return await func(update, context, *args, **kwargs)
        
        return wrapper
    return decorator

# ════════════════════════════════════════════════════════════════════

# utils/validators.py
"""Advanced input validation for all user inputs"""

import re
from config import ValidationRules, CourseConfig

def validate_title(title: str) -> tuple:
    """Validate course title"""
    if not title or len(title) < ValidationRules.TITLE_MIN:
        return False, f"Title too short (min {ValidationRules.TITLE_MIN} chars)"
    
    if len(title) > ValidationRules.TITLE_MAX:
        return False, f"Title too long (max {ValidationRules.TITLE_MAX} chars)"
    
    if not re.match(r"^[a-zA-Z0-9\s\-_()&.,]+$", title):
        return False, "Title contains invalid characters"
    
    return True, "Valid"

def validate_description(desc: str) -> tuple:
    """Validate course description"""
    if not desc or len(desc) < ValidationRules.DESC_MIN:
        return False, f"Description too short (min {ValidationRules.DESC_MIN} chars)"
    
    if len(desc) > ValidationRules.DESC_MAX:
        return False, f"Description too long (max {ValidationRules.DESC_MAX} chars)"
    
    return True, "Valid"

def validate_price(price: float) -> tuple:
    """Validate course price"""
    if price < ValidationRules.PRICE_MIN:
        return False, f"Price too low (min ₹{ValidationRules.PRICE_MIN})"
    
    if price > ValidationRules.PRICE_MAX:
        return False, f"Price too high (max ₹{ValidationRules.PRICE_MAX})"
    
    if price % 1 != 0 and price % 0.50 != 0:
        return False, "Price must be in increments of ₹0.50"
    
    return True, "Valid"

def validate_category(category: str) -> tuple:
    """Validate course category"""
    if category not in CourseConfig.CATEGORIES:
        return False, f"Invalid category. Choose from: {', '.join(CourseConfig.CATEGORIES.keys())}"
    
    return True, "Valid"

def validate_email(email: str) -> tuple:
    """Validate email address"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(pattern, email):
        return False, "Invalid email format"
    
    return True, "Valid"

def sanitize_input(text: str) -> str:
    """Sanitize user input to prevent injection"""
    # Remove potentially harmful characters
    text = text.replace('<', '&lt;').replace('>', '&gt;')
    text = text.replace('"', '&quot;').replace("'", '&#39;')
    return text.strip()
