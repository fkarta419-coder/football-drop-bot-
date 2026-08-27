# main.py
# FOOTBALL DROP
# aiogram 3 + SQLite
#
# Возможности:
# - DROP раз в час
# - Lucky Charm за Telegram Stars
# - Паки за Stars и монеты
# - Коллекция
# - Продажа карт БОТУ
# - Рынок
# - Daily
# - Задания
# - Промокоды
# - Рейтинг
# - Ивенты для @foqlu
# - Ивент сохраняется в SQLite после перезапуска
# - @foqlu запускает и останавливает ивенты кнопками
# - Пользователи получают уведомление о начале ивента

import os
import time
import random
import asyncio
import html
from datetime import datetime, timezone

import aiosqlite
from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command
from aiogram.types import (
    Message,
    CallbackQuery,
    LabeledPrice,
    PreCheckoutQuery,
)
from aiogram.utils.keyboard import InlineKeyboardBuilder

try:
    from keep_alive import keep_alive
    keep_alive()
except Exception:
    pass


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

REQUIRED_CHANNEL = os.getenv("REQUIRED_CHANNEL", "")
CHANNEL_LINK = "https://t.me/+MHTPcaFy2j5lOWMy"

# 1 ЧАС
DROP_COOLDOWN = 60 * 60

LUCKY_COST = 15
LUCKY_HOURS = 24

# =========================================================
# RARITIES
# =========================================================

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
    "Common",
    "Rare",
    "Super Rare",
    "Epic",
    "Legendary",
    "Icon",
    "Ultimate",
]


# =========================================================
# PLAYERS
# =========================================================

PLAYERS = [
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

    ("Килиан Мбаппе", "🇫🇷", "ST", 92, "Legendary", 85000),
    ("Эрлинг Холанд", "🇳🇴", "ST", 91, "Legendary", 80000),
    ("Мохамед Салах", "🇪🇬", "RW", 90, "Legendary", 70000),
    ("Джуд Беллингем", "🏴", "CAM", 90, "Legendary", 75000),
    ("Неймар", "🇧🇷", "LW", 91, "Legendary", 90000),
    ("Антуан Гризманн", "🇫🇷", "CF", 89, "Legendary", 70000),
    ("Тибо Куртуа", "🇧🇪", "GK", 90, "Legendary", 70000),
    ("Алиссон", "🇧🇷", "GK", 89, "Legendary", 65000),
    ("Ван Дейк", "🇳🇱", "CB", 89, "Legendary", 65000),

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

    ("Месси Ultimate", "🇦🇷", "RW", 99, "Ultimate", 500000),
    ("Роналду Ultimate", "🇵🇹", "ST", 99, "Ultimate", 500000),
    ("Пеле Ultimate", "🇧🇷", "ST", 99, "Ultimate", 500000),
    ("Марадона Ultimate", "🇦🇷", "CAM", 99, "Ultimate", 500000),

    ("Александр Исак", "🇸🇪", "ST", 86, "Super Rare", 27000),
    ("Виктор Осимхен", "🇳🇬", "ST", 86, "Super Rare", 27000),
    ("Хулиан Альварес", "🇦🇷", "ST", 87, "Super Rare", 30000),
    ("Виктор Дьёкереш", "🇸🇪", "ST", 86, "Super Rare", 27000),
    ("Александр Митрович", "🇷🇸", "ST", 80, "Rare", 9000),
    ("Олли Уоткинс", "🏴", "ST", 84, "Rare", 18000),
    ("Дарвин Нуньес", "🇺🇾", "ST", 83, "Rare", 16000),
    ("Джонатан Дэвид", "🇨🇦", "ST", 84, "Rare", 18000),
    ("Луис Диас", "🇨🇴", "LW", 85, "Super Rare", 23000),
    ("Лерой Сане", "🇩🇪", "RW", 84, "Rare", 18000),
    ("Кингсли Коман", "🇫🇷", "LW", 84, "Rare", 18000),
    ("Букаё Сака", "🏴", "RW", 89, "Epic", 45000),
    ("Мартин Эдегор", "🇳🇴", "CAM", 87, "Super Rare", 30000),
    ("Деклан Райс", "🏴", "CDM", 87, "Super Rare", 30000),
    ("Бруну Фернандеш", "🇵🇹", "CAM", 88, "Epic", 40000),
    ("Матео Ковачич", "🇭🇷", "CM", 84, "Rare", 18000),
    ("Френки де Йонг", "🇳🇱", "CM", 86, "Super Rare", 27000),
    ("Николо Барелла", "🇮🇹", "CM", 87, "Super Rare", 30000),
    ("Хакан Чалханоглу", "🇹🇷", "CM", 86, "Super Rare", 27000),
    ("Маркус Тюрам", "🇫🇷", "ST", 84, "Rare", 18000),
    ("Кенан Йылдыз", "🇹🇷", "LW", 82, "Rare", 12000),
    ("Виктор Цыганков", "🇺🇦", "RW", 82, "Rare", 12000),
    ("Микель Оярсабаль", "🇪🇸", "LW", 83, "Rare", 16000),
    ("Ферран Торрес", "🇪🇸", "RW", 82, "Rare", 12000),
    ("Алекс Баэна", "🇪🇸", "CAM", 83, "Rare", 16000),
    ("Микель Мерино", "🇪🇸", "CM", 84, "Rare", 18000),
    ("Марк Кукурелья", "🇪🇸", "LB", 82, "Rare", 12000),
    ("Пау Торрес", "🇪🇸", "CB", 83, "Rare", 16000),
    ("Аймерик Лапорт", "🇪🇸", "CB", 84, "Rare", 18000),
    ("Дани Карвахаль", "🇪🇸", "RB", 85, "Super Rare", 23000),
    ("Андреа Камбьязо", "🇮🇹", "LB", 81, "Rare", 10000),
    ("Алессандро Бастони", "🇮🇹", "CB", 87, "Super Rare", 30000),
    ("Франческо Ачерби", "🇮🇹", "CB", 81, "Rare", 10000),
    ("Джанлука Манчини", "🇮🇹", "CB", 82, "Rare", 12000),
    ("Давиде Фраттези", "🇮🇹", "CM", 82, "Rare", 12000),
    ("Лоренцо Пеллегрини", "🇮🇹", "CAM", 83, "Rare", 16000),
    ("Федерико Димарко", "🇮🇹", "LB", 85, "Super Rare", 23000),
    ("Мойзе Кин", "🇮🇹", "ST", 81, "Rare", 10000),
    ("Маттиа Дзакканьи", "🇮🇹", "LW", 83, "Rare", 16000),
    ("Жоржиньо", "🇮🇹", "CM", 82, "Rare", 12000),
    ("Доменико Берарди", "🇮🇹", "RW", 82, "Rare", 12000),
    ("Бенжамен Павар", "🇫🇷", "CB", 83, "Rare", 16000),
    ("Ибраима Конате", "🇫🇷", "CB", 85, "Super Rare", 23000),
    ("Люка Эрнандес", "🇫🇷", "CB", 84, "Rare", 18000),
    ("Усман Дембеле", "🇫🇷", "RW", 88, "Epic", 40000),
    ("Адриен Рабьо", "🇫🇷", "CM", 82, "Rare", 12000),
    ("Рандаль Коло Муани", "🇫🇷", "ST", 82, "Rare", 12000),
    ("Брэдли Баркола", "🇫🇷", "LW", 84, "Rare", 18000),
    ("Дезире Дуэ", "🇫🇷", "CAM", 82, "Rare", 12000),
    ("Лоис Опенда", "🇧🇪", "ST", 84, "Rare", 18000),
    ("Ромелу Лукаку", "🇧🇪", "ST", 84, "Rare", 18000),
    ("Юри Тилеманс", "🇧🇪", "CM", 82, "Rare", 12000),
    ("Амаду Онана", "🇧🇪", "CDM", 81, "Rare", 10000),
    ("Йохан Бакайоко", "🇧🇪", "RW", 81, "Rare", 10000),
    ("Кеннет Тейлор", "🇳🇱", "CM", 80, "Rare", 9000),
    ("Маттейс де Лигт", "🇳🇱", "CB", 84, "Rare", 18000),
    ("Натан Аке", "🇳🇱", "CB", 83, "Rare", 16000),
    ("Дензел Дюмфрис", "🇳🇱", "RB", 84, "Rare", 18000),
    ("Мемфис Депай", "🇳🇱", "ST", 82, "Rare", 12000),
    ("Коди Гакпо", "🇳🇱", "LW", 84, "Rare", 18000),
    ("Тён Копмейнерс", "🇳🇱", "CM", 83, "Rare", 16000),
    ("Райан Гравенберх", "🇳🇱", "CM", 83, "Rare", 16000),
    ("Майки Мур", "🏴", "RW", 78, "Common", 5000),
    ("Эберечи Эзе", "🏴", "CAM", 84, "Rare", 18000),
    ("Энтони Гордон", "🏴", "LW", 83, "Rare", 16000),
    ("Джеймс Мэддисон", "🏴", "CAM", 84, "Rare", 18000),
    ("Морган Гиббс-Уайт", "🏴", "CAM", 82, "Rare", 12000),
    ("Адам Уортон", "🏴", "CM", 80, "Rare", 9000),
    ("Кайл Уокер", "🏴", "RB", 83, "Rare", 16000),
    ("Джон Стоунз", "🏴", "CB", 84, "Rare", 18000),
    ("Люк Шоу", "🏴", "LB", 81, "Rare", 10000),
    ("Киран Триппьер", "🏴", "RB", 81, "Rare", 10000),
    ("Иван Перишич", "🇭🇷", "LW", 80, "Rare", 9000),
    ("Иосип Сутало", "🇭🇷", "CB", 80, "Rare", 9000),
    ("Йошко Гвардиол", "🇭🇷", "CB", 85, "Super Rare", 23000),
    ("Бруно Петкович", "🇭🇷", "ST", 80, "Rare", 9000),
    ("Андрей Крамарич", "🇭🇷", "ST", 82, "Rare", 12000),
    ("Никола Влашич", "🇭🇷", "CAM", 80, "Rare", 9000),
    ("Лука Модрич", "🇭🇷", "CM", 85, "Super Rare", 23000),
    ("Мануэль Угарте", "🇺🇾", "CDM", 82, "Rare", 12000),
    ("Факундо Пельистри", "🇺🇾", "RW", 79, "Common", 6000),
    ("Максимилиано Араухо", "🇺🇾", "LW", 81, "Rare", 10000),
    ("Мануэль Аканжи", "🇨🇭", "CB", 83, "Rare", 16000),
    ("Гранит Джака", "🇨🇭", "CM", 84, "Rare", 18000),
    ("Ремо Фройлер", "🇨🇭", "CDM", 78, "Common", 5000),
    ("Брель Эмболо", "🇨🇭", "ST", 80, "Rare", 9000),
    ("Янн Зоммер", "🇨🇭", "GK", 83, "Rare", 16000),
    ("Мурад Мустапха", "🇩🇿", "ST", 78, "Common", 5000),
    ("Рияд Марез", "🇩🇿", "RW", 83, "Rare", 16000),
    ("Саид Бенрахма", "🇩🇿", "LW", 79, "Common", 6000),
    ("Исмаэль Беннасер", "🇩🇿", "CM", 81, "Rare", 10000),
    ("Ахраф Хакими", "🇲🇦", "RB", 88, "Epic", 40000),
    ("Софьян Амрабат", "🇲🇦", "CDM", 81, "Rare", 10000),
    ("Юссеф Эн-Несири", "🇲🇦", "ST", 81, "Rare", 10000),
    ("Билал Эль-Ханнус", "🇲🇦", "CAM", 80, "Rare", 9000),
    ("Софьян Буфаль", "🇲🇦", "LW", 79, "Common", 6000),
    ("Такефуса Кубо", "🇯🇵", "RW", 84, "Rare", 18000),
    ("Каору Митома", "🇯🇵", "LW", 82, "Rare", 12000),
    ("Даити Камада", "🇯🇵", "CAM", 80, "Rare", 9000),
    ("Ватару Эндо", "🇯🇵", "CDM", 80, "Rare", 9000),
    ("Такуми Минамино", "🇯🇵", "CAM", 81, "Rare", 10000),
    ("Ким Мин Джэ", "🇰🇷", "CB", 85, "Super Rare", 23000),
    ("Ли Кан Ин", "🇰🇷", "CAM", 83, "Rare", 16000),
    ("Хван Хи Чхан", "🇰🇷", "ST", 81, "Rare", 10000),
    ("Ким Сын Гю", "🇰🇷", "GK", 78, "Common", 5000),
    ("Сердар Азмун", "🇮🇷", "ST", 80, "Rare", 9000),
    ("Мехди Тареми", "🇮🇷", "ST", 82, "Rare", 12000),
    ("Сардар Дурсун", "🇹🇷", "ST", 77, "Common", 5000),
    ("Ирфан Джан Кахведжи", "🇹🇷", "CAM", 80, "Rare", 9000),
    ("Оркун Кёкчю", "🇹🇷", "CM", 82, "Rare", 12000),
    ("Керем Актюркоглу", "🇹🇷", "LW", 82, "Rare", 12000),
    ("Абдюлькерим Бардакчи", "🇹🇷", "CB", 79, "Common", 6000),
    ("Ферди Кадыоглу", "🇹🇷", "LB", 82, "Rare", 12000),
    ("Дженк Тосун", "🇹🇷", "ST", 78, "Common", 5000),
    ("Мерих Демирал", "🇹🇷", "CB", 80, "Rare", 9000),
    ("Мартин Батурина", "🇭🇷", "CAM", 79, "Common", 6000),
    ("Виктор Бонифейс", "🇳🇬", "ST", 83, "Rare", 16000),
    ("Адемола Лукман", "🇳🇬", "RW", 84, "Rare", 18000),
    ("Саму Омордион", "🇪🇸", "ST", 81, "Rare", 10000),
    ("Родриго", "🇧🇷", "RW", 88, "Epic", 40000),
    ("Габриэл Мартинелли", "🇧🇷", "LW", 83, "Rare", 16000),
    ("Бруно Гимарайнс", "🇧🇷", "CM", 86, "Super Rare", 27000),
    ("Дуглас Луис", "🇧🇷", "CM", 82, "Rare", 12000),
    ("Жоао Педро", "🇧🇷", "ST", 82, "Rare", 12000),
    ("Эдерсон", "🇧🇷", "GK", 88, "Epic", 40000),
    ("Маркиньос", "🇧🇷", "CB", 87, "Super Rare", 30000),
    ("Габриэл Магальяйнс", "🇧🇷", "CB", 85, "Super Rare", 23000),
    ("Эмерсон Роял", "🇧🇷", "RB", 79, "Common", 6000),
    ("Каземиро", "🇧🇷", "CDM", 82, "Rare", 12000),
    ("Фабиньо", "🇧🇷", "CDM", 81, "Rare", 10000),
    ("Анхель Ди Мария", "🇦🇷", "RW", 84, "Rare", 18000),
    ("Пауло Дибала", "🇦🇷", "CAM", 85, "Super Rare", 23000),
    ("Алексис Мак Аллистер", "🇦🇷", "CM", 86, "Super Rare", 27000),
    ("Эмилиано Мартинес", "🇦🇷", "GK", 87, "Super Rare", 30000),
    ("Кристиан Ромеро", "🇦🇷", "CB", 86, "Super Rare", 27000),
    ("Лисандро Мартинес", "🇦🇷", "CB", 84, "Rare", 18000),
    ("Николас Отаменди", "🇦🇷", "CB", 80, "Rare", 9000),
    ("Леандро Паредес", "🇦🇷", "CDM", 81, "Rare", 10000),
    ("Анхель Корреа", "🇦🇷", "RW", 81, "Rare", 10000),
    ("Энцо Диас", "🇦🇷", "LB", 78, "Common", 5000),
    ("Родриго Де Пауль", "🇦🇷", "CM", 84, "Rare", 18000),
    ("Николас Гонсалес", "🇦🇷", "LW", 82, "Rare", 12000),
    ("Савио", "🇧🇷", "RW", 81, "Rare", 10000),
    ("Эстевао", "🇧🇷", "RW", 80, "Rare", 9000),
    ("Витор Роке", "🇧🇷", "ST", 79, "Common", 6000),
    ("Андре Сантос", "🇧🇷", "CM", 77, "Common", 5000),
    ("Жоау Невеш", "🇵🇹", "CM", 84, "Rare", 18000),
    ("Витинья", "🇵🇹", "CM", 87, "Super Rare", 30000),
    ("Нуну Мендеш", "🇵🇹", "LB", 85, "Super Rare", 23000),
    ("Диогу Жота", "🇵🇹", "ST", 84, "Rare", 18000),
    ("Гонсалу Рамуш", "🇵🇹", "ST", 81, "Rare", 10000),
    ("Педру Нету", "🇵🇹", "RW", 83, "Rare", 16000),
    ("Диогу Кошта", "🇵🇹", "GK", 84, "Rare", 18000),
    ("Рубен Диаш", "🇵🇹", "CB", 87, "Super Rare", 30000),
    ("Вильям Карвалью", "🇵🇹", "CDM", 80, "Rare", 9000),
    ("Рикарду Орта", "🇵🇹", "LW", 80, "Rare", 9000),
    ("Матеус Нунес", "🇵🇹", "CM", 81, "Rare", 10000),
    ("Бенуа Бадьяшиль", "🇫🇷", "CB", 80, "Rare", 9000),
    ("Леви Колвилл", "🏴", "CB", 81, "Rare", 10000),
    ("Мало Гюсто", "🇫🇷", "RB", 81, "Rare", 10000),
    ("Рис Джеймс", "🏴", "RB", 84, "Rare", 18000),
    ("Николас Джексон", "🇸🇳", "ST", 82, "Rare", 12000),
    ("Мойсес Кайседо", "🇪🇨", "CDM", 84, "Rare", 18000),
    ("Ромео Лавия", "🇧🇪", "CDM", 78, "Common", 5000),
    ("Марк Гехи", "🏴", "CB", 82, "Rare", 12000),
    ("Жан-Филипп Матета", "🇫🇷", "ST", 81, "Rare", 10000),
    ("Джаррод Боуэн", "🏴", "RW", 83, "Rare", 16000),
    ("Лукас Пакета", "🇧🇷", "CAM", 83, "Rare", 16000),
    ("Мохаммед Кудус", "🇬🇭", "RW", 82, "Rare", 12000),
    ("Майкл Кайоде", "🇮🇹", "RB", 77, "Common", 5000),
    ("Пьеро Инкапье", "🇪🇨", "CB", 80, "Rare", 9000),
    ("Пьер-Эмерик Обамеянг", "🇬🇦", "ST", 81, "Rare", 10000),
    ("Садио Мане", "🇸🇳", "LW", 84, "Rare", 18000),
    ("Калиду Кулибали", "🇸🇳", "CB", 80, "Rare", 9000),
    ("Идрисса Гейе", "🇸🇳", "CDM", 78, "Common", 5000),
    ("Исмаила Сарр", "🇸🇳", "RW", 80, "Rare", 9000),
    ("Майрон Боаду", "🇳🇱", "ST", 78, "Common", 5000),
    ("Арно Данджума", "🇳🇱", "LW", 79, "Common", 6000),
    ("Стивен Бергвейн", "🇳🇱", "LW", 80, "Rare", 9000),
    ("Ваут Вегхорст", "🇳🇱", "ST", 79, "Common", 6000),
    ("Ноа Ланг", "🇳🇱", "LW", 81, "Rare", 10000),
    ("Ибрагим Сангари", "🇨🇮", "CDM", 79, "Common", 6000),
    ("Секу Койта", "🇲🇱", "ST", 78, "Common", 5000),
    ("Мохамед Эль-Шеннави", "🇪🇬", "GK", 78, "Common", 5000),
    ("Махмуд Хассан", "🇪🇬", "LW", 77, "Common", 5000),
    ("Трезеге", "🇪🇬", "LW", 80, "Rare", 9000),
    ("Омар Мармуш", "🇪🇬", "ST", 84, "Rare", 18000),
    ("Мостафа Мохамед", "🇪🇬", "ST", 78, "Common", 5000),
    ("Андре Онана", "🇨🇲", "GK", 82, "Rare", 12000),
    ("Брайан Мбемо", "🇨🇲", "RW", 84, "Rare", 18000),
    ("Карл Токо Экамби", "🇨🇲", "LW", 78, "Common", 5000),
    ("Йереми Пино", "🇪🇸", "RW", 80, "Rare", 9000),
    ("Микель Весга", "🇪🇸", "CM", 78, "Common", 5000),
    ("Серхио Регилон", "🇪🇸", "LB", 77, "Common", 5000),
    ("Тьяско Сеговия", "🇻🇪", "CM", 76, "Common", 4500),
    ("Тадео Альенде", "🇦🇷", "RW", 76, "Common", 4500),
    ("Луис Суарес", "🇺🇾", "ST", 83, "Rare", 16000),
]


# =========================================================
# PACKS
# =========================================================

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


# =========================================================
# EVENTS
# =========================================================

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
}


# =========================================================
# DATABASE
# =========================================================

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
        )
        """)

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
        )
        """)

        await db.execute("""
        CREATE TABLE IF NOT EXISTS market(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            seller_id INTEGER NOT NULL,
            card_id INTEGER NOT NULL,
            price INTEGER NOT NULL
        )
        """)

        await db.execute("""
        CREATE TABLE IF NOT EXISTS payments(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            product TEXT NOT NULL,
            stars INTEGER NOT NULL,
            created INTEGER NOT NULL
        )
        """)

        await db.execute("""
        CREATE TABLE IF NOT EXISTS missions(
            user_id INTEGER PRIMARY KEY,
            drops INTEGER DEFAULT 0,
            cards INTEGER DEFAULT 0,
            claimed INTEGER DEFAULT 0
        )
        """)

        await db.execute("""
        CREATE TABLE IF NOT EXISTS promo_codes(
            code TEXT PRIMARY KEY,
            coins INTEGER DEFAULT 0,
            stars INTEGER DEFAULT 0,
            activations INTEGER NOT NULL,
            used INTEGER DEFAULT 0,
            created INTEGER NOT NULL
        )
        """)

        await db.execute("""
        CREATE TABLE IF NOT EXISTS promo_uses(
            code TEXT NOT NULL,
            user_id INTEGER NOT NULL,
            PRIMARY KEY(code,user_id)
        )
        """)

        await db.execute("""
        CREATE TABLE IF NOT EXISTS lucky_charms(
            user_id INTEGER PRIMARY KEY,
            expires_at INTEGER NOT NULL
        )
        """)

        # ИВЕНТЫ ХРАНЯТСЯ В БАЗЕ
        await db.execute("""
        CREATE TABLE IF NOT EXISTS active_event(
            id INTEGER PRIMARY KEY CHECK(id = 1),
            event_key TEXT NOT NULL,
            expires_at INTEGER NOT NULL,
            active INTEGER DEFAULT 1
        )
        """)

        await db.commit()

        # Миграции для старой БД
        for column, definition in [
            ("stars", "INTEGER DEFAULT 0"),
            ("coins", "INTEGER DEFAULT 0"),
            ("last_drop", "INTEGER DEFAULT 0"),
            ("banned", "INTEGER DEFAULT 0"),
        ]:
            try:
                await db.execute(
                    f"ALTER TABLE users ADD COLUMN {column} {definition}"
                )
            except Exception:
                pass

        await db.commit()


# =========================================================
# USER FUNCTIONS
# =========================================================

async def register(user):
    async with aiosqlite.connect(DB) as db:

        await db.execute(
            """
            INSERT OR IGNORE INTO users
            (user_id, username, first_name)
            VALUES (?, ?, ?)
            """,
            (
                user.id,
                user.username or "",
                user.first_name or "",
            )
        )

        await db.execute(
            """
            UPDATE users
            SET username=?, first_name=?
            WHERE user_id=?
            """,
            (
                user.username or "",
                user.first_name or "",
                user.id,
            )
        )

        await db.execute(
            """
            INSERT OR IGNORE INTO missions(user_id)
            VALUES(?)
            """,
            (user.id,)
        )

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
            """
            UPDATE users
            SET coins=coins+?
            WHERE user_id=?
            """,
            (amount, user_id)
        )

        await db.commit()


async def spend_coins(user_id, amount):
    async with aiosqlite.connect(DB) as db:

        cur = await db.execute(
            """
            SELECT coins,banned
            FROM users
            WHERE user_id=?
            """,
            (user_id,)
        )

        row = await cur.fetchone()

        if not row:
            return False

        if row[1]:
            return False

        if row[0] < amount:
            return False

        await db.execute(
            """
            UPDATE users
            SET coins=coins-?
            WHERE user_id=?
            """,
            (amount, user_id)
        )

        await db.commit()

        return True


async def add_card(user_id, player):
    name, nation, position, rating, rarity, price = player

    async with aiosqlite.connect(DB) as db:
        await db.execute(
            """
            INSERT INTO cards
            (user_id,name,nation,position,rating,rarity,price,created_at)
            VALUES(?,?,?,?,?,?,?,?)
            """,
            (
                user_id,
                name,
                nation,
                position,
                rating,
                rarity,
                price,
                int(time.time()),
            )
        )

        await db.commit()


async def mission_update(user_id, field, amount=1):
    if field not in ("drops", "cards"):
        return

    async with aiosqlite.connect(DB) as db:
        await db.execute(
            f"""
            UPDATE missions
            SET {field}={field}+?
            WHERE user_id=?
            """,
            (amount, user_id)
        )

        await db.commit()


def is_owner(user):
    return (user.username or "").lower() == OWNER.lower()


# =========================================================
# SUBSCRIPTION
# =========================================================

async def check_access(user_id):
    if not REQUIRED_CHANNEL:
        return True

    try:
        member = await BOT.get_chat_member(
            REQUIRED_CHANNEL,
            user_id
        )

        return member.status in (
            "creator",
            "administrator",
            "member",
        )

    except Exception:
        return False


def subscribe_keyboard():
    kb = InlineKeyboardBuilder()

    kb.button(
        text="📢 Подписаться на канал",
        url=CHANNEL_LINK
    )

    kb.button(
        text="✅ Проверить подписку",
        callback_data="check_sub"
    )

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
        reply_markup=subscribe_keyboard(),
        parse_mode="HTML",
    )

    return False


# =========================================================
# EVENTS
# =========================================================

async def get_active_event():
    now = int(time.time())

    async with aiosqlite.connect(DB) as db:
        db.row_factory = aiosqlite.Row

        cur = await db.execute(
            """
            SELECT *
            FROM active_event
            WHERE id=1 AND active=1
            """
        )

        row = await cur.fetchone()

        if not row:
            return None

        if row["expires_at"] != 0 and row["expires_at"] <= now:

            await db.execute(
                """
                UPDATE active_event
                SET active=0
                WHERE id=1
                """
            )

            await db.commit()

            return None

        return row


async def start_event(event_key, minutes):
    if event_key not in EVENTS:
        return False

    if minutes == 0:
        expires_at = 0
    else:
        expires_at = int(time.time()) + minutes * 60

    async with aiosqlite.connect(DB) as db:

        await db.execute(
            """
            INSERT INTO active_event
            (id,event_key,expires_at,active)
            VALUES(1,?,?,1)
            ON CONFLICT(id)
            DO UPDATE SET
                event_key=excluded.event_key,
                expires_at=excluded.expires_at,
                active=1
            """,
            (
                event_key,
                expires_at,
            )
        )

        await db.commit()

    return True


async def stop_event():
    async with aiosqlite.connect(DB) as db:

        await db.execute(
            """
            UPDATE active_event
            SET active=0
            WHERE id=1
            """
        )

        await db.commit()


async def notify_event_started(event_key, minutes):
    event = EVENTS[event_key]

    if minutes == 0:
        duration = "♾ навсегда"
    else:
        duration = f"⏳ {minutes} мин."

    async with aiosqlite.connect(DB) as db:
        cur = await db.execute(
            "SELECT user_id FROM users WHERE banned=0"
        )

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
            await BOT.send_message(
                row[0],
                text,
                parse_mode="HTML"
            )

            await asyncio.sleep(0.03)

        except Exception:
            pass


def event_keyboard():
    kb = InlineKeyboardBuilder()

    for key, event in EVENTS.items():
        kb.button(
            text=event["name"],
            callback_data=f"event_select:{key}"
        )

    kb.button(
        text="⛔ Остановить текущий ивент",
        callback_data="event_stop"
    )

    kb.adjust(1)

    return kb.as_markup()


def event_duration_keyboard(event_key):
    kb = InlineKeyboardBuilder()

    options = [
        ("⏱ 1 минута", 1),
        ("⏱ 10 минут", 10),
        ("⏱ 1 час", 60),
        ("⏱ 3 часа", 180),
        ("♾ Навсегда", 0),
    ]

    for text, minutes in options:
        kb.button(
            text=text,
            callback_data=f"event_start:{event_key}:{minutes}"
        )

    kb.button(
        text="⬅️ Назад",
        callback_data="event_menu"
    )

    kb.adjust(1)

    return kb.as_markup()


def get_event_multiplier_weights(multiplier):
    weights = []

    for rarity in RARITIES:
        weight = RARITIES[rarity]

        if rarity == "Common":
            weight *= 1
        else:
            weight *= multiplier

        weights.append(weight)

    return weights


def choose_rarity(user=None, event=None):
    names = list(RARITIES.keys())
    weights = list(RARITIES.values())

    # Lucky Charm
    if user and user["lucky_until"] > int(time.time()):
        weights = [
            weights[i] *
            (1 if names[i] == "Common" else 3)
            for i in range(len(names))
        ]

    # Event
    if event:
        event_key = event["event_key"]
        event_data = EVENTS.get(event_key)

        if event_data:
            event_type = event_data["type"]

            if event_type == "rarity":
                weights = get_event_multiplier_weights(
                    event_data["value"]
                )

            elif event_type == "ultimate":
                for i, rarity in enumerate(names):
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

    return random.choices(
        names,
        weights=weights,
        k=1
    )[0]


def random_player(user=None, event=None):
    rarity = choose_rarity(user, event)

    pool = [
        p for p in PLAYERS
        if p[4] == rarity
    ]

    if not pool:
        pool = PLAYERS

    return random.choice(pool)


# =========================================================
# KEYBOARDS
# =========================================================

def main_keyboard(user=None):
    kb = InlineKeyboardBuilder()

    buttons = [
        ("🃏 DROP", "drop"),
        ("📚 Коллекция", "collection"),
        ("👤 Профиль", "profile"),
        ("🛒 Магазин", "shop"),
        ("🏪 Рынок", "market"),
        ("🎁 Daily", "daily"),
        ("🎯 Задания", "missions"),
        ("🏆 Рейтинг", "top"),
        ("📦 Паки за 🪙", "coinpacks"),
        ("⭐ Паки за Stars", "packs"),
        ("🎟️ Промокод", "promo"),
        ("🍀 Lucky Charm", "lucky"),
    ]

    if user and is_owner(user):
        buttons.append(
            ("👑 Ивенты", "event_menu")
        )

    for text, data in buttons:
        kb.button(
            text=text,
            callback_data=data
        )

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

    now = int(time.time())

    # ВЛАДЕЛЕЦ МОЖЕТ ТЕСТИРОВАТЬ DROP
    if not is_owner(message.from_user):

        if user["last_drop"]:
            remaining = DROP_COOLDOWN - (
                now - user["last_drop"]
            )

            if remaining > 0:
                hours = remaining // 3600
                minutes = (remaining % 3600) // 60
                seconds = remaining % 60

                await message.answer(
                    "⏳ <b>DROP ЕЩЁ НЕ ДОСТУПЕН</b>\n\n"
                    f"Осталось: "
                    f"<b>{hours}ч {minutes}м {seconds}с</b>",
                    parse_mode="HTML"
                )

                return

    async with aiosqlite.connect(DB) as db:
        await db.execute(
            """
            UPDATE users
            SET last_drop=?
            WHERE user_id=?
            """,
            (
                now,
                message.from_user.id,
            )
        )

        await db.commit()

    event = await get_active_event()

    # Монеты
    coins = random.randint(100, 400)

    if event:
        event_data = EVENTS.get(event["event_key"])

        if event_data and event_data["type"] == "coins":
            coins *= event_data["value"]

    await add_coins(
        message.from_user.id,
        coins
    )

    await mission_update(
        message.from_user.id,
        "drops"
    )

    await message.answer(
        "📦 <b>ПАК ОТКРЫВАЕТСЯ...</b>",
        parse_mode="HTML"
    )

    await asyncio.sleep(0.7)

    # Количество карт
    amount = 1

    if event:
        event_data = EVENTS.get(event["event_key"])

        if (
            event_data
            and event_data["type"] == "double"
        ):
            amount = 2

    pulled = []

    for _ in range(amount):

        # обновляем user перед выбором
        user = await get_user(
            message.from_user.id
        )

        player = random_player(
            user,
            event
        )

        name, nation, pos, rating, rarity, price = player

        await add_card(
            message.from_user.id,
            player
        )

        await mission_update(
            message.from_user.id,
            "cards"
        )

        pulled.append(player)

    # Ответ
    text = (
        "⚽ <b>FOOTBALL DROP!</b>\n\n"
    )

    if event:
        event_data = EVENTS.get(
            event["event_key"]
        )

        text += (
            f"🚨 Ивент: <b>{event_data['name']}</b>\n\n"
        )

    for index, player in enumerate(pulled, 1):

        name, nation, pos, rating, rarity, price = player

        if amount > 1:
            text += f"🃏 <b>КАРТА {index}</b>\n"

        text += (
            f"{RARITY_EMOJI.get(rarity, '⚪')} "
            f"<b>{rarity.upper()}</b>\n"
            f"{nation} <b>{html.escape(name)}</b>\n"
            f"⚡ Позиция: <b>{pos}</b>\n"
            f"⭐ Рейтинг: <b>{rating}</b>\n"
            f"💰 Цена: <b>€{price:,}</b>\n\n"
        )

    text += f"🪙 Бонус: <b>+{coins}</b>"

    kb = InlineKeyboardBuilder()

    kb.button(
        text="📚 Коллекция",
        callback_data="collection"
    )

    kb.button(
        text="🏪 Продать карту боту",
        callback_data="market"
    )

    kb.adjust(1)

    await message.answer(
        text,
        reply_markup=kb.as_markup(),
        parse_mode="HTML"
    )


@DP.message(Command("drop"))
async def drop_command(message: Message):
    await do_drop(message)


# =========================================================
# START
# =========================================================

@DP.message(Command("start"))
async def start(message: Message):
    await register(message.from_user)

    if not await require_subscription(message):
        return

    user = await get_user(
        message.from_user.id
    )

    if user["banned"] and not is_owner(message.from_user):
        await message.answer("🚫 Вы заблокированы.")
        return

    cards = await count_cards(
        message.from_user.id
    )

    await message.answer(
        f"⚽ <b>FOOTBALL DROP</b>\n\n"
        f"Привет, <b>{html.escape(message.from_user.first_name)}</b>!\n\n"
        f"🪙 Монеты: <b>{user['coins']:,}</b>\n"
        f"⭐ Stars: <b>{user['stars']}</b>\n"
        f"🃏 Карт: <b>{cards}</b>\n\n"
        "⚽ DROP — раз в час\n"
        "📚 Коллекция — твои карты\n"
        "🏪 Магазин — покупки\n"
        "💰 Рынок — продажа карт\n"
        "🎁 Daily — ежедневная награда\n"
        "🎯 Задания — дополнительные награды\n"
        "🍀 Lucky Charm — повышенный шанс",
        reply_markup=main_keyboard(message.from_user),
        parse_mode="HTML"
    )


# =========================================================
# PROFILE
# =========================================================

async def show_profile(message):
    await register(message.from_user)

    if not await require_subscription(message):
        return

    u = await get_user(
        message.from_user.id
    )

    lucky = (
        "активен"
        if u["lucky_until"] > int(time.time())
        else "нет"
    )

    await message.answer(
        "👤 <b>ПРОФИЛЬ</b>\n\n"
        f"👤 {html.escape(message.from_user.first_name)}\n"
        f"🪙 Монеты: <b>{u['coins']:,}</b>\n"
        f"⭐ Stars: <b>{u['stars']}</b>\n"
        f"🃏 Карт: <b>{await count_cards(message.from_user.id)}</b>\n"
        f"🏆 Побед: <b>{u['wins']}</b>\n"
        f"💀 Поражений: <b>{u['losses']}</b>\n"
        f"🍀 Lucky Charm: <b>{lucky}</b>",
        parse_mode="HTML"
    )


@DP.message(Command("profile"))
async def profile_command(message):
    await show_profile(message)


# =========================================================
# COLLECTION
# =========================================================

async def show_collection(message):
    await register(message.from_user)

    if not await require_subscription(message):
        return

    async with aiosqlite.connect(DB) as db:
        db.row_factory = aiosqlite.Row

        cur = await db.execute(
            """
            SELECT *
            FROM cards
            WHERE user_id=?
            ORDER BY rating DESC, id DESC
            LIMIT 100
            """,
            (message.from_user.id,)
        )

        cards = await cur.fetchall()

    if not cards:
        await message.answer(
            "📚 <b>ТВОЯ КОЛЛЕКЦИЯ ПУСТА</b>\n\n"
            "Открой свой первый DROP ⚽",
            parse_mode="HTML"
        )
        return

    text = "📚 <b>ТВОЯ КОЛЛЕКЦИЯ</b>\n\n"

    for i, card in enumerate(cards, 1):
        text += (
            f"{i}. "
            f"{RARITY_EMOJI.get(card['rarity'], '⚪')} "
            f"<b>{html.escape(card['name'])}</b>\n"
            f"   {card['nation']} "
            f"{card['position']} | "
            f"⭐ {card['rating']}\n"
            f"   💰 €{card['price']:,}\n\n"
        )

    kb = InlineKeyboardBuilder()

    kb.button(
        text="⚽ DROP",
        callback_data="drop"
    )

    kb.button(
        text="🏪 Продать карты",
        callback_data="market"
    )

    kb.adjust(2)

    await message.answer(
        text,
        reply_markup=kb.as_markup(),
        parse_mode="HTML"
    )


@DP.message(Command("collection"))
async def collection_command(message):
    await show_collection(message)


@DP.message(Command("mycards"))
async def mycards_command(message):
    await show_collection(message)


# =========================================================
# SHOP
# =========================================================

def shop_keyboard():
    kb = InlineKeyboardBuilder()

    kb.button(
        text="🍀 Lucky Charm",
        callback_data="lucky"
    )

    kb.button(
        text="⭐ Паки за Stars",
        callback_data="packs"
    )

    kb.button(
        text="📦 Паки за 🪙",
        callback_data="coinpacks"
    )

    kb.button(
        text="🏪 Продать карту боту",
        callback_data="market"
    )

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
        reply_markup=shop_keyboard(),
        parse_mode="HTML"
    )


@DP.message(Command("shop"))
async def shop_command(message):
    await show_shop(message)


# =========================================================
# LUCKY
# =========================================================

@DP.message(Command("lucky"))
async def lucky_command(message):
    await register(message.from_user)

    if not await require_subscription(message):
        return

    await send_lucky_invoice(
        message.chat.id
    )


async def send_lucky_invoice(chat_id):
    await BOT.send_invoice(
        chat_id=chat_id,
        title="🍀 Lucky Charm",
        description="24 часа повышенного шанса на редкие карты.",
        payload=f"lucky:{chat_id}:{int(time.time())}",
        currency="XTR",
        prices=[
            LabeledPrice(
                label="Lucky Charm",
                amount=LUCKY_COST
            )
        ]
    )


# =========================================================
# STAR PACKS
# =========================================================

async def show_packs(message):
    await register(message.from_user)

    if not await require_subscription(message):
        return

    kb = InlineKeyboardBuilder()

    for key, (stars, amount, name) in STAR_PACKS.items():
        kb.button(
            text=f"{name} — {stars} ⭐",
            callback_data=f"pack:{key}"
        )

    kb.button(
        text="⬅️ Магазин",
        callback_data="shop"
    )

    kb.adjust(1)

    await message.answer(
        "⭐ <b>ПАКИ ЗА STARS</b>\n\n"
        "Выбери пак:",
        reply_markup=kb.as_markup(),
        parse_mode="HTML"
    )


@DP.message(Command("packs"))
async def packs_command(message):
    await show_packs(message)


async def open_star_pack(user_id, key):
    if key not in STAR_PACKS:
        return None

    stars, amount, name = STAR_PACKS[key]

    async with aiosqlite.connect(DB) as db:
        db.row_factory = aiosqlite.Row

        cur = await db.execute(
            """
            SELECT stars
            FROM users
            WHERE user_id=?
            """,
            (user_id,)
        )

        user = await cur.fetchone()

        if not user or user["stars"] < stars:
            return None

        await db.execute(
            """
            UPDATE users
            SET stars=stars-?
            WHERE user_id=?
            """,
            (stars, user_id)
        )

        await db.commit()

    pulled = []

    user = await get_user(user_id)
    event = await get_active_event()

    for _ in range(amount):
        player = random_player(user, event)
        await add_card(user_id, player)
        await mission_update(user_id, "cards")
        pulled.append(player)

    return name, pulled


@DP.callback_query(F.data.startswith("pack:"))
async def pack_callback(callback: CallbackQuery):
    await callback.answer()

    await register(callback.from_user)

    key = callback.data.split(":", 1)[1]

    result = await open_star_pack(
        callback.from_user.id,
        key
    )

    if not result:
        stars = STAR_PACKS[key][0]

        await callback.message.answer(
            f"❌ Недостаточно Stars.\n\n"
            f"Нужно: <b>{stars} ⭐</b>",
            parse_mode="HTML"
        )

        return

    name, pulled = result

    best = max(
        pulled,
        key=lambda p: p[3]
    )

    await callback.message.answer(
        "📦 <b>ПАК ОТКРЫТ!</b>\n\n"
        f"{name}\n"
        f"🃏 Получено карт: <b>{len(pulled)}</b>\n\n"
        f"🔥 Лучшая карта:\n"
        f"{RARITY_EMOJI[best[4]]} "
        f"<b>{html.escape(best[0])}</b>\n"
        f"⭐ {best[3]} OVR\n"
        f"💰 €{best[5]:,}",
        parse_mode="HTML"
    )


# =========================================================
# COIN PACKS
# =========================================================

async def show_coinpacks(message):
    await register(message.from_user)

    if not await require_subscription(message):
        return

    kb = InlineKeyboardBuilder()

    for key, (price, amount, name) in COIN_PACKS.items():
        kb.button(
            text=f"{name} — {price:,} 🪙",
            callback_data=f"coinpack:{key}"
        )

    kb.adjust(1)

    await message.answer(
        "📦 <b>ПАКИ ЗА МОНЕТЫ</b>",
        reply_markup=kb.as_markup(),
        parse_mode="HTML"
    )


@DP.message(Command("coinpacks"))
async def coinpacks_command(message):
    await show_coinpacks(message)


@DP.callback_query(F.data.startswith("coinpack:"))
async def coinpack_callback(callback: CallbackQuery):
    await callback.answer()

    await register(callback.from_user)

    key = callback.data.split(":", 1)[1]

    if key not in COIN_PACKS:
        return

    price, amount, pack_name = COIN_PACKS[key]

    if not await spend_coins(
        callback.from_user.id,
        price
    ):
        await callback.message.answer(
            "❌ Недостаточно монет."
        )
        return

    user = await get_user(
        callback.from_user.id
    )

    event = await get_active_event()

    pulled = []

    for _ in range(amount):

        player = random_player(
            user,
            event
        )

        await add_card(
            callback.from_user.id,
            player
        )

        await mission_update(
            callback.from_user.id,
            "cards"
        )

        pulled.append(player)

    best = max(
        pulled,
        key=lambda p: p[3]
    )

    await callback.message.answer(
        "📦 <b>ПАК ОТКРЫТ!</b>\n\n"
        f"{pack_name}\n"
        f"🃏 Карт: <b>{amount}</b>\n\n"
        f"🔥 Лучшая:\n"
        f"{RARITY_EMOJI[best[4]]} "
        f"<b>{html.escape(best[0])}</b>\n"
        f"⭐ {best[3]} OVR\n"
        f"💰 €{best[5]:,}",
        parse_mode="HTML"
    )


# =========================================================
# MARKET / SELL TO BOT
# =========================================================

@DP.callback_query(F.data == "market")
async def market_callback(callback: CallbackQuery):
    await callback.answer()

    await register(callback.from_user)

    async with aiosqlite.connect(DB) as db:
        db.row_factory = aiosqlite.Row

        cur = await db.execute(
            """
            SELECT *
            FROM cards
            WHERE user_id=?
            ORDER BY rating DESC, id DESC
            LIMIT 20
            """,
            (callback.from_user.id,)
        )

        cards = await cur.fetchall()

    if not cards:
        await callback.message.answer(
            "🏪 <b>ПРОДАЖА КАРТ БОТУ</b>\n\n"
            "У тебя нет карт.",
            parse_mode="HTML"
        )
        return

    text = (
        "🏪 <b>ПРОДАТЬ КАРТУ БОТУ</b>\n\n"
        "Нажми на карту — бот купит её за указанную цену.\n\n"
    )

    kb = InlineKeyboardBuilder()

    for card in cards:
        text += (
            f"{RARITY_EMOJI.get(card['rarity'], '⚪')} "
            f"<b>{html.escape(card['name'])}</b> "
            f"— €{card['price']:,}\n"
        )

        kb.button(
            text=f"💰 Продать {card['name']}",
            callback_data=f"sell:{card['id']}"
        )

    kb.adjust(1)

    await callback.message.answer(
        text,
        reply_markup=kb.as_markup(),
        parse_mode="HTML"
    )


@DP.callback_query(F.data.startswith("sell:"))
async def sell_callback(callback: CallbackQuery):
    await callback.answer()

    try:
        card_id = int(
            callback.data.split(":")[1]
        )
    except Exception:
        return

    async with aiosqlite.connect(DB) as db:
        db.row_factory = aiosqlite.Row

        cur = await db.execute(
            """
            SELECT *
            FROM cards
            WHERE id=? AND user_id=?
            """,
            (
                card_id,
                callback.from_user.id,
            )
        )

        card = await cur.fetchone()

        if not card:
            await callback.message.answer(
                "❌ Карта уже продана или не найдена."
            )
            return

        price = card["price"]

        await db.execute(
            """
            DELETE FROM cards
            WHERE id=? AND user_id=?
            """,
            (
                card_id,
                callback.from_user.id,
            )
        )

        await db.execute(
            """
            UPDATE users
            SET coins=coins+?
            WHERE user_id=?
            """,
            (
                price,
                callback.from_user.id,
            )
        )

        await db.commit()

    await callback.message.answer(
        "💰 <b>КАРТА ПРОДАНА БОТУ!</b>\n\n"
        f"👤 {html.escape(card['name'])}\n"
        f"⭐ {card['rating']} OVR\n"
        f"💵 Получено: <b>{price:,} 🪙</b>",
        parse_mode="HTML"
    )


# =========================================================
# BALANCE
# =========================================================

@DP.message(Command("balance"))
async def balance_command(message):
    await register(message.from_user)

    user = await get_user(
        message.from_user.id
    )

    await message.answer(
        "💰 <b>ТВОЙ БАЛАНС</b>\n\n"
        f"🪙 Монеты: <b>{user['coins']:,}</b>\n"
        f"⭐ Stars: <b>{user['stars']}</b>",
        parse_mode="HTML"
    )


# =========================================================
# DAILY
# =========================================================

@DP.message(Command("daily"))
async def daily_command(message):
    await register(message.from_user)

    if not await require_subscription(message):
        return

    today = datetime.now(
        timezone.utc
    ).strftime("%Y-%m-%d")

    async with aiosqlite.connect(DB) as db:

        cur = await db.execute(
            """
            SELECT daily_date,daily_streak
            FROM users
            WHERE user_id=?
            """,
            (message.from_user.id,)
        )

        user = await cur.fetchone()

        if user[0] == today:
            await message.answer(
                "🎁 Daily уже получен сегодня."
            )
            return

        streak = user[1] + 1

        reward = 500 + (
            min(streak, 7) * 100
        )

        await db.execute(
            """
            UPDATE users
            SET daily_date=?, daily_streak=?
            WHERE user_id=?
            """,
            (
                today,
                streak,
                message.from_user.id,
            )
        )

        await db.commit()

    await add_coins(
        message.from_user.id,
        reward
    )

    await message.answer(
        "🎁 <b>DAILY ПОЛУЧЕН!</b>\n\n"
        f"🔥 Серия: <b>{streak}</b>\n"
        f"🪙 Награда: <b>+{reward:,}</b>",
        parse_mode="HTML"
    )


# =========================================================
# MISSIONS
# =========================================================

@DP.message(Command("missions"))
async def missions_command(message):
    await register(message.from_user)

    if not await require_subscription(message):
        return

    async with aiosqlite.connect(DB) as db:
        db.row_factory = aiosqlite.Row

        cur = await db.execute(
            """
            SELECT *
            FROM missions
            WHERE user_id=?
            """,
            (message.from_user.id,)
        )

        m = await cur.fetchone()

    await message.answer(
        "🎯 <b>ЗАДАНИЯ</b>\n\n"
        f"⚽ DROP: <b>{m['drops']}/10</b>\n"
        f"🃏 Карты: <b>{m['cards']}/20</b>\n\n"
        "🎁 Награды за выполнение можно добавить "
        "в следующей версии.",
        parse_mode="HTML"
    )


# =========================================================
# TOP
# =========================================================

@DP.message(Command("top"))
async def top_command(message):
    await register(message.from_user)

    if not await require_subscription(message):
        return

    async with aiosqlite.connect(DB) as db:
        cur = await db.execute(
            """
            SELECT user_id,username,first_name,coins
            FROM users
            WHERE banned=0
            ORDER BY coins DESC
            LIMIT 10
            """
        )

        rows = await cur.fetchall()

    text = "🏆 <b>ТОП 10</b>\n\n"

    for i, row in enumerate(rows, 1):

        name = row[1] or row[2] or "Игрок"

        text += (
            f"{i}. <b>{html.escape(name)}</b> "
            f"— {row[3]:,} 🪙\n"
        )

    await message.answer(
        text,
        parse_mode="HTML"
    )


# =========================================================
# PROMO
# =========================================================

@DP.message(Command("promo"))
async def promo_command(message):
    await register(message.from_user)

    if not await require_subscription(message):
        return

    parts = message.text.split()

    if len(parts) < 2:
        await message.answer(
            "🎟️ Использование:\n"
            "<code>/promo CODE</code>",
            parse_mode="HTML"
        )
        return

    code = parts[1].upper().strip()

    async with aiosqlite.connect(DB) as db:
        db.row_factory = aiosqlite.Row

        cur = await db.execute(
            """
            SELECT *
            FROM promo_codes
            WHERE code=?
            """,
            (code,)
        )

        promo = await cur.fetchone()

        if not promo:
            await message.answer(
                "❌ Промокод не найден."
            )
            return

        cur = await db.execute(
            """
            SELECT 1
            FROM promo_uses
            WHERE code=? AND user_id=?
            """,
            (
                code,
                message.from_user.id,
            )
        )

        used = await cur.fetchone()

        if used:
            await message.answer(
                "❌ Ты уже использовал этот промокод."
            )
            return

        if promo["used"] >= promo["activations"]:
            await message.answer(
                "❌ Лимит активаций закончился."
            )
            return

        await db.execute(
            """
            INSERT INTO promo_uses(code,user_id)
            VALUES(?,?)
            """,
            (
                code,
                message.from_user.id,
            )
        )

        await db.execute(
            """
            UPDATE promo_codes
            SET used=used+1
            WHERE code=?
            """,
            (code,)
        )

        await db.execute(
            """
            UPDATE users
            SET coins=coins+?, stars=stars+?
            WHERE user_id=?
            """,
            (
                promo["coins"],
                promo["stars"],
                message.from_user.id,
            )
        )

        await db.commit()

    await message.answer(
        "🎉 <b>ПРОМОКОД АКТИВИРОВАН!</b>\n\n"
        f"🪙 +{promo['coins']:,}\n"
        f"⭐ +{promo['stars']}",
        parse_mode="HTML"
    )


# =========================================================
# LUCKY CHARM STATUS
# =========================================================

@DP.message(Command("charm"))
async def charm_command(message):
    await register(message.from_user)

    if not await require_subscription(message):
        return

    async with aiosqlite.connect(DB) as db:
        db.row_factory = aiosqlite.Row

        cur = await db.execute(
            """
            SELECT *
            FROM lucky_charms
            WHERE user_id=?
            """,
            (message.from_user.id,)
        )

        charm = await cur.fetchone()

    if not charm:
        await message.answer(
            "🍀 <b>LUCKY CHARM</b>\n\n"
            "❌ Сейчас не активен.\n\n"
            "Купить можно в магазине.",
            parse_mode="HTML"
        )
        return

    left = charm["expires_at"] - int(time.time())

    if left <= 0:
        await message.answer(
            "🍀 Lucky Charm закончился."
        )
        return

    hours = left // 3600
    minutes = (left % 3600) // 60

    await message.answer(
        "🍀 <b>LUCKY CHARM АКТИВЕН</b>\n\n"
        "🔥 Повышенный шанс редких карт.\n"
        f"⏳ Осталось: <b>{hours}ч {minutes}м</b>",
        parse_mode="HTML"
    )


# =========================================================
# ADMIN / EVENTS
# =========================================================

@DP.message(Command("event"))
async def event_command(message):
    await register(message.from_user)

    if not is_owner(message.from_user):
        await message.answer(
            "❌ Только владелец бота."
        )
        return

    await message.answer(
        "👑 <b>ПАНЕЛЬ ИВЕНТОВ</b>\n\n"
        "Выбери ивент, который хочешь включить:",
        reply_markup=event_keyboard(),
        parse_mode="HTML"
    )


@DP.callback_query(F.data == "event_menu")
async def event_menu_callback(callback):
    await callback.answer()

    if not is_owner(callback.from_user):
        return

    await callback.message.answer(
        "👑 <b>ВЫБЕРИ ИВЕНТ</b>\n\n"
        "Нажми на нужный ивент:",
        reply_markup=event_keyboard(),
        parse_mode="HTML"
    )


@DP.callback_query(F.data.startswith("event_select:"))
async def event_select_callback(callback):
    await callback.answer()

    if not is_owner(callback.from_user):
        await callback.answer(
            "❌ Нет доступа.",
            show_alert=True
        )
        return

    event_key = callback.data.split(":", 1)[1]

    if event_key not in EVENTS:
        return

    event = EVENTS[event_key]

    await callback.message.answer(
        f"{event['name']}\n\n"
        f"📋 {event['description']}\n\n"
        "⏳ <b>На сколько включить?</b>",
        reply_markup=event_duration_keyboard(event_key),
        parse_mode="HTML"
    )


@DP.callback_query(F.data.startswith("event_start:"))
async def event_start_callback(callback):
    await callback.answer()

    if not is_owner(callback.from_user):
        return

    parts = callback.data.split(":")

    if len(parts) != 3:
        return

    event_key = parts[1]

    try:
        minutes = int(parts[2])
    except ValueError:
        return

    if event_key not in EVENTS:
        return

    # Останавливаем старый ивент
    await stop_event()

    # Запускаем новый
    await start_event(
        event_key,
        minutes
    )

    event = EVENTS[event_key]

    if minutes == 0:
        duration = "♾ НАВСЕГДА"
    elif minutes < 60:
        duration = f"{minutes} минут"
    elif minutes == 60:
        duration = "1 час"
    else:
        duration = f"{minutes // 60} часов"

    await callback.message.answer(
        "🚨 <b>ИВЕНТ ВКЛЮЧЁН!</b>\n\n"
        f"{event['name']}\n"
        f"📋 {event['description']}\n"
        f"⏳ Длительность: <b>{duration}</b>",
        parse_mode="HTML"
    )

    # Уведомляем пользователей в фоне
    asyncio.create_task(
        notify_event_started(
            event_key,
            minutes
        )
    )


@DP.callback_query(F.data == "event_stop")
async def event_stop_callback(callback):
    await callback.answer()

    if not is_owner(callback.from_user):
        return

    active = await get_active_event()

    if not active:
        await callback.message.answer(
            "ℹ️ Сейчас нет активного ивента."
        )
        return

    event_key = active["event_key"]

    await stop_event()

    event = EVENTS.get(event_key)

    await callback.message.answer(
        "⛔ <b>ИВЕНТ ОСТАНОВЛЕН!</b>\n\n"
        f"{event['name'] if event else event_key}",
        parse_mode="HTML"
    )


@DP.message(Command("events"))
async def events_command(message):
    await register(message.from_user)

    if not is_owner(message.from_user):
        await message.answer(
            "❌ Только владелец бота."
        )
        return

    active = await get_active_event()

    if not active:
        await message.answer(
            "📭 Сейчас активных ивентов нет."
        )
        return

    event = EVENTS.get(
        active["event_key"]
    )

    if not event:
        return

    if active["expires_at"] == 0:
        left = "♾ навсегда"
    else:
        seconds = active["expires_at"] - int(time.time())

        if seconds <= 0:
            await stop_event()
            await message.answer(
                "📭 Ивент уже закончился."
            )
            return

        left = (
            f"{seconds // 3600}ч "
            f"{(seconds % 3600) // 60}м "
            f"{seconds % 60}с"
        )

    await message.answer(
        "🚨 <b>АКТИВНЫЙ ИВЕНТ</b>\n\n"
        f"{event['name']}\n"
        f"📋 {event['description']}\n"
        f"⏳ Осталось: <b>{left}</b>",
        parse_mode="HTML"
    )


# =========================================================
# ADMIN COMMANDS
# =========================================================

@DP.message(Command("stats"))
async def stats_command(message):
    await register(message.from_user)

    if not is_owner(message.from_user):
        return

    async with aiosqlite.connect(DB) as db:

        cur = await db.execute(
            "SELECT COUNT(*) FROM users"
        )
        users = (await cur.fetchone())[0]

        cur = await db.execute(
            "SELECT COUNT(*) FROM cards"
        )
        cards = (await cur.fetchone())[0]

        cur = await db.execute(
            "SELECT SUM(coins) FROM users"
        )
        coins = (await cur.fetchone())[0] or 0

    await message.answer(
        "👑 <b>СТАТИСТИКА</b>\n\n"
        f"👥 Пользователей: <b>{users}</b>\n"
        f"🃏 Карт: <b>{cards}</b>\n"
        f"🪙 Монет в системе: <b>{coins:,}</b>",
        parse_mode="HTML"
    )


@DP.message(Command("give"))
async def give_command(message):
    await register(message.from_user)

    if not is_owner(message.from_user):
        return

    parts = message.text.split()

    if len(parts) != 3:
        await message.answer(
            "Использование:\n"
            "<code>/give USER_ID COINS</code>",
            parse_mode="HTML"
        )
        return

    try:
        user_id = int(parts[1])
        amount = int(parts[2])
    except ValueError:
        await message.answer(
            "❌ Неверные данные."
        )
        return

    await add_coins(
        user_id,
        amount
    )

    await message.answer(
        f"✅ Выдано <b>{amount:,} 🪙</b>\n"
        f"👤 ID: <code>{user_id}</code>",
        parse_mode="HTML"
    )


@DP.message(Command("ban"))
async def ban_command(message):
    if not is_owner(message.from_user):
        return

    parts = message.text.split()

    if len(parts) != 2:
        return

    try:
        user_id = int(parts[1])
    except ValueError:
        return

    async with aiosqlite.connect(DB) as db:
        await db.execute(
            """
            UPDATE users
            SET banned=1
            WHERE user_id=?
            """,
            (user_id,)
        )
        await db.commit()

    await message.answer(
        f"🚫 Пользователь <code>{user_id}</code> заблокирован.",
        parse_mode="HTML"
    )


@DP.message(Command("unban"))
async def unban_command(message):
    if not is_owner(message.from_user):
        return

    parts = message.text.split()

    if len(parts) != 2:
        return

    try:
        user_id = int(parts[1])
    except ValueError:
        return

    async with aiosqlite.connect(DB) as db:
        await db.execute(
            """
            UPDATE users
            SET banned=0
            WHERE user_id=?
            """,
            (user_id,)
        )
        await db.commit()

    await message.answer(
        f"✅ Пользователь <code>{user_id}</code> разблокирован.",
        parse_mode="HTML"
    )


# =========================================================
# CALLBACKS
# =========================================================

@DP.callback_query(F.data == "drop")
async def drop_callback(callback):
    await callback.answer()
    await do_drop(callback.message)


@DP.callback_query(F.data == "collection")
async def collection_callback(callback):
    await callback.answer()
    await show_collection(callback.message)


@DP.callback_query(F.data == "profile")
async def profile_callback(callback):
    await callback.answer()
    await show_profile(callback.message)


@DP.callback_query(F.data == "shop")
async def shop_callback(callback):
    await callback.answer()
    await show_shop(callback.message)


@DP.callback_query(F.data == "packs")
async def packs_callback(callback):
    await callback.answer()
    await show_packs(callback.message)


@DP.callback_query(F.data == "coinpacks")
async def coinpacks_callback(callback):
    await callback.answer()
    await show_coinpacks(callback.message)


@DP.callback_query(F.data == "lucky")
async def lucky_callback(callback):
    await callback.answer()
    await send_lucky_invoice(
        callback.from_user.id
    )


@DP.callback_query(F.data == "daily")
async def daily_callback(callback):
    await callback.answer()

    # вызываем ту же логику Daily
    await daily_command(
        callback.message
    )


@DP.callback_query(F.data == "missions")
async def missions_callback(callback):
    await callback.answer()

    await missions_command(
        callback.message
    )


@DP.callback_query(F.data == "top")
async def top_callback(callback):
    await callback.answer()

    await top_command(
        callback.message
    )


@DP.callback_query(F.data == "promo")
async def promo_callback(callback):
    await callback.answer()

    await callback.message.answer(
        "🎟️ Введи промокод командой:\n\n"
        "<code>/promo CODE</code>",
        parse_mode="HTML"
    )


@DP.callback_query(F.data == "back_main")
async def back_main_callback(callback):
    await callback.answer()

    user = await get_user(
        callback.from_user.id
    )

    await callback.message.answer(
        "⚽ <b>FOOTBALL DROP</b>\n\n"
        "Главное меню:",
        reply_markup=main_keyboard(
            callback.from_user
        ),
        parse_mode="HTML"
    )


@DP.callback_query(F.data == "check_sub")
async def check_sub_callback(callback):
    await callback.answer()

    if await check_access(
        callback.from_user.id
    ):
        await callback.message.answer(
            "✅ <b>Подписка подтверждена!</b>\n\n"
            "Теперь можешь пользоваться ботом.",
            reply_markup=main_keyboard(
                callback.from_user
            ),
            parse_mode="HTML"
        )
    else:
        await callback.message.answer(
            "❌ Подписка не найдена.\n\n"
            "Подпишись на канал и нажми кнопку ещё раз."
        )


# =========================================================
# TELEGRAM STARS PAYMENTS
# =========================================================

@DP.pre_checkout_query()
async def pre_checkout_query(
    query: PreCheckoutQuery
):
    await query.answer(
        ok=True
    )


@DP.message(F.successful_payment)
async def successful_payment(
    message: Message
):
    payment = message.successful_payment

    payload = payment.invoice_payload

    await register(message.from_user)

    if payload.startswith("lucky:"):

        expires = (
            int(time.time())
            + LUCKY_HOURS * 60 * 60
        )

        async with aiosqlite.connect(DB) as db:

            await db.execute(
                """
                INSERT INTO lucky_charms
                (user_id,expires_at)
                VALUES(?,?)
                ON CONFLICT(user_id)
                DO UPDATE SET
                    expires_at=excluded.expires_at
                """,
                (
                    message.from_user.id,
                    expires,
                )
            )

            await db.execute(
                """
                INSERT INTO payments
                (user_id,product,stars,created)
                VALUES(?,?,?,?)
                """,
                (
                    message.from_user.id,
                    "lucky_charm",
                    payment.total_amount,
                    int(time.time()),
                )
            )

            await db.commit()

        await message.answer(
            "🍀 <b>LUCKY CHARM АКТИВИРОВАН!</b>\n\n"
            "🔥 Повышенный шанс редких карт.\n"
            "⏳ Длительность: <b>24 часа</b>.",
            parse_mode="HTML"
        )


# =========================================================
# ERROR-SAFE POLLING
# =========================================================

async def main():

    await init_db()

    print("===================================")
    print("⚽ FOOTBALL DROP запущен")
    print(f"👑 OWNER: @{OWNER}")
    print("⏰ DROP COOLDOWN: 1 HOUR")
    print("🎯 EVENTS: ENABLED")
    print("===================================")

    await DP.start_polling(
        BOT,
        allowed_updates=DP.resolve_used_update_types()
    )


if __name__ == "__main__":
    asyncio.run(main())
