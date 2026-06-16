import os
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes
from supabase import create_client, Client

TOKEN = os.environ.get("TOKEN", "YOUR_TOKEN")
SUPABASE_URL = os.environ.get("SUPABASE_URL", "https://lekdzqlbpmukuzfjjwlv.supabase.co")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY", "YOUR_SUPABASE_KEY")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

ADMIN_ID = 123456789
OWNER_PHONE = "+998930352203"
PARTNER_PHONE = "+998946373090"

user_states = {}

# ===================== MENYUNI YUKLASH =====================
def get_menu():
    try:
        res = supabase.table("menu").select("*").eq("available", True).execute()
        menu = {}
        for item in res.data:
            cat = item["category"]
            if cat not in menu:
                menu[cat] = []
            menu[cat].append((item["name"], item["price"], item["id"]))
        return menu
    except:
        return {
            "🌯 Lavash & Hotdog": [("Lavash", "25,000 - 40,000 so'm", 1), ("Hotdog", "15,000 - 40,000 so'm", 2)],
            "🥤 Ichimliklar": [("Chalop", "5,000 so'mdan", 3)],
            "🍦 Muzqaymoq & Marjon": [("Muzqaymoq", "5,000 so'mdan", 5)],
            "🍿 Qo'shimcha mahsulotlar": [("Suxariklar", "Qo'ng'iroqda", 7)],
        }

# ===================== FOYDALANUVCHINI SAQLASH =====================
async def save_user(user):
    try:
        supabase.table("users").upsert({
            "id": user.id,
            "first_name": user.first_name,
            "username": user.username or ""
        }).execute()
    except:
        pass

# ===================== BOSH SAHIFA =====================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    await save_user(user)
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
    menu = get_menu()
    keyboard = []
    for cat in menu:
        keyboard.append([InlineKeyboardButton(cat, callback_data=f"cat_{cat}")])
    keyboard.append([InlineKeyboardButton("🏠 Bosh sahifa", callback_data="home")])
    await query.edit_message_text(
        "📦 Kategoriyalar\n\nBo'limni tanlang:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

# ===================== MAHSULOTLAR =====================
async def show_products(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    category = query.data.replace("cat_", "")
    menu = get_menu()
    text = f"{category}\n\n"
    if category in menu:
        for name, price_text, _ in menu[category]:
            text += f"▸ {name} — {price_text}\n"
    text += "\nBuyurtma berish uchun pastdagi tugmani bosing."
    keyboard = [
        [InlineKeyboardButton("📞 Zakaz berish", callback_data="order_contact")],
        [InlineKeyboardButton("🔙 Kategoriyalar", callback_data="products")],
        [InlineKeyboardButton("🏠 Bosh sahifa", callback_data="home")],
    ]
    await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard))

# ===================== ZAKAZ BERISH =====================
async def order_contact(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer(
        f"Buyurtma uchun qo'ng'iroq qiling:\n{OWNER_PHONE}",
        show_alert=True
    )
    text = (
        "📞 Buyurtma berish uchun qo'ng'iroq qiling:\n"
        f"{OWNER_PHONE}\n\n"
        "Ish vaqti: doimiy\n"
        "Yetkazib berish: 20-40 daqiqa"
    )
    keyboard = [
        [InlineKeyboardButton("🛍️ Mahsulotlar", callback_data="products")],
        [InlineKeyboardButton("🏠 Bosh sahifa", callback_data="home")],
    ]
    await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard))

# ===================== AKSIYALAR =====================
async def show_sales(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text(
        "🎯 Aksiyalar\n\n"
        "Joriy aksiyalar va chegirmalar haqida\n"
        "ma'lumot olish uchun qo'ng'iroq qiling.\n\n"
        "🚚 Buston hududi bo'ylab yetkazib berish\n"
        "chegirmali shartlarda amalga oshiriladi.",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("📞 Zakaz berish", callback_data="order_contact")],
            [InlineKeyboardButton("🛍️ Mahsulotlar", callback_data="products")],
            [InlineKeyboardButton("🏠 Bosh sahifa", callback_data="home")]
        ])
    )

# ===================== IZOHLAR =====================
async def show_reviews(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    text = "⭐ Mijozlar izohi\n\n"
    try:
        res = supabase.table("reviews").select("*").order("created_at", desc=True).limit(5).execute()
        if not res.data:
            text += "Hali izoh yo'q.\nBirinchi bo'lib izoh qoldiring."
        else:
            for review in res.data:
                text += (
                    f"{'⭐' * review['rating']}\n"
                    f"👤 {review['user_name']}\n"
                    f"💬 {review['text']}\n\n"
                )
    except:
        text += "Izohlarni yuklashda xatolik."
    keyboard = [
        [InlineKeyboardButton("✍️ Izoh qoldirish", callback_data="add_review")],
        [InlineKeyboardButton("🏠 Bosh sahifa", callback_data="home")]
    ]
    await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard))

async def add_review(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    keyboard = [
        [InlineKeyboardButton("⭐ 1", callback_data="rate_1"),
         InlineKeyboardButton("⭐⭐ 2", callback_data="rate_2"),
         InlineKeyboardButton("⭐⭐⭐ 3", callback_data="rate_3")],
        [InlineKeyboardButton("⭐⭐⭐⭐ 4", callback_data="rate_4"),
         InlineKeyboardButton("⭐⭐⭐⭐⭐ 5", callback_data="rate_5")],
        [InlineKeyboardButton("🔙 Orqaga", callback_data="reviews")]
    ]
    await query.edit_message_text(
        "✍️ Izoh qoldirish\n\nXizmatimizga baho bering:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def rate(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    rating = int(query.data.replace("rate_", ""))
    user_states[user_id] = {"action": "waiting_review_text", "rating": rating}
    await query.edit_message_text(
        f"{'⭐' * rating} tanlandi.\n\nEndi izohingizni yozing:"
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    state = user_states.get(user_id)
    if isinstance(state, dict) and state.get("action") == "waiting_review_text":
        try:
            supabase.table("reviews").insert({
                "user_id": user_id,
                "user_name": update.effective_user.first_name,
                "rating": state["rating"],
                "text": update.message.text
            }).execute()
        except:
            pass
        user_states[user_id] = None
        await update.message.reply_text(
            "Izohingiz qabul qilindi va saqlandi! ✅\n\n"
            f"{'⭐' * state['rating']}\n"
            f"💬 {update.message.text}\n\n"
            "Rahmat!",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🏠 Bosh sahifa", callback_data="home")]
            ])
        )

# ===================== HAMKORLIK =====================
async def partner(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer(
        f"Hamkorlik uchun qo'ng'iroq qiling:\n{PARTNER_PHONE}",
        show_alert=True
    )
    text = (
        "🤝 Hamkorlik\n\n"
        "Hamkorlik takliflari va savollar uchun:\n\n"
        "👤 Saidov Og'abek\n"
        f"📞 {PARTNER_PHONE}"
    )
    keyboard = [[InlineKeyboardButton("🏠 Bosh sahifa", callback_data="home")]]
    await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard))

# ===================== HAQIMIZDA =====================
async def about(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    keyboard = [
        [InlineKeyboardButton("📞 Zakaz berish", callback_data="order_contact")],
        [InlineKeyboardButton("🏠 Bosh sahifa", callback_data="home")]
    ]
    await query.edit_message_text(
        "ℹ️ Haqimizda\n\n"
        "BustonFood — Buston mahallasi tez taom xizmati.\n\n"
        "Menyu:\n"
        "🌯 Lavash & Hotdog\n"
        "🥤 Ichimliklar\n"
        "🍦 Muzqaymoq va marjon\n"
        "🍿 Qo'shimcha mahsulotlar\n\n"
        "🚚 Yetkazib berish: 20-40 daqiqa\n\n"
        "📍 Manzil: Alijon MFY, M37 yo'l yoqasida\n"
        f"📞 Tel: {OWNER_PHONE}",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

# ===================== SERVER (Render uchun) =====================
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

# ===================== ISHGA TUSHIRISH =====================
def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(show_categories, pattern="^products$"))
    app.add_handler(CallbackQueryHandler(show_products, pattern="^cat_"))
    app.add_handler(CallbackQueryHandler(order_contact, pattern="^order_contact$"))
    app.add_handler(CallbackQueryHandler(show_sales, pattern="^sales$"))
    app.add_handler(CallbackQueryHandler(add_review, pattern="^add_review$"))
    app.add_handler(CallbackQueryHandler(show_reviews, pattern="^reviews$"))
    app.add_handler(CallbackQueryHandler(rate, pattern="^rate_"))
    app.add_handler(CallbackQueryHandler(partner, pattern="^partner$"))
    app.add_handler(CallbackQueryHandler(about, pattern="^about$"))
    app.add_handler(CallbackQueryHandler(start, pattern="^home$"))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    print("BustonFood bot ishga tushdi ✅")
    app.run_polling()

if __name__ == "__main__":
    main()
