from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
import re
import os
import logging

# Set up logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# Bot Configuration
BOT_TOKEN = os.environ.get("BOT_TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")

def handle_sms(update: Update, context: CallbackContext):
    """SMS forward karte hi direct click-to-copy message"""
    try:
        message_text = update.message.text
        
        # Send original message for full copy
        context.bot.send_message(
            chat_id=CHAT_ID,
            text=f"`{message_text}`",
            parse_mode='MarkdownV2'
        )
        
        # Extract and send number separately
        outgoing_match = re.search(r'Outgoing\s*:\s*(\d{10,})', message_text)
        if outgoing_match:
            number = outgoing_match.group(1)
            context.bot.send_message(
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
            context.bot.send_message(
                chat_id=CHAT_ID,
                text=f"`{complete_token}`",
                parse_mode='MarkdownV2'
            )
        
        update.message.reply_text("✅ SMS processed! Click any text to copy.")
        
    except Exception as e:
        update.message.reply_text(f"❌ Error: {str(e)}")

def start(update: Update, context: CallbackContext):
    update.message.reply_text(
        "🤖 SMS Copy Bot\n\n"
        "Forward any SMS → Click text to copy instantly!\n\n"
        "✅ Number - Separate copy\n"
        "✅ Token - Separate copy\n" 
        "✅ Full message - Separate copy"
    )

def setup(update: Update, context: CallbackContext):
    user_chat_id = update.message.chat_id
    update.message.reply_text(f"✅ Your Chat ID: {user_chat_id}")

def main():
    # Validate environment variables
    if not BOT_TOKEN or not CHAT_ID:
        print("❌ ERROR: BOT_TOKEN or CHAT_ID not set in environment variables")
        return
    
    # Create updater
    updater = Updater(BOT_TOKEN, use_context=True)
    
    # Get dispatcher
    dp = updater.dispatcher
    
    # Add handlers
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("setup", setup))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_sms))
    
    print("🚀 BOT STARTED ON RENDER!")
    print(f"✅ Bot Token: {BOT_TOKEN[:10]}...")
    print(f"✅ Chat ID: {CHAT_ID}")
    
    # Start polling
    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
