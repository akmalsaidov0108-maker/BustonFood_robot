import os
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes

TOKEN = os.environ.get("TOKEN", "YOUR_TOKEN")
ADMIN_ID = 123456789  # O'z Telegram ID ingizni yozing

OWNER_PHONE = "+998930352203"
OWNER_USERNAME = "https://t.me/+998930352203"
PARTNER_PHONE = "+998946373090"

PRODUCTS = {
    "🌯 Lavash & Hotdog": {
        "🌯 Lavash (oddiy)": 8000,
        "🌯 Lavash (maxsus)": 12000,
        "🌭 Hotdog (klassik)": 10000,
        "🌭 Hotdog (maxsus)": 15000,
    },
    "🥤 Salqin Ichimliklar": {
        "🥤 Coca-Cola (0.5L)": 5000,
        "🥤 Pepsi (0.5L)": 5000,
        "🥤 Sprite (0.5L)": 5000,
        "🧃 Sharbat (1L)": 7000,
        "💧 Mineral suv (0.5L)": 3000,
        "🥛 Chalop (0.5L)": 6000,
        "🥛 Chalop (1L)": 10000,
    },
    "🍦 Muzqaymoq & Marjon": {
        "🍦 Muzqaymoq (1 dona)": 5000,
        "🍨 Marjon (1 dona)": 7000,
        "🍧 Maxsus marjon": 10000,
    },
    "🍿 Quruq Tamaddum": {
        "🍿 Suxariklar (50g)": 3000,
        "🍿 Suxariklar (100g)": 5000,
        "🥨 Yengil tamaddum": 4000,
    },
}

user_carts = {}
user_reviews = {}
user_states = {}

# ═══════════════════════════════════════
# 🏠 BOSH SAHIFA
# ═══════════════════════════════════════
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    keyboard = [
        [InlineKeyboardButton("🛍️ Mahsulotlar", callback_data="products"),
         InlineKeyboardButton("🛒 Savatcha", callback_data="cart")],
        [InlineKeyboardButton("🎯 Aksiyalar", callback_data="sales"),
         InlineKeyboardButton("⭐ Izohlar", callback_data="reviews")],
        [InlineKeyboardButton("📞 Zakaz berish", callback_data="order_contact")],
        [InlineKeyboardButton("🤝 Hamkorlik", callback_data="partner"),
         InlineKeyboardButton("ℹ️ Haqimizda", callback_data="about")],
    ]
    text = (
        "╔═══════════════════════╗\n"
        "║  🌿 BUSTON FOOD 🌿   ║\n"
        "║  Mazali • Tez • Arzon ║\n"
        "╚═══════════════════════╝\n\n"
        f"Assalomu alaykum, {user.first_name}! 👋\n\n"
        "🏆 Buston mahallasining №1\n"
        "tez taom xizmati!\n\n"
        "🌯 Lavash & Hotdog — eng mazali\n"
        "🥤 Salqin ichimliklar — har xil\n"
        "🍦 Muzqaymoq — yangi va sovuq\n"
        "🚚 Yetkazish — Buston bo'ylab\n\n"
        "━━━━━━━━━━━━━━━━━━━━━━━\n"
        "👇 Xizmatdan foydalaning:"
    )
    if update.message:
        await update.message.reply_text(text, reply_markup=InlineKeyboardMarkup(keyboard))
    else:
        await update.callback_query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard))

# ═══════════════════════════════════════
# 📦 KATEGORIYALAR
# ═══════════════════════════════════════
async def show_categories(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    keyboard = []
    for cat in PRODUCTS:
        count = len(PRODUCTS[cat])
        keyboard.append([InlineKeyboardButton(f"{cat}  ({count} xil)", callback_data=f"cat_{cat}")])
    keyboard.append([InlineKeyboardButton("🏠 Bosh sahifa", callback_data="home")])
    await query.edit_message_text(
        "╔═══════════════════════╗\n"
        "║   📦 KATEGORIYALAR    ║\n"
        "╚═══════════════════════╝\n\n"
        "Kerakli bo'limni tanlang 👇",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

# ═══════════════════════════════════════
# 🛍️ MAHSULOTLAR
# ═══════════════════════════════════════
async def show_products(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    category = query.data.replace("cat_", "")
    keyboard = []
    for product, price in PRODUCTS[category].items():
        keyboard.append([InlineKeyboardButton(
            f"{product}  —  {price:,} so'm  ➕",
            callback_data=f"add_{product}_{price}"
        )])
    keyboard.append([InlineKeyboardButton("🔙 Kategoriyalar", callback_data="products")])
    keyboard.append([InlineKeyboardButton("🛒 Savatcham", callback_data="cart")])
    await query.edit_message_text(
        f"╔═══════════════════════╗\n"
        f"║ {category[:21]:<21} ║\n"
        f"╚═══════════════════════╝\n\n"
        f"➕ — savatchaga qo'shish\n\n"
        f"Mahsulot tanlang 👇",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

# ═══════════════════════════════════════
# ➕ SAVATCHAGA QO'SHISH
# ═══════════════════════════════════════
async def add_to_cart(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
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
    qty = user_carts[user_id][product]["qty"]
    total = sum(i["price"] * i["qty"] for i in user_carts[user_id].values())
    await query.answer(
        f"✅ Savatchaga qo'shildi!\n"
        f"▸ {product}\n"
        f"Miqdor: {qty} ta\n"
        f"Jami: {total:,} so'm",
        show_alert=True
    )

# ═══════════════════════════════════════
# 🛒 SAVATCHA
# ═══════════════════════════════════════
async def show_cart(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    cart = user_carts.get(user_id, {})
    if not cart:
        await query.edit_message_text(
            "╔═══════════════════════╗\n"
            "║     🛒 SAVATCHA       ║\n"
            "╚═══════════════════════╝\n\n"
            "😔 Savatchangiz bo'sh!\n\n"
            "Mahsulot qo'shish uchun\n"
            "«🛍️ Mahsulotlar» ga o'ting 👇",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🛍️ Mahsulotlarga o'tish", callback_data="products")],
                [InlineKeyboardButton("🏠 Bosh sahifa", callback_data="home")]
            ])
        )
        return
    text = "╔═══════════════════════╗\n║     🛒 SAVATCHA       ║\n╚═══════════════════════╝\n\n"
    total = 0
    for product, info in cart.items():
        subtotal = info["price"] * info["qty"]
        text += f"▸ {product}\n  {info['qty']} ta × {info['price']:,} = {subtotal:,} so'm\n\n"
        total += subtotal
    text += (
        f"━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"💰 JAMI: {total:,} so'm\n"
        f"🚚 Yetkazish: hududga qarab"
    )
    keyboard = [
        [InlineKeyboardButton("📞 Zakaz berish", callback_data="order_contact")],
        [InlineKeyboardButton("🗑️ Tozalash", callback_data="clear_cart"),
         InlineKeyboardButton("🛍️ Yana xarid", callback_data="products")],
        [InlineKeyboardButton("🏠 Bosh sahifa", callback_data="home")],
    ]
    await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard))

# ═══════════════════════════════════════
# 🗑️ TOZALASH
# ═══════════════════════════════════════
async def clear_cart(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    user_carts[user_id] = {}
    await query.answer("🗑️ Savatcha tozalandi!", show_alert=True)
    await show_cart(update, context)

# ═══════════════════════════════════════
# 📞 ZAKAZ BERISH — TELEFON + TELEGRAM
# ═══════════════════════════════════════
async def order_contact(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    cart = user_carts.get(user_id, {})

    if cart:
        total = sum(i["price"] * i["qty"] for i in cart.values())
        cart_text = "\n🛒 Savatchangizdagi mahsulotlar:\n"
        for product, info in cart.items():
            cart_text += f"▸ {product} × {info['qty']} = {info['price']*info['qty']:,} so'm\n"
        cart_text += f"\n💰 Jami: {total:,} so'm\n"
    else:
        cart_text = ""

    keyboard = [
        [InlineKeyboardButton("📞 Qo'ng'iroq qilish", url=f"tel:{OWNER_PHONE}")],
        [InlineKeyboardButton("💬 Telegram orqali yozish", url=f"https://t.me/+998930352203")],
        [InlineKeyboardButton("🔙 Savatchaga qaytish", callback_data="cart")],
        [InlineKeyboardButton("🏠 Bosh sahifa", callback_data="home")],
    ]
    await query.edit_message_text(
        "╔═══════════════════════╗\n"
        "║   📞 ZAKAZ BERISH     ║\n"
        "╚═══════════════════════╝\n"
        f"{cart_text}\n"
        "━━━━━━━━━━━━━━━━━━━━━━━\n"
        "Quyidagi usullardan biri\n"
        "orqali zakaz bering:\n\n"
        "📞 Telefon:\n"
        f"   {OWNER_PHONE}\n\n"
        "💬 Telegram:\n"
        f"   @BustonFood operatori\n\n"
        "⏰ Ish vaqti: Doimiy\n"
        "🚚 Yetkazish: 20-40 daqiqa\n"
        "━━━━━━━━━━━━━━━━━━━━━━━\n"
        "👇 Qulay usulni tanlang:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

# ═══════════════════════════════════════
# 🎯 AKSIYALAR
# ═══════════════════════════════════════
async def show_sales(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text(
        "╔═══════════════════════╗\n"
        "║    🎯 AKSIYALAR       ║\n"
        "╚═══════════════════════╝\n\n"
        "🔥 Bugungi maxsus takliflar:\n\n"
        "🌯 Lavash + Ichimlik combo\n"
        "   ~~13,000~~ → 10,000 so'm\n"
        "   Tejash: 3,000 so'm! 🎉\n\n"
        "🌭 Hotdog + Suxarik combo\n"
        "   ~~13,000~~ → 11,000 so'm\n"
        "   Tejash: 2,000 so'm! 🎉\n\n"
        "🍦 2 ta Muzqaymoq\n"
        "   ~~10,000~~ → 8,000 so'm\n"
        "   Tejash: 2,000 so'm! 🎉\n\n"
        "━━━━━━━━━━━━━━━━━━━━━━━\n"
        "🚚 Buston hududi bo'ylab\n"
        "   yetkazish — CHEGIRMADA!\n\n"
        "⚡ Taklif cheklangan vaqt!\n"
        "Hoziroq zakaz bering 👇",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("📞 Zakaz berish", callback_data="order_contact")],
            [InlineKeyboardButton("🛍️ Mahsulotlar", callback_data="products")],
            [InlineKeyboardButton("🏠 Bosh sahifa", callback_data="home")]
        ])
    )

# ═══════════════════════════════════════
# ⭐ IZOHLAR
# ═══════════════════════════════════════
async def show_reviews(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    text = "╔═══════════════════════╗\n║  ⭐ MIJOZLAR IZOHI   ║\n╚═══════════════════════╝\n\n"
    if not user_reviews:
        text += "Hali izoh yo'q.\nBirinchi bo'lib izoh qoldiring! 😊"
    else:
        for review in list(user_reviews.values())[-5:]:
            text += (
                f"{'⭐' * review['rating']}\n"
                f"👤 {review['name']}\n"
                f"💬 {review['text']}\n"
                f"{'─' * 23}\n"
            )
    keyboard = [
        [InlineKeyboardButton("✍️ Izoh qoldirish", callback_data="add_review")],
        [InlineKeyboardButton("🏠 Bosh sahifa", callback_data="home")]
    ]
    await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard))

async def add_review(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    keyboard = [
        [InlineKeyboardButton("⭐ 1", callback_data="rate_1"),
         InlineKeyboardButton("⭐⭐ 2", callback_data="rate_2"),
         InlineKeyboardButton("⭐⭐⭐ 3", callback_data="rate_3")],
        [InlineKeyboardButton("⭐⭐⭐⭐ 4", callback_data="rate_4"),
         InlineKeyboardButton("⭐⭐⭐⭐⭐ 5", callback_data="rate_5")],
        [InlineKeyboardButton("🔙 Orqaga", callback_data="reviews")]
    ]
    await query.edit_message_text(
        "╔═══════════════════════╗\n"
        "║  ✍️ IZOH QOLDIRISH   ║\n"
        "╚═══════════════════════╝\n\n"
        "Xizmatimizga baho bering:\n\n"
        "⭐ 1 — Yomon\n"
        "⭐⭐ 2 — Qoniqarsiz\n"
        "⭐⭐⭐ 3 — O'rtacha\n"
        "⭐⭐⭐⭐ 4 — Yaxshi\n"
        "⭐⭐⭐⭐⭐ 5 — A'lo!",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def rate(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    rating = int(query.data.replace("rate_", ""))
    user_states[user_id] = {"action": "waiting_review_text", "rating": rating}
    await query.edit_message_text(
        f"{'⭐' * rating} — Baho berdingiz!\n\n"
        f"Endi izohingizni yozing 👇\n"
        f"(Xizmat, tezlik, sifat haqida)"
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    state = user_states.get(user_id)
    if isinstance(state, dict) and state.get("action") == "waiting_review_text":
        user_reviews[user_id] = {
            "name": update.effective_user.first_name,
            "rating": state["rating"],
            "text": update.message.text
        }
        user_states[user_id] = None
        await update.message.reply_text(
            "✅ Izohingiz qabul qilindi!\n\n"
            f"{'⭐' * state['rating']}\n"
            f"💬 {update.message.text}\n\n"
            "Rahmat! 🙏",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🏠 Bosh sahifa", callback_data="home")]
            ])
        )

# ═══════════════════════════════════════
# 🤝 HAMKORLIK
# ═══════════════════════════════════════
async def partner(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    keyboard = [
        [InlineKeyboardButton("📞 Qo'ng'iroq", url=f"tel:{PARTNER_PHONE}")],
        [InlineKeyboardButton("💬 Telegram", url=f"https://t.me/+998946373090")],
        [InlineKeyboardButton("🏠 Bosh sahifa", callback_data="home")]
    ]
    await query.edit_message_text(
        "╔═══════════════════════╗\n"
        "║    🤝 HAMKORLIK       ║\n"
        "╚═══════════════════════╝\n\n"
        "Hamkorlik takliflari va\n"
        "savollar uchun murojaat:\n\n"
        "👤 Saidov Og'abek\n"
        "   (BustonFood hamkori)\n\n"
        "📱 Telefon:\n"
        f"   {PARTNER_PHONE}\n\n"
        "━━━━━━━━━━━━━━━━━━━━━━━\n"
        "Biz doim hamkorlikka\n"
        "tayyormiz! 🌿\n\n"
        "👇 Bog'laning:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

# ═══════════════════════════════════════
# ℹ️ HAQIMIZDA
# ═══════════════════════════════════════
async def about(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    keyboard = [
        [InlineKeyboardButton("📞 Zakaz berish", callback_data="order_contact")],
        [InlineKeyboardButton("🏠 Bosh sahifa", callback_data="home")]
    ]
    await query.edit_message_text(
        "╔═══════════════════════╗\n"
        "║    ℹ️ HAQIMIZDA       ║\n"
        "╚═══════════════════════╝\n\n"
        "🌿 BustonFood — Buston\n"
        "mahallasining yagona va\n"
        "ishonchli tez taom xizmati!\n\n"
        "🏆 Nima uchun biz?\n\n"
        "🌯 Lavash & Hotdog — eng mazali\n"
        "🥤 Salqin ichimliklar — sovuq\n"
        "🍦 Muzqaymoq — har doim yangi\n"
        "🚚 Tez yetkazish — 20-40 daq\n"
        "💰 Narxlar — hammabop\n"
        "⏰ Ish vaqti — doimiy\n\n"
        "━━━━━━━━━━━━━━━━━━━━━━━\n"
        "👤 Do'kon egasi:\n"
        "   Olmosov To'lqin\n\n"
        "🤖 Bot muallifi:\n"
        "   BustonFood hamkori\n"
        "   Saidov Og'abek\n\n"
        "━━━━━━━━━━━━━━━━━━━━━━━\n"
        "📍 Manzil: Alijon MFY\n"
        "   M37 yo'l yoqasida\n"
        f"📞 Tel: {OWNER_PHONE}",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

# ═══════════════════════════════════════
# 🌐 SERVER
# ═══════════════════════════════════════
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

# ═══════════════════════════════════════
# 🚀 ISHGA TUSHIRISH
# ═══════════════════════════════════════
def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(show_categories, pattern="^products$"))
    app.add_handler(CallbackQueryHandler(show_products, pattern="^cat_"))
    app.add_handler(CallbackQueryHandler(add_to_cart, pattern="^add_"))
    app.add_handler(CallbackQueryHandler(show_cart, pattern="^cart$"))
    app.add_handler(CallbackQueryHandler(clear_cart, pattern="^clear_cart$"))
    app.add_handler(CallbackQueryHandler(order_contact, pattern="^order_contact$"))
    app.add_handler(CallbackQueryHandler(show_sales, pattern="^sales$"))
    app.add_handler(CallbackQueryHandler(show_reviews, pattern="^reviews$"))
    app.add_handler(CallbackQueryHandler(add_review, pattern="^add_review$"))
    app.add_handler(CallbackQueryHandler(rate, pattern="^rate_"))
    app.add_handler(CallbackQueryHandler(partner, pattern="^partner$"))
    app.add_handler(CallbackQueryHandler(about, pattern="^about$"))
    app.add_handler(CallbackQueryHandler(start, pattern="^home$"))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    print("✅ BustonFood bot ishga tushdi!")
    app.run_polling()

if __name__ == "__main__":
    main()            
