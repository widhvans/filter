# bot.py (Fixed Version 2)

import logging
import re
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# config.py से बॉट टोकन इम्पोर्ट करें
from config import TELEGRAM_BOT_TOKEN

# लॉगिंग सेट अप करें
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# इन कीवर्ड्स को ग्लोबल बना दें ताकि दोनों फंक्शन्स में इस्तेमाल हो सकें
UNWANTED_KEYWORDS = [
    '1080p', '720p', '480p', '2160p', '4k', 'bluray', 'blu-ray', 'web-dl', 'hdrip', 
    'webrip', 'hdtv', 'x264', 'x265', 'hevc', 'aac', 'dd5.1', 'dual audio', 'hindi',
    'english', 'telugu', 'tamil', 'multi', 'subbed', 'dubbed'
]

def filter_movie_name(raw_text: str) -> str:
    """यह फ़ंक्शन रॉ टेक्स्ट में से मूवी का नाम फ़िल्टर करता है।"""
    text = raw_text
    
    # 1. ब्रैकेट () और [] में मौजूद किसी भी चीज़ को हटा दें
    text = re.sub(r'[\(\[].*?[\)\]]', '', text)

    # 2. सामान्य कीवर्ड और क्वालिटी टैग्स को हटा दें
    pattern = r'\b(' + '|'.join(UNWANTED_KEYWORDS) + r')\b'
    text = re.sub(pattern, '', text, flags=re.IGNORECASE)

    # 3. डॉट्स, अंडरस्कोर को स्पेस से बदलें
    text = text.replace('.', ' ').replace('_', ' ')

    # 4. विशेष सिंबल हटा दें
    text = re.sub(r'[^\w\s]', '', text)

    # 5. अतिरिक्त स्पेस को हटा दें
    cleaned_name = ' '.join(text.split()).strip()

    return cleaned_name

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """/start कमांड का जवाब देता है।"""
    user = update.effective_user
    await update.message.reply_html(
        f"नमस्ते {user.mention_html()}!\n\n"
        f"मुझे कोई भी मूवी का नाम भेजें और मैं उसे साफ़ करके आपको दूँगा।",
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """इनकमिंग मैसेज को हैंडल करता है।"""
    message = update.message or update.edited_message or update.channel_post

    # ## --- यहाँ सुधार किए गए हैं --- ##

    # 1. अगर मैसेज में टेक्स्ट नहीं है या मैसेज किसी दूसरे बॉट का है तो उसे अनदेखा करें
    if not message or not message.text or (message.from_user and message.from_user.is_bot):
        return

    user_message = message.text
    
    # 2. जांचें कि क्या मैसेज में मूवी से संबंधित कोई कीवर्ड है।
    #    इससे बॉट सामान्य बातचीत का जवाब नहीं देगा।
    #    `r'\b\d{4}\b'` साल (जैसे 2023) की जांच करता है।
    contains_movie_keyword = any(re.search(r'\b' + re.escape(keyword) + r'\b', user_message, re.IGNORECASE) for keyword in UNWANTED_KEYWORDS)
    contains_year = re.search(r'\b\d{4}\b', user_message)

    if not contains_movie_keyword and not contains_year:
        logger.info(f"Ignoring general chat message: {user_message[:50]}...")
        return
        
    # ## --- सुधार समाप्त --- ##

    logger.info(f"Processing text: {user_message[:100]}")

    cleaned_name = filter_movie_name(user_message)

    if cleaned_name:
        logger.info(f"Filtered name: {cleaned_name}")
        try:
            # Markdown का उपयोग करने से बचें ताकि कोई एरर न आए
            await message.reply_text(cleaned_name)
        except Exception as e:
            logger.error(f"Failed to send message: {e}")
    else:
        logger.warning("Could not extract a valid name from the text.")
        await message.reply_text("माफ़ करें, मुझे इस टेक्स्ट में से कोई मान्य नाम नहीं मिला।")

def main() -> None:
    """बॉट को स्टार्ट करता है।"""
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    logger.info("Starting bot...")
    application.run_polling(drop_pending_updates=True) # पुरानी पेंडिंग अपडेट्स को हटा दें

if __name__ == '__main__':
    main()
