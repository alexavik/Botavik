# 🖼️ VISION AI FEATURES - Gemini 2.0 Flash

## 🌟 Overview

Your Botavik now has **vision capabilities** powered by **Gemini 2.0 Flash Vision API** through OpenRouter!

### What's New?

✅ **Image Analysis** - Analyze any image with AI
✅ **Thumbnail Review** - Get feedback on course thumbnails
✅ **Payment Verification** - Auto-verify payment screenshots
✅ **Streaming Support** - Real-time AI responses
✅ **Multimodal** - Text + Image in single API call

---

## 🚀 Quick Start

### 1. Test Vision API

In your Termux/Terminal:

```python
from services.ai_service import ai_service
import asyncio

# Test basic connection
async def test():
    result = await ai_service.test_vision()
    print("Vision API:", "Working ✅" if result else "Failed ❌")

asyncio.run(test())
```

### 2. Analyze an Image

```python
from services.ai_service import ai_service
import asyncio

async def analyze():
    image_url = "https://example.com/image.jpg"
    result = await ai_service.analyze_image(
        image_url=image_url,
        question="What is in this image?"
    )
    print(result)

asyncio.run(analyze())
```

---

## 📚 API Reference

### 1. `analyze_image(image_url, question)`

Analyze any image with custom question.

**Parameters:**
- `image_url` (str): Direct URL to the image
- `question` (str): Question to ask about the image

**Returns:**
- `str`: AI analysis or None if failed

**Example:**
```python
result = await ai_service.analyze_image(
    image_url="https://example.com/photo.jpg",
    question="Is this a professional photo?"
)
print(result)
```

---

### 2. `analyze_course_thumbnail(image_url, course_name)`

Get design feedback for course thumbnails.

**Parameters:**
- `image_url` (str): Thumbnail image URL
- `course_name` (str): Name of the course

**Returns:**
- `str`: Design feedback with rating and suggestions

**Example:**
```python
result = await ai_service.analyze_course_thumbnail(
    image_url="https://example.com/thumbnail.jpg",
    course_name="Python for Beginners"
)
print(result)
```

**Output example:**
```
🎨 Design Quality: 8/10

✅ Visible Elements:
- Professional Python logo
- Clean typography
- Gradient background

💡 Suggestions:
1. Add more contrast to text
2. Include course level badge
3. Use brighter colors for CTA

✅ Professional: Yes, suitable for course marketplace
```

---

### 3. `analyze_payment_proof(image_url)`

Verify payment screenshots automatically.

**Parameters:**
- `image_url` (str): Payment screenshot URL

**Returns:**
- `dict`: Verification details in JSON format

**Example:**
```python
result = await ai_service.analyze_payment_proof(
    image_url="https://example.com/payment.jpg"
)
print(result)
```

**Output example:**
```json
{
  "valid": true,
  "method": "UPI/FamPay",
  "amount": "₹499",
  "transaction_id": "TXN123456789",
  "status": "Success",
  "timestamp": "2025-12-31 08:15 AM",
  "confidence": "High",
  "notes": "Valid UPI payment with clear transaction details visible"
}
```

---

## 👨‍💻 Usage in Telegram Bot

### Access Vision Features

1. Open your bot in Telegram
2. Send `/admin` (or click Admin button)
3. Click `🤖 AI Assistant`
4. Click `🖼️ Vision AI` (new button)

### Vision Menu Options

```
🖼️ Analyze Image - Analyze any image
🇿 Review Thumbnail - Get design feedback
💳 Verify Payment - Auto-verify payments
🧪 Test Vision - Test API connection
```

---

## 🛠️ Integration Examples

### Example 1: Auto-verify User Payments

```python
from services.ai_service import ai_service

async def verify_user_payment(user_id, screenshot_url):
    """
    Automatically verify user payment screenshot
    """
    result = await ai_service.analyze_payment_proof(screenshot_url)
    
    if result and result.get('valid'):
        amount = result.get('amount')
        txn_id = result.get('transaction_id')
        
        # Grant access to user
        await grant_course_access(user_id, amount)
        
        return {
            'verified': True,
            'amount': amount,
            'txn_id': txn_id
        }
    else:
        return {'verified': False, 'reason': 'Invalid payment proof'}
```

### Example 2: Review Course Thumbnails

```python
from services.ai_service import ai_service

async def review_course_creation(course_data):
    """
    Review course thumbnail before publishing
    """
    thumbnail_url = course_data['thumbnail_url']
    course_name = course_data['name']
    
    feedback = await ai_service.analyze_course_thumbnail(
        image_url=thumbnail_url,
        course_name=course_name
    )
    
    # Show feedback to admin
    return feedback
```

### Example 3: Image-based Course Search

```python
from services.ai_service import ai_service

async def find_similar_courses(image_url):
    """
    Find courses similar to image content
    """
    analysis = await ai_service.analyze_image(
        image_url=image_url,
        question="What topics or subjects are shown in this image? List them."
    )
    
    # Extract topics and search database
    topics = extract_topics(analysis)
    courses = search_courses_by_topics(topics)
    
    return courses
```

---

## ⚙️ Configuration

### Environment Variables

Make sure these are set in your Railway/Render environment:

```env
OPENROUTER_API_KEY=sk-or-v1-your-key-here
AI_MODEL=google/gemini-2.0-flash-exp:free
AI_ENABLED=True
```

### Model Info

**Model:** `google/gemini-2.0-flash-exp:free`

**Capabilities:**
- ✅ Text generation
- ✅ Image analysis (vision)
- ✅ Multimodal (text + image)
- ✅ Streaming responses
- ✅ FREE tier available!

**Limits:**
- Max image size: 10MB
- Supported formats: JPG, PNG, WebP, GIF
- Rate limit: Depends on API key tier

---

## 🔧 Advanced Usage

### Streaming Responses

For real-time AI responses:

```python
result = await ai_service._call_vision_api(
    text="Describe this image",
    image_url="https://example.com/image.jpg",
    stream=True  # Enable streaming
)
```

### Batch Image Analysis

```python
import asyncio

async def analyze_multiple_images(image_urls):
    tasks = [
        ai_service.analyze_image(url, "Describe this image")
        for url in image_urls
    ]
    results = await asyncio.gather(*tasks)
    return results

# Analyze 5 images concurrently
images = ["url1", "url2", "url3", "url4", "url5"]
results = await analyze_multiple_images(images)
```

---

## ❌ Troubleshooting

### Issue 1: "Vision API test failed"

**Solution:**
```bash
# Check API key
echo $OPENROUTER_API_KEY

# Verify AI is enabled
echo $AI_ENABLED  # Should be True

# Test manually
python3 -c "from services.ai_service import ai_service; import asyncio; print(asyncio.run(ai_service.test_connection()))"
```

### Issue 2: "Image analysis returns None"

**Reasons:**
- Image URL is not accessible
- Image format not supported
- API rate limit reached
- Network timeout

**Solution:**
```python
# Add error handling
try:
    result = await ai_service.analyze_image(image_url, question)
    if result:
        print(result)
    else:
        print("Analysis failed - check logs")
except Exception as e:
    print(f"Error: {e}")
```

### Issue 3: "Payment verification not accurate"

**Tips:**
- Use high-resolution screenshots
- Ensure text is clearly visible
- Avoid cropped or zoomed images
- Include full transaction details

---

## 📊 Performance Tips

1. **Cache Results:**
```python
from functools import lru_cache

@lru_cache(maxsize=100)
async def cached_image_analysis(image_url, question):
    return await ai_service.analyze_image(image_url, question)
```

2. **Optimize Image URLs:**
- Use CDN links for faster loading
- Compress images before analysis
- Use direct image URLs (not HTML pages)

3. **Handle Timeouts:**
```python
import asyncio

try:
    result = await asyncio.wait_for(
        ai_service.analyze_image(url, question),
        timeout=30  # 30 seconds max
    )
except asyncio.TimeoutError:
    print("Analysis timed out")
```

---

## 🎉 What's Next?

### Future Enhancements

- [ ] Bulk image processing
- [ ] Image comparison (A vs B)
- [ ] OCR text extraction
- [ ] Face detection/recognition
- [ ] Object detection
- [ ] Image quality scoring
- [ ] Auto-tagging images

---

## 📝 Example Use Cases

### For Course Platform:

1. **Thumbnail Quality Check:**
   - Auto-review all course thumbnails
   - Reject low-quality designs
   - Suggest improvements

2. **Payment Automation:**
   - Auto-verify UPI screenshots
   - Extract transaction IDs
   - Grant instant access

3. **Content Moderation:**
   - Check uploaded images for inappropriate content
   - Verify course preview images
   - Ensure brand consistency

4. **Smart Search:**
   - Upload image to find similar courses
   - Visual course recommendations
   - Image-based categorization

---

## 🔗 Resources

- **OpenRouter Docs:** https://openrouter.ai/docs
- **Gemini 2.0 Flash:** https://ai.google.dev/gemini-api
- **Vision API Guide:** https://openrouter.ai/docs/multimodal
- **Python SDK:** https://github.com/openrouter/openrouter-sdk

---

## ✅ Testing Checklist

Before deployment, test:

- [ ] Basic image analysis works
- [ ] Thumbnail review provides feedback
- [ ] Payment verification extracts details
- [ ] Error handling works properly
- [ ] Timeout handling in place
- [ ] Logging captures all events
- [ ] Admin dashboard integration works
- [ ] Telegram photo uploads work

---

**Version:** 1.0.0  
**Last Updated:** December 31, 2025  
**Model:** google/gemini-2.0-flash-exp:free  
**Status:** 🟢 Production Ready

---

**Made with ❤️ by Avik | Powered by Gemini 2.0 Flash Vision**
