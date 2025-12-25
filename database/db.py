# 🛠️ Database Connection Pool & Query Manager

import asyncpg
import logging
from typing import Optional
from config import DatabaseConfig

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


# Global database instance
db = Database()
