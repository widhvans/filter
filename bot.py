# bot.py (Fixed Version)

import logging
import re
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# config.py से बॉट टोकन इम्पोर्ट करें
from config import TELEGRAM_BOT_TOKEN

# लॉगिंग सेट अप करें ताकि आपको पता चले कि बॉट क्या कर रहा है
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

logger = logging.getLogger(__name__)

def filter_movie_name(raw_text: str) -> str:
    """
    यह फ़ंक्शन रॉ टेक्स्ट में से मूवी का नाम फ़िल्टर करता है।
    """
    # 1. ब्रैकेट () और [] में मौजूद किसी भी चीज़ को हटा दें (जैसे साल, भाषा)
    text = re.sub(r'[\(\[].*?[\)\]]', '', raw_text)

    # 2. सामान्य कीवर्ड और क्वालिटी टैग्स को हटा दें (case-insensitive)
    unwanted_keywords = [
        '1080p', '720p', '480p', '4k', 'bluray', 'web-dl', 'hdrip', 'webrip', 'hdtv',
        'x264', 'x265', 'hevc', 'aac', 'dd5.1', 'dual audio', 'hindi', 'english',
        'telugu', 'tamil', 'multi'
    ]
    pattern = r'\b(' + '|'.join(unwanted_keywords) + r')\b'
    text = re.sub(pattern, '', text, flags=re.IGNORECASE)

    # 3. डॉट्स, अंडरस्कोर को स्पेस से बदलें
    text = text.replace('.', ' ').replace('_', ' ')

    # 4. विशेष सिंबल हटा दें जो अभी भी बचे हों (अक्षर, अंक और स्पेस को छोड़कर)
    text = re.sub(r'[^\w\s]', '', text)

    # 5. अतिरिक्त स्पेस को हटा दें और शुरुआत/अंत के स्पेस को हटा दें
    cleaned_name = ' '.join(text.split()).strip()

    return cleaned_name

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """/start कमांड भेजने पर यह फ़ंक्शन चलता है।"""
    user = update.effective_user
    await update.message.reply_html(
        f"नमस्ते {user.mention_html()}!\n\n"
        f"मुझे कोई भी मूवी का नाम भेजें (जैसे: Jawan (2023) [Hindi] 1080p) और मैं उसे साफ़ करके आपको दूँगा।",
    )

# ######################################################################
# ##               यहाँ बदलाव किया गया है (CHANGES ARE HERE)           ##
# ######################################################################

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """टेक्स्ट मैसेज को हैंडल करता है, जिसमें एडिट किए गए मैसेज और चैनल पोस्ट भी शामिल हैं।"""
    # स्टेप 1: सही मैसेज ऑब्जेक्ट को ढूंढें
    # यह या तो नया मैसेज (update.message) हो सकता है, एडिट किया गया मैसेज (update.edited_message),
    # या चैनल पोस्ट (update.channel_post)
    message = update.message or update.edited_message or update.channel_post

    # स्टेप 2: जांचें कि मैसेज और उसमें टेक्स्ट मौजूद है या नहीं
    # अगर नहीं, तो फंक्शन से बाहर निकल जाएं ताकि कोई एरर न आए
    if not message or not message.text:
        logger.info("Received an update without processable text, ignoring.")
        return

    user_message = message.text
    logger.info(f"Received text: {user_message}")

    # मूवी का नाम फ़िल्टर करें
    cleaned_name = filter_movie_name(user_message)

    if cleaned_name:
        logger.info(f"Filtered name: {cleaned_name}")
        # जवाब देने के लिए `message.reply_text` का उपयोग करें
        # ताकि यह सही चैट (नए मैसेज, एडिटेड मैसेज या चैनल पोस्ट) में जवाब दे
        await message.reply_text(f"`{cleaned_name}`", parse_mode='MarkdownV2')
    else:
        logger.warning("Could not extract a valid name from the text.")
        await message.reply_text("माफ़ करें, मुझे इस टेक्स्ट में से कोई मान्य नाम नहीं मिला।")

def main() -> None:
    """बॉट को स्टार्ट करता है।"""
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    logger.info("Starting bot...")
    application.run_polling()

if __name__ == '__main__':
    main()
