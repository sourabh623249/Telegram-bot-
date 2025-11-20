from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import re
import time
import os
from flask import Flask

# Bot Configuration
BOT_TOKEN = os.environ.get("BOT_TOKEN", "YOUR_BOT_TOKEN_HERE")
CHAT_ID = os.environ.get("CHAT_ID", "YOUR_CHAT_ID_HERE")

# Flask app for Render
app = Flask(__name__)

@app.route('/')
def home():
    return "🤖 Telegram SMS Forwarder Bot is Running!"

@app.route('/health')
def health():
    return "✅ Bot is Healthy"

copy_data = {}

async def handle_sms(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """SMS forward karte hi direct click-to-copy message"""
    message_text = update.message.text
    
    # Extract number
    outgoing_match = re.search(r'Outgoing\s*:\s*(\d{10,})', message_text)
    number = outgoing_match.group(1) if outgoing_match else None
    
    # Extract token (multi-line support)
    lines = message_text.split('\n')
    token_parts = []
    
    for line in lines:
        if re.search(r'[A-Za-z0-9]{20,}', line):
            token_parts.append(line.strip())
    
    complete_token = ' '.join(token_parts) if token_parts else None
    
    # Create unique ID
    msg_id = int(time.time() * 1000)
    
    # Store data
    if number:
        copy_data[f"num_{msg_id}"] = number
    
    if complete_token and len(complete_token) > 20:
        copy_data[f"tok_{msg_id}"] = complete_token
    
    copy_data[f"full_{msg_id}"] = message_text
    
    # Send separate clickable messages
    if number:
        await context.bot.send_message(
            chat_id=CHAT_ID,
            text=f"`{number}`",
            parse_mode='MarkdownV2'
        )
    
    if complete_token and len(complete_token) > 20:
        await context.bot.send_message(
            chat_id=CHAT_ID,
            text=f"`{complete_token}`",
            parse_mode='MarkdownV2'
        )
    
    await context.bot.send_message(
        chat_id=CHAT_ID,
        text=f"`{message_text}`",
        parse_mode='MarkdownV2'
    )

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🤖 Direct Copy Bot - Forward SMS, click text to copy")

async def setup(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global CHAT_ID
    CHAT_ID = update.message.chat_id
    await update.message.reply_text(f"✅ {CHAT_ID}")

def main():
    # Create application
    application = Application.builder().token(BOT_TOKEN).build()
    
    # Add handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("setup", setup))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_sms))
    
    print("🚀 BOT STARTED ON RENDER!")
    
    # Start polling
    application.run_polling()

if __name__ == "__main__":
    # Start Flask app in separate thread for Render
    from threading import Thread
    flask_thread = Thread(target=lambda: app.run(host='0.0.0.0', port=5000, debug=False))
    flask_thread.daemon = True
    flask_thread.start()
    
    # Start Telegram bot
    main()