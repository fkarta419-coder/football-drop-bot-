# main.py
# CRYPTO EMPIRE — ПОЛНАЯ ВЕРСИЯ
# КАЗИНО + БИЗНЕСЫ + КЛАНЫ + ДОСТИЖЕНИЯ

import os
import time
import random
import asyncio
import html
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

START_COINS = 5000
REFERRAL_BONUS = 25000
REFERRAL_FRIEND_BONUS = 5000

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
# ДОСТИЖЕНИЯ
# =========================================================
ACHIEVEMENTS = {
    "first_million": {"name": "💰 Первый миллион", "reward": 100000, "condition": 1000000},
    "first_business": {"name": "🏪 Первый бизнес", "reward": 50000, "condition": 1},
    "ten_businesses": {"name": "🏢 10 бизнесов", "reward": 500000, "condition": 10},
    "level_10": {"name": "⭐ Уровень 10", "reward": 500000, "condition": 10},
    "level_50": {"name": "⭐ Уровень 50", "reward": 5000000, "condition": 50},
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
            coins INTEGER DEFAULT 5000,
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
            created_at INTEGER DEFAULT 0
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
        CREATE TABLE IF NOT EXISTS clans (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            owner_id INTEGER NOT NULL,
            created_at INTEGER DEFAULT 0,
            coins INTEGER DEFAULT 0,
            level INTEGER DEFAULT 1,
            members_count INTEGER DEFAULT 1
        )
        """)

        await db.execute("""
        CREATE TABLE IF NOT EXISTS clan_members (
            user_id INTEGER PRIMARY KEY,
            clan_id INTEGER NOT NULL,
            role TEXT DEFAULT 'member',
            joined_at INTEGER DEFAULT 0
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
        CREATE TABLE IF NOT EXISTS bet_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            game_type TEXT NOT NULL,
            bet_amount INTEGER NOT NULL,
            win_amount INTEGER DEFAULT 0,
            result TEXT NOT NULL,
            created_at INTEGER DEFAULT 0
        )
        """)

        await db.execute("""
        CREATE TABLE IF NOT EXISTS casino_stats (
            user_id INTEGER PRIMARY KEY,
            roulette_plays INTEGER DEFAULT 0,
            slots_plays INTEGER DEFAULT 0,
            dice_plays INTEGER DEFAULT 0,
            blackjack_plays INTEGER DEFAULT 0,
            roulette_wins INTEGER DEFAULT 0,
            slots_wins INTEGER DEFAULT 0,
            dice_wins INTEGER DEFAULT 0,
            blackjack_wins INTEGER DEFAULT 0
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
        
        await db.execute("INSERT INTO casino_stats (user_id) VALUES (?)", (user_id,))
        
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
    next_level = current_level + 1
    next_exp = LEVELS.get(next_level, 99999999)
    
    while new_exp >= next_exp:
        new_exp -= next_exp
        current_level += 1
        next_level = current_level + 1
        next_exp = LEVELS.get(next_level, 99999999)
        
        await db_execute("UPDATE users SET level = level + 1 WHERE user_id = ?", (user_id,))
    
    async with aiosqlite.connect(DB) as db:
        await db.execute("UPDATE users SET exp = ? WHERE user_id = ?", (new_exp, user_id))
        await db.commit()

async def db_execute(query, params=()):
    async with aiosqlite.connect(DB) as db:
        await db.execute(query, params)
        await db.commit()

# =========================================================
# КЛАВИАТУРЫ
# =========================================================
def main_keyboard():
    kb = InlineKeyboardBuilder()
    kb.button(text="👤 Профиль", callback_data="profile")
    kb.button(text="🏪 Бизнесы", callback_data="businesses")
    kb.button(text="🎰 Казино", callback_data="casino")
    kb.button(text="🏆 Кланы", callback_data="clans")
    kb.button(text="🎯 Достижения", callback_data="achievements")
    kb.button(text="👥 Рефералка", callback_data="referral")
    kb.button(text="🏆 Топ", callback_data="top")
    kb.button(text="💰 Баланс", callback_data="balance")
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

def roulette_keyboard():
    kb = InlineKeyboardBuilder()
    kb.button(text="🔴 Красное (x2)", callback_data="roulette_bet:red")
    kb.button(text="⚫ Чёрное (x2)", callback_data="roulette_bet:black")
    kb.button(text="🟢 Зелёное (x14)", callback_data="roulette_bet:green")
    kb.button(text="📊 Чёт (x2)", callback_data="roulette_bet:even")
    kb.button(text="📊 Нечет (x2)", callback_data="roulette_bet:odd")
    kb.button(text="⬅️ Назад", callback_data="casino")
    kb.adjust(2)
    return kb.as_markup()

# =========================================================
# ПОДПИСКА
# =========================================================
def subscribe_keyboard():
    kb = InlineKeyboardBuilder()
    kb.button(text="📢 Подписаться", url=CHANNEL_LINK)
    kb.button(text="✅ Проверить", callback_data="check_sub")
    kb.adjust(1)
    return kb.as_markup()

async def require_subscription(message):
    if (message.from_user.username or "").lower() == OWNER.lower():
        return True
    if not REQUIRED_CHANNEL:
        return True
    try:
        member = await BOT.get_chat_member(REQUIRED_CHANNEL, message.from_user.id)
        if member.status in ("creator", "administrator", "member"):
            return True
    except:
        pass
    
    await message.answer(
        "🔒 <b>ТРЕБУЕТСЯ ПОДПИСКА</b>\n\n"
        f"Подпишись на канал: {CHANNEL_LINK}",
        reply_markup=subscribe_keyboard(),
        parse_mode="HTML"
    )
    return False

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
        "Цель: стать крипто-магнатом!\n"
        "Покупай бизнесы, играй в казино, инвестируй!",
        reply_markup=main_keyboard(),
        parse_mode="HTML"
    )

@DP.callback_query(F.data == "check_sub")
async def check_sub_callback(callback: CallbackQuery):
    await callback.answer()
    try:
        member = await BOT.get_chat_member(REQUIRED_CHANNEL, callback.from_user.id)
        if member.status in ("creator", "administrator", "member"):
            await callback.message.edit_text(
                "✅ Подписка подтверждена!",
                reply_markup=main_keyboard(),
                parse_mode="HTML"
            )
        else:
            await callback.message.answer("❌ Подписка не найдена.", reply_markup=subscribe_keyboard())
    except:
        await callback.message.answer("❌ Ошибка.", reply_markup=subscribe_keyboard())

# =========================================================
# ПРОФИЛЬ
# =========================================================
@DP.message(Command("profile"))
async def profile_command(message: Message):
    if not await require_subscription(message):
        return
    user = await get_user(message.from_user.id)
    income = await get_total_income(message.from_user.id)
    businesses = await get_businesses(message.from_user.id)
    
    await message.answer(
        f"👤 <b>ПРОФИЛЬ</b>\n\n"
        f"Имя: {html.escape(user['first_name'])}\n"
        f"⭐ Уровень: <b>{user['level']}</b>\n"
        f"💰 Баланс: <b>{user['coins']:,} 🪙</b>\n"
        f"📈 Доход: <b>+{income:,} 🪙/час</b>\n"
        f"🏪 Бизнесов: <b>{len(businesses)}</b>\n"
        f"🏆 Заработано: <b>{user['total_earned']:,}</b>\n"
        f"🎰 Выигрышей: <b>{user['total_wins']}</b>\n"
        f"👥 Друзей: <b>{user['referral_count']}</b>",
        reply_markup=main_keyboard(),
        parse_mode="HTML"
    )

@DP.callback_query(F.data == "profile")
async def profile_callback(callback: CallbackQuery):
    await callback.answer()
    await profile_command(callback.message)

@DP.callback_query(F.data == "balance")
async def balance_callback(callback: CallbackQuery):
    await callback.answer()
    user = await get_user(callback.from_user.id)
    income = await get_total_income(callback.from_user.id)
    await callback.message.edit_text(
        f"💰 <b>БАЛАНС</b>\n\n"
        f"🪙 Монеты: <b>{user['coins']:,}</b>\n"
        f"📈 Доход: <b>+{income:,} 🪙/час</b>\n"
        f"⭐ Уровень: <b>{user['level']}</b>",
        reply_markup=main_keyboard(),
        parse_mode="HTML"
    )

@DP.message(Command("balance"))
async def balance_command(message: Message):
    if not await require_subscription(message):
        return
    await balance_callback(message)

# =========================================================
# БИЗНЕСЫ
# =========================================================
@DP.message(Command("businesses"))
async def businesses_command(message: Message):
    if not await require_subscription(message):
        return
    user = await get_user(message.from_user.id)
    businesses = await get_businesses(message.from_user.id)
    income = await get_total_income(message.from_user.id)
    
    text = "🏪 <b>ТВОИ БИЗНЕСЫ</b>\n\n"
    if not businesses:
        text += "У тебя пока нет бизнесов!\nКупи первый бизнес:\n\n"
    else:
        for biz in businesses:
            data = BUSINESSES.get(biz['biz_type'])
            if data:
                text += f"{data['emoji']} {data['name']} (Ур.{biz['level']}) — +{data['income'] * biz['level']:,} 🪙/час\n"
        text += f"\n📈 Общий доход: <b>+{income:,} 🪙/час</b>\n\n"
    
    kb = InlineKeyboardBuilder()
    for key, data in BUSINESSES.items():
        kb.button(text=f"Купить {data['name']} — {data['price']:,}🪙", callback_data=f"buy_biz:{key}")
    kb.button(text="⬅️ Назад", callback_data="menu")
    kb.adjust(1)
    
    await message.answer(text, reply_markup=kb.as_markup(), parse_mode="HTML")

@DP.callback_query(F.data == "businesses")
async def businesses_callback(callback: CallbackQuery):
    await callback.answer()
    await businesses_command(callback.message)

@DP.callback_query(F.data.startswith("buy_biz:"))
async def buy_biz_callback(callback: CallbackQuery):
    await callback.answer()
    biz_type = callback.data.split(":")[1]
    data = BUSINESSES.get(biz_type)
    if not data:
        return
    
    user = await get_user(callback.from_user.id)
    if user['coins'] < data['price']:
        await callback.message.answer(f"❌ Недостаточно монет! Нужно: <b>{data['price']:,} 🪙</b>", parse_mode="HTML")
        return
    
    await update_coins(callback.from_user.id, -data['price'])
    
    async with aiosqlite.connect(DB) as db:
        await db.execute("""
            INSERT INTO businesses (user_id, biz_type, level, bought_at, last_collected)
            VALUES (?, ?, ?, ?, ?)
        """, (callback.from_user.id, biz_type, 1, int(time.time()), int(time.time())))
        await db.commit()
    
    # Проверка достижения
    businesses = await get_businesses(callback.from_user.id)
    if len(businesses) >= 10:
        await check_achievement(callback.from_user.id, "ten_businesses")
    
    await callback.message.answer(
        f"✅ <b>{data['name']}</b> куплен!\n"
        f"💰 Доход: <b>+{data['income']} 🪙/час</b>",
        parse_mode="HTML"
    )

@DP.callback_query(F.data == "collect_income")
async def collect_income_callback(callback: CallbackQuery):
    await callback.answer()
    businesses = await get_businesses(callback.from_user.id)
    if not businesses:
        await callback.message.answer("❌ У тебя нет бизнесов!")
        return
    
    total_income = 0
    now = int(time.time())
    
    for biz in businesses:
        data = BUSINESSES.get(biz['biz_type'])
        if data:
            hours = (now - biz['last_collected']) // 3600
            if hours > 0:
                earned = data['income'] * biz['level'] * hours
                total_income += earned
                
                async with aiosqlite.connect(DB) as db:
                    await db.execute("UPDATE businesses SET last_collected = ? WHERE id = ?", (now, biz['id']))
                    await db.commit()
    
    if total_income > 0:
        await update_coins(callback.from_user.id, total_income)
        await callback.message.answer(f"💰 Собрано доходов: <b>+{total_income:,} 🪙</b>", parse_mode="HTML")
    else:
        await callback.message.answer("⏳ Доходов пока нет. Подожди ещё!")

# =========================================================
# ДОСТИЖЕНИЯ
# =========================================================
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

@DP.message(Command("achievements"))
async def achievements_command(message: Message):
    if not await require_subscription(message):
        return
    
    async with aiosqlite.connect(DB) as db:
        cur = await db.execute("SELECT ach_type FROM achievements WHERE user_id = ?", (message.from_user.id,))
        unlocked = [row[0] for row in await cur.fetchall()]
    
    text = "🎯 <b>ДОСТИЖЕНИЯ</b>\n\n"
    for key, data in ACHIEVEMENTS.items():
        status = "✅" if key in unlocked else "🔒"
        text += f"{status} {data['name']} — +{data['reward']:,} 🪙\n"
    
    await message.answer(text, parse_mode="HTML", reply_markup=main_keyboard())

@DP.callback_query(F.data == "achievements")
async def achievements_callback(callback: CallbackQuery):
    await callback.answer()
    await achievements_command(callback.message)

# =========================================================
# РЕФЕРАЛКА
# =========================================================
@DP.message(Command("referral"))
async def referral_command(message: Message):
    if not await require_subscription(message):
        return
    
    bot_info = await BOT.get_me()
    await message.answer(
        f"👥 <b>РЕФЕРАЛЬНАЯ СИСТЕМА</b>\n\n"
        f"Приведи друга и получи <b>{REFERRAL_BONUS:,} 🪙</b>!\n"
        f"Друг получит <b>{REFERRAL_FRIEND_BONUS:,} 🪙</b>\n\n"
        f"Твоя ссылка:\n"
        f"<code>https://t.me/{bot_info.username}?start=ref_{message.from_user.id}</code>",
        parse_mode="HTML",
        reply_markup=main_keyboard()
    )

@DP.callback_query(F.data == "referral")
async def referral_callback(callback: CallbackQuery):
    await callback.answer()
    await referral_command(callback.message)

# =========================================================
# ТОП
# =========================================================
@DP.message(Command("top"))
async def top_command(message: Message):
    if not await require_subscription(message):
        return
    
    async with aiosqlite.connect(DB) as db:
        cur = await db.execute("""
            SELECT first_name, coins, level FROM users 
            WHERE banned = 0 
            ORDER BY coins DESC 
            LIMIT 10
        """)
        rows = await cur.fetchall()
    
    text = "🏆 <b>ТОП 10 ПО БОГАТСТВУ</b>\n\n"
    for i, row in enumerate(rows, 1):
        name = html.escape(row[0] or "Игрок")
        text += f"{i}. {name} — 💰{row[1]:,} 🪙 (Ур.{row[2]})\n"
    
    await message.answer(text, parse_mode="HTML", reply_markup=main_keyboard())

@DP.callback_query(F.data == "top")
async def top_callback(callback: CallbackQuery):
    await callback.answer()
    await top_command(callback.message)

# =========================================================
# КАЗИНО
# =========================================================
@DP.message(Command("casino"))
async def casino_command(message: Message):
    if not await require_subscription(message):
        return
    
    user = await get_user(message.from_user.id)
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

@DP.callback_query(F.data == "menu")
async def menu_callback(callback: CallbackQuery):
    await callback.answer()
    user = await get_user(callback.from_user.id)
    await callback.message.edit_text(
        f"💎 <b>CRYPTO EMPIRE</b>\n\n"
        f"💰 Баланс: <b>{user['coins']:,} 🪙</b>\n"
        f"⭐ Уровень: <b>{user['level']}</b>",
        reply_markup=main_keyboard(),
        parse_mode="HTML"
    )

# =========================================================
# РУЛЕТКА
# =========================================================
@DP.callback_query(F.data == "roulette")
async def roulette_callback(callback: CallbackQuery):
    await callback.answer()
    user = await get_user(callback.from_user.id)
    await callback.message.edit_text(
        f"🎲 <b>РУЛЕТКА</b>\n\n"
        f"💰 Баланс: <b>{user['coins']:,} 🪙</b>\n\n"
        f"Выбери ставку (введи сумму в чате):\n"
        f"<code>1000</code> — поставить 1000\n"
        f"<code>all</code> — поставить всё\n\n"
        f"После этого выбери цвет:",
        reply_markup=roulette_keyboard(),
        parse_mode="HTML"
    )

@DP.callback_query(F.data.startswith("roulette_bet:"))
async def roulette_bet_callback(callback: CallbackQuery):
    await callback.answer()
    bet_type = callback.data.split(":")[1]
    
    # Ждём сумму ставки
    await callback.message.answer(
        f"🎲 Введи сумму ставки (цифру) в чате:\n"
        f"Например: <code>1000</code> или <code>all</code>",
        parse_mode="HTML"
    )
    
    # Сохраняем тип ставки
    async with aiosqlite.connect(DB) as db:
        await db.execute("UPDATE users SET vip_level = ? WHERE user_id = ?", 
                        (bet_type, callback.from_user.id))
        await db.commit()

# =========================================================
# БЛЭКДЖЕК
# =========================================================
@DP.callback_query(F.data == "blackjack")
async def blackjack_callback(callback: CallbackQuery):
    await callback.answer()
    await callback.message.answer(
        "🃏 <b>БЛЭКДЖЕК</b>\n\n"
        "Введи сумму ставки в чате:\n"
        "<code>1000</code> — поставить 1000\n"
        "<code>all</code> — поставить всё\n\n"
        "После этого начнётся игра против дилера!",
        parse_mode="HTML"
    )

# =========================================================
# СЛОТЫ
# =========================================================
@DP.callback_query(F.data == "slots")
async def slots_callback(callback: CallbackQuery):
    await callback.answer()
    await callback.message.answer(
        "🎰 <b>СЛОТЫ</b>\n\n"
        "Введи сумму ставки в чате:\n"
        "<code>100</code> — минимум\n"
        "<code>all</code> — поставить всё\n\n"
        "Символы: 🍒 🍋 🍊 🍇 🔔 💎 🎰",
        parse_mode="HTML"
    )

# =========================================================
# КОСТИ
# =========================================================
@DP.callback_query(F.data == "dice")
async def dice_callback(callback: CallbackQuery):
    await callback.answer()
    await callback.message.answer(
        "🎲 <b>КОСТИ</b>\n\n"
        "Введи сумму ставки и число (1-100):\n"
        "<code>1000 50</code> — поставить 1000 на число 50\n"
        "<code>all 75</code> — поставить всё на число 75\n\n"
        "Если выпадет твоё число → x50 выигрыш!",
        parse_mode="HTML"
    )

# =========================================================
# КЛАНЫ
# =========================================================
@DP.message(Command("clans"))
async def clans_command(message: Message):
    if not await require_subscription(message):
        return
    
    async with aiosqlite.connect(DB) as db:
        db.row_factory = aiosqlite.Row
        cur = await db.execute("SELECT * FROM clans")
        clans = await cur.fetchall()
    
    text = "🏆 <b>КЛАНЫ</b>\n\n"
    if not clans:
        text += "Кланов пока нет!\n\n"
    else:
        for clan in clans[:10]:
            text += f"🏛️ {clan['name']} (Ур.{clan['level']}) — 👥{clan['members_count']} участников\n"
    
    kb = InlineKeyboardBuilder()
    kb.button(text="📝 Создать клан", callback_data="create_clan")
    kb.button(text="⬅️ Назад", callback_data="menu")
    kb.adjust(1)
    
    await message.answer(text, reply_markup=kb.as_markup(), parse_mode="HTML")

@DP.callback_query(F.data == "clans")
async def clans_callback(callback: CallbackQuery):
    await callback.answer()
    await clans_command(callback.message)

# =========================================================
# ОБРАБОТКА СООБЩЕНИЙ (СТАВКИ)
# =========================================================
@DP.message(F.text)
async def handle_text(message: Message):
    if not await require_subscription(message):
        return
    
    user = await get_user(message.from_user.id)
    text = message.text.lower()
    
    # Проверяем, есть ли активная игра
    # Это упрощённая версия — для полной нужно больше логики
    
    if text == "all":
        amount = user['coins']
    else:
        try:
            amount = int(text)
        except:
            return
    
    if amount <= 0:
        await message.answer("❌ Ставка должна быть больше 0!")
        return
    
    if amount > user['coins']:
        await message.answer(f"❌ Недостаточно монет! Есть: <b>{user['coins']:,} 🪙</b>", parse_mode="HTML")
        return
    
    # Простая рулетка (для демонстрации)
    if message.text and message.text.isdigit():
        # Случайный выигрыш
        win = random.choice([0, 0, 0, 1, 1, 2, 2, 3, 5])
        win_amount = amount * win if win > 0 else 0
        
        if win_amount > 0:
            await update_coins(message.from_user.id, win_amount)
            await add_exp(message.from_user.id, win_amount // 10)
            await message.answer(
                f"🎉 <b>ВЫИГРЫШ!</b>\n\n"
                f"💰 Ставка: <b>{amount:,} 🪙</b>\n"
                f"💎 Выигрыш: <b>+{win_amount:,} 🪙</b>\n"
                f"⭐ Опыт: <b>+{win_amount // 10}</b>",
                parse_mode="HTML"
            )
        else:
            await update_coins(message.from_user.id, -amount)
            await message.answer(
                f"💀 <b>ПРОИГРЫШ!</b>\n\n"
                f"💰 Ставка: <b>{amount:,} 🪙</b>\n"
                f"💸 Потеряно: <b>-{amount:,} 🪙</b>",
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
