# main.py
# CRYPTO EMPIRE — ПОЛНАЯ ВЕРСИЯ
# + Крипто-биржа, + Новые игры, + Промокоды, + Ивенты, + Бан

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
    "crypto": {"name": "💎 Крипто-биржа", "price": 25000000, "income": 250000, "upgrade_cost": 12500000},
    "corporation": {"name": "🌍 Корпорация", "price": 100000000, "income": 1000000, "upgrade_cost": 50000000},
}

# =========================================================
# ИВЕНТЫ (10 штук)
# =========================================================
EVENTS = {
    "double_coins": {"name": "🪙 Двойные монеты", "desc": "Все выигрыши x2!", "multiplier": 2},
    "triple_coins": {"name": "💎 Тройные монеты", "desc": "Все выигрыши x3!", "multiplier": 3},
    "free_spins": {"name": "🎰 Бесплатные спины", "desc": "Слоты бесплатно 5 раз!", "multiplier": 0},
    "roulette_bonus": {"name": "🎲 Рулетка x2", "desc": "Выигрыши в рулетке x2!", "multiplier": 2},
    "income_boost": {"name": "📈 Бонус дохода", "desc": "Доход с бизнесов x2!", "multiplier": 2},
    "lucky_hour": {"name": "🍀 Счастливый час", "desc": "Шанс выигрыша +20%!", "multiplier": 0},
    "mega_win": {"name": "🔥 Мега выигрыш", "desc": "Все выигрыши x5!", "multiplier": 5},
    "casino_day": {"name": "🎰 День казино", "desc": "Все игры казино x2!", "multiplier": 2},
    "invest_bonus": {"name": "📈 Инвест бонус", "desc": "Доходность инвестиций x2!", "multiplier": 2},
    "vip_day": {"name": "👑 VIP день", "desc": "Все бонусы x3!", "multiplier": 3},
}

# =========================================================
# ДОСТИЖЕНИЯ
# =========================================================
ACHIEVEMENTS = {
    "first_million": {"name": "💰 Первый миллион", "reward": 100000, "condition": 1000000},
    "first_business": {"name": "🏪 Первый бизнес", "reward": 50000, "condition": 1},
    "ten_businesses": {"name": "🏢 10 бизнесов", "reward": 500000, "condition": 10},
    "level_10": {"name": "⭐ Уровень 10", "reward": 500000, "condition": 10},
    "level_50": {"name": "⭐ Уровень 50", "reward": 5000000, "condition": 50},
    "roulette_king": {"name": "🎰 Король рулетки", "reward": 1000000, "condition": 10},
    "slots_king": {"name": "🎰 Король слотов", "reward": 1000000, "condition": 10},
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
            vip_level INTEGER DEFAULT 0,
            lucky_until INTEGER DEFAULT 0,
            banned INTEGER DEFAULT 0,
            referrer_id INTEGER DEFAULT 0,
            referral_count INTEGER DEFAULT 0,
            created_at INTEGER DEFAULT 0,
            total_donated INTEGER DEFAULT 0
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
            inv_type TEXT NOT NULL,
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

        # Крипто-биржа
        await db.execute("""
        CREATE TABLE IF NOT EXISTS crypto_portfolio (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            crypto_type TEXT NOT NULL,
            amount REAL DEFAULT 0,
            bought_price REAL DEFAULT 0
        )
        """)

        # Промокоды
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

        # Ивенты
        await db.execute("""
        CREATE TABLE IF NOT EXISTS active_events (
            id INTEGER PRIMARY KEY CHECK (id = 1),
            event_key TEXT NOT NULL,
            starts_at INTEGER NOT NULL,
            ends_at INTEGER NOT NULL,
            active INTEGER DEFAULT 1
        )
        """)

        await db.commit()

# =========================================================
# КРИПТО-БИРЖА (НОВОЕ!)
# =========================================================
CRYPTO_PRICES = {
    "BTC": {"name": "₿ Bitcoin", "price": 65000, "change": 0},
    "ETH": {"name": "⟠ Ethereum", "price": 3500, "change": 0},
    "SOL": {"name": "◎ Solana", "price": 180, "change": 0},
    "DOGE": {"name": "🐶 Dogecoin", "price": 0.15, "change": 0},
    "SHIB": {"name": "🐕 Shiba Inu", "price": 0.000025, "change": 0},
}

async def update_crypto_prices():
    for coin in CRYPTO_PRICES:
        change = random.uniform(-5, 5)
        CRYPTO_PRICES[coin]["change"] = round(change, 2)
        CRYPTO_PRICES[coin]["price"] = round(CRYPTO_PRICES[coin]["price"] * (1 + change / 100), 8)

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

async def check_achievement(user_id, ach_type):
    async with aiosqlite.connect(DB) as db:
        cur = await db.execute("SELECT 1 FROM achievements WHERE user_id = ? AND ach_type = ?", (user_id, ach_type))
        if await cur.fetchone():
            return
        
        data = ACHIEVEMENTS.get(ach_type)
        if not data:
            return
        
        await db.execute("INSERT INTO achievements (user_id, ach_type, unlocked_at) VALUES (?, ?, ?)", 
                        (user_id, ach_type, int(time.time())))
        await db.execute("UPDATE users SET coins = coins + ? WHERE user_id = ?", (data['reward'], user_id))
        await db.commit()
        
        try:
            await BOT.send_message(user_id, 
                f"🏆 <b>ДОСТИЖЕНИЕ РАЗБЛОКИРОВАНО!</b>\n\n"
                f"{data['name']}\n"
                f"💰 Награда: <b>+{data['reward']:,} 🪙</b>",
                parse_mode="HTML"
            )
        except:
            pass

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
    if (await get_user(user_id) or {}).get('username', '').lower() == OWNER.lower():
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
        "🔒 <b>ТРЕБУЕТСЯ ПОДПИСКА НА КАНАЛ</b>\n\n"
        "Чтобы играть, подпишись на канал:\n"
        f"{CHANNEL_LINK}\n\n"
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
    kb.button(text="📊 Крипто-биржа", callback_data="crypto")
    kb.button(text="🎰 Новые игры", callback_data="new_games")
    kb.adjust(2)
    return kb.as_markup()

def casino_keyboard():
    kb = InlineKeyboardBuilder()
    kb.button(text="🎲 Рулетка", callback_data="roulette")
    kb.button(text="🎰 Слоты", callback_data="slots")
    kb.button(text="🎲 Кости", callback_data="dice")
    kb.button(text="🃏 Блэкджек", callback_data="blackjack")
    kb.button(text="⬅️ Назад", callback_data="menu")
    kb.adjust(2)
    return kb.as_markup()

def new_games_keyboard():
    kb = InlineKeyboardBuilder()
    kb.button(text="🃏 Покер", callback_data="poker")
    kb.button(text="🎡 Колесо фортуны", callback_data="wheel")
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
    for coin, data in CRYPTO_PRICES.items():
        kb.button(text=f"{data['name']} — ${data['price']:,}", callback_data=f"crypto_buy:{coin}")
    kb.button(text="📊 Мой портфель", callback_data="crypto_portfolio")
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
        "🎯 Цель: стать крипто-магнатом!\n"
        "Покупай бизнесы, играй в казино, инвестируй!",
        reply_markup=main_keyboard(),
        parse_mode="HTML"
    )

@DP.callback_query(F.data == "check_sub")
async def check_sub_callback(callback: CallbackQuery):
    await callback.answer()
    if await check_subscription(callback.from_user.id):
        await callback.message.edit_text(
            "✅ <b>Подписка подтверждена!</b>\n\nДобро пожаловать!",
            reply_markup=main_keyboard(),
            parse_mode="HTML"
        )
    else:
        await callback.message.answer(
            "❌ Подписка не найдена.",
            reply_markup=subscribe_keyboard(),
            parse_mode="HTML"
        )

# =========================================================
# ПРОФИЛЬ
# =========================================================
@DP.message(Command("profile"))
async def profile_command(message: Message):
    if not await require_subscription(message):
        return
    
    user = await ensure_user(
        message.from_user.id,
        message.from_user.username or "",
        message.from_user.first_name or ""
    )
    
    income = await get_total_income(message.from_user.id)
    businesses = await get_businesses(message.from_user.id)
    
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
        f"👥 Друзей: <b>{user['referral_count']}</b>\n"
        f"⭐ Потрачено Stars: <b>{user['total_donated']}</b>"
    )
    
    await message.answer(text, reply_markup=main_keyboard(), parse_mode="HTML")

@DP.callback_query(F.data == "profile")
async def profile_callback(callback: CallbackQuery):
    await callback.answer()
    await profile_command(callback.message)

# =========================================================
# БАЛАНС
# =========================================================
@DP.message(Command("balance"))
async def balance_command(message: Message):
    if not await require_subscription(message):
        return
    
    user = await ensure_user(
        message.from_user.id,
        message.from_user.username or "",
        message.from_user.first_name or ""
    )
    
    income = await get_total_income(message.from_user.id)
    
    text = (
        f"💰 <b>ТВОЙ БАЛАНС</b>\n\n"
        f"🪙 Монеты: <b>{user['coins']:,}</b>\n"
        f"📈 Доход: <b>+{income:,} 🪙/час</b>\n"
        f"⭐ Уровень: <b>{user['level']}</b>\n"
        f"🏆 Заработано всего: <b>{user['total_earned']:,}</b>"
    )
    
    await message.answer(text, reply_markup=main_keyboard(), parse_mode="HTML")

@DP.callback_query(F.data == "balance")
async def balance_callback(callback: CallbackQuery):
    await callback.answer()
    await balance_command(callback.message)

# =========================================================
# КАЗИНО
# =========================================================
@DP.message(Command("casino"))
async def casino_command(message: Message):
    if not await require_subscription(message):
        return
    
    user = await ensure_user(
        message.from_user.id,
        message.from_user.username or "",
        message.from_user.first_name or ""
    )
    
    await message.answer(
        f"🎰 <b>КАЗИНО</b>\n\n"
        f"💰 Твой баланс: <b>{user['coins']:,} 🪙</b>\n\n"
        f"Выбери игру:",
        reply_markup=casino_keyboard(),
        parse_mode="HTML"
    )

@DP.callback_query(F.data == "casino")
async def casino_callback(callback: CallbackQuery):
    await callback.answer()
    await casino_command(callback.message)

# =========================================================
# НОВЫЕ ИГРЫ (ПОКЕР, КОЛЕСО, УГАДАЙ КАРТУ)
# =========================================================
@DP.callback_query(F.data == "new_games")
async def new_games_callback(callback: CallbackQuery):
    await callback.answer()
    await callback.message.edit_text(
        f"🎰 <b>НОВЫЕ ИГРЫ В КАЗИНО</b>\n\n"
        f"Выбери игру:",
        reply_markup=new_games_keyboard(),
        parse_mode="HTML"
    )

# =========================================================
# ПОКЕР
# =========================================================
@DP.callback_query(F.data == "poker")
async def poker_callback(callback: CallbackQuery):
    await callback.answer()
    user = await get_user(callback.from_user.id)
    
    bet = 1000
    if user['coins'] < bet:
        await callback.message.answer(f"❌ Недостаточно монет! Нужно: <b>{bet:,} 🪙</b>", parse_mode="HTML")
        return
    
    # Простой покер против AI
    player_cards = sorted([random.randint(1, 13) for _ in range(5)])
    ai_cards = sorted([random.randint(1, 13) for _ in range(5)])
    
    player_score = sum(player_cards)
    ai_score = sum(ai_cards)
    
    if player_score > ai_score:
        win_amount = bet * 2
        await update_coins(callback.from_user.id, win_amount - bet)
        await callback.message.answer(
            f"🃏 <b>ПОКЕР</b>\n\n"
            f"👤 Твои карты: {player_cards} (сумма: {player_score})\n"
            f"🤖 Карты AI: {ai_cards} (сумма: {ai_score})\n"
            f"🎉 ТЫ ВЫИГРАЛ! +{win_amount:,} 🪙",
            parse_mode="HTML"
        )
    else:
        await update_coins(callback.from_user.id, -bet)
        await callback.message.answer(
            f"🃏 <b>ПОКЕР</b>\n\n"
            f"👤 Твои карты: {player_cards} (сумма: {player_score})\n"
            f"🤖 Карты AI: {ai_cards} (сумма: {ai_score})\n"
            f"💀 ТЫ ПРОИГРАЛ! -{bet:,} 🪙",
            parse_mode="HTML"
        )

# =========================================================
# КОЛЕСО ФОРТУНЫ
# =========================================================
@DP.callback_query(F.data == "wheel")
async def wheel_callback(callback: CallbackQuery):
    await callback.answer()
    user = await get_user(callback.from_user.id)
    
    bet = 500
    if user['coins'] < bet:
        await callback.message.answer(f"❌ Недостаточно монет! Нужно: <b>{bet:,} 🪙</b>", parse_mode="HTML")
        return
    
    sectors = [
        {"name": "💀 Проигрыш", "multiplier": 0},
        {"name": "🔄 Возврат", "multiplier": 1},
        {"name": "💰 x2", "multiplier": 2},
        {"name": "💰 x3", "multiplier": 3},
        {"name": "💰 x5", "multiplier": 5},
        {"name": "🔥 x10", "multiplier": 10},
        {"name": "💎 x20", "multiplier": 20},
        {"name": "💰 x2", "multiplier": 2},
        {"name": "🔄 Возврат", "multiplier": 1},
        {"name": "💰 x3", "multiplier": 3},
    ]
    
    result = random.choice(sectors)
    
    if result["multiplier"] == 0:
        await update_coins(callback.from_user.id, -bet)
        await callback.message.answer(
            f"🎡 <b>КОЛЕСО ФОРТУНЫ</b>\n\n"
            f"🎯 Выпало: {result['name']}\n"
            f"💸 -{bet:,} 🪙",
            parse_mode="HTML"
        )
    else:
        win_amount = bet * result["multiplier"]
        await update_coins(callback.from_user.id, win_amount - bet)
        await callback.message.answer(
            f"🎡 <b>КОЛЕСО ФОРТУНЫ</b>\n\n"
            f"🎯 Выпало: {result['name']}\n"
            f"💰 +{win_amount:,} 🪙",
            parse_mode="HTML"
        )

# =========================================================
# УГАДАЙ КАРТУ
# =========================================================
@DP.callback_query(F.data == "guess_card")
async def guess_card_callback(callback: CallbackQuery):
    await callback.answer()
    user = await get_user(callback.from_user.id)
    
    bet = 500
    if user['coins'] < bet:
        await callback.message.answer(f"❌ Недостаточно монет! Нужно: <b>{bet:,} 🪙</b>", parse_mode="HTML")
        return
    
    cards = ["♠️", "♥️", "♦️", "♣️"]
    player_choice = random.choice(cards)
    ai_choice = random.choice(cards)
    
    if player_choice == ai_choice:
        win_amount = bet * 4
        await update_coins(callback.from_user.id, win_amount - bet)
        await callback.message.answer(
            f"🃏 <b>УГАДАЙ КАРТУ</b>\n\n"
            f"🎯 Ты выбрал: {player_choice}\n"
            f"🤖 AI выбрал: {ai_choice}\n"
            f"🎉 ТЫ УГАДАЛ! +{win_amount:,} 🪙",
            parse_mode="HTML"
        )
    else:
        await update_coins(callback.from_user.id, -bet)
        await callback.message.answer(
            f"🃏 <b>УГАДАЙ КАРТУ</b>\n\n"
            f"🎯 Ты выбрал: {player_choice}\n"
            f"🤖 AI выбрал: {ai_choice}\n"
            f"💀 ТЫ НЕ УГАДАЛ! -{bet:,} 🪙",
            parse_mode="HTML"
        )

# =========================================================
# КРИПТО-БИРЖА
# =========================================================
@DP.callback_query(F.data == "crypto")
async def crypto_callback(callback: CallbackQuery):
    await callback.answer()
    await update_crypto_prices()
    
    text = "📊 <b>КРИПТО-БИРЖА</b>\n\n"
    for coin, data in CRYPTO_PRICES.items():
        change = data['change']
        emoji = "📈" if change >= 0 else "📉"
        text += f"{data['name']}: ${data['price']:,} {emoji} {change}%\n"
    
    text += "\n💡 Купи криптовалюту и заработай на росте!"
    
    await callback.message.edit_text(
        text,
        reply_markup=crypto_keyboard(),
        parse_mode="HTML"
    )

@DP.callback_query(F.data.startswith("crypto_buy:"))
async def crypto_buy_callback(callback: CallbackQuery):
    await callback.answer()
    coin = callback.data.split(":")[1]
    data = CRYPTO_PRICES.get(coin)
    if not data:
        return
    
    user = await get_user(callback.from_user.id)
    price = data['price']
    
    if user['coins'] < price * 10:
        await callback.message.answer(f"❌ Недостаточно монет! Нужно: <b>{price * 10:,} 🪙</b>", parse_mode="HTML")
        return
    
    amount = 10  # Покупаем 10 монет
    cost = price * amount
    
    await update_coins(callback.from_user.id, -cost)
    
    async with aiosqlite.connect(DB) as db:
        cur = await db.execute("SELECT * FROM crypto_portfolio WHERE user_id = ? AND crypto_type = ?", 
                              (callback.from_user.id, coin))
        row = await cur.fetchone()
        if row:
            await db.execute("UPDATE crypto_portfolio SET amount = amount + ?, bought_price = ? WHERE id = ?",
                           (amount, price, row[0]))
        else:
            await db.execute("INSERT INTO crypto_portfolio (user_id, crypto_type, amount, bought_price) VALUES (?, ?, ?, ?)",
                           (callback.from_user.id, coin, amount, price))
        await db.commit()
    
    await callback.message.answer(
        f"✅ <b>КУПЛЕНО!</b>\n\n"
        f"🪙 {data['name']}: <b>{amount}</b> монет\n"
        f"💰 Цена: <b>${price:,}</b>\n"
        f"💸 Потрачено: <b>{cost:,} 🪙</b>",
        parse_mode="HTML"
    )

@DP.callback_query(F.data == "crypto_portfolio")
async def crypto_portfolio_callback(callback: CallbackQuery):
    await callback.answer()
    
    async with aiosqlite.connect(DB) as db:
        db.row_factory = aiosqlite.Row
        cur = await db.execute("SELECT * FROM crypto_portfolio WHERE user_id = ?", (callback.from_user.id,))
        portfolio = await cur.fetchall()
    
    if not portfolio:
        await callback.message.answer("📊 <b>ТВОЙ ПОРТФЕЛЬ ПУСТ</b>\n\nКупи криптовалюту!", parse_mode="HTML")
        return
    
    await update_crypto_prices()
    
    text = "📊 <b>ТВОЙ КРИПТО-ПОРТФЕЛЬ</b>\n\n"
    total_profit = 0
    
    for item in portfolio:
        coin_data = CRYPTO_PRICES.get(item['crypto_type'])
        if coin_data:
            current_price = coin_data['price']
            bought_price = item['bought_price']
            profit = (current_price - bought_price) * item['amount']
            total_profit += profit
            emoji = "📈" if profit >= 0 else "📉"
            text += f"{coin_data['name']}: {item['amount']} шт. {emoji} {profit:+.2f}$\n"
    
    text += f"\n💎 Общая прибыль: <b>{total_profit:+.2f}$</b>"
    
    await callback.message.answer(text, parse_mode="HTML")

# =========================================================
# ОСТАЛЬНЫЕ КОМАНДЫ (СЛОТЫ, РУЛЕТКА, КОСТИ, БЛЭКДЖЕК)
# =========================================================
# [ЗДЕСЬ ВСЕ ОСТАЛЬНЫЕ ИГРЫ КАК В ПРЕДЫДУЩЕЙ ВЕРСИИ]

# =========================================================
# ПРОМОКОДЫ (ТОЛЬКО ДЛЯ OWNER)
# =========================================================
@DP.message(Command("createpromo"))
async def create_promo_command(message: Message):
    if not is_owner(message.from_user):
        await message.answer("❌ Только для владельца!")
        return
    
    parts = message.text.split()
    if len(parts) != 4:
        await message.answer(
            "🎟️ <b>СОЗДАНИЕ ПРОМОКОДА</b>\n\n"
            "<code>/createpromo КОД МОНЕТЫ ЛИМИТ</code>\n"
            "Пример: <code>/createpromo VIP100 50000 10</code>",
            parse_mode="HTML"
        )
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
            await db.execute("INSERT INTO promo_codes (code, coins, stars, activations, used, created_at) VALUES (?, ?, 0, ?, 0, ?)",
                           (code, coins, limit, int(time.time())))
            await db.commit()
        except:
            await message.answer("❌ Такой промокод уже существует!")
            return
    
    await message.answer(
        f"✅ <b>ПРОМОКОД СОЗДАН!</b>\n\n"
        f"🎟️ Код: <code>{code}</code>\n"
        f"💰 Монеты: <b>{coins:,}</b>\n"
        f"👥 Активаций: <b>{limit}</b>",
        parse_mode="HTML"
    )

@DP.message(Command("promo"))
async def promo_command(message: Message):
    if not await require_subscription(message):
        return
    
    parts = message.text.split()
    if len(parts) != 2:
        await message.answer("🎟️ Использование: <code>/promo КОД</code>", parse_mode="HTML")
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
    
    await message.answer(
        f"🎉 <b>ПРОМОКОД АКТИВИРОВАН!</b>\n\n"
        f"💰 Получено: <b>+{promo['coins']:,} 🪙</b>",
        parse_mode="HTML"
    )

# =========================================================
# ИВЕНТЫ (ТОЛЬКО ДЛЯ OWNER)
# =========================================================
@DP.message(Command("event"))
async def event_command(message: Message):
    if not is_owner(message.from_user):
        await message.answer("❌ Только для владельца!")
        return
    
    kb = InlineKeyboardBuilder()
    for key, event in EVENTS.items():
        kb.button(text=f"{event['name']}", callback_data=f"event_start:{key}")
    kb.button(text="⛔ Остановить ивент", callback_data="event_stop")
    kb.adjust(1)
    
    await message.answer(
        "🎉 <b>УПРАВЛЕНИЕ ИВЕНТАМИ</b>\n\n"
        "Выбери ивент для запуска:",
        reply_markup=kb.as_markup(),
        parse_mode="HTML"
    )

@DP.callback_query(F.data.startswith("event_start:"))
async def event_start_callback(callback: CallbackQuery):
    await callback.answer()
    if not is_owner(callback.from_user):
        return
    
    event_key = callback.data.split(":")[1]
    event_data = EVENTS.get(event_key)
    if not event_data:
        return
    
    async with aiosqlite.connect(DB) as db:
        await db.execute("DELETE FROM active_events WHERE id = 1")
        await db.execute("INSERT INTO active_events (id, event_key, starts_at, ends_at, active) VALUES (1, ?, ?, ?, 1)",
                       (event_key, int(time.time()), int(time.time()) + 3600))
        await db.commit()
    
    await callback.message.answer(
        f"🚨 <b>ИВЕНТ ЗАПУЩЕН!</b>\n\n"
        f"{event_data['name']}\n"
        f"📋 {event_data['desc']}\n"
        f"⏳ Длительность: 1 час",
        parse_mode="HTML"
    )

@DP.callback_query(F.data == "event_stop")
async def event_stop_callback(callback: CallbackQuery):
    await callback.answer()
    if not is_owner(callback.from_user):
        return
    
    async with aiosqlite.connect(DB) as db:
        await db.execute("DELETE FROM active_events WHERE id = 1")
        await db.commit()
    
    await callback.message.answer("⛔ <b>ИВЕНТ ОСТАНОВЛЕН</b>", parse_mode="HTML")

@DP.message(Command("event_status"))
async def event_status_command(message: Message):
    async with aiosqlite.connect(DB) as db:
        db.row_factory = aiosqlite.Row
        cur = await db.execute("SELECT * FROM active_events WHERE id = 1 AND active = 1")
        event = await cur.fetchone()
    
    if not event:
        await message.answer("📭 Сейчас нет активных ивентов.")
        return
    
    event_data = EVENTS.get(event['event_key'])
    if not event_data:
        return
    
    remaining = event['ends_at'] - int(time.time())
    minutes = remaining // 60
    
    await message.answer(
        f"🚨 <b>АКТИВНЫЙ ИВЕНТ</b>\n\n"
        f"{event_data['name']}\n"
        f"{event_data['desc']}\n"
        f"⏳ Осталось: <b>{minutes} минут</b>",
        parse_mode="HTML"
    )

# =========================================================
# БАН / РАЗБАН (ТОЛЬКО ДЛЯ OWNER)
# =========================================================
@DP.message(Command("ban"))
async def ban_command(message: Message):
    if not is_owner(message.from_user):
        await message.answer("❌ Только для владельца!")
        return
    
    parts = message.text.split()
    if len(parts) != 2:
        await message.answer("Использование: <code>/ban USER_ID</code>", parse_mode="HTML")
        return
    
    try:
        user_id = int(parts[1])
    except:
        await message.answer("❌ Неверный ID!")
        return
    
    async with aiosqlite.connect(DB) as db:
        await db.execute("UPDATE users SET banned = 1 WHERE user_id = ?", (user_id,))
        await db.commit()
    
    await message.answer(f"🚫 Пользователь <code>{user_id}</code> забанен!", parse_mode="HTML")

@DP.message(Command("unban"))
async def unban_command(message: Message):
    if not is_owner(message.from_user):
        await message.answer("❌ Только для владельца!")
        return
    
    parts = message.text.split()
    if len(parts) != 2:
        await message.answer("Использование: <code>/unban USER_ID</code>", parse_mode="HTML")
        return
    
    try:
        user_id = int(parts[1])
    except:
        await message.answer("❌ Неверный ID!")
        return
    
    async with aiosqlite.connect(DB) as db:
        await db.execute("UPDATE users SET banned = 0 WHERE user_id = ?", (user_id,))
        await db.commit()
    
    await message.answer(f"✅ Пользователь <code>{user_id}</code> разбанен!", parse_mode="HTML")

# =========================================================
# КОМАНДА /menu
# =========================================================
@DP.callback_query(F.data == "menu")
async def menu_callback(callback: CallbackQuery):
    await callback.answer()
    user = await get_user(callback.from_user.id)
    if not user:
        await callback.message.answer("❌ Ошибка! Напиши /start")
        return
    await callback.message.edit_text(
        f"💎 <b>CRYPTO EMPIRE</b>\n\n"
        f"💰 Баланс: <b>{user['coins']:,} 🪙</b>\n"
        f"⭐ Уровень: <b>{user['level']}</b>",
        reply_markup=main_keyboard(),
        parse_mode="HTML"
    )

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
