# ✅ Input Validation Utilities

import re
import logging
from config import ValidationRules

logger = logging.getLogger(__name__)


class Validator:
    """Input validation utilities"""
    
    @staticmethod
    def validate_course_title(title: str) -> tuple[bool, str]:
        """Validate course title"""
        if not title or not isinstance(title, str):
            return False, "Title must be a non-empty string"
        
        title = title.strip()
        
        if len(title) < ValidationRules.MIN_TITLE_LENGTH:
            return False, f"Title must be at least {ValidationRules.MIN_TITLE_LENGTH} characters"
        
        if len(title) > ValidationRules.MAX_TITLE_LENGTH:
            return False, f"Title must be no more than {ValidationRules.MAX_TITLE_LENGTH} characters"
        
        return True, "Valid"
    
    @staticmethod
    def validate_description(description: str) -> tuple[bool, str]:
        """Validate course description"""
        if not description or not isinstance(description, str):
            return False, "Description must be a non-empty string"
        
        description = description.strip()
        
        if len(description) < ValidationRules.MIN_DESCRIPTION_LENGTH:
            return False, f"Description must be at least {ValidationRules.MIN_DESCRIPTION_LENGTH} characters"
        
        if len(description) > ValidationRules.MAX_DESCRIPTION_LENGTH:
            return False, f"Description must be no more than {ValidationRules.MAX_DESCRIPTION_LENGTH} characters"
        
        return True, "Valid"
    
    @staticmethod
    def validate_price(price) -> tuple[bool, str]:
        """Validate course price"""
        try:
            price = float(price)
        except (ValueError, TypeError):
            return False, "Price must be a valid number"
        
        if price < ValidationRules.MIN_PRICE:
            return False, f"Price must be at least ₹{ValidationRules.MIN_PRICE}"
        
        if price > ValidationRules.MAX_PRICE:
            return False, f"Price must not exceed ₹{ValidationRules.MAX_PRICE}"
        
        return True, "Valid"
    
    @staticmethod
    def validate_category(category: str) -> tuple[bool, str]:
        """Validate course category"""
        if not category:
            return True, "Valid"  # Optional field
        
        if category not in [c[0] for c in ValidationRules.ALLOWED_CATEGORIES]:
            return False, "Invalid category"
        
        return True, "Valid"
    
    @staticmethod
    def validate_upi_id(upi_id: str) -> tuple[bool, str]:
        """Validate UPI ID format"""
        # UPI format: username@bank
        upi_pattern = r'^[a-zA-Z0-9._-]+@[a-zA-Z0-9]+$'
        
        if not re.match(upi_pattern, upi_id):
            return False, "Invalid UPI ID format (should be like: name@bank)"
        
        return True, "Valid"
    
    @staticmethod
    def validate_username(username: str) -> tuple[bool, str]:
        """Validate Telegram username"""
        # Username: 5-32 alphanumeric and underscore
        if not username:
            return False, "Username cannot be empty"
        
        if len(username) < 5 or len(username) > 32:
            return False, "Username must be 5-32 characters"
        
        if not re.match(r'^[a-zA-Z0-9_]+$', username):
            return False, "Username can only contain letters, numbers, and underscores"
        
        return True, "Valid"
    
    @staticmethod
    def validate_user_input(text: str, min_length: int = 1, max_length: int = 4096) -> tuple[bool, str]:
        """Generic text input validation"""
        if not text or not isinstance(text, str):
            return False, "Input must be a non-empty string"
        
        text = text.strip()
        
        if len(text) < min_length:
            return False, f"Input must be at least {min_length} characters"
        
        if len(text) > max_length:
            return False, f"Input must be no more than {max_length} characters"
        
        return True, "Valid"
    
    @staticmethod
    def sanitize_input(text: str) -> str:
        """Remove potentially harmful characters"""
        # Remove SQL special characters
        text = text.replace("'", "''")
        text = text.replace('"', '""')
        
        # Remove multiple spaces
        text = re.sub(r'\s+', ' ', text)
        
        return text.strip()
    
    @staticmethod
    def validate_all_course_data(title: str, description: str, price, category: str = None) -> tuple[bool, str]:
        """Validate all course creation data at once"""
        # Validate title
        is_valid, msg = Validator.validate_course_title(title)
        if not is_valid:
            return False, f"Title: {msg}"
        
        # Validate description
        is_valid, msg = Validator.validate_description(description)
        if not is_valid:
            return False, f"Description: {msg}"
        
        # Validate price
        is_valid, msg = Validator.validate_price(price)
        if not is_valid:
            return False, f"Price: {msg}"
        
        # Validate category
        if category:
            is_valid, msg = Validator.validate_category(category)
            if not is_valid:
                return False, f"Category: {msg}"
        
        return True, "All data valid"
