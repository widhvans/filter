# bot.py (PEAK PERFORMANCE VERSION)

import logging
import re
import PTN  # यह हमारी नई शक्तिशाली लाइब्रेरी है
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


def get_clean_title(raw_text: str) -> str:
    """
    parse-torrent-name (PTN) लाइब्रेरी का उपयोग करके साफ़ टाइटल निकालता है।
    यह अब तक का सबसे प्रभावी तरीका है।
    """
    try:
        # PTN लाइब्रेरी से टेक्स्ट को पार्स करें
        parsed_info = PTN.parse(raw_text)

        # टाइटल निकालें
        title = parsed_info.get('title', '')
        
        # अगर यह एक टीवी शो है, तो सीजन, एपिसोड और एपिसोड का नाम जोड़ें
        if 'season' in parsed_info and 'episode' in parsed_info:
            season = parsed_info.get('season')
            episode = parsed_info.get('episode')
            
            # S01E05 जैसा फॉर्मेट बनाएं
            title_with_episode = f"{title} S{str(season).zfill(2)}E{str(episode).zfill(2)}"
            
            # यदि एपिसोड का नाम मौजूद है, तो उसे भी जोड़ें
            episode_name = parsed_info.get('episodeName')
            if episode_name:
                return f"{title_with_episode} {episode_name}".strip()
            else:
                return title_with_episode.strip()

        # अगर यह एक मूवी है, तो सिर्फ टाइटल लौटाएं
        return title.strip()
        
    except Exception as e:
        logger.error(f"Error parsing with PTN: {e}")
        # अगर PTN फेल हो जाता है, तो एक बेसिक क्लीनअप करें
        # साल और ब्रैकेट हटाएं
        text = re.sub(r'[\(\[].*?[\)\]]', '', raw_text)
        # पहले известная техническая информация
        match = re.split(r'720p|1080p|4k|web-dl|bluray|hdrip', text, flags=re.IGNORECASE)
        return match[0].replace('.', ' ').strip() if match else text.strip()


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """/start कमांड का जवाब देता है।"""
    user = update.effective_user
    await update.message.reply_html(
        f"नमस्ते {user.mention_html()}!\n\n"
        f"मुझे कोई भी मूवी/शो का फ़ाइलनेम भेजें और मैं आपको उसका बिल्कुल साफ़ नाम दूँगा।",
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """इनकमिंग मैसेज को हैंडल करता है।"""
    message = update.message or update.edited_message or update.channel_post

    # अगर मैसेज में टेक्स्ट नहीं है या मैसेज किसी दूसरे बॉट का है तो उसे अनदेखा करें
    if not message or not message.text or (message.from_user and message.from_user.is_bot):
        return

    user_message = message.text
    logger.info(f"Processing text: {user_message[:100]}")

    # हमारे नए शक्तिशाली फ़ंक्शन का उपयोग करें
    cleaned_name = get_clean_title(user_message)

    if cleaned_name:
        logger.info(f"Filtered name: {cleaned_name}")
        
        # उपयोगकर्ता के अनुरोध के अनुसार हेडर जोड़ें
        response_text = (
            f"Here is your cleared text:\n\n"
            f"**{cleaned_name}**"
        )
        
        try:
            # Markdown फॉर्मेट में जवाब भेजें
            await message.reply_text(response_text, parse_mode='Markdown')
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
    application.run_polling(drop_pending_updates=True)

if __name__ == '__main__':
    main()
