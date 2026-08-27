# main.py
# FOOTBALL DROP — ПОЛНАЯ ВЕРСИЯ
# Добавлено:
# - PvP против реальных людей (/battle @username)
# - Состав/ТОП-11 (/team)
# - AI-соперник (/ai_battle)
# - Прокачка карт (/upgrade_card ID)
# - Рынок между игроками (/marketplace, /sell_card ID цена)
# - Бан в owner-панели

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

DROP_COOLDOWN = 10 * 60
LUCKY_COST = 15
LUCKY_HOURS = 24
UPGRADE_COST = 100000
MAX_UPGRADE = 5

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
    # ===== COMMON =====
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

    # ===== RARE =====
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

    # ===== SUPER RARE =====
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

    # ===== EPIC =====
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

    # ===== LEGENDARY =====
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

    # ===== ICON =====
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

# =========================================================
# ИНИЦИАЛИЗАЦИЯ БД
# =========================================================
async def init_db():
    async with aiosqlite.connect(DB) as db:
        # Таблица пользователей
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
            banned INTEGER DEFAULT 0,
            battle_wins INTEGER DEFAULT 0,
            battle_losses INTEGER DEFAULT 0,
            battles_played INTEGER DEFAULT 0
        )""")

        # Таблица карт
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
            upgrade_level INTEGER DEFAULT 0,
            created_at INTEGER DEFAULT 0
        )""")

        # Таблица рынка (продажа боту)
        await db.execute("""
        CREATE TABLE IF NOT EXISTS market(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            seller_id INTEGER NOT NULL,
            card_id INTEGER NOT NULL,
            price INTEGER NOT NULL
        )""")

        # Таблица рынка между игроками
        await db.execute("""
        CREATE TABLE IF NOT EXISTS marketplace(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            seller_id INTEGER NOT NULL,
            card_id INTEGER NOT NULL,
            price INTEGER NOT NULL,
            created_at INTEGER NOT NULL,
            sold INTEGER DEFAULT 0
        )""")

        # Таблица покупок
        await db.execute("""
        CREATE TABLE IF NOT EXISTS payments(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            product TEXT NOT NULL,
            stars INTEGER NOT NULL,
            created INTEGER NOT NULL
        )""")

        # Таблица миссий
        await db.execute("""
        CREATE TABLE IF NOT EXISTS missions(
            user_id INTEGER PRIMARY KEY,
            drops INTEGER DEFAULT 0,
            cards INTEGER DEFAULT 0,
            claimed INTEGER DEFAULT 0
        )""")

        # Таблица промокодов
        await db.execute("""
        CREATE TABLE IF NOT EXISTS promo_codes(
            code TEXT PRIMARY KEY,
            coins INTEGER DEFAULT 0,
            stars INTEGER DEFAULT 0,
            activations INTEGER NOT NULL,
            used INTEGER DEFAULT 0,
            created INTEGER NOT NULL
        )""")

        # Таблица использований промокодов
        await db.execute("""
        CREATE TABLE IF NOT EXISTS promo_uses(
            code TEXT NOT NULL,
            user_id INTEGER NOT NULL,
            PRIMARY KEY(code,user_id)
        )""")

        # Таблица Lucky Charm
        await db.execute("""
        CREATE TABLE IF NOT EXISTS lucky_charms(
            user_id INTEGER PRIMARY KEY,
            expires_at INTEGER NOT NULL
        )""")

        # Таблица активных ивентов
        await db.execute("""
        CREATE TABLE IF NOT EXISTS active_event(
            id INTEGER PRIMARY KEY CHECK(id = 1),
            event_key TEXT NOT NULL,
            expires_at INTEGER NOT NULL,
            active INTEGER DEFAULT 1
        )""")

        # Таблица обменов
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

        # Таблица PvP боёв
        await db.execute("""
        CREATE TABLE IF NOT EXISTS battles(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            player1_id INTEGER NOT NULL,
            player2_id INTEGER NOT NULL,
            player1_score INTEGER DEFAULT 0,
            player2_score INTEGER DEFAULT 0,
            winner_id INTEGER DEFAULT 0,
            status TEXT DEFAULT 'waiting',
            bet_coins INTEGER DEFAULT 0,
            bet_card_id INTEGER DEFAULT 0,
            created_at INTEGER NOT NULL,
            finished_at INTEGER DEFAULT 0
        )""")

        await db.commit()

# =========================================================
# БАЗОВЫЕ ФУНКЦИИ
# =========================================================
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
        ("🏪 Marketplace","marketplace"),
        ("🎁 Daily","daily"),
        ("🎯 Задания","missions"),
        ("🏆 Рейтинг","top"),
        ("📦 Паки за 🪙","coinpacks"),
        ("⭐ Паки за Stars","packs"),
        ("🎟️ Промокод","promo"),
        ("🍀 Lucky Charm","lucky"),
        ("🔄 Обмен","trade_menu"),
        ("📋 Все игроки","players"),
        ("⚔️ PvP","pvp_menu"),
        ("🏆 Состав","team_menu"),
        ("🤖 AI Битва","ai_battle"),
        ("📈 Прокачка","upgrade_menu"),
    ]
    if user and is_owner(user):
        buttons.append(("👑 Owner","owner"))
    for text,data in buttons:
        kb.button(text=text,callback_data=data)
    kb.adjust(2)
    return kb.as_markup()

# =========================================================
# DROP
# =========================================================
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
# ОСНОВНЫЕ КОМАНДЫ
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
        f"🃏 Карт: <b>{cards}</b>\n"
        f"🏆 Побед PvP: <b>{user.get('battle_wins', 0)}</b>\n"
        f"💀 Поражений PvP: <b>{user.get('battle_losses', 0)}</b>\n\n"
        "⚽ DROP — раз в 10 минут\n"
        "📚 Коллекция — твои карты\n"
        "⚔️ PvP — сражайся с игроками\n"
        "🤖 AI Битва — сражайся с ботом\n"
        "🏆 Состав — собери ТОП-11\n"
        "📈 Прокачка — улучшай карты\n"
        "🏪 Marketplace — покупай/продавай",
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
        "🎁 <code>/daily</code> — Daily\n"
        "🎯 <code>/missions</code> — задания\n"
        "🏆 <code>/top</code> — рейтинг\n"
        "🎟️ <code>/promo CODE</code> — промокод\n"
        "🔄 <code>/trade @user</code> — обмен\n"
        "📋 <code>/players</code> — все игроки\n"
        "⚔️ <code>/battle @user</code> — PvP битва\n"
        "🤖 <code>/ai_battle</code> — битва с AI\n"
        "🏆 <code>/team</code> — ТОП-11 состав\n"
        "📈 <code>/upgrade_card ID</code> — прокачка (+1 = 100к)\n"
        "🏪 <code>/sell_card ID цена</code> — продать карту\n"
        "🏪 <code>/marketplace</code> — рынок\n"
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

# =========================================================
# КОЛЛЕКЦИЯ
# =========================================================
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
        upgrade = f" +{card['upgrade_level']}" if card.get('upgrade_level', 0) > 0 else ""
        text += (
            f"{i}. {RARITY_EMOJI.get(card['rarity'],'⚪')} "
            f"<b>{html.escape(card['name'])}</b>\n"
            f"   {card['nation']} {card['position']} | "
            f"⭐ {card['rating']}{upgrade}\n"
            f"   💰 €{card['price']:,}\n"
            f"   ID: <code>{card['id']}</code>\n\n"
        )

    kb = InlineKeyboardBuilder()
    kb.button(text="⚽ DROP",callback_data="drop")
    kb.button(text="🏪 Продать карты",callback_data="market")
    kb.button(text="🔄 Обмен",callback_data="trade_menu")
    kb.button(text="📈 Прокачать",callback_data="upgrade_menu")
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

# =========================================================
# ПРОФИЛЬ
# =========================================================
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
        f"⚔️ PvP Побед: <b>{u.get('battle_wins', 0)}</b>\n"
        f"⚔️ PvP Поражений: <b>{u.get('battle_losses', 0)}</b>\n"
        f"🍀 Lucky Charm: <b>{lucky}</b>",
        parse_mode="HTML")

@DP.message(Command("profile"))
async def profile_command(message):
    await show_profile(message)

# =========================================================
# МАГАЗИН
# =========================================================
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

# =========================================================
# LUCKY CHARM
# =========================================================
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

# =========================================================
# ПАКИ ЗА STARS
# =========================================================
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

# =========================================================
# ПАКИ ЗА МОНЕТЫ
# =========================================================
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

# =========================================================
# ПРОДАЖА КАРТ БОТУ
# =========================================================
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
        upgrade = f" +{card['upgrade_level']}" if card.get('upgrade_level', 0) > 0 else ""
        text += (
            f"{RARITY_EMOJI.get(card['rarity'],'⚪')} "
            f"<b>{html.escape(card['name'])}</b> — €{card['price']:,}{upgrade}\n")
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

# =========================================================
# ПРОКАЧКА КАРТ (НОВОЕ!)
# =========================================================
@DP.message(Command("upgrade_card"))
async def upgrade_card_command(message: Message):
    await register(message.from_user)
    if not await require_subscription(message):
        return
    
    parts = message.text.split()
    if len(parts) < 2:
        await message.answer(
            "📈 <b>ПРОКАЧКА КАРТЫ</b>\n\n"
            "<code>/upgrade_card ID</code> — прокачать карту\n\n"
            "Цена: <b>100 000 🪙</b> за +1 рейтинг\n"
            "Максимум: <b>+5</b> к рейтингу\n\n"
            "Чтобы узнать ID карты, используй <code>/collection</code>",
            parse_mode="HTML",
            reply_markup=main_keyboard(message.from_user)
        )
        return
    
    try:
        card_id = int(parts[1])
    except ValueError:
        await message.answer("❌ Введи правильный ID карты.")
        return
    
    async with aiosqlite.connect(DB) as db:
        db.row_factory = aiosqlite.Row
        cur = await db.execute(
            "SELECT * FROM cards WHERE id = ? AND user_id = ?",
            (card_id, message.from_user.id)
        )
        card = await cur.fetchone()
        
        if not card:
            await message.answer("❌ Карта не найдена или не принадлежит тебе.")
            return
        
        if card["upgrade_level"] >= MAX_UPGRADE:
            await message.answer(f"❌ Карта уже прокачана до максимума (+{MAX_UPGRADE}).")
            return
        
        if not await spend_coins(message.from_user.id, UPGRADE_COST):
            await message.answer(f"❌ Недостаточно монет. Нужно: <b>{UPGRADE_COST:,} 🪙</b>", parse_mode="HTML")
            return
        
        new_level = card["upgrade_level"] + 1
        new_rating = card["rating"] + 1
        new_price = card["price"] + int(card["price"] * 0.1)  # +10% к цене
        
        await db.execute(
            "UPDATE cards SET upgrade_level = ?, rating = ?, price = ? WHERE id = ?",
            (new_level, new_rating, new_price, card_id)
        )
        await db.commit()
    
    await message.answer(
        f"✅ <b>КАРТА ПРОКАЧАНА!</b>\n\n"
        f"👤 {html.escape(card['name'])}\n"
        f"⭐ Рейтинг: {card['rating']} → <b>{new_rating}</b>\n"
        f"📈 Уровень прокачки: <b>+{new_level}</b>\n"
        f"💰 Цена: €{card['price']:,} → <b>€{new_price:,}</b>\n"
        f"💵 Потрачено: <b>{UPGRADE_COST:,} 🪙</b>",
        parse_mode="HTML"
    )

@DP.callback_query(F.data == "upgrade_menu")
async def upgrade_menu_callback(callback: CallbackQuery):
    await callback.answer()
    await callback.message.answer(
        "📈 <b>ПРОКАЧКА КАРТ</b>\n\n"
        "Используй команду:\n"
        "<code>/upgrade_card ID</code>\n\n"
        "Цена: <b>100 000 🪙</b> за +1 рейтинг\n"
        "Максимум: <b>+5</b> к рейтингу\n\n"
        "Узнай ID карты в <code>/collection</code>",
        parse_mode="HTML",
        reply_markup=main_keyboard(callback.from_user)
    )

# =========================================================
# РЫНОК МЕЖДУ ИГРОКАМИ (НОВОЕ!)
# =========================================================
@DP.message(Command("sell_card"))
async def sell_card_command(message: Message):
    await register(message.from_user)
    if not await require_subscription(message):
        return
    
    parts = message.text.split()
    if len(parts) < 3:
        await message.answer(
            "🏪 <b>ПРОДАЖА КАРТЫ</b>\n\n"
            "<code>/sell_card ID ЦЕНА</code> — выставить карту на рынок\n\n"
            "Пример: <code>/sell_card 5 50000</code>\n\n"
            "Комиссия бота: <b>5%</b>",
            parse_mode="HTML"
        )
        return
    
    try:
        card_id = int(parts[1])
        price = int(parts[2])
        if price < 1000:
            await message.answer("❌ Минимальная цена: 1 000 монет.")
            return
    except ValueError:
        await message.answer("❌ Введи правильные данные.")
        return
    
    async with aiosqlite.connect(DB) as db:
        db.row_factory = aiosqlite.Row
        cur = await db.execute(
            "SELECT * FROM cards WHERE id = ? AND user_id = ?",
            (card_id, message.from_user.id)
        )
        card = await cur.fetchone()
        
        if not card:
            await message.answer("❌ Карта не найдена или не принадлежит тебе.")
            return
        
        # Проверяем, не выставлена ли уже карта
        cur2 = await db.execute(
            "SELECT 1 FROM marketplace WHERE card_id = ? AND sold = 0",
            (card_id,)
        )
        if await cur2.fetchone():
            await message.answer("❌ Карта уже выставлена на рынок.")
            return
        
        await db.execute(
            "INSERT INTO marketplace (seller_id, card_id, price, created_at) VALUES (?, ?, ?, ?)",
            (message.from_user.id, card_id, price, int(time.time()))
        )
        await db.commit()
    
    await message.answer(
        f"✅ <b>КАРТА ВЫСТАВЛЕНА НА РЫНОК!</b>\n\n"
        f"👤 {html.escape(card['name'])}\n"
        f"⭐ {card['rating']} OVR\n"
        f"💰 Цена: <b>{price:,} 🪙</b>\n"
        f"📊 Комиссия: <b>5%</b>\n\n"
        f"Используй <code>/marketplace</code> для просмотра",
        parse_mode="HTML"
    )

@DP.message(Command("marketplace"))
async def marketplace_command(message: Message):
    await register(message.from_user)
    if not await require_subscription(message):
        return
    
    async with aiosqlite.connect(DB) as db:
        db.row_factory = aiosqlite.Row
        cur = await db.execute("""
            SELECT m.*, c.name, c.rating, c.rarity, c.nation, c.position, c.upgrade_level
            FROM marketplace m
            JOIN cards c ON m.card_id = c.id
            WHERE m.sold = 0
            ORDER BY m.price ASC
            LIMIT 30
        """)
        listings = await cur.fetchall()
    
    if not listings:
        await message.answer(
            "🏪 <b>РЫНОК ПУСТ</b>\n\n"
            "Выставь свою карту: <code>/sell_card ID ЦЕНА</code>",
            parse_mode="HTML"
        )
        return
    
    text = "🏪 <b>РЫНОК КАРТ</b>\n\n"
    kb = InlineKeyboardBuilder()
    
    for listing in listings:
        upgrade = f" +{listing['upgrade_level']}" if listing['upgrade_level'] > 0 else ""
        text += (
            f"{RARITY_EMOJI.get(listing['rarity'], '⚪')} "
            f"<b>{html.escape(listing['name'])}</b>\n"
            f"   ⭐ {listing['rating']}{upgrade} | {listing['nation']} {listing['position']}\n"
            f"   💰 <b>{listing['price']:,} 🪙</b>\n\n"
        )
        kb.button(
            text=f"Купить {listing['name']} ({listing['price']:,}🪙)",
            callback_data=f"buy_card:{listing['id']}"
        )
    
    kb.button("⬅️ Назад", callback_data="back_menu")
    kb.adjust(1)
    
    await message.answer(text, reply_markup=kb.as_markup(), parse_mode="HTML")

@DP.callback_query(F.data.startswith("buy_card:"))
async def buy_card_callback(callback: CallbackQuery):
    await callback.answer()
    
    listing_id = int(callback.data.split(":")[1])
    
    async with aiosqlite.connect(DB) as db:
        db.row_factory = aiosqlite.Row
        cur = await db.execute("""
            SELECT m.*, c.user_id as card_owner, c.name, c.rating, c.rarity
            FROM marketplace m
            JOIN cards c ON m.card_id = c.id
            WHERE m.id = ? AND m.sold = 0
        """, (listing_id,))
        listing = await cur.fetchone()
        
        if not listing:
            await callback.message.answer("❌ Карта уже продана или не найдена.")
            return
        
        if listing["seller_id"] == callback.from_user.id:
            await callback.message.answer("❌ Нельзя купить свою карту.")
            return
        
        price = listing["price"]
        commission = int(price * 0.05)
        seller_gets = price - commission
        
        # Проверяем баланс покупателя
        buyer = await get_user(callback.from_user.id)
        if not buyer or buyer["coins"] < price:
            await callback.message.answer(f"❌ Недостаточно монет. Нужно: <b>{price:,} 🪙</b>", parse_mode="HTML")
            return
        
        # Переводим монеты
        await db.execute(
            "UPDATE users SET coins = coins - ? WHERE user_id = ?",
            (price, callback.from_user.id)
        )
        await db.execute(
            "UPDATE users SET coins = coins + ? WHERE user_id = ?",
            (seller_gets, listing["seller_id"])
        )
        
        # Меняем владельца карты
        await db.execute(
            "UPDATE cards SET user_id = ? WHERE id = ?",
            (callback.from_user.id, listing["card_id"])
        )
        
        # Отмечаем как проданное
        await db.execute(
            "UPDATE marketplace SET sold = 1 WHERE id = ?",
            (listing_id,)
        )
        await db.commit()
    
    await callback.message.edit_text(
        f"✅ <b>ПОКУПКА УСПЕШНА!</b>\n\n"
        f"👤 Карта: {html.escape(listing['name'])}\n"
        f"⭐ Рейтинг: {listing['rating']}\n"
        f"💰 Цена: <b>{price:,} 🪙</b>\n"
        f"📊 Комиссия бота: <b>{commission:,} 🪙</b>\n"
        f"💵 Продавец получил: <b>{seller_gets:,} 🪙</b>\n\n"
        f"Карта теперь в твоей коллекции!",
        parse_mode="HTML"
    )

# =========================================================
# КОМАНДА /players
# =========================================================
@DP.message(Command("players"))
async def players_command(message: Message):
    await register(message.from_user)
    if not await require_subscription(message):
        return
    
    sorted_players = sorted(PLAYERS, key=lambda x: x[3], reverse=True)
    
    text = "📋 <b>ВСЕ ИГРОКИ В ИГРЕ</b>\n\n"
    text += f"👥 Всего игроков: <b>{len(PLAYERS)}</b>\n\n"
    
    for rarity in RARITY_ORDER:
        players_in_rarity = [p for p in sorted_players if p[4] == rarity]
        if players_in_rarity:
            text += f"\n{RARITY_EMOJI.get(rarity, '')} <b>{rarity.upper()}</b> ({len(players_in_rarity)}):\n"
            for p in players_in_rarity[:10]:
                text += f"  • {p[1]} {p[0]} — {p[2]} (⭐{p[3]})\n"
            if len(players_in_rarity) > 10:
                text += f"  ... и ещё {len(players_in_rarity) - 10}\n"
    
    await message.answer(text, parse_mode="HTML", reply_markup=main_keyboard(message.from_user))

# =========================================================
# ОБМЕН (TRADE) - УЖЕ БЫЛО РАНЬШЕ
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
            "<code>/trade @username</code> — начать обмен\n"
            "<code>/trade_list</code> — список обменов",
            parse_mode="HTML",
            reply_markup=main_keyboard(message.from_user)
        )
        return
    
    target = parts[1]
    if target.startswith("@"):
        target = target[1:]
    
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
    
    await show_trade_selection(message.from_user.id, target_id, message.chat.id)

async def show_trade_selection(sender_id, receiver_id, chat_id):
    async with aiosqlite.connect(DB) as db:
        db.row_factory = aiosqlite.Row
        cur = await db.execute("""
            SELECT id, name, rating, rarity, nation, position, price, upgrade_level
            FROM cards 
            WHERE user_id = ?
            ORDER BY rating DESC
            LIMIT 20
        """, (sender_id,))
        sender_cards = await cur.fetchall()
        
        cur2 = await db.execute("""
            SELECT id, name, rating, rarity, nation, position, price, upgrade_level
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
        upgrade = f" +{card['upgrade_level']}" if card['upgrade_level'] > 0 else ""
        kb.button(
            text=f"{RARITY_EMOJI.get(card['rarity'], '')} {card['name']} (⭐{card['rating']}{upgrade})",
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
        
        cur2 = await db.execute("""
            SELECT id, name, rating, rarity, nation, position, price, upgrade_level
            FROM cards 
            WHERE user_id = ?
            ORDER BY rating DESC
            LIMIT 20
        """, (receiver_id,))
        receiver_cards = await cur2.fetchall()
    
    if not receiver_cards:
        await callback.message.answer("❌ У пользователя нет карт для обмена.")
        return
    
    upgrade = f" +{sender_card['upgrade_level']}" if sender_card['upgrade_level'] > 0 else ""
    text = "🔄 <b>ВЫБЕРИ КАРТУ ДЛЯ ОБМЕНА</b>\n\n"
    text += f"Твоя карта: {RARITY_EMOJI.get(sender_card['rarity'], '')} {sender_card['name']} (⭐{sender_card['rating']}{upgrade})\n\n"
    text += "Выбери карту, которую хочешь получить:"
    
    kb = InlineKeyboardBuilder()
    for card in receiver_cards:
        upgrade2 = f" +{card['upgrade_level']}" if card['upgrade_level'] > 0 else ""
        kb.button(
            text=f"{RARITY_EMOJI.get(card['rarity'], '')} {card['name']} (⭐{card['rating']}{upgrade2})",
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
    
    async with aiosqlite.connect(DB) as db:
        db.row_factory = aiosqlite.Row
        
        cur1 = await db.execute(
            "SELECT * FROM cards WHERE id = ? AND user_id = ?",
            (sender_card_id, callback.from_user.id)
        )
        sender_card = await cur1.fetchone()
        
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
        
        await db.execute("""
            INSERT INTO trades (sender_id, receiver_id, sender_card_id, receiver_card_id, created_at)
            VALUES (?, ?, ?, ?, ?)
        """, (callback.from_user.id, receiver_id, sender_card_id, receiver_card_id, int(time.time())))
        await db.commit()
        
        cur3 = await db.execute("SELECT username FROM users WHERE user_id = ?", (receiver_id,))
        receiver_user = await cur3.fetchone()
        receiver_name = receiver_user["username"] if receiver_user else str(receiver_id)
    
    trade_text = (
        f"🔄 <b>НОВЫЙ ЗАПРОС НА ОБМЕН!</b>\n\n"
        f"Пользователь {callback.from_user.first_name} предлагает обмен:\n\n"
        f"📤 Его карта: {RARITY_EMOJI.get(sender_card['rarity'], '')} {sender_card['name']} (⭐{sender_card['rating']})\n"
        f"📥 Твоя карта: {RARITY_EMOJI.get(receiver_card['rarity'], '')} {receiver_card['name']} (⭐{receiver_card['rating']})\n\n"
        f"Используй <code>/trade_list</code> чтобы принять или отклонить."
    )
    
    try:
        await BOT.send_message(receiver_id, trade_text, parse_mode="HTML")
    except Exception:
        pass
    
    await callback.message.answer(
        "✅ <b>ЗАПРОС НА ОБМЕН ОТПРАВЛЕН!</b>\n\n"
        f"Пользователь {receiver_name} получил уведомление.",
        parse_mode="HTML"
    )

@DP.message(Command("trade_list"))
async def trade_list_command(message: Message):
    await register(message.from_user)
    if not await require_subscription(message):
        return
    
    async with aiosqlite.connect(DB) as db:
        db.row_factory = aiosqlite.Row
        
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
    
    if incoming_trades:
        for trade in incoming_trades:
            sender = trade["sender_username"] or str(trade["sender_id"])
            text = (
                f"🔄 <b>ВХОДЯЩИЙ ЗАПРОС</b>\n\n"
                f"От: {sender}\n"
                f"📤 {RARITY_EMOJI.get(trade['sender_card_rarity'], '')} {trade['sender_card_name']} (⭐{trade['sender_card_rating']})\n"
                f"📥 {RARITY_EMOJI.get(trade['receiver_card_rarity'], '')} {trade['receiver_card_name']} (⭐{trade['receiver_card_rating']})\n"
            )
            
            kb = InlineKeyboardBuilder()
            kb.button(text="✅ Принять", callback_data=f"trade_accept:{trade['id']}")
            kb.button(text="❌ Отклонить", callback_data=f"trade_decline:{trade['id']}")
            kb.adjust(2)
            
            await message.answer(text, reply_markup=kb.as_markup(), parse_mode="HTML")
    
    if outgoing_trades:
        text = "📤 <b>ИСХОДЯЩИЕ ЗАПРОСЫ:</b>\n\n"
        for trade in outgoing_trades:
            text += (
                f"ID: {trade['id']}\n"
                f"📤 {RARITY_EMOJI.get(trade['sender_card_rarity'], '')} {trade['sender_card_name']} (⭐{trade['sender_card_rating']})\n"
                f"📥 {RARITY_EMOJI.get(trade['receiver_card_rarity'], '')} {trade['receiver_card_name']} (⭐{trade['receiver_card_rating']})\n"
                f"⏳ Ожидает ответа...\n\n"
            )
        await message.answer(text, parse_mode="HTML")

@DP.callback_query(F.data.startswith("trade_accept:"))
async def trade_accept_callback(callback: CallbackQuery):
    await callback.answer()
    
    trade_id = int(callback.data.split(":")[1])
    
    async with aiosqlite.connect(DB) as db:
        db.row_factory = aiosqlite.Row
        cur = await db.execute("SELECT * FROM trades WHERE id = ? AND receiver_id = ? AND status = 'pending'", 
                               (trade_id, callback.from_user.id))
        trade = await cur.fetchone()
        
        if not trade:
            await callback.message.answer("❌ Обмен не найден или уже обработан.")
            return
        
        cur1 = await db.execute("SELECT * FROM cards WHERE id = ?", (trade["sender_card_id"],))
        sender_card = await cur1.fetchone()
        
        cur2 = await db.execute("SELECT * FROM cards WHERE id = ?", (trade["receiver_card_id"],))
        receiver_card = await cur2.fetchone()
        
        if not sender_card or not receiver_card:
            await callback.message.answer("❌ Одна из карт уже не доступна.")
            await db.execute("UPDATE trades SET status = 'cancelled' WHERE id = ?", (trade_id,))
            await db.commit()
            return
        
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
        
        await db.execute("UPDATE cards SET user_id = ? WHERE id = ?", (trade["sender_id"], trade["receiver_card_id"]))
        await db.execute("UPDATE cards SET user_id = ? WHERE id = ?", (trade["receiver_id"], trade["sender_card_id"]))
        
        await db.execute("UPDATE trades SET status = 'completed' WHERE id = ?", (trade_id,))
        await db.commit()
    
    await callback.message.edit_text(
        "✅ <b>ОБМЕН УСПЕШНО ЗАВЕРШЁН!</b>\n\n"
        f"Ты получил: {RARITY_EMOJI.get(sender_card['rarity'], '')} {sender_card['name']} (⭐{sender_card['rating']})",
        parse_mode="HTML"
    )
    
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
        cur = await db.execute("SELECT * FROM trades WHERE id = ? AND receiver_id = ? AND status = 'pending'", 
                               (trade_id, callback.from_user.id))
        trade = await cur.fetchone()
        
        if not trade:
            await callback.message.answer("❌ Обмен не найден или уже обработан.")
            return
        
        await db.execute("UPDATE trades SET status = 'declined' WHERE id = ?", (trade_id,))
        await db.commit()
    
    await callback.message.edit_text("❌ <b>ОБМЕН ОТКЛОНЁН</b>", parse_mode="HTML")
    
    try:
        await BOT.send_message(
            trade["sender_id"],
            "❌ <b>ОБМЕН ОТКЛОНЁН</b>\n\nПользователь отклонил твой запрос.",
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
        "<code>/trade @username</code> — начать обмен\n"
        "<code>/trade_list</code> — список обменов",
        parse_mode="HTML",
        reply_markup=main_keyboard(callback.from_user)
    )

@DP.callback_query(F.data == "trade_cancel")
async def trade_cancel_callback(callback: CallbackQuery):
    await callback.answer()
    await callback.message.edit_text("❌ Обмен отменён.", reply_markup=main_keyboard(callback.from_user))

# =========================================================
# PVP ПРОТИВ РЕАЛЬНЫХ ИГРОКОВ (НОВОЕ!)
# =========================================================
@DP.message(Command("battle"))
async def battle_command(message: Message):
    await register(message.from_user)
    if not await require_subscription(message):
        return
    
    parts = message.text.split()
    if len(parts) < 2:
        await message.answer(
            "⚔️ <b>PVP БИТВА</b>\n\n"
            "<code>/battle @username</code> — вызвать на битву\n"
            "<code>/battle @username СТАВКА</code> — с ставкой монет\n\n"
            "Твой ТОП-11 будет автоматически выбран для битвы.\n"
            "Побеждает игрок с самым высоким общим рейтингом команды.",
            parse_mode="HTML"
        )
        return
    
    target = parts[1]
    if target.startswith("@"):
        target = target[1:]
    
    bet = 0
    if len(parts) >= 3:
        try:
            bet = int(parts[2])
            if bet < 1000:
                await message.answer("❌ Минимальная ставка: 1 000 монет.")
                return
        except ValueError:
            await message.answer("❌ Ставка должна быть числом.")
            return
    
    async with aiosqlite.connect(DB) as db:
        cur = await db.execute(
            "SELECT user_id, first_name, coins FROM users WHERE username LIKE ?",
            (f"%{target}%",)
        )
        user_row = await cur.fetchone()
        
        if not user_row:
            await message.answer("❌ Пользователь не найден.")
            return
        
        target_id = user_row[0]
        target_name = user_row[1]
        
        if target_id == message.from_user.id:
            await message.answer("❌ Нельзя биться с самим собой.")
            return
        
        # Проверяем, есть ли у обоих игроков карты
        cur1 = await db.execute("SELECT COUNT(*) FROM cards WHERE user_id = ?", (message.from_user.id,))
        my_cards = (await cur1.fetchone())[0]
        
        cur2 = await db.execute("SELECT COUNT(*) FROM cards WHERE user_id = ?", (target_id,))
        their_cards = (await cur2.fetchone())[0]
        
        if my_cards < 11:
            await message.answer("❌ У тебя должно быть минимум 11 карт для битвы.")
            return
        
        if their_cards < 11:
            await message.answer(f"❌ У {target_name} меньше 11 карт, битва невозможна.")
            return
        
        # Проверяем баланс для ставки
        if bet > 0:
            cur3 = await db.execute("SELECT coins FROM users WHERE user_id = ?", (message.from_user.id,))
            my_coins = (await cur3.fetchone())[0]
            
            cur4 = await db.execute("SELECT coins FROM users WHERE user_id = ?", (target_id,))
            their_coins = (await cur4.fetchone())[0]
            
            if my_coins < bet:
                await message.answer(f"❌ У тебя недостаточно монет для ставки. Нужно: <b>{bet:,} 🪙</b>", parse_mode="HTML")
                return
            
            if their_coins < bet:
                await message.answer(f"❌ У {target_name} недостаточно монет для ставки.", parse_mode="HTML")
                return
    
    # Создаём запрос на битву
    battle_id = int(time.time()) + random.randint(1000, 9999)
    
    text = (
        f"⚔️ <b>НОВЫЙ ВЫЗОВ НА БИТВУ!</b>\n\n"
        f"{message.from_user.first_name} вызывает тебя на битву!\n\n"
    )
    if bet > 0:
        text += f"💰 Ставка: <b>{bet:,} 🪙</b>\n\n"
    text += "Нажми на кнопку, чтобы принять вызов:"
    
    kb = InlineKeyboardBuilder()
    kb.button(text="⚔️ Принять бой", callback_data=f"accept_battle:{message.from_user.id}:{bet}:{battle_id}")
    kb.button(text="❌ Отклонить", callback_data=f"decline_battle:{message.from_user.id}:{battle_id}")
    kb.adjust(1)
    
    try:
        await BOT.send_message(target_id, text, reply_markup=kb.as_markup(), parse_mode="HTML")
        await message.answer(f"✅ Вызов отправлен {target_name}! Ожидай ответа.")
    except Exception:
        await message.answer("❌ Не удалось отправить вызов. Возможно, пользователь не в боте.")

@DP.callback_query(F.data.startswith("accept_battle:"))
async def accept_battle_callback(callback: CallbackQuery):
    await callback.answer()
    
    _, challenger_id, bet_str, battle_id = callback.data.split(":")
    challenger_id = int(challenger_id)
    bet = int(bet_str)
    battle_id = int(battle_id)
    
    # Получаем обе команды
    challenger_team = await get_best_team(challenger_id)
    defender_team = await get_best_team(callback.from_user.id)
    
    if not challenger_team or not defender_team:
        await callback.message.answer("❌ У одного из игроков недостаточно карт для битвы.")
        return
    
    # Рассчитываем общие рейтинги
    challenger_rating = sum(c["rating"] for c in challenger_team)
    defender_rating = sum(c["rating"] for c in defender_team)
    
    # Определяем победителя
    if challenger_rating > defender_rating:
        winner_id = challenger_id
        loser_id = callback.from_user.id
        winner_rating = challenger_rating
        loser_rating = defender_rating
    elif defender_rating > challenger_rating:
        winner_id = callback.from_user.id
        loser_id = challenger_id
        winner_rating = defender_rating
        loser_rating = challenger_rating
    else:
        # Ничья - побеждает тот, кто вызвал
        winner_id = challenger_id
        loser_id = callback.from_user.id
        winner_rating = challenger_rating
        loser_rating = defender_rating
    
    # Записываем битву в БД
    async with aiosqlite.connect(DB) as db:
        await db.execute("""
            INSERT INTO battles (player1_id, player2_id, player1_score, player2_score, winner_id, status, bet_coins, created_at, finished_at)
            VALUES (?, ?, ?, ?, ?, 'finished', ?, ?, ?)
        """, (challenger_id, callback.from_user.id, challenger_rating, defender_rating, winner_id, bet, int(time.time()), int(time.time())))
        
        # Обновляем статистику
        await db.execute("UPDATE users SET battle_wins = battle_wins + 1 WHERE user_id = ?", (winner_id,))
        await db.execute("UPDATE users SET battle_losses = battle_losses + 1 WHERE user_id = ?", (loser_id,))
        await db.execute("UPDATE users SET battles_played = battles_played + 1 WHERE user_id = ?", (challenger_id,))
        await db.execute("UPDATE users SET battles_played = battles_played + 1 WHERE user_id = ?", (callback.from_user.id,))
        
        # Переводим ставку
        if bet > 0:
            await db.execute("UPDATE users SET coins = coins - ? WHERE user_id = ?", (bet, loser_id))
            await db.execute("UPDATE users SET coins = coins + ? WHERE user_id = ?", (bet, winner_id))
        
        await db.commit()
    
    # Формируем сообщение о результате
    winner_name = callback.from_user.first_name if winner_id == callback.from_user.id else await get_username(challenger_id)
    loser_name = callback.from_user.first_name if loser_id == callback.from_user.id else await get_username(challenger_id)
    
    result_text = (
        f"⚔️ <b>РЕЗУЛЬТАТ БИТВЫ!</b>\n\n"
        f"🏆 <b>ПОБЕДИТЕЛЬ: {winner_name}</b>\n"
        f"⭐ Общий рейтинг: <b>{winner_rating}</b>\n\n"
        f"💀 {loser_name}\n"
        f"⭐ Общий рейтинг: <b>{loser_rating}</b>\n\n"
    )
    
    if bet > 0:
        result_text += f"💰 {winner_name} выиграл <b>{bet:,} 🪙</b>!\n"
    
    result_text += "\n<b>ТОП-3 лучших карт победителя:</b>\n"
    for i, card in enumerate(sorted(winner_team if winner_id == challenger_id else defender_team, key=lambda x: x["rating"], reverse=True)[:3], 1):
        upgrade = f" +{card['upgrade_level']}" if card.get('upgrade_level', 0) > 0 else ""
        result_text += f"{i}. {RARITY_EMOJI.get(card['rarity'], '⚪')} {card['name']} ⭐{card['rating']}{upgrade}\n"
    
    await callback.message.edit_text(result_text, parse_mode="HTML")
    
    # Отправляем результат второму игроку
    try:
        await BOT.send_message(challenger_id if challenger_id != callback.from_user.id else callback.from_user.id, result_text, parse_mode="HTML")
    except Exception:
        pass

@DP.callback_query(F.data.startswith("decline_battle:"))
async def decline_battle_callback(callback: CallbackQuery):
    await callback.answer()
    
    _, challenger_id, battle_id = callback.data.split(":")
    challenger_id = int(challenger_id)
    
    await callback.message.edit_text("❌ <b>ВЫЗОВ ОТКЛОНЁН</b>", parse_mode="HTML")
    
    try:
        await BOT.send_message(challenger_id, f"❌ {callback.from_user.first_name} отклонил твой вызов на битву.")
    except Exception:
        pass

async def get_best_team(user_id):
    """Получает ТОП-11 карт пользователя"""
    async with aiosqlite.connect(DB) as db:
        db.row_factory = aiosqlite.Row
        cur = await db.execute("""
            SELECT * FROM cards 
            WHERE user_id = ? 
            ORDER BY rating DESC 
            LIMIT 11
        """, (user_id,))
        return await cur.fetchall()

async def get_username(user_id):
    user = await get_user(user_id)
    return user["first_name"] if user else str(user_id)

@DP.callback_query(F.data == "pvp_menu")
async def pvp_menu_callback(callback: CallbackQuery):
    await callback.answer()
    await callback.message.answer(
        "⚔️ <b>PVP БИТВЫ</b>\n\n"
        "Команды:\n"
        "<code>/battle @username</code> — вызвать на битву\n"
        "<code>/battle @username СТАВКА</code> — с ставкой монет\n\n"
        "Твой ТОП-11 будет автоматически выбран.\n"
        "Побеждает игрок с самым высоким рейтингом команды.",
        parse_mode="HTML",
        reply_markup=main_keyboard(callback.from_user)
    )

# =========================================================
# AI СОПЕРНИК (НОВОЕ!)
# =========================================================
@DP.message(Command("ai_battle"))
async def ai_battle_command(message: Message):
    await register(message.from_user)
    if not await require_subscription(message):
        return
    
    # Проверяем наличие карт
    cards = await get_best_team(message.from_user.id)
    if len(cards) < 11:
        await message.answer("❌ У тебя должно быть минимум 11 карт для битвы с AI.")
        return
    
    # Генерируем AI команду
    ai_team = []
    for _ in range(11):
        player = random.choice(PLAYERS)
        ai_team.append({
            "name": player[0],
            "rating": player[3],
            "rarity": player[4],
            "nation": player[1],
            "position": player[2],
            "upgrade_level": random.randint(0, 2)  # AI может иметь прокачку
        })
    
    # Рассчитываем рейтинги
    player_rating = sum(c["rating"] + c.get("upgrade_level", 0) for c in cards)
    ai_rating = sum(c["rating"] + c["upgrade_level"] for c in ai_team)
    
    # Сложность AI (рандом)
    difficulty = random.choice(["Легкий", "Средний", "Сложный"])
    if difficulty == "Легкий":
        ai_rating = int(ai_rating * 0.8)
    elif difficulty == "Сложный":
        ai_rating = int(ai_rating * 1.2)
    
    # Определяем победителя
    if player_rating > ai_rating:
        result = "🏆 <b>ТЫ ПОБЕДИЛ!</b> 🎉"
        reward = random.randint(5000, 20000)
        await add_coins(message.from_user.id, reward)
        await mission_update(message.from_user.id, "drops", 2)
        reward_text = f"\n💰 Награда: <b>+{reward:,} 🪙</b>"
    elif ai_rating > player_rating:
        result = "💀 <b>ТЫ ПРОИГРАЛ</b> 😢"
        reward_text = ""
    else:
        result = "🤝 <b>НИЧЬЯ!</b>"
        reward = random.randint(1000, 5000)
        await add_coins(message.from_user.id, reward)
        reward_text = f"\n💰 Утешительный приз: <b>+{reward:,} 🪙</b>"
    
    text = (
        f"🤖 <b>БИТВА С AI</b>\n\n"
        f"Сложность: <b>{difficulty}</b>\n\n"
        f"👤 Твой рейтинг: <b>{player_rating}</b>\n"
        f"🤖 AI рейтинг: <b>{ai_rating}</b>\n\n"
        f"{result}{reward_text}\n\n"
        f"<b>Твои лучшие 3 карты:</b>\n"
    )
    
    for i, card in enumerate(sorted(cards, key=lambda x: x["rating"], reverse=True)[:3], 1):
        upgrade = f" +{card['upgrade_level']}" if card.get('upgrade_level', 0) > 0 else ""
        text += f"{i}. {RARITY_EMOJI.get(card['rarity'], '⚪')} {card['name']} ⭐{card['rating']}{upgrade}\n"
    
    await message.answer(text, parse_mode="HTML", reply_markup=main_keyboard(message.from_user))

@DP.callback_query(F.data == "ai_battle")
async def ai_battle_callback(callback: CallbackQuery):
    await callback.answer()
    await ai_battle_command(callback.message)

# =========================================================
# СОСТАВ/ТОП-11 (НОВОЕ!)
# =========================================================
@DP.message(Command("team"))
async def team_command(message: Message):
    await register(message.from_user)
    if not await require_subscription(message):
        return
    
    cards = await get_best_team(message.from_user.id)
    
    if len(cards) < 11:
        await message.answer(
            "🏆 <b>ТВОЙ СОСТАВ</b>\n\n"
            f"У тебя только <b>{len(cards)}</b> карт из 11.\n"
            "Собери больше карт, чтобы собрать ТОП-11!",
            parse_mode="HTML"
        )
        return
    
    total_rating = sum(c["rating"] + c.get("upgrade_level", 0) for c in cards)
    
    # Группировка по позициям
    positions = {
        "GK": [],
        "LB": [], "RB": [], "CB": [], "LWB": [], "RWB": [],
        "CDM": [], "CM": [], "CAM": [], "LM": [], "RM": [],
        "LW": [], "RW": [], "ST": [], "CF": []
    }
    
    for card in cards:
        pos = card["position"]
        if pos in positions:
            positions[pos].append(card)
        else:
            if pos in ["LW", "RW", "ST", "CF"]:
                positions["ST"].append(card)
            elif pos in ["LM", "RM"]:
                positions["CM"].append(card)
            elif pos in ["LB", "RB", "CB", "LWB", "RWB"]:
                positions["DEF"].append(card) if "DEF" not in positions else positions["DEF"].append(card)
    
    text = "🏆 <b>ТВОЙ ТОП-11 СОСТАВ</b>\n\n"
    text += f"⭐ Общий рейтинг: <b>{total_rating}</b>\n"
    text += f"🃏 Карт в составе: <b>{len(cards)}</b>\n\n"
    
    text += "<b>📋 СОСТАВ:</b>\n"
    
    # GK
    gks = [c for c in cards if c["position"] == "GK"]
    if gks:
        gk = gks[0]
        upgrade = f" +{gk['upgrade_level']}" if gk.get('upgrade_level', 0) > 0 else ""
        text += f"🧤 GK: {gk['name']} (⭐{gk['rating']}{upgrade})\n"
    
    # DEF
    defs = [c for c in cards if c["position"] in ["LB", "RB", "CB", "LWB", "RWB"]]
    for i, d in enumerate(defs[:4], 1):
        upgrade = f" +{d['upgrade_level']}" if d.get('upgrade_level', 0) > 0 else ""
        text += f"🛡️ DEF{i}: {d['name']} (⭐{d['rating']}{upgrade})\n"
    
    # MID
    mids = [c for c in cards if c["position"] in ["CDM", "CM", "CAM", "LM", "RM"]]
    for i, m in enumerate(mids[:4], 1):
        upgrade = f" +{m['upgrade_level']}" if m.get('upgrade_level', 0) > 0 else ""
        text += f"⚡ MID{i}: {m['name']} (⭐{m['rating']}{upgrade})\n"
    
    # FWD
    fwds = [c for c in cards if c["position"] in ["LW", "RW", "ST", "CF"]]
    for i, f in enumerate(fwds[:2], 1):
        upgrade = f" +{f['upgrade_level']}" if f.get('upgrade_level', 0) > 0 else ""
        text += f"⚽ FWD{i}: {f['name']} (⭐{f['rating']}{upgrade})\n"
    
    await message.answer(text, parse_mode="HTML", reply_markup=main_keyboard(message.from_user))

@DP.callback_query(F.data == "team_menu")
async def team_menu_callback(callback: CallbackQuery):
    await callback.answer()
    await team_command(callback.message)

# =========================================================
# ОСТАЛЬНЫЕ КОМАНДЫ
# =========================================================
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
    text="🏆 <b>ТОП 10 ПО МОНЕТАМ</b>\n\n"
    for i,row in enumerate(rows,1):
        name=row[1] or row[2] or "Игрок"
        text += f"{i}. <b>{html.escape(name)}</b> — {row[3]:,} 🪙\n"
    
    # ТОП по PvP победам
    cur2=await db.execute("""
        SELECT user_id,username,first_name,battle_wins FROM users
        WHERE banned=0 ORDER BY battle_wins DESC LIMIT 5
    """)
    pvp_rows=await cur2.fetchall()
    
    if pvp_rows and pvp_rows[0]["battle_wins"] > 0:
        text += "\n⚔️ <b>ТОП ПО PVP ПОБЕДАМ</b>\n"
        for i,row in enumerate(pvp_rows,1):
            name=row[1] or row[2] or "Игрок"
            text += f"{i}. <b>{html.escape(name)}</b> — {row[3]} побед\n"
    
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

# =========================================================
# OWNER ПАНЕЛЬ (С БАНОМ!)
# =========================================================
def owner_keyboard():
    kb=InlineKeyboardBuilder()
    kb.button(text="🎉 Ивенты",callback_data="event_menu")
    kb.button(text="📊 Статистика",callback_data="owner_stats")
    kb.button(text="🎟️ Создать промокод",callback_data="owner_promo_help")
    kb.button(text="📡 Активный ивент",callback_data="owner_events")
    kb.button(text="🚫 Забанить пользователя",callback_data="owner_ban")
    kb.button(text="✅ Разбанить пользователя",callback_data="owner_unban")
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
        "🎟️ Промокоды — создание промокодов.\n"
        "🚫 Бан — заблокировать пользователя.\n"
        "✅ Разбан — разблокировать пользователя.\n\n"
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

# =========================================================
# БАН В OWNER ПАНЕЛИ (НОВОЕ!)
# =========================================================
@DP.callback_query(F.data=="owner_ban")
async def owner_ban_callback(callback: CallbackQuery):
    await callback.answer()
    if not is_owner(callback.from_user):
        return
    await callback.message.answer(
        "🚫 <b>ЗАБАНИТЬ ПОЛЬЗОВАТЕЛЯ</b>\n\n"
        "Введи ID пользователя:\n\n"
        "Пример: <code>123456789</code>\n\n"
        "Или используй команду: <code>/ban USER_ID</code>",
        parse_mode="HTML"
    )

@DP.callback_query(F.data=="owner_unban")
async def owner_unban_callback(callback: CallbackQuery):
    await callback.answer()
    if not is_owner(callback.from_user):
        return
    await callback.message.answer(
        "✅ <b>РАЗБАНИТЬ ПОЛЬЗОВАТЕЛЯ</b>\n\n"
        "Введи ID пользователя:\n\n"
        "Пример: <code>123456789</code>\n\n"
        "Или используй команду: <code>/unban USER_ID</code>",
        parse_mode="HTML"
    )

@DP.message(Command("ban"))
async def ban_command(message):
    if not is_owner(message.from_user):
        return
    parts=message.text.split()
    if len(parts)!=2:
        await message.answer("❌ Использование: <code>/ban USER_ID</code>", parse_mode="HTML")
        return
    try:
        user_id=int(parts[1])
    except ValueError:
        await message.answer("❌ Неверный ID.")
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
        await message.answer("❌ Использование: <code>/unban USER_ID</code>", parse_mode="HTML")
        return
    try:
        user_id=int(parts[1])
    except ValueError:
        await message.answer("❌ Неверный ID.")
        return
    async with aiosqlite.connect(DB) as db:
        await db.execute(
            "UPDATE users SET banned=0 WHERE user_id=?",(user_id,))
        await db.commit()
    await message.answer(
        f"✅ Пользователь <code>{user_id}</code> разблокирован.",
        parse_mode="HTML")

# =========================================================
# ИВЕНТЫ
# =========================================================
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
        cur=await db.execute("SELECT SUM(battle_wins) FROM users")
        total_battles=(await cur.fetchone())[0] or 0
    await message.answer(
        "👑 <b>СТАТИСТИКА</b>\n\n"
        f"👥 Пользователей: <b>{users}</b>\n"
        f"🃏 Карт: <b>{cards}</b>\n"
        f"🪙 Монет в системе: <b>{coins:,}</b>\n"
        f"⚔️ Всего PvP битв: <b>{total_battles}</b>",
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

# =========================================================
# PAYMENTS
# =========================================================
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

# =========================================================
# CALLBACKS
# =========================================================
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

@DP.callback_query(F.data=="marketplace")
async def marketplace_callback(callback):
    await callback.answer()
    await marketplace_command(callback.message)

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

@DP.callback_query(F.data=="back_menu")
async def back_menu_callback(callback: CallbackQuery):
    await callback.answer()
    await callback.message.edit_text(
        "Главное меню",
        reply_markup=main_keyboard(callback.from_user)
    )

# =========================================================
# MAIN
# =========================================================
async def main():
    await init_db()
    print("===================================")
    print("⚽ FOOTBALL DROP — ПОЛНАЯ ВЕРСИЯ")
    print(f"👑 OWNER: @{OWNER}")
    print("⏰ DROP COOLDOWN: 10 MINUTES")
    print("⚔️ PVP: ENABLED")
    print("🤖 AI BATTLE: ENABLED")
    print("🏆 TEAM/TOP-11: ENABLED")
    print("📈 UPGRADE CARDS: ENABLED")
    print("🏪 MARKETPLACE: ENABLED")
    print("🔄 TRADE SYSTEM: ENABLED")
    print("👑 OWNER BAN: ENABLED")
    print("===================================")
    await DP.start_polling(
        BOT,
        allowed_updates=DP.resolve_used_update_types()
    )

if __name__=="__main__":
    asyncio.run(main())
