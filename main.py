# main.py
# FOOTBALL DROP — обновлённая версия
# Изменения:
# - DROP каждые 10 минут
# - новый ивент "⚡ Minute Drop" = DROP каждые 1 минуту
# - /help со всеми командами
# - исправлена кнопка «Коллекция»
# - @foqlu может создавать промокоды
# - добавлена /owner-панель для @foqlu
# - сохранены ивенты в SQLite и уведомления пользователей
# - добавлена команда /players для просмотра всех игроков
# - добавлена система обмена игроками /trade

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
DB = "football_drop.db"

OWNER = "foqlu"
REQUIRED_CHANNEL = os.getenv("REQUIRED_CHANNEL", "")
CHANNEL_LINK = "https://t.me/+MHTPcaFy2j5lOWMy"

# Обычный DROP теперь раз в 10 минут
DROP_COOLDOWN = 10 * 60

LUCKY_COST = 15
LUCKY_HOURS = 24

RARITIES = {
    "Common": 68.0,
    "Rare": 22.0,
    "Super Rare": 7.0,
    "Epic": 2.5,
    "Legendary": 0.45,
    "Icon": 0.049,
    "Ultimate": 0.001,
}

RARITY_EMOJI = {
    "Common": "⚪",
    "Rare": "🟢",
    "Super Rare": "🔵",
    "Epic": "🟣",
    "Legendary": "🟡",
    "Icon": "🔴",
    "Ultimate": "🌈",
}

RARITY_ORDER = [
    "Common", "Rare", "Super Rare", "Epic",
    "Legendary", "Icon", "Ultimate"
]

# =========================================================
# PLAYERS — РАСШИРЕННЫЙ СПИСОК (100+ игроков)
# =========================================================
PLAYERS = [
    # ===== COMMON (обычные) =====
    ("Фран Гарсия", "🇪🇸", "LB", 78, "Common", 5000),
    ("Браим Диас", "🇪🇸", "RW", 79, "Common", 6000),
    ("Арда Гюлер", "🇹🇷", "CAM", 79, "Common", 6500),
    ("Эндрик", "🇧🇷", "ST", 78, "Common", 5000),
    ("Александр Исак", "🇸🇪", "ST", 80, "Common", 7000),
    ("Джереми Доку", "🇧🇪", "RW", 80, "Common", 7200),
    ("Жоау Педро", "🇧🇷", "ST", 79, "Common", 6200),
    ("Майкл Олисе", "🇫🇷", "RW", 79, "Common", 6400),
    ("Хвича Кварацхелия", "🇬🇪", "LW", 80, "Common", 7500),
    ("Рандаль Коло Муани", "🇫🇷", "ST", 79, "Common", 6300),
    ("Рафаэл Леау", "🇵🇹", "LW", 79, "Common", 6600),
    ("Бенджамин Сеско", "🇸🇮", "ST", 78, "Common", 5400),
    ("Алехандро Гарначо", "🇦🇷", "LW", 79, "Common", 6100),
    ("Конор Брэдли", "🏴", "RB", 78, "Common", 5300),
    ("Яррад Брантуэйт", "🏴", "CB", 78, "Common", 5100),
    ("Гонсалу Рамуш", "🇵🇹", "ST", 79, "Common", 6400),
    ("Жоан Феликс", "🇵🇹", "CAM", 79, "Common", 6700),
    ("Ансу Фати", "🇪🇸", "LW", 78, "Common", 5500),
    ("Маркос Леон", "🇪🇸", "RB", 78, "Common", 5100),
    ("Кристоф Баумгартнер", "🇦🇹", "CM", 79, "Common", 6300),
    ("Томас Сулек", "🇨🇿", "CB", 78, "Common", 5400),
    ("Ян Кучта", "🇨🇿", "ST", 78, "Common", 5200),
    ("Матиас Йенсен", "🇩🇰", "CM", 79, "Common", 6100),
    ("Андреас Сков Ольсен", "🇩🇰", "LW", 78, "Common", 5500),
    ("Уго Экитике", "🇫🇷", "ST", 78, "Common", 5300),
    ("Арно Калимуэндо", "🇫🇷", "ST", 78, "Common", 5400),
    ("Брадли Баркола", "🇫🇷", "LW", 78, "Common", 5600),
    ("Матис Тель", "🇫🇷", "ST", 78, "Common", 5200),
    ("Янник Синнер", "🇮🇹", "RW", 78, "Common", 5200),
    ("Серхио Гомес", "🇪🇸", "LB", 78, "Common", 5100),
    ("Пабло Торре", "🇪🇸", "CM", 78, "Common", 5300),
    ("Марк Гиу", "🇪🇸", "ST", 78, "Common", 5200),

    # ===== RARE (редкие) =====
    ("Кобби Майну", "🏴", "CM", 81, "Rare", 10000),
    ("Кристиан Пулишич", "🇺🇸", "LW", 82, "Rare", 12000),
    ("Нико Уильямс", "🇪🇸", "LW", 83, "Rare", 15000),
    ("Габриэл Мартинелли", "🇧🇷", "LW", 82, "Rare", 13000),
    ("Букайо Сака", "🏴", "RW", 83, "Rare", 16000),
    ("Деклан Райс", "🏴", "CDM", 83, "Rare", 15500),
    ("Федерико Вальверде", "🇺🇾", "CM", 83, "Rare", 14500),
    ("Эдуардо Камавинга", "🇫🇷", "CM", 82, "Rare", 12500),
    ("Орельен Тчуамени", "🇫🇷", "CDM", 82, "Rare", 12800),
    ("Хулиан Альварес", "🇦🇷", "ST", 82, "Rare", 13500),
    ("Дарвин Нуньес", "🇺🇾", "ST", 82, "Rare", 13200),
    ("Луис Диас", "🇨🇴", "LW", 82, "Rare", 14000),
    ("Бруно Гимараэс", "🇧🇷", "CM", 83, "Rare", 15200),
    ("Антони Гордон", "🏴", "RW", 82, "Rare", 13800),
    ("Матео Гендузи", "🇫🇷", "CM", 81, "Rare", 11000),
    ("Бреннан Джонсон", "🏴", "RW", 81, "Rare", 10800),
    ("Конор Галлахер", "🏴", "CM", 81, "Rare", 11200),
    ("Мохаммед Кудус", "🇬🇭", "CAM", 81, "Rare", 11800),
    ("Якуб Кивиор", "🇵🇱", "CB", 81, "Rare", 10500),
    ("Юссеф Эн-Несири", "🇲🇦", "ST", 82, "Rare", 12500),
    ("Исмаил Беннасер", "🇩🇿", "CM", 81, "Rare", 11500),
    ("Алексей Миранчук", "🇷🇺", "CAM", 81, "Rare", 10800),
    ("Артём Довбик", "🇺🇦", "ST", 82, "Rare", 12200),
    ("Виктор Цыганков", "🇺🇦", "RW", 81, "Rare", 11200),
    ("Александр Зинченко", "🇺🇦", "LB", 81, "Rare", 11500),
    ("Илья Забарный", "🇺🇦", "CB", 81, "Rare", 11000),
    ("Хорхе Вальдес", "🇵🇾", "CB", 81, "Rare", 10800),
    ("Энцо Фернандес", "🇦🇷", "CM", 82, "Rare", 13000),
    ("Алексис Макаллистер", "🇦🇷", "CM", 82, "Rare", 12800),
    ("Анхель Ди Мария", "🇦🇷", "RW", 82, "Rare", 12500),

    # ===== SUPER RARE (супер редкие) =====
    ("Педри", "🇪🇸", "CM", 86, "Super Rare", 25000),
    ("Гави", "🇪🇸", "CM", 85, "Super Rare", 23000),
    ("Коул Палмер", "🏴", "CAM", 87, "Super Rare", 30000),
    ("Джуд Беллингем", "🏴", "CAM", 86, "Super Rare", 28000),
    ("Джек Грилиш", "🏴", "LW", 85, "Super Rare", 24000),
    ("Маркус Рашфорд", "🏴", "LW", 85, "Super Rare", 24500),
    ("Филип Фоден", "🏴", "RW", 86, "Super Rare", 27000),
    ("Мейсон Маунт", "🏴", "CAM", 85, "Super Rare", 23500),
    ("Хаверц Кай", "🇩🇪", "ST", 85, "Super Rare", 25000),
    ("Джамал Мусиала", "🇩🇪", "CAM", 86, "Super Rare", 27500),
    ("Флориан Виртц", "🇩🇪", "CAM", 85, "Super Rare", 24000),
    ("Жереми Фримпонг", "🇳🇱", "RB", 85, "Super Rare", 23000),
    ("Коди Гакпо", "🇳🇱", "LW", 84, "Super Rare", 21000),
    ("Маттейс де Лигт", "🇳🇱", "CB", 85, "Super Rare", 24500),
    ("Андре Онана", "🇨🇲", "GK", 85, "Super Rare", 22000),
    ("Уго Льорис", "🇫🇷", "GK", 84, "Super Rare", 20000),
    ("Антуан Гризманн", "🇫🇷", "ST", 86, "Super Rare", 26000),
    ("Кингсли Коман", "🇫🇷", "LW", 85, "Super Rare", 23500),
    ("Усман Дембеле", "🇫🇷", "RW", 85, "Super Rare", 24000),
    ("Жюль Кунде", "🇫🇷", "CB", 84, "Super Rare", 21000),

    # ===== EPIC (эпические) =====
    ("Ламин Ямаль", "🇪🇸", "RW", 89, "Epic", 45000),
    ("Винисиус Жуниор", "🇧🇷", "LW", 91, "Epic", 60000),
    ("Родри", "🇪🇸", "CDM", 90, "Epic", 50000),
    ("Эрлинг Холанд", "🇳🇴", "ST", 91, "Epic", 55000),
    ("Килиан Мбаппе", "🇫🇷", "ST", 92, "Epic", 65000),
    ("Лука Модрич", "🇭🇷", "CM", 89, "Epic", 45000),
    ("Тони Кроос", "🇩🇪", "CM", 89, "Epic", 42000),
    ("Неймар", "🇧🇷", "LW", 89, "Epic", 48000),
    ("Трент Александер-Арнольд", "🏴", "RB", 88, "Epic", 40000),
    ("Эндрю Робертсон", "🏴", "LB", 88, "Epic", 38000),
    ("Алиссон Бекер", "🇧🇷", "GK", 89, "Epic", 43000),
    ("Ян Облак", "🇸🇮", "GK", 88, "Epic", 39000),
    ("Рубен Диаш", "🇵🇹", "CB", 88, "Epic", 41000),
    ("Хосе Мария Хименес", "🇺🇾", "CB", 88, "Epic", 39500),
    ("Маркос Льоренте", "🇪🇸", "CM", 88, "Epic", 38500),

    # ===== LEGENDARY (легендарные) =====
    ("Мохамед Салах", "🇪🇬", "RW", 90, "Legendary", 70000),
    ("Садио Мане", "🇸🇳", "LW", 89, "Legendary", 55000),
    ("Карим Бензема", "🇫🇷", "ST", 91, "Legendary", 75000),
    ("Кевин Де Брюйне", "🇧🇪", "CM", 91, "Legendary", 80000),
    ("Эден Азар", "🇧🇪", "LW", 89, "Legendary", 60000),
    ("Роберт Левандовски", "🇵🇱", "ST", 90, "Legendary", 72000),
    ("Гарри Кейн", "🏴", "ST", 90, "Legendary", 70000),
    ("Сон Хын Мин", "🇰🇷", "LW", 89, "Legendary", 58000),
    ("Сака", "🇯🇵", "CAM", 89, "Legendary", 55000),
    ("Мануэль Нойер", "🇩🇪", "GK", 90, "Legendary", 65000),
    ("Тибо Куртуа", "🇧🇪", "GK", 90, "Legendary", 68000),
    ("Вирджил Ван Дейк", "🇳🇱", "CB", 90, "Legendary", 72000),
    ("Серхио Рамос", "🇪🇸", "CB", 89, "Legendary", 62000),
    ("Джорджио Кьеллини", "🇮🇹", "CB", 89, "Legendary", 59000),

    # ===== ICON (иконы) =====
    ("Лионель Месси", "🇦🇷", "RW", 95, "Icon", 150000),
    ("Криштиану Роналду", "🇵🇹", "ST", 94, "Icon", 140000),
    ("Роналдиньо", "🇧🇷", "LW", 96, "Icon", 220000),
    ("Пеле", "🇧🇷", "ST", 98, "Icon", 350000),
    ("Зинедин Зидан", "🇫🇷", "CAM", 95, "Icon", 200000),
    ("Андрей Шевченко", "🇺🇦", "ST", 93, "Icon", 120000),
    ("Паоло Мальдини", "🇮🇹", "CB", 94, "Icon", 150000),
    ("Франко Барези", "🇮🇹", "CB", 93, "Icon", 130000),
    ("Мишель Платини", "🇫🇷", "CAM", 94, "Icon", 160000),
    ("Йохан Кройф", "🇳🇱", "LW", 96, "Icon", 250000),
    ("Гарринча", "🇧🇷", "RW", 93, "Icon", 140000),
    ("Бобби Чарльтон", "🏴", "CM", 93, "Icon", 135000),

    # ===== ULTIMATE =====
    ("Месси Ultimate", "🇦🇷", "RW", 99, "Ultimate", 500000),
    ("Роналду Ultimate", "🇵🇹", "ST", 99, "Ultimate", 500000),
    ("Пеле Ultimate", "🇧🇷", "ST", 99, "Ultimate", 500000),
    ("Марадона Ultimate", "🇦🇷", "CAM", 99, "Ultimate", 500000),
    ("Кройф Ultimate", "🇳🇱", "LW", 99, "Ultimate", 500000),
]

STAR_PACKS = {
    "basic": (10, 1, "🥉 Basic Pack"),
    "pro": (25, 3, "🥈 Pro Pack"),
    "elite": (50, 6, "🥇 Elite Pack"),
    "legend": (100, 12, "💎 Legendary Pack"),
    "icon": (250, 20, "🔥 Icon Pack"),
    "ultimate": (500, 35, "🌈 Ultimate Pack"),
}

COIN_PACKS = {
    "c1": (15000, 1, "📦 Bronze Coin Pack"),
    "c2": (40000, 3, "📦 Silver Coin Pack"),
    "c3": (90000, 7, "📦 Gold Coin Pack"),
    "c4": (200000, 18, "💎 Diamond Coin Pack"),
}

# EVENTS
EVENTS = {
    "lucky": {
        "name": "🍀 Lucky Drop",
        "description": "Повышенный шанс получить редкую карту.",
        "type": "rarity",
        "value": 2,
    },
    "super": {
        "name": "🔥 Super Drop",
        "description": "x3 к шансам редких карт.",
        "type": "rarity",
        "value": 3,
    },
    "mega": {
        "name": "💎 Mega Drop",
        "description": "x5 к шансам редких карт.",
        "type": "rarity",
        "value": 5,
    },
    "ultimate": {
        "name": "🌈 Ultimate Hour",
        "description": "Сильно повышенный шанс Icon и Ultimate.",
        "type": "ultimate",
        "value": 8,
    },
    "coins": {
        "name": "🪙 Coin Rain",
        "description": "В 3 раза больше монет за DROP.",
        "type": "coins",
        "value": 3,
    },
    "double": {
        "name": "🎯 Double Drop",
        "description": "Каждый DROP даёт 2 карты.",
        "type": "double",
        "value": 2,
    },
    "minute": {
        "name": "⚡ Minute Drop",
        "description": "DROP можно открывать каждую 1 минуту.",
        "type": "cooldown",
        "value": 60,
    },
}

async def init_db():
    async with aiosqlite.connect(DB) as db:
        await db.execute("""
        CREATE TABLE IF NOT EXISTS users(
            user_id INTEGER PRIMARY KEY,
            username TEXT DEFAULT '',
            first_name TEXT DEFAULT '',
            coins INTEGER DEFAULT 0,
            stars INTEGER DEFAULT 0,
            last_drop INTEGER DEFAULT 0,
            daily_date TEXT DEFAULT '',
            daily_streak INTEGER DEFAULT 0,
            wins INTEGER DEFAULT 0,
            losses INTEGER DEFAULT 0,
            lucky_until INTEGER DEFAULT 0,
            banned INTEGER DEFAULT 0
        )""")

        await db.execute("""
        CREATE TABLE IF NOT EXISTS cards(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            name TEXT NOT NULL,
            nation TEXT NOT NULL,
            position TEXT NOT NULL,
            rating INTEGER NOT NULL,
            rarity TEXT NOT NULL,
            price INTEGER NOT NULL,
            created_at INTEGER DEFAULT 0
        )""")

        await db.execute("""
        CREATE TABLE IF NOT EXISTS market(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            seller_id INTEGER NOT NULL,
            card_id INTEGER NOT NULL,
            price INTEGER NOT NULL
        )""")

        await db.execute("""
        CREATE TABLE IF NOT EXISTS payments(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            product TEXT NOT NULL,
            stars INTEGER NOT NULL,
            created INTEGER NOT NULL
        )""")

        await db.execute("""
        CREATE TABLE IF NOT EXISTS missions(
            user_id INTEGER PRIMARY KEY,
            drops INTEGER DEFAULT 0,
            cards INTEGER DEFAULT 0,
            claimed INTEGER DEFAULT 0
        )""")

        await db.execute("""
        CREATE TABLE IF NOT EXISTS promo_codes(
            code TEXT PRIMARY KEY,
            coins INTEGER DEFAULT 0,
            stars INTEGER DEFAULT 0,
            activations INTEGER NOT NULL,
            used INTEGER DEFAULT 0,
            created INTEGER NOT NULL
        )""")

        await db.execute("""
        CREATE TABLE IF NOT EXISTS promo_uses(
            code TEXT NOT NULL,
            user_id INTEGER NOT NULL,
            PRIMARY KEY(code,user_id)
        )""")

        await db.execute("""
        CREATE TABLE IF NOT EXISTS lucky_charms(
            user_id INTEGER PRIMARY KEY,
            expires_at INTEGER NOT NULL
        )""")

        await db.execute("""
        CREATE TABLE IF NOT EXISTS active_event(
            id INTEGER PRIMARY KEY CHECK(id = 1),
            event_key TEXT NOT NULL,
            expires_at INTEGER NOT NULL,
            active INTEGER DEFAULT 1
        )""")

        # Таблица для торгов (обменов)
        await db.execute("""
        CREATE TABLE IF NOT EXISTS trades(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sender_id INTEGER NOT NULL,
            receiver_id INTEGER NOT NULL,
            sender_card_id INTEGER NOT NULL,
            receiver_card_id INTEGER NOT NULL,
            status TEXT DEFAULT 'pending',
            created_at INTEGER NOT NULL
        )""")

        await db.commit()

async def register(user):
    async with aiosqlite.connect(DB) as db:
        await db.execute("""
            INSERT OR IGNORE INTO users(user_id,username,first_name)
            VALUES(?,?,?)
        """, (user.id, user.username or "", user.first_name or ""))

        await db.execute("""
            UPDATE users SET username=?,first_name=? WHERE user_id=?
        """, (user.username or "", user.first_name or "", user.id))

        await db.execute("""
            INSERT OR IGNORE INTO missions(user_id) VALUES(?)
        """, (user.id,))
        await db.commit()

async def get_user(user_id):
    async with aiosqlite.connect(DB) as db:
        db.row_factory = aiosqlite.Row
        cur = await db.execute(
            "SELECT * FROM users WHERE user_id=?", (user_id,))
        return await cur.fetchone()

async def count_cards(user_id):
    async with aiosqlite.connect(DB) as db:
        cur = await db.execute(
            "SELECT COUNT(*) FROM cards WHERE user_id=?", (user_id,))
        return (await cur.fetchone())[0]

async def add_coins(user_id, amount):
    async with aiosqlite.connect(DB) as db:
        await db.execute(
            "UPDATE users SET coins=coins+? WHERE user_id=?",
            (amount, user_id))
        await db.commit()

async def spend_coins(user_id, amount):
    async with aiosqlite.connect(DB) as db:
        cur = await db.execute(
            "SELECT coins,banned FROM users WHERE user_id=?", (user_id,))
        row = await cur.fetchone()
        if not row or row[1] or row[0] < amount:
            return False
        await db.execute(
            "UPDATE users SET coins=coins-? WHERE user_id=?",
            (amount, user_id))
        await db.commit()
        return True

async def add_card(user_id, player):
    name, nation, position, rating, rarity, price = player
    async with aiosqlite.connect(DB) as db:
        await db.execute("""
            INSERT INTO cards
            (user_id,name,nation,position,rating,rarity,price,created_at)
            VALUES(?,?,?,?,?,?,?,?)
        """, (user_id,name,nation,position,rating,rarity,price,int(time.time())))
        await db.commit()
        return True

async def mission_update(user_id, field, amount=1):
    if field not in ("drops", "cards"):
        return
    async with aiosqlite.connect(DB) as db:
        await db.execute(
            f"UPDATE missions SET {field}={field}+? WHERE user_id=?",
            (amount,user_id))
        await db.commit()

def is_owner(user):
    return (user.username or "").lower() == OWNER.lower()

async def check_access(user_id):
    if not REQUIRED_CHANNEL:
        return True
    try:
        member = await BOT.get_chat_member(REQUIRED_CHANNEL,user_id)
        return member.status in ("creator","administrator","member")
    except Exception:
        return False

def subscribe_keyboard():
    kb = InlineKeyboardBuilder()
    kb.button(text="📢 Подписаться на канал",url=CHANNEL_LINK)
    kb.button(text="✅ Проверить подписку",callback_data="check_sub")
    kb.adjust(1)
    return kb.as_markup()

async def require_subscription(message):
    if is_owner(message.from_user):
        return True
    if await check_access(message.from_user.id):
        return True
    await message.answer(
        "🔒 <b>СНАЧАЛА ПОДПИШИСЬ НА КАНАЛ</b>\n\n"
        "После подписки нажми «Проверить подписку».",
        reply_markup=subscribe_keyboard(),parse_mode="HTML")
    return False

async def get_active_event():
    now = int(time.time())
    async with aiosqlite.connect(DB) as db:
        db.row_factory = aiosqlite.Row
        cur = await db.execute(
            "SELECT * FROM active_event WHERE id=1 AND active=1")
        row = await cur.fetchone()
        if not row:
            return None
        if row["expires_at"] and row["expires_at"] <= now:
            await db.execute("UPDATE active_event SET active=0 WHERE id=1")
            await db.commit()
            return None
        return row

async def start_event(event_key, minutes):
    if event_key not in EVENTS:
        return False
    expires_at = 0 if minutes == 0 else int(time.time()) + minutes * 60
    async with aiosqlite.connect(DB) as db:
        await db.execute("""
            INSERT INTO active_event(id,event_key,expires_at,active)
            VALUES(1,?,?,1)
            ON CONFLICT(id) DO UPDATE SET
            event_key=excluded.event_key,
            expires_at=excluded.expires_at,
            active=1
        """, (event_key,expires_at))
        await db.commit()
    return True

async def stop_event():
    async with aiosqlite.connect(DB) as db:
        await db.execute("UPDATE active_event SET active=0 WHERE id=1")
        await db.commit()

async def notify_event_started(event_key, minutes):
    event = EVENTS[event_key]
    duration = "♾ навсегда" if minutes == 0 else f"⏳ {minutes} мин."
    async with aiosqlite.connect(DB) as db:
        cur = await db.execute("SELECT user_id FROM users WHERE banned=0")
        users = await cur.fetchall()

    text = (
        "🚨 <b>НОВЫЙ ИВЕНТ!</b>\n\n"
        f"{event['name']}\n"
        f"📋 {event['description']}\n"
        f"{duration}\n\n"
        "⚽ Заходи и открывай DROP!"
    )

    for row in users:
        try:
            await BOT.send_message(row[0],text,parse_mode="HTML")
            await asyncio.sleep(0.03)
        except Exception:
            pass

def event_keyboard():
    kb = InlineKeyboardBuilder()
    for key,event in EVENTS.items():
        kb.button(text=event["name"],callback_data=f"event_select:{key}")
    kb.button(text="⛔ Остановить текущий ивент",callback_data="event_stop")
    kb.adjust(1)
    return kb.as_markup()

def event_duration_keyboard(event_key):
    kb = InlineKeyboardBuilder()
    options = [
        ("⏱ 1 минута",1),
        ("⏱ 10 минут",10),
        ("⏱ 1 час",60),
        ("⏱ 3 часа",180),
        ("♾ Навсегда",0),
    ]
    for text,minutes in options:
        kb.button(text=text,callback_data=f"event_start:{event_key}:{minutes}")
    kb.button(text="⬅️ Назад",callback_data="event_menu")
    kb.adjust(1)
    return kb.as_markup()

def get_event_multiplier_weights(multiplier):
    weights = []
    for rarity in RARITIES:
        weight = RARITIES[rarity]
        if rarity != "Common":
            weight *= multiplier
        weights.append(weight)
    return weights

def choose_rarity(user=None,event=None):
    names = list(RARITIES.keys())
    weights = list(RARITIES.values())

    if user and user["lucky_until"] > int(time.time()):
        weights = [
            weights[i] * (1 if names[i] == "Common" else 3)
            for i in range(len(names))
        ]

    if event:
        data = EVENTS.get(event["event_key"])
        if data:
            if data["type"] == "rarity":
                weights = get_event_multiplier_weights(data["value"])
            elif data["type"] == "ultimate":
                for i,rarity in enumerate(names):
                    if rarity == "Common":
                        weights[i] *= 0.7
                    elif rarity == "Rare":
                        weights[i] *= 0.7
                    elif rarity == "Super Rare":
                        weights[i] *= 1.2
                    elif rarity == "Epic":
                        weights[i] *= 3
                    elif rarity == "Legendary":
                        weights[i] *= 5
                    elif rarity == "Icon":
                        weights[i] *= 8
                    elif rarity == "Ultimate":
                        weights[i] *= 12

    return random.choices(names,weights=weights,k=1)[0]

def random_player(user=None,event=None):
    rarity = choose_rarity(user,event)
    pool = [p for p in PLAYERS if p[4] == rarity]
    return random.choice(pool or PLAYERS)

def get_drop_cooldown(event):
    if event and event["event_key"] == "minute":
        return 60
    return DROP_COOLDOWN

def main_keyboard(user=None):
    kb = InlineKeyboardBuilder()
    buttons = [
        ("🃏 DROP","drop"),
        ("📚 Коллекция","collection"),
        ("👤 Профиль","profile"),
        ("🛒 Магазин","shop"),
        ("🏪 Рынок","market"),
        ("🎁 Daily","daily"),
        ("🎯 Задания","missions"),
        ("🏆 Рейтинг","top"),
        ("📦 Паки за 🪙","coinpacks"),
        ("⭐ Паки за Stars","packs"),
        ("🎟️ Промокод","promo"),
        ("🍀 Lucky Charm","lucky"),
        ("🔄 Обмен","trade_menu"),
        ("📋 Все игроки","players"),
    ]
    if user and is_owner(user):
        buttons.append(("👑 Owner","owner"))
    for text,data in buttons:
        kb.button(text=text,callback_data=data)
    kb.adjust(2)
    return kb.as_markup()

async def do_drop(message):
    await register(message.from_user)
    if not await require_subscription(message):
        return

    user = await get_user(message.from_user.id)
    if not user:
        return
    if user["banned"] and not is_owner(message.from_user):
        await message.answer("🚫 Вы заблокированы.")
        return

    event = await get_active_event()
    now = int(time.time())

    if not is_owner(message.from_user):
        cooldown = get_drop_cooldown(event)
        if user["last_drop"]:
            remaining = cooldown - (now - user["last_drop"])
            if remaining > 0:
                minutes = remaining // 60
                seconds = remaining % 60
                await message.answer(
                    "⏳ <b>DROP ЕЩЁ НЕ ДОСТУПЕН</b>\n\n"
                    f"Осталось: <b>{minutes}м {seconds}с</b>",
                    parse_mode="HTML")
                return

    async with aiosqlite.connect(DB) as db:
        await db.execute(
            "UPDATE users SET last_drop=? WHERE user_id=?",
            (now,message.from_user.id))
        await db.commit()

    coins = random.randint(100,400)
    if event and EVENTS[event["event_key"]]["type"] == "coins":
        coins *= EVENTS[event["event_key"]]["value"]

    await add_coins(message.from_user.id,coins)
    await mission_update(message.from_user.id,"drops")

    await message.answer("📦 <b>ПАК ОТКРЫВАЕТСЯ...</b>",parse_mode="HTML")
    await asyncio.sleep(0.7)

    amount = 2 if (
        event and EVENTS[event["event_key"]]["type"] == "double"
    ) else 1

    pulled = []
    for _ in range(amount):
        user = await get_user(message.from_user.id)
        player = random_player(user,event)
        await add_card(message.from_user.id,player)
        await mission_update(message.from_user.id,"cards")
        pulled.append(player)

    text = "⚽ <b>FOOTBALL DROP!</b>\n\n"
    if event:
        text += f"🚨 Ивент: <b>{EVENTS[event['event_key']]['name']}</b>\n\n"

    for index,player in enumerate(pulled,1):
        name,nation,pos,rating,rarity,price = player
        if amount > 1:
            text += f"🃏 <b>КАРТА {index}</b>\n"
        text += (
            f"{RARITY_EMOJI.get(rarity,'⚪')} <b>{rarity.upper()}</b>\n"
            f"{nation} <b>{html.escape(name)}</b>\n"
            f"⚡ Позиция: <b>{pos}</b>\n"
            f"⭐ Рейтинг: <b>{rating}</b>\n"
            f"💰 Цена: <b>€{price:,}</b>\n\n"
        )

    text += f"🪙 Бонус: <b>+{coins}</b>"

    kb = InlineKeyboardBuilder()
    kb.button(text="📚 Коллекция",callback_data="collection")
    kb.button(text="🏪 Продать карту боту",callback_data="market")
    kb.adjust(1)

    await message.answer(text,reply_markup=kb.as_markup(),parse_mode="HTML")

# =========================================================
# КОМАНДА /players — показать всех игроков
# =========================================================
@DP.message(Command("players"))
async def players_command(message: Message):
    await register(message.from_user)
    if not await require_subscription(message):
        return
    
    # Сортировка по рейтингу (от высокого к низкому)
    sorted_players = sorted(PLAYERS, key=lambda x: x[3], reverse=True)
    
    text = "📋 <b>ВСЕ ИГРОКИ В ИГРЕ</b>\n\n"
    text += f"👥 Всего игроков: <b>{len(PLAYERS)}</b>\n\n"
    
    # Группировка по редкости
    for rarity in RARITY_ORDER:
        players_in_rarity = [p for p in sorted_players if p[4] == rarity]
        if players_in_rarity:
            text += f"\n{RARITY_EMOJI.get(rarity, '')} <b>{rarity.upper()}</b> ({len(players_in_rarity)}):\n"
            # Показываем только 10 лучших в каждой редкости
            for p in players_in_rarity[:10]:
                text += f"  • {p[1]} {p[0]} — {p[2]} (⭐{p[3]})\n"
            if len(players_in_rarity) > 10:
                text += f"  ... и ещё {len(players_in_rarity) - 10}\n"
    
    await message.answer(text, parse_mode="HTML", reply_markup=main_keyboard(message.from_user))

# =========================================================
# СИСТЕМА ОБМЕНА ИГРОКАМИ (TRADE)
# =========================================================

@DP.message(Command("trade"))
async def trade_command(message: Message):
    await register(message.from_user)
    if not await require_subscription(message):
        return
    
    parts = message.text.split()
    if len(parts) < 2:
        await message.answer(
            "🔄 <b>ОБМЕН ИГРОКАМИ</b>\n\n"
            "Команды:\n"
            "<code>/trade @username</code> — начать обмен с пользователем\n"
            "<code>/trade_list</code> — список активных обменов\n\n"
            "Или используй кнопки меню.",
            parse_mode="HTML",
            reply_markup=main_keyboard(message.from_user)
        )
        return
    
    target = parts[1]
    # Убираем @ если есть
    if target.startswith("@"):
        target = target[1:]
    
    # Ищем пользователя по username
    async with aiosqlite.connect(DB) as db:
        cur = await db.execute(
            "SELECT user_id FROM users WHERE username LIKE ?",
            (f"%{target}%",)
        )
        user_row = await cur.fetchone()
        
        if not user_row:
            await message.answer("❌ Пользователь не найден.")
            return
        
        target_id = user_row[0]
        
        if target_id == message.from_user.id:
            await message.answer("❌ Нельзя обменяться с самим собой.")
            return
    
    # Показываем карты пользователя для выбора
    await show_trade_selection(message.from_user.id, target_id, message.chat.id)

async def show_trade_selection(sender_id, receiver_id, chat_id):
    """Показывает карты для выбора при обмене"""
    async with aiosqlite.connect(DB) as db:
        db.row_factory = aiosqlite.Row
        cur = await db.execute("""
            SELECT id, name, rating, rarity, nation, position, price 
            FROM cards 
            WHERE user_id = ?
            ORDER BY rating DESC
            LIMIT 20
        """, (sender_id,))
        sender_cards = await cur.fetchall()
        
        # Проверяем карты получателя
        cur2 = await db.execute("""
            SELECT id, name, rating, rarity, nation, position, price 
            FROM cards 
            WHERE user_id = ?
            ORDER BY rating DESC
            LIMIT 20
        """, (receiver_id,))
        receiver_cards = await cur2.fetchall()
    
    if not sender_cards:
        await BOT.send_message(chat_id, "❌ У тебя нет карт для обмена.")
        return
    
    if not receiver_cards:
        await BOT.send_message(chat_id, "❌ У пользователя нет карт для обмена.")
        return
    
    text = "🔄 <b>ВЫБЕРИ СВОЮ КАРТУ ДЛЯ ОБМЕНА</b>\n\n"
    kb = InlineKeyboardBuilder()
    
    for card in sender_cards:
        kb.button(
            text=f"{RARITY_EMOJI.get(card['rarity'], '')} {card['name']} (⭐{card['rating']})",
            callback_data=f"trade_send:{receiver_id}:{card['id']}"
        )
    
    kb.button("❌ Отмена", callback_data="trade_cancel")
    kb.adjust(1)
    
    await BOT.send_message(chat_id, text, reply_markup=kb.as_markup(), parse_mode="HTML")

@DP.callback_query(F.data.startswith("trade_send:"))
async def trade_send_callback(callback: CallbackQuery):
    await callback.answer()
    
    _, receiver_id, sender_card_id = callback.data.split(":")
    receiver_id = int(receiver_id)
    sender_card_id = int(sender_card_id)
    
    # Проверяем, что карта принадлежит пользователю
    async with aiosqlite.connect(DB) as db:
        db.row_factory = aiosqlite.Row
        cur = await db.execute(
            "SELECT * FROM cards WHERE id = ? AND user_id = ?",
            (sender_card_id, callback.from_user.id)
        )
        sender_card = await cur.fetchone()
        
        if not sender_card:
            await callback.message.answer("❌ Карта не найдена.")
            return
        
        # Показываем карты получателя для выбора
        cur2 = await db.execute("""
            SELECT id, name, rating, rarity, nation, position, price 
            FROM cards 
            WHERE user_id = ?
            ORDER BY rating DESC
            LIMIT 20
        """, (receiver_id,))
        receiver_cards = await cur2.fetchall()
    
    if not receiver_cards:
        await callback.message.answer("❌ У пользователя нет карт для обмена.")
        return
    
    text = "🔄 <b>ВЫБЕРИ КАРТУ ДЛЯ ОБМЕНА</b>\n\n"
    text += f"Твоя карта: {RARITY_EMOJI.get(sender_card['rarity'], '')} {sender_card['name']} (⭐{sender_card['rating']})\n\n"
    text += "Выбери карту, которую хочешь получить:"
    
    kb = InlineKeyboardBuilder()
    for card in receiver_cards:
        kb.button(
            text=f"{RARITY_EMOJI.get(card['rarity'], '')} {card['name']} (⭐{card['rating']})",
            callback_data=f"trade_confirm:{receiver_id}:{sender_card_id}:{card['id']}"
        )
    
    kb.button("❌ Отмена", callback_data="trade_cancel")
    kb.adjust(1)
    
    await callback.message.edit_text(text, reply_markup=kb.as_markup(), parse_mode="HTML")

@DP.callback_query(F.data.startswith("trade_confirm:"))
async def trade_confirm_callback(callback: CallbackQuery):
    await callback.answer()
    
    _, receiver_id, sender_card_id, receiver_card_id = callback.data.split(":")
    receiver_id = int(receiver_id)
    sender_card_id = int(sender_card_id)
    receiver_card_id = int(receiver_card_id)
    
    # Проверяем обе карты
    async with aiosqlite.connect(DB) as db:
        db.row_factory = aiosqlite.Row
        
        # Проверяем карту отправителя
        cur1 = await db.execute(
            "SELECT * FROM cards WHERE id = ? AND user_id = ?",
            (sender_card_id, callback.from_user.id)
        )
        sender_card = await cur1.fetchone()
        
        # Проверяем карту получателя
        cur2 = await db.execute(
            "SELECT * FROM cards WHERE id = ? AND user_id = ?",
            (receiver_card_id, receiver_id)
        )
        receiver_card = await cur2.fetchone()
        
        if not sender_card:
            await callback.message.answer("❌ Твоя карта уже не доступна.")
            return
        
        if not receiver_card:
            await callback.message.answer("❌ Карта получателя уже не доступна.")
            return
        
        # Создаем запись об обмене
        await db.execute("""
            INSERT INTO trades (sender_id, receiver_id, sender_card_id, receiver_card_id, created_at)
            VALUES (?, ?, ?, ?, ?)
        """, (callback.from_user.id, receiver_id, sender_card_id, receiver_card_id, int(time.time())))
        await db.commit()
        
        # Получаем username получателя
        cur3 = await db.execute("SELECT username FROM users WHERE user_id = ?", (receiver_id,))
        receiver_user = await cur3.fetchone()
        receiver_name = receiver_user["username"] if receiver_user else str(receiver_id)
    
    # Отправляем уведомление получателю
    trade_text = (
        f"🔄 <b>НОВЫЙ ЗАПРОС НА ОБМЕН!</b>\n\n"
        f"Пользователь {callback.from_user.first_name} предлагает обмен:\n\n"
        f"📤 Его карта: {RARITY_EMOJI.get(sender_card['rarity'], '')} {sender_card['name']} (⭐{sender_card['rating']})\n"
        f"📥 Твоя карта: {RARITY_EMOJI.get(receiver_card['rarity'], '')} {receiver_card['name']} (⭐{receiver_card['rating']})\n\n"
        f"Используй команду <code>/trade_list</code> чтобы принять или отклонить обмен."
    )
    
    try:
        await BOT.send_message(receiver_id, trade_text, parse_mode="HTML")
    except Exception:
        pass
    
    await callback.message.answer(
        "✅ <b>ЗАПРОС НА ОБМЕН ОТПРАВЛЕН!</b>\n\n"
        f"Пользователь {receiver_name} получил уведомление.\n"
        "Ожидай ответа.",
        parse_mode="HTML"
    )

@DP.message(Command("trade_list"))
async def trade_list_command(message: Message):
    await register(message.from_user)
    if not await require_subscription(message):
        return
    
    async with aiosqlite.connect(DB) as db:
        db.row_factory = aiosqlite.Row
        
        # Получаем обмены где пользователь получатель и статус pending
        cur = await db.execute("""
            SELECT t.*, 
                   s.name as sender_card_name, s.rating as sender_card_rating, s.rarity as sender_card_rarity,
                   r.name as receiver_card_name, r.rating as receiver_card_rating, r.rarity as receiver_card_rarity,
                   u.username as sender_username
            FROM trades t
            JOIN cards s ON t.sender_card_id = s.id
            JOIN cards r ON t.receiver_card_id = r.id
            LEFT JOIN users u ON t.sender_id = u.user_id
            WHERE t.receiver_id = ? AND t.status = 'pending'
            ORDER BY t.created_at DESC
        """, (message.from_user.id,))
        incoming_trades = await cur.fetchall()
        
        # Получаем обмены где пользователь отправитель и статус pending
        cur2 = await db.execute("""
            SELECT t.*,
                   s.name as sender_card_name, s.rating as sender_card_rating, s.rarity as sender_card_rarity,
                   r.name as receiver_card_name, r.rating as receiver_card_rating, r.rarity as receiver_card_rarity
            FROM trades t
            JOIN cards s ON t.sender_card_id = s.id
            JOIN cards r ON t.receiver_card_id = r.id
            WHERE t.sender_id = ? AND t.status = 'pending'
            ORDER BY t.created_at DESC
        """, (message.from_user.id,))
        outgoing_trades = await cur2.fetchall()
    
    if not incoming_trades and not outgoing_trades:
        await message.answer("📭 Нет активных обменов.", reply_markup=main_keyboard(message.from_user))
        return
    
    text = "🔄 <b>АКТИВНЫЕ ОБМЕНЫ</b>\n\n"
    
    if incoming_trades:
        text += "📥 <b>ВХОДЯЩИЕ ЗАПРОСЫ:</b>\n"
        for trade in incoming_trades:
            sender = trade["sender_username"] or str(trade["sender_id"])
            text += (
                f"└ От {sender}\n"
                f"   📤 {RARITY_EMOJI.get(trade['sender_card_rarity'], '')} {trade['sender_card_name']} (⭐{trade['sender_card_rating']})\n"
                f"   📥 {RARITY_EMOJI.get(trade['receiver_card_rarity'], '')} {trade['receiver_card_name']} (⭐{trade['receiver_card_rating']})\n"
            )
            
            kb = InlineKeyboardBuilder()
            kb.button(text="✅ Принять", callback_data=f"trade_accept:{trade['id']}")
            kb.button(text="❌ Отклонить", callback_data=f"trade_decline:{trade['id']}")
            kb.adjust(2)
            
            await BOT.send_message(
                message.chat.id,
                text,
                reply_markup=kb.as_markup(),
                parse_mode="HTML"
            )
            text = ""  # Сбрасываем текст, так как уже отправили
    
    if outgoing_trades:
        text = "📤 <b>ИСХОДЯЩИЕ ЗАПРОСЫ:</b>\n"
        for trade in outgoing_trades:
            text += (
                f"└ ID: {trade['id']}\n"
                f"   📤 {RARITY_EMOJI.get(trade['sender_card_rarity'], '')} {trade['sender_card_name']} (⭐{trade['sender_card_rating']})\n"
                f"   📥 {RARITY_EMOJI.get(trade['receiver_card_rarity'], '')} {trade['receiver_card_name']} (⭐{trade['receiver_card_rating']})\n"
                f"   ⏳ Ожидает ответа...\n"
            )
        
        await message.answer(text, parse_mode="HTML")

@DP.callback_query(F.data.startswith("trade_accept:"))
async def trade_accept_callback(callback: CallbackQuery):
    await callback.answer()
    
    trade_id = int(callback.data.split(":")[1])
    
    async with aiosqlite.connect(DB) as db:
        db.row_factory = aiosqlite.Row
        
        # Получаем данные обмена
        cur = await db.execute("SELECT * FROM trades WHERE id = ? AND receiver_id = ? AND status = 'pending'", 
                               (trade_id, callback.from_user.id))
        trade = await cur.fetchone()
        
        if not trade:
            await callback.message.answer("❌ Обмен не найден или уже обработан.")
            return
        
        # Проверяем, что карты все еще существуют
        cur1 = await db.execute("SELECT * FROM cards WHERE id = ?", (trade["sender_card_id"],))
        sender_card = await cur1.fetchone()
        
        cur2 = await db.execute("SELECT * FROM cards WHERE id = ?", (trade["receiver_card_id"],))
        receiver_card = await cur2.fetchone()
        
        if not sender_card or not receiver_card:
            await callback.message.answer("❌ Одна из карт уже не доступна.")
            # Обновляем статус
            await db.execute("UPDATE trades SET status = 'cancelled' WHERE id = ?", (trade_id,))
            await db.commit()
            return
        
        # Проверяем, что карты принадлежат правильным пользователям
        if sender_card["user_id"] != trade["sender_id"]:
            await callback.message.answer("❌ Карта отправителя уже не принадлежит ему.")
            await db.execute("UPDATE trades SET status = 'cancelled' WHERE id = ?", (trade_id,))
            await db.commit()
            return
        
        if receiver_card["user_id"] != trade["receiver_id"]:
            await callback.message.answer("❌ Твоя карта уже не доступна.")
            await db.execute("UPDATE trades SET status = 'cancelled' WHERE id = ?", (trade_id,))
            await db.commit()
            return
        
        # Меняем владельцев карт
        await db.execute("UPDATE cards SET user_id = ? WHERE id = ?", (trade["sender_id"], trade["receiver_card_id"]))
        await db.execute("UPDATE cards SET user_id = ? WHERE id = ?", (trade["receiver_id"], trade["sender_card_id"]))
        
        # Обновляем статус обмена
        await db.execute("UPDATE trades SET status = 'completed' WHERE id = ?", (trade_id,))
        await db.commit()
    
    await callback.message.edit_text(
        "✅ <b>ОБМЕН УСПЕШНО ЗАВЕРШЁН!</b>\n\n"
        f"Ты получил: {RARITY_EMOJI.get(sender_card['rarity'], '')} {sender_card['name']} (⭐{sender_card['rating']})",
        parse_mode="HTML"
    )
    
    # Уведомляем отправителя
    try:
        await BOT.send_message(
            trade["sender_id"],
            f"✅ <b>ОБМЕН ПРИНЯТ!</b>\n\n"
            f"Ты получил: {RARITY_EMOJI.get(receiver_card['rarity'], '')} {receiver_card['name']} (⭐{receiver_card['rating']})",
            parse_mode="HTML"
        )
    except Exception:
        pass

@DP.callback_query(F.data.startswith("trade_decline:"))
async def trade_decline_callback(callback: CallbackQuery):
    await callback.answer()
    
    trade_id = int(callback.data.split(":")[1])
    
    async with aiosqlite.connect(DB) as db:
        # Получаем данные обмена
        cur = await db.execute("SELECT * FROM trades WHERE id = ? AND receiver_id = ? AND status = 'pending'", 
                               (trade_id, callback.from_user.id))
        trade = await cur.fetchone()
        
        if not trade:
            await callback.message.answer("❌ Обмен не найден или уже обработан.")
            return
        
        # Обновляем статус
        await db.execute("UPDATE trades SET status = 'declined' WHERE id = ?", (trade_id,))
        await db.commit()
    
    await callback.message.edit_text(
        "❌ <b>ОБМЕН ОТКЛОНЁН</b>",
        parse_mode="HTML"
    )
    
    # Уведомляем отправителя
    try:
        await BOT.send_message(
            trade["sender_id"],
            "❌ <b>ОБМЕН ОТКЛОНЁН</b>\n\nПользователь отклонил твой запрос на обмен.",
            parse_mode="HTML"
        )
    except Exception:
        pass

@DP.callback_query(F.data == "trade_menu")
async def trade_menu_callback(callback: CallbackQuery):
    await callback.answer()
    await callback.message.answer(
        "🔄 <b>ОБМЕН ИГРОКАМИ</b>\n\n"
        "Команды:\n"
        "<code>/trade @username</code> — начать обмен с пользователем\n"
        "<code>/trade_list</code> — список активных обменов",
        parse_mode="HTML",
        reply_markup=main_keyboard(callback.from_user)
    )

@DP.callback_query(F.data == "trade_cancel")
async def trade_cancel_callback(callback: CallbackQuery):
    await callback.answer()
    await callback.message.edit_text("❌ Обмен отменён.", reply_markup=main_keyboard(callback.from_user))

# =========================================================
# ОСТАЛЬНЫЕ КОМАНДЫ (без изменений)
# =========================================================

@DP.message(Command("drop"))
async def drop_command(message: Message):
    await do_drop(message)

@DP.message(Command("start"))
async def start(message: Message):
    await register(message.from_user)
    if not await require_subscription(message):
        return
    user = await get_user(message.from_user.id)
    if user["banned"] and not is_owner(message.from_user):
        await message.answer("🚫 Вы заблокированы.")
        return
    cards = await count_cards(message.from_user.id)
    await message.answer(
        f"⚽ <b>FOOTBALL DROP</b>\n\n"
        f"Привет, <b>{html.escape(message.from_user.first_name)}</b>!\n\n"
        f"🪙 Монеты: <b>{user['coins']:,}</b>\n"
        f"⭐ Stars: <b>{user['stars']}</b>\n"
        f"🃏 Карт: <b>{cards}</b>\n\n"
        "⚽ DROP — раз в 10 минут\n"
        "📚 Коллекция — твои карты\n"
        "🏪 Магазин — покупки\n"
        "💰 Рынок — продажа карт\n"
        "🎁 Daily — ежедневная награда\n"
        "🎯 Задания — дополнительные награды\n"
        "🍀 Lucky Charm — повышенный шанс\n"
        "🔄 Обмен — меняйся картами с друзьями",
        reply_markup=main_keyboard(message.from_user),parse_mode="HTML")

@DP.message(Command("help"))
async def help_command(message: Message):
    await register(message.from_user)
    if not await require_subscription(message):
        return

    text = (
        "🆘 <b>ПОМОЩЬ — FOOTBALL DROP</b>\n\n"
        "🃏 <code>/drop</code> — открыть DROP\n"
        "👤 <code>/profile</code> — профиль\n"
        "📚 <code>/collection</code> — коллекция\n"
        "💰 <code>/balance</code> — баланс\n"
        "🛒 <code>/shop</code> — магазин\n"
        "⭐ <code>/packs</code> — паки за Stars\n"
        "🪙 <code>/coinpacks</code> — паки за монеты\n"
        "🍀 <code>/lucky</code> — Lucky Charm\n"
        "🍀 <code>/charm</code> — статус Lucky Charm\n"
        "🎁 <code>/daily</code> — Daily\n"
        "🎯 <code>/missions</code> — задания\n"
        "🏆 <code>/top</code> — рейтинг\n"
        "🎟️ <code>/promo CODE</code> — активировать промокод\n"
        "🔄 <code>/trade @username</code> — обмен картами\n"
        "🔄 <code>/trade_list</code> — список обменов\n"
        "📋 <code>/players</code> — все игроки\n"
        "🆘 <code>/help</code> — список команд\n\n"
    )
    if is_owner(message.from_user):
        text += (
            "👑 <b>КОМАНДЫ OWNER</b>\n"
            "👑 <code>/owner</code> — панель владельца\n"
            "🎉 <code>/event</code> — управление ивентами\n"
            "📊 <code>/stats</code> — статистика\n"
            "🎟️ <code>/createpromo CODE COINS STARS LIMIT</code>\n"
            "💰 <code>/give USER_ID COINS</code>\n"
            "🚫 <code>/ban USER_ID</code>\n"
            "✅ <code>/unban USER_ID</code>\n"
            "📡 <code>/events</code> — активный ивент\n"
        )
    await message.answer(text,parse_mode="HTML",reply_markup=main_keyboard(message.from_user))

async def show_collection_for_user(user_id,chat_id):
    user = await get_user(user_id)
    if not user:
        return

    async with aiosqlite.connect(DB) as db:
        db.row_factory = aiosqlite.Row
        cur = await db.execute("""
            SELECT * FROM cards
            WHERE user_id=?
            ORDER BY rating DESC,id DESC
            LIMIT 100
        """,(user_id,))
        cards = await cur.fetchall()

    if not cards:
        await BOT.send_message(
            chat_id,
            "📚 <b>ТВОЯ КОЛЛЕКЦИЯ ПУСТА</b>\n\n"
            "Открой свой первый DROP ⚽",
            parse_mode="HTML")
        return

    text = "📚 <b>ТВОЯ КОЛЛЕКЦИЯ</b>\n\n"
    for i,card in enumerate(cards,1):
        text += (
            f"{i}. {RARITY_EMOJI.get(card['rarity'],'⚪')} "
            f"<b>{html.escape(card['name'])}</b>\n"
            f"   {card['nation']} {card['position']} | "
            f"⭐ {card['rating']}\n"
            f"   💰 €{card['price']:,}\n\n"
        )

    kb = InlineKeyboardBuilder()
    kb.button(text="⚽ DROP",callback_data="drop")
    kb.button(text="🏪 Продать карты",callback_data="market")
    kb.button(text="🔄 Обмен",callback_data="trade_menu")
    kb.adjust(2)

    await BOT.send_message(
        chat_id,text,reply_markup=kb.as_markup(),parse_mode="HTML")

@DP.message(Command("collection"))
async def collection_command(message: Message):
    await register(message.from_user)
    if not await require_subscription(message):
        return
    await show_collection_for_user(message.from_user.id,message.chat.id)

@DP.message(Command("mycards"))
async def mycards_command(message: Message):
    await collection_command(message)

async def show_profile(message):
    await register(message.from_user)
    if not await require_subscription(message):
        return
    u = await get_user(message.from_user.id)
    lucky = "активен" if u["lucky_until"] > int(time.time()) else "нет"
    await message.answer(
        "👤 <b>ПРОФИЛЬ</b>\n\n"
        f"👤 {html.escape(message.from_user.first_name)}\n"
        f"🪙 Монеты: <b>{u['coins']:,}</b>\n"
        f"⭐ Stars: <b>{u['stars']}</b>\n"
        f"🃏 Карт: <b>{await count_cards(message.from_user.id)}</b>\n"
        f"🏆 Побед: <b>{u['wins']}</b>\n"
        f"💀 Поражений: <b>{u['losses']}</b>\n"
        f"🍀 Lucky Charm: <b>{lucky}</b>",
        parse_mode="HTML")

@DP.message(Command("profile"))
async def profile_command(message):
    await show_profile(message)

def shop_keyboard():
    kb = InlineKeyboardBuilder()
    kb.button(text="🍀 Lucky Charm",callback_data="lucky")
    kb.button(text="⭐ Паки за Stars",callback_data="packs")
    kb.button(text="📦 Паки за 🪙",callback_data="coinpacks")
    kb.button(text="🏪 Продать карту боту",callback_data="market")
    kb.adjust(1)
    return kb.as_markup()

async def show_shop(message):
    await register(message.from_user)
    if not await require_subscription(message):
        return
    await message.answer(
        "🏪 <b>МАГАЗИН</b>\n\n"
        "🍀 Lucky Charm — 15 ⭐\n"
        "✨ Действует 24 часа.\n\n"
        "⭐ Паки — за Telegram Stars.\n"
        "📦 Coin Packs — за монеты.\n\n"
        "💰 Продать карту — получить монеты.",
        reply_markup=shop_keyboard(),parse_mode="HTML")

@DP.message(Command("shop"))
async def shop_command(message):
    await show_shop(message)

async def send_lucky_invoice(chat_id):
    await BOT.send_invoice(
        chat_id=chat_id,title="🍀 Lucky Charm",
        description="24 часа повышенного шанса на редкие карты.",
        payload=f"lucky:{chat_id}:{int(time.time())}",
        currency="XTR",
        prices=[LabeledPrice(label="Lucky Charm",amount=LUCKY_COST)])

@DP.message(Command("lucky"))
async def lucky_command(message):
    await register(message.from_user)
    if not await require_subscription(message):
        return
    await send_lucky_invoice(message.chat.id)

async def show_packs(message):
    await register(message.from_user)
    if not await require_subscription(message):
        return
    kb = InlineKeyboardBuilder()
    for key,(stars,amount,name) in STAR_PACKS.items():
        kb.button(text=f"{name} — {stars} ⭐",callback_data=f"pack:{key}")
    kb.adjust(1)
    await message.answer(
        "⭐ <b>ПАКИ ЗА STARS</b>\n\nВыбери пак:",
        reply_markup=kb.as_markup(),parse_mode="HTML")

@DP.message(Command("packs"))
async def packs_command(message):
    await show_packs(message)

async def open_star_pack(user_id,key):
    if key not in STAR_PACKS:
        return None
    stars,amount,name = STAR_PACKS[key]
    async with aiosqlite.connect(DB) as db:
        db.row_factory = aiosqlite.Row
        cur = await db.execute(
            "SELECT stars FROM users WHERE user_id=?",(user_id,))
        user = await cur.fetchone()
        if not user or user["stars"] < stars:
            return None
        await db.execute(
            "UPDATE users SET stars=stars-? WHERE user_id=?",
            (stars,user_id))
        await db.commit()

    pulled=[]
    user=await get_user(user_id)
    event=await get_active_event()
    for _ in range(amount):
        player=random_player(user,event)
        await add_card(user_id,player)
        await mission_update(user_id,"cards")
        pulled.append(player)
    return name,pulled

@DP.callback_query(F.data.startswith("pack:"))
async def pack_callback(callback):
    await callback.answer()
    await register(callback.from_user)
    key=callback.data.split(":",1)[1]
    result=await open_star_pack(callback.from_user.id,key)
    if not result:
        await callback.message.answer(
            f"❌ Недостаточно Stars.\n\nНужно: <b>{STAR_PACKS[key][0]} ⭐</b>",
            parse_mode="HTML")
        return
    name,pulled=result
    best=max(pulled,key=lambda p:p[3])
    await callback.message.answer(
        "📦 <b>ПАК ОТКРЫТ!</b>\n\n"
        f"{name}\n🃏 Получено карт: <b>{len(pulled)}</b>\n\n"
        "🔥 Лучшая карта:\n"
        f"{RARITY_EMOJI[best[4]]} <b>{html.escape(best[0])}</b>\n"
        f"⭐ {best[3]} OVR\n💰 €{best[5]:,}",
        parse_mode="HTML")

async def show_coinpacks(message):
    await register(message.from_user)
    if not await require_subscription(message):
        return
    kb=InlineKeyboardBuilder()
    for key,(price,amount,name) in COIN_PACKS.items():
        kb.button(text=f"{name} — {price:,} 🪙",
                  callback_data=f"coinpack:{key}")
    kb.adjust(1)
    await message.answer(
        "📦 <b>ПАКИ ЗА МОНЕТЫ</b>",
        reply_markup=kb.as_markup(),parse_mode="HTML")

@DP.message(Command("coinpacks"))
async def coinpacks_command(message):
    await show_coinpacks(message)

@DP.callback_query(F.data.startswith("coinpack:"))
async def coinpack_callback(callback):
    await callback.answer()
    await register(callback.from_user)
    key=callback.data.split(":",1)[1]
    if key not in COIN_PACKS:
        return
    price,amount,pack_name=COIN_PACKS[key]
    if not await spend_coins(callback.from_user.id,price):
        await callback.message.answer("❌ Недостаточно монет.")
        return
    user=await get_user(callback.from_user.id)
    event=await get_active_event()
    pulled=[]
    for _ in range(amount):
        player=random_player(user,event)
        await add_card(callback.from_user.id,player)
        await mission_update(callback.from_user.id,"cards")
        pulled.append(player)
    best=max(pulled,key=lambda p:p[3])
    await callback.message.answer(
        "📦 <b>ПАК ОТКРЫТ!</b>\n\n"
        f"{pack_name}\n🃏 Карт: <b>{amount}</b>\n\n"
        "🔥 Лучшая:\n"
        f"{RARITY_EMOJI[best[4]]} <b>{html.escape(best[0])}</b>\n"
        f"⭐ {best[3]} OVR\n💰 €{best[5]:,}",
        parse_mode="HTML")

async def show_market(user_id,chat_id):
    async with aiosqlite.connect(DB) as db:
        db.row_factory=aiosqlite.Row
        cur=await db.execute("""
            SELECT * FROM cards WHERE user_id=?
            ORDER BY rating DESC,id DESC LIMIT 20
        """,(user_id,))
        cards=await cur.fetchall()

    if not cards:
        await BOT.send_message(
            chat_id,"🏪 <b>ПРОДАЖА КАРТ БОТУ</b>\n\nУ тебя нет карт.",
            parse_mode="HTML")
        return

    text=("🏪 <b>ПРОДАТЬ КАРТУ БОТУ</b>\n\n"
          "Нажми на карту — бот купит её за указанную цену.\n\n")
    kb=InlineKeyboardBuilder()
    for card in cards:
        text += (
            f"{RARITY_EMOJI.get(card['rarity'],'⚪')} "
            f"<b>{html.escape(card['name'])}</b> — €{card['price']:,}\n")
        kb.button(text=f"💰 Продать {card['name']}",
                  callback_data=f"sell:{card['id']}")
    kb.adjust(1)
    await BOT.send_message(
        chat_id,text,reply_markup=kb.as_markup(),parse_mode="HTML")

@DP.callback_query(F.data=="market")
async def market_callback(callback):
    await callback.answer()
    await register(callback.from_user)
    await show_market(callback.from_user.id,callback.message.chat.id)

@DP.callback_query(F.data.startswith("sell:"))
async def sell_callback(callback):
    await callback.answer()
    try:
        card_id=int(callback.data.split(":")[1])
    except Exception:
        return
    async with aiosqlite.connect(DB) as db:
        db.row_factory=aiosqlite.Row
        cur=await db.execute(
            "SELECT * FROM cards WHERE id=? AND user_id=?",
            (card_id,callback.from_user.id))
        card=await cur.fetchone()
        if not card:
            await callback.message.answer(
                "❌ Карта уже продана или не найдена.")
            return
        price=card["price"]
        await db.execute(
            "DELETE FROM cards WHERE id=? AND user_id=?",
            (card_id,callback.from_user.id))
        await db.execute(
            "UPDATE users SET coins=coins+? WHERE user_id=?",
            (price,callback.from_user.id))
        await db.commit()
    await callback.message.answer(
        "💰 <b>КАРТА ПРОДАНА БОТУ!</b>\n\n"
        f"👤 {html.escape(card['name'])}\n"
        f"⭐ {card['rating']} OVR\n"
        f"💵 Получено: <b>{price:,} 🪙</b>",
        parse_mode="HTML")

@DP.message(Command("balance"))
async def balance_command(message):
    await register(message.from_user)
    user=await get_user(message.from_user.id)
    await message.answer(
        "💰 <b>ТВОЙ БАЛАНС</b>\n\n"
        f"🪙 Монеты: <b>{user['coins']:,}</b>\n"
        f"⭐ Stars: <b>{user['stars']}</b>",
        parse_mode="HTML")

async def do_daily(user_id,chat_id):
    today=datetime.now(timezone.utc).strftime("%Y-%m-%d")
    async with aiosqlite.connect(DB) as db:
        cur=await db.execute(
            "SELECT daily_date,daily_streak FROM users WHERE user_id=?",
            (user_id,))
        user=await cur.fetchone()
        if user[0]==today:
            await BOT.send_message(chat_id,"🎁 Daily уже получен сегодня.")
            return
        streak=user[1]+1
        reward=500+min(streak,7)*100
        await db.execute("""
            UPDATE users SET daily_date=?,daily_streak=? WHERE user_id=?
        """,(today,streak,user_id))
        await db.commit()
    await add_coins(user_id,reward)
    await BOT.send_message(
        chat_id,
        "🎁 <b>DAILY ПОЛУЧЕН!</b>\n\n"
        f"🔥 Серия: <b>{streak}</b>\n"
        f"🪙 Награда: <b>+{reward:,}</b>",
        parse_mode="HTML")

@DP.message(Command("daily"))
async def daily_command(message):
    await register(message.from_user)
    if not await require_subscription(message):
        return
    await do_daily(message.from_user.id,message.chat.id)

async def do_missions(user_id,chat_id):
    async with aiosqlite.connect(DB) as db:
        db.row_factory=aiosqlite.Row
        cur=await db.execute(
            "SELECT * FROM missions WHERE user_id=?",(user_id,))
        m=await cur.fetchone()
    await BOT.send_message(
        chat_id,
        "🎯 <b>ЗАДАНИЯ</b>\n\n"
        f"⚽ DROP: <b>{m['drops']}/10</b>\n"
        f"🃏 Карты: <b>{m['cards']}/20</b>\n\n"
        "🎁 Награды за выполнение можно добавить в следующей версии.",
        parse_mode="HTML")

@DP.message(Command("missions"))
async def missions_command(message):
    await register(message.from_user)
    if not await require_subscription(message):
        return
    await do_missions(message.from_user.id,message.chat.id)

@DP.message(Command("top"))
async def top_command(message):
    await register(message.from_user)
    if not await require_subscription(message):
        return
    async with aiosqlite.connect(DB) as db:
        cur=await db.execute("""
            SELECT user_id,username,first_name,coins FROM users
            WHERE banned=0 ORDER BY coins DESC LIMIT 10
        """)
        rows=await cur.fetchall()
    text="🏆 <b>ТОП 10</b>\n\n"
    for i,row in enumerate(rows,1):
        name=row[1] or row[2] or "Игрок"
        text += f"{i}. <b>{html.escape(name)}</b> — {row[3]:,} 🪙\n"
    await message.answer(text,parse_mode="HTML")

@DP.message(Command("promo"))
async def promo_command(message):
    await register(message.from_user)
    if not await require_subscription(message):
        return
    parts=message.text.split()
    if len(parts)<2:
        await message.answer(
            "🎟️ Использование:\n<code>/promo CODE</code>",
            parse_mode="HTML")
        return
    code=parts[1].upper().strip()
    async with aiosqlite.connect(DB) as db:
        db.row_factory=aiosqlite.Row
        cur=await db.execute(
            "SELECT * FROM promo_codes WHERE code=?",(code,))
        promo=await cur.fetchone()
        if not promo:
            await message.answer("❌ Промокод не найден.")
            return
        cur=await db.execute(
            "SELECT 1 FROM promo_uses WHERE code=? AND user_id=?",
            (code,message.from_user.id))
        if await cur.fetchone():
            await message.answer("❌ Ты уже использовал этот промокод.")
            return
        if promo["used"]>=promo["activations"]:
            await message.answer("❌ Лимит активаций закончился.")
            return
        await db.execute(
            "INSERT INTO promo_uses(code,user_id) VALUES(?,?)",
            (code,message.from_user.id))
        await db.execute(
            "UPDATE promo_codes SET used=used+1 WHERE code=?",(code,))
        await db.execute("""
            UPDATE users SET coins=coins+?,stars=stars+? WHERE user_id=?
        """,(promo["coins"],promo["stars"],message.from_user.id))
        await db.commit()
    await message.answer(
        "🎉 <b>ПРОМОКОД АКТИВИРОВАН!</b>\n\n"
        f"🪙 +{promo['coins']:,}\n"
        f"⭐ +{promo['stars']}",
        parse_mode="HTML")

async def create_promo(code,coins,stars,activations):
    async with aiosqlite.connect(DB) as db:
        try:
            await db.execute("""
                INSERT INTO promo_codes
                (code,coins,stars,activations,used,created)
                VALUES(?,?,?,?,0,?)
            """,(code,coins,stars,activations,int(time.time())))
            await db.commit()
            return True
        except aiosqlite.IntegrityError:
            return False

@DP.message(Command("createpromo"))
async def createpromo_command(message):
    await register(message.from_user)
    if not is_owner(message.from_user):
        await message.answer("❌ Только владелец бота.")
        return

    parts=message.text.split()
    if len(parts)!=5:
        await message.answer(
            "🎟️ <b>Создание промокода</b>\n\n"
            "<code>/createpromo CODE COINS STARS LIMIT</code>\n\n"
            "Пример:\n"
            "<code>/createpromo FOOTBALL 5000 0 100</code>",
            parse_mode="HTML")
        return

    code=parts[1].upper()
    try:
        coins=int(parts[2])
        stars=int(parts[3])
        activations=int(parts[4])
        if coins<0 or stars<0 or activations<1:
            raise ValueError
    except ValueError:
        await message.answer("❌ COINS, STARS и LIMIT должны быть числами.")
        return

    ok=await create_promo(code,coins,stars,activations)
    if not ok:
        await message.answer("❌ Такой промокод уже существует.")
        return

    await message.answer(
        "✅ <b>ПРОМОКОД СОЗДАН!</b>\n\n"
        f"🎟️ Код: <code>{html.escape(code)}</code>\n"
        f"🪙 Награда: <b>+{coins:,}</b>\n"
        f"⭐ Stars: <b>+{stars}</b>\n"
        f"👥 Активаций: <b>{activations}</b>",
        parse_mode="HTML")

@DP.message(Command("charm"))
async def charm_command(message):
    await register(message.from_user)
    if not await require_subscription(message):
        return
    async with aiosqlite.connect(DB) as db:
        db.row_factory=aiosqlite.Row
        cur=await db.execute(
            "SELECT * FROM lucky_charms WHERE user_id=?",
            (message.from_user.id,))
        charm=await cur.fetchone()
    if not charm:
        await message.answer(
            "🍀 <b>LUCKY CHARM</b>\n\n❌ Сейчас не активен.",
            parse_mode="HTML")
        return
    left=charm["expires_at"]-int(time.time())
    if left<=0:
        await message.answer("🍀 Lucky Charm закончился.")
        return
    await message.answer(
        "🍀 <b>LUCKY CHARM АКТИВЕН</b>\n\n"
        f"⏳ Осталось: <b>{left//3600}ч {(left%3600)//60}м</b>",
        parse_mode="HTML")

def owner_keyboard():
    kb=InlineKeyboardBuilder()
    kb.button(text="🎉 Ивенты",callback_data="event_menu")
    kb.button(text="📊 Статистика",callback_data="owner_stats")
    kb.button(text="🎟️ Создать промокод",callback_data="owner_promo_help")
    kb.button(text="📡 Активный ивент",callback_data="owner_events")
    kb.adjust(1)
    return kb.as_markup()

async def show_owner_panel(message):
    if not is_owner(message.from_user):
        await message.answer("❌ Только владелец бота.")
        return
    await message.answer(
        "👑 <b>OWNER PANEL</b>\n\n"
        "Здесь @foqlu может управлять ботом.\n\n"
        "🎉 Ивенты — включение/выключение и выбор длительности.\n"
        "📊 Статистика — пользователи, карты и монеты.\n"
        "🎟️ Промокоды — создание промокодов.\n\n"
        "Создать промокод командой:\n"
        "<code>/createpromo CODE COINS STARS LIMIT</code>",
        reply_markup=owner_keyboard(),parse_mode="HTML")

@DP.message(Command("owner"))
async def owner_command(message):
    await register(message.from_user)
    await show_owner_panel(message)

@DP.callback_query(F.data=="owner")
async def owner_callback(callback):
    await callback.answer()
    await show_owner_panel(callback.message)

@DP.callback_query(F.data=="owner_promo_help")
async def owner_promo_help(callback):
    await callback.answer()
    if not is_owner(callback.from_user):
        return
    await callback.message.answer(
        "🎟️ <b>СОЗДАНИЕ ПРОМОКОДА</b>\n\n"
        "<code>/createpromo CODE COINS STARS LIMIT</code>\n\n"
        "Пример:\n"
        "<code>/createpromo DROP10 10000 0 50</code>",
        parse_mode="HTML")

@DP.message(Command("event"))
async def event_command(message):
    await register(message.from_user)
    if not is_owner(message.from_user):
        await message.answer("❌ Только владелец бота.")
        return
    await message.answer(
        "👑 <b>ПАНЕЛЬ ИВЕНТОВ</b>\n\nВыбери ивент:",
        reply_markup=event_keyboard(),parse_mode="HTML")

@DP.callback_query(F.data=="event_menu")
async def event_menu_callback(callback):
    await callback.answer()
    if not is_owner(callback.from_user):
        return
    await callback.message.answer(
        "👑 <b>ВЫБЕРИ ИВЕНТ</b>\n\nНажми на нужный ивент:",
        reply_markup=event_keyboard(),parse_mode="HTML")

@DP.callback_query(F.data.startswith("event_select:"))
async def event_select_callback(callback):
    await callback.answer()
    if not is_owner(callback.from_user):
        return
    event_key=callback.data.split(":",1)[1]
    if event_key not in EVENTS:
        return
    event=EVENTS[event_key]
    await callback.message.answer(
        f"{event['name']}\n\n"
        f"📋 {event['description']}\n\n"
        "⏳ <b>На сколько включить?</b>",
        reply_markup=event_duration_keyboard(event_key),
        parse_mode="HTML")

@DP.callback_query(F.data.startswith("event_start:"))
async def event_start_callback(callback):
    await callback.answer()
    if not is_owner(callback.from_user):
        return
    parts=callback.data.split(":")
    if len(parts)!=3:
        return
    event_key=parts[1]
    try:
        minutes=int(parts[2])
    except ValueError:
        return
    if event_key not in EVENTS:
        return

    await stop_event()
    await start_event(event_key,minutes)
    event=EVENTS[event_key]

    if minutes==0:
        duration="♾ НАВСЕГДА"
    elif minutes<60:
        duration=f"{minutes} минут"
    elif minutes==60:
        duration="1 час"
    else:
        duration=f"{minutes//60} часов"

    await callback.message.answer(
        "🚨 <b>ИВЕНТ ВКЛЮЧЁН!</b>\n\n"
        f"{event['name']}\n"
        f"📋 {event['description']}\n"
        f"⏳ Длительность: <b>{duration}</b>",
        parse_mode="HTML")

    asyncio.create_task(notify_event_started(event_key,minutes))

@DP.callback_query(F.data=="event_stop")
async def event_stop_callback(callback):
    await callback.answer()
    if not is_owner(callback.from_user):
        return
    active=await get_active_event()
    if not active:
        await callback.message.answer("ℹ️ Сейчас нет активного ивента.")
        return
    event=EVENTS.get(active["event_key"])
    await stop_event()
    await callback.message.answer(
        "⛔ <b>ИВЕНТ ОСТАНОВЛЕН!</b>\n\n"
        f"{event['name'] if event else active['event_key']}",
        parse_mode="HTML")

@DP.message(Command("events"))
async def events_command(message):
    await register(message.from_user)
    if not is_owner(message.from_user):
        await message.answer("❌ Только владелец бота.")
        return
    active=await get_active_event()
    if not active:
        await message.answer("📭 Сейчас активных ивентов нет.")
        return
    event=EVENTS.get(active["event_key"])
    if not event:
        return
    if active["expires_at"]==0:
        left="♾ навсегда"
    else:
        seconds=active["expires_at"]-int(time.time())
        if seconds<=0:
            await stop_event()
            await message.answer("📭 Ивент уже закончился.")
            return
        left=f"{seconds//3600}ч {(seconds%3600)//60}м {seconds%60}с"
    await message.answer(
        "🚨 <b>АКТИВНЫЙ ИВЕНТ</b>\n\n"
        f"{event['name']}\n"
        f"📋 {event['description']}\n"
        f"⏳ Осталось: <b>{left}</b>",
        parse_mode="HTML")

@DP.message(Command("stats"))
async def stats_command(message):
    await register(message.from_user)
    if not is_owner(message.from_user):
        return
    async with aiosqlite.connect(DB) as db:
        cur=await db.execute("SELECT COUNT(*) FROM users")
        users=(await cur.fetchone())[0]
        cur=await db.execute("SELECT COUNT(*) FROM cards")
        cards=(await cur.fetchone())[0]
        cur=await db.execute("SELECT SUM(coins) FROM users")
        coins=(await cur.fetchone())[0] or 0
    await message.answer(
        "👑 <b>СТАТИСТИКА</b>\n\n"
        f"👥 Пользователей: <b>{users}</b>\n"
        f"🃏 Карт: <b>{cards}</b>\n"
        f"🪙 Монет в системе: <b>{coins:,}</b>",
        parse_mode="HTML")

@DP.callback_query(F.data=="owner_stats")
async def owner_stats_callback(callback):
    await callback.answer()
    if not is_owner(callback.from_user):
        return
    await stats_command(callback.message)

@DP.callback_query(F.data=="owner_events")
async def owner_events_callback(callback):
    await callback.answer()
    if not is_owner(callback.from_user):
        return
    await events_command(callback.message)

@DP.message(Command("give"))
async def give_command(message):
    await register(message.from_user)
    if not is_owner(message.from_user):
        return
    parts=message.text.split()
    if len(parts)!=3:
        await message.answer(
            "Использование:\n<code>/give USER_ID COINS</code>",
            parse_mode="HTML")
        return
    try:
        user_id=int(parts[1])
        amount=int(parts[2])
    except ValueError:
        await message.answer("❌ Неверные данные.")
        return
    await add_coins(user_id,amount)
    await message.answer(
        f"✅ Выдано <b>{amount:,} 🪙</b>\n"
        f"👤 ID: <code>{user_id}</code>",
        parse_mode="HTML")

@DP.message(Command("ban"))
async def ban_command(message):
    if not is_owner(message.from_user):
        return
    parts=message.text.split()
    if len(parts)!=2:
        return
    try:
        user_id=int(parts[1])
    except ValueError:
        return
    async with aiosqlite.connect(DB) as db:
        await db.execute(
            "UPDATE users SET banned=1 WHERE user_id=?",(user_id,))
        await db.commit()
    await message.answer(
        f"🚫 Пользователь <code>{user_id}</code> заблокирован.",
        parse_mode="HTML")

@DP.message(Command("unban"))
async def unban_command(message):
    if not is_owner(message.from_user):
        return
    parts=message.text.split()
    if len(parts)!=2:
        return
    try:
        user_id=int(parts[1])
    except ValueError:
        return
    async with aiosqlite.connect(DB) as db:
        await db.execute(
            "UPDATE users SET banned=0 WHERE user_id=?",(user_id,))
        await db.commit()
    await message.answer(
        f"✅ Пользователь <code>{user_id}</code> разблокирован.",
        parse_mode="HTML")

# ---------- CALLBACKS ----------

@DP.callback_query(F.data=="drop")
async def drop_callback(callback):
    await callback.answer()
    await do_drop(callback.message)

@DP.callback_query(F.data=="collection")
async def collection_callback(callback):
    await callback.answer()
    await register(callback.from_user)
    await show_collection_for_user(
        callback.from_user.id,
        callback.message.chat.id
    )

@DP.callback_query(F.data=="profile")
async def profile_callback(callback):
    await callback.answer()
    await show_profile(callback.message)

@DP.callback_query(F.data=="shop")
async def shop_callback(callback):
    await callback.answer()
    await show_shop(callback.message)

@DP.callback_query(F.data=="packs")
async def packs_callback(callback):
    await callback.answer()
    await show_packs(callback.message)

@DP.callback_query(F.data=="coinpacks")
async def coinpacks_callback(callback):
    await callback.answer()
    await show_coinpacks(callback.message)

@DP.callback_query(F.data=="lucky")
async def lucky_callback(callback):
    await callback.answer()
    await send_lucky_invoice(callback.from_user.id)

@DP.callback_query(F.data=="daily")
async def daily_callback(callback):
    await callback.answer()
    await register(callback.from_user)
    await do_daily(callback.from_user.id,callback.message.chat.id)

@DP.callback_query(F.data=="missions")
async def missions_callback(callback):
    await callback.answer()
    await register(callback.from_user)
    await do_missions(callback.from_user.id,callback.message.chat.id)

@DP.callback_query(F.data=="top")
async def top_callback(callback):
    await callback.answer()
    await top_command(callback.message)

@DP.callback_query(F.data=="promo")
async def promo_callback(callback):
    await callback.answer()
    await callback.message.answer(
        "🎟️ Введи промокод командой:\n\n"
        "<code>/promo CODE</code>",
        parse_mode="HTML")

@DP.callback_query(F.data=="players")
async def players_callback(callback):
    await callback.answer()
    await players_command(callback.message)

@DP.callback_query(F.data=="check_sub")
async def check_sub_callback(callback):
    await callback.answer()
    if await check_access(callback.from_user.id):
        await callback.message.answer(
            "✅ <b>Подписка подтверждена!</b>\n\n"
            "Теперь можешь пользоваться ботом.",
            reply_markup=main_keyboard(callback.from_user),
            parse_mode="HTML")
    else:
        await callback.message.answer(
            "❌ Подписка не найдена.\n\n"
            "Подпишись на канал и нажми кнопку ещё раз.")

@DP.pre_checkout_query()
async def pre_checkout_query(query: PreCheckoutQuery):
    await query.answer(ok=True)

@DP.message(F.successful_payment)
async def successful_payment(message: Message):
    payment=message.successful_payment
    payload=payment.invoice_payload
    await register(message.from_user)

    if payload.startswith("lucky:"):
        expires=int(time.time())+LUCKY_HOURS*60*60
        async with aiosqlite.connect(DB) as db:
            await db.execute("""
                INSERT INTO lucky_charms(user_id,expires_at)
                VALUES(?,?)
                ON CONFLICT(user_id) DO UPDATE SET
                expires_at=excluded.expires_at
            """,(message.from_user.id,expires))
            await db.execute("""
                INSERT INTO payments(user_id,product,stars,created)
                VALUES(?,?,?,?)
            """,(message.from_user.id,"lucky_charm",
                payment.total_amount,int(time.time())))
            await db.commit()

        await message.answer(
            "🍀 <b>LUCKY CHARM АКТИВИРОВАН!</b>\n\n"
            "🔥 Повышенный шанс редких карт.\n"
            "⏳ Длительность: <b>24 часа</b>.",
            parse_mode="HTML")

async def main():
    await init_db()
    print("===================================")
    print("⚽ FOOTBALL DROP запущен")
    print(f"👑 OWNER: @{OWNER}")
    print("⏰ DROP COOLDOWN: 10 MINUTES")
    print("⚡ MINUTE DROP EVENT: ENABLED")
    print("🎯 EVENTS: ENABLED")
    print("🎟️ PROMO CREATOR: ENABLED")
    print("🔄 TRADE SYSTEM: ENABLED")
    print("📋 PLAYERS LIST: ENABLED")
    print("===================================")
    await DP.start_polling(
        BOT,
        allowed_updates=DP.resolve_used_update_types()
    )

if __name__=="__main__":
    asyncio.run(main())
