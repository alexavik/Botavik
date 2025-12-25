# ❤️ Wishlist Database Model

import logging
from database.db import db

logger = logging.getLogger(__name__)


class Wishlist:
    """Wishlist database operations"""
    
    @staticmethod
    async def add(user_id: int, course_id: int) -> bool:
        """Add course to wishlist"""
        query = """
            INSERT INTO wishlist (user_id, course_id)
            VALUES ($1, $2)
            ON CONFLICT (user_id, course_id) DO NOTHING
        """
        result = await db.execute(query, user_id, course_id)
        if result == "INSERT 0 1":
            logger.info(f"✅ Course {course_id} added to wishlist for user {user_id}")
            return True
        return False
    
    @staticmethod
    async def remove(user_id: int, course_id: int) -> bool:
        """Remove course from wishlist"""
        query = "DELETE FROM wishlist WHERE user_id = $1 AND course_id = $2"
        result = await db.execute(query, user_id, course_id)
        if result == "DELETE 1":
            logger.info(f"✅ Course {course_id} removed from wishlist for user {user_id}")
            return True
        return False
    
    @staticmethod
    async def get_user_wishlist(user_id: int):
        """Get all wishlisted courses for user"""
        query = """
            SELECT c.* FROM wishlist w
            JOIN courses c ON w.course_id = c.id
            WHERE w.user_id = $1 AND c.deleted_at IS NULL
            ORDER BY w.created_at DESC
        """
        return await db.fetch(query, user_id)
    
    @staticmethod
    async def is_wishlisted(user_id: int, course_id: int) -> bool:
        """Check if course is in user's wishlist"""
        query = "SELECT id FROM wishlist WHERE user_id = $1 AND course_id = $2 LIMIT 1"
        result = await db.fetchrow(query, user_id, course_id)
        return result is not None
    
    @staticmethod
    async def count_wishlist(user_id: int) -> int:
        """Count courses in user's wishlist"""
        query = "SELECT COUNT(*) FROM wishlist WHERE user_id = $1"
        result = await db.fetchval(query, user_id)
        return result or 0
    
    @staticmethod
    async def get_wishlist_count(course_id: int) -> int:
        """Count how many users have this course in wishlist"""
        query = "SELECT COUNT(*) FROM wishlist WHERE course_id = $1"
        result = await db.fetchval(query, course_id)
        return result or 0
    
    @staticmethod
    async def toggle(user_id: int, course_id: int) -> bool:
        """Toggle wishlist status (add if not exists, remove if exists)"""
        is_wishlisted = await Wishlist.is_wishlisted(user_id, course_id)
        
        if is_wishlisted:
            return await Wishlist.remove(user_id, course_id)
        else:
            return await Wishlist.add(user_id, course_id)
    
    @staticmethod
    async def clear_user_wishlist(user_id: int):
        """Clear all wishlist entries for a user"""
        query = "DELETE FROM wishlist WHERE user_id = $1"
        await db.execute(query, user_id)
        logger.info(f"✅ Wishlist cleared for user {user_id}")
