from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes

# TOKEN ni shu yerga yozing
TOKEN = "8772106926:AAFLFhvELrajGsChbpc8wyhvujh0FZaPVzI"

# Mahsulotlar (o'zingiznikini qo'shing)
PRODUCTS = {
    "🍎 Mevalar": {
        "Olma": 5000,
        "Banan": 8000,
        "Apelsin": 7000,
    },
    "🥦 Sabzavotlar": {
        "Pomidor": 4000,
        "Bodring": 3000,
        "Karam": 2500,
    },
    "🥛 Sut mahsulotlari": {
        "Sut (1L)": 6000,
        "Qatiq": 4500,
        "Pishloq": 15000,
    }
}

# Savatcha (har user uchun)
user_carts = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("🛍️ Mahsulotlar", callback_data="products")],
        [InlineKeyboardButton("🛒 Savatcha", callback_data="cart")],
        [InlineKeyboardButton("📞 Bog'lanish", callback_data="contact")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "🌿 *BustonFood* ga xush kelibsiz!\n\n"
        "Yangi va sifatli oziq-ovqat mahsulotlari 🥗\n\n"
        "Quyidagi bo'limlardan birini tanlang:",
        reply_markup=reply_markup,
        parse_mode="Markdown"
    )

async def show_categories(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    keyboard = []
    for category in PRODUCTS:
        keyboard.append([InlineKeyboardButton(category, callback_data=f"cat_{category}")])
    keyboard.append([InlineKeyboardButton("🔙 Orqaga", callback_data="back")])
    await query.edit_message_text(
        "📦 Kategoriyani tanlang:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def show_products(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    category = query.data.replace("cat_", "")
    keyboard = []
    for product, price in PRODUCTS[category].items():
        keyboard.append([InlineKeyboardButton(
            f"{product} — {price:,} so'm",
            callback_data=f"add_{product}_{price}"
        )])
    keyboard.append([InlineKeyboardButton("🔙 Orqaga", callback_data="products")])
    await query.edit_message_text(
        f"{category} mahsulotlari:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def add_to_cart(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    parts = query.data.split("_", 2)
    product = parts[1]
    price = int(parts[2])
    if user_id not in user_carts:
        user_carts[user_id] = {}
    if product in user_carts[user_id]:
        user_carts[user_id][product]["qty"] += 1
    else:
        user_carts[user_id][product] = {"price": price, "qty": 1}
    await query.answer(f"✅ {product} savatchaga qo'shildi!", show_alert=True)

async def show_cart(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    cart = user_carts.get(user_id, {})
    if not cart:
        await query.edit_message_text(
            "🛒 Savatchangiz bo'sh!\n\nMahsulot qo'shish uchun '🛍️ Mahsulotlar' ni bosing.",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Orqaga", callback_data="back")]])
        )
        return
    text = "🛒 *Sizning savatchаngiz:*\n\n"
    total = 0
    for product, info in cart.items():
        subtotal = info["price"] * info["qty"]
        text += f"• {product} x{info['qty']} = {subtotal:,} so'm\n"
        total += subtotal
    text += f"\n💰 *Jami: {total:,} so'm*"
    keyboard = [
        [InlineKeyboardButton("✅ Buyurtma berish", callback_data="order")],
        [InlineKeyboardButton("🗑️ Tozalash", callback_data="clear_cart")],
        [InlineKeyboardButton("🔙 Orqaga", callback_data="back")],
    ]
    await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")

async def clear_cart(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    user_carts[user_id] = {}
    await query.answer("🗑️ Savatcha tozalandi!", show_alert=True)
    await show_cart(update, context)

async def order(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    cart = user_carts.get(user_id, {})
    total = sum(i["price"] * i["qty"] for i in cart.values())
    # ADMIN ga xabar yuborish (o'z ID ingizni yozing)
    ADMIN_ID = 123456789  # ← o'zingizning Telegram ID ingiz
    order_text = f"🆕 Yangi buyurtma!\n\nMijoz: @{query.from_user.username}\n\n"
    for product, info in cart.items():
        order_text += f"• {product} x{info['qty']}\n"
    order_text += f"\n💰 Jami: {total:,} so'm"
    await context.bot.send_message(ADMIN_ID, order_text)
    user_carts[user_id] = {}
    await query.edit_message_text(
        "✅ *Buyurtmangiz qabul qilindi!*\n\n"
        "Tez orada siz bilan bog'lanamiz 📞\n\n"
        "Rahmat, BustonFood dan xarid qilganingiz uchun! 🌿",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🏠 Bosh sahifa", callback_data="back")]])
    )

async def contact(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text(
        "📞 *Bog'lanish:*\n\n"
        "📱 Telefon: +998 XX XXX XX XX\n"
        "📍 Manzil: Shahar, ko'cha\n"
        "🕐 Ish vaqti: 9:00 - 21:00",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Orqaga", callback_data="back")]])
    )

async def back(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    keyboard = [
        [InlineKeyboardButton("🛍️ Mahsulotlar", callback_data="products")],
        [InlineKeyboardButton("🛒 Savatcha", callback_data="cart")],
        [InlineKeyboardButton("📞 Bog'lanish", callback_data="contact")],
    ]
    await query.edit_message_text(
        "🌿 *BustonFood*\n\nQuyidagi bo'limlardan birini tanlang:",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="Markdown"
    )
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"BustonFood bot ishlayapti!")
    def log_message(self, format, *args):
        pass

def run_server():
    HTTPServer(('0.0.0.0', 8080), Handler).serve_forever()

threading.Thread(target=run_server, daemon=True).start()
def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(show_categories, pattern="^products$"))
    app.add_handler(CallbackQueryHandler(show_products, pattern="^cat_"))
    app.add_handler(CallbackQueryHandler(add_to_cart, pattern="^add_"))
    app.add_handler(CallbackQueryHandler(show_cart, pattern="^cart$"))
    app.add_handler(CallbackQueryHandler(clear_cart, pattern="^clear_cart$"))
    app.add_handler(CallbackQueryHandler(order, pattern="^order$"))
    app.add_handler(CallbackQueryHandler(contact, pattern="^contact$"))
    app.add_handler(CallbackQueryHandler(back, pattern="^back$"))
    print("✅ BustonFood bot ishga tushdi!")
    app.run_polling()

if __name__ == "__main__":
    main()
