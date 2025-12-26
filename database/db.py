# 🛠️ Database Connection Pool & Query Manager

import asyncpg
import logging
from typing import Optional, List, Dict
from config import DatabaseConfig
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class Database:
    """PostgreSQL database connection manager with connection pooling"""
    
    def __init__(self):
        self.pool: Optional[asyncpg.Pool] = None
    
    async def connect(self):
        """Initialize database connection pool"""
        try:
            self.pool = await asyncpg.create_pool(
                dsn=DatabaseConfig.DATABASE_URL,
                min_size=10,
                max_size=20,
                command_timeout=60
            )
            logger.info("✅ Database connected")
            await self.create_tables()
        except Exception as e:
            logger.error(f"❌ Database connection failed: {e}")
            raise
    
    async def disconnect(self):
        """Close all database connections"""
        if self.pool:
            await self.pool.close()
            logger.info("✅ Database disconnected")
    
    async def execute(self, query: str, *args):
        """Execute a query (INSERT, UPDATE, DELETE)"""
        async with self.pool.acquire() as connection:
            return await connection.execute(query, *args)
    
    async def fetch(self, query: str, *args):
        """Fetch multiple rows"""
        async with self.pool.acquire() as connection:
            return await connection.fetch(query, *args)
    
    async def fetchrow(self, query: str, *args):
        """Fetch single row"""
        async with self.pool.acquire() as connection:
            return await connection.fetchrow(query, *args)
    
    async def fetchval(self, query: str, *args):
        """Fetch single value"""
        async with self.pool.acquire() as connection:
            return await connection.fetchval(query, *args)
    
    async def create_tables(self):
        """Create all necessary tables if they don't exist"""
        try:
            queries = [
                # Users table
                """
                CREATE TABLE IF NOT EXISTS users (
                    user_id BIGINT PRIMARY KEY,
                    username VARCHAR(255),
                    first_name VARCHAR(255),
                    last_name VARCHAR(255),
                    credits INTEGER DEFAULT 0,
                    is_verified BOOLEAN DEFAULT FALSE,
                    is_banned BOOLEAN DEFAULT FALSE,
                    is_premium BOOLEAN DEFAULT FALSE,
                    created_at TIMESTAMP DEFAULT NOW(),
                    last_active TIMESTAMP DEFAULT NOW()
                )
                """,
                
                # Admins table
                """
                CREATE TABLE IF NOT EXISTS admins (
                    user_id BIGINT PRIMARY KEY,
                    name VARCHAR(255),
                    role VARCHAR(50) DEFAULT 'admin',
                    permissions JSONB DEFAULT '{}',
                    added_at TIMESTAMP DEFAULT NOW(),
                    added_by BIGINT
                )
                """,
                
                # Force join channels table
                """
                CREATE TABLE IF NOT EXISTS force_join_channels (
                    channel_id BIGINT PRIMARY KEY,
                    username VARCHAR(255),
                    title VARCHAR(255),
                    added_at TIMESTAMP DEFAULT NOW()
                )
                """,
                
                # Broadcast history table
                """
                CREATE TABLE IF NOT EXISTS broadcast_history (
                    id SERIAL PRIMARY KEY,
                    message TEXT,
                    success_count INTEGER DEFAULT 0,
                    failed_count INTEGER DEFAULT 0,
                    sent_at TIMESTAMP DEFAULT NOW(),
                    sent_by BIGINT
                )
                """,
                
                # Credits history table
                """
                CREATE TABLE IF NOT EXISTS credits_history (
                    id SERIAL PRIMARY KEY,
                    user_id BIGINT,
                    amount INTEGER,
                    type VARCHAR(20),
                    reason TEXT,
                    created_at TIMESTAMP DEFAULT NOW(),
                    created_by BIGINT
                )
                """,
                
                # Content customization table
                """
                CREATE TABLE IF NOT EXISTS content_customization (
                    key VARCHAR(255) PRIMARY KEY,
                    value TEXT,
                    updated_at TIMESTAMP DEFAULT NOW()
                )
                """
            ]
            
            for query in queries:
                await self.execute(query)
            
            logger.info("✅ All tables created/verified")
            
        except Exception as e:
            logger.error(f"❌ Error creating tables: {e}")
    
    # ==================== USER METHODS ====================
    
    async def get_or_create_user(self, user_id: int, username: str = None, first_name: str = None, last_name: str = None) -> Dict:
        """Get user or create if doesn't exist"""
        try:
            user = await self.fetchrow(
                "SELECT * FROM users WHERE user_id = $1",
                user_id
            )
            
            if not user:
                await self.execute(
                    """INSERT INTO users (user_id, username, first_name, last_name) 
                       VALUES ($1, $2, $3, $4)""",
                    user_id, username, first_name, last_name
                )
                user = await self.fetchrow(
                    "SELECT * FROM users WHERE user_id = $1",
                    user_id
                )
            
            return dict(user)
        except Exception as e:
            logger.error(f"Error in get_or_create_user: {e}")
            return {}
    
    async def get_all_users(self) -> List[Dict]:
        """Get all users"""
        try:
            rows = await self.fetch("SELECT * FROM users ORDER BY created_at DESC")
            return [dict(row) for row in rows]
        except Exception as e:
            logger.error(f"Error getting all users: {e}")
            return []
    
    async def get_total_users(self) -> int:
        """Get total user count"""
        try:
            return await self.fetchval("SELECT COUNT(*) FROM users") or 0
        except Exception as e:
            logger.error(f"Error getting total users: {e}")
            return 0
    
    async def is_user_verified(self, user_id: int) -> bool:
        """Check if user is verified"""
        try:
            result = await self.fetchval(
                "SELECT is_verified FROM users WHERE user_id = $1",
                user_id
            )
            return result or False
        except Exception as e:
            logger.error(f"Error checking user verification: {e}")
            return False
    
    async def mark_user_verified(self, user_id: int):
        """Mark user as verified"""
        try:
            await self.execute(
                "UPDATE users SET is_verified = TRUE WHERE user_id = $1",
                user_id
            )
        except Exception as e:
            logger.error(f"Error marking user verified: {e}")
    
    async def get_user_stats(self) -> Dict:
        """Get user statistics"""
        try:
            total = await self.fetchval("SELECT COUNT(*) FROM users") or 0
            active_24h = await self.fetchval(
                "SELECT COUNT(*) FROM users WHERE last_active > NOW() - INTERVAL '24 hours'"
            ) or 0
            premium = await self.fetchval(
                "SELECT COUNT(*) FROM users WHERE is_premium = TRUE"
            ) or 0
            banned = await self.fetchval(
                "SELECT COUNT(*) FROM users WHERE is_banned = TRUE"
            ) or 0
            
            return {
                'total': total,
                'active_24h': active_24h,
                'premium': premium,
                'banned': banned
            }
        except Exception as e:
            logger.error(f"Error getting user stats: {e}")
            return {'total': 0, 'active_24h': 0, 'premium': 0, 'banned': 0}
    
    # ==================== ADMIN METHODS ====================
    
    async def get_admin(self, user_id: int) -> Optional[Dict]:
        """Get admin by user ID"""
        try:
            row = await self.fetchrow(
                "SELECT * FROM admins WHERE user_id = $1",
                user_id
            )
            return dict(row) if row else None
        except Exception as e:
            logger.error(f"Error getting admin: {e}")
            return None
    
    async def get_all_admins(self) -> List[Dict]:
        """Get all admins"""
        try:
            rows = await self.fetch("SELECT * FROM admins ORDER BY added_at DESC")
            return [dict(row) for row in rows]
        except Exception as e:
            logger.error(f"Error getting all admins: {e}")
            return []
    
    async def add_admin(self, user_id: int, name: str, role: str = 'admin', added_by: int = None):
        """Add new admin"""
        try:
            await self.execute(
                """INSERT INTO admins (user_id, name, role, added_by) 
                   VALUES ($1, $2, $3, $4) 
                   ON CONFLICT (user_id) DO UPDATE SET role = $3""",
                user_id, name, role, added_by
            )
        except Exception as e:
            logger.error(f"Error adding admin: {e}")
    
    async def remove_admin(self, user_id: int):
        """Remove admin"""
        try:
            await self.execute("DELETE FROM admins WHERE user_id = $1", user_id)
        except Exception as e:
            logger.error(f"Error removing admin: {e}")
    
    # ==================== FORCE JOIN METHODS ====================
    
    async def get_force_join_channels(self) -> List[Dict]:
        """Get all force join channels"""
        try:
            rows = await self.fetch("SELECT * FROM force_join_channels ORDER BY added_at DESC")
            return [dict(row) for row in rows]
        except Exception as e:
            logger.error(f"Error getting force join channels: {e}")
            return []
    
    async def add_force_join_channel(self, channel_id: int, username: str, title: str):
        """Add force join channel"""
        try:
            await self.execute(
                """INSERT INTO force_join_channels (channel_id, username, title) 
                   VALUES ($1, $2, $3) 
                   ON CONFLICT (channel_id) DO UPDATE SET username = $2, title = $3""",
                channel_id, username, title
            )
        except Exception as e:
            logger.error(f"Error adding force join channel: {e}")
    
    async def remove_force_join_channel(self, channel_id: int):
        """Remove force join channel"""
        try:
            await self.execute(
                "DELETE FROM force_join_channels WHERE channel_id = $1",
                channel_id
            )
        except Exception as e:
            logger.error(f"Error removing force join channel: {e}")
    
    # ==================== BROADCAST METHODS ====================
    
    async def save_broadcast_stats(self, message: str, success_count: int, failed_count: int, sent_by: int = None):
        """Save broadcast statistics"""
        try:
            await self.execute(
                """INSERT INTO broadcast_history (message, success_count, failed_count, sent_by) 
                   VALUES ($1, $2, $3, $4)""",
                message, success_count, failed_count, sent_by
            )
        except Exception as e:
            logger.error(f"Error saving broadcast stats: {e}")
    
    async def get_broadcast_history(self, limit: int = 10) -> List[Dict]:
        """Get broadcast history"""
        try:
            rows = await self.fetch(
                "SELECT * FROM broadcast_history ORDER BY sent_at DESC LIMIT $1",
                limit
            )
            return [dict(row) for row in rows]
        except Exception as e:
            logger.error(f"Error getting broadcast history: {e}")
            return []
    
    # ==================== CREDITS METHODS ====================
    
    async def add_credits(self, user_id: int, amount: int, reason: str = None, added_by: int = None):
        """Add credits to user"""
        try:
            await self.execute(
                "UPDATE users SET credits = credits + $1 WHERE user_id = $2",
                amount, user_id
            )
            await self.execute(
                """INSERT INTO credits_history (user_id, amount, type, reason, created_by) 
                   VALUES ($1, $2, 'add', $3, $4)""",
                user_id, amount, reason, added_by
            )
        except Exception as e:
            logger.error(f"Error adding credits: {e}")
    
    async def deduct_credits(self, user_id: int, amount: int, reason: str = None, deducted_by: int = None):
        """Deduct credits from user"""
        try:
            await self.execute(
                "UPDATE users SET credits = GREATEST(credits - $1, 0) WHERE user_id = $2",
                amount, user_id
            )
            await self.execute(
                """INSERT INTO credits_history (user_id, amount, type, reason, created_by) 
                   VALUES ($1, $2, 'deduct', $3, $4)""",
                user_id, -amount, reason, deducted_by
            )
        except Exception as e:
            logger.error(f"Error deducting credits: {e}")
    
    async def get_user_credits(self, user_id: int) -> int:
        """Get user credits"""
        try:
            result = await self.fetchval(
                "SELECT credits FROM users WHERE user_id = $1",
                user_id
            )
            return result or 0
        except Exception as e:
            logger.error(f"Error getting user credits: {e}")
            return 0
    
    # ==================== STATISTICS METHODS ====================
    
    async def get_bot_stats(self) -> Dict:
        """Get comprehensive bot statistics"""
        try:
            total_users = await self.fetchval("SELECT COUNT(*) FROM users") or 0
            active_today = await self.fetchval(
                "SELECT COUNT(*) FROM users WHERE last_active::date = CURRENT_DATE"
            ) or 0
            new_users_week = await self.fetchval(
                "SELECT COUNT(*) FROM users WHERE created_at > NOW() - INTERVAL '7 days'"
            ) or 0
            
            return {
                'total_users': total_users,
                'active_today': active_today,
                'new_users_week': new_users_week,
                'total_courses': 0,  # Implement when course table exists
                'total_revenue': 0,  # Implement when payment table exists
                'pending_orders': 0  # Implement when order table exists
            }
        except Exception as e:
            logger.error(f"Error getting bot stats: {e}")
            return {
                'total_users': 0,
                'active_today': 0,
                'new_users_week': 0,
                'total_courses': 0,
                'total_revenue': 0,
                'pending_orders': 0
            }
    
    # ==================== CONTENT CUSTOMIZATION ====================
    
    async def get_custom_content(self, key: str) -> Optional[str]:
        """Get custom content by key"""
        try:
            result = await self.fetchval(
                "SELECT value FROM content_customization WHERE key = $1",
                key
            )
            return result
        except Exception as e:
            logger.error(f"Error getting custom content: {e}")
            return None
    
    async def set_custom_content(self, key: str, value: str):
        """Set custom content"""
        try:
            await self.execute(
                """INSERT INTO content_customization (key, value) 
                   VALUES ($1, $2) 
                   ON CONFLICT (key) DO UPDATE SET value = $2, updated_at = NOW()""",
                key, value
            )
        except Exception as e:
            logger.error(f"Error setting custom content: {e}")


# Global database instance
db = Database()
