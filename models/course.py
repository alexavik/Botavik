# 📚 Course Database Model

import logging
from datetime import datetime
from database.db import db

logger = logging.getLogger(__name__)


class Course:
    """Course database operations"""
    
    @staticmethod
    async def create(title: str, description: str, price: float, 
                     category: str = None, demo_video_id: str = None) -> int:
        """Create new course, returns course ID"""
        query = """
            INSERT INTO courses (title, description, price, category, demo_video_id)
            VALUES ($1, $2, $3, $4, $5)
            RETURNING id
        """
        result = await db.fetchval(query, title, description, price, category, demo_video_id)
        logger.info(f"✅ Course created: {title} (ID: {result})")
        return result
    
    @staticmethod
    async def get_by_id(course_id: int):
        """Get course by ID"""
        query = "SELECT * FROM courses WHERE id = $1 AND deleted_at IS NULL"
        return await db.fetchrow(query, course_id)
    
    @staticmethod
    async def get_all(limit: int = 100, offset: int = 0):
        """Get all courses paginated"""
        query = "SELECT * FROM courses WHERE deleted_at IS NULL ORDER BY created_at DESC LIMIT $1 OFFSET $2"
        return await db.fetch(query, limit, offset)
    
    @staticmethod
    async def get_by_category(category: str):
        """Get courses by category"""
        query = "SELECT * FROM courses WHERE category = $1 AND deleted_at IS NULL ORDER BY created_at DESC"
        return await db.fetch(query, category)
    
    @staticmethod
    async def update_caption(course_id: int, caption: str):
        """Update AI-generated caption"""
        query = "UPDATE courses SET ai_caption = $1, updated_at = NOW() WHERE id = $2"
        await db.execute(query, caption, course_id)
        logger.info(f"✅ Caption updated for course {course_id}")
    
    @staticmethod
    async def update_channel_post(course_id: int, channel_post_id: int):
        """Update channel post ID after posting"""
        query = "UPDATE courses SET channel_post_id = $1, updated_at = NOW() WHERE id = $2"
        await db.execute(query, channel_post_id, course_id)
        logger.info(f"✅ Channel post updated for course {course_id}")
    
    @staticmethod
    async def update_demo_video(course_id: int, video_file_id: str):
        """Update demo video file ID"""
        query = "UPDATE courses SET demo_video_id = $1, updated_at = NOW() WHERE id = $2"
        await db.execute(query, video_file_id, course_id)
        logger.info(f"✅ Demo video updated for course {course_id}")
    
    @staticmethod
    async def add_rating(course_id: int, rating: float, reviews: int):
        """Update rating and review count"""
        query = "UPDATE courses SET rating = $1, reviews = $2, updated_at = NOW() WHERE id = $3"
        await db.execute(query, rating, reviews, course_id)
    
    @staticmethod
    async def soft_delete(course_id: int):
        """Soft delete course (mark as deleted)"""
        query = "UPDATE courses SET deleted_at = NOW() WHERE id = $1"
        await db.execute(query, course_id)
        logger.info(f"✅ Course {course_id} deleted")
    
    @staticmethod
    async def delete_permanent(course_id: int):
        """Permanently delete course"""
        query = "DELETE FROM courses WHERE id = $1"
        await db.execute(query, course_id)
        logger.info(f"✅ Course {course_id} permanently deleted")
    
    @staticmethod
    async def count_all():
        """Count all active courses"""
        query = "SELECT COUNT(*) FROM courses WHERE deleted_at IS NULL"
        return await db.fetchval(query)
