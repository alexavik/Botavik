# 🖼️ Vision Handler - Image Analysis Features

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler
from services.ai_service import ai_service
import logging

logger = logging.getLogger(__name__)

# Conversation states
AWAIT_IMAGE_URL = 1
AWAIT_IMAGE_QUESTION = 2
AWAIT_THUMBNAIL_URL = 3
AWAIT_PAYMENT_PROOF = 4


class VisionHandler:
    """Handle image analysis features"""
    
    @staticmethod
    async def vision_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """
        Show vision AI menu
        """
        query = update.callback_query
        await query.answer()
        
        keyboard = [
            [
                InlineKeyboardButton("🖼️ Analyze Image", callback_data='vision_analyze'),
                InlineKeyboardButton("🇿 Review Thumbnail", callback_data='vision_thumbnail')
            ],
            [
                InlineKeyboardButton("💳 Verify Payment", callback_data='vision_payment'),
                InlineKeyboardButton("🧪 Test Vision", callback_data='vision_test')
            ],
            [
                InlineKeyboardButton("⬅️ Back to AI Menu", callback_data='admin_ai')
            ]
        ]
        
        text = """
🖼️ **VISION AI FEATURES**

👁️ **Image Analysis:**
- Upload or send image URL
- Ask questions about images
- Get detailed descriptions

🇿 **Thumbnail Review:**
- Analyze course thumbnails
- Get design feedback
- Improvement suggestions

💳 **Payment Verification:**
- Verify payment screenshots
- Extract transaction details
- Auto-validate proofs

🧪 **Test:**
- Test vision AI with sample image

**Select an option below:**
        """
        
        await query.edit_message_text(
            text,
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
    
    @staticmethod
    async def start_analyze_image(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """
        Start image analysis flow
        """
        query = update.callback_query
        await query.answer()
        
        text = """
🖼️ **ANALYZE IMAGE**

Send me:
1. Image URL (direct link)
2. Or upload/forward an image

I'll analyze it using Gemini 2.0 Flash Vision! 👁️

**Examples:**
- https://example.com/image.jpg
- Or just send/forward the image

Type /cancel to abort.
        """
        
        await query.edit_message_text(text)
        return AWAIT_IMAGE_URL
    
    @staticmethod
    async def receive_image_url(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """
        Receive image URL or photo upload
        """
        # Check if it's a photo upload
        if update.message.photo:
            # Get highest resolution photo
            photo = update.message.photo[-1]
            image_url = await photo.get_file()
            image_url = image_url.file_path
            
            await update.message.reply_text("🔍 Analyzing uploaded image...")
        
        # Check if it's a URL
        elif update.message.text:
            if update.message.text.startswith('http'):
                image_url = update.message.text.strip()
                await update.message.reply_text("🔍 Analyzing image from URL...")
            else:
                await update.message.reply_text(
                    "❌ Invalid URL. Please send a valid image URL starting with http:// or https://\n\n"
                    "Or upload/forward an image directly."
                )
                return AWAIT_IMAGE_URL
        else:
            await update.message.reply_text(
                "❌ Please send an image URL or upload an image."
            )
            return AWAIT_IMAGE_URL
        
        # Store image URL in context
        context.user_data['vision_image_url'] = image_url
        
        # Ask what question to ask about the image
        keyboard = [
            [InlineKeyboardButton("📝 Default Question", callback_data='vision_default_q')],
            [InlineKeyboardButton("✏️ Custom Question", callback_data='vision_custom_q')]
        ]
        
        await update.message.reply_text(
            "✅ Image received!\n\n"
            "What would you like to know about this image?\n\n"
            "📝 **Default:** 'What is in this image?'\n"
            "✏️ **Custom:** Ask your own question",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        
        return AWAIT_IMAGE_QUESTION
    
    @staticmethod
    async def process_image_analysis(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """
        Process image analysis with AI
        """
        query = update.callback_query
        await query.answer()
        
        image_url = context.user_data.get('vision_image_url')
        
        if query.data == 'vision_default_q':
            question = "What is in this image? Describe it in detail."
        else:
            await query.edit_message_text(
                "✏️ **Custom Question**\n\n"
                "Type your question about the image:\n"
                "(e.g., 'Is this a professional design?', 'What colors are used?')"
            )
            return AWAIT_IMAGE_QUESTION
        
        # Perform analysis
        await query.edit_message_text("🤖 Analyzing image with Gemini 2.0 Flash Vision...")
        
        try:
            result = await ai_service.analyze_image(image_url, question)
            
            if result:
                response = f"""
✅ **IMAGE ANALYSIS COMPLETE**

🖼️ **Image:** {image_url[:50]}...

💬 **AI Response:**
{result}

———————————————
🤖 Powered by Gemini 2.0 Flash Vision
                """
                
                keyboard = [
                    [InlineKeyboardButton("🔄 Analyze Another", callback_data='vision_analyze')],
                    [InlineKeyboardButton("⬅️ Back to Vision Menu", callback_data='vision_menu')]
                ]
                
                await query.edit_message_text(
                    response,
                    reply_markup=InlineKeyboardMarkup(keyboard)
                )
            else:
                await query.edit_message_text(
                    "❌ Analysis failed. Please try again or check the image URL."
                )
        
        except Exception as e:
            logger.error(f"Error in image analysis: {e}")
            await query.edit_message_text(
                f"❌ Error during analysis: {str(e)}"
            )
        
        return ConversationHandler.END
    
    @staticmethod
    async def start_thumbnail_review(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """
        Start course thumbnail review
        """
        query = update.callback_query
        await query.answer()
        
        text = """
🇿 **COURSE THUMBNAIL REVIEW**

Send me:
1. Course thumbnail image URL
2. Course name

Format:
```
Course Name: Python for Beginners
Image URL: https://example.com/thumbnail.jpg
```

Or upload the thumbnail directly and I'll ask for the course name.

Type /cancel to abort.
        """
        
        await query.edit_message_text(text)
        return AWAIT_THUMBNAIL_URL
    
    @staticmethod
    async def receive_thumbnail(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """
        Receive thumbnail for review
        """
        # Parse input
        if update.message.photo:
            photo = update.message.photo[-1]
            image_url = await photo.get_file()
            image_url = image_url.file_path
            
            await update.message.reply_text(
                "✅ Thumbnail received!\n\n"
                "Now send me the course name:"
            )
            
            context.user_data['thumbnail_url'] = image_url
            return AWAIT_THUMBNAIL_URL
        
        elif update.message.text:
            text = update.message.text
            
            # Try to parse course name and URL
            if 'Course Name:' in text and 'Image URL:' in text:
                lines = text.split('\n')
                course_name = None
                image_url = None
                
                for line in lines:
                    if 'Course Name:' in line:
                        course_name = line.split('Course Name:')[1].strip()
                    elif 'Image URL:' in line:
                        image_url = line.split('Image URL:')[1].strip()
                
                if course_name and image_url:
                    await update.message.reply_text("🔍 Reviewing thumbnail...")
                    
                    result = await ai_service.analyze_course_thumbnail(image_url, course_name)
                    
                    if result:
                        response = f"""
✅ **THUMBNAIL REVIEW COMPLETE**

🎨 **Course:** {course_name}
🖼️ **Thumbnail:** {image_url[:50]}...

📝 **AI Feedback:**
{result}

———————————————
🤖 Powered by Gemini 2.0 Flash Vision
                        """
                        
                        keyboard = [
                            [InlineKeyboardButton("🔄 Review Another", callback_data='vision_thumbnail')],
                            [InlineKeyboardButton("⬅️ Back", callback_data='vision_menu')]
                        ]
                        
                        await update.message.reply_text(
                            response,
                            reply_markup=InlineKeyboardMarkup(keyboard)
                        )
                    else:
                        await update.message.reply_text(
                            "❌ Review failed. Please try again."
                        )
                    
                    return ConversationHandler.END
            
            # If just course name (after photo upload)
            elif context.user_data.get('thumbnail_url'):
                course_name = text.strip()
                image_url = context.user_data['thumbnail_url']
                
                await update.message.reply_text("🔍 Reviewing thumbnail...")
                
                result = await ai_service.analyze_course_thumbnail(image_url, course_name)
                
                if result:
                    response = f"""
✅ **THUMBNAIL REVIEW COMPLETE**

🎨 **Course:** {course_name}

📝 **AI Feedback:**
{result}

———————————————
🤖 Powered by Gemini 2.0 Flash Vision
                    """
                    
                    keyboard = [
                        [InlineKeyboardButton("🔄 Review Another", callback_data='vision_thumbnail')],
                        [InlineKeyboardButton("⬅️ Back", callback_data='vision_menu')]
                    ]
                    
                    await update.message.reply_text(
                        response,
                        reply_markup=InlineKeyboardMarkup(keyboard)
                    )
                else:
                    await update.message.reply_text(
                        "❌ Review failed. Please try again."
                    )
                
                return ConversationHandler.END
        
        await update.message.reply_text(
            "❌ Invalid format. Please follow the format shown above."
        )
        return AWAIT_THUMBNAIL_URL
    
    @staticmethod
    async def start_payment_verification(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """
        Start payment proof verification
        """
        query = update.callback_query
        await query.answer()
        
        text = """
💳 **PAYMENT PROOF VERIFICATION**

Send me:
1. Payment screenshot URL
2. Or upload/forward the payment screenshot

I'll verify:
✅ Payment method (UPI/FamPay/etc)
✅ Transaction ID
✅ Amount paid
✅ Payment status
✅ Validity

Type /cancel to abort.
        """
        
        await query.edit_message_text(text)
        return AWAIT_PAYMENT_PROOF
    
    @staticmethod
    async def verify_payment_proof(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """
        Verify payment proof screenshot
        """
        # Get image
        if update.message.photo:
            photo = update.message.photo[-1]
            image_url = await photo.get_file()
            image_url = image_url.file_path
        elif update.message.text and update.message.text.startswith('http'):
            image_url = update.message.text.strip()
        else:
            await update.message.reply_text(
                "❌ Please send a payment screenshot or valid image URL."
            )
            return AWAIT_PAYMENT_PROOF
        
        await update.message.reply_text("🔍 Verifying payment proof...")
        
        try:
            result = await ai_service.analyze_payment_proof(image_url)
            
            if result and isinstance(result, dict):
                valid_emoji = "✅" if result.get('valid') else "❌"
                
                response = f"""
{valid_emoji} **PAYMENT VERIFICATION RESULT**

💳 **Method:** {result.get('method', 'N/A')}
💵 **Amount:** {result.get('amount', 'N/A')}
🆔 **Transaction ID:** {result.get('transaction_id', 'N/A')}
✅ **Status:** {result.get('status', 'N/A')}
📅 **Timestamp:** {result.get('timestamp', 'N/A')}
🎯 **Confidence:** {result.get('confidence', 'N/A')}

📝 **Notes:**
{result.get('notes', 'No additional notes')}

———————————————
🤖 Powered by Gemini 2.0 Flash Vision
                """
                
                keyboard = [
                    [InlineKeyboardButton("🔄 Verify Another", callback_data='vision_payment')],
                    [InlineKeyboardButton("⬅️ Back", callback_data='vision_menu')]
                ]
                
                await update.message.reply_text(
                    response,
                    reply_markup=InlineKeyboardMarkup(keyboard)
                )
            else:
                await update.message.reply_text(
                    "❌ Verification failed. The image may not be a valid payment proof."
                )
        
        except Exception as e:
            logger.error(f"Error in payment verification: {e}")
            await update.message.reply_text(
                f"❌ Error during verification: {str(e)}"
            )
        
        return ConversationHandler.END
    
    @staticmethod
    async def test_vision_api(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """
        Test vision API with sample image
        """
        query = update.callback_query
        await query.answer()
        
        await query.edit_message_text("🧪 Testing Vision API with sample image...")
        
        success = await ai_service.test_vision()
        
        if success:
            keyboard = [
                [InlineKeyboardButton("⬅️ Back to Vision Menu", callback_data='vision_menu')]
            ]
            
            await query.edit_message_text(
                "✅ **VISION API TEST SUCCESSFUL!**\n\n"
                "Gemini 2.0 Flash Vision is working perfectly!\n\n"
                "You can now use all vision features.",
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
        else:
            await query.edit_message_text(
                "❌ **VISION API TEST FAILED**\n\n"
                "Please check:\n"
                "1. API key is valid\n"
                "2. AI_ENABLED is True in config\n"
                "3. Network connection is stable"
            )
