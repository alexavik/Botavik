# 🔐 Authorization & Logging Decorators

import logging
import functools
from typing import Callable
from telegram.update import Update
from telegram.ext import ContextTypes
from config import BotConfig

logger = logging.getLogger(__name__)


def admin_only(func: Callable) -> Callable:
    """Decorator to restrict command to admin users only"""
    @functools.wraps(func)
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        user_id = update.effective_user.id
        
        if user_id not in BotConfig.ADMIN_USER_IDS:
            await update.message.reply_text(
                "❌ You don't have permission to use this command.\n"
                f"Only admin users can access this."
            )
            logger.warning(f"⚠️ Unauthorized access attempt by user {user_id}")
            return
        
        logger.info(f"✅ Admin command accessed by user {user_id}")
        await func(update, context)
    
    return wrapper


def log_command(command_name: str):
    """Decorator to log command execution"""
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
            user_id = update.effective_user.id
            username = update.effective_user.username or "Unknown"
            
            logger.info(f"📝 Command '{command_name}' executed by @{username} (ID: {user_id})")
            
            try:
                await func(update, context)
            except Exception as e:
                logger.error(f"❌ Error in {command_name}: {e}")
                try:
                    await update.message.reply_text(
                        "❌ An error occurred while processing your request.\n"
                        "Please try again later."
                    )
                except:
                    pass
        
        return wrapper
    return decorator


def handle_errors(func: Callable) -> Callable:
    """Decorator for generic error handling"""
    @functools.wraps(func)
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        try:
            await func(update, context)
        except Exception as e:
            logger.error(f"❌ Error in {func.__name__}: {e}", exc_info=True)
            try:
                await update.message.reply_text(
                    "❌ Something went wrong. Please try again."
                )
            except:
                pass
    
    return wrapper
