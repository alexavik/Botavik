# Configuration file for Telegram Course Sales Bot
# All settings in one place

import os
from dotenv import load_dotenv

load_dotenv()

class BotConfig:
    """Bot configuration"""
    TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
    ADMIN_USER_IDS = [int(x.strip()) for x in os.getenv("ADMIN_USER_IDS", "").split(",") if x.strip()]
    PUBLISHING_CHANNEL_ID = int(os.getenv("PUBLISHING_CHANNEL_ID", "-1001234567890"))
    BOT_USERNAME = os.getenv("BOT_USERNAME", "your_bot")
    OWNER_CREDIT = os.getenv("OWNER_CREDIT", "@unknownwarrior911")
    ENVIRONMENT = os.getenv("ENVIRONMENT", "development")

class AIConfig:
    """AI API configuration (OpenRouter + Gemini)"""
    OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
    OPENROUTER_MODEL = "google/gemini-2.0-flash-exp:free"
    OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"
    TEMPERATURE = 0.7
    MAX_TOKENS = 1024
    TIMEOUT = 30

class PaymentConfig:
    """Payment configuration (FamPay UPI)"""
    PAYMENT_METHOD = os.getenv("PAYMENT_METHOD", "fampay")
    FAMPAY_UPI_ID = os.getenv("FAMPAY_UPI_ID")
    CURRENCY = "₹"
    MIN_AMOUNT = 100.0
    MAX_AMOUNT = 100000.0

class DatabaseConfig:
    """Database configuration (PostgreSQL)"""
    DATABASE_URL = os.getenv("DATABASE_URL")
    # Connection pool settings
    MIN_CONNECTIONS = 5
    MAX_CONNECTIONS = 20
    COMMAND_TIMEOUT = 30

class CourseConfig:
    """Course settings"""
    MAX_TITLE_LENGTH = 255
    MAX_DESCRIPTION_LENGTH = 2000
    MAX_PRICE = PaymentConfig.MAX_AMOUNT
    MIN_PRICE = 100.0
    MAX_VIDEO_SIZE = 20 * 1024 * 1024  # 20MB
    
    # Categories with emojis
    CATEGORIES = {
        'hacking': '🔐 Ethical Hacking',
        'python': '🐍 Python Programming',
        'web': '🌐 Web Development',
        'android': '📱 Android Development',
        'cybersecurity': '🛡️ Cybersecurity',
        'other': '📚 Other'
    }

class ValidationRules:
    """Input validation rules"""
    TITLE_MIN = 5
    TITLE_MAX = 100
    DESC_MIN = 20
    DESC_MAX = 1000
    PRICE_MIN = 100
    PRICE_MAX = 100000

# Verify critical settings
def validate_config():
    """Validate that all critical settings are set"""
    errors = []
    
    if not BotConfig.TELEGRAM_BOT_TOKEN:
        errors.append("❌ TELEGRAM_BOT_TOKEN not set in .env")
    
    if not AIConfig.OPENROUTER_API_KEY:
        errors.append("❌ OPENROUTER_API_KEY not set in .env")
    
    if not PaymentConfig.FAMPAY_UPI_ID:
        errors.append("⚠️ FAMPAY_UPI_ID not set (payments disabled)")
    
    if not DatabaseConfig.DATABASE_URL:
        errors.append("❌ DATABASE_URL not set in .env")
    
    if not BotConfig.ADMIN_USER_IDS:
        errors.append("⚠️ ADMIN_USER_IDS not set (no admin access)")
    
    return errors

# On import, check config
config_errors = validate_config()
if config_errors:
    print("\n⚠️ CONFIG VALIDATION WARNINGS:")
    for error in config_errors:
        print(f"  {error}")
    print()
