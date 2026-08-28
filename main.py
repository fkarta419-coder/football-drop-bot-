# main.py
# FOOTBALL DROP — ПОЛНАЯ ВЕРСИЯ С 300+ ИГРОКАМИ

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
# 300+ ИГРОКОВ
# =========================================================
PLAYERS = [
    # ===== COMMON (80+) =====
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
    ("Нико Уильямс", "🇪🇸", "LW", 80, "Common", 7500),
    ("Ферран Торрес", "🇪🇸", "RW", 80, "Common", 7200),
    ("Алекс Баэна", "🇪🇸", "CAM", 80, "Common", 7100),
    ("Микель Мерино", "🇪🇸", "CM", 80, "Common", 7000),
    ("Марк Кукурелья", "🇪🇸", "LB", 80, "Common", 6800),
    ("Пау Торрес", "🇪🇸", "CB", 80, "Common", 6900),
    ("Аймерик Лапорт", "🇪🇸", "CB", 80, "Common", 7000),
    ("Дани Карвахаль", "🇪🇸", "RB", 80, "Common", 7300),
    ("Андреа Камбьязо", "🇮🇹", "LB", 80, "Common", 6800),
    ("Алессандро Бастони", "🇮🇹", "CB", 80, "Common", 7000),
    ("Франческо Ачерби", "🇮🇹", "CB", 80, "Common", 6700),
    ("Джанлука Манчини", "🇮🇹", "CB", 80, "Common", 6600),
    ("Давиде Фраттези", "🇮🇹", "CM", 80, "Common", 6900),
    ("Лоренцо Пеллегрини", "🇮🇹", "CAM", 80, "Common", 7100),
    ("Федерико Димарко", "🇮🇹", "LB", 80, "Common", 7200),
    ("Мойзе Кин", "🇮🇹", "ST", 80, "Common", 6800),
    ("Маттиа Дзакканьи", "🇮🇹", "LW", 80, "Common", 7000),
    ("Жоржиньо", "🇮🇹", "CM", 80, "Common", 6900),
    ("Доменико Берарди", "🇮🇹", "RW", 80, "Common", 7100),
    ("Бенжамен Павар", "🇫🇷", "CB", 80, "Common", 6900),
    ("Ибраима Конате", "🇫🇷", "CB", 80, "Common", 7000),
    ("Уильям Салиба", "🇫🇷", "CB", 80, "Common", 7100),
    ("Люка Эрнандес", "🇫🇷", "CB", 80, "Common", 7200),
    ("Усман Дембеле", "🇫🇷", "RW", 80, "Common", 7400),
    ("Кингсли Коман", "🇫🇷", "LW", 80, "Common", 7300),
    ("Эдуардо Камавинга", "🇫🇷", "CM", 80, "Common", 7200),
    ("Орельен Тчуамени", "🇫🇷", "CDM", 80, "Common", 7100),
    ("Адриен Рабьо", "🇫🇷", "CM", 80, "Common", 6900),
    ("Рандаль Коло Муани", "🇫🇷", "ST", 80, "Common", 7000),
    ("Маркус Тюрам", "🇫🇷", "ST", 80, "Common", 7100),
    ("Брэдли Баркола", "🇫🇷", "LW", 80, "Common", 6900),
    ("Дезире Дуэ", "🇫🇷", "CAM", 80, "Common", 6800),
    ("Лоис Опенда", "🇧🇪", "ST", 80, "Common", 7000),
    ("Ромелу Лукаку", "🇧🇪", "ST", 80, "Common", 7200),
    ("Юри Тилеманс", "🇧🇪", "CM", 80, "Common", 6900),
    ("Амаду Онана", "🇧🇪", "CDM", 80, "Common", 6800),
    ("Йохан Бакайоко", "🇧🇪", "RW", 80, "Common", 6700),
    ("Кеннет Тейлор", "🇳🇱", "CM", 80, "Common", 6800),
    ("Маттейс де Лигт", "🇳🇱", "CB", 80, "Common", 7200),
    ("Натан Аке", "🇳🇱", "CB", 80, "Common", 6900),
    ("Дензел Дюмфрис", "🇳🇱", "RB", 80, "Common", 7100),
    ("Мемфис Депай", "🇳🇱", "ST", 80, "Common", 7000),
    ("Коди Гакпо", "🇳🇱", "LW", 80, "Common", 7300),
    ("Тён Копмейнерс", "🇳🇱", "CM", 80, "Common", 6900),
    ("Райан Гравенберх", "🇳🇱", "CM", 80, "Common", 7000),
    ("Майки Мур", "🏴", "RW", 78, "Common", 5200),
    ("Эберечи Эзе", "🏴", "CAM", 80, "Common", 7000),
    ("Энтони Гордон", "🏴", "LW", 80, "Common", 6900),
    ("Джеймс Мэддисон", "🏴", "CAM", 80, "Common", 7200),
    ("Морган Гиббс-Уайт", "🏴", "CAM", 80, "Common", 6800),
    ("Адам Уортон", "🏴", "CM", 80, "Common", 6700),
    ("Кайл Уокер", "🏴", "RB", 80, "Common", 7100),
    ("Джон Стоунз", "🏴", "CB", 80, "Common", 7000),
    ("Люк Шоу", "🏴", "LB", 80, "Common", 6900),
    ("Киран Триппьер", "🏴", "RB", 80, "Common", 6800),
    ("Иван Перишич", "🇭🇷", "LW", 80, "Common", 6900),
    ("Матео Ковачич", "🇭🇷", "CM", 80, "Common", 7000),
    ("Иосип Сутало", "🇭🇷", "CB", 80, "Common", 6700),
    ("Йошко Гвардиол", "🇭🇷", "CB", 80, "Common", 7200),
    ("Бруно Петкович", "🇭🇷", "ST", 80, "Common", 6800),
    ("Дани Ольмо", "🇪🇸", "CAM", 80, "Common", 7100),
    ("Андрей Крамарич", "🇭🇷", "ST", 80, "Common", 6900),
    ("Никола Влашич", "🇭🇷", "CAM", 80, "Common", 6800),
    ("Лука Модрич", "🇭🇷", "CM", 80, "Common", 7500),
    ("Мануэль Угарте", "🇺🇾", "CDM", 80, "Common", 6900),
    ("Факундо Пельистри", "🇺🇾", "RW", 79, "Common", 6400),
    ("Максимилиано Араухо", "🇺🇾", "LW", 80, "Common", 6800),

    # ===== RARE (60+) =====
    ("Кобби Майну", "🏴", "CM", 81, "Rare", 10000),
    ("Кристиан Пулишич", "🇺🇸", "LW", 82, "Rare", 12000),
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
    ("Лаутаро Мартинес", "🇦🇷", "ST", 82, "Rare", 13500),
    ("Кристиан Ромеро", "🇦🇷", "CB", 82, "Rare", 13000),
    ("Лисандро Мартинес", "🇦🇷", "CB", 81, "Rare", 11500),
    ("Николас Отаменди", "🇦🇷", "CB", 81, "Rare", 11000),
    ("Леандро Паредес", "🇦🇷", "CDM", 81, "Rare", 11200),
    ("Анхель Корреа", "🇦🇷", "RW", 81, "Rare", 10800),
    ("Родриго Де Пауль", "🇦🇷", "CM", 82, "Rare", 12500),
    ("Николас Гонсалес", "🇦🇷", "LW", 82, "Rare", 12000),
    ("Савио", "🇧🇷", "RW", 81, "Rare", 11500),
    ("Эстевао", "🇧🇷", "RW", 81, "Rare", 11000),
    ("Витор Роке", "🇧🇷", "ST", 81, "Rare", 10800),
    ("Андре Сантос", "🇧🇷", "CM", 81, "Rare", 10500),
    ("Жоау Невеш", "🇵🇹", "CM", 82, "Rare", 12500),
    ("Витинья", "🇵🇹", "CM", 82, "Rare", 12800),
    ("Нуну Мендеш", "🇵🇹", "LB", 82, "Rare", 13000),
    ("Диогу Жота", "🇵🇹", "ST", 82, "Rare", 13200),
    ("Педру Нету", "🇵🇹", "RW", 82, "Rare", 12500),
    ("Диогу Кошта", "🇵🇹", "GK", 82, "Rare", 12800),
    ("Рубен Диаш", "🇵🇹", "CB", 82, "Rare", 13500),
    ("Вильям Карвалью", "🇵🇹", "CDM", 81, "Rare", 11500),
    ("Рикарду Орта", "🇵🇹", "LW", 81, "Rare", 11200),
    ("Матеус Нунес", "🇵🇹", "CM", 81, "Rare", 11000),
    ("Бенуа Бадьяшиль", "🇫🇷", "CB", 81, "Rare", 11500),
    ("Леви Колвилл", "🏴", "CB", 81, "Rare", 11200),
    ("Мало Гюсто", "🇫🇷", "RB", 81, "Rare", 10800),
    ("Рис Джеймс", "🏴", "RB", 82, "Rare", 12500),
    ("Николас Джексон", "🇸🇳", "ST", 82, "Rare", 12800),
    ("Мойсес Кайседо", "🇪🇨", "CDM", 82, "Rare", 13000),
    ("Ромео Лавия", "🇧🇪", "CDM", 81, "Rare", 11000),
    ("Марк Гехи", "🏴", "CB", 82, "Rare", 12500),
    ("Жан-Филипп Матета", "🇫🇷", "ST", 81, "Rare", 11500),
    ("Джаррод Боуэн", "🏴", "RW", 82, "Rare", 12800),
    ("Лукас Пакета", "🇧🇷", "CAM", 82, "Rare", 13000),
    ("Пьеро Инкапье", "🇪🇨", "CB", 81, "Rare", 11200),
    ("Пьер-Эмерик Обамеянг", "🇬🇦", "ST", 81, "Rare", 11800),
    ("Садио Мане", "🇸🇳", "LW", 82, "Rare", 13500),
    ("Калиду Кулибали", "🇸🇳", "CB", 81, "Rare", 11500),
    ("Идрисса Гейе", "🇸🇳", "CDM", 81, "Rare", 11000),
    ("Исмаила Сарр", "🇸🇳", "RW", 81, "Rare", 11200),
    ("Майрон Боаду", "🇳🇱", "ST", 81, "Rare", 10800),
    ("Арно Данджума", "🇳🇱", "LW", 81, "Rare", 11000),
    ("Стивен Бергвейн", "🇳🇱", "LW", 81, "Rare", 11500),
    ("Ваут Вегхорст", "🇳🇱", "ST", 81, "Rare", 11200),
    ("Ноа Ланг", "🇳🇱", "LW", 81, "Rare", 10800),
    ("Ибрагим Сангари", "🇨🇮", "CDM", 81, "Rare", 11000),
    ("Секу Койта", "🇲🇱", "ST", 81, "Rare", 10800),
    ("Мохамед Эль-Шеннави", "🇪🇬", "GK", 81, "Rare", 11200),
    ("Махмуд Хассан", "🇪🇬", "LW", 81, "Rare", 10800),
    ("Трезеге", "🇪🇬", "LW", 81, "Rare", 11000),
    ("Омар Мармуш", "🇪🇬", "ST", 82, "Rare", 12500),
    ("Мостафа Мохамед", "🇪🇬", "ST", 81, "Rare", 11200),
    ("Андре Онана", "🇨🇲", "GK", 82, "Rare", 12800),
    ("Брайан Мбемо", "🇨🇲", "RW", 82, "Rare", 12500),
    ("Карл Токо Экамби", "🇨🇲", "LW", 81, "Rare", 11500),
    ("Йереми Пино", "🇪🇸", "RW", 81, "Rare", 11200),
    ("Микель Весга", "🇪🇸", "CM", 81, "Rare", 11000),
    ("Серхио Регилон", "🇪🇸", "LB", 81, "Rare", 10800),
    ("Тьяско Сеговия", "🇻🇪", "CM", 81, "Rare", 10800),
    ("Тадео Альенде", "🇦🇷", "RW", 81, "Rare", 10800),
    ("Луис Суарес", "🇺🇾", "ST", 82, "Rare", 13500),

    # ===== SUPER RARE (50+) =====
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
    ("Тео Эрнандес", "🇫🇷", "LB", 84, "Super Rare", 22000),
    ("Люка Эрнандес", "🇫🇷", "CB", 84, "Super Rare", 21000),
    ("Бенжамен Павар", "🇫🇷", "RB", 84, "Super Rare", 21000),
    ("Ибраима Конате", "🇫🇷", "CB", 84, "Super Rare", 21500),
    ("Уильям Салиба", "🇫🇷", "CB", 84, "Super Rare", 22000),
    ("Антони", "🇧🇷", "RW", 84, "Super Rare", 20000),
    ("Габриэл Мартинелли", "🇧🇷", "LW", 84, "Super Rare", 21000),
    ("Бруно Гимараэс", "🇧🇷", "CM", 85, "Super Rare", 24000),
    ("Дуглас Луис", "🇧🇷", "CM", 84, "Super Rare", 21000),
    ("Жоао Педро", "🇧🇷", "ST", 84, "Super Rare", 21000),
    ("Эдерсон", "🇧🇷", "GK", 85, "Super Rare", 23000),
    ("Маркиньос", "🇧🇷", "CB", 85, "Super Rare", 24000),
    ("Габриэл Магальяйнс", "🇧🇷", "CB", 84, "Super Rare", 21500),
    ("Эмерсон Роял", "🇧🇷", "RB", 84, "Super Rare", 20000),
    ("Каземиро", "🇧🇷", "CDM", 84, "Super Rare", 22000),
    ("Фабиньо", "🇧🇷", "CDM", 84, "Super Rare", 21000),
    ("Анхель Ди Мария", "🇦🇷", "RW", 84, "Super Rare", 22000),
    ("Пауло Дибала", "🇦🇷", "CAM", 85, "Super Rare", 23500),
    ("Алексис Мак Аллистер", "🇦🇷", "CM", 85, "Super Rare", 24000),
    ("Эмилиано Мартинес", "🇦🇷", "GK", 85, "Super Rare", 23000),
    ("Кристиан Ромеро", "🇦🇷", "CB", 85, "Super Rare", 23500),
    ("Лисандро Мартинес", "🇦🇷", "CB", 84, "Super Rare", 21000),
    ("Николас Отаменди", "🇦🇷", "CB", 84, "Super Rare", 20000),
    ("Леандро Паредес", "🇦🇷", "CDM", 84, "Super Rare", 20000),
    ("Анхель Корреа", "🇦🇷", "RW", 84, "Super Rare", 20500),
    ("Родриго Де Пауль", "🇦🇷", "CM", 84, "Super Rare", 21500),
    ("Николас Гонсалес", "🇦🇷", "LW", 84, "Super Rare", 21000),
    ("Савио", "🇧🇷", "RW", 84, "Super Rare", 20500),
    ("Эстевао", "🇧🇷", "RW", 84, "Super Rare", 20000),
    ("Витор Роке", "🇧🇷", "ST", 84, "Super Rare", 20000),
    ("Жоау Невеш", "🇵🇹", "CM", 84, "Super Rare", 21500),
    ("Витинья", "🇵🇹", "CM", 84, "Super Rare", 22000),
    ("Нуну Мендеш", "🇵🇹", "LB", 84, "Super Rare", 21500),
    ("Диогу Жота", "🇵🇹", "ST", 84, "Super Rare", 22000),
    ("Педру Нету", "🇵🇹", "RW", 84, "Super Rare", 21000),
    ("Диогу Кошта", "🇵🇹", "GK", 84, "Super Rare", 21000),
    ("Рубен Диаш", "🇵🇹", "CB", 85, "Super Rare", 24000),
    ("Матеус Нунес", "🇵🇹", "CM", 84, "Super Rare", 21000),

    # ===== EPIC (30+) =====
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
    ("Рафинья", "🇧🇷", "LW", 90, "Epic", 50000),
    ("Бернарду Силва", "🇵🇹", "CAM", 88, "Epic", 43000),
    ("Фил Фоден", "🏴", "RW", 88, "Epic", 43000),
    ("Кевин Де Брёйне", "🇧🇪", "CAM", 89, "Epic", 48000),
    ("Салиба", "🇫🇷", "CB", 88, "Epic", 40000),
    ("Рюдигер", "🇩🇪", "CB", 88, "Epic", 40000),
    ("Хакими", "🇲🇦", "RB", 88, "Epic", 43000),
    ("Гарри Кейн", "🏴", "ST", 90, "Epic", 52000),
    ("Левандовски", "🇵🇱", "ST", 89, "Epic", 48000),
    ("Сон Хын Мин", "🇰🇷", "LW", 89, "Epic", 45000),
    ("Кварацхелия", "🇬🇪", "LW", 89, "Epic", 46000),
    ("Осимхен", "🇳🇬", "ST", 89, "Epic", 45000),
    ("Влахович", "🇷🇸", "ST", 88, "Epic", 41000),
    ("Вальверде", "🇺🇾", "CM", 88, "Epic", 42000),
    ("Энцо Фернандес", "🇦🇷", "CM", 88, "Epic", 41000),
    ("Дани Ольмо", "🇪🇸", "CAM", 88, "Epic", 42000),
    ("Педри", "🇪🇸", "CM", 88, "Epic", 43000),

    # ===== LEGENDARY (20+) =====
    ("Мохамед Салах", "🇪🇬", "RW", 90, "Legendary", 70000),
    ("Садио Мане", "🇸🇳", "LW", 89, "Legendary", 55000),
    ("Карим Бензема", "🇫🇷", "ST", 91, "Legendary", 75000),
    ("Кевин Де Брюйне", "🇧🇪", "CM", 91, "Legendary", 80000),
    ("Эден Азар", "🇧🇪", "LW", 89, "Legendary", 60000),
    ("Роберт Левандовски", "🇵🇱", "ST", 90, "Legendary", 72000),
    ("Гарри Кейн", "🏴", "ST", 90, "Legendary", 70000),
    ("Сон Хын Мин", "🇰🇷", "LW", 89, "Legendary", 58000),
    ("Мануэль Нойер", "🇩🇪", "GK", 90, "Legendary", 65000),
    ("Тибо Куртуа", "🇧🇪", "GK", 90, "Legendary", 68000),
    ("Вирджил Ван Дейк", "🇳🇱", "CB", 90, "Legendary", 72000),
    ("Серхио Рамос", "🇪🇸", "CB", 89, "Legendary", 62000),
    ("Джорджио Кьеллини", "🇮🇹", "CB", 89, "Legendary", 59000),
    ("Килиан Мбаппе", "🇫🇷", "ST", 92, "Legendary", 85000),
    ("Эрлинг Холанд", "🇳🇴", "ST", 91, "Legendary", 80000),
    ("Джуд Беллингем", "🏴", "CAM", 90, "Legendary", 75000),
    ("Неймар", "🇧🇷", "LW", 91, "Legendary", 90000),
    ("Антуан Гризманн", "🇫🇷", "CF", 89, "Legendary", 70000),
    ("Винисиус Жуниор", "🇧🇷", "LW", 91, "Legendary", 85000),
    ("Ламин Ямаль", "🇪🇸", "RW", 90, "Legendary", 70000),

    # ===== ICON (15+) =====
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
    ("Роналдо Назарио", "🇧🇷", "ST", 97, "Icon", 250000),
    ("Марадона", "🇦🇷", "CAM", 97, "Icon", 300000),
    ("Кака", "🇧🇷", "CAM", 95, "Icon", 200000),
    ("Тьерри Анри", "🇫🇷", "ST", 96, "Icon", 220000),
    ("Иньеста", "🇪🇸", "CM", 96, "Icon", 220000),
    ("Мальдини", "🇮🇹", "CB", 96, "Icon", 230000),

    # ===== ULTIMATE (6) =====
    ("Месси Ultimate", "🇦🇷", "RW", 99, "Ultimate", 500000),
    ("Роналду Ultimate", "🇵🇹", "ST", 99, "Ultimate", 500000),
    ("Пеле Ultimate", "🇧🇷", "ST", 99, "Ultimate", 500000),
    ("Марадона Ultimate", "🇦🇷", "CAM", 99, "Ultimate", 500000),
    ("Кройф Ultimate", "🇳🇱", "LW", 99, "Ultimate", 500000),
    ("Зидан Ultimate", "🇫🇷", "CAM", 99, "Ultimate", 500000),
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

# =========================================================
# ИНИЦИАЛИЗАЦИЯ БД
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
            banned INTEGER DEFAULT 0,
            battle_wins INTEGER DEFAULT 0,
            battle_losses INTEGER DEFAULT 0,
            battles_played INTEGER DEFAULT 0
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
            upgrade_level INTEGER DEFAULT 0,
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
        CREATE TABLE IF NOT EXISTS marketplace(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            seller_id INTEGER NOT NULL,
            card_id INTEGER NOT NULL,
            price INTEGER NOT NULL,
            created_at INTEGER NOT NULL,
            sold INTEGER DEFAULT 0
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
        CREATE TABLE IF NOT EXISTS trades(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sender_id INTEGER NOT NULL,
            receiver_id INTEGER NOT NULL,
            sender_card_id INTEGER NOT NULL,
            receiver_card_id INTEGER NOT NULL,
            status TEXT DEFAULT 'pending',
            created_at INTEGER NOT NULL
        )""")

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
        cur = await db.execute("SELECT * FROM users WHERE user_id=?", (user_id,))
        return await cur.fetchone()

async def count_cards(user_id):
    async with aiosqlite.connect(DB) as db:
        cur = await db.execute("SELECT COUNT(*) FROM cards WHERE user_id=?", (user_id,))
        return (await cur.fetchone())[0]

async def add_coins(user_id, amount):
    async with aiosqlite.connect(DB) as db:
        await db.execute("UPDATE users SET coins=coins+? WHERE user_id=?", (amount, user_id))
        await db.commit()

async def spend_coins(user_id, amount):
    async with aiosqlite.connect(DB) as db:
        cur = await db.execute("SELECT coins,banned FROM users WHERE user_id=?", (user_id,))
        row = await cur.fetchone()
        if not row or row[1] or row[0] < amount:
            return False
        await db.execute("UPDATE users SET coins=coins-? WHERE user_id=?", (amount, user_id))
        await db.commit()
        return True

async def add_card(user_id, player):
    name, nation, position, rating, rarity, price = player
    async with aiosqlite.connect(DB) as db:
        await db.execute("""
            INSERT INTO cards (user_id,name,nation,position,rating,rarity,price,created_at)
            VALUES(?,?,?,?,?,?,?,?)
        """, (user_id, name, nation, position, rating, rarity, price, int(time.time())))
        await db.commit()
        return True

async def mission_update(user_id, field, amount=1):
    if field not in ("drops", "cards"):
        return
    async with aiosqlite.connect(DB) as db:
        await db.execute(f"UPDATE missions SET {field}={field}+? WHERE user_id=?", (amount, user_id))
        await db.commit()

def is_owner(user):
    return (user.username or "").lower() == OWNER.lower()

async def check_access(user_id):
    if not REQUIRED_CHANNEL:
        return True
    try:
        member = await BOT.get_chat_member(REQUIRED_CHANNEL, user_id)
        return member.status in ("creator", "administrator", "member")
    except Exception:
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
    if await check_access(message.from_user.id):
        return True
    await message.answer(
        "🔒 <b>ТРЕБУЕТСЯ ПОДПИСКА НА КАНАЛ</b>\n\n"
        "Для использования всех функций бота нужно подписаться на наш канал:\n"
        f"{CHANNEL_LINK}\n\n"
        "После подписки нажми «Проверить подписку»",
        reply_markup=subscribe_keyboard(),
        parse_mode="HTML"
    )
    return False

def choose_rarity(user=None):
    names = list(RARITIES.keys())
    weights = list(RARITIES.values())
    if user and user["lucky_until"] > int(time.time()):
        weights = [weights[i] * (1 if names[i] == "Common" else 3) for i in range(len(names))]
    return random.choices(names, weights=weights, k=1)[0]

def random_player(user=None):
    rarity = choose_rarity(user)
    pool = [p for p in PLAYERS if p[4] == rarity]
    return random.choice(pool or PLAYERS)

def main_keyboard(user=None):
    kb = InlineKeyboardBuilder()
    buttons = [
        ("🃏 DROP", "drop"),
        ("📚 Коллекция", "collection"),
        ("👤 Профиль", "profile"),
        ("🛒 Магазин", "shop"),
        ("🏪 Рынок", "market"),
        ("🏪 Marketplace", "marketplace"),
        ("🎁 Daily", "daily"),
        ("🎯 Задания", "missions"),
        ("🏆 Рейтинг", "top"),
        ("📦 Паки за 🪙", "coinpacks"),
        ("⭐ Паки за Stars", "packs"),
        ("🎟️ Промокод", "promo"),
        ("🍀 Lucky Charm", "lucky"),
        ("📋 Все игроки", "players"),
        ("⚔️ PvP", "pvp_menu"),
        ("🏆 Состав", "team_menu"),
        ("🤖 AI Битва", "ai_battle"),
        ("📈 Прокачка", "upgrade_menu"),
        ("🎰 Рулетка", "roulette"),
        ("🔨 Крафт", "craft"),
        ("👥 Рефералка", "referral"),
        ("🔄 Обмен", "trade_menu"),
    ]
    if user and is_owner(user):
        buttons.append(("👑 Owner", "owner_panel"))
    for text, data in buttons:
        kb.button(text=text, callback_data=data)
    kb.adjust(2)
    return kb.as_markup()

# =========================================================
# КОМАНДА /start (ИСПРАВЛЕННАЯ)
# =========================================================
@DP.message(Command("start"))
async def start_command(message: Message):
    await register(message.from_user)
    
    # Проверяем реферальный код
    parts = message.text.split()
    if len(parts) > 1 and parts[0] == "/start" and parts[1].startswith("ref_"):
        try:
            referrer_id = int(parts[1].split("_")[1])
            if referrer_id != message.from_user.id:
                async with aiosqlite.connect(DB) as db:
                    # Проверяем, не использовал ли уже
                    cur = await db.execute(
                        "SELECT 1 FROM promo_uses WHERE code = ? AND user_id = ?",
                        (f"REF{referrer_id}", message.from_user.id)
                    )
                    if not await cur.fetchone():
                        # Активируем рефералку
                        await db.execute(
                            "INSERT INTO promo_uses (code, user_id) VALUES (?, ?)",
                            (f"REF{referrer_id}", message.from_user.id)
                        )
                        await db.execute(
                            "UPDATE users SET coins = coins + 25000 WHERE user_id = ?",
                            (referrer_id,)
                        )
                        await db.execute(
                            "UPDATE users SET coins = coins + 5000 WHERE user_id = ?",
                            (message.from_user.id,)
                        )
                        await db.commit()
                        
                        # Уведомляем реферера
                        try:
                            await BOT.send_message(
                                referrer_id,
                                f"🎉 <b>ТВОЙ ДРУГ ПРИСОЕДИНИЛСЯ!</b>\n\n"
                                f"👤 {html.escape(message.from_user.first_name)}\n"
                                f"💰 Ты получил: <b>+25,000 🪙</b>",
                                parse_mode="HTML"
                            )
                        except Exception:
                            pass
                        
                        await message.answer(
                            f"🎉 <b>ПРИВЕТСТВУЮ В ИГРЕ!</b>\n\n"
                            f"Ты пришёл по реферальной ссылке!\n"
                            f"💰 Бонус: <b>+5,000 🪙</b>\n\n"
                            f"Начинай игру с <code>/drop</code>!",
                            parse_mode="HTML"
                        )
        except Exception as e:
            print(f"Referral error: {e}")
    
    # Проверяем подписку
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
        "Используй меню или команды:\n"
        "/drop — открыть DROP\n"
        "/profile — профиль\n"
        "/collection — коллекция\n"
        "/battle @user — PvP\n"
        "/ai_battle — AI битва\n"
        "/team — ТОП-11 состав\n"
        "/help — все команды",
        reply_markup=main_keyboard(message.from_user),
        parse_mode="HTML"
    )

# =========================================================
# КОМАНДА /help
# =========================================================
@DP.message(Command("help"))
async def help_command(message: Message):
    if not await require_subscription(message):
        return
    
    text = (
        "🆘 <b>ВСЕ КОМАНДЫ</b>\n\n"
        "🃏 /drop — открыть DROP\n"
        "👤 /profile — профиль\n"
        "📚 /collection — коллекция\n"
        "💰 /balance — баланс\n"
        "🛒 /shop — магазин\n"
        "⭐ /packs — паки за Stars\n"
        "🪙 /coinpacks — паки за монеты\n"
        "🍀 /lucky — Lucky Charm\n"
        "🎁 /daily — ежедневная награда\n"
        "🎯 /missions — задания\n"
        "🏆 /top — рейтинг\n"
        "🎟️ /promo КОД — промокод\n"
        "📋 /players — все игроки\n"
        "⚔️ /battle @user — PvP битва\n"
        "🤖 /ai_battle — битва с AI\n"
        "🏆 /team — ТОП-11 состав\n"
        "📈 /upgrade_card ID — прокачка\n"
        "🏪 /sell_card ID ЦЕНА — продать карту\n"
        "🏪 /marketplace — рынок\n"
        "🎰 /roulette СТАВКА [цвет] — рулетка\n"
        "🔨 /craft_do РЕДКОСТЬ — крафт\n"
        "👥 /referral — рефералка\n"
        "🔄 /trade @user — обмен\n"
        "📋 /players — все игроки\n\n"
        f"📢 Канал: {CHANNEL_LINK}"
    )
    
    if is_owner(message.from_user):
        text += (
            "\n👑 <b>КОМАНДЫ ВЛАДЕЛЬЦА</b>\n"
            "/owner — панель владельца\n"
            "/stats — статистика\n"
            "/give ID КОЛИЧЕСТВО — выдать монеты\n"
            "/ban ID — забанить\n"
            "/unban ID — разбанить\n"
            "/createpromo КОД МОНЕТЫ STARS ЛИМИТ — создать промокод"
        )
    
    await message.answer(text, parse_mode="HTML", reply_markup=main_keyboard(message.from_user))

# =========================================================
# КОМАНДА /drop
# =========================================================
@DP.message(Command("drop"))
async def drop_command(message: Message):
    if not await require_subscription(message):
        return
    
    user = await get_user(message.from_user.id)
    if user["banned"] and not is_owner(message.from_user):
        await message.answer("🚫 Вы заблокированы.")
        return
    
    now = int(time.time())
    if not is_owner(message.from_user):
        remaining = DROP_COOLDOWN - (now - user["last_drop"])
        if remaining > 0:
            minutes = remaining // 60
            seconds = remaining % 60
            await message.answer(
                f"⏳ Следующий DROP через <b>{minutes}м {seconds}с</b>",
                parse_mode="HTML"
            )
            return
    
    async with aiosqlite.connect(DB) as db:
        await db.execute("UPDATE users SET last_drop=? WHERE user_id=?", (now, message.from_user.id))
        await db.commit()
    
    coins = random.randint(100, 400)
    await add_coins(message.from_user.id, coins)
    await mission_update(message.from_user.id, "drops")
    
    await message.answer("📦 <b>ПАК ОТКРЫВАЕТСЯ...</b>", parse_mode="HTML")
    await asyncio.sleep(0.7)
    
    player = random_player(user)
    await add_card(message.from_user.id, player)
    await mission_update(message.from_user.id, "cards")
    
    name, nation, pos, rating, rarity, price = player
    
    await message.answer(
        f"{RARITY_EMOJI.get(rarity, '⚪')} <b>{rarity.upper()}</b>\n\n"
        f"{nation} <b>{html.escape(name)}</b>\n"
        f"⚡ Позиция: <b>{pos}</b>\n"
        f"⭐ Рейтинг: <b>{rating}</b>\n"
        f"💰 Цена: <b>{price:,} 🪙</b>\n"
        f"🪙 Бонус: <b>+{coins}</b>\n"
        f"📚 Карта добавлена в коллекцию!",
        parse_mode="HTML"
    )

# =========================================================
# КОМАНДА /profile
# =========================================================
@DP.message(Command("profile"))
async def profile_command(message: Message):
    if not await require_subscription(message):
        return
    
    u = await get_user(message.from_user.id)
    lucky = "активен" if u["lucky_until"] > int(time.time()) else "нет"
    cards = await count_cards(message.from_user.id)
    
    await message.answer(
        f"👤 <b>ПРОФИЛЬ</b>\n\n"
        f"👤 {html.escape(message.from_user.first_name)}\n"
        f"🪙 Монеты: <b>{u['coins']:,}</b>\n"
        f"⭐ Stars: <b>{u['stars']}</b>\n"
        f"🃏 Карт: <b>{cards}</b>\n"
        f"🏆 Побед: <b>{u['wins']}</b>\n"
        f"💀 Поражений: <b>{u['losses']}</b>\n"
        f"⚔️ PvP Побед: <b>{u.get('battle_wins', 0)}</b>\n"
        f"⚔️ PvP Поражений: <b>{u.get('battle_losses', 0)}</b>\n"
        f"🍀 Lucky Charm: <b>{lucky}</b>",
        parse_mode="HTML"
    )

# =========================================================
# КОМАНДА /collection
# =========================================================
@DP.message(Command("collection"))
async def collection_command(message: Message):
    if not await require_subscription(message):
        return
    
    async with aiosqlite.connect(DB) as db:
        db.row_factory = aiosqlite.Row
        cur = await db.execute(
            "SELECT id,name,nation,position,rating,rarity,price,upgrade_level FROM cards WHERE user_id=? ORDER BY rating DESC LIMIT 50",
            (message.from_user.id,)
        )
        cards = await cur.fetchall()
    
    if not cards:
        await message.answer(
            "📚 <b>КОЛЛЕКЦИЯ ПУСТА</b>\n\n"
            "Открой свой первый DROP: /drop",
            parse_mode="HTML"
        )
        return
    
    text = "📚 <b>ТВОЯ КОЛЛЕКЦИЯ</b>\n\n"
    for card in cards:
        upgrade = f" +{card['upgrade_level']}" if card.get('upgrade_level', 0) > 0 else ""
        text += (
            f"{RARITY_EMOJI.get(card['rarity'], '⚪')} "
            f"<b>{html.escape(card['name'])}</b>\n"
            f"   {card['nation']} {card['position']} | ⭐{card['rating']}{upgrade}\n"
            f"   ID: <code>{card['id']}</code>\n\n"
        )
    
    await message.answer(text, parse_mode="HTML")

# =========================================================
# КОМАНДА /top
# =========================================================
@DP.message(Command("top"))
async def top_command(message: Message):
    if not await require_subscription(message):
        return
    
    async with aiosqlite.connect(DB) as db:
        cur = await db.execute(
            "SELECT username,first_name,coins FROM users WHERE banned=0 ORDER BY coins DESC LIMIT 10"
        )
        rows = await cur.fetchall()
    
    text = "🏆 <b>ТОП 10 ПО МОНЕТАМ</b>\n\n"
    for i, row in enumerate(rows, 1):
        name = row[0] or row[1] or "Игрок"
        text += f"{i}. <b>{html.escape(name)}</b> — {row[2]:,} 🪙\n"
    
    await message.answer(text, parse_mode="HTML")

# =========================================================
# КОМАНДА /shop
# =========================================================
@DP.message(Command("shop"))
async def shop_command(message: Message):
    if not await require_subscription(message):
        return
    
    kb = InlineKeyboardBuilder()
    kb.button(text="🍀 Lucky Charm", callback_data="lucky")
    kb.button(text="⭐ Паки за Stars", callback_data="packs")
    kb.button(text="📦 Паки за 🪙", callback_data="coinpacks")
    kb.adjust(1)
    
    await message.answer(
        "🏪 <b>МАГАЗИН</b>\n\n"
        "🍀 Lucky Charm — 15 ⭐ (24 часа)\n"
        "⭐ Паки за Telegram Stars\n"
        "📦 Паки за монеты",
        reply_markup=kb.as_markup(),
        parse_mode="HTML"
    )

# =========================================================
# КОМАНДА /lucky
# =========================================================
@DP.message(Command("lucky"))
async def lucky_command(message: Message):
    if not await require_subscription(message):
        return
    
    u = await get_user(message.from_user.id)
    now = int(time.time())
    
    if u["lucky_until"] > now:
        left = u["lucky_until"] - now
        await message.answer(
            f"🍀 Lucky Charm уже активен!\nОсталось: <b>{left//3600}ч {(left%3600)//60}м</b>",
            parse_mode="HTML"
        )
        return
    
    await BOT.send_invoice(
        chat_id=message.chat.id,
        title="🍀 Lucky Charm",
        description="24 часа повышенного шанса на редкие карты.",
        payload=f"lucky:{message.from_user.id}",
        currency="XTR",
        prices=[LabeledPrice(label="Lucky Charm", amount=LUCKY_COST)]
    )

# =========================================================
# КОМАНДА /packs
# =========================================================
@DP.message(Command("packs"))
async def packs_command(message: Message):
    if not await require_subscription(message):
        return
    
    kb = InlineKeyboardBuilder()
    for key, (stars, amount, name) in STAR_PACKS.items():
        kb.button(text=f"{name} — {stars} ⭐", callback_data=f"pack:{key}")
    kb.adjust(1)
    
    await message.answer("⭐ <b>ПАКИ ЗА STARS</b>", reply_markup=kb.as_markup(), parse_mode="HTML")

# =========================================================
# КОМАНДА /coinpacks
# =========================================================
@DP.message(Command("coinpacks"))
async def coinpacks_command(message: Message):
    if not await require_subscription(message):
        return
    
    kb = InlineKeyboardBuilder()
    for key, (price, amount, name) in COIN_PACKS.items():
        kb.button(text=f"{name} — {price:,} 🪙", callback_data=f"coinpack:{key}")
    kb.adjust(1)
    
    await message.answer("📦 <b>ПАКИ ЗА МОНЕТЫ</b>", reply_markup=kb.as_markup(), parse_mode="HTML")

# =========================================================
# КОМАНДА /daily
# =========================================================
@DP.message(Command("daily"))
async def daily_command(message: Message):
    if not await require_subscription(message):
        return
    
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    
    async with aiosqlite.connect(DB) as db:
        cur = await db.execute("SELECT daily_date, daily_streak FROM users WHERE user_id=?", (message.from_user.id,))
        user = await cur.fetchone()
        
        if user[0] == today:
            await message.answer("🎁 Daily уже получен сегодня.")
            return
        
        streak = user[1] + 1
        reward = 500 + min(streak, 7) * 100
        
        await db.execute(
            "UPDATE users SET daily_date=?, daily_streak=?, coins=coins+? WHERE user_id=?",
            (today, streak, reward, message.from_user.id)
        )
        await db.commit()
    
    await message.answer(
        f"🎁 <b>DAILY ПОЛУЧЕН!</b>\n\n"
        f"🔥 Серия: <b>{streak}</b>\n"
        f"🪙 Награда: <b>+{reward:,}</b>",
        parse_mode="HTML"
    )

# =========================================================
# КОМАНДА /missions
# =========================================================
@DP.message(Command("missions"))
async def missions_command(message: Message):
    if not await require_subscription(message):
        return
    
    async with aiosqlite.connect(DB) as db:
        db.row_factory = aiosqlite.Row
        cur = await db.execute("SELECT * FROM missions WHERE user_id=?", (message.from_user.id,))
        m = await cur.fetchone()
    
    await message.answer(
        f"🎯 <b>ЗАДАНИЯ</b>\n\n"
        f"⚽ DROP: <b>{m['drops']}/10</b>\n"
        f"🃏 Карты: <b>{m['cards']}/20</b>",
        parse_mode="HTML"
    )

# =========================================================
# КОМАНДА /players
# =========================================================
@DP.message(Command("players"))
async def players_command(message: Message):
    if not await require_subscription(message):
        return
    
    text = "📋 <b>ВСЕ ИГРОКИ</b>\n\n"
    text += f"👥 Всего: <b>{len(PLAYERS)}</b>\n\n"
    
    for rarity in RARITY_ORDER:
        players = [p for p in PLAYERS if p[4] == rarity]
        if players:
            text += f"{RARITY_EMOJI.get(rarity, '')} <b>{rarity}</b> ({len(players)}):\n"
            for p in players[:5]:
                text += f"  • {p[1]} {p[0]} — ⭐{p[3]}\n"
            if len(players) > 5:
                text += f"  ... и ещё {len(players) - 5}\n"
            text += "\n"
    
    await message.answer(text, parse_mode="HTML")

# =========================================================
# КОМАНДА /balance
# =========================================================
@DP.message(Command("balance"))
async def balance_command(message: Message):
    if not await require_subscription(message):
        return
    
    user = await get_user(message.from_user.id)
    await message.answer(
        f"💰 <b>ТВОЙ БАЛАНС</b>\n\n"
        f"🪙 Монеты: <b>{user['coins']:,}</b>\n"
        f"⭐ Stars: <b>{user['stars']}</b>",
        parse_mode="HTML"
    )

# =========================================================
# КОМАНДА /promo
# =========================================================
@DP.message(Command("promo"))
async def promo_command(message: Message):
    if not await require_subscription(message):
        return
    
    parts = message.text.split()
    if len(parts) < 2:
        await message.answer("🎟️ Использование: <code>/promo КОД</code>", parse_mode="HTML")
        return
    
    code = parts[1].upper().strip()
    
    async with aiosqlite.connect(DB) as db:
        db.row_factory = aiosqlite.Row
        cur = await db.execute("SELECT * FROM promo_codes WHERE code=?", (code,))
        promo = await cur.fetchone()
        
        if not promo:
            await message.answer("❌ Промокод не найден.")
            return
        
        cur = await db.execute("SELECT 1 FROM promo_uses WHERE code=? AND user_id=?", (code, message.from_user.id))
        if await cur.fetchone():
            await message.answer("❌ Ты уже использовал этот промокод.")
            return
        
        if promo["used"] >= promo["activations"]:
            await message.answer("❌ Лимит активаций закончился.")
            return
        
        await db.execute("INSERT INTO promo_uses(code,user_id) VALUES(?,?)", (code, message.from_user.id))
        await db.execute("UPDATE promo_codes SET used=used+1 WHERE code=?", (code,))
        await db.execute("UPDATE users SET coins=coins+?, stars=stars+? WHERE user_id=?", 
                        (promo["coins"], promo["stars"], message.from_user.id))
        await db.commit()
    
    await message.answer(
        f"🎉 <b>ПРОМОКОД АКТИВИРОВАН!</b>\n\n"
        f"🪙 +{promo['coins']:,}\n"
        f"⭐ +{promo['stars']}",
        parse_mode="HTML"
    )

# =========================================================
# КОМАНДА /team (ТОП-11)
# =========================================================
@DP.message(Command("team"))
async def team_command(message: Message):
    if not await require_subscription(message):
        return
    
    async with aiosqlite.connect(DB) as db:
        db.row_factory = aiosqlite.Row
        cur = await db.execute(
            "SELECT * FROM cards WHERE user_id=? ORDER BY rating DESC LIMIT 11",
            (message.from_user.id,)
        )
        cards = await cur.fetchall()
    
    if len(cards) < 11:
        await message.answer(
            f"🏆 <b>ТВОЙ СОСТАВ</b>\n\n"
            f"У тебя только <b>{len(cards)}</b> карт из 11.\n"
            "Нужно минимум 11 карт для составления команды!",
            parse_mode="HTML"
        )
        return
    
    total_rating = sum(c["rating"] + c.get("upgrade_level", 0) for c in cards)
    
    text = f"🏆 <b>ТВОЙ ТОП-11 СОСТАВ</b>\n\n"
    text += f"⭐ Общий рейтинг: <b>{total_rating}</b>\n\n"
    
    for i, card in enumerate(cards, 1):
        upgrade = f" +{card['upgrade_level']}" if card.get('upgrade_level', 0) > 0 else ""
        text += f"{i}. {RARITY_EMOJI.get(card['rarity'], '⚪')} {card['name']} — ⭐{card['rating']}{upgrade}\n"
    
    await message.answer(text, parse_mode="HTML")

# =========================================================
# КОМАНДА /ai_battle
# =========================================================
@DP.message(Command("ai_battle"))
async def ai_battle_command(message: Message):
    if not await require_subscription(message):
        return
    
    async with aiosqlite.connect(DB) as db:
        db.row_factory = aiosqlite.Row
        cur = await db.execute(
            "SELECT * FROM cards WHERE user_id=? ORDER BY rating DESC LIMIT 11",
            (message.from_user.id,)
        )
        cards = await cur.fetchall()
    
    if len(cards) < 11:
        await message.answer("❌ Нужно минимум 11 карт для битвы с AI!")
        return
    
    player_rating = sum(c["rating"] + c.get("upgrade_level", 0) for c in cards)
    ai_rating = random.randint(player_rating - 50, player_rating + 50)
    
    if player_rating > ai_rating:
        reward = random.randint(5000, 20000)
        await add_coins(message.from_user.id, reward)
        result = f"🏆 <b>ТЫ ПОБЕДИЛ!</b> 🎉\n💰 Награда: <b>+{reward:,} 🪙</b>"
    elif ai_rating > player_rating:
        result = "💀 <b>ТЫ ПРОИГРАЛ</b> 😢"
    else:
        reward = random.randint(1000, 5000)
        await add_coins(message.from_user.id, reward)
        result = f"🤝 <b>НИЧЬЯ!</b>\n💰 Утешительный приз: <b>+{reward:,} 🪙</b>"
    
    await message.answer(
        f"🤖 <b>БИТВА С AI</b>\n\n"
        f"👤 Твой рейтинг: <b>{player_rating}</b>\n"
        f"🤖 AI рейтинг: <b>{ai_rating}</b>\n\n"
        f"{result}",
        parse_mode="HTML"
    )

# =========================================================
# КОМАНДА /battle (PVP)
# =========================================================
@DP.message(Command("battle"))
async def battle_command(message: Message):
    if not await require_subscription(message):
        return
    
    parts = message.text.split()
    if len(parts) < 2:
        await message.answer(
            "⚔️ <b>PVP БИТВА</b>\n\n"
            "<code>/battle @username</code> — вызвать на битву\n"
            "<code>/battle @username СТАВКА</code> — со ставкой",
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
        except ValueError:
            pass
    
    async with aiosqlite.connect(DB) as db:
        cur = await db.execute("SELECT user_id, first_name FROM users WHERE username LIKE ?", (f"%{target}%",))
        row = await cur.fetchone()
        
        if not row:
            await message.answer("❌ Пользователь не найден.")
            return
        
        target_id = row[0]
        
        if target_id == message.from_user.id:
            await message.answer("❌ Нельзя биться с самим собой.")
            return
    
    text = (
        f"⚔️ <b>ВЫЗОВ НА БИТВУ!</b>\n\n"
        f"{message.from_user.first_name} вызывает тебя!\n"
    )
    if bet > 0:
        text += f"💰 Ставка: <b>{bet:,} 🪙</b>\n"
    
    kb = InlineKeyboardBuilder()
    kb.button(text="⚔️ Принять", callback_data=f"battle_accept:{message.from_user.id}:{bet}")
    kb.button(text="❌ Отклонить", callback_data=f"battle_decline:{message.from_user.id}")
    kb.adjust(1)
    
    try:
        await BOT.send_message(target_id, text, reply_markup=kb.as_markup(), parse_mode="HTML")
        await message.answer(f"✅ Вызов отправлен {target}!")
    except Exception:
        await message.answer("❌ Не удалось отправить вызов.")

@DP.callback_query(F.data.startswith("battle_accept:"))
async def battle_accept_callback(callback: CallbackQuery):
    await callback.answer()
    
    _, challenger_id, bet_str = callback.data.split(":")
    challenger_id = int(challenger_id)
    bet = int(bet_str)
    
    async with aiosqlite.connect(DB) as db:
        db.row_factory = aiosqlite.Row
        cur1 = await db.execute("SELECT * FROM cards WHERE user_id=? ORDER BY rating DESC LIMIT 11", (challenger_id,))
        challenger_cards = await cur1.fetchall()
        
        cur2 = await db.execute("SELECT * FROM cards WHERE user_id=? ORDER BY rating DESC LIMIT 11", (callback.from_user.id,))
        defender_cards = await cur2.fetchall()
    
    if len(challenger_cards) < 11 or len(defender_cards) < 11:
        await callback.message.answer("❌ У одного из игроков меньше 11 карт.")
        return
    
    challenger_rating = sum(c["rating"] + c.get("upgrade_level", 0) for c in challenger_cards)
    defender_rating = sum(c["rating"] + c.get("upgrade_level", 0) for c in defender_cards)
    
    if challenger_rating > defender_rating:
        winner_id = challenger_id
        winner_rating = challenger_rating
        loser_rating = defender_rating
    elif defender_rating > challenger_rating:
        winner_id = callback.from_user.id
        winner_rating = defender_rating
        loser_rating = challenger_rating
    else:
        winner_id = challenger_id
        winner_rating = challenger_rating
        loser_rating = defender_rating
    
    if bet > 0:
        async with aiosqlite.connect(DB) as db:
            await db.execute("UPDATE users SET coins = coins - ? WHERE user_id = ?", (bet, callback.from_user.id if winner_id == challenger_id else challenger_id))
            await db.execute("UPDATE users SET coins = coins + ? WHERE user_id = ?", (bet, winner_id))
            await db.commit()
    
    winner_name = callback.from_user.first_name if winner_id == callback.from_user.id else "Соперник"
    
    await callback.message.edit_text(
        f"⚔️ <b>РЕЗУЛЬТАТ БИТВЫ</b>\n\n"
        f"🏆 <b>ПОБЕДИТЕЛЬ: {winner_name}</b>\n"
        f"⭐ Рейтинг победителя: <b>{winner_rating}</b>\n"
        f"💀 Рейтинг проигравшего: <b>{loser_rating}</b>\n"
        f"{'💰 Ставка: ' + str(bet) + ' 🪙' if bet > 0 else ''}",
        parse_mode="HTML"
    )

@DP.callback_query(F.data.startswith("battle_decline:"))
async def battle_decline_callback(callback: CallbackQuery):
    await callback.answer()
    await callback.message.edit_text("❌ Вызов отклонён", parse_mode="HTML")

# =========================================================
# КОМАНДА /upgrade_card
# =========================================================
@DP.message(Command("upgrade_card"))
async def upgrade_card_command(message: Message):
    if not await require_subscription(message):
        return
    
    parts = message.text.split()
    if len(parts) < 2:
        await message.answer(
            "📈 <b>ПРОКАЧКА КАРТЫ</b>\n\n"
            "<code>/upgrade_card ID</code> — прокачать карту\n"
            "Цена: <b>100 000 🪙</b> за +1 рейтинг\n"
            "Максимум: <b>+5</b>",
            parse_mode="HTML"
        )
        return
    
    try:
        card_id = int(parts[1])
    except ValueError:
        await message.answer("❌ Неверный ID.")
        return
    
    async with aiosqlite.connect(DB) as db:
        db.row_factory = aiosqlite.Row
        cur = await db.execute("SELECT * FROM cards WHERE id=? AND user_id=?", (card_id, message.from_user.id))
        card = await cur.fetchone()
        
        if not card:
            await message.answer("❌ Карта не найдена.")
            return
        
        if card["upgrade_level"] >= MAX_UPGRADE:
            await message.answer(f"❌ Карта уже прокачана до максимума (+{MAX_UPGRADE}).")
            return
        
        if not await spend_coins(message.from_user.id, UPGRADE_COST):
            await message.answer(f"❌ Недостаточно монет. Нужно: <b>{UPGRADE_COST:,} 🪙</b>", parse_mode="HTML")
            return
        
        new_level = card["upgrade_level"] + 1
        new_rating = card["rating"] + 1
        
        await db.execute(
            "UPDATE cards SET upgrade_level=?, rating=? WHERE id=?",
            (new_level, new_rating, card_id)
        )
        await db.commit()
    
    await message.answer(
        f"✅ <b>КАРТА ПРОКАЧАНА!</b>\n\n"
        f"👤 {html.escape(card['name'])}\n"
        f"⭐ {card['rating']} → <b>{new_rating}</b>\n"
        f"📈 Уровень: <b>+{new_level}</b>",
        parse_mode="HTML"
    )

# =========================================================
# КОМАНДА /sell_card (Marketplace)
# =========================================================
@DP.message(Command("sell_card"))
async def sell_card_command(message: Message):
    if not await require_subscription(message):
        return
    
    parts = message.text.split()
    if len(parts) < 3:
        await message.answer(
            "🏪 <b>ПРОДАЖА КАРТЫ</b>\n\n"
            "<code>/sell_card ID ЦЕНА</code> — выставить на рынок\n"
            "Комиссия: <b>5%</b>",
            parse_mode="HTML"
        )
        return
    
    try:
        card_id = int(parts[1])
        price = int(parts[2])
    except ValueError:
        await message.answer("❌ Неверные данные.")
        return
    
    async with aiosqlite.connect(DB) as db:
        db.row_factory = aiosqlite.Row
        cur = await db.execute("SELECT * FROM cards WHERE id=? AND user_id=?", (card_id, message.from_user.id))
        card = await cur.fetchone()
        
        if not card:
            await message.answer("❌ Карта не найдена.")
            return
        
        await db.execute(
            "INSERT INTO marketplace (seller_id, card_id, price, created_at) VALUES (?, ?, ?, ?)",
            (message.from_user.id, card_id, price, int(time.time()))
        )
        await db.commit()
    
    await message.answer(
        f"✅ <b>КАРТА ВЫСТАВЛЕНА!</b>\n\n"
        f"👤 {html.escape(card['name'])}\n"
        f"💰 Цена: <b>{price:,} 🪙</b>",
        parse_mode="HTML"
    )

# =========================================================
# КОМАНДА /marketplace
# =========================================================
@DP.message(Command("marketplace"))
async def marketplace_command(message: Message):
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
            LIMIT 20
        """)
        listings = await cur.fetchall()
    
    if not listings:
        await message.answer("🏪 <b>РЫНОК ПУСТ</b>\n\nВыставь свою карту: /sell_card", parse_mode="HTML")
        return
    
    text = "🏪 <b>РЫНОК КАРТ</b>\n\n"
    kb = InlineKeyboardBuilder()
    
    for listing in listings:
        upgrade = f" +{listing['upgrade_level']}" if listing['upgrade_level'] > 0 else ""
        text += (
            f"{RARITY_EMOJI.get(listing['rarity'], '⚪')} "
            f"<b>{html.escape(listing['name'])}</b>\n"
            f"   ⭐ {listing['rating']}{upgrade} | 💰 <b>{listing['price']:,} 🪙</b>\n\n"
        )
        kb.button(
            text=f"Купить {listing['name']} ({listing['price']:,}🪙)",
            callback_data=f"buy_market:{listing['id']}"
        )
    
    kb.adjust(1)
    await message.answer(text, reply_markup=kb.as_markup(), parse_mode="HTML")

@DP.callback_query(F.data.startswith("buy_market:"))
async def buy_market_callback(callback: CallbackQuery):
    await callback.answer()
    
    listing_id = int(callback.data.split(":")[1])
    
    async with aiosqlite.connect(DB) as db:
        db.row_factory = aiosqlite.Row
        cur = await db.execute("""
            SELECT m.*, c.name, c.rating, c.user_id as owner_id
            FROM marketplace m
            JOIN cards c ON m.card_id = c.id
            WHERE m.id = ? AND m.sold = 0
        """, (listing_id,))
        listing = await cur.fetchone()
        
        if not listing:
            await callback.message.answer("❌ Карта уже продана.")
            return
        
        if listing["seller_id"] == callback.from_user.id:
            await callback.message.answer("❌ Нельзя купить свою карту.")
            return
        
        price = listing["price"]
        commission = int(price * 0.05)
        seller_gets = price - commission
        
        buyer = await get_user(callback.from_user.id)
        if buyer["coins"] < price:
            await callback.message.answer(f"❌ Недостаточно монет. Нужно: <b>{price:,} 🪙</b>", parse_mode="HTML")
            return
        
        await db.execute("UPDATE users SET coins = coins - ? WHERE user_id = ?", (price, callback.from_user.id))
        await db.execute("UPDATE users SET coins = coins + ? WHERE user_id = ?", (seller_gets, listing["seller_id"]))
        await db.execute("UPDATE cards SET user_id = ? WHERE id = ?", (callback.from_user.id, listing["card_id"]))
        await db.execute("UPDATE marketplace SET sold = 1 WHERE id = ?", (listing_id,))
        await db.commit()
    
    await callback.message.edit_text(
        f"✅ <b>ПОКУПКА УСПЕШНА!</b>\n\n"
        f"👤 Карта: {html.escape(listing['name'])}\n"
        f"⭐ Рейтинг: {listing['rating']}\n"
        f"💰 Цена: <b>{price:,} 🪙</b>\n"
        f"📊 Комиссия: <b>{commission:,} 🪙</b>",
        parse_mode="HTML"
    )

# =========================================================
# КОМАНДА /referral
# =========================================================
@DP.message(Command("referral"))
async def referral_command(message: Message):
    if not await require_subscription(message):
        return
    
    async with aiosqlite.connect(DB) as db:
        cur = await db.execute("SELECT * FROM promo_codes WHERE code = ?", (f"REF{message.from_user.id}",))
        promo = await cur.fetchone()
        
        if not promo:
            await db.execute(
                "INSERT INTO promo_codes (code, coins, stars, activations, used, created) VALUES (?, ?, ?, ?, ?, ?)",
                (f"REF{message.from_user.id}", 25000, 0, 100, 0, int(time.time()))
            )
            await db.commit()
    
    bot_info = await BOT.get_me()
    
    text = (
        "👥 <b>РЕФЕРАЛЬНАЯ СИСТЕМА</b>\n\n"
        "Приведи друга и получи <b>25,000 🪙</b>!\n\n"
        "📌 Твоя реферальная ссылка:\n"
        f"<code>https://t.me/{bot_info.username}?start=ref_{message.from_user.id}</code>\n\n"
        "🎟️ Или используй промокод:\n"
        f"<code>REF{message.from_user.id}</code>\n\n"
        "📊 Как это работает:\n"
        "1️⃣ Твой друг переходит по ссылке или вводит промокод\n"
        "2️⃣ Ты автоматически получаешь 25,000 🪙\n"
        "3️⃣ Друг тоже получает 5,000 🪙 бонусом!\n\n"
        f"👤 Твой реферальный код: <code>REF{message.from_user.id}</code>"
    )
    
    await message.answer(text, parse_mode="HTML")

# =========================================================
# КОМАНДА /roulette
# =========================================================
@DP.message(Command("roulette"))
async def roulette_command(message: Message):
    if not await require_subscription(message):
        return
    
    parts = message.text.split()
    if len(parts) < 2:
        await message.answer(
            "🎰 <b>РУЛЕТКА</b>\n\n"
            "<code>/roulette СТАВКА [цвет]</code>\n"
            "Цвета: красное, черное, зеленое\n"
            "Пример: <code>/roulette 5000 красное</code>",
            parse_mode="HTML"
        )
        return
    
    try:
        bet = int(parts[1])
        if bet < 1000:
            await message.answer("❌ Минимальная ставка: 1 000 🪙")
            return
    except ValueError:
        await message.answer("❌ Ставка должна быть числом.")
        return
    
    user = await get_user(message.from_user.id)
    if user["coins"] < bet:
        await message.answer(f"❌ Недостаточно монет. Нужно: <b>{bet:,} 🪙</b>", parse_mode="HTML")
        return
    
    color = None
    if len(parts) >= 3:
        color = parts[2].lower()
        if color not in ["красное", "черное", "зеленое"]:
            await message.answer("❌ Доступные цвета: красное, черное, зеленое")
            return
    
    colors = ["красное"] * 18 + ["черное"] * 18 + ["зеленое"] * 1
    result = random.choice(colors)
    
    if color:
        if color == result:
            winnings = bet * 14 if color == "зеленое" else bet * 2
            await add_coins(message.from_user.id, winnings - bet)
            result_text = f"🎉 <b>ВЫИГРЫШ!</b>\n💰 Выигрыш: <b>{winnings:,} 🪙</b>"
        else:
            await spend_coins(message.from_user.id, bet)
            result_text = f"💀 <b>ПРОИГРЫШ!</b>\n💸 Потеряно: <b>{bet:,} 🪙</b>"
    else:
        if result in ["красное", "черное"]:
            winnings = bet * 2
            await add_coins(message.from_user.id, winnings - bet)
            result_text = f"🎉 <b>ВЫИГРЫШ!</b>\n💰 Выигрыш: <b>{winnings:,} 🪙</b>"
        else:
            await spend_coins(message.from_user.id, bet)
            result_text = f"💀 <b>ПРОИГРЫШ!</b>\n💸 Потеряно: <b>{bet:,} 🪙</b>"
    
    emoji = "🔴" if result == "красное" else "⚫" if result == "черное" else "🟢"
    
    await message.answer(
        f"🎰 <b>РУЛЕТКА</b>\n\n"
        f"🎯 Выпало: {emoji} <b>{result.upper()}</b>\n"
        f"📊 Ставка: <b>{bet:,} 🪙</b>\n"
        f"{result_text}",
        parse_mode="HTML"
    )

# =========================================================
# КОМАНДА /craft
# =========================================================
@DP.message(Command("craft"))
async def craft_command(message: Message):
    if not await require_subscription(message):
        return
    
    await message.answer(
        "🔨 <b>КРАФТ КАРТ</b>\n\n"
        "Обменяй 5 карт одной редкости на 1 карту выше!\n\n"
        "Доступно:\n"
        "🔄 5 Common → 1 Rare\n"
        "🔄 5 Rare → 1 Super Rare\n"
        "🔄 5 Super Rare → 1 Epic\n"
        "🔄 5 Epic → 1 Legendary\n"
        "🔄 5 Legendary → 1 Icon\n"
        "🔄 5 Icon → 1 Ultimate\n\n"
        "Использование:\n"
        "<code>/craft_do РЕДКОСТЬ</code>\n"
        "Пример: <code>/craft_do Rare</code>\n\n"
        "⚠️ Шанс неудачи: 20% (сгорают 3 карты)",
        parse_mode="HTML"
    )

@DP.message(Command("craft_do"))
async def craft_do_command(message: Message):
    if not await require_subscription(message):
        return
    
    parts = message.text.split()
    if len(parts) < 2:
        await message.answer("❌ Укажи редкость: <code>/craft_do Rare</code>", parse_mode="HTML")
        return
    
    rarity_from = parts[1].title()
    rarity_map = {
        "Common": "Rare",
        "Rare": "Super Rare",
        "Super Rare": "Epic",
        "Epic": "Legendary",
        "Legendary": "Icon",
        "Icon": "Ultimate"
    }
    
    if rarity_from not in rarity_map:
        await message.answer("❌ Недопустимая редкость. Доступно: Common, Rare, Super Rare, Epic, Legendary, Icon")
        return
    
    rarity_to = rarity_map[rarity_from]
    
    async with aiosqlite.connect(DB) as db:
        cur = await db.execute("SELECT id FROM cards WHERE user_id=? AND rarity=?", (message.from_user.id, rarity_from))
        cards = await cur.fetchall()
    
    if len(cards) < 5:
        await message.answer(f"❌ Нужно 5 карт редкости <b>{rarity_from}</b>. У тебя: {len(cards)}", parse_mode="HTML")
        return
    
    if random.random() < 0.2:
        async with aiosqlite.connect(DB) as db:
            for card in cards[:3]:
                await db.execute("DELETE FROM cards WHERE id=?", (card[0],))
            await db.commit()
        
        await message.answer(
            f"💥 <b>КРАФТ НЕ УДАЛСЯ!</b>\n\n"
            f"Сгорело 3 карты {rarity_from} 😢",
            parse_mode="HTML"
        )
        return
    
    players_of_rarity = [p for p in PLAYERS if p[4] == rarity_to]
    if not players_of_rarity:
        await message.answer("❌ Нет доступных карт для крафта.")
        return
    
    new_player = random.choice(players_of_rarity)
    
    async with aiosqlite.connect(DB) as db:
        for card in cards[:5]:
            await db.execute("DELETE FROM cards WHERE id=?", (card[0],))
        await add_card(message.from_user.id, new_player)
        await db.commit()
    
    await message.answer(
        f"✅ <b>КРАФТ УСПЕШЕН!</b>\n\n"
        f"🔄 5 {rarity_from} → 1 {rarity_to}\n\n"
        f"🎴 Ты получил:\n"
        f"{RARITY_EMOJI.get(rarity_to, '⚪')} <b>{html.escape(new_player[0])}</b>\n"
        f"⭐ {new_player[3]} OVR | {new_player[2]} | {new_player[1]}",
        parse_mode="HTML"
    )

# =========================================================
# КОМАНДА /trade (ОБМЕН)
# =========================================================
@DP.message(Command("trade"))
async def trade_command(message: Message):
    if not await require_subscription(message):
        return
    
    parts = message.text.split()
    if len(parts) < 2:
        await message.answer(
            "🔄 <b>ОБМЕН КАРТАМИ</b>\n\n"
            "<code>/trade @username</code> — предложить обмен\n"
            "<code>/trade_list</code> — список обменов",
            parse_mode="HTML"
        )
        return
    
    target = parts[1]
    if target.startswith("@"):
        target = target[1:]
    
    async with aiosqlite.connect(DB) as db:
        cur = await db.execute("SELECT user_id, first_name FROM users WHERE username LIKE ?", (f"%{target}%",))
        row = await cur.fetchone()
        
        if not row:
            await message.answer("❌ Пользователь не найден.")
            return
        
        target_id = row[0]
        
        if target_id == message.from_user.id:
            await message.answer("❌ Нельзя обменяться с самим собой.")
            return
    
    await message.answer(f"🔄 Отправь запрос на обмен пользователю @{target} через /trade_list")

@DP.message(Command("trade_list"))
async def trade_list_command(message: Message):
    if not await require_subscription(message):
        return
    
    await message.answer(
        "🔄 <b>СПИСОК ОБМЕНОВ</b>\n\n"
        "Пока что система обменов в разработке.\n"
        "Скоро появится возможность обмениваться картами!",
        parse_mode="HTML"
    )

# =========================================================
# КОМАНДА /owner (ПАНЕЛЬ ВЛАДЕЛЬЦА)
# =========================================================
@DP.message(Command("owner"))
async def owner_command(message: Message):
    if not is_owner(message.from_user):
        await message.answer("❌ Только владелец бота.")
        return
    
    kb = InlineKeyboardBuilder()
    kb.button(text="📊 Статистика", callback_data="owner_stats")
    kb.button(text="🎟️ Создать промокод", callback_data="owner_promo")
    kb.button(text="🚫 Забанить", callback_data="owner_ban")
    kb.button(text="✅ Разбанить", callback_data="owner_unban")
    kb.button(text="💰 Выдать монеты", callback_data="owner_give")
    kb.adjust(1)
    
    await message.answer(
        "👑 <b>ПАНЕЛЬ ВЛАДЕЛЬЦА</b>\n\n"
        "Выбери действие:",
        reply_markup=kb.as_markup(),
        parse_mode="HTML"
    )

# =========================================================
# КОМАНДА /stats
# =========================================================
@DP.message(Command("stats"))
async def stats_command(message: Message):
    if not is_owner(message.from_user):
        return
    
    async with aiosqlite.connect(DB) as db:
        cur = await db.execute("SELECT COUNT(*) FROM users")
        users = (await cur.fetchone())[0]
        
        cur = await db.execute("SELECT COUNT(*) FROM cards")
        cards = (await cur.fetchone())[0]
        
        cur = await db.execute("SELECT SUM(coins) FROM users")
        coins = (await cur.fetchone())[0] or 0
    
    await message.answer(
        f"📊 <b>СТАТИСТИКА</b>\n\n"
        f"👥 Пользователей: <b>{users}</b>\n"
        f"🃏 Карт: <b>{cards}</b>\n"
        f"🪙 Монет в системе: <b>{coins:,}</b>\n"
        f"👥 Игроков в базе: <b>{len(PLAYERS)}</b>",
        parse_mode="HTML"
    )

# =========================================================
# КОМАНДА /give
# =========================================================
@DP.message(Command("give"))
async def give_command(message: Message):
    if not is_owner(message.from_user):
        return
    
    parts = message.text.split()
    if len(parts) != 3:
        await message.answer("Использование: <code>/give USER_ID КОЛИЧЕСТВО</code>", parse_mode="HTML")
        return
    
    try:
        user_id = int(parts[1])
        amount = int(parts[2])
    except ValueError:
        await message.answer("❌ Неверные данные.")
        return
    
    await add_coins(user_id, amount)
    await message.answer(f"✅ Выдано <b>{amount:,} 🪙</b> пользователю <code>{user_id}</code>", parse_mode="HTML")

# =========================================================
# КОМАНДА /ban
# =========================================================
@DP.message(Command("ban"))
async def ban_command(message: Message):
    if not is_owner(message.from_user):
        return
    
    parts = message.text.split()
    if len(parts) != 2:
        await message.answer("Использование: <code>/ban USER_ID</code>", parse_mode="HTML")
        return
    
    try:
        user_id = int(parts[1])
    except ValueError:
        await message.answer("❌ Неверный ID.")
        return
    
    async with aiosqlite.connect(DB) as db:
        await db.execute("UPDATE users SET banned=1 WHERE user_id=?", (user_id,))
        await db.commit()
    
    await message.answer(f"🚫 Пользователь <code>{user_id}</code> заблокирован.", parse_mode="HTML")

# =========================================================
# КОМАНДА /unban
# =========================================================
@DP.message(Command("unban"))
async def unban_command(message: Message):
    if not is_owner(message.from_user):
        return
    
    parts = message.text.split()
    if len(parts) != 2:
        await message.answer("Использование: <code>/unban USER_ID</code>", parse_mode="HTML")
        return
    
    try:
        user_id = int(parts[1])
    except ValueError:
        await message.answer("❌ Неверный ID.")
        return
    
    async with aiosqlite.connect(DB) as db:
        await db.execute("UPDATE users SET banned=0 WHERE user_id=?", (user_id,))
        await db.commit()
    
    await message.answer(f"✅ Пользователь <code>{user_id}</code> разблокирован.", parse_mode="HTML")

# =========================================================
# КОМАНДА /createpromo
# =========================================================
@DP.message(Command("createpromo"))
async def createpromo_command(message: Message):
    if not is_owner(message.from_user):
        return
    
    parts = message.text.split()
    if len(parts) != 5:
        await message.answer(
            "🎟️ <b>СОЗДАНИЕ ПРОМОКОДА</b>\n\n"
            "<code>/createpromo КОД МОНЕТЫ STARS ЛИМИТ</code>\n"
            "Пример: <code>/createpromo TEST 5000 10 100</code>",
            parse_mode="HTML"
        )
        return
    
    code = parts[1].upper()
    try:
        coins = int(parts[2])
        stars = int(parts[3])
        limit = int(parts[4])
    except ValueError:
        await message.answer("❌ Неверные данные.")
        return
    
    async with aiosqlite.connect(DB) as db:
        try:
            await db.execute(
                "INSERT INTO promo_codes (code, coins, stars, activations, used, created) VALUES (?, ?, ?, ?, 0, ?)",
                (code, coins, stars, limit, int(time.time()))
            )
            await db.commit()
        except aiosqlite.IntegrityError:
            await message.answer("❌ Такой промокод уже существует.")
            return
    
    await message.answer(
        f"✅ <b>ПРОМОКОД СОЗДАН!</b>\n\n"
        f"🎟️ Код: <code>{code}</code>\n"
        f"🪙 +{coins:,} монет\n"
        f"⭐ +{stars} Stars\n"
        f"👥 Лимит: {limit}",
        parse_mode="HTML"
    )

# =========================================================
# Покупка паков
# =========================================================
@DP.callback_query(F.data.startswith("pack:"))
async def pack_callback(callback: CallbackQuery):
    await callback.answer()
    
    key = callback.data.split(":")[1]
    if key not in STAR_PACKS:
        return
    
    stars, amount, name = STAR_PACKS[key]
    
    user = await get_user(callback.from_user.id)
    if user["stars"] < stars:
        await callback.message.answer(f"❌ Недостаточно Stars. Нужно: <b>{stars} ⭐</b>", parse_mode="HTML")
        return
    
    async with aiosqlite.connect(DB) as db:
        await db.execute("UPDATE users SET stars = stars - ? WHERE user_id = ?", (stars, callback.from_user.id))
        await db.commit()
    
    pulled = []
    for _ in range(amount):
        player = random_player(user)
        await add_card(callback.from_user.id, player)
        pulled.append(player)
    
    best = max(pulled, key=lambda p: p[3])
    
    await callback.message.answer(
        f"📦 <b>ПАК ОТКРЫТ!</b>\n\n"
        f"{name}\n"
        f"🃏 Карт: <b>{amount}</b>\n\n"
        f"🔥 Лучшая:\n"
        f"{RARITY_EMOJI.get(best[4], '⚪')} <b>{html.escape(best[0])}</b>\n"
        f"⭐ {best[3]} OVR",
        parse_mode="HTML"
    )

@DP.callback_query(F.data.startswith("coinpack:"))
async def coinpack_callback(callback: CallbackQuery):
    await callback.answer()
    
    key = callback.data.split(":")[1]
    if key not in COIN_PACKS:
        return
    
    price, amount, name = COIN_PACKS[key]
    
    if not await spend_coins(callback.from_user.id, price):
        await callback.message.answer("❌ Недостаточно монет.")
        return
    
    user = await get_user(callback.from_user.id)
    pulled = []
    
    for _ in range(amount):
        player = random_player(user)
        await add_card(callback.from_user.id, player)
        pulled.append(player)
    
    best = max(pulled, key=lambda p: p[3])
    
    await callback.message.answer(
        f"📦 <b>ПАК ОТКРЫТ!</b>\n\n"
        f"{name}\n"
        f"🃏 Карт: <b>{amount}</b>\n\n"
        f"🔥 Лучшая:\n"
        f"{RARITY_EMOJI.get(best[4], '⚪')} <b>{html.escape(best[0])}</b>\n"
        f"⭐ {best[3]} OVR",
        parse_mode="HTML"
    )

# =========================================================
# ОБРАБОТКА ПЛАТЕЖЕЙ
# =========================================================
@DP.pre_checkout_query()
async def pre_checkout_query(query: PreCheckoutQuery):
    await query.answer(ok=True)

@DP.message(F.successful_payment)
async def successful_payment(message: Message):
    payment = message.successful_payment
    payload = payment.invoice_payload
    
    if payload.startswith("lucky:"):
        expires = int(time.time()) + LUCKY_HOURS * 60 * 60
        async with aiosqlite.connect(DB) as db:
            await db.execute(
                "INSERT INTO lucky_charms(user_id, expires_at) VALUES(?, ?) ON CONFLICT(user_id) DO UPDATE SET expires_at = excluded.expires_at",
                (message.from_user.id, expires)
            )
            await db.commit()
        
        await message.answer(
            "🍀 <b>LUCKY CHARM АКТИВИРОВАН!</b>\n\n"
            "🔥 Повышенный шанс редких карт.\n"
            "⏳ Длительность: <b>24 часа</b>.",
            parse_mode="HTML"
        )

# =========================================================
# ВСЕ CALLBACK'И
# =========================================================
@DP.callback_query(F.data == "check_sub")
async def check_sub_callback(callback: CallbackQuery):
    await callback.answer()
    
    if await check_access(callback.from_user.id):
        await callback.message.edit_text(
            "✅ <b>ПОДПИСКА ПОДТВЕРЖДЕНА!</b>\n\n"
            "Теперь ты можешь пользоваться всеми функциями.",
            reply_markup=main_keyboard(callback.from_user),
            parse_mode="HTML"
        )
    else:
        await callback.message.answer(
            "❌ Подписка не найдена.\n\n"
            "Подпишись на канал и нажми «Проверить подписку».",
            reply_markup=subscribe_keyboard(),
            parse_mode="HTML"
        )

@DP.callback_query(F.data == "drop")
async def drop_callback(callback: CallbackQuery):
    await callback.answer()
    await drop_command(callback.message)

@DP.callback_query(F.data == "collection")
async def collection_callback(callback: CallbackQuery):
    await callback.answer()
    await collection_command(callback.message)

@DP.callback_query(F.data == "profile")
async def profile_callback(callback: CallbackQuery):
    await callback.answer()
    await profile_command(callback.message)

@DP.callback_query(F.data == "shop")
async def shop_callback(callback: CallbackQuery):
    await callback.answer()
    await shop_command(callback.message)

@DP.callback_query(F.data == "market")
async def market_callback(callback: CallbackQuery):
    await callback.answer()
    await callback.message.answer("🏪 Используй /sell_card или /marketplace")

@DP.callback_query(F.data == "marketplace")
async def marketplace_callback(callback: CallbackQuery):
    await callback.answer()
    await marketplace_command(callback.message)

@DP.callback_query(F.data == "daily")
async def daily_callback(callback: CallbackQuery):
    await callback.answer()
    await daily_command(callback.message)

@DP.callback_query(F.data == "missions")
async def missions_callback(callback: CallbackQuery):
    await callback.answer()
    await missions_command(callback.message)

@DP.callback_query(F.data == "top")
async def top_callback(callback: CallbackQuery):
    await callback.answer()
    await top_command(callback.message)

@DP.callback_query(F.data == "coinpacks")
async def coinpacks_callback(callback: CallbackQuery):
    await callback.answer()
    await coinpacks_command(callback.message)

@DP.callback_query(F.data == "packs")
async def packs_callback(callback: CallbackQuery):
    await callback.answer()
    await packs_command(callback.message)

@DP.callback_query(F.data == "lucky")
async def lucky_callback(callback: CallbackQuery):
    await callback.answer()
    await lucky_command(callback.message)

@DP.callback_query(F.data == "promo")
async def promo_callback(callback: CallbackQuery):
    await callback.answer()
    await callback.message.answer("🎟️ Используй: <code>/promo КОД</code>", parse_mode="HTML")

@DP.callback_query(F.data == "players")
async def players_callback(callback: CallbackQuery):
    await callback.answer()
    await players_command(callback.message)

@DP.callback_query(F.data == "pvp_menu")
async def pvp_menu_callback(callback: CallbackQuery):
    await callback.answer()
    await callback.message.answer(
        "⚔️ <b>PVP БИТВЫ</b>\n\n"
        "<code>/battle @username</code> — вызвать на битву\n"
        "<code>/battle @username СТАВКА</code> — со ставкой",
        parse_mode="HTML"
    )

@DP.callback_query(F.data == "team_menu")
async def team_menu_callback(callback: CallbackQuery):
    await callback.answer()
    await team_command(callback.message)

@DP.callback_query(F.data == "ai_battle")
async def ai_battle_callback(callback: CallbackQuery):
    await callback.answer()
    await ai_battle_command(callback.message)

@DP.callback_query(F.data == "upgrade_menu")
async def upgrade_menu_callback(callback: CallbackQuery):
    await callback.answer()
    await upgrade_card_command(callback.message)

@DP.callback_query(F.data == "roulette")
async def roulette_callback(callback: CallbackQuery):
    await callback.answer()
    await roulette_command(callback.message)

@DP.callback_query(F.data == "craft")
async def craft_callback(callback: CallbackQuery):
    await callback.answer()
    await craft_command(callback.message)

@DP.callback_query(F.data == "referral")
async def referral_callback(callback: CallbackQuery):
    await callback.answer()
    await referral_command(callback.message)

@DP.callback_query(F.data == "trade_menu")
async def trade_menu_callback(callback: CallbackQuery):
    await callback.answer()
    await trade_command(callback.message)

@DP.callback_query(F.data == "owner_panel")
async def owner_panel_callback(callback: CallbackQuery):
    await callback.answer()
    await owner_command(callback.message)

@DP.callback_query(F.data == "owner_stats")
async def owner_stats_callback(callback: CallbackQuery):
    await callback.answer()
    await stats_command(callback.message)

@DP.callback_query(F.data == "owner_promo")
async def owner_promo_callback(callback: CallbackQuery):
    await callback.answer()
    await callback.message.answer(
        "🎟️ <b>СОЗДАНИЕ ПРОМОКОДА</b>\n\n"
        "<code>/createpromo КОД МОНЕТЫ STARS ЛИМИТ</code>\n"
        "Пример: <code>/createpromo TEST 5000 10 100</code>",
        parse_mode="HTML"
    )

@DP.callback_query(F.data == "owner_ban")
async def owner_ban_callback(callback: CallbackQuery):
    await callback.answer()
    await callback.message.answer(
        "🚫 <b>БАН ПОЛЬЗОВАТЕЛЯ</b>\n\n"
        "<code>/ban USER_ID</code>",
        parse_mode="HTML"
    )

@DP.callback_query(F.data == "owner_unban")
async def owner_unban_callback(callback: CallbackQuery):
    await callback.answer()
    await callback.message.answer(
        "✅ <b>РАЗБАН ПОЛЬЗОВАТЕЛЯ</b>\n\n"
        "<code>/unban USER_ID</code>",
        parse_mode="HTML"
    )

@DP.callback_query(F.data == "owner_give")
async def owner_give_callback(callback: CallbackQuery):
    await callback.answer()
    await callback.message.answer(
        "💰 <b>ВЫДАЧА МОНЕТ</b>\n\n"
        "<code>/give USER_ID КОЛИЧЕСТВО</code>",
        parse_mode="HTML"
    )

# =========================================================
# MAIN
# =========================================================
async def main():
    await init_db()
    print("=" * 50)
    print("⚽ FOOTBALL DROP BOT")
    print(f"👑 OWNER: @{OWNER}")
    print(f"📢 КАНАЛ: {CHANNEL_LINK}")
    print("🔒 ПРИНУДИТЕЛЬНАЯ ПОДПИСКА: ВКЛЮЧЕНА")
    print(f"👥 ИГРОКОВ В БАЗЕ: {len(PLAYERS)}")
    print("=" * 50)
    await DP.start_polling(BOT, allowed_updates=DP.resolve_used_update_types())

if __name__ == "__main__":
    asyncio.run(main())
