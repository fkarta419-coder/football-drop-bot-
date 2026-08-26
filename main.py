import os
import time
import random
import asyncio
import html
from datetime import datetime, timezone, timedelta

import aiosqlite
from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery, LabeledPrice, PreCheckoutQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder


# =========================================================
# CONFIG
# =========================================================

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

if not TOKEN:
    raise RuntimeError("TELEGRAM_BOT_TOKEN is not set")

BOT = Bot(token=TOKEN)
DP = Dispatcher()

DB = "football_drop.db"
OWNER = "foqlu"

DROP_COOLDOWN = 60 * 60


# =========================================================
# RARITIES
# =========================================================

RARITIES = {
    "Common": 68,
    "Rare": 22,
    "Super Rare": 7,
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


# =========================================================
# PLAYERS
# name, nation, position, rating, rarity, coin_price
# =========================================================

PLAYERS = [
    # COMMON
    ("Фран Гарсия", "🇪🇸", "LB", 78, "Common", 5000),
    ("Браим Диас", "🇪🇸", "RW", 79, "Common", 6000),
    ("Арда Гюлер", "🇹🇷", "CAM", 79, "Common", 6500),
    ("Эндрик", "🇧🇷", "ST", 78, "Common", 5000),
    ("Жоау Феликс", "🇵🇹", "SS", 78, "Common", 5500),
    ("Джек Грилиш", "🏴", "LW", 79, "Common", 6500),
    ("Ришарлисон", "🇧🇷", "ST", 79, "Common", 6000),
    ("Габриэл Жезус", "🇧🇷", "ST", 79, "Common", 6000),
    ("Федерико Кьеза", "🇮🇹", "RW", 79, "Common", 6500),
    ("Антони", "🇧🇷", "RW", 77, "Common", 4500),

    # RARE
    ("Кобби Майну", "🏴", "CM", 81, "Rare", 10000),
    ("Кристиан Пулишич", "🇺🇸", "LW", 82, "Rare", 12000),
    ("Нико Уильямс", "🇪🇸", "LW", 83, "Rare", 15000),
    ("Душан Влахович", "🇷🇸", "ST", 83, "Rare", 15000),
    ("Рафаэл Леау", "🇵🇹", "LW", 84, "Rare", 18000),
    ("Федерико Вальверде", "🇺🇾", "CM", 84, "Rare", 19000),
    ("Энцо Фернандес", "🇦🇷", "CM", 83, "Rare", 16000),
    ("Дани Ольмо", "🇪🇸", "CAM", 84, "Rare", 18000),
    ("Жюль Кунде", "🇫🇷", "CB", 84, "Rare", 18000),
    ("Рональд Араухо", "🇺🇾", "CB", 84, "Rare", 19000),
    ("Камавинга", "🇫🇷", "CM", 84, "Rare", 19000),
    ("Тчуамени", "🇫🇷", "CDM", 83, "Rare", 16000),

    # SUPER RARE
    ("Педри", "🇪🇸", "CM", 86, "Super Rare", 25000),
    ("Гави", "🇪🇸", "CM", 85, "Super Rare", 23000),
    ("Майкл Олисе", "🇫🇷", "RW", 86, "Super Rare", 27000),
    ("Коул Палмер", "🏴", "CAM", 87, "Super Rare", 30000),
    ("Флориан Вирц", "🇩🇪", "CAM", 87, "Super Rare", 30000),
    ("Лаутаро Мартинес", "🇦🇷", "ST", 87, "Super Rare", 30000),
    ("Сон Хын Мин", "🇰🇷", "LW", 87, "Super Rare", 32000),
    ("Кварацхелия", "🇬🇪", "LW", 86, "Super Rare", 27000),
    ("Трент Александер-Арнольд", "🏴", "RB", 86, "Super Rare", 26000),
    ("Тео Эрнандес", "🇫🇷", "LB", 87, "Super Rare", 30000),

    # EPIC
    ("Ламин Ямаль", "🇪🇸", "RW", 89, "Epic", 45000),
    ("Рафинья", "🇧🇷", "LW", 90, "Epic", 50000),
    ("Винисиус Жуниор", "🇧🇷", "LW", 91, "Epic", 60000),
    ("Родри", "🇪🇸", "CDM", 90, "Epic", 50000),
    ("Бернарду Силва", "🇵🇹", "CAM", 88, "Epic", 43000),
    ("Фил Фоден", "🏴", "RW", 88, "Epic", 43000),
    ("Кевин Де Брёйне", "🇧🇪", "CAM", 89, "Epic", 48000),
    ("Салиба", "🇫🇷", "CB", 88, "Epic", 40000),
    ("Рюдигер", "🇩🇪", "CB", 88, "Epic", 40000),
    ("Хакими", "🇲🇦", "RB", 88, "Epic", 43000),
    ("Гарри Кейн", "🏴", "ST", 90, "Epic", 52000),
    ("Левандовски", "🇵🇱", "ST", 89, "Epic", 48000),

    # LEGENDARY
    ("Килиан Мбаппе", "🇫🇷", "ST", 92, "Legendary", 85000),
    ("Эрлинг Холанд", "🇳🇴", "ST", 91, "Legendary", 80000),
    ("Мохамед Салах", "🇪🇬", "RW", 90, "Legendary", 70000),
    ("Джуд Беллингем", "🏴", "CAM", 90, "Legendary", 75000),
    ("Неймар", "🇧🇷", "LW", 91, "Legendary", 90000),
    ("Антуан Гризманн", "🇫🇷", "CF", 89, "Legendary", 70000),
    ("Тибо Куртуа", "🇧🇪", "GK", 90, "Legendary", 70000),
    ("Алиссон", "🇧🇷", "GK", 89, "Legendary", 65000),
    ("Ван Дейк", "🇳🇱", "CB", 89, "Legendary", 65000),

    # ICON
    ("Лионель Месси", "🇦🇷", "RW", 95, "Icon", 150000),
    ("Криштиану Роналду", "🇵🇹", "ST", 94, "Icon", 140000),
    ("Роналдиньо", "🇧🇷", "LW", 96, "Icon", 220000),
    ("Зинедин Зидан", "🇫🇷", "CAM", 97, "Icon", 250000),
    ("Роналдо Назарио", "🇧🇷", "ST", 97, "Icon", 250000),
    ("Пеле", "🇧🇷", "ST", 98, "Icon", 350000),
    ("Марадона", "🇦🇷", "CAM", 97, "Icon", 300000),
    ("Кройфф", "🇳🇱", "CF", 96, "Icon", 230000),
    ("Мальдини", "🇮🇹", "CB", 96, "Icon", 230000),
    ("Кака", "🇧🇷", "CAM", 95, "Icon", 200000),
    ("Тьерри Анри", "🇫🇷", "ST", 96, "Icon", 220000),
    ("Иньеста", "🇪🇸", "CM", 96, "Icon", 220000),

    # ULTIMATE
    ("Месси Ultimate", "🇦🇷", "RW", 99, "Ultimate", 500000),
    ("Роналду Ultimate", "🇵🇹", "ST", 99, "Ultimate", 500000),
    ("Пеле Ultimate", "🇧🇷", "ST", 99, "Ultimate", 500000),
    ("Марадона Ultimate", "🇦🇷", "CAM", 99, "Ultimate", 500000),
]


# =========================================================
# STARS PRODUCTS
# =========================================================

STAR_PACKS = {
    "basic": (10, 1, "🥉 Basic Pack"),
    "pro": (25, 3, "🥈 Pro Pack"),
    "elite": (50, 6, "🥇 Elite Pack"),
    "legend": (100, 12, "💎 Legendary Pack"),
    "icon": (250, 20, "🔥 Icon Pack"),
    "ultimate": (500, 35, "🌈 Ultimate Pack"),
}

STAR_PLAYERS = [
    ("Мбаппе Premium", "🇫🇷", "ST", 94, "Premium", 125),
    ("Винисиус Premium", "🇧🇷", "LW", 94, "Premium", 125),
    ("Месси Premium", "🇦🇷", "RW", 96, "Premium", 250),
    ("Роналду Premium", "🇵🇹", "ST", 96, "Premium", 250),
    ("Роналдиньо Premium", "🇧🇷", "LW", 97, "Premium", 300),
]


# =========================================================
# DATABASE
# =========================================================

async def init_db():
    async with aiosqlite.connect(DB) as db:

        await db.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            username TEXT DEFAULT '',
            first_name TEXT DEFAULT '',
            coins INTEGER DEFAULT 0,
            last_drop INTEGER DEFAULT 0,
            daily_date TEXT DEFAULT '',
            daily_streak INTEGER DEFAULT 0,
            wins INTEGER DEFAULT 0,
            losses INTEGER DEFAULT 0
        )
        """)

        await db.execute("""
        CREATE TABLE IF NOT EXISTS cards (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            name TEXT NOT NULL,
            nation TEXT NOT NULL,
            position TEXT NOT NULL,
            rating INTEGER NOT NULL,
            rarity TEXT NOT NULL,
            price INTEGER NOT NULL
        )
        """)

        await db.execute("""
        CREATE TABLE IF NOT EXISTS market (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            seller_id INTEGER NOT NULL,
            card_id INTEGER NOT NULL,
            price INTEGER NOT NULL
        )
        """)

        await db.execute("""
        CREATE TABLE IF NOT EXISTS payments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            product TEXT NOT NULL,
            stars INTEGER NOT NULL,
            created INTEGER NOT NULL
        )
        """)

        await db.execute("""
        CREATE TABLE IF NOT EXISTS missions (
            user_id INTEGER PRIMARY KEY,
            drops INTEGER DEFAULT 0,
            matches INTEGER DEFAULT 0,
            cards INTEGER DEFAULT 0,
            claimed INTEGER DEFAULT 0
        )
        """)

        await db.commit()


async def register(user):
    async with aiosqlite.connect(DB) as db:
        await db.execute("""
        INSERT OR IGNORE INTO users
        (user_id, username, first_name)
        VALUES (?, ?, ?)
        """, (
            user.id,
            user.username or "",
            user.first_name or ""
        ))

        await db.execute("""
        UPDATE users
        SET username=?, first_name=?
        WHERE user_id=?
        """, (
            user.username or "",
            user.first_name or "",
            user.id
        ))

        await db.execute("""
        INSERT OR IGNORE INTO missions(user_id)
        VALUES(?)
        """, (user.id,))

        await db.commit()


async def get_user(user_id):
    async with aiosqlite.connect(DB) as db:
        db.row_factory = aiosqlite.Row
        cur = await db.execute(
            "SELECT * FROM users WHERE user_id=?",
            (user_id,)
        )
        return await cur.fetchone()


async def count_cards(user_id):
    async with aiosqlite.connect(DB) as db:
        cur = await db.execute(
            "SELECT COUNT(*) FROM cards WHERE user_id=?",
            (user_id,)
        )
        return (await cur.fetchone())[0]


async def add_coins(user_id, amount):
    async with aiosqlite.connect(DB) as db:
        await db.execute(
            "UPDATE users SET coins=coins+? WHERE user_id=?",
            (amount, user_id)
        )
        await db.commit()


async def spend_coins(user_id, amount):
    async with aiosqlite.connect(DB) as db:
        cur = await db.execute(
            "SELECT coins FROM users WHERE user_id=?",
            (user_id,)
        )
        row = await cur.fetchone()

        if not row or row[0] < amount:
            return False

        await db.execute(
            "UPDATE users SET coins=coins-? WHERE user_id=?",
            (amount, user_id)
        )

        await db.commit()
        return True


async def add_card(user_id, player):
    async with aiosqlite.connect(DB) as db:
        await db.execute("""
        INSERT INTO cards
        (user_id, name, nation, position, rating, rarity, price)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            user_id,
            player[0],
            player[1],
            player[2],
            player[3],
            player[4],
            player[5]
        ))
        await db.commit()


async def mission_update(user_id, field):
    async with aiosqlite.connect(DB) as db:
        await db.execute(
            f"UPDATE missions SET {field}={field}+1 WHERE user_id=?",
            (user_id,)
        )
        await db.commit()


# =========================================================
# HELPERS
# =========================================================

def owner(user):
    return (user.username or "").lower() == OWNER.lower()


def choose_rarity():
    names = list(RARITIES.keys())
    weights = list(RARITIES.values())
    return random.choices(names, weights=weights, k=1)[0]


def random_player():
    rarity = choose_rarity()
    pool = [p for p in PLAYERS if p[4] == rarity]

    if not pool:
        pool = [p for p in PLAYERS if p[4] == "Common"]

    return random.choice(pool)


def main_keyboard():
    kb = InlineKeyboardBuilder()

    kb.button(text="🃏 DROP", callback_data="drop")
    kb.button(text="📚 Коллекция", callback_data="collection")
    kb.button(text="👤 Профиль", callback_data="profile")
    kb.button(text="🛒 Магазин", callback_data="shop")
    kb.button(text="🏪 Рынок", callback_data="market")
    kb.button(text="🎁 Daily", callback_data="daily")
    kb.button(text="🎯 Задания", callback_data="missions")
    kb.button(text="🏆 Рейтинг", callback_data="top")

    kb.adjust(2)

    return kb.as_markup()


# =========================================================
# START
# =========================================================

@DP.message(Command("start"))
async def start(message: Message):
    await register(message.from_user)

    user = await get_user(message.from_user.id)
    cards = await count_cards(message.from_user.id)

    await message.answer(
        f"⚽ <b>FOOTBALL DROP</b>\n\n"
        f"Привет, <b>{html.escape(message.from_user.first_name)}</b>!\n\n"
        f"🪙 Монеты: <b>{user['coins']:,}</b>\n"
        f"🃏 Карт: <b>{cards}</b>\n\n"
        f"🃏 /drop — получить карту\n"
        f"🛒 /shop — купить игрока\n"
        f"⭐ /packs — паки за Stars\n"
        f"🏪 /market — рынок\n"
        f"🎁 /daily — ежедневная награда\n\n"
        f"Редкие карты выпадают очень редко.",
        reply_markup=main_keyboard(),
        parse_mode="HTML"
    )


# =========================================================
# DROP
# =========================================================

async def do_drop(message: Message):
    await register(message.from_user)

    user_id = message.from_user.id
    user = await get_user(user_id)

    now = int(time.time())

    if not owner(message.from_user):
        remaining = DROP_COOLDOWN - (now - user["last_drop"])

        if remaining > 0:
            minutes = remaining // 60
            seconds = remaining % 60

            await message.answer(
                f"⏳ Следующий DROP через "
                f"<b>{minutes} мин. {seconds} сек.</b>",
                parse_mode="HTML"
            )
            return

    async with aiosqlite.connect(DB) as db:
        await db.execute(
            "UPDATE users SET last_drop=? WHERE user_id=?",
            (now, user_id)
        )
        await db.commit()

    coins = random.randint(100, 400)
    await add_coins(user_id, coins)
    await mission_update(user_id, "drops")

    await message.answer("📦 <b>ПАК ОТКРЫВАЕТСЯ...</b>", parse_mode="HTML")
    await asyncio.sleep(1)

    await message.answer("🃏 <b>РАСКРЫВАЕМ...</b>", parse_mode="HTML")
    await asyncio.sleep(1)

    player = random_player()
    await add_card(user_id, player)
    await mission_update(user_id, "cards")

    name, nation, position, rating, rarity, price = player

    await message.answer(
        f"{RARITY_EMOJI[rarity]} "
        f"<b>{rarity.upper()}</b>\n\n"
        f"{nation} <b>{html.escape(name)}</b>\n"
        f"⚡ Позиция: <b>{position}</b>\n"
        f"⭐ Рейтинг: <b>{rating}</b>\n"
        f"💰 Цена: <b>{price:,} 🪙</b>\n\n"
        f"🪙 Бонус за DROP: +{coins}\n\n"
        f"📚 Карта добавлена в коллекцию!",
        parse_mode="HTML"
    )


@DP.message(Command("drop"))
async def drop(message: Message):
    await do_drop(message)


# =========================================================
# PROFILE
# =========================================================

@DP.message(Command("profile"))
async def profile(message: Message):
    await register(message.from_user)

    user = await get_user(message.from_user.id)
    cards = await count_cards(message.from_user.id)

    await message.answer(
        f"👤 <b>ПРОФИЛЬ</b>\n\n"
        f"👤 {html.escape(message.from_user.first_name)}\n"
        f"🪙 Монеты: <b>{user['coins']:,}</b>\n"
        f"🃏 Карт: <b>{cards}</b>\n"
        f"🏆 Побед: <b>{user['wins']}</b>\n"
        f"💀 Поражений: <b>{user['losses']}</b>",
        parse_mode="HTML"
    )


# =========================================================
# COLLECTION
# =========================================================

@DP.message(Command("collection"))
async def collection(message: Message):
    await register(message.from_user)

    async with aiosqlite.connect(DB) as db:
        cur = await db.execute("""
        SELECT id, name, nation, position, rating, rarity
        FROM cards
        WHERE user_id=?
        ORDER BY rating DESC
        LIMIT 50
        """, (message.from_user.id,))

        cards = await cur.fetchall()

    if not cards:
        await message.answer(
            "📚 Коллекция пустая.\n\nИспользуй /drop."
        )
        return

    text = "📚 <b>КОЛЛЕКЦИЯ</b>\n\n"

    for card in cards:
        text += (
            f"ID <code>{card[0]}</code> | "
            f"{RARITY_EMOJI[card[5]]} "
            f"{card[2]} <b>{html.escape(card[1])}</b> "
            f"— {card[4]} OVR\n"
        )

    await message.answer(text, parse_mode="HTML")


# =========================================================
# MY CARDS
# =========================================================

@DP.message(Command("mycards"))
async def mycards(message: Message):
    await collection(message)


# =========================================================
# SHOP
# =========================================================

@DP.message(Command("shop"))
async def shop(message: Message):
    await register(message.from_user)

    kb = InlineKeyboardBuilder()

    for i, player in enumerate(PLAYERS):
        if player[3] >= 80:
            kb.button(
                text=f"{player[1]} {player[0]} — {player[5]:,} 🪙",
                callback_data=f"buy:{i}"
            )

    kb.adjust(1)

    await message.answer(
        "🛒 <b>МАГАЗИН ИГРОКОВ</b>\n\n"
        "Покупай игроков за 🪙.\n"
        "Цены снижены, но монеты всё равно не будут "
        "зарабатываться слишком легко.",
        reply_markup=kb.as_markup(),
        parse_mode="HTML"
    )


@DP.callback_query(F.data.startswith("buy:"))
async def buy(callback: CallbackQuery):
    await register(callback.from_user)

    index = int(callback.data.split(":")[1])
    player = PLAYERS[index]
    price = player[5]

    if owner(callback.from_user):
        await add_card(callback.from_user.id, player)
        await callback.answer("👑 Бесплатно для @foqlu!")
    else:
        if not await spend_coins(callback.from_user.id, price):
            await callback.answer(
                "❌ Недостаточно монет.",
                show_alert=True
            )
            return

        await add_card(callback.from_user.id, player)
        await callback.answer("✅ Игрок куплен!")

    await callback.message.answer(
        f"✅ <b>ИГРОК ПОЛУЧЕН</b>\n\n"
        f"{player[1]} <b>{html.escape(player[0])}</b>\n"
        f"⭐ {player[3]} OVR\n"
        f"💎 {player[4]}",
        parse_mode="HTML"
    )


# =========================================================
# SELL TO BOT
# =========================================================

@DP.message(Command("sellbot"))
async def sellbot(message: Message):
    await register(message.from_user)

    args = message.text.split()

    if len(args) != 2:
        await message.answer(
            "Используй: <code>/sellbot ID</code>",
            parse_mode="HTML"
        )
        return

    try:
        card_id = int(args[1])
    except ValueError:
        await message.answer("❌ Неверный ID.")
        return

    async with aiosqlite.connect(DB) as db:
        cur = await db.execute("""
        SELECT id, name, rating, rarity, price
        FROM cards
        WHERE id=? AND user_id=?
        """, (card_id, message.from_user.id))

        card = await cur.fetchone()

        if not card:
            await message.answer("❌ Карта не найдена.")
            return

        cur = await db.execute(
            "SELECT id FROM market WHERE card_id=?",
            (card_id,)
        )

        if await cur.fetchone():
            await message.answer("❌ Карта уже выставлена на рынок.")
            return

        sell_price = max(100, card[4] // 2)

        await db.execute(
            "DELETE FROM cards WHERE id=?",
            (card_id,)
        )

        await db.execute(
            "UPDATE users SET coins=coins+? WHERE user_id=?",
            (sell_price, message.from_user.id)
        )

        await db.commit()

    await message.answer(
        f"🤖 <b>БОТ ВЫКУПИЛ КАРТУ</b>\n\n"
        f"⚽ {html.escape(card[1])}\n"
        f"⭐ {card[2]} OVR\n"
        f"💎 {card[3]}\n\n"
        f"🪙 Получено: <b>{sell_price:,}</b>",
        parse_mode="HTML"
    )


# =========================================================
# MARKET
# =========================================================

@DP.message(Command("market"))
async def market(message: Message):
    await register(message.from_user)

    async with aiosqlite.connect(DB) as db:
        db.row_factory = aiosqlite.Row

        cur = await db.execute("""
        SELECT
            market.id,
            market.seller_id,
            market.card_id,
            market.price,
            cards.name,
            cards.nation,
            cards.rating,
            cards.rarity,
            users.username
        FROM market
        JOIN cards ON cards.id=market.card_id
        JOIN users ON users.user_id=market.seller_id
        ORDER BY market.id DESC
        LIMIT 30
        """)

        listings = await cur.fetchall()

    if not listings:
        await message.answer(
            "🏪 <b>РЫНОК ПУСТ</b>\n\n"
            "Выставь карту:\n"
            "<code>/sell ID цена</code>",
            parse_mode="HTML"
        )
        return

    kb = InlineKeyboardBuilder()
    text = "🏪 <b>РЫНОК</b>\n\n"

    for item in listings:
        text += (
            f"{RARITY_EMOJI[item['rarity']]} "
            f"{item['nation']} <b>{html.escape(item['name'])}</b>\n"
            f"⭐ {item['rating']} OVR\n"
            f"🪙 {item['price']:,}\n"
            f"👤 @{html.escape(item['username'] or 'player')}\n\n"
        )

        kb.button(
            text=f"🛒 Купить {item['name']}",
            callback_data=f"marketbuy:{item['id']}"
        )

    kb.adjust(1)

    await message.answer(
        text,
        reply_markup=kb.as_markup(),
        parse_mode="HTML"
    )


# =========================================================
# SELL
# =========================================================

@DP.message(Command("sell"))
async def sell(message: Message):
    await register(message.from_user)

    args = message.text.split()

    if len(args) != 3:
        await message.answer(
            "Формат:\n<code>/sell ID цена</code>",
            parse_mode="HTML"
        )
        return

    try:
        card_id = int(args[1])
        price = int(args[2])
    except ValueError:
        await message.answer("❌ ID и цена должны быть числами.")
        return

    if price <= 0:
        await message.answer("❌ Цена должна быть больше 0.")
        return

    async with aiosqlite.connect(DB) as db:

        cur = await db.execute("""
        SELECT id, name, rating, rarity
        FROM cards
        WHERE id=? AND user_id=?
        """, (card_id, message.from_user.id))

        card = await cur.fetchone()

        if not card:
            await message.answer("❌ Карта не найдена.")
            return

        cur = await db.execute(
            "SELECT id FROM market WHERE card_id=?",
            (card_id,)
        )

        if await cur.fetchone():
            await message.answer("❌ Карта уже на рынке.")
            return

        await db.execute("""
        INSERT INTO market(seller_id, card_id, price)
        VALUES (?, ?, ?)
        """, (
            message.from_user.id,
            card_id,
            price
        ))

        await db.commit()

    await message.answer(
        f"🏪 <b>КАРТА ВЫСТАВЛЕНА</b>\n\n"
        f"⚽ {html.escape(card[1])}\n"
        f"⭐ {card[2]} OVR\n"
        f"💎 {card[3]}\n"
        f"🪙 Цена: <b>{price:,}</b>",
        parse_mode="HTML"
    )


# =========================================================
# MARKET BUY
# =========================================================

@DP.callback_query(F.data.startswith("marketbuy:"))
async def marketbuy(callback: CallbackQuery):
    await register(callback.from_user)

    listing_id = int(callback.data.split(":")[1])

    async with aiosqlite.connect(DB) as db:
        db.row_factory = aiosqlite.Row

        cur = await db.execute("""
        SELECT
            market.id,
            market.seller_id,
            market.card_id,
            market.price,
            cards.name,
            cards.nation,
            cards.rating,
            cards.rarity
        FROM market
        JOIN cards ON cards.id=market.card_id
        WHERE market.id=?
        """, (listing_id,))

        item = await cur.fetchone()

        if not item:
            await callback.answer(
                "❌ Лот уже продан.",
                show_alert=True
            )
            return

        if item["seller_id"] == callback.from_user.id:
            await callback.answer(
                "❌ Нельзя купить свою карту.",
                show_alert=True
            )
            return

        if not await spend_coins(
            callback.from_user.id,
            item["price"]
        ):
            await callback.answer(
                "❌ Недостаточно монет.",
                show_alert=True
            )
            return

        await db.execute("""
        UPDATE cards
        SET user_id=?
        WHERE id=?
        """, (
            callback.from_user.id,
            item["card_id"]
        ))

        await db.execute("""
        UPDATE users
        SET coins=coins+?
        WHERE user_id=?
        """, (
            item["price"],
            item["seller_id"]
        ))

        await db.execute(
            "DELETE FROM market WHERE id=?",
            (listing_id,)
        )

        await db.commit()

    await callback.answer("✅ Карта куплена!")

    await callback.message.answer(
        f"✅ <b>КАРТА КУПЛЕНА</b>\n\n"
        f"{item['nation']} <b>{html.escape(item['name'])}</b>\n"
        f"⭐ {item['rating']} OVR\n"
        f"💎 {item['rarity']}\n"
        f"🪙 {item['price']:,}",
        parse_mode="HTML"
    )


# =========================================================
# DAILY
# =========================================================

async def daily_logic(message: Message):
    await register(message.from_user)

    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    async with aiosqlite.connect(DB) as db:

        cur = await db.execute("""
        SELECT daily_date, daily_streak
        FROM users
        WHERE user_id=?
        """, (message.from_user.id,))

        user = await cur.fetchone()

        if user[0] == today:
            await message.answer("🎁 Daily уже забран сегодня.")
            return

        streak = user[1] + 1
        reward = min(400 + streak * 100, 2000)

        await db.execute("""
        UPDATE users
        SET daily_date=?, daily_streak=?, coins=coins+?
        WHERE user_id=?
        """, (
            today,
            streak,
            reward,
            message.from_user.id
        ))

        await db.commit()

    await message.answer(
        f"🎁 <b>DAILY</b>\n\n"
        f"🔥 Серия: <b>{streak}</b>\n"
        f"🪙 Получено: <b>+{reward}</b>",
        parse_mode="HTML"
    )


@DP.message(Command("daily"))
async def daily(message: Message):
    await daily_logic(message)


# =========================================================
# MATCH
# =========================================================

@DP.message(Command("match"))
async def match(message: Message):
    await register(message.from_user)

    cards = await count_cards(message.from_user.id)

    if cards < 3:
        await message.answer(
            "⚽ Для матча нужно минимум <b>3 карты</b>.",
            parse_mode="HTML"
        )
        return

    user = await get_user(message.from_user.id)

    my_power = cards * 8 + random.randint(1, 100)
    enemy_power = random.randint(60, 170)

    if my_power >= enemy_power:
        reward = random.randint(300, 800)

        async with aiosqlite.connect(DB) as db:
            await db.execute("""
            UPDATE users
            SET wins=wins+1, coins=coins+?
            WHERE user_id=?
            """, (reward, message.from_user.id))

            await db.commit()

        await mission_update(message.from_user.id, "matches")

        await message.answer(
            f"🏆 <b>ПОБЕДА!</b>\n\n"
            f"⚽ Твоя команда выиграла.\n"
            f"🪙 +{reward}",
            parse_mode="HTML"
        )

    else:
        async with aiosqlite.connect(DB) as db:
            await db.execute("""
            UPDATE users
            SET losses=losses+1
            WHERE user_id=?
            """, (message.from_user.id,))

            await db.commit()

        await message.answer(
            "💀 <b>ПОРАЖЕНИЕ</b>\n\n"
            "Попробуй усилить коллекцию.",
            parse_mode="HTML"
        )


# =========================================================
# MISSIONS
# =========================================================

@DP.message(Command("missions"))
async def missions(message: Message):
    await register(message.from_user)

    async with aiosqlite.connect(DB) as db:
        cur = await db.execute("""
        SELECT drops, matches, cards, claimed
        FROM missions
        WHERE user_id=?
        """, (message.from_user.id,))

        m = await cur.fetchone()

    await message.answer(
        f"🎯 <b>ЗАДАНИЯ</b>\n\n"
        f"🃏 DROP: {m[0]}/3\n"
        f"⚽ Матчи: {m[1]}/3\n"
        f"📚 Карты: {m[2]}/5\n\n"
        f"🎁 Награда за выполнение: <b>3000 🪙</b>\n\n"
        f"Статус: {'✅ Выполнено' if m[3] else '⏳ В процессе'}",
        parse_mode="HTML"
    )


@DP.message(Command("claim"))
async def claim(message: Message):
    await register(message.from_user)

    async with aiosqlite.connect(DB) as db:
        cur = await db.execute("""
        SELECT drops, matches, cards, claimed
        FROM missions
        WHERE user_id=?
        """, (message.from_user.id,))

        m = await cur.fetchone()

        if m[3]:
            await message.answer("❌ Награда уже получена.")
            return

        if m[0] < 3 or m[1] < 3 or m[2] < 5:
            await message.answer(
                "❌ Задания ещё не выполнены."
            )
            return

        await db.execute("""
        UPDATE missions
        SET claimed=1
        WHERE user_id=?
        """, (message.from_user.id,))

        await db.execute("""
        UPDATE users
        SET coins=coins+3000
        WHERE user_id=?
        """, (message.from_user.id,))

        await db.commit()

    await message.answer(
        "🎉 <b>ЗАДАНИЯ ВЫПОЛНЕНЫ!</b>\n\n"
        "🪙 +3000",
        parse_mode="HTML"
    )


# =========================================================
# LEADERBOARD
# =========================================================

@DP.message(Command("top"))
@DP.message(Command("leaderboard"))
async def top(message: Message):
    async with aiosqlite.connect(DB) as db:
        cur = await db.execute("""
        SELECT username, wins, coins
        FROM users
        ORDER BY wins DESC, coins DESC
        LIMIT 10
        """)

        rows = await cur.fetchall()

    text = "🏆 <b>ТОП ИГРОКОВ</b>\n\n"

    for i, row in enumerate(rows, 1):
        username = row[0] or "player"

        text += (
            f"{i}. @{html.escape(username)} "
            f"— 🏆 {row[1]} | 🪙 {row[2]:,}\n"
        )

    await message.answer(text, parse_mode="HTML")


# =========================================================
# STARS PACKS
# =========================================================

@DP.message(Command("packs"))
async def packs(message: Message):
    await register(message.from_user)

    kb = InlineKeyboardBuilder()

    for key, data in STAR_PACKS.items():
        stars, amount, name = data

        kb.button(
            text=f"{name} — {stars} ⭐",
            callback_data=f"pack:{key}"
        )

    kb.adjust(1)

    await message.answer(
        "⭐ <b>PREMIUM PACKS</b>\n\n"
        "Паки покупаются через Telegram Stars.\n\n"
        "🎁 Количество карт зависит от пака.",
        reply_markup=kb.as_markup(),
        parse_mode="HTML"
    )


@DP.callback_query(F.data.startswith("pack:"))
async def pack_callback(callback: CallbackQuery):
    key = callback.data.split(":")[1]

    if key not in STAR_PACKS:
        await callback.answer("Ошибка", show_alert=True)
        return

    stars, amount, name = STAR_PACKS[key]

    await BOT.send_invoice(
        chat_id=callback.from_user.id,
        title=name,
        description=f"Цифровой футбольный пак. Карт: {amount}",
        payload=f"pack:{key}:{callback.from_user.id}",
        currency="XTR",
        prices=[
            LabeledPrice(
                label=name,
                amount=stars
            )
        ]
    )

    await callback.answer()


# =========================================================
# STARS PLAYERS
# =========================================================

@DP.message(Command("starplayers"))
async def starplayers(message: Message):
    await register(message.from_user)

    kb = InlineKeyboardBuilder()

    for i, player in enumerate(STAR_PLAYERS):
        kb.button(
            text=f"{player[1]} {player[0]} — {player[5]} ⭐",
            callback_data=f"starplayer:{i}"
        )

    kb.adjust(1)

    await message.answer(
        "⭐ <b>PLAYERS FOR STARS</b>\n\n"
        "Эксклюзивные карты.",
        reply_markup=kb.as_markup(),
        parse_mode="HTML"
    )


@DP.callback_query(F.data.startswith("starplayer:"))
async def starplayer_callback(callback: CallbackQuery):
    index = int(callback.data.split(":")[1])

    if index >= len(STAR_PLAYERS):
        await callback.answer("Ошибка", show_alert=True)
        return

    player = STAR_PLAYERS[index]
    stars = player[5]

    await BOT.send_invoice(
        chat_id=callback.from_user.id,
        title=player[0],
        description=f"Эксклюзивная карта {player[0]}",
        payload=f"starplayer:{index}:{callback.from_user.id}",
        currency="XTR",
        prices=[
            LabeledPrice(
                label=player[0],
                amount=stars
            )
        ]
    )

    await callback.answer()


# =========================================================
# PRE-CHECKOUT
# =========================================================

@DP.pre_checkout_query()
async def pre_checkout(query: PreCheckoutQuery):
    await query.answer(ok=True)


# =========================================================
# PAYMENT
# =========================================================

@DP.message(F.successful_payment)
async def successful_payment(message: Message):
    payment = message.successful_payment
    payload = payment.invoice_payload

    if payload.startswith("pack:"):

        parts = payload.split(":")
        key = parts[1]

        if key not in STAR_PACKS:
            return

        stars, amount, name = STAR_PACKS[key]

        for _ in range(amount):
            await add_card(
                message.from_user.id,
                random_player()
            )

        async with aiosqlite.connect(DB) as db:
            await db.execute("""
            INSERT INTO payments
            (user_id, product, stars, created)
            VALUES (?, ?, ?, ?)
            """, (
                message.from_user.id,
                key,
                stars,
                int(time.time())
            ))

            await db.commit()

        await message.answer(
            f"✅ <b>ПАК КУПЛЕН!</b>\n\n"
            f"📦 {name}\n"
            f"⭐ {stars} Stars\n"
            f"🃏 Карт: {amount}\n\n"
            f"/collection",
            parse_mode="HTML"
        )

    elif payload.startswith("starplayer:"):

        parts = payload.split(":")
        index = int(parts[1])

        if index >= len(STAR_PLAYERS):
            return

        player = STAR_PLAYERS[index]

        await add_card(message.from_user.id, player)

        await message.answer(
            f"🔥 <b>ЭКСКЛЮЗИВНАЯ КАРТА!</b>\n\n"
            f"{player[1]} <b>{player[0]}</b>\n"
            f"⭐ {player[3]} OVR\n"
            f"💎 Premium\n\n"
            f"📚 Добавлена в коллекцию.",
            parse_mode="HTML"
        )


# =========================================================
# HELP
# =========================================================

@DP.message(Command("help"))
async def help_command(message: Message):
    await message.answer(
        "⚽ <b>КОМАНДЫ FOOTBALL DROP</b>\n\n"
        "🃏 /drop — дроп раз в час\n"
        "👤 /profile — профиль\n"
        "📚 /collection — коллекция\n"
        "🃏 /mycards — карты с ID\n"
        "🛒 /shop — магазин за монеты\n"
        "⭐ /packs — паки за Stars\n"
        "⭐ /starplayers — игроки за Stars\n"
        "🏪 /market — рынок\n"
        "📤 /sell ID цена — выставить карту\n"
        "🤖 /sellbot ID — продать боту\n"
        "🎁 /daily — Daily\n"
        "🎯 /missions — задания\n"
        "🎁 /claim — забрать награду\n"
        "⚽ /match — матч\n"
        "🏆 /top — рейтинг\n"
        "❓ /help — помощь",
        parse_mode="HTML"
    )


# =========================================================
# OWNER
# =========================================================

@DP.message(Command("owner"))
async def owner_panel(message: Message):
    if not owner(message.from_user):
        await message.answer("❌ Нет доступа.")
        return

    await message.answer(
        "👑 <b>OWNER</b>\n\n"
        "Аккаунт: @foqlu\n\n"
        "🆓 DROP без кулдауна\n"
        "🆓 Игроки за монеты бесплатно\n"
        "🆓 Все обычные функции доступны.",
        parse_mode="HTML"
    )


# =========================================================
# STATS
# =========================================================

@DP.message(Command("stats"))
async def stats(message: Message):
    async with aiosqlite.connect(DB) as db:

        cur = await db.execute("SELECT COUNT(*) FROM users")
        users = (await cur.fetchone())[0]

        cur = await db.execute("SELECT COUNT(*) FROM cards")
        cards = (await cur.fetchone())[0]

        cur = await db.execute("SELECT COUNT(*) FROM market")
        market_count = (await cur.fetchone())[0]

    await message.answer(
        f"📊 <b>СТАТИСТИКА</b>\n\n"
        f"👥 Пользователей: <b>{users}</b>\n"
        f"🃏 Карт: <b>{cards}</b>\n"
        f"🏪 На рынке: <b>{market_count}</b>",
        parse_mode="HTML"
    )


# =========================================================
# BUTTONS
# =========================================================

@DP.callback_query(F.data == "drop")
async def button_drop(callback: CallbackQuery):
    await callback.answer()
    await do_drop(callback.message)


@DP.callback_query(F.data == "profile")
async def button_profile(callback: CallbackQuery):
    await callback.answer()

    user = await get_user(callback.from_user.id)

    await callback.message.answer(
        f"👤 <b>ПРОФИЛЬ</b>\n\n"
        f"🪙 {user['coins']:,} монет\n"
        f"🃏 {await count_cards(callback.from_user.id)} карт\n"
        f"🏆 {user['wins']} побед\n"
        f"💀 {user['losses']} поражений",
        parse_mode="HTML"
    )


@DP.callback_query(F.data == "collection")
async def button_collection(callback: CallbackQuery):
    await callback.answer()

    async with aiosqlite.connect(DB) as db:
        cur = await db.execute("""
        SELECT id, name, nation, rating, rarity
        FROM cards
        WHERE user_id=?
        ORDER BY rating DESC
        LIMIT 30
        """, (callback.from_user.id,))

        cards = await cur.fetchall()

    if not cards:
        await callback.message.answer(
            "📚 Коллекция пустая."
        )
        return

    text = "📚 <b>КОЛЛЕКЦИЯ</b>\n\n"

    for card in cards:
        text += (
            f"ID <code>{card[0]}</code> | "
            f"{RARITY_EMOJI[card[4]]} "
            f"{card[2]} {html.escape(card[1])} "
            f"— {card[3]}\n"
        )

    await callback.message.answer(
        text,
        parse_mode="HTML"
    )


@DP.callback_query(F.data == "shop")
async def button_shop(callback: CallbackQuery):
    await callback.answer()
    await callback.message.answer(
        "🛒 Используй /shop"
    )


@DP.callback_query(F.data == "market")
async def button_market(callback: CallbackQuery):
    await callback.answer()
    await callback.message.answer(
        "🏪 Используй /market"
    )


@DP.callback_query(F.data == "daily")
async def button_daily(callback: CallbackQuery):
    await callback.answer()
    await daily_logic(callback.message)


@DP.callback_query(F.data == "missions")
async def button_missions(callback: CallbackQuery):
    await callback.answer()

    await callback.message.answer(
        "🎯 Используй /missions"
    )


@DP.callback_query(F.data == "top")
async def button_top(callback: CallbackQuery):
    await callback.answer()

    async with aiosqlite.connect(DB) as db:
        cur = await db.execute("""
        SELECT username, wins, coins
        FROM users
        ORDER BY wins DESC, coins DESC
        LIMIT 10
        """)

        rows = await cur.fetchall()

    text = "🏆 <b>ТОП</b>\n\n"

    for i, row in enumerate(rows, 1):
        text += (
            f"{i}. @{html.escape(row[0] or 'player')} "
            f"— {row[1]} 🏆 | {row[2]:,} 🪙\n"
        )

    await callback.message.answer(
        text,
        parse_mode="HTML"
    )


# =========================================================
# START BOT
# =========================================================

async def main():
    await init_db()

    print("================================")
    print("FOOTBALL DROP BOT STARTED")
    print("TOKEN: Render Environment")
    print("================================")

    await DP.start_polling(BOT)


if __name__ == "__main__":
    asyncio.run(main())
