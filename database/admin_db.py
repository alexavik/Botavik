# Admin Database Methods
# Comprehensive database operations for admin panel

import asyncpg
import logging
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
from database.db import db

logger = logging.getLogger(__name__)

class AdminDatabase:
    """Admin-specific database operations"""
    
    # ==================== ADMIN MANAGEMENT ====================
    
    @staticmethod
    async def is_admin(user_id: int) -> bool:
        """Check if user is admin"""
        try:
            query = "SELECT EXISTS(SELECT 1 FROM admins WHERE user_id = $1 AND active = true)"
            result = await db.fetchval(query, user_id)
            return result if result else False
        except Exception as e:
            logger.error(f"Error checking admin status: {e}")
            return False
    
    @staticmethod
    async def add_admin(user_id: int, name: str, role: str = 'admin', added_by: int = None) -> bool:
        """Add new admin user"""
        try:
            query = """
                INSERT INTO admins (user_id, name, role, added_by, added_at, active)
                VALUES ($1, $2, $3, $4, $5, true)
                ON CONFLICT (user_id) DO UPDATE SET active = true
                RETURNING id
            """
            result = await db.fetchval(query, user_id, name, role, added_by, datetime.now())
            logger.info(f"✅ Admin added: {user_id} ({name})")
            return True if result else False
        except Exception as e:
            logger.error(f"Error adding admin: {e}")
            return False
    
    @staticmethod
    async def remove_admin(user_id: int) -> bool:
        """Remove admin privileges"""
        try:
            query = "UPDATE admins SET active = false WHERE user_id = $1"
            await db.execute(query, user_id)
            logger.info(f"✅ Admin removed: {user_id}")
            return True
        except Exception as e:
            logger.error(f"Error removing admin: {e}")
            return False
    
    @staticmethod
    async def get_all_admins() -> List[Dict[str, Any]]:
        """Get all admins"""
        try:
            query = """
                SELECT user_id, name, role, added_at, active
                FROM admins
                WHERE active = true
                ORDER BY added_at DESC
            """
            rows = await db.fetch(query)
            return [dict(row) for row in rows]
        except Exception as e:
            logger.error(f"Error fetching admins: {e}")
            return []
    
    # ==================== USER MANAGEMENT ====================
    
    @staticmethod
    async def get_user_statistics() -> Dict[str, int]:
        """Get user statistics"""
        try:
            query = """
                SELECT 
                    COUNT(*) as total,
                    COUNT(CASE WHEN last_active > NOW() - INTERVAL '24 hours' THEN 1 END) as active,
                    COUNT(CASE WHEN banned = true THEN 1 END) as banned,
                    COUNT(CASE WHEN created_at > NOW() - INTERVAL '1 day' THEN 1 END) as new_today
                FROM users
            """
            row = await db.fetchrow(query)
            return dict(row) if row else {'total': 0, 'active': 0, 'banned': 0, 'new_today': 0}
        except Exception as e:
            logger.error(f"Error fetching user stats: {e}")
            return {'total': 0, 'active': 0, 'banned': 0, 'new_today': 0}
    
    @staticmethod
    async def search_user(query_text: str) -> List[Dict[str, Any]]:
        """Search users by username, name or ID"""
        try:
            query = """
                SELECT user_id, username, first_name, credits, banned, created_at
                FROM users
                WHERE 
                    CAST(user_id AS TEXT) LIKE $1 OR
                    username ILIKE $1 OR
                    first_name ILIKE $1
                LIMIT 50
            """
            search_pattern = f"%{query_text}%"
            rows = await db.fetch(query, search_pattern)
            return [dict(row) for row in rows]
        except Exception as e:
            logger.error(f"Error searching users: {e}")
            return []
    
    @staticmethod
    async def ban_user(user_id: int, reason: str = None, banned_by: int = None) -> bool:
        """Ban a user"""
        try:
            query = """
                UPDATE users 
                SET banned = true, ban_reason = $2, banned_at = $3, banned_by = $4
                WHERE user_id = $1
            """
            await db.execute(query, user_id, reason, datetime.now(), banned_by)
            logger.info(f"✅ User banned: {user_id}")
            return True
        except Exception as e:
            logger.error(f"Error banning user: {e}")
            return False
    
    @staticmethod
    async def unban_user(user_id: int) -> bool:
        """Unban a user"""
        try:
            query = "UPDATE users SET banned = false, ban_reason = NULL WHERE user_id = $1"
            await db.execute(query, user_id)
            logger.info(f"✅ User unbanned: {user_id}")
            return True
        except Exception as e:
            logger.error(f"Error unbanning user: {e}")
            return False
    
    @staticmethod
    async def adjust_credits(user_id: int, amount: int, reason: str = None) -> bool:
        """Adjust user credits (positive or negative)"""
        try:
            query = """
                UPDATE users 
                SET credits = GREATEST(0, credits + $2)
                WHERE user_id = $1
                RETURNING credits
            """
            new_credits = await db.fetchval(query, user_id, amount)
            
            # Log transaction
            log_query = """
                INSERT INTO credit_transactions (user_id, amount, reason, created_at)
                VALUES ($1, $2, $3, $4)
            """
            await db.execute(log_query, user_id, amount, reason, datetime.now())
            
            logger.info(f"✅ Credits adjusted for {user_id}: {amount} (new: {new_credits})")
            return True
        except Exception as e:
            logger.error(f"Error adjusting credits: {e}")
            return False
    
    @staticmethod
    async def get_all_users(limit: int = 100, offset: int = 0) -> List[Dict[str, Any]]:
        """Get all users with pagination"""
        try:
            query = """
                SELECT user_id, username, first_name, credits, banned, created_at, last_active
                FROM users
                ORDER BY created_at DESC
                LIMIT $1 OFFSET $2
            """
            rows = await db.fetch(query, limit, offset)
            return [dict(row) for row in rows]
        except Exception as e:
            logger.error(f"Error fetching users: {e}")
            return []
    
    # ==================== FORCE JOIN MANAGEMENT ====================
    
    @staticmethod
    async def get_force_join_channels() -> List[Dict[str, Any]]:
        """Get all force join channels"""
        try:
            query = """
                SELECT id, channel_id, title, username, active, added_at
                FROM force_join_channels
                ORDER BY added_at DESC
            """
            rows = await db.fetch(query)
            return [dict(row) for row in rows]
        except Exception as e:
            logger.error(f"Error fetching force join channels: {e}")
            return []
    
    @staticmethod
    async def add_force_join_channel(channel_id: int, title: str, username: str) -> bool:
        """Add force join channel"""
        try:
            query = """
                INSERT INTO force_join_channels (channel_id, title, username, active, added_at)
                VALUES ($1, $2, $3, true, $4)
                ON CONFLICT (channel_id) DO UPDATE SET active = true
            """
            await db.execute(query, channel_id, title, username, datetime.now())
            logger.info(f"✅ Force join channel added: {username}")
            return True
        except Exception as e:
            logger.error(f"Error adding force join channel: {e}")
            return False
    
    @staticmethod
    async def remove_force_join_channel(channel_id: int) -> bool:
        """Remove force join channel"""
        try:
            query = "DELETE FROM force_join_channels WHERE channel_id = $1"
            await db.execute(query, channel_id)
            logger.info(f"✅ Force join channel removed: {channel_id}")
            return True
        except Exception as e:
            logger.error(f"Error removing force join channel: {e}")
            return False
    
    @staticmethod
    async def toggle_force_join_status(channel_id: int, active: bool) -> bool:
        """Enable/disable force join channel"""
        try:
            query = "UPDATE force_join_channels SET active = $2 WHERE channel_id = $1"
            await db.execute(query, channel_id, active)
            return True
        except Exception as e:
            logger.error(f"Error toggling force join status: {e}")
            return False
    
    # ==================== BROADCAST MANAGEMENT ====================
    
    @staticmethod
    async def save_broadcast(message_text: str, sent_by: int, total_users: int) -> int:
        """Save broadcast record"""
        try:
            query = """
                INSERT INTO broadcasts (message_text, sent_by, total_users, sent_at, status)
                VALUES ($1, $2, $3, $4, 'pending')
                RETURNING id
            """
            broadcast_id = await db.fetchval(query, message_text, sent_by, total_users, datetime.now())
            logger.info(f"✅ Broadcast saved: {broadcast_id}")
            return broadcast_id
        except Exception as e:
            logger.error(f"Error saving broadcast: {e}")
            return 0
    
    @staticmethod
    async def update_broadcast_stats(broadcast_id: int, success: int, failed: int) -> bool:
        """Update broadcast statistics"""
        try:
            query = """
                UPDATE broadcasts 
                SET success_count = $2, failed_count = $3, status = 'completed', completed_at = $4
                WHERE id = $1
            """
            await db.execute(query, broadcast_id, success, failed, datetime.now())
            return True
        except Exception as e:
            logger.error(f"Error updating broadcast stats: {e}")
            return False
    
    @staticmethod
    async def get_broadcast_history(limit: int = 20) -> List[Dict[str, Any]]:
        """Get broadcast history"""
        try:
            query = """
                SELECT b.id, b.message_text, b.total_users, b.success_count, 
                       b.failed_count, b.sent_at, b.status, a.name as sent_by_name
                FROM broadcasts b
                LEFT JOIN admins a ON b.sent_by = a.user_id
                ORDER BY b.sent_at DESC
                LIMIT $1
            """
            rows = await db.fetch(query, limit)
            return [dict(row) for row in rows]
        except Exception as e:
            logger.error(f"Error fetching broadcast history: {e}")
            return []
    
    # ==================== ANALYTICS ====================
    
    @staticmethod
    async def get_admin_stats() -> Dict[str, Any]:
        """Get admin dashboard statistics"""
        try:
            # Multiple queries for different stats
            users_query = "SELECT COUNT(*) FROM users"
            courses_query = "SELECT COUNT(*) FROM courses"
            revenue_query = "SELECT COALESCE(SUM(amount), 0) FROM orders WHERE status = 'completed'"
            orders_query = "SELECT COUNT(*) FROM orders WHERE status = 'pending'"
            admins_query = "SELECT COUNT(*) FROM admins WHERE active = true"
            
            total_users = await db.fetchval(users_query)
            total_courses = await db.fetchval(courses_query)
            total_revenue = await db.fetchval(revenue_query)
            pending_orders = await db.fetchval(orders_query)
            active_admins = await db.fetchval(admins_query)
            
            return {
                'total_users': total_users or 0,
                'total_courses': total_courses or 0,
                'total_revenue': total_revenue or 0,
                'pending_orders': pending_orders or 0,
                'active_admins': active_admins or 0
            }
        except Exception as e:
            logger.error(f"Error fetching admin stats: {e}")
            return {
                'total_users': 0,
                'total_courses': 0,
                'total_revenue': 0,
                'pending_orders': 0,
                'active_admins': 0
            }
    
    @staticmethod
    async def get_analytics_data() -> Dict[str, Any]:
        """Get comprehensive analytics data"""
        try:
            # User metrics
            user_metrics_query = """
                SELECT 
                    COUNT(*) as total_users,
                    COUNT(CASE WHEN last_active > NOW() - INTERVAL '1 day' THEN 1 END) as active_today,
                    COUNT(CASE WHEN created_at > NOW() - INTERVAL '7 days' THEN 1 END) as new_week,
                    ROUND((
                        COUNT(CASE WHEN created_at > NOW() - INTERVAL '7 days' THEN 1 END)::float /
                        NULLIF(COUNT(CASE WHEN created_at > NOW() - INTERVAL '14 days' AND created_at <= NOW() - INTERVAL '7 days' THEN 1 END), 0)
                    ) * 100, 2) as growth_rate
                FROM users
            """
            
            # Course metrics
            course_metrics_query = """
                SELECT 
                    COUNT(*) as total_courses,
                    COALESCE(SUM((SELECT COUNT(*) FROM orders WHERE course_id = courses.id AND status = 'completed')), 0) as total_sales,
                    COALESCE(SUM((SELECT SUM(amount) FROM orders WHERE course_id = courses.id AND status = 'completed')), 0) as revenue,
                    COALESCE(AVG(price), 0) as avg_price
                FROM courses
            """
            
            # Engagement metrics
            engagement_query = """
                SELECT 
                    COUNT(*) as messages,
                    (SELECT COUNT(*) FROM broadcasts) as broadcasts,
                    (SELECT COUNT(*) FROM user_interactions WHERE action_type = 'button_click') as clicks,
                    ROUND((
                        (SELECT COUNT(*) FROM orders WHERE status = 'completed')::float /
                        NULLIF(COUNT(*), 0)
                    ) * 100, 2) as conversion
                FROM user_interactions
                WHERE created_at > NOW() - INTERVAL '30 days'
            """
            
            user_metrics = await db.fetchrow(user_metrics_query)
            course_metrics = await db.fetchrow(course_metrics_query)
            engagement = await db.fetchrow(engagement_query)
            
            return {
                **dict(user_metrics or {}),
                **dict(course_metrics or {}),
                **dict(engagement or {})
            }
        except Exception as e:
            logger.error(f"Error fetching analytics data: {e}")
            return {}
    
    # ==================== CONTENT MANAGEMENT ====================
    
    @staticmethod
    async def get_bot_content(content_key: str) -> Optional[str]:
        """Get bot content by key"""
        try:
            query = "SELECT content FROM bot_content WHERE key = $1"
            return await db.fetchval(query, content_key)
        except Exception as e:
            logger.error(f"Error fetching content: {e}")
            return None
    
    @staticmethod
    async def update_bot_content(content_key: str, content: str, updated_by: int) -> bool:
        """Update bot content"""
        try:
            query = """
                INSERT INTO bot_content (key, content, updated_by, updated_at)
                VALUES ($1, $2, $3, $4)
                ON CONFLICT (key) DO UPDATE 
                SET content = $2, updated_by = $3, updated_at = $4
            """
            await db.execute(query, content_key, content, updated_by, datetime.now())
            logger.info(f"✅ Content updated: {content_key}")
            return True
        except Exception as e:
            logger.error(f"Error updating content: {e}")
            return False

# Global admin database instance
admin_db = AdminDatabase()
