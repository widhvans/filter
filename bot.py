# bot.py

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
    # उदाहरण: "(2023)", "[Hindi]"
    text = re.sub(r'[\(\[].*?[\)\]]', '', raw_text)

    # 2. सामान्य कीवर्ड और क्वालिटी टैग्स को हटा दें (case-insensitive)
    # उदाहरण: "1080p", "720p", "BluRay", "WEBRip", "x264"
    unwanted_keywords = [
        '1080p', '720p', '480p', '4k', 'bluray', 'web-dl', 'hdrip', 'webrip', 'hdtv',
        'x264', 'x265', 'hevc', 'aac', 'dd5.1', 'dual audio', 'hindi', 'english',
        'telugu', 'tamil', 'multi'
    ]
    # regex पैटर्न बनाएं: \b(word1|word2|...)\b
    # \b यह सुनिश्चित करता है कि पूरा शब्द मैच हो
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

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """टेक्स्ट मैसेज को हैंडल करता है।"""
    user_message = update.message.text
    logger.info(f"User '{update.effective_user.first_name}' sent: {user_message}")

    # मूवी का नाम फ़िल्टर करें
    cleaned_name = filter_movie_name(user_message)

    if cleaned_name:
        logger.info(f"Filtered name: {cleaned_name}")
        await update.message.reply_text(f"`{cleaned_name}`", parse_mode='MarkdownV2')
    else:
        logger.warning("Could not extract a valid name.")
        await update.message.reply_text("माफ़ करें, मुझे इस टेक्स्ट में से कोई मान्य नाम नहीं मिला।")

def main() -> None:
    """बॉट को स्टार्ट करता है।"""
    # एप्लीकेशन बनाएं
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    # कमांड हैंडलर जोड़ें
    application.add_handler(CommandHandler("start", start))

    # मैसेज हैंडलर जोड़ें (यह कमांड के अलावा सभी टेक्स्ट मैसेज पर चलेगा)
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # बॉट को चलाना शुरू करें
    logger.info("Starting bot...")
    application.run_polling()

if __name__ == '__main__':
    main()
