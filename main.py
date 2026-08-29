# main.py
# CRYPTO EMPIRE — ПОЛНАЯ РАБОЧАЯ ВЕРСИЯ
# С ОБЯЗАТЕЛЬНОЙ ПОДПИСКОЙ НА КАНАЛ

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

# =========================================================
# ПРОВЕРКА ПОДПИСКИ (ОБЯЗАТЕЛЬНАЯ!)
# =========================================================
async def check_subscription(user_id):
    """Проверяет, подписан ли пользователь на канал"""
    if not REQUIRED_CHANNEL:
        return True
    if (await get_user(user_id) or {}).get('username', '').lower() == OWNER.lower():
        return True
    try:
        member = await BOT.get_chat_member(REQUIRED_CHANNEL, user_id)
        return member.status in ("creator", "administrator", "member")
    except Exception as e:
        print(f"Ошибка проверки подписки: {e}")
        return False

def subscribe_keyboard():
    kb = InlineKeyboardBuilder()
    kb.button(text="📢 Подписаться на канал", url=CHANNEL_LINK)
    kb.button(text="✅ Проверить подписку", callback_data="check_sub")
    kb.adjust(1)
    return kb.as_markup()

async def require_subscription(message):
    """Проверяет подписку и если нет - блокирует"""
    if (message.from_user.username or "").lower() == OWNER.lower():
        return True
    if not REQUIRED_CHANNEL:
        return True
    
    is_subscribed = await check_subscription(message.from_user.id)
    if is_subscribed:
        return True
    
    await message.answer(
        "🔒 <b>ТРЕБУЕТСЯ ПОДПИСКА НА КАНАЛ</b>\n\n"
        "Чтобы играть в CRYPTO EMPIRE, нужно подписаться на наш канал:\n"
        f"{CHANNEL_LINK}\n\n"
        "1️⃣ Нажми кнопку «Подписаться на канал»\n"
        "2️⃣ Подпишись\n"
        "3️⃣ Нажми «Проверить подписку»\n\n"
        "⚠️ Без подписки бот НЕ РАБОТАЕТ!",
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

def donate_keyboard():
    kb = InlineKeyboardBuilder()
    for key, data in DONATE_PACKS.items():
        kb.button(text=f"{data['name']} — {data['stars']} ⭐", callback_data=f"donate:{key}")
    kb.button(text="⬅️ Назад", callback_data="menu")
    kb.adjust(1)
    return kb.as_markup()

# =========================================================
# КОМАНДА /start (С ПРОВЕРКОЙ ПОДПИСКИ)
# =========================================================
@DP.message(Command("start"))
async def start_command(message: Message):
    # Сначала проверяем подписку
    if not await require_subscription(message):
        return
    
    # Регистрируем пользователя
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
    
    is_subscribed = await check_subscription(callback.from_user.id)
    
    if is_subscribed:
        await callback.message.edit_text(
            "✅ <b>Подписка подтверждена!</b>\n\n"
            "Добро пожаловать в CRYPTO EMPIRE!\n"
            "Теперь ты можешь играть! 🚀",
            reply_markup=main_keyboard(),
            parse_mode="HTML"
        )
    else:
        await callback.message.answer(
            "❌ <b>ПОДПИСКА НЕ НАЙДЕНА</b>\n\n"
            "Ты ещё не подписался на канал!\n\n"
            "1️⃣ Нажми кнопку «Подписаться на канал»\n"
            "2️⃣ Подпишись\n"
            "3️⃣ Нажми «Проверить подписку»",
            reply_markup=subscribe_keyboard(),
            parse_mode="HTML"
        )

# =========================================================
# КОМАНДА /profile
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
# КОМАНДА /balance
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
# КОМАНДА /casino
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
# КОМАНДА /businesses
# =========================================================
@DP.message(Command("businesses"))
async def businesses_command(message: Message):
    if not await require_subscription(message):
        return
    
    user = await ensure_user(
        message.from_user.id,
        message.from_user.username or "",
        message.from_user.first_name or ""
    )
    
    businesses = await get_businesses(message.from_user.id)
    income = await get_total_income(message.from_user.id)
    
    text = "🏪 <b>ТВОИ БИЗНЕСЫ</b>\n\n"
    if not businesses:
        text += "У тебя пока нет бизнесов!\nКупи первый бизнес:\n\n"
    else:
        for biz in businesses:
            data = BUSINESSES.get(biz['biz_type'])
            if data:
                text += f"{data['name']} (Ур.{biz['level']}) — +{data['income'] * biz['level']:,} 🪙/час\n"
        text += f"\n📈 Общий доход: <b>+{income:,} 🪙/час</b>\n\n"
    
    text += "💰 Доступно для покупки:\n"
    
    kb = InlineKeyboardBuilder()
    for key, data in BUSINESSES.items():
        kb.button(text=f"Купить {data['name']} — {data['price']:,}🪙", callback_data=f"buy_biz:{key}")
    kb.button(text="💰 Собрать доход", callback_data="collect_income")
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
    
    businesses = await get_businesses(callback.from_user.id)
    if len(businesses) == 1:
        await check_achievement(callback.from_user.id, "first_business")
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
# РУЛЕТКА
# =========================================================
@DP.callback_query(F.data == "roulette")
async def roulette_callback(callback: CallbackQuery):
    await callback.answer()
    user = await get_user(callback.from_user.id)
    await callback.message.edit_text(
        f"🎲 <b>РУЛЕТКА</b>\n\n"
        f"💰 Баланс: <b>{user['coins']:,} 🪙</b>\n\n"
        f"Введи сумму ставки в чате:\n"
        f"<code>1000</code> — поставить 1000\n"
        f"<code>all</code> — поставить всё\n\n"
        f"После ставки выбери цвет!",
        reply_markup=None,
        parse_mode="HTML"
    )
    async with aiosqlite.connect(DB) as db:
        await db.execute("UPDATE users SET vip_level = 1 WHERE user_id = ?", (callback.from_user.id,))
        await db.commit()

# =========================================================
# СЛОТЫ
# =========================================================
@DP.callback_query(F.data == "slots")
async def slots_callback(callback: CallbackQuery):
    await callback.answer()
    user = await get_user(callback.from_user.id)
    
    symbols = ["🍒", "🍋", "🍊", "🍇", "🔔", "💎", "🎰"]
    result = [random.choice(symbols) for _ in range(3)]
    
    win = 0
    if result[0] == result[1] == result[2]:
        if result[0] == "🎰":
            win = 50
        elif result[0] == "💎":
            win = 20
        elif result[0] == "🔔":
            win = 10
        else:
            win = 5
    elif result[0] == result[1] or result[1] == result[2] or result[0] == result[2]:
        win = 2
    
    bet = 1000
    if user['coins'] < bet:
        await callback.message.answer(f"❌ Недостаточно монет! Нужно: <b>{bet:,} 🪙</b>", parse_mode="HTML")
        return
    
    if win > 0:
        win_amount = bet * win
        await update_coins(callback.from_user.id, win_amount - bet)
        await add_exp(callback.from_user.id, win_amount // 10)
        await callback.message.answer(
            f"🎰 <b>СЛОТЫ</b>\n\n"
            f"Результат: {' '.join(result)}\n"
            f"🎉 ВЫИГРЫШ! x{win}\n"
            f"💰 +{win_amount:,} 🪙",
            parse_mode="HTML"
        )
    else:
        await update_coins(callback.from_user.id, -bet)
        await callback.message.answer(
            f"🎰 <b>СЛОТЫ</b>\n\n"
            f"Результат: {' '.join(result)}\n"
            f"💀 ПРОИГРЫШ!\n"
            f"💸 -{bet:,} 🪙",
            parse_mode="HTML"
        )

# =========================================================
# КОСТИ
# =========================================================
@DP.callback_query(F.data == "dice")
async def dice_callback(callback: CallbackQuery):
    await callback.answer()
    user = await get_user(callback.from_user.id)
    
    bet = 1000
    number = random.randint(1, 100)
    guess = random.randint(1, 100)
    
    if user['coins'] < bet:
        await callback.message.answer(f"❌ Недостаточно монет! Нужно: <b>{bet:,} 🪙</b>", parse_mode="HTML")
        return
    
    if number == guess:
        win_amount = bet * 50
        await update_coins(callback.from_user.id, win_amount - bet)
        await callback.message.answer(
            f"🎲 <b>КОСТИ</b>\n\n"
            f"🎯 Выпало число: <b>{number}</b>\n"
            f"🎉 ТЫ УГАДАЛ! x50\n"
            f"💰 +{win_amount:,} 🪙",
            parse_mode="HTML"
        )
    else:
        await update_coins(callback.from_user.id, -bet)
        await callback.message.answer(
            f"🎲 <b>КОСТИ</b>\n\n"
            f"🎯 Выпало число: <b>{number}</b>\n"
            f"💀 ТЫ НЕ УГАДАЛ!\n"
            f"💸 -{bet:,} 🪙",
            parse_mode="HTML"
        )

# =========================================================
# БЛЭКДЖЕК
# =========================================================
@DP.callback_query(F.data == "blackjack")
async def blackjack_callback(callback: CallbackQuery):
    await callback.answer()
    user = await get_user(callback.from_user.id)
    
    bet = 1000
    if user['coins'] < bet:
        await callback.message.answer(f"❌ Недостаточно монет! Нужно: <b>{bet:,} 🪙</b>", parse_mode="HTML")
        return
    
    player_cards = [random.randint(1, 11), random.randint(1, 11)]
    dealer_cards = [random.randint(1, 11), random.randint(1, 11)]
    player_total = sum(player_cards)
    dealer_total = sum(dealer_cards)
    
    while player_total < 17:
        player_cards.append(random.randint(1, 11))
        player_total = sum(player_cards)
    
    while dealer_total < 17:
        dealer_cards.append(random.randint(1, 11))
        dealer_total = sum(dealer_cards)
    
    if player_total > 21:
        result = "💀 ПЕРЕБОР! Ты проиграл"
        await update_coins(callback.from_user.id, -bet)
    elif dealer_total > 21:
        result = "🎉 ДИЛЕР ПЕРЕБРАЛ! Ты выиграл"
        win_amount = bet * 2
        await update_coins(callback.from_user.id, win_amount - bet)
    elif player_total > dealer_total:
        result = f"🎉 ТЫ ВЫИГРАЛ! {player_total} vs {dealer_total}"
        win_amount = bet * 2
        await update_coins(callback.from_user.id, win_amount - bet)
    elif player_total < dealer_total:
        result = f"💀 ТЫ ПРОИГРАЛ! {player_total} vs {dealer_total}"
        await update_coins(callback.from_user.id, -bet)
    else:
        result = f"🤝 НИЧЬЯ! {player_total} vs {dealer_total}"
    
    await callback.message.answer(
        f"🃏 <b>БЛЭКДЖЕК</b>\n\n"
        f"👤 Твои карты: {player_cards} = <b>{player_total}</b>\n"
        f"🤖 Карты дилера: {dealer_cards} = <b>{dealer_total}</b>\n\n"
        f"{result}",
        parse_mode="HTML"
    )

# =========================================================
# КОМАНДА /daily
# =========================================================
@DP.message(Command("daily"))
async def daily_command(message: Message):
    if not await require_subscription(message):
        return
    
    user = await ensure_user(
        message.from_user.id,
        message.from_user.username or "",
        message.from_user.first_name or ""
    )
    
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    
    if user['daily_date'] == today:
        await message.answer("🎁 <b>DAILY УЖЕ ПОЛУЧЕН!</b>\n\nПриходи завтра!", parse_mode="HTML")
        return
    
    streak = user['daily_streak'] + 1
    reward = 500 + min(streak, 7) * 100
    
    await update_coins(message.from_user.id, reward)
    
    async with aiosqlite.connect(DB) as db:
        await db.execute("UPDATE users SET daily_date = ?, daily_streak = ? WHERE user_id = ?", 
                        (today, streak, message.from_user.id))
        await db.commit()
    
    await message.answer(
        f"🎁 <b>DAILY БОНУС ПОЛУЧЕН!</b>\n\n"
        f"🔥 Серия: <b>{streak}</b>\n"
        f"💰 Награда: <b>+{reward:,} 🪙</b>",
        parse_mode="HTML"
    )

@DP.callback_query(F.data == "daily")
async def daily_callback(callback: CallbackQuery):
    await callback.answer()
    await daily_command(callback.message)

# =========================================================
# КОМАНДА /investments
# =========================================================
@DP.message(Command("investments"))
async def investments_command(message: Message):
    if not await require_subscription(message):
        return
    
    user = await ensure_user(
        message.from_user.id,
        message.from_user.username or "",
        message.from_user.first_name or ""
    )
    
    kb = InlineKeyboardBuilder()
    kb.button(text="📈 Инвестировать 10 000", callback_data="invest:10000")
    kb.button(text="📈 Инвестировать 50 000", callback_data="invest:50000")
    kb.button(text="📈 Инвестировать 100 000", callback_data="invest:100000")
    kb.button(text="📈 Инвестировать 500 000", callback_data="invest:500000")
    kb.button(text="📈 Инвестировать 1 000 000", callback_data="invest:1000000")
    kb.button(text="⬅️ Назад", callback_data="menu")
    kb.adjust(1)
    
    await message.answer(
        f"📈 <b>ИНВЕСТИЦИИ</b>\n\n"
        f"💰 Баланс: <b>{user['coins']:,} 🪙</b>\n\n"
        f"Инвестируй монеты и получай прибыль!\n"
        f"📊 Доходность: <b>15-30%</b> в день\n"
        f"⏳ Срок: <b>24 часа</b>\n\n"
        f"Выбери сумму инвестиции:",
        reply_markup=kb.as_markup(),
        parse_mode="HTML"
    )

@DP.callback_query(F.data == "investments")
async def investments_callback(callback: CallbackQuery):
    await callback.answer()
    await investments_command(callback.message)

@DP.callback_query(F.data.startswith("invest:"))
async def invest_callback(callback: CallbackQuery):
    await callback.answer()
    amount = int(callback.data.split(":")[1])
    user = await get_user(callback.from_user.id)
    
    if user['coins'] < amount:
        await callback.message.answer(f"❌ Недостаточно монет! Нужно: <b>{amount:,} 🪙</b>", parse_mode="HTML")
        return
    
    await update_coins(callback.from_user.id, -amount)
    profit_percent = random.randint(15, 30)
    profit = int(amount * profit_percent / 100)
    
    async with aiosqlite.connect(DB) as db:
        await db.execute("""
            INSERT INTO investments (user_id, inv_type, amount, invested_at, profit)
            VALUES (?, ?, ?, ?, ?)
        """, (callback.from_user.id, f"Инвестиция {amount}", amount, int(time.time()), profit))
        await db.commit()
    
    await callback.message.answer(
        f"✅ <b>ИНВЕСТИЦИЯ СОЗДАНА!</b>\n\n"
        f"💰 Сумма: <b>{amount:,} 🪙</b>\n"
        f"📈 Доходность: <b>{profit_percent}%</b>\n"
        f"💎 Прибыль через 24 часа: <b>+{profit:,} 🪙</b>\n\n"
        f"⏳ Придёт автоматически через 24 часа!",
        parse_mode="HTML"
    )

# =========================================================
# КОМАНДА /achievements
# =========================================================
@DP.message(Command("achievements"))
async def achievements_command(message: Message):
    if not await require_subscription(message):
        return
    
    user = await ensure_user(
        message.from_user.id,
        message.from_user.username or "",
        message.from_user.first_name or ""
    )
    
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
# КОМАНДА /referral
# =========================================================
@DP.message(Command("referral"))
async def referral_command(message: Message):
    if not await require_subscription(message):
        return
    
    user = await ensure_user(
        message.from_user.id,
        message.from_user.username or "",
        message.from_user.first_name or ""
    )
    
    bot_info = await BOT.get_me()
    
    await message.answer(
        f"👥 <b>РЕФЕРАЛЬНАЯ СИСТЕМА</b>\n\n"
        f"💰 За каждого друга: <b>{REFERRAL_BONUS:,} 🪙</b>\n"
        f"🎁 Друг получит: <b>{REFERRAL_FRIEND_BONUS:,} 🪙</b>\n"
        f"👥 Приглашено: <b>{user['referral_count']}</b>\n\n"
        f"🔗 Твоя ссылка:\n"
        f"<code>https://t.me/{bot_info.username}?start=ref_{message.from_user.id}</code>",
        parse_mode="HTML",
        reply_markup=main_keyboard()
    )

@DP.callback_query(F.data == "referral")
async def referral_callback(callback: CallbackQuery):
    await callback.answer()
    await referral_command(callback.message)

# =========================================================
# КОМАНДА /top
# =========================================================
@DP.message(Command("top"))
async def top_command(message: Message):
    if not await require_subscription(message):
        return
    
    await ensure_user(
        message.from_user.id,
        message.from_user.username or "",
        message.from_user.first_name or ""
    )
    
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
# КОМАНДА /donate
# =========================================================
@DP.message(Command("donate"))
async def donate_command(message: Message):
    if not await require_subscription(message):
        return
    
    user = await ensure_user(
        message.from_user.id,
        message.from_user.username or "",
        message.from_user.first_name or ""
    )
    
    await message.answer(
        f"⭐ <b>ДОНАТ ЗА STARS</b>\n\n"
        f"💰 Твой баланс: <b>{user['coins']:,} 🪙</b>\n\n"
        f"Пополни баланс за Telegram Stars!\n"
        f"Выбери пак:",
        reply_markup=donate_keyboard(),
        parse_mode="HTML"
    )

@DP.callback_query(F.data == "donate")
async def donate_callback(callback: CallbackQuery):
    await callback.answer()
    await donate_command(callback.message)

@DP.callback_query(F.data.startswith("donate:"))
async def donate_pack_callback(callback: CallbackQuery):
    await callback.answer()
    pack_key = callback.data.split(":")[1]
    pack = DONATE_PACKS.get(pack_key)
    if not pack:
        return
    
    await BOT.send_invoice(
        chat_id=callback.from_user.id,
        title=f"💰 {pack['name']}",
        description=f"Получи {pack['coins']:,} 🪙 за {pack['stars']} ⭐",
        payload=f"donate:{pack_key}:{callback.from_user.id}",
        currency="XTR",
        prices=[LabeledPrice(label=pack['name'], amount=pack['stars'])]
    )

# =========================================================
# ОБРАБОТКА ОПЛАТЫ
# =========================================================
@DP.pre_checkout_query()
async def pre_checkout_query(query: PreCheckoutQuery):
    await query.answer(ok=True)

@DP.message(F.successful_payment)
async def successful_payment(message: Message):
    payment = message.successful_payment
    payload = payment.invoice_payload
    
    if payload.startswith("donate:"):
        parts = payload.split(":")
        pack_key = parts[1]
        user_id = int(parts[2])
        pack = DONATE_PACKS.get(pack_key)
        
        if pack:
            await update_coins(user_id, pack['coins'])
            
            async with aiosqlite.connect(DB) as db:
                await db.execute("""
                    INSERT INTO donations (user_id, pack_id, stars, coins, created_at)
                    VALUES (?, ?, ?, ?, ?)
                """, (user_id, pack_key, pack['stars'], pack['coins'], int(time.time())))
                await db.execute("UPDATE users SET total_donated = total_donated + ? WHERE user_id = ?", 
                                (pack['stars'], user_id))
                await db.commit()
            
            await message.answer(
                f"✅ <b>ПОПОЛНЕНИЕ УСПЕШНО!</b>\n\n"
                f"📦 Пак: {pack['name']}\n"
                f"💰 Получено: <b>+{pack['coins']:,} 🪙</b>\n"
                f"⭐ Потрачено Stars: <b>{pack['stars']}</b>\n\n"
                f"Спасибо за поддержку! 🙏",
                parse_mode="HTML"
            )

# =========================================================
# КОМАНДА /menu (НАЗАД В МЕНЮ)
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
# ОБРАБОТКА СТАВОК В РУЛЕТКУ
# =========================================================
@DP.message(F.text)
async def handle_roulette_bet(message: Message):
    if not await require_subscription(message):
        return
    
    user = await get_user(message.from_user.id)
    if not user:
        return
    
    # Проверяем, есть ли активная игра в рулетку
    async with aiosqlite.connect(DB) as db:
        cur = await db.execute("SELECT vip_level FROM users WHERE user_id = ?", (message.from_user.id,))
        row = await cur.fetchone()
        if not row or row[0] != 1:
            return
    
    text = message.text.lower()
    
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
        f"🎲 <b>РУЛЕТКА</b>\n\n"
        f"💰 Ставка: <b>{amount:,} 🪙</b>\n\n"
        f"Выбери ставку:",
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
    green = [0]
    
    result_num = random.choice(numbers)
    result_color = "green" if result_num in green else "red" if result_num in red else "black"
    
    win = False
    win_amount = 0
    
    if bet_type == "red" and result_color == "red":
        win = True
        win_amount = amount * 2
    elif bet_type == "black" and result_color == "black":
        win = True
        win_amount = amount * 2
    elif bet_type == "green" and result_color == "green":
        win = True
        win_amount = amount * 14
    elif bet_type == "even" and result_num % 2 == 0 and result_num != 0:
        win = True
        win_amount = amount * 2
    elif bet_type == "odd" and result_num % 2 == 1:
        win = True
        win_amount = amount * 2
    
    if win:
        await update_coins(callback.from_user.id, win_amount - amount)
        await add_exp(callback.from_user.id, win_amount // 10)
        
        emoji = "🔴" if result_color == "red" else "⚫" if result_color == "black" else "🟢"
        await callback.message.edit_text(
            f"🎲 <b>РУЛЕТКА</b>\n\n"
            f"🎯 Выпало: {emoji} <b>{result_num}</b>\n"
            f"🎉 ВЫИГРЫШ! x{2 if bet_type in ['red','black','even','odd'] else 14}\n"
            f"💰 +{win_amount:,} 🪙",
            parse_mode="HTML"
        )
    else:
        await update_coins(callback.from_user.id, -amount)
        
        emoji = "🔴" if result_color == "red" else "⚫" if result_color == "black" else "🟢"
        await callback.message.edit_text(
            f"🎲 <b>РУЛЕТКА</b>\n\n"
            f"🎯 Выпало: {emoji} <b>{result_num}</b>\n"
            f"💀 ПРОИГРЫШ!\n"
            f"💸 -{amount:,} 🪙",
            parse_mode="HTML"
        )
    
    async with aiosqlite.connect(DB) as db:
        await db.execute("UPDATE users SET vip_level = 0 WHERE user_id = ?", (callback.from_user.id,))
        await db.commit()

# =========================================================
# АДМИНКА
# =========================================================
@DP.message(Command("stats"))
async def stats_command(message: Message):
    if (message.from_user.username or "").lower() != OWNER.lower():
        await message.answer("❌ Только для владельца!")
        return
    
    async with aiosqlite.connect(DB) as db:
        cur = await db.execute("SELECT COUNT(*) FROM users")
        users = (await cur.fetchone())[0]
        
        cur = await db.execute("SELECT SUM(coins) FROM users")
        total_coins = (await cur.fetchone())[0] or 0
        
        cur = await db.execute("SELECT COUNT(*) FROM businesses")
        businesses = (await cur.fetchone())[0]
    
    await message.answer(
        f"📊 <b>СТАТИСТИКА</b>\n\n"
        f"👥 Пользователей: <b>{users}</b>\n"
        f"🪙 Монет в системе: <b>{total_coins:,}</b>\n"
        f"🏪 Всего бизнесов: <b>{businesses}</b>",
        parse_mode="HTML"
    )

@DP.message(Command("give"))
async def give_command(message: Message):
    if (message.from_user.username or "").lower() != OWNER.lower():
        await message.answer("❌ Только для владельца!")
        return
    
    parts = message.text.split()
    if len(parts) != 3:
        await message.answer("Использование: /give USER_ID КОЛИЧЕСТВО")
        return
    
    try:
        user_id = int(parts[1])
        amount = int(parts[2])
    except:
        await message.answer("❌ Неверные данные!")
        return
    
    await update_coins(user_id, amount)
    await message.answer(f"✅ Выдано <b>{amount:,} 🪙</b> пользователю <code>{user_id}</code>", parse_mode="HTML")

# =========================================================
# ЗАПУСК
# =========================================================
async def main():
    await init_db()
    print("=" * 60)
    print("💎 CRYPTO EMPIRE BOT")
    print(f"👑 OWNER: @{OWNER}")
    print(f"📢 КАНАЛ: {CHANNEL_LINK}")
    print("🔒 ОБЯЗАТЕЛЬНАЯ ПОДПИСКА: ВКЛЮЧЕНА")
    print("⭐ ДОНАТЫ ЗА STARS: ВКЛЮЧЕНЫ")
    print("=" * 60)
    await DP.start_polling(BOT)

if __name__ == "__main__":
    asyncio.run(main())
