import os
import re
import logging
import asyncio
import httpx
from telegram import Update
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler,
    ContextTypes, filters
)

API_BASE = os.getenv("API_BASE", "http://127.0.0.1:8000")
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

URL_REGEX = re.compile(
    r'(https?://[^\s]+)', re.IGNORECASE
)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        "👋 Namaste! I am your Phishing Awareness Bot.\n\n"
        "Send me any suspicious *message* or *link* and I’ll analyze it.\n\n"
        "Examples:\n"
        "• Paste an SMS or WhatsApp message from an unknown number.\n"
        "• Send a link you are not sure about.\n\n"
        "I'll reply with a risk level (LOW/MEDIUM/HIGH) and explain why. 🕵️‍♂️"
    )
    await update.message.reply_markdown(text)

async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        "🛡 *How to use me:*\n\n"
        "• Just send any suspicious text or URL.\n"
        "• If it's a link, I’ll treat it as URL.\n"
        "• If it's a normal message, I’ll analyze the text.\n\n"
        "Remember: Bank kabhi bhi OTP, PIN, ya password nahi maangta. 💡"
    )
    await update.message.reply_markdown(text)

async def analyze_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text:
        return

    user_text = update.message.text.strip()
    urls = URL_REGEX.findall(user_text)

    async with httpx.AsyncClient(timeout=10) as client:
        try:
            if len(urls) == 1 and user_text.strip() == urls[0]:
                # Pure URL message
                payload = {"url": urls[0]}
                resp = await client.post(f"{API_BASE}/analyze/url", json=payload)
                data = resp.json()
            elif len(urls) >= 1:
                # Mixed message, focus on first URL
                payload = {"url": urls[0]}
                resp = await client.post(f"{API_BASE}/analyze/url", json=payload)
                data = resp.json()
                data["reasons"].append("Message also contains additional text; be extra careful.")
            else:
                # No URL → treat as text
                payload = {"text": user_text}
                resp = await client.post(f"{API_BASE}/analyze/text", json=payload)
                data = resp.json()
        except Exception as e:
            logger.error(f"Error calling API: {e}")
            await update.message.reply_text(
                "❌ Sorry, I couldn't reach the analyzer service. Try again later."
            )
            return

    risk = data["risk"]
    score = data["score"]
    reasons = data["reasons"]
    advice = data["advice"]
    analysis_type = data["type"]

    emoji = {"LOW": "🟢", "MEDIUM": "🟠", "HIGH": "🔴"}.get(risk, "⚪")

    reply = (
        f"{emoji} *Risk Level:* {risk}\n"
        f"📊 *Score:* {score:.2f}\n"
        f"📂 *Type:* {analysis_type.upper()}\n\n"
        f"*Why I think so:*\n"
        + "\n".join([f"• {r}" for r in reasons])
        + "\n\n"
        f"*Advice:* {advice}\n\n"
        "_Tip: Never share OTP, PIN, CVV or passwords with anyone._"
    )

    await update.message.reply_markdown(reply)

async def main():
    if not BOT_TOKEN:
        raise RuntimeError("Set TELEGRAM_BOT_TOKEN env variable")

    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_cmd))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, analyze_message))

    logger.info("Bot starting...")
    await app.run_polling()

if __name__ == "__main__":
    asyncio.run(main())
