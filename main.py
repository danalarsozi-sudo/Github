import logging
import asyncio
import os
import random
from datetime import datetime
from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiohttp import web

# --- AYARLAR (SETTINGS) ---
# Alfa, buraya kendi bilgilerini kontrol ederek gir
API_TOKEN = '8335704519:AAGEOdWFuXWS-qnlHOMF_zJI42Xd3Bc_tGI'
ADMIN_ID = 1748533804
OWNER_CONTACT = "@Alfa_onlyy"
OWNER_PHONE = "+8618418404036"
CHANNEL_USERNAME = "@onlybrazzz" # Kendi kanal kullanıcı adını buraya yaz (Zorunlu takip)

logging.basicConfig(level=logging.INFO)
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

# Veritabanı (Database Simulation)
db = {} # {user_id: {"lang": "tk", "rights": 5, "refs": 0, "is_admin": False}}

# --- DİL PAKETLERİ (LANGUAGE PACKS) ---
STRINGS = {
    "tk": {
        "welcome": "👁 **ALFA OSINT ULTIMATE**\nMaglumat gözleg ulgamyna hoş geldiňiz.",
        "force_join": "❌ **Giriş gadagan!**\nDowam etmek üçin kanalymyza goşulyň: {channel}",
        "check_sub": "✅ Goşuldym",
        "search_prompt": "🔍 @username, Telefon ýa-da Ady-Familiýa ýazyň:",
        "scanning": "📡 **Taralýar...**\nBölüm: {layer}\nLütfen garaşyň...",
        "no_rights": "❌ Sorgu hukugyňyz gutardy! 5 dostuňyzy çagyryň.",
        "profile": "👤 **Profil**\nID: `{id}`\nHukuk: {rights}\nReferal: {refs}",
        "admin_info": "👨‍💻 **Admin:** {owner}\n📞 **IMO:** {phone}",
        "scan_res": "🕵️ **ALFA REPORT: {query}**\n━━━━━━━━━━━━━━━\n📂 Toplanan maglumatlar yuklendi."
    },
    "ru": {
        "welcome": "👁 **ALFA OSINT ULTIMATE**\nДобро пожаловать в систему разведки.",
        "force_join": "❌ **Доступ запрещен!**\nПодпишитесь на канал: {channel}",
        "check_sub": "✅ Я подписался",
        "search_prompt": "🔍 Введите @username, Телефон или Имя-Фамилию:",
        "scanning": "📡 **Сканирование...**\nСлой: {layer}\nПожалуйста, подождите...",
        "no_rights": "❌ Лимиты исчерпаны! Пригласите 5 друзей.",
        "profile": "👤 **Профиль**\nID: `{id}`\nЛимиты: {rights}\nРефералы: {refs}",
        "admin_info": "👨‍💻 **Админ:** {owner}\n📞 **IMO:** {phone}",
        "scan_res": "🕵️ **ALFA REPORT: {query}**\n━━━━━━━━━━━━━━━\n📂 Данные успешно собраны."
    },
    "tr": {
        "welcome": "👁 **ALFA OSINT ULTIMATE**\nİstihbarat sistemine hoş geldiniz.",
        "force_join": "❌ **Erişim Reddedildi!**\nDevam etmek için kanala katılın: {channel}",
        "check_sub": "✅ Katıldım",
        "search_prompt": "🔍 @username, Telefon veya Ad-Soyad yazın:",
        "scanning": "📡 **Taranıyor...**\nKatman: {layer}\nLütfen bekleyin...",
        "no_rights": "❌ Sorgu hakkınız bitti! 5 arkadaş davet edin.",
        "profile": "👤 **Profilim**\nID: `{id}`\nSorgu Hakkı: {rights}\nReferans: {refs}",
        "admin_info": "👨‍💻 **Yönetici:** {owner}\n📞 **IMO:** {phone}",
        "scan_res": "🕵️ **ALFA RAPORU: {query}**\n━━━━━━━━━━━━━━━\n📂 Veriler başarıyla analiz edildi."
    }
}

# --- YARDIMCI FONKSİYONLAR ---
def get_user(uid):
    if uid not in db:
        db[uid] = {"lang": "tk", "rights": 5, "refs": 0, "is_admin": (uid == ADMIN_ID)}
    return db[uid]

async def is_subscribed(user_id):
    try:
        member = await bot.get_chat_member(CHANNEL_USERNAME, user_id)
        return member.status != 'left'
    except:
        return True # Kanal ayarlı değilse geç

# --- MENÜLER ---
def get_main_menu(uid):
    u = get_user(uid)
    l = u["lang"]
    kb = InlineKeyboardMarkup(row_width=2)
    kb.add(
        InlineKeyboardButton("🔍 Deep Scan", callback_data="start_scan"),
        InlineKeyboardButton("👤 Profil", callback_data="profile")
    )
    kb.add(
        InlineKeyboardButton("📞 Admin / IMO", callback_data="admin_info"),
        InlineKeyboardButton("🌐 Dil / Language", callback_data="lang_menu")
    )
    return kb

# --- RENDER WEB SERVER ---
async def handle(request): return web.Response(text="ALFA OSINT SERVER IS RUNNING")
async def start_web_server():
    app = web.Application()
    app.router.add_get('/', handle)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', int(os.getenv("PORT", 8080)))
    await site.start()

# --- BOT HANDLERS ---
@dp.message_handler(commands=['start'])
async def cmd_start(message: types.Message):
    uid = message.from_user.id
    user = get_user(uid)
    
    # Referans Sistemi
    if " " in message.text:
        ref_id = message.text.split()[1]
        if ref_id.isdigit() and int(ref_id) != uid:
            ref_owner = get_user(int(ref_id))
            ref_owner["refs"] += 1
            if ref_owner["refs"] % 5 == 0:
                ref_owner["rights"] += 5
                await bot.send_message(ref_id, "🎉 5 arkadaşınızı davet ettiğiniz için +5 sorgu kazandınız!")

    if not await is_subscribed(uid):
        kb = InlineKeyboardMarkup().add(InlineKeyboardButton("Kanal", url=f"t.me/{CHANNEL_USERNAME.replace('@','')}")).add(InlineKeyboardButton(STRINGS[user['lang']]['check_sub'], callback_data="check_sub"))
        await message.reply(STRINGS[user['lang']]['force_join'].format(channel=CHANNEL_USERNAME), reply_markup=kb)
        return

    await message.reply(STRINGS[user['lang']]['welcome'], reply_markup=get_main_menu(uid))

@dp.callback_query_handler(lambda c: True)
async def process_callback(c: types.CallbackQuery):
    uid = c.from_user.id
    user = get_user(uid)
    l = user["lang"]

    if c.data == "check_sub":
        if await is_subscribed(uid):
            await bot.send_message(uid, STRINGS[l]['welcome'], reply_markup=get_main_menu(uid))
        else:
            await c.answer("❌ Kanalymyza goşulyň!", show_alert=True)
    
    elif c.data == "profile":
        ref_link = f"t.me/{(await bot.get_me()).username}?start={uid}"
        rights = "Sınırsız ∞" if user['is_admin'] else user['rights']
        await c.message.edit_text(STRINGS[l]['profile'].format(id=uid, rights=rights, refs=user['refs']) + f"\n\n🔗 Ref Link: `{ref_link}`", parse_mode="Markdown")

    elif c.data == "admin_info":
        await c.message.edit_text(STRINGS[l]['admin_info'].format(owner=OWNER_CONTACT, phone=OWNER_PHONE))

    elif c.data == "lang_menu":
        kb = InlineKeyboardMarkup().add(
            InlineKeyboardButton("Türkmençe 🇹🇲", callback_data="set_tk"),
            InlineKeyboardButton("Русский 🇷🇺", callback_data="set_ru"),
            InlineKeyboardButton("Türkçe 🇹🇷", callback_data="set_tr")
        )
        await c.message.edit_text("Dil saýlaň / Выберите язык:", reply_markup=kb)

    elif c.data.startswith("set_"):
        user["lang"] = c.data.split("_")[1]
        await c.message.edit_text("✅ OK!", reply_markup=get_main_menu(uid))
    
    elif c.data == "start_scan":
        await c.message.answer(STRINGS[l]['search_prompt'])

@dp.message_handler()
async def handle_search(message: types.Message):
    uid = message.from_user.id
    user = get_user(uid)
    l = user["lang"]

    if not user['is_admin'] and user['rights'] <= 0:
        await message.reply(STRINGS[l]['no_rights'])
        return

    query = message.text
    wait = await message.reply(STRINGS[l]['scanning'].format(layer="OSINT Data Layers"))
    
    # Simülasyon Efektleri
    steps = ["Leak Database", "Social Footprints", "Private Metadata", "Network Nodes"]
    for step in steps:
        await asyncio.sleep(1.2)
        await wait.edit_text(STRINGS[l]['scanning'].format(layer=step))

    if not user['is_admin']: user['rights'] -= 1
    
    # Sonuç Raporu
    res = (
        f"{STRINGS[l]['scan_res'].format(query=query)}\n"
        f"🆔 **Digital ID:** `{random.getrandbits(32)}`\n"
        f"📍 **Yerleşiş:** `Türkmenistan (Tahmini)`\n"
        f"🗄 **Sızıntı:** `Eşleşme Bulundu (2023)`\n"
        f"🌐 **Platformlar:** [Instagram], [Twitter], [Facebook]\n"
        f"👥 **Ortak Gruplar:** `18`\n"
        f"━━━━━━━━━━━━━━━\n"
        f"🔒 *Alfa Intelligence Security Raporu*"
    )
    await wait.edit_text(res, parse_mode="Markdown")

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.create_task(start_web_server())
    executor.start_polling(dp, skip_updates=True)
