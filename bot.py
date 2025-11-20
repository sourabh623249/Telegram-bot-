from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import re
import os
from flask import Flask

# Bot Configuration - DIRECT FROM ENVIRONMENT
BOT_TOKEN = os.environ.get("BOT_TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")

# Flask app for Render
app = Flask(__name__)

@app.route('/')
def home():
    return "🤖 Telegram SMS Forwarder Bot is Running!"

@app.route('/health')
def health():
    return "✅ Bot is Healthy"

async def handle_sms(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """SMS forward karte hi direct click-to-copy message"""
    try:
        message_text = update.message.text
        
        # Send original message for full copy
        await context.bot.send_message(
            chat_id=CHAT_ID,
            text=f"`{message_text}`",
            parse_mode='MarkdownV2'
        )
        
        # Extract and send number separately
        outgoing_match = re.search(r'Outgoing\s*:\s*(\d{10,})', message_text)
        if outgoing_match:
            number = outgoing_match.group(1)
            await context.bot.send_message(
                chat_id=CHAT_ID,
                text=f"`{number}`",
                parse_mode='MarkdownV2'
            )
        
        # Extract and send token separately
        lines = message_text.split('\n')
        token_parts = []
        
        for line in lines:
            if re.search(r'[A-Za-z0-9]{20,}', line):
                token_parts.append(line.strip())
        
        if token_parts:
            complete_token = ' '.join(token_parts)
            await context.bot.send_message(
                chat_id=CHAT_ID,
                text=f"`{complete_token}`",
                parse_mode='MarkdownV2'
            )
        
        await update.message.reply_text("✅ SMS processed! Click any text to copy.")
        
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {str(e)}")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🤖 SMS Copy Bot\n\n"
        "Forward any SMS → Click text to copy instantly!\n\n"
        "✅ Number - Separate copy\n"
        "✅ Token - Separate copy\n" 
        "✅ Full message - Separate copy"
    )

async def setup(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_chat_id = update.message.chat_id
    await update.message.reply_text(f"✅ Your Chat ID: {user_chat_id}")

def main():
    # Validate environment variables
    if not BOT_TOKEN or not CHAT_ID:
        print("❌ ERROR: BOT_TOKEN or CHAT_ID not set in environment variables")
        return
    
    # Create application
    application = Application.builder().token(BOT_TOKEN).build()
    
    # Add handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("setup", setup))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_sms))
    
    print("🚀 BOT STARTED ON RENDER!")
    print(f"✅ Bot Token: {BOT_TOKEN[:10]}...")
    print(f"✅ Chat ID: {CHAT_ID}")
    
    # Start polling
    application.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    # Start Flask app for Render health checks
    from threading import Thread
    flask_thread = Thread(target=lambda: app.run(host='0.0.0.0', port=5000, debug=False, use_reloader=False))
    flask_thread.daemon = True
    flask_thread.start()
    
    # Start Telegram bot
    main()
