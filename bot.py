import os
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes

TOKEN = os.environ.get("TOKEN", "YOUR_TOKEN")
ADMIN_ID = 123456789

OWNER_PHONE = "+998930352203"
PARTNER_PHONE = "+998946373090"

# Menyu: kategoriya -> [(mahsulot nomi, narx matni), ...]
MENU = {
    "🌯 Lavash & Hotdog": [
        ("Lavash", "25,000 - 40,000 so'm (turiga qarab)"),
        ("Hotdog", "15,000 - 40,000 so'm (turiga qarab)"),
    ],
    "🥤 Ichimliklar": [
        ("Chalop", "5,000 so'mdan"),
        ("Boshqa ichimliklar", "narxi qo'ng'iroqda aytiladi"),
    ],
    "🍦 Muzqaymoq & Marjon": [
        ("Muzqaymoq", "5,000 so'mdan boshlanadi"),
        ("Marjon va boshqa turlari", "narxi qo'ng'iroqda aytiladi"),
    ],
    "🍿 Qo'shimcha mahsulotlar": [
        ("Suxariklar va boshqalar", "narxi qo'ng'iroqda aytiladi"),
    ],
}

user_reviews = {}
user_states = {}

# ===================== BOSH SAHIFA =====================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    keyboard = [
        [InlineKeyboardButton("🛍️ Mahsulotlar", callback_data="products"),
         InlineKeyboardButton("🎯 Aksiyalar", callback_data="sales")],
        [InlineKeyboardButton("⭐ Izohlar", callback_data="reviews"),
         InlineKeyboardButton("ℹ️ Haqimizda", callback_data="about")],
        [InlineKeyboardButton("📞 Zakaz berish", callback_data="order_contact")],
        [InlineKeyboardButton("🤝 Hamkorlik", callback_data="partner")],
    ]
    text = (
        "🌿 BUSTON FOOD 🌿\n"
        "Mazali • Tez • Arzon\n\n"
        f"Assalomu alaykum, {user.first_name}!\n\n"
        "Menyumizda:\n"
        "🌯 Lavash & Hotdog\n"
        "🥤 Ichimliklar\n"
        "🍦 Muzqaymoq va marjon\n"
        "🍿 Qo'shimcha mahsulotlar\n\n"
        "🚚 Yetkazib berish: Buston bo'ylab\n\n"
        "Bo'limni tanlang:"
    )
    if update.message:
        await update.message.reply_text(text, reply_markup=InlineKeyboardMarkup(keyboard))
    else:
        await update.callback_query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard))

# ===================== KATEGORIYALAR =====================
async def show_categories(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    keyboard = []
    for cat in MENU:
        keyboard.append([InlineKeyboardButton(cat, callback_data=f"cat_{cat}")])
    keyboard.append([InlineKeyboardButton("🏠 Bosh sahifa", callback_data="home")])
    await query.edit_message_text(
        "📦 Kategoriyalar\n\nBo'limni tanlang:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

# ===================== MAHSULOTLAR / NARXLAR =====================
async def show_products(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    category = query.data.replace("cat_", "")
    text = f"{category}\n\n"
    for name, price_text in MENU[category]:
        text += f"▸ {name} — {price_text}\n"
    text += "\nBuyurtma berish uchun pastdagi tugmani bosing."
    keyboard            
