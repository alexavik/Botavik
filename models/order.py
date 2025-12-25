# 📦 Order Database Model

import logging
from database.db import db

logger = logging.getLogger(__name__)


class Order:
    """Order database operations"""
    
    @staticmethod
    async def create(user_id: int, course_id: int, price: float, user_name: str = None) -> int:
        """Create new order, returns order ID"""
        query = """
            INSERT INTO orders (user_id, course_id, price, user_name, payment_status)
            VALUES ($1, $2, $3, $4, 'pending')
            RETURNING id
        """
        result = await db.fetchval(query, user_id, course_id, price, user_name)
        logger.info(f"✅ Order created: User {user_id}, Course {course_id} (Order ID: {result})")
        return result
    
    @staticmethod
    async def get_by_id(order_id: int):
        """Get order by ID"""
        query = "SELECT * FROM orders WHERE id = $1"
        return await db.fetchrow(query, order_id)
    
    @staticmethod
    async def get_user_orders(user_id: int):
        """Get all orders for a user"""
        query = "SELECT * FROM orders WHERE user_id = $1 ORDER BY created_at DESC"
        return await db.fetch(query, user_id)
    
    @staticmethod
    async def get_user_course_purchase(user_id: int, course_id: int):
        """Check if user has purchased this course"""
        query = """
            SELECT * FROM orders 
            WHERE user_id = $1 AND course_id = $2 AND payment_status = 'completed'
            LIMIT 1
        """
        return await db.fetchrow(query, user_id, course_id)
    
    @staticmethod
    async def mark_completed(order_id: int, transaction_id: str = None):
        """Mark order as completed"""
        query = """
            UPDATE orders 
            SET payment_status = 'completed', transaction_id = $1, updated_at = NOW()
            WHERE id = $2
        """
        await db.execute(query, transaction_id, order_id)
        logger.info(f"✅ Order {order_id} marked as completed")
    
    @staticmethod
    async def mark_failed(order_id: int):
        """Mark order as failed"""
        query = """
            UPDATE orders 
            SET payment_status = 'failed', updated_at = NOW()
            WHERE id = $1
        """
        await db.execute(query, order_id)
        logger.info(f"❌ Order {order_id} marked as failed")
    
    @staticmethod
    async def get_pending_orders(limit: int = 100):
        """Get all pending orders"""
        query = "SELECT * FROM orders WHERE payment_status = 'pending' ORDER BY created_at DESC LIMIT $1"
        return await db.fetch(query, limit)
    
    @staticmethod
    async def get_completed_orders(course_id: int = None):
        """Get completed orders for a course"""
        if course_id:
            query = """
                SELECT * FROM orders 
                WHERE course_id = $1 AND payment_status = 'completed'
                ORDER BY created_at DESC
            """
            return await db.fetch(query, course_id)
        else:
            query = "SELECT * FROM orders WHERE payment_status = 'completed' ORDER BY created_at DESC"
            return await db.fetch(query)
    
    @staticmethod
    async def count_course_sales(course_id: int):
        """Count successful sales for a course"""
        query = "SELECT COUNT(*) FROM orders WHERE course_id = $1 AND payment_status = 'completed'"
        return await db.fetchval(query, course_id)
    
    @staticmethod
    async def get_total_revenue():
        """Calculate total revenue from completed orders"""
        query = "SELECT SUM(price) FROM orders WHERE payment_status = 'completed'"
        result = await db.fetchval(query)
        return result or 0
    
    @staticmethod
    async def delete_pending(order_id: int):
        """Delete a pending order"""
        query = "DELETE FROM orders WHERE id = $1 AND payment_status = 'pending'"
        await db.execute(query, order_id)
        logger.info(f"✅ Pending order {order_id} deleted")
