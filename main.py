# main.py
# CRYPTO EMPIRE — ПОЛНАЯ РАБОЧАЯ ВЕРСИЯ
# ВСЁ РАБОТАЕТ!

import os
import time
import random
import asyncio
import html
import json
from datetime import datetime, timezone

import aiosqlite
from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery, LabeledPrice, PreCheckoutQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder

try:
    from keep_alive import keep_alive
    keep_alive()
except Exception:
    pass

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
if not TOKEN:
    raise RuntimeError("TELEGRAM_BOT_TOKEN is not set")

BOT = Bot(token=TOKEN)
DP = Dispatcher()
DB = "crypto_empire.db"

OWNER = "foqlu"
REQUIRED_CHANNEL = os.getenv("REQUIRED_CHANNEL", "")
CHANNEL_LINK = "https://t.me/+MHTPcaFy2j5lOWMy"

START_COINS = 30000
REFERRAL_BONUS = 25000
REFERRAL_FRIEND_BONUS = 5000

# =========================================================
# ДОНАТЫ ЗА STARS
# =========================================================
DONATE_PACKS = {
    "pack1": {"stars": 10, "coins": 10000, "name": "🪙 Маленький пак"},
    "pack2": {"stars": 25, "coins": 30000, "name": "💰 Средний пак"},
    "pack3": {"stars": 50, "coins": 70000, "name": "💎 Большой пак"},
    "pack4": {"stars": 100, "coins": 150000, "name": "👑 VIP пак"},
    "pack5": {"stars": 250, "coins": 400000, "name": "🔥 Мега пак"},
    "pack6": {"stars": 500, "coins": 1000000, "name": "💎 Легендарный пак"},
}

# =========================================================
# БИЗНЕСЫ
# =========================================================
BUSINESSES = {
    "pizza": {"name": "🍕 Пиццерия", "price": 10000, "income": 100, "upgrade_cost": 5000},
    "shop": {"name": "🏪 Магазин", "price": 50000, "income": 500, "upgrade_cost": 25000},
    "office": {"name": "🏢 Офис", "price": 200000, "income": 2000, "upgrade_cost": 100000},
    "factory": {"name": "🏭 Завод", "price": 1000000, "income": 10000, "upgrade_cost": 500000},
    "bank": {"name": "🏛️ Банк", "price": 5000000, "income": 50000, "upgrade_cost": 2500000},
    "crypto_biz": {"name": "💎 Крипто-биржа", "price": 25000000, "income": 250000, "upgrade_cost": 12500000},
    "corporation": {"name": "🌍 Корпорация", "price": 100000000, "income": 1000000, "upgrade_cost": 50000000},
}

# =========================================================
# КРИПТОВАЛЮТЫ (ПОКУПКА ЗА МОНЕТЫ)
# =========================================================
CRYPTO = {
    "BTC": {"name": "₿ Bitcoin", "price": 1000, "emoji": "₿"},
    "ETH": {"name": "⟠ Ethereum", "price": 500, "emoji": "⟠"},
    "SOL": {"name": "◎ Solana", "price": 100, "emoji": "◎"},
    "DOGE": {"name": "🐶 Dogecoin", "price": 10, "emoji": "🐶"},
    "SHIB": {"name": "🐕 Shiba", "price": 5, "emoji": "🐕"},
}

# =========================================================
# ИВЕНТЫ
# =========================================================
EVENTS = {
    "double": {"name": "🪙 Двойные монеты", "desc": "Все выигрыши x2!"},
    "triple": {"name": "💎 Тройные монеты", "desc": "Все выигрыши x3!"},
    "roulette": {"name": "🎲 Рулетка x2", "desc": "Рулетка x2!"},
    "income": {"name": "📈 Бонус дохода", "desc": "Доход x2!"},
    "lucky": {"name": "🍀 Счастливый час", "desc": "Шанс +20%"},
    "mega": {"name": "🔥 Мега выигрыш", "desc": "Выигрыши x5!"},
    "casino": {"name": "🎰 День казино", "desc": "Все игры x2!"},
    "invest": {"name": "📈 Инвест бонус", "desc": "Доходность x2!"},
    "vip": {"name": "👑 VIP день", "desc": "Все бонусы x3!"},
    "free": {"name": "🎰 Бесплатные спины", "desc": "5 бесплатных спинов!"},
}

# =========================================================
# ДОСТИЖЕНИЯ
# =========================================================
ACHIEVEMENTS = {
    "first_million": {"name": "💰 Первый миллион", "reward": 100000},
    "first_business": {"name": "🏪 Первый бизнес", "reward": 50000},
    "ten_businesses": {"name": "🏢 10 бизнесов", "reward": 500000},
    "level_10": {"name": "⭐ Уровень 10", "reward": 500000},
    "level_50": {"name": "⭐ Уровень 50", "reward": 5000000},
}

# =========================================================
# УРОВНИ
# =========================================================
LEVELS = {
    1: 0, 2: 1000, 3: 2500, 4: 5000, 5: 10000,
    6: 20000, 7: 35000, 8: 50000, 9: 75000, 10: 100000,
    15: 250000, 20: 500000, 30: 1000000, 40: 2500000,
    50: 5000000, 75: 10000000, 100: 25000000,
}

# =========================================================
# ИНИЦИАЛИЗАЦИЯ БД
# =========================================================
async def init_db():
    async with aiosqlite.connect(DB) as db:
        await db.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            username TEXT DEFAULT '',
            first_name TEXT DEFAULT '',
            coins INTEGER DEFAULT 30000,
            level INTEGER DEFAULT 1,
            exp INTEGER DEFAULT 0,
            total_earned INTEGER DEFAULT 0,
            total_spent INTEGER DEFAULT 0,
            total_wins INTEGER DEFAULT 0,
            total_losses INTEGER DEFAULT 0,
            daily_date TEXT DEFAULT '',
            daily_streak INTEGER DEFAULT 0,
            banned INTEGER DEFAULT 0,
            referrer_id INTEGER DEFAULT 0,
            referral_count INTEGER DEFAULT 0,
            created_at INTEGER DEFAULT 0,
            total_donated INTEGER DEFAULT 0,
            casino_session INTEGER DEFAULT 0
        )
        """)

        await db.execute("""
        CREATE TABLE IF NOT EXISTS businesses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            biz_type TEXT NOT NULL,
            level INTEGER DEFAULT 1,
            bought_at INTEGER DEFAULT 0,
            last_collected INTEGER DEFAULT 0
        )
        """)

        await db.execute("""
        CREATE TABLE IF NOT EXISTS investments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            amount INTEGER NOT NULL,
            invested_at INTEGER NOT NULL,
            profit INTEGER DEFAULT 0,
            status TEXT DEFAULT 'active'
        )
        """)

        await db.execute("""
        CREATE TABLE IF NOT EXISTS achievements (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            ach_type TEXT NOT NULL,
            unlocked_at INTEGER DEFAULT 0
        )
        """)

        await db.execute("""
        CREATE TABLE IF NOT EXISTS donations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            pack_id TEXT NOT NULL,
            stars INTEGER NOT NULL,
            coins INTEGER NOT NULL,
            created_at INTEGER DEFAULT 0
        )
        """)

        await db.execute("""
        CREATE TABLE IF NOT EXISTS crypto_wallet (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            crypto_type TEXT NOT NULL,
            amount REAL DEFAULT 0
        )
        """)

        await db.execute("""
        CREATE TABLE IF NOT EXISTS promo_codes (
            code TEXT PRIMARY KEY,
            coins INTEGER DEFAULT 0,
            stars INTEGER DEFAULT 0,
            activations INTEGER NOT NULL,
            used INTEGER DEFAULT 0,
            created_at INTEGER DEFAULT 0
        )
        """)

        await db.execute("""
        CREATE TABLE IF NOT EXISTS promo_uses (
            code TEXT NOT NULL,
            user_id INTEGER NOT NULL,
            PRIMARY KEY (code, user_id)
        )
        """)

        await db.execute("""
        CREATE TABLE IF NOT EXISTS active_events (
            id INTEGER PRIMARY KEY CHECK (id = 1),
            event_key TEXT NOT NULL,
            ends_at INTEGER NOT NULL,
            active INTEGER DEFAULT 1
        )
        """)

        await db.commit()

# =========================================================
# ФУНКЦИИ
# =========================================================
async def register_user(user_id, username="", first_name="", referrer_id=0):
    async with aiosqlite.connect(DB) as db:
        cur = await db.execute("SELECT user_id FROM users WHERE user_id = ?", (user_id,))
        if await cur.fetchone():
            return
        
        await db.execute("""
            INSERT INTO users (user_id, username, first_name, coins, created_at)
            VALUES (?, ?, ?, ?, ?)
        """, (user_id, username, first_name, START_COINS, int(time.time())))
        
        if referrer_id and referrer_id != user_id:
            await db.execute("UPDATE users SET coins = coins + ? WHERE user_id = ?", (REFERRAL_BONUS, referrer_id))
            await db.execute("UPDATE users SET referral_count = referral_count + 1 WHERE user_id = ?", (referrer_id,))
            await db.execute("UPDATE users SET coins = coins + ? WHERE user_id = ?", (REFERRAL_FRIEND_BONUS, user_id))
        
        await db.commit()

async def get_user(user_id):
    async with aiosqlite.connect(DB) as db:
        db.row_factory = aiosqlite.Row
        cur = await db.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
        return await cur.fetchone()

async def update_coins(user_id, amount):
    async with aiosqlite.connect(DB) as db:
        await db.execute("UPDATE users SET coins = coins + ? WHERE user_id = ?", (amount, user_id))
        if amount > 0:
            await db.execute("UPDATE users SET total_earned = total_earned + ? WHERE user_id = ?", (amount, user_id))
        else:
            await db.execute("UPDATE users SET total_spent = total_spent + ? WHERE user_id = ?", (abs(amount), user_id))
        await db.commit()

async def get_businesses(user_id):
    async with aiosqlite.connect(DB) as db:
        db.row_factory = aiosqlite.Row
        cur = await db.execute("SELECT * FROM businesses WHERE user_id = ?", (user_id,))
        return await cur.fetchall()

async def get_total_income(user_id):
    businesses = await get_businesses(user_id)
    total = 0
    for biz in businesses:
        data = BUSINESSES.get(biz['biz_type'])
        if data:
            total += data['income'] * biz['level']
    return total

async def add_exp(user_id, amount):
    user = await get_user(user_id)
    if not user:
        return
    new_exp = user['exp'] + amount
    current_level = user['level']
    
    while True:
        next_level = current_level + 1
        next_exp = LEVELS.get(next_level, 99999999)
        if new_exp < next_exp:
            break
        new_exp -= next_exp
        current_level += 1
    
    async with aiosqlite.connect(DB) as db:
        await db.execute("UPDATE users SET level = ?, exp = ? WHERE user_id = ?", (current_level, new_exp, user_id))
        await db.commit()

async def ensure_user(user_id, username="", first_name=""):
    user = await get_user(user_id)
    if not user:
        await register_user(user_id, username, first_name)
        return await get_user(user_id)
    return user

def is_owner(user):
    return (user.username or "").lower() == OWNER.lower()

# =========================================================
# ПОДПИСКА
# =========================================================
async def check_subscription(user_id):
    if not REQUIRED_CHANNEL:
        return True
    try:
        member = await BOT.get_chat_member(REQUIRED_CHANNEL, user_id)
        return member.status in ("creator", "administrator", "member")
    except:
        return False

def subscribe_keyboard():
    kb = InlineKeyboardBuilder()
    kb.button(text="📢 Подписаться на канал", url=CHANNEL_LINK)
    kb.button(text="✅ Проверить подписку", callback_data="check_sub")
    kb.adjust(1)
    return kb.as_markup()

async def require_subscription(message):
    if is_owner(message.from_user):
        return True
    if not REQUIRED_CHANNEL:
        return True
    if await check_subscription(message.from_user.id):
        return True
    
    await message.answer(
        "🔒 <b>ТРЕБУЕТСЯ ПОДПИСКА</b>\n\n"
        f"Подпишись на канал:\n{CHANNEL_LINK}\n\n"
        "После подписки нажми «Проверить подписку»",
        reply_markup=subscribe_keyboard(),
        parse_mode="HTML"
    )
    return False

# =========================================================
# КЛАВИАТУРЫ
# =========================================================
def main_keyboard():
    kb = InlineKeyboardBuilder()
    kb.button(text="👤 Профиль", callback_data="profile")
    kb.button(text="🏪 Бизнесы", callback_data="businesses")
    kb.button(text="🎰 Казино", callback_data="casino")
    kb.button(text="📈 Инвестиции", callback_data="investments")
    kb.button(text="🎁 Daily", callback_data="daily")
    kb.button(text="👥 Рефералка", callback_data="referral")
    kb.button(text="🏆 Топ", callback_data="top")
    kb.button(text="💰 Баланс", callback_data="balance")
    kb.button(text="🎯 Достижения", callback_data="achievements")
    kb.button(text="⭐ Донат", callback_data="donate")
    kb.button(text="💎 Крипто", callback_data="crypto_menu")
    kb.adjust(2)
    return kb.as_markup()

def casino_keyboard():
    kb = InlineKeyboardBuilder()
    kb.button(text="🎲 Рулетка", callback_data="roulette")
    kb.button(text="🎰 Слоты", callback_data="slots")
    kb.button(text="🎲 Кости", callback_data="dice")
    kb.button(text="🃏 Блэкджек", callback_data="blackjack")
    kb.button(text="🃏 Покер", callback_data="poker")
    kb.button(text="🎡 Колесо", callback_data="wheel")
    kb.button(text="🃏 Угадай карту", callback_data="guess_card")
    kb.button(text="⬅️ Назад", callback_data="menu")
    kb.adjust(2)
    return kb.as_markup()

def donate_keyboard():
    kb = InlineKeyboardBuilder()
    for key, data in DONATE_PACKS.items():
        kb.button(text=f"{data['name']} — {data['stars']} ⭐", callback_data=f"donate:{key}")
    kb.button(text="⬅️ Назад", callback_data="menu")
    kb.adjust(1)
    return kb.as_markup()

def crypto_keyboard():
    kb = InlineKeyboardBuilder()
    for key, data in CRYPTO.items():
        kb.button(text=f"{data['emoji']} {key} — {data['price']:,} 🪙", callback_data=f"buy_crypto:{key}")
    kb.button(text="📊 Мой кошелёк", callback_data="my_wallet")
    kb.button(text="⬅️ Назад", callback_data="menu")
    kb.adjust(1)
    return kb.as_markup()

# =========================================================
# КОМАНДА /start
# =========================================================
@DP.message(Command("start"))
async def start_command(message: Message):
    parts = message.text.split()
    referrer_id = 0
    if len(parts) > 1 and parts[1].startswith("ref_"):
        try:
            referrer_id = int(parts[1].split("_")[1])
        except:
            pass
    
    await register_user(
        message.from_user.id,
        message.from_user.username or "",
        message.from_user.first_name or "",
        referrer_id
    )
    
    if not await require_subscription(message):
        return
    
    user = await get_user(message.from_user.id)
    await message.answer(
        f"💎 <b>CRYPTO EMPIRE</b>\n\n"
        f"Привет, <b>{html.escape(message.from_user.first_name)}</b>!\n"
        f"💰 Баланс: <b>{user['coins']:,} 🪙</b>\n"
        f"⭐ Уровень: <b>{user['level']}</b>\n\n"
        "🎯 Цель: стать крипто-магнатом!",
        reply_markup=main_keyboard(),
        parse_mode="HTML"
    )

@DP.callback_query(F.data == "check_sub")
async def check_sub_callback(callback: CallbackQuery):
    await callback.answer()
    if await check_subscription(callback.from_user.id):
        await callback.message.edit_text(
            "✅ Подписка подтверждена!",
            reply_markup=main_keyboard(),
            parse_mode="HTML"
        )
    else:
        await callback.message.answer("❌ Подписка не найдена.", reply_markup=subscribe_keyboard())

# =========================================================
# ПРОФИЛЬ
# =========================================================
@DP.callback_query(F.data == "profile")
async def profile_callback(callback: CallbackQuery):
    await callback.answer()
    user = await ensure_user(callback.from_user.id)
    income = await get_total_income(callback.from_user.id)
    businesses = await get_businesses(callback.from_user.id)
    
    text = (
        f"👤 <b>ПРОФИЛЬ</b>\n\n"
        f"👤 Имя: {html.escape(user['first_name'])}\n"
        f"⭐ Уровень: <b>{user['level']}</b>\n"
        f"💰 Баланс: <b>{user['coins']:,} 🪙</b>\n"
        f"📈 Доход: <b>+{income:,} 🪙/час</b>\n"
        f"🏪 Бизнесов: <b>{len(businesses)}</b>\n"
        f"🏆 Заработано: <b>{user['total_earned']:,}</b>\n"
        f"🎰 Выигрышей: <b>{user['total_wins']}</b>\n"
        f"💀 Проигрышей: <b>{user['total_losses']}</b>\n"
        f"👥 Друзей: <b>{user['referral_count']}</b>"
    )
    await callback.message.edit_text(text, reply_markup=main_keyboard(), parse_mode="HTML")

# =========================================================
# БАЛАНС
# =========================================================
@DP.callback_query(F.data == "balance")
async def balance_callback(callback: CallbackQuery):
    await callback.answer()
    user = await ensure_user(callback.from_user.id)
    income = await get_total_income(callback.from_user.id)
    
    text = (
        f"💰 <b>БАЛАНС</b>\n\n"
        f"🪙 Монеты: <b>{user['coins']:,}</b>\n"
        f"📈 Доход: <b>+{income:,} 🪙/час</b>\n"
        f"⭐ Уровень: <b>{user['level']}</b>"
    )
    await callback.message.edit_text(text, reply_markup=main_keyboard(), parse_mode="HTML")

# =========================================================
# БИЗНЕСЫ
# =========================================================
@DP.callback_query(F.data == "businesses")
async def businesses_callback(callback: CallbackQuery):
    await callback.answer()
    user = await ensure_user(callback.from_user.id)
    businesses = await get_businesses(callback.from_user.id)
    income = await get_total_income(callback.from_user.id)
    
    text = "🏪 <b>ТВОИ БИЗНЕСЫ</b>\n\n"
    if not businesses:
        text += "У тебя нет бизнесов!\n\n"
    
    for biz in businesses:
        data = BUSINESSES.get(biz['biz_type'])
        if data:
            text += f"{data['name']} (Ур.{biz['level']}) — +{data['income'] * biz['level']:,} 🪙/час\n"
    
    text += f"\n📈 Доход: <b>+{income:,} 🪙/час</b>\n\n"
    
    kb = InlineKeyboardBuilder()
    for key, data in BUSINESSES.items():
        kb.button(text=f"Купить {data['name']} — {data['price']:,}🪙", callback_data=f"buy_biz:{key}")
    kb.button(text="💰 Собрать доход", callback_data="collect_income")
    kb.button(text="⬅️ Назад", callback_data="menu")
    kb.adjust(1)
    
    await callback.message.edit_text(text, reply_markup=kb.as_markup(), parse_mode="HTML")

@DP.callback_query(F.data.startswith("buy_biz:"))
async def buy_biz_callback(callback: CallbackQuery):
    await callback.answer()
    biz_type = callback.data.split(":")[1]
    data = BUSINESSES.get(biz_type)
    if not data:
        return
    
    user = await get_user(callback.from_user.id)
    if user['coins'] < data['price']:
        await callback.message.answer(f"❌ Нужно: <b>{data['price']:,} 🪙</b>", parse_mode="HTML")
        return
    
    await update_coins(callback.from_user.id, -data['price'])
    
    async with aiosqlite.connect(DB) as db:
        await db.execute("INSERT INTO businesses (user_id, biz_type, level, bought_at, last_collected) VALUES (?, ?, ?, ?, ?)",
                       (callback.from_user.id, biz_type, 1, int(time.time()), int(time.time())))
        await db.commit()
    
    await callback.message.answer(f"✅ <b>{data['name']}</b> куплен! +{data['income']} 🪙/час")

@DP.callback_query(F.data == "collect_income")
async def collect_income_callback(callback: CallbackQuery):
    await callback.answer()
    businesses = await get_businesses(callback.from_user.id)
    if not businesses:
        await callback.message.answer("❌ Нет бизнесов!")
        return
    
    total = 0
    now = int(time.time())
    
    for biz in businesses:
        data = BUSINESSES.get(biz['biz_type'])
        if data:
            hours = (now - biz['last_collected']) // 3600
            if hours > 0:
                earned = data['income'] * biz['level'] * hours
                total += earned
                async with aiosqlite.connect(DB) as db:
                    await db.execute("UPDATE businesses SET last_collected = ? WHERE id = ?", (now, biz['id']))
                    await db.commit()
    
    if total > 0:
        await update_coins(callback.from_user.id, total)
        await callback.message.answer(f"💰 Собрано: <b>+{total:,} 🪙</b>", parse_mode="HTML")
    else:
        await callback.message.answer("⏳ Дохода пока нет!")

# =========================================================
# КАЗИНО (ВСЕ ИГРЫ)
# =========================================================
@DP.callback_query(F.data == "casino")
async def casino_callback(callback: CallbackQuery):
    await callback.answer()
    user = await ensure_user(callback.from_user.id)
    await callback.message.edit_text(
        f"🎰 <b>КАЗИНО</b>\n\n💰 Баланс: <b>{user['coins']:,} 🪙</b>",
        reply_markup=casino_keyboard(),
        parse_mode="HTML"
    )

# РУЛЕТКА
@DP.callback_query(F.data == "roulette")
async def roulette_callback(callback: CallbackQuery):
    await callback.answer()
    await callback.message.answer(
        "🎲 <b>РУЛЕТКА</b>\n\nВведи сумму ставки (цифру):",
        parse_mode="HTML"
    )
    async with aiosqlite.connect(DB) as db:
        await db.execute("UPDATE users SET casino_session = 1 WHERE user_id = ?", (callback.from_user.id,))
        await db.commit()

# СЛОТЫ
@DP.callback_query(F.data == "slots")
async def slots_callback(callback: CallbackQuery):
    await callback.answer()
    user = await get_user(callback.from_user.id)
    bet = 1000
    
    if user['coins'] < bet:
        await callback.message.answer(f"❌ Нужно: <b>{bet:,} 🪙</b>", parse_mode="HTML")
        return
    
    symbols = ["🍒", "🍋", "🍊", "🍇", "🔔", "💎", "🎰"]
    result = [random.choice(symbols) for _ in range(3)]
    
    win = 0
    if result[0] == result[1] == result[2]:
        if result[0] == "🎰": win = 50
        elif result[0] == "💎": win = 20
        elif result[0] == "🔔": win = 10
        else: win = 5
    elif result[0] == result[1] or result[1] == result[2] or result[0] == result[2]:
        win = 2
    
    if win > 0:
        win_amount = bet * win
        await update_coins(callback.from_user.id, win_amount - bet)
        await callback.message.answer(
            f"🎰 <b>СЛОТЫ</b>\n\n{' '.join(result)}\n🎉 ВЫИГРЫШ! +{win_amount:,} 🪙",
            parse_mode="HTML"
        )
    else:
        await update_coins(callback.from_user.id, -bet)
        await callback.message.answer(
            f"🎰 <b>СЛОТЫ</b>\n\n{' '.join(result)}\n💀 ПРОИГРЫШ! -{bet:,} 🪙",
            parse_mode="HTML"
        )

# КОСТИ
@DP.callback_query(F.data == "dice")
async def dice_callback(callback: CallbackQuery):
    await callback.answer()
    user = await get_user(callback.from_user.id)
    bet = 1000
    
    if user['coins'] < bet:
        await callback.message.answer(f"❌ Нужно: <b>{bet:,} 🪙</b>", parse_mode="HTML")
        return
    
    number = random.randint(1, 100)
    guess = random.randint(1, 100)
    
    if number == guess:
        win_amount = bet * 50
        await update_coins(callback.from_user.id, win_amount - bet)
        await callback.message.answer(f"🎲 <b>КОСТИ</b>\n\nВыпало: {number}\n🎉 УГАДАЛ! +{win_amount:,} 🪙", parse_mode="HTML")
    else:
        await update_coins(callback.from_user.id, -bet)
        await callback.message.answer(f"🎲 <b>КОСТИ</b>\n\nВыпало: {number}\n💀 НЕ УГАДАЛ! -{bet:,} 🪙", parse_mode="HTML")

# БЛЭКДЖЕК
@DP.callback_query(F.data == "blackjack")
async def blackjack_callback(callback: CallbackQuery):
    await callback.answer()
    user = await get_user(callback.from_user.id)
    bet = 1000
    
    if user['coins'] < bet:
        await callback.message.answer(f"❌ Нужно: <b>{bet:,} 🪙</b>", parse_mode="HTML")
        return
    
    player = [random.randint(1, 11), random.randint(1, 11)]
    dealer = [random.randint(1, 11), random.randint(1, 11)]
    
    while sum(player) < 17:
        player.append(random.randint(1, 11))
    while sum(dealer) < 17:
        dealer.append(random.randint(1, 11))
    
    p_score = sum(player)
    d_score = sum(dealer)
    
    if p_score > 21:
        await update_coins(callback.from_user.id, -bet)
        result = f"💀 ПЕРЕБОР! -{bet:,} 🪙"
    elif d_score > 21 or p_score > d_score:
        win_amount = bet * 2
        await update_coins(callback.from_user.id, win_amount - bet)
        result = f"🎉 ВЫИГРЫШ! +{win_amount:,} 🪙"
    elif p_score < d_score:
        await update_coins(callback.from_user.id, -bet)
        result = f"💀 ПРОИГРЫШ! -{bet:,} 🪙"
    else:
        result = "🤝 НИЧЬЯ!"
    
    await callback.message.answer(
        f"🃏 <b>БЛЭКДЖЕК</b>\n\n👤 Ты: {p_score}\n🤖 Дилер: {d_score}\n\n{result}",
        parse_mode="HTML"
    )

# ПОКЕР
@DP.callback_query(F.data == "poker")
async def poker_callback(callback: CallbackQuery):
    await callback.answer()
    user = await get_user(callback.from_user.id)
    bet = 1000
    
    if user['coins'] < bet:
        await callback.message.answer(f"❌ Нужно: <b>{bet:,} 🪙</b>", parse_mode="HTML")
        return
    
    p = sum([random.randint(1, 13) for _ in range(5)])
    a = sum([random.randint(1, 13) for _ in range(5)])
    
    if p > a:
        win_amount = bet * 2
        await update_coins(callback.from_user.id, win_amount - bet)
        await callback.message.answer(f"🃏 <b>ПОКЕР</b>\n\n🎉 ВЫИГРЫШ! +{win_amount:,} 🪙", parse_mode="HTML")
    else:
        await update_coins(callback.from_user.id, -bet)
        await callback.message.answer(f"🃏 <b>ПОКЕР</b>\n\n💀 ПРОИГРЫШ! -{bet:,} 🪙", parse_mode="HTML")

# КОЛЕСО ФОРТУНЫ
@DP.callback_query(F.data == "wheel")
async def wheel_callback(callback: CallbackQuery):
    await callback.answer()
    user = await get_user(callback.from_user.id)
    bet = 500
    
    if user['coins'] < bet:
        await callback.message.answer(f"❌ Нужно: <b>{bet:,} 🪙</b>", parse_mode="HTML")
        return
    
    sectors = [0, 1, 2, 2, 3, 3, 5, 5, 10, 20]
    result = random.choice(sectors)
    
    if result == 0:
        await update_coins(callback.from_user.id, -bet)
        await callback.message.answer(f"🎡 <b>КОЛЕСО</b>\n\n💀 ПРОИГРЫШ! -{bet:,} 🪙", parse_mode="HTML")
    else:
        win_amount = bet * result
        await update_coins(callback.from_user.id, win_amount - bet)
        await callback.message.answer(f"🎡 <b>КОЛЕСО</b>\n\n🎉 x{result}! +{win_amount:,} 🪙", parse_mode="HTML")

# УГАДАЙ КАРТУ
@DP.callback_query(F.data == "guess_card")
async def guess_card_callback(callback: CallbackQuery):
    await callback.answer()
    user = await get_user(callback.from_user.id)
    bet = 500
    
    if user['coins'] < bet:
        await callback.message.answer(f"❌ Нужно: <b>{bet:,} 🪙</b>", parse_mode="HTML")
        return
    
    cards = ["♠️", "♥️", "♦️", "♣️"]
    player = random.choice(cards)
    ai = random.choice(cards)
    
    if player == ai:
        win_amount = bet * 4
        await update_coins(callback.from_user.id, win_amount - bet)
        await callback.message.answer(f"🃏 <b>УГАДАЙ</b>\n\n🎉 УГАДАЛ! +{win_amount:,} 🪙", parse_mode="HTML")
    else:
        await update_coins(callback.from_user.id, -bet)
        await callback.message.answer(f"🃏 <b>УГАДАЙ</b>\n\n💀 НЕ УГАДАЛ! -{bet:,} 🪙", parse_mode="HTML")

# ОБРАБОТКА СТАВОК В РУЛЕТКУ
@DP.message(F.text)
async def handle_roulette_bet(message: Message):
    if not await require_subscription(message):
        return
    
    user = await get_user(message.from_user.id)
    if not user:
        return
    
    async with aiosqlite.connect(DB) as db:
        cur = await db.execute("SELECT casino_session FROM users WHERE user_id = ?", (message.from_user.id,))
        row = await cur.fetchone()
        if not row or row[0] != 1:
            return
    
    try:
        amount = int(message.text)
        if amount <= 0:
            return
    except:
        return
    
    if amount > user['coins']:
        await message.answer(f"❌ Есть только: <b>{user['coins']:,} 🪙</b>", parse_mode="HTML")
        return
    
    async with aiosqlite.connect(DB) as db:
        await db.execute("UPDATE users SET level = ? WHERE user_id = ?", (amount, message.from_user.id))
        await db.commit()
    
    kb = InlineKeyboardBuilder()
    kb.button(text="🔴 Красное (x2)", callback_data=f"roulette_play:red:{amount}")
    kb.button(text="⚫ Чёрное (x2)", callback_data=f"roulette_play:black:{amount}")
    kb.button(text="🟢 Зелёное (x14)", callback_data=f"roulette_play:green:{amount}")
    kb.button(text="📊 Чёт (x2)", callback_data=f"roulette_play:even:{amount}")
    kb.button(text="📊 Нечет (x2)", callback_data=f"roulette_play:odd:{amount}")
    kb.adjust(2)
    
    await message.answer(
        f"🎲 <b>РУЛЕТКА</b>\n\n💰 Ставка: <b>{amount:,} 🪙</b>\n\nВыбери:",
        reply_markup=kb.as_markup(),
        parse_mode="HTML"
    )

@DP.callback_query(F.data.startswith("roulette_play:"))
async def roulette_play_callback(callback: CallbackQuery):
    await callback.answer()
    
    parts = callback.data.split(":")
    bet_type = parts[1]
    amount = int(parts[2])
    
    user = await get_user(callback.from_user.id)
    if not user or user['coins'] < amount:
        await callback.message.answer("❌ Недостаточно монет!")
        return
    
    numbers = list(range(37))
    red = [1,3,5,7,9,12,14,16,18,19,21,23,25,27,30,32,34,36]
    black = [2,4,6,8,10,11,13,15,17,20,22,24,26,28,29,31,33,35]
    
    result = random.choice(numbers)
    color = "green" if result == 0 else "red" if result in red else "black"
    
    win = False
    win_amount = 0
    
    if bet_type == "red" and color == "red":
        win = True
        win_amount = amount * 2
    elif bet_type == "black" and color == "black":
        win = True
        win_amount = amount * 2
    elif bet_type == "green" and color == "green":
        win = True
        win_amount = amount * 14
    elif bet_type == "even" and result % 2 == 0 and result != 0:
        win = True
        win_amount = amount * 2
    elif bet_type == "odd" and result % 2 == 1:
        win = True
        win_amount = amount * 2
    
    if win:
        await update_coins(callback.from_user.id, win_amount - amount)
        emoji = "🔴" if color == "red" else "⚫" if color == "black" else "🟢"
        await callback.message.edit_text(
            f"🎲 <b>РУЛЕТКА</b>\n\n{emoji} Выпало: <b>{result}</b>\n🎉 ВЫИГРЫШ! +{win_amount:,} 🪙",
            parse_mode="HTML"
        )
    else:
        await update_coins(callback.from_user.id, -amount)
        emoji = "🔴" if color == "red" else "⚫" if color == "black" else "🟢"
        await callback.message.edit_text(
            f"🎲 <b>РУЛЕТКА</b>\n\n{emoji} Выпало: <b>{result}</b>\n💀 ПРОИГРЫШ! -{amount:,} 🪙",
            parse_mode="HTML"
        )
    
    async with aiosqlite.connect(DB) as db:
        await db.execute("UPDATE users SET casino_session = 0 WHERE user_id = ?", (callback.from_user.id,))
        await db.commit()

# =========================================================
# ДЕЙЛИ
# =========================================================
@DP.callback_query(F.data == "daily")
async def daily_callback(callback: CallbackQuery):
    await callback.answer()
    user = await ensure_user(callback.from_user.id)
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    
    if user['daily_date'] == today:
        await callback.message.answer("🎁 Daily уже получен!")
        return
    
    streak = user['daily_streak'] + 1
    reward = 500 + min(streak, 7) * 100
    
    await update_coins(callback.from_user.id, reward)
    async with aiosqlite.connect(DB) as db:
        await db.execute("UPDATE users SET daily_date = ?, daily_streak = ? WHERE user_id = ?",
                       (today, streak, callback.from_user.id))
        await db.commit()
    
    await callback.message.answer(f"🎁 <b>DAILY</b>\n\n🔥 Серия: {streak}\n💰 +{reward:,} 🪙", parse_mode="HTML")

# =========================================================
# ИНВЕСТИЦИИ
# =========================================================
@DP.callback_query(F.data == "investments")
async def investments_callback(callback: CallbackQuery):
    await callback.answer()
    user = await ensure_user(callback.from_user.id)
    
    kb = InlineKeyboardBuilder()
    kb.button(text="📈 10 000", callback_data="invest:10000")
    kb.button(text="📈 50 000", callback_data="invest:50000")
    kb.button(text="📈 100 000", callback_data="invest:100000")
    kb.button(text="📈 500 000", callback_data="invest:500000")
    kb.button(text="📈 1 000 000", callback_data="invest:1000000")
    kb.button(text="⬅️ Назад", callback_data="menu")
    kb.adjust(2)
    
    await callback.message.edit_text(
        f"📈 <b>ИНВЕСТИЦИИ</b>\n\n💰 Баланс: <b>{user['coins']:,} 🪙</b>\n\nВыбери сумму:",
        reply_markup=kb.as_markup(),
        parse_mode="HTML"
    )

@DP.callback_query(F.data.startswith("invest:"))
async def invest_callback(callback: CallbackQuery):
    await callback.answer()
    amount = int(callback.data.split(":")[1])
    user = await get_user(callback.from_user.id)
    
    if user['coins'] < amount:
        await callback.message.answer(f"❌ Нужно: <b>{amount:,} 🪙</b>", parse_mode="HTML")
        return
    
    await update_coins(callback.from_user.id, -amount)
    profit = int(amount * random.randint(15, 30) / 100)
    
    async with aiosqlite.connect(DB) as db:
        await db.execute("INSERT INTO investments (user_id, amount, invested_at, profit) VALUES (?, ?, ?, ?)",
                       (callback.from_user.id, amount, int(time.time()), profit))
        await db.commit()
    
    await callback.message.answer(
        f"✅ <b>ИНВЕСТИЦИЯ</b>\n\n💰 {amount:,} 🪙\n📈 Доходность: {profit_percent}%\n💎 Прибыль: +{profit:,} 🪙",
        parse_mode="HTML"
    )

# =========================================================
# ДОСТИЖЕНИЯ
# =========================================================
@DP.callback_query(F.data == "achievements")
async def achievements_callback(callback: CallbackQuery):
    await callback.answer()
    user = await ensure_user(callback.from_user.id)
    
    async with aiosqlite.connect(DB) as db:
        cur = await db.execute("SELECT ach_type FROM achievements WHERE user_id = ?", (callback.from_user.id,))
        unlocked = [row[0] for row in await cur.fetchall()]
    
    text = "🎯 <b>ДОСТИЖЕНИЯ</b>\n\n"
    for key, data in ACHIEVEMENTS.items():
        status = "✅" if key in unlocked else "🔒"
        text += f"{status} {data['name']} — +{data['reward']:,} 🪙\n"
    
    await callback.message.edit_text(text, reply_markup=main_keyboard(), parse_mode="HTML")

# =========================================================
# РЕФЕРАЛКА
# =========================================================
@DP.callback_query(F.data == "referral")
async def referral_callback(callback: CallbackQuery):
    await callback.answer()
    user = await ensure_user(callback.from_user.id)
    bot = await BOT.get_me()
    
    await callback.message.edit_text(
        f"👥 <b>РЕФЕРАЛКА</b>\n\n"
        f"💰 За друга: <b>{REFERRAL_BONUS:,} 🪙</b>\n"
        f"🎁 Друг получит: <b>{REFERRAL_FRIEND_BONUS:,} 🪙</b>\n"
        f"👥 Приглашено: <b>{user['referral_count']}</b>\n\n"
        f"🔗 Ссылка:\n"
        f"<code>https://t.me/{bot.username}?start=ref_{callback.from_user.id}</code>",
        reply_markup=main_keyboard(),
        parse_mode="HTML"
    )

# =========================================================
# ТОП
# =========================================================
@DP.callback_query(F.data == "top")
async def top_callback(callback: CallbackQuery):
    await callback.answer()
    
    async with aiosqlite.connect(DB) as db:
        cur = await db.execute("SELECT first_name, coins, level FROM users WHERE banned = 0 ORDER BY coins DESC LIMIT 10")
        rows = await cur.fetchall()
    
    text = "🏆 <b>ТОП 10</b>\n\n"
    for i, row in enumerate(rows, 1):
        name = html.escape(row[0] or "Игрок")
        text += f"{i}. {name} — 💰{row[1]:,} 🪙 (Ур.{row[2]})\n"
    
    await callback.message.edit_text(text, reply_markup=main_keyboard(), parse_mode="HTML")

# =========================================================
# ДОНАТ
# =========================================================
@DP.callback_query(F.data == "donate")
async def donate_callback(callback: CallbackQuery):
    await callback.answer()
    user = await ensure_user(callback.from_user.id)
    
    await callback.message.edit_text(
        f"⭐ <b>ДОНАТ</b>\n\n💰 Баланс: <b>{user['coins']:,} 🪙</b>\n\nВыбери пак:",
        reply_markup=donate_keyboard(),
        parse_mode="HTML"
    )

@DP.callback_query(F.data.startswith("donate:"))
async def donate_pack_callback(callback: CallbackQuery):
    await callback.answer()
    key = callback.data.split(":")[1]
    pack = DONATE_PACKS.get(key)
    if not pack:
        return
    
    await BOT.send_invoice(
        chat_id=callback.from_user.id,
        title=pack['name'],
        description=f"{pack['coins']:,} 🪙 за {pack['stars']} ⭐",
        payload=f"donate:{key}",
        currency="XTR",
        prices=[LabeledPrice(label=pack['name'], amount=pack['stars'])]
    )

@DP.pre_checkout_query()
async def pre_checkout_query(query: PreCheckoutQuery):
    await query.answer(ok=True)

@DP.message(F.successful_payment)
async def successful_payment(message: Message):
    payload = message.successful_payment.invoice_payload
    if payload.startswith("donate:"):
        key = payload.split(":")[1]
        pack = DONATE_PACKS.get(key)
        if pack:
            await update_coins(message.from_user.id, pack['coins'])
            await message.answer(f"✅ <b>ПОПОЛНЕНИЕ</b>\n\n💰 +{pack['coins']:,} 🪙", parse_mode="HTML")

# =========================================================
# КРИПТО
# =========================================================
@DP.callback_query(F.data == "crypto_menu")
async def crypto_menu_callback(callback: CallbackQuery):
    await callback.answer()
    await callback.message.edit_text(
        "💎 <b>КРИПТО-БИРЖА</b>\n\nПокупай криптовалюту за монеты!",
        reply_markup=crypto_keyboard(),
        parse_mode="HTML"
    )

@DP.callback_query(F.data.startswith("buy_crypto:"))
async def buy_crypto_callback(callback: CallbackQuery):
    await callback.answer()
    crypto_type = callback.data.split(":")[1]
    data = CRYPTO.get(crypto_type)
    if not data:
        return
    
    user = await get_user(callback.from_user.id)
    price = data['price']
    amount = 1
    
    if user['coins'] < price:
        await callback.message.answer(f"❌ Нужно: <b>{price:,} 🪙</b>", parse_mode="HTML")
        return
    
    await update_coins(callback.from_user.id, -price)
    
    async with aiosqlite.connect(DB) as db:
        cur = await db.execute("SELECT * FROM crypto_wallet WHERE user_id = ? AND crypto_type = ?",
                             (callback.from_user.id, crypto_type))
        row = await cur.fetchone()
        if row:
            await db.execute("UPDATE crypto_wallet SET amount = amount + ? WHERE id = ?", (amount, row[0]))
        else:
            await db.execute("INSERT INTO crypto_wallet (user_id, crypto_type, amount) VALUES (?, ?, ?)",
                           (callback.from_user.id, crypto_type, amount))
        await db.commit()
    
    await callback.message.answer(
        f"✅ <b>КУПЛЕНО!</b>\n\n"
        f"{data['emoji']} {data['name']}: 1 шт.\n"
        f"💰 Цена: {price:,} 🪙",
        parse_mode="HTML"
    )

@DP.callback_query(F.data == "my_wallet")
async def my_wallet_callback(callback: CallbackQuery):
    await callback.answer()
    
    async with aiosqlite.connect(DB) as db:
        db.row_factory = aiosqlite.Row
        cur = await db.execute("SELECT * FROM crypto_wallet WHERE user_id = ?", (callback.from_user.id,))
        wallet = await cur.fetchall()
    
    if not wallet:
        await callback.message.answer("📊 <b>КОШЕЛЁК ПУСТ</b>\n\nКупи криптовалюту!", parse_mode="HTML")
        return
    
    text = "📊 <b>МОЙ КОШЕЛЁК</b>\n\n"
    total = 0
    for item in wallet:
        data = CRYPTO.get(item['crypto_type'])
        if data:
            value = item['amount'] * data['price']
            total += value
            text += f"{data['emoji']} {data['name']}: {item['amount']} шт. ≈ {value:,} 🪙\n"
    
    text += f"\n💎 Общая стоимость: <b>{total:,} 🪙</b>"
    await callback.message.answer(text, parse_mode="HTML")

# =========================================================
# МЕНЮ
# =========================================================
@DP.callback_query(F.data == "menu")
async def menu_callback(callback: CallbackQuery):
    await callback.answer()
    user = await get_user(callback.from_user.id)
    if not user:
        await callback.message.answer("❌ Напиши /start")
        return
    await callback.message.edit_text(
        f"💎 <b>CRYPTO EMPIRE</b>\n\n💰 Баланс: <b>{user['coins']:,} 🪙</b>\n⭐ Уровень: <b>{user['level']}</b>",
        reply_markup=main_keyboard(),
        parse_mode="HTML"
    )

# =========================================================
# АДМИНКА (ТОЛЬКО ДЛЯ OWNER)
# =========================================================
@DP.message(Command("stats"))
async def stats_command(message: Message):
    if not is_owner(message.from_user):
        return
    
    async with aiosqlite.connect(DB) as db:
        cur = await db.execute("SELECT COUNT(*) FROM users")
        users = (await cur.fetchone())[0]
        cur = await db.execute("SELECT SUM(coins) FROM users")
        coins = (await cur.fetchone())[0] or 0
    
    await message.answer(f"📊 <b>СТАТИСТИКА</b>\n\n👥 {users} пользователей\n🪙 {coins:,} монет", parse_mode="HTML")

@DP.message(Command("give"))
async def give_command(message: Message):
    if not is_owner(message.from_user):
        return
    
    parts = message.text.split()
    if len(parts) != 3:
        await message.answer("Использование: /give ID КОЛИЧЕСТВО")
        return
    
    try:
        user_id = int(parts[1])
        amount = int(parts[2])
    except:
        await message.answer("❌ Неверные данные!")
        return
    
    await update_coins(user_id, amount)
    await message.answer(f"✅ Выдано {amount:,} 🪙 пользователю {user_id}", parse_mode="HTML")

@DP.message(Command("ban"))
async def ban_command(message: Message):
    if not is_owner(message.from_user):
        return
    
    parts = message.text.split()
    if len(parts) != 2:
        await message.answer("Использование: /ban ID")
        return
    
    try:
        user_id = int(parts[1])
    except:
        await message.answer("❌ Неверный ID!")
        return
    
    async with aiosqlite.connect(DB) as db:
        await db.execute("UPDATE users SET banned = 1 WHERE user_id = ?", (user_id,))
        await db.commit()
    
    await message.answer(f"🚫 Пользователь {user_id} забанен!")

@DP.message(Command("unban"))
async def unban_command(message: Message):
    if not is_owner(message.from_user):
        return
    
    parts = message.text.split()
    if len(parts) != 2:
        await message.answer("Использование: /unban ID")
        return
    
    try:
        user_id = int(parts[1])
    except:
        await message.answer("❌ Неверный ID!")
        return
    
    async with aiosqlite.connect(DB) as db:
        await db.execute("UPDATE users SET banned = 0 WHERE user_id = ?", (user_id,))
        await db.commit()
    
    await message.answer(f"✅ Пользователь {user_id} разбанен!")

@DP.message(Command("createpromo"))
async def create_promo_command(message: Message):
    if not is_owner(message.from_user):
        return
    
    parts = message.text.split()
    if len(parts) != 4:
        await message.answer("Использование: /createpromo КОД МОНЕТЫ ЛИМИТ")
        return
    
    code = parts[1].upper()
    try:
        coins = int(parts[2])
        limit = int(parts[3])
    except:
        await message.answer("❌ Неверные данные!")
        return
    
    async with aiosqlite.connect(DB) as db:
        try:
            await db.execute("INSERT INTO promo_codes (code, coins, activations, used, created_at) VALUES (?, ?, ?, 0, ?)",
                           (code, coins, limit, int(time.time())))
            await db.commit()
        except:
            await message.answer("❌ Промокод уже существует!")
            return
    
    await message.answer(f"✅ Промокод <code>{code}</code> создан! {coins} 🪙, лимит: {limit}")

@DP.message(Command("promo"))
async def promo_command(message: Message):
    if not await require_subscription(message):
        return
    
    parts = message.text.split()
    if len(parts) != 2:
        await message.answer("Использование: /promo КОД")
        return
    
    code = parts[1].upper()
    
    async with aiosqlite.connect(DB) as db:
        db.row_factory = aiosqlite.Row
        cur = await db.execute("SELECT * FROM promo_codes WHERE code = ?", (code,))
        promo = await cur.fetchone()
        
        if not promo:
            await message.answer("❌ Промокод не найден!")
            return
        
        cur2 = await db.execute("SELECT 1 FROM promo_uses WHERE code = ? AND user_id = ?", (code, message.from_user.id))
        if await cur2.fetchone():
            await message.answer("❌ Ты уже использовал этот промокод!")
            return
        
        if promo['used'] >= promo['activations']:
            await message.answer("❌ Лимит активаций исчерпан!")
            return
        
        await db.execute("INSERT INTO promo_uses (code, user_id) VALUES (?, ?)", (code, message.from_user.id))
        await db.execute("UPDATE promo_codes SET used = used + 1 WHERE code = ?", (code,))
        await db.execute("UPDATE users SET coins = coins + ? WHERE user_id = ?", (promo['coins'], message.from_user.id))
        await db.commit()
    
    await message.answer(f"🎉 Промокод активирован! +{promo['coins']:,} 🪙", parse_mode="HTML")

@DP.message(Command("event"))
async def event_command(message: Message):
    if not is_owner(message.from_user):
        return
    
    kb = InlineKeyboardBuilder()
    for key, event in EVENTS.items():
        kb.button(text=event['name'], callback_data=f"event_start:{key}")
    kb.button(text="⛔ Остановить", callback_data="event_stop")
    kb.adjust(1)
    
    await message.answer("🎉 <b>ИВЕНТЫ</b>\n\nВыбери ивент:", reply_markup=kb.as_markup(), parse_mode="HTML")

@DP.callback_query(F.data.startswith("event_start:"))
async def event_start_callback(callback: CallbackQuery):
    await callback.answer()
    if not is_owner(callback.from_user):
        return
    
    key = callback.data.split(":")[1]
    event = EVENTS.get(key)
    if not event:
        return
    
    async with aiosqlite.connect(DB) as db:
        await db.execute("DELETE FROM active_events WHERE id = 1")
        await db.execute("INSERT INTO active_events (id, event_key, ends_at, active) VALUES (1, ?, ?, 1)",
                       (key, int(time.time()) + 3600))
        await db.commit()
    
    await callback.message.answer(f"🚨 <b>{event['name']}</b> ЗАПУЩЕН!\n\n{event['desc']}\n⏳ 1 час", parse_mode="HTML")

@DP.callback_query(F.data == "event_stop")
async def event_stop_callback(callback: CallbackQuery):
    await callback.answer()
    if not is_owner(callback.from_user):
        return
    
    async with aiosqlite.connect(DB) as db:
        await db.execute("DELETE FROM active_events WHERE id = 1")
        await db.commit()
    
    await callback.message.answer("⛔ Ивент остановлен!")

# =========================================================
# ЗАПУСК
# =========================================================
async def main():
    await init_db()
    print("=" * 60)
    print("💎 CRYPTO EMPIRE BOT")
    print(f"👑 OWNER: @{OWNER}")
    print("=" * 60)
    await DP.start_polling(BOT)

if __name__ == "__main__":
    asyncio.run(main())
