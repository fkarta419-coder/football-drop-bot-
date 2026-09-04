import asyncio
import json
import logging
import os
import random
import threading
from datetime import datetime, timedelta, date

import aiosqlite
from flask import Flask
from aiogram import Bot, Dispatcher, F, Router
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import (
    Message,
    CallbackQuery,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    LabeledPrice,
    PreCheckoutQuery,
)

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------

logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s")
logger = logging.getLogger("akinator-bot")

BOT_TOKEN = os.environ.get("BOT_TOKEN", "")
DB_PATH = os.environ.get("DB_PATH", "akinator.db")
PORT = int(os.environ.get("PORT", 10000))

FREE_DAILY_GAMES = 20
SUB_PRICE_STARS = 15
SUB_DAYS = 30
ADS_CONTACT = "@foqlu"

MAX_QUESTIONS = 18
MIN_QUESTIONS_BEFORE_GUESS = 5

# ---------------------------------------------------------------------------
# Flask keep-alive server (Render web service requires an open HTTP port)
# ---------------------------------------------------------------------------

flask_app = Flask(__name__)


@flask_app.route("/")
def health():
    return "Akinator bot is running."


def run_flask():
    flask_app.run(host="0.0.0.0", port=PORT)


# ---------------------------------------------------------------------------
# Bot / Dispatcher
# ---------------------------------------------------------------------------

bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
storage = MemoryStorage()
dp = Dispatcher(storage=storage)
router = Router()
dp.include_router(router)

# In-memory active game sessions: {user_id: {...}}
GAME_SESSIONS: dict[int, dict] = {}


class AddCharacterStates(StatesGroup):
    waiting_name = State()
    waiting_category = State()


# ---------------------------------------------------------------------------
# Questions bank
# index -> question text
# ---------------------------------------------------------------------------

QUESTIONS = [
    "Это мужчина?",                                            # 0
    "Он/она жив(а) сейчас?",                                   # 1
    "Известен(на) в первую очередь благодаря спорту?",         # 2
    "Связан(а) с футболом?",                                   # 3
    "Он/она из Европы?",                                       # 4
    "Он/она блогер или стример?",                              # 5
    "Это вымышленный персонаж (не реальный человек)?",         # 6
    "Он/она актёр или актриса?",                                # 7
    "Снимался(лась) в супергеройских фильмах?",                # 8
    "Он/она музыкант или певец(певица)?",                       # 9
    "Персонаж из видеоигры?",                                   # 10
    "Известен(на) в первую очередь в русскоязычном интернете?", # 11
    "Он/она из США?",                                           # 12
    "Историческая личность (жил(а) более 100 лет назад)?",     # 13
    "Он/она бизнесмен(вумен) или предприниматель(ница)?",       # 14
    "Это женщина?",                                             # 15
    "Играет (играл) в баскетбол?",                              # 16
    "Персонаж из аниме или манги?",                             # 17
]

# ---------------------------------------------------------------------------
# Character seed database
# Each character maps a subset of question indices to a weight:
#   1  -> да
#  -1  -> нет
#   0 / отсутствует -> неизвестно / не применимо (не влияет на счёт)
# This is intentionally a small starter set — designed to be expanded via
# the in-bot "learning" mechanic (see add_pending_character / promote flow).
# ---------------------------------------------------------------------------

CHARACTERS_SEED = {
    "Криштиану Роналду": {"category": "Футболисты", "attrs": {0: 1, 1: 1, 2: 1, 3: 1, 4: 1, 5: -1, 6: -1, 7: -1, 9: -1, 12: -1, 13: -1, 15: -1}},
    "Лионель Месси": {"category": "Футболисты", "attrs": {0: 1, 1: 1, 2: 1, 3: 1, 4: -1, 12: -1, 13: -1, 15: -1}},
    "Неймар": {"category": "Футболисты", "attrs": {0: 1, 1: 1, 2: 1, 3: 1, 4: -1, 12: -1, 13: -1, 15: -1}},
    "Килиан Мбаппе": {"category": "Футболисты", "attrs": {0: 1, 1: 1, 2: 1, 3: 1, 4: 1, 12: -1, 13: -1, 15: -1}},
    "Илон Маск": {"category": "Бизнес", "attrs": {0: 1, 1: 1, 2: -1, 3: -1, 6: -1, 14: 1, 12: 1, 13: -1, 15: -1}},
    "Марк Цукерберг": {"category": "Бизнес", "attrs": {0: 1, 1: 1, 2: -1, 6: -1, 14: 1, 12: 1, 13: -1, 15: -1}},
    "MrBeast": {"category": "Блогеры", "attrs": {0: 1, 1: 1, 5: 1, 12: 1, 11: -1, 13: -1, 15: -1, 6: -1}},
    "PewDiePie": {"category": "Блогеры", "attrs": {0: 1, 1: 1, 5: 1, 4: 1, 11: -1, 13: -1, 15: -1, 6: -1}},
    "Павел Дуров": {"category": "Бизнес", "attrs": {0: 1, 1: 1, 14: 1, 11: 1, 12: -1, 4: 1, 13: -1, 15: -1, 6: -1}},
    "Ivangai": {"category": "Блогеры", "attrs": {0: 1, 1: 1, 5: 1, 11: 1, 13: -1, 15: -1, 6: -1}},
    "Моргенштерн": {"category": "Блогеры", "attrs": {0: 1, 1: 1, 9: 1, 11: 1, 13: -1, 15: -1, 6: -1}},
    "Дима Билан": {"category": "Блогеры", "attrs": {0: 1, 1: 1, 9: 1, 11: 1, 13: -1, 15: -1, 6: -1}},
    "Ариана Гранде": {"category": "Блогеры", "attrs": {0: -1, 1: 1, 9: 1, 12: 1, 15: 1, 13: -1, 6: -1}},
    "Тейлор Свифт": {"category": "Блогеры", "attrs": {0: -1, 1: 1, 9: 1, 12: 1, 15: 1, 13: -1, 6: -1}},
    "Бейонсе": {"category": "Блогеры", "attrs": {0: -1, 1: 1, 9: 1, 12: 1, 15: 1, 13: -1, 6: -1}},
    "Железный человек": {"category": "Персонажи", "attrs": {0: 1, 6: 1, 8: 1, 7: -1, 13: -1, 15: -1}},
    "Бэтмен": {"category": "Персонажи", "attrs": {0: 1, 6: 1, 8: 1, 13: -1, 15: -1}},
    "Человек-паук": {"category": "Персонажи", "attrs": {0: 1, 6: 1, 8: 1, 13: -1, 15: -1}},
    "Наруто Узумаки": {"category": "Персонажи", "attrs": {0: 1, 6: 1, 17: 1, 13: -1, 15: -1}},
    "Сон Гоку": {"category": "Персонажи", "attrs": {0: 1, 6: 1, 17: 1, 13: -1, 15: -1}},
    "Марио": {"category": "Персонажи", "attrs": {0: 1, 6: 1, 10: 1, 13: -1, 15: -1}},
    "Соник": {"category": "Персонажи", "attrs": {0: 1, 6: 1, 10: 1, 13: -1, 15: -1}},
    "Леонардо Ди Каприо": {"category": "Актёры", "attrs": {0: 1, 1: 1, 7: 1, 12: 1, 13: -1, 15: -1, 6: -1}},
    "Роберт Дауни-младший": {"category": "Актёры", "attrs": {0: 1, 1: 1, 7: 1, 8: 1, 12: 1, 13: -1, 15: -1, 6: -1}},
    "Джонни Депп": {"category": "Актёры", "attrs": {0: 1, 1: 1, 7: 1, 12: 1, 13: -1, 15: -1, 6: -1}},
    "Альберт Эйнштейн": {"category": "Исторические", "attrs": {0: 1, 1: -1, 13: 1, 14: -1, 4: 1, 15: -1, 6: -1}},
    "Наполеон Бонапарт": {"category": "Исторические", "attrs": {0: 1, 1: -1, 13: 1, 4: 1, 15: -1, 6: -1}},
    "Стив Джобс": {"category": "Бизнес", "attrs": {0: 1, 1: -1, 14: 1, 12: 1, 13: -1, 15: -1, 6: -1}},
    "Билл Гейтс": {"category": "Бизнес", "attrs": {0: 1, 1: 1, 14: 1, 12: 1, 13: -1, 15: -1, 6: -1}},
    "Леброн Джеймс": {"category": "Спорт", "attrs": {0: 1, 1: 1, 2: 1, 16: 1, 12: 1, 3: -1, 13: -1, 15: -1, 6: -1}},
    "Майкл Джордан": {"category": "Спорт", "attrs": {0: 1, 1: 1, 2: 1, 16: 1, 12: 1, 3: -1, 13: -1, 15: -1, 6: -1}},
}

CATEGORIES = ["Все категории", "Футболисты", "Спорт", "Блогеры", "Актёры", "Персонажи", "Бизнес", "Исторические"]

ANSWER_VALUES = {
    "yes": 1.0,
    "no": -1.0,
    "probably_yes": 0.5,
    "probably_no": -0.5,
    "dont_know": 0.0,
}

ANSWER_LABELS = {
    "yes": "✅ Да",
    "no": "❌ Нет",
    "probably_yes": "↔️ Скорее да",
    "probably_no": "↔️ Скорее нет",
    "dont_know": "🤔 Не знаю",
}

LEVELS = [
    (0, "🌱 Новичок"),
    (50, "🔍 Детектив"),
    (150, "🧠 Знаток"),
    (400, "🎯 Мастер угадывания"),
    (1000, "👑 Легенда Акинатора"),
]


def get_level_info(xp: int) -> tuple[int, str, int | None]:
    """Returns (level_number, title, xp_needed_for_next_level_or_None)."""
    level_num = 1
    title = LEVELS[0][1]
    for i, (threshold, name) in enumerate(LEVELS):
        if xp >= threshold:
            level_num = i + 1
            title = name
        else:
            break
    next_threshold = None
    if level_num < len(LEVELS):
        next_threshold = LEVELS[level_num][0]
    return level_num, title, next_threshold


# ---------------------------------------------------------------------------
# Database layer
# ---------------------------------------------------------------------------

async def init_db():
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                username TEXT,
                xp INTEGER NOT NULL DEFAULT 0,
                games_played INTEGER NOT NULL DEFAULT 0,
                bot_correct_guesses INTEGER NOT NULL DEFAULT 0,
                bot_wrong_guesses INTEGER NOT NULL DEFAULT 0,
                daily_games_count INTEGER NOT NULL DEFAULT 0,
                daily_reset_date TEXT,
                subscription_until TEXT,
                created_at TEXT
            )
            """
        )
        await db.execute(
            """
            CREATE TABLE IF NOT EXISTS characters (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                category TEXT NOT NULL,
                attrs TEXT NOT NULL,
                approved INTEGER NOT NULL DEFAULT 1,
                added_by INTEGER,
                created_at TEXT
            )
            """
        )
        await db.commit()

        cur = await db.execute("SELECT COUNT(*) FROM characters")
        (count,) = await cur.fetchone()
        if count == 0:
            now = datetime.utcnow().isoformat()
            rows = [
                (name, data["category"], json.dumps(data["attrs"]), 1, None, now)
                for name, data in CHARACTERS_SEED.items()
            ]
            await db.executemany(
                "INSERT INTO characters (name, category, attrs, approved, added_by, created_at) VALUES (?, ?, ?, ?, ?, ?)",
                rows,
            )
            await db.commit()
            logger.info("Seeded %d characters into database", len(rows))


async def get_or_create_user(user_id: int, username: str | None):
    async with aiosqlite.connect(DB_PATH) as db:
        cur = await db.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
        row = await cur.fetchone()
        if row is None:
            now = datetime.utcnow().isoformat()
            today = date.today().isoformat()
            await db.execute(
                """INSERT INTO users
                   (user_id, username, xp, games_played, bot_correct_guesses, bot_wrong_guesses,
                    daily_games_count, daily_reset_date, subscription_until, created_at)
                   VALUES (?, ?, 0, 0, 0, 0, 0, ?, NULL, ?)""",
                (user_id, username, today, now),
            )
            await db.commit()
        else:
            await db.execute("UPDATE users SET username = ? WHERE user_id = ?", (username, user_id))
            await db.commit()


async def _reset_daily_if_needed(db: aiosqlite.Connection, user_id: int):
    today = date.today().isoformat()
    cur = await db.execute("SELECT daily_reset_date FROM users WHERE user_id = ?", (user_id,))
    (reset_date,) = await cur.fetchone()
    if reset_date != today:
        await db.execute(
            "UPDATE users SET daily_games_count = 0, daily_reset_date = ? WHERE user_id = ?",
            (today, user_id),
        )
        await db.commit()


async def is_subscribed(user_id: int) -> bool:
    async with aiosqlite.connect(DB_PATH) as db:
        cur = await db.execute("SELECT subscription_until FROM users WHERE user_id = ?", (user_id,))
        row = await cur.fetchone()
        if not row or not row[0]:
            return False
        until = datetime.fromisoformat(row[0])
        return until > datetime.utcnow()


async def can_start_game(user_id: int) -> tuple[bool, int]:
    """Returns (allowed, games_left_today). games_left_today is meaningless if subscribed."""
    if await is_subscribed(user_id):
        return True, -1
    async with aiosqlite.connect(DB_PATH) as db:
        await _reset_daily_if_needed(db, user_id)
        cur = await db.execute("SELECT daily_games_count FROM users WHERE user_id = ?", (user_id,))
        (count,) = await cur.fetchone()
        left = FREE_DAILY_GAMES - count
        return left > 0, max(left, 0)


async def register_game_start(user_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        await _reset_daily_if_needed(db, user_id)
        await db.execute(
            "UPDATE users SET daily_games_count = daily_games_count + 1, games_played = games_played + 1 WHERE user_id = ?",
            (user_id,),
        )
        await db.commit()


async def add_xp(user_id: int, amount: int):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("UPDATE users SET xp = xp + ? WHERE user_id = ?", (amount, user_id))
        await db.commit()


async def register_guess_result(user_id: int, correct: bool):
    field = "bot_correct_guesses" if correct else "bot_wrong_guesses"
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(f"UPDATE users SET {field} = {field} + 1 WHERE user_id = ?", (user_id,))
        await db.commit()


async def activate_subscription(user_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        cur = await db.execute("SELECT subscription_until FROM users WHERE user_id = ?", (user_id,))
        row = await cur.fetchone()
        base = datetime.utcnow()
        if row and row[0]:
            current_until = datetime.fromisoformat(row[0])
            if current_until > base:
                base = current_until
        new_until = base + timedelta(days=SUB_DAYS)
        await db.execute(
            "UPDATE users SET subscription_until = ? WHERE user_id = ?",
            (new_until.isoformat(), user_id),
        )
        await db.commit()
        return new_until


async def get_user_stats(user_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        cur = await db.execute(
            """SELECT xp, games_played, bot_correct_guesses, bot_wrong_guesses,
                      subscription_until FROM users WHERE user_id = ?""",
            (user_id,),
        )
        return await cur.fetchone()


async def get_top_players(limit: int = 10):
    async with aiosqlite.connect(DB_PATH) as db:
        cur = await db.execute(
            "SELECT username, xp, user_id FROM users ORDER BY xp DESC LIMIT ?",
            (limit,),
        )
        return await cur.fetchall()


async def get_characters(category: str | None = None):
    async with aiosqlite.connect(DB_PATH) as db:
        if category and category != "Все категории":
            cur = await db.execute(
                "SELECT name, attrs FROM characters WHERE approved = 1 AND category = ?", (category,)
            )
        else:
            cur = await db.execute("SELECT name, attrs FROM characters WHERE approved = 1")
        rows = await cur.fetchall()
        result = {}
        for name, attrs_str in rows:
            # attrs are stored as JSON with string keys; convert back to int keys
            result[name] = {int(k): v for k, v in json.loads(attrs_str).items()}
        return result


async def add_pending_character(name: str, category: str, added_by: int):
    async with aiosqlite.connect(DB_PATH) as db:
        now = datetime.utcnow().isoformat()
        await db.execute(
            "INSERT INTO characters (name, category, attrs, approved, added_by, created_at) VALUES (?, ?, ?, 0, ?, ?)",
            (name, category, json.dumps({}), added_by, now),
        )
        await db.commit()


# ---------------------------------------------------------------------------
# Keyboards
# ---------------------------------------------------------------------------

def kb_main_menu() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🎮 Начать игру", callback_data="menu:play")],
            [InlineKeyboardButton(text="🏆 Мой профиль", callback_data="menu:profile")],
            [InlineKeyboardButton(text="📊 Рейтинг игроков", callback_data="menu:top")],
            [InlineKeyboardButton(text="➕ Добавить персонажа", callback_data="menu:add")],
            [InlineKeyboardButton(text="⭐ Подписка (безлимит)", callback_data="menu:sub")],
            [InlineKeyboardButton(text="📢 Реклама", callback_data="menu:ads")],
        ]
    )


def kb_back_to_menu() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[[InlineKeyboardButton(text="⬅️ В меню", callback_data="menu:root")]]
    )


def kb_categories() -> InlineKeyboardMarkup:
    rows = []
    row = []
    for i, cat in enumerate(CATEGORIES, 1):
        row.append(InlineKeyboardButton(text=cat, callback_data=f"cat:{cat}"))
        if i % 2 == 0:
            rows.append(row)
            row = []
    if row:
        rows.append(row)
    rows.append([InlineKeyboardButton(text="⬅️ В меню", callback_data="menu:root")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def kb_answers() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text=ANSWER_LABELS["yes"], callback_data="ans:yes"),
                InlineKeyboardButton(text=ANSWER_LABELS["no"], callback_data="ans:no"),
            ],
            [
                InlineKeyboardButton(text=ANSWER_LABELS["probably_yes"], callback_data="ans:probably_yes"),
                InlineKeyboardButton(text=ANSWER_LABELS["probably_no"], callback_data="ans:probably_no"),
            ],
            [InlineKeyboardButton(text=ANSWER_LABELS["dont_know"], callback_data="ans:dont_know")],
            [InlineKeyboardButton(text="🏁 Закончить игру", callback_data="game:stop")],
        ]
    )


def kb_guess_confirm() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="✅ Да, угадал!", callback_data="guess:yes"),
                InlineKeyboardButton(text="❌ Нет, не угадал", callback_data="guess:no"),
            ]
        ]
    )


def kb_play_again() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🎮 Играть ещё", callback_data="menu:play")],
            [InlineKeyboardButton(text="⬅️ В меню", callback_data="menu:root")],
        ]
    )


def kb_subscribe() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=f"⭐ Оформить за {SUB_PRICE_STARS}", callback_data="sub:buy")],
            [InlineKeyboardButton(text="⬅️ В меню", callback_data="menu:root")],
        ]
    )


# ---------------------------------------------------------------------------
# Game engine (simplified Akinator-style scoring)
# ---------------------------------------------------------------------------

def choose_next_question(candidates: dict, asked: set) -> int | None:
    """Pick the unasked question that best splits the remaining candidates
    (closest to a 50/50 yes/no split among characters that have an opinion)."""
    best_q = None
    best_balance = -1.0
    for q_idx in range(len(QUESTIONS)):
        if q_idx in asked:
            continue
        yes_count = 0
        no_count = 0
        for name in candidates:
            attr = candidates[name].get(q_idx, 0)
            if attr > 0:
                yes_count += 1
            elif attr < 0:
                no_count += 1
        total = yes_count + no_count
        if total == 0:
            continue
        balance = min(yes_count, no_count) / total  # 0.5 = perfect split
        # slight preference for questions that more characters have an opinion on
        score = balance + 0.001 * total
        if score > best_balance:
            best_balance = score
            best_q = q_idx
    return best_q


def apply_answer(scores: dict, candidates: dict, q_idx: int, value: float):
    for name in candidates:
        attr = candidates[name].get(q_idx, 0)
        scores[name] += value * attr


def top_candidates(scores: dict, n: int = 2):
    return sorted(scores.items(), key=lambda kv: kv[1], reverse=True)[:n]


def should_guess(scores: dict, question_count: int) -> bool:
    if question_count < MIN_QUESTIONS_BEFORE_GUESS:
        return False
    ranked = top_candidates(scores, 2)
    if not ranked:
        return question_count >= MAX_QUESTIONS
    if len(ranked) == 1:
        return True
    top_score = ranked[0][1]
    second_score = ranked[1][1]
    if top_score >= 2.0 and (top_score - second_score) >= 1.5:
        return True
    return question_count >= MAX_QUESTIONS


# ---------------------------------------------------------------------------
# Handlers — main menu / navigation
# ---------------------------------------------------------------------------

WELCOME_TEXT = (
    "🧞 <b>Акинатор-бот</b>\n\n"
    "Загадай реального человека, персонажа, футболиста или блогера — "
    "а я попробую угадать, отвечая на пару вопросов!\n\n"
    f"Бесплатно: {FREE_DAILY_GAMES} игр в день.\n"
    f"⭐ Подписка за {SUB_PRICE_STARS} звёзд/месяц снимает лимит."
)


@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    await state.clear()
    await get_or_create_user(message.from_user.id, message.from_user.username)
    await message.answer(WELCOME_TEXT, reply_markup=kb_main_menu())


@router.callback_query(F.data == "menu:root")
async def cb_menu_root(call: CallbackQuery, state: FSMContext):
    await state.clear()
    GAME_SESSIONS.pop(call.from_user.id, None)
    await call.message.edit_text(WELCOME_TEXT, reply_markup=kb_main_menu())
    await call.answer()


@router.callback_query(F.data == "menu:ads")
async def cb_menu_ads(call: CallbackQuery):
    text = (
        "📢 <b>Реклама и сотрудничество</b>\n\n"
        f"По вопросам размещения рекламы и партнёрства пишите: {ADS_CONTACT}"
    )
    await call.message.edit_text(text, reply_markup=kb_back_to_menu())
    await call.answer()


@router.callback_query(F.data == "menu:profile")
async def cb_menu_profile(call: CallbackQuery):
    user_id = call.from_user.id
    stats = await get_user_stats(user_id)
    if not stats:
        await get_or_create_user(user_id, call.from_user.username)
        stats = await get_user_stats(user_id)
    xp, games_played, correct, wrong, sub_until = stats
    level_num, title, next_xp = get_level_info(xp)
    sub_line = "не активна"
    if sub_until:
        until_dt = datetime.fromisoformat(sub_until)
        if until_dt > datetime.utcnow():
            sub_line = f"активна до {until_dt.strftime('%d.%m.%Y')}"
    next_line = f"\nДо следующего уровня: {next_xp - xp} XP" if next_xp else "\nМаксимальный уровень!"
    text = (
        f"🏆 <b>Твой профиль</b>\n\n"
        f"Уровень {level_num}: {title}\n"
        f"Опыт: {xp} XP{next_line}\n\n"
        f"🎮 Игр сыграно: {games_played}\n"
        f"🎯 Бот угадал: {correct}\n"
        f"😎 Ты обыграл бота: {wrong}\n\n"
        f"⭐ Подписка: {sub_line}"
    )
    await call.message.edit_text(text, reply_markup=kb_back_to_menu())
    await call.answer()


@router.callback_query(F.data == "menu:top")
async def cb_menu_top(call: CallbackQuery):
    top = await get_top_players(10)
    if not top:
        text = "📊 Рейтинг пока пуст — сыграй первым!"
    else:
        lines = ["📊 <b>Топ игроков по опыту</b>\n"]
        medals = ["🥇", "🥈", "🥉"]
        for i, (username, xp, user_id) in enumerate(top):
            medal = medals[i] if i < 3 else f"{i + 1}."
            display = f"@{username}" if username else f"игрок {user_id}"
            lines.append(f"{medal} {display} — {xp} XP")
        text = "\n".join(lines)
    await call.message.edit_text(text, reply_markup=kb_back_to_menu())
    await call.answer()


@router.callback_query(F.data == "menu:sub")
async def cb_menu_sub(call: CallbackQuery):
    subscribed = await is_subscribed(call.from_user.id)
    if subscribed:
        text = "⭐ У тебя уже активна подписка — безлимитные игры доступны!"
        await call.message.edit_text(text, reply_markup=kb_back_to_menu())
    else:
        text = (
            f"⭐ <b>Подписка на месяц — {SUB_PRICE_STARS} звёзд</b>\n\n"
            f"Безлимитные игры без ограничения в {FREE_DAILY_GAMES}/день, на {SUB_DAYS} дней."
        )
        await call.message.edit_text(text, reply_markup=kb_subscribe())
    await call.answer()


@router.callback_query(F.data == "sub:buy")
async def cb_sub_buy(call: CallbackQuery):
    await call.answer()
    await bot.send_invoice(
        chat_id=call.from_user.id,
        title="Подписка Акинатор-бот — 1 месяц",
        description=f"Безлимитные игры на {SUB_DAYS} дней, без ограничения в {FREE_DAILY_GAMES} игр/день.",
        payload="subscription_1_month",
        currency="XTR",
        prices=[LabeledPrice(label="Подписка на месяц", amount=SUB_PRICE_STARS)],
        provider_token="",
    )


@router.pre_checkout_query()
async def pre_checkout(pre_checkout_q: PreCheckoutQuery):
    await bot.answer_pre_checkout_query(pre_checkout_q.id, ok=True)


@router.message(F.successful_payment)
async def successful_payment(message: Message):
    new_until = await activate_subscription(message.from_user.id)
    await message.answer(
        f"✅ Оплата получена! Подписка активна до {new_until.strftime('%d.%m.%Y')}.\n"
        f"Теперь игры без ограничений 🎉",
        reply_markup=kb_main_menu(),
    )


# ---------------------------------------------------------------------------
# Handlers — add character flow
# ---------------------------------------------------------------------------

@router.callback_query(F.data == "menu:add")
async def cb_menu_add(call: CallbackQuery, state: FSMContext):
    await call.message.edit_text(
        "➕ <b>Добавить персонажа</b>\n\nНапиши имя персонажа, которого хочешь добавить в базу:",
        reply_markup=kb_back_to_menu(),
    )
    await state.set_state(AddCharacterStates.waiting_name)
    await call.answer()


@router.message(AddCharacterStates.waiting_name)
async def process_add_name(message: Message, state: FSMContext):
    await state.update_data(name=message.text.strip()[:100])
    rows = []
    row = []
    for i, cat in enumerate(CATEGORIES[1:], 1):  # skip "Все категории"
        row.append(InlineKeyboardButton(text=cat, callback_data=f"addcat:{cat}"))
        if i % 2 == 0:
            rows.append(row)
            row = []
    if row:
        rows.append(row)
    await message.answer("Выбери категорию персонажа:", reply_markup=InlineKeyboardMarkup(inline_keyboard=rows))
    await state.set_state(AddCharacterStates.waiting_category)


@router.callback_query(AddCharacterStates.waiting_category, F.data.startswith("addcat:"))
async def process_add_category(call: CallbackQuery, state: FSMContext):
    category = call.data.split(":", 1)[1]
    data = await state.get_data()
    name = data.get("name", "Без имени")
    await add_pending_character(name, category, call.from_user.id)
    await add_xp(call.from_user.id, 15)
    await state.clear()
    await call.message.edit_text(
        f"✅ Персонаж «{name}» ({category}) добавлен на модерацию!\n"
        f"+15 XP начислено. После проверки он появится в игре 🎉",
        reply_markup=kb_main_menu(),
    )
    await call.answer()


# ---------------------------------------------------------------------------
# Handlers — game flow
# ---------------------------------------------------------------------------

@router.callback_query(F.data == "menu:play")
async def cb_menu_play(call: CallbackQuery, state: FSMContext):
    await state.clear()
    allowed, left = await can_start_game(call.from_user.id)
    if not allowed:
        text = (
            f"🎮 На сегодня лимит игр закончился ({FREE_DAILY_GAMES}/{FREE_DAILY_GAMES}).\n\n"
            f"Оформи подписку за {SUB_PRICE_STARS} ⭐ и играй без ограничений весь месяц!"
        )
        await call.message.edit_text(text, reply_markup=kb_subscribe())
        await call.answer()
        return
    await call.message.edit_text("Выбери категорию:", reply_markup=kb_categories())
    await call.answer()


@router.callback_query(F.data.startswith("cat:"))
async def cb_pick_category(call: CallbackQuery):
    category = call.data.split(":", 1)[1]
    user_id = call.from_user.id

    allowed, left = await can_start_game(user_id)
    if not allowed:
        text = f"🎮 На сегодня лимит игр закончился. Оформи подписку за {SUB_PRICE_STARS} ⭐."
        await call.message.edit_text(text, reply_markup=kb_subscribe())
        await call.answer()
        return

    candidates = await get_characters(category)
    if len(candidates) < 3:
        await call.answer("В этой категории пока маловато персонажей 🙈 Выбери другую.", show_alert=True)
        return

    await register_game_start(user_id)

    GAME_SESSIONS[user_id] = {
        "category": category,
        "candidates": candidates,
        "scores": {name: 0.0 for name in candidates},
        "asked": set(),
        "question_count": 0,
        "guessed_names": set(),
    }

    await ask_next_question(call, user_id)
    await call.answer()


async def ask_next_question(call: CallbackQuery, user_id: int):
    session = GAME_SESSIONS.get(user_id)
    if not session:
        await call.message.edit_text("Сессия игры не найдена. Начни заново.", reply_markup=kb_main_menu())
        return

    candidates = {
        name: attrs for name, attrs in session["candidates"].items()
        if name not in session["guessed_names"]
    }

    if should_guess(session["scores"], session["question_count"]) or len(candidates) <= 1:
        await make_guess(call, user_id)
        return

    q_idx = choose_next_question(candidates, session["asked"])
    if q_idx is None:
        await make_guess(call, user_id)
        return

    session["asked"].add(q_idx)
    q_num = session["question_count"] + 1
    text = f"❓ Вопрос {q_num}\n\n<b>{QUESTIONS[q_idx]}</b>"
    session["current_question"] = q_idx
    await call.message.edit_text(text, reply_markup=kb_answers())


@router.callback_query(F.data.startswith("ans:"))
async def cb_answer(call: CallbackQuery):
    user_id = call.from_user.id
    session = GAME_SESSIONS.get(user_id)
    if not session:
        await call.answer("Игра не найдена, начни заново из меню.", show_alert=True)
        return

    answer_key = call.data.split(":", 1)[1]
    value = ANSWER_VALUES.get(answer_key, 0.0)
    q_idx = session.get("current_question")

    if q_idx is not None:
        apply_answer(session["scores"], session["candidates"], q_idx, value)
        session["question_count"] += 1

    await ask_next_question(call, user_id)
    await call.answer()


async def make_guess(call: CallbackQuery, user_id: int):
    session = GAME_SESSIONS.get(user_id)
    if not session:
        return

    candidates = {
        name: sc for name, sc in session["scores"].items()
        if name not in session["guessed_names"]
    }
    if not candidates:
        await end_game_no_guess(call, user_id)
        return

    best_name = max(candidates.items(), key=lambda kv: kv[1])[0]
    session["guessed_names"].add(best_name)
    session["last_guess"] = best_name

    text = f"🎯 Кажется, вы загадали <b>{best_name}</b>!\n\nЯ угадал?"
    await call.message.edit_text(text, reply_markup=kb_guess_confirm())


@router.callback_query(F.data == "guess:yes")
async def cb_guess_yes(call: CallbackQuery):
    user_id = call.from_user.id
    session = GAME_SESSIONS.get(user_id)
    guessed = session.get("last_guess", "персонажа") if session else "персонажа"

    await register_guess_result(user_id, correct=True)
    await add_xp(user_id, 10)
    GAME_SESSIONS.pop(user_id, None)

    text = f"🎉 Отлично, я угадал — <b>{guessed}</b>!\n\n+10 XP начислено."
    await call.message.edit_text(text, reply_markup=kb_play_again())
    await call.answer()


@router.callback_query(F.data == "guess:no")
async def cb_guess_no(call: CallbackQuery):
    user_id = call.from_user.id
    session = GAME_SESSIONS.get(user_id)
    if not session:
        await call.answer("Игра не найдена.", show_alert=True)
        return

    remaining = {
        name: sc for name, sc in session["scores"].items()
        if name not in session["guessed_names"]
    }
    unasked_left = any(q not in session["asked"] for q in range(len(QUESTIONS)))

    if remaining and session["question_count"] < MAX_QUESTIONS and unasked_left:
        # Try again with next best question / candidate
        await ask_next_question(call, user_id)
        await call.answer("Хм, пробую ещё раз 🤔")
        return

    await end_game_no_guess(call, user_id)
    await call.answer()


async def end_game_no_guess(call: CallbackQuery, user_id: int):
    await register_guess_result(user_id, correct=False)
    await add_xp(user_id, 25)
    GAME_SESSIONS.pop(user_id, None)
    text = (
        "😅 Сдаюсь! Ты меня обыграл.\n\n"
        "+25 XP начислено за победу над ботом!\n"
        "Кстати, ты можешь добавить своего персонажа в базу через меню 👇"
    )
    await call.message.edit_text(text, reply_markup=kb_play_again())


@router.callback_query(F.data == "game:stop")
async def cb_game_stop(call: CallbackQuery, state: FSMContext):
    GAME_SESSIONS.pop(call.from_user.id, None)
    await state.clear()
    await call.message.edit_text("Игра остановлена.", reply_markup=kb_main_menu())
    await call.answer()


@router.message(Command("profile"))
async def cmd_profile(message: Message):
    await get_or_create_user(message.from_user.id, message.from_user.username)
    stats = await get_user_stats(message.from_user.id)
    xp = stats[0] if stats else 0
    level_num, title, _ = get_level_info(xp)
    await message.answer(f"Уровень {level_num}: {title} ({xp} XP)", reply_markup=kb_main_menu())


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

async def main():
    if not BOT_TOKEN:
        raise RuntimeError("BOT_TOKEN env var is not set")

    await init_db()

    flask_thread = threading.Thread(target=run_flask, daemon=True)
    flask_thread.start()
    logger.info("Flask keep-alive server started on port %s", PORT)

    logger.info("Starting bot polling...")
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
