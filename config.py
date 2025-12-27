# 🛠️ Configuration Management - Telegram Course Sales Bot

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class BotConfig:
    """Telegram Bot Configuration"""
    TELEGRAM_BOT_TOKEN = os.getenv(
        'TELEGRAM_BOT_TOKEN',
        'YOUR_TOKEN_HERE'
    )
    ALLOWED_USER_IDS = os.getenv('ALLOWED_USER_IDS', '')
    OWNER_ID = int(os.getenv('OWNER_ID', 0)) if os.getenv('OWNER_ID') else None
    SUPPORT_CHAT_ID = os.getenv('SUPPORT_CHAT_ID', '')


class DatabaseConfig:
    """PostgreSQL Database Configuration"""
    DATABASE_URL = os.getenv(
        'DATABASE_URL',
        'postgresql://user:password@localhost/botavik'
    )


class PaymentConfig:
    """Payment Gateway Configuration"""
    UPI_ID = os.getenv('UPI_ID', '')
    RAZORPAY_KEY = os.getenv('RAZORPAY_KEY', '')
    RAZORPAY_SECRET = os.getenv('RAZORPAY_SECRET', '')
    PAYMENT_WEBHOOK_SECRET = os.getenv('PAYMENT_WEBHOOK_SECRET', '')


class AIConfig:
    """OpenRouter AI Configuration"""
    
    # OpenRouter API Key
    OPENROUTER_API_KEY = os.getenv(
        'OPENROUTER_API_KEY',
        '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'
    )
    
    # AI Model Selection
    AI_MODEL = os.getenv(
        'AI_MODEL',
        'google/gemini-2.0-flash-exp'
    )
    
    # AI Features Toggle - FIXED: Convert to boolean safely
    AI_ENABLED = os.getenv('AI_ENABLED', 'True').lower() == 'true'
    
    # API Configuration
    OPENROUTER_API_BASE = 'https://openrouter.ai/api/v1'
    API_TIMEOUT = 30
    MAX_RETRIES = 3
    
    # Temperature and top_p for generation
    TEMPERATURE = 0.7
    TOP_P = 0.9
    MAX_TOKENS = 1500
    
    # Prompts for different AI tasks
    PROMPTS = {
        'course_description': """You are a professional course creator. Generate an engaging, 
detailed course description for '{course_name}' that covers topics: {topics}. 
Make it compelling and highlight key benefits. Keep it under 200 words.""",
        
        'promotional_message': """Create an engaging promotional message for '{course_name}' 
with price ₹{price}. Make it catchy, use emojis, and include a call-to-action. 
Keep it concise but persuasive.""",
        
        'broadcast_message': """Write a professional broadcast message for users about: {content}. 
Make it engaging with proper formatting and emojis. Keep it concise.""",
        
        'faq_generator': """Generate 5-7 FAQs for the course '{course_name}' with topics: {topics}. 
Format as Q&A pairs. Make answers concise and helpful.""",
        
        'email_template': """Create a professional email template for {purpose}. 
Include: subject line, greeting, body, and closing. Make it suitable for course sales."""
    }
    
    @staticmethod
    def is_configured() -> bool:
        """Check if AI is properly configured"""
        return AIConfig.AI_ENABLED and bool(AIConfig.OPENROUTER_API_KEY)


class ChannelConfig:
    """Channel and Group Configuration"""
    COURSE_CHANNEL_ID = os.getenv('COURSE_CHANNEL_ID', '')
    ANNOUNCEMENT_CHANNEL_ID = os.getenv('ANNOUNCEMENT_CHANNEL_ID', '')
    SUPPORT_GROUP_ID = os.getenv('SUPPORT_GROUP_ID', '')
    DISCUSSION_GROUP_ID = os.getenv('DISCUSSION_GROUP_ID', '')


class AppConfig:
    """Application Configuration"""
    # Environment
    DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'
    ENVIRONMENT = os.getenv('ENVIRONMENT', 'production')
    
    # Logging
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    LOG_FILE = os.getenv('LOG_FILE', 'logs/bot.log')
    
    # Rate limiting
    BROADCAST_DELAY = float(os.getenv('BROADCAST_DELAY', '0.1'))  # seconds between broadcasts
    MAX_BROADCAST_SIZE = int(os.getenv('MAX_BROADCAST_SIZE', '100'))  # batch size
    
    # Features - FIXED: Get string value first before calling .lower()
    ENABLE_COURSES = os.getenv('ENABLE_COURSES', 'True').lower() == 'true'
    ENABLE_PAYMENTS = os.getenv('ENABLE_PAYMENTS', 'True').lower() == 'true'
    ENABLE_FORCE_JOIN = os.getenv('ENABLE_FORCE_JOIN', 'True').lower() == 'true'
    ENABLE_ADMIN_DASHBOARD = os.getenv('ENABLE_ADMIN_DASHBOARD', 'True').lower() == 'true'
    ENABLE_AI_FEATURES = os.getenv('ENABLE_AI_FEATURES', 'True').lower() == 'true'


class ValidationConfig:
    """Validation Configuration"""
    MIN_COURSE_TITLE_LENGTH = 5
    MAX_COURSE_TITLE_LENGTH = 150
    MIN_COURSE_DESCRIPTION_LENGTH = 20
    MAX_COURSE_DESCRIPTION_LENGTH = 2000
    MIN_PRICE = 0.01
    MAX_PRICE = 1000000


class ValidationRules:
    """Validation Rules for Course Data"""
    
    # Course Title Validation
    MIN_TITLE_LENGTH = 5
    MAX_TITLE_LENGTH = 150
    
    # Course Description Validation
    MIN_DESCRIPTION_LENGTH = 20
    MAX_DESCRIPTION_LENGTH = 2000
    
    # Price Validation
    MIN_PRICE = 0.01
    MAX_PRICE = 1000000
    
    # URL Validation
    ALLOWED_URL_SCHEMES = ['http', 'https']
    MAX_URL_LENGTH = 500
    
    # File Validation
    ALLOWED_IMAGE_FORMATS = ['jpg', 'jpeg', 'png', 'gif', 'webp']
    ALLOWED_VIDEO_FORMATS = ['mp4', 'avi', 'mov', 'mkv']
    MAX_FILE_SIZE_MB = 50
    
    # Text Validation
    MAX_MESSAGE_LENGTH = 4096  # Telegram limit
    MAX_CAPTION_LENGTH = 1024  # Telegram limit
    
    # Numeric Validation
    MIN_COURSE_DURATION = 1  # minutes
    MAX_COURSE_DURATION = 10000  # minutes
    
    # User Input Validation
    MAX_USERNAME_LENGTH = 32
    MIN_USERNAME_LENGTH = 3
    
    # Admin Validation
    MIN_ADMIN_LEVEL = 1
    MAX_ADMIN_LEVEL = 10
    
    @staticmethod
    def is_valid_price(price: float) -> bool:
        """Check if price is valid"""
        return ValidationRules.MIN_PRICE <= price <= ValidationRules.MAX_PRICE
    
    @staticmethod
    def is_valid_title(title: str) -> bool:
        """Check if title is valid"""
        return ValidationRules.MIN_TITLE_LENGTH <= len(title) <= ValidationRules.MAX_TITLE_LENGTH
    
    @staticmethod
    def is_valid_description(description: str) -> bool:
        """Check if description is valid"""
        return ValidationRules.MIN_DESCRIPTION_LENGTH <= len(description) <= ValidationRules.MAX_DESCRIPTION_LENGTH
    
    @staticmethod
    def is_valid_url(url: str) -> bool:
        """Check if URL is valid"""
        if not url or len(url) > ValidationRules.MAX_URL_LENGTH:
            return False
        return any(url.startswith(f"{scheme}://") for scheme in ValidationRules.ALLOWED_URL_SCHEMES)
