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

from keep_alive import keep_alive

keep_alive()

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
if not TOKEN:
    raise RuntimeError("TELEGRAM_BOT_TOKEN is not set")

BOT = Bot(TOKEN)
DP = Dispatcher()

DB = "football_drop.db"

OWNER = "foqlu"
OWNER_ID = int(os.getenv("OWNER_ID", "0"))

REQUIRED_CHANNEL = os.getenv("REQUIRED_CHANNEL", "")
CHANNEL_LINK = "https://t.me/+MHTPcaFy2j5lOWMy"

DROP_COOLDOWN = 60
LUCKY_COST = 15
LUCKY_HOURS = 24
LUCKY_MULTIPLIER = 3

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
# 200+ ИГРОКОВ
# =========================================================

PLAYERS = [
    ("Фран Гарсия","🇪🇸","LB",78,"Common",5000),
    ("Браим Диас","🇪🇸","RW",79,"Common",6000),
    ("Арда Гюлер","🇹🇷","CAM",79,"Common",6500),
    ("Эндрик","🇧🇷","ST",78,"Common",5000),
    ("Жоау Феликс","🇵🇹","SS",78,"Common",5500),
    ("Джек Грилиш","🏴","LW",79,"Common",6500),
    ("Ришарлисон","🇧🇷","ST",79,"Common",6000),
    ("Габриэл Жезус","🇧🇷","ST",79,"Common",6000),
    ("Федерико Кьеза","🇮🇹","RW",79,"Common",6500),
    ("Антони","🇧🇷","RW",77,"Common",4500),

    ("Кобби Майну","🏴","CM",81,"Rare",10000),
    ("Кристиан Пулишич","🇺🇸","LW",82,"Rare",12000),
    ("Нико Уильямс","🇪🇸","LW",83,"Rare",15000),
    ("Душан Влахович","🇷🇸","ST",83,"Rare",15000),
    ("Рафаэл Леау","🇵🇹","LW",84,"Rare",18000),
    ("Федерико Вальверде","🇺🇾","CM",84,"Rare",19000),
    ("Энцо Фернандес","🇦🇷","CM",83,"Rare",16000),
    ("Дани Ольмо","🇪🇸","CAM",84,"Rare",18000),
    ("Жюль Кунде","🇫🇷","CB",84,"Rare",18000),
    ("Рональд Араухо","🇺🇾","CB",84,"Rare",19000),
    ("Камавинга","🇫🇷","CM",84,"Rare",19000),
    ("Тчуамени","🇫🇷","CDM",83,"Rare",16000),

    ("Педри","🇪🇸","CM",86,"Super Rare",25000),
    ("Гави","🇪🇸","CM",85,"Super Rare",23000),
    ("Майкл Олисе","🇫🇷","RW",86,"Super Rare",27000),
    ("Коул Палмер","🏴","CAM",87,"Super Rare",30000),
    ("Флориан Вирц","🇩🇪","CAM",87,"Super Rare",30000),
    ("Лаутаро Мартинес","🇦🇷","ST",87,"Super Rare",30000),
    ("Сон Хын Мин","🇰🇷","LW",87,"Super Rare",32000),
    ("Кварацхелия","🇬🇪","LW",86,"Super Rare",27000),
    ("Трент Александер-Арнольд","🏴","RB",86,"Super Rare",26000),
    ("Тео Эрнандес","🇫🇷","LB",87,"Super Rare",30000),

    ("Ламин Ямаль","🇪🇸","RW",89,"Epic",45000),
    ("Рафинья","🇧🇷","LW",90,"Epic",50000),
    ("Винисиус Жуниор","🇧🇷","LW",91,"Epic",60000),
    ("Родри","🇪🇸","CDM",90,"Epic",50000),
    ("Бернарду Силва","🇵🇹","CAM",88,"Epic",43000),
    ("Фил Фоден","🏴","RW",88,"Epic",43000),
    ("Кевин Де Брёйне","🇧🇪","CAM",89,"Epic",48000),
    ("Салиба","🇫🇷","CB",88,"Epic",40000),
    ("Рюдигер","🇩🇪","CB",88,"Epic",40000),
    ("Хакими","🇲🇦","RB",88,"Epic",43000),
    ("Гарри Кейн","🏴","ST",90,"Epic",52000),
    ("Левандовски","🇵🇱","ST",89,"Epic",48000),

    ("Килиан Мбаппе","🇫🇷","ST",92,"Legendary",85000),
    ("Эрлинг Холанд","🇳🇴","ST",91,"Legendary",80000),
    ("Мохамед Салах","🇪🇬","RW",90,"Legendary",70000),
    ("Джуд Беллингем","🏴","CAM",90,"Legendary",75000),
    ("Неймар","🇧🇷","LW",91,"Legendary",90000),
    ("Антуан Гризманн","🇫🇷","CF",89,"Legendary",70000),
    ("Тибо Куртуа","🇧🇪","GK",90,"Legendary",70000),
    ("Алиссон","🇧🇷","GK",89,"Legendary",65000),
    ("Ван Дейк","🇳🇱","CB",89,"Legendary",65000),

    ("Лионель Месси","🇦🇷","RW",95,"Icon",150000),
    ("Криштиану Роналду","🇵🇹","ST",94,"Icon",140000),
    ("Роналдиньо","🇧🇷","LW",96,"Icon",220000),
    ("Зинедин Зидан","🇫🇷","CAM",97,"Icon",250000),
    ("Роналдо Назарио","🇧🇷","ST",97,"Icon",250000),
    ("Пеле","🇧🇷","ST",98,"Icon",350000),
    ("Марадона","🇦🇷","CAM",97,"Icon",300000),
    ("Кройфф","🇳🇱","CF",96,"Icon",230000),
    ("Мальдини","🇮🇹","CB",96,"Icon",230000),
    ("Кака","🇧🇷","CAM",95,"Icon",200000),
    ("Тьерри Анри","🇫🇷","ST",96,"Icon",220000),
    ("Иньеста","🇪🇸","CM",96,"Icon",220000),

    ("Месси Ultimate","🇦🇷","RW",99,"Ultimate",500000),
    ("Роналду Ultimate","🇵🇹","ST",99,"Ultimate",500000),
    ("Пеле Ultimate","🇧🇷","ST",99,"Ultimate",500000),
    ("Марадона Ultimate","🇦🇷","CAM",99,"Ultimate",500000),

    ("Александр Исак","🇸🇪","ST",86,"Super Rare",27000),
    ("Виктор Осимхен","🇳🇬","ST",86,"Super Rare",27000),
    ("Хулиан Альварес","🇦🇷","ST",87,"Super Rare",30000),
    ("Виктор Дьёкереш","🇸🇪","ST",86,"Super Rare",27000),
    ("Александр Митрович","🇷🇸","ST",80,"Rare",9000),
    ("Олли Уоткинс","🏴","ST",84,"Rare",18000),
    ("Дарвин Нуньес","🇺🇾","ST",83,"Rare",16000),
    ("Джонатан Дэвид","🇨🇦","ST",84,"Rare",18000),
    ("Луис Диас","🇨🇴","LW",85,"Super Rare",23000),
    ("Лерой Сане","🇩🇪","RW",84,"Rare",18000),
    ("Кингсли Коман","🇫🇷","LW",84,"Rare",18000),
    ("Букаё Сака","🏴","RW",89,"Epic",45000),
    ("Мартин Эдегор","🇳🇴","CAM",87,"Super Rare",30000),
    ("Деклан Райс","🏴","CDM",87,"Super Rare",30000),
    ("Бруну Фернандеш","🇵🇹","CAM",88,"Epic",40000),
    ("Матео Ковачич","🇭🇷","CM",84,"Rare",18000),
    ("Френки де Йонг","🇳🇱","CM",86,"Super Rare",27000),
    ("Николо Барелла","🇮🇹","CM",87,"Super Rare",30000),
    ("Хакан Чалханоглу","🇹🇷","CM",86,"Super Rare",27000),
    ("Маркус Тюрам","🇫🇷","ST",84,"Rare",18000),
    ("Кенан Йылдыз","🇹🇷","LW",82,"Rare",12000),
    ("Виктор Цыганков","🇺🇦","RW",82,"Rare",12000),
    ("Микель Оярсабаль","🇪🇸","LW",83,"Rare",16000),
    ("Ферран Торрес","🇪🇸","RW",82,"Rare",12000),
    ("Алекс Баэна","🇪🇸","CAM",83,"Rare",16000),
    ("Микель Мерино","🇪🇸","CM",84,"Rare",18000),
    ("Марк Кукурелья","🇪🇸","LB",82,"Rare",12000),
    ("Пау Торрес","🇪🇸","CB",83,"Rare",16000),
    ("Аймерик Лапорт","🇪🇸","CB",84,"Rare",18000),
    ("Дани Карвахаль","🇪🇸","RB",85,"Super Rare",23000),
    ("Андреа Камбьязо","🇮🇹","LB",81,"Rare",10000),
    ("Алессандро Бастони","🇮🇹","CB",87,"Super Rare",30000),
    ("Франческо Ачерби","🇮🇹","CB",81,"Rare",10000),
    ("Джанлука Манчини","🇮🇹","CB",82,"Rare",12000),
    ("Давиде Фраттези","🇮🇹","CM",82,"Rare",12000),
    ("Лоренцо Пеллегрини","🇮🇹","CAM",83,"Rare",16000),
    ("Федерико Димарко","🇮🇹","LB",85,"Super Rare",23000),
    ("Мойзе Кин","🇮🇹","ST",81,"Rare",10000),
    ("Маттиа Дзакканьи","🇮🇹","LW",83,"Rare",16000),
    ("Жоржиньо","🇮🇹","CM",82,"Rare",12000),
    ("Доменико Берарди","🇮🇹","RW",82,"Rare",12000),
    ("Бенжамен Павар","🇫🇷","CB",83,"Rare",16000),
    ("Ибраима Конате","🇫🇷","CB",85,"Super Rare",23000),
    ("Люка Эрнандес","🇫🇷","CB",84,"Rare",18000),
    ("Усман Дембеле","🇫🇷","RW",88,"Epic",40000),
    ("Адриен Рабьо","🇫🇷","CM",82,"Rare",12000),
    ("Рандаль Коло Муани","🇫🇷","ST",82,"Rare",12000),
    ("Брэдли Баркола","🇫🇷","LW",84,"Rare",18000),
    ("Дезире Дуэ","🇫🇷","CAM",82,"Rare",12000),
    ("Лоис Опенда","🇧🇪","ST",84,"Rare",18000),
    ("Ромелу Лукаку","🇧🇪","ST",84,"Rare",18000),
    ("Юри Тилеманс","🇧🇪","CM",82,"Rare",12000),
    ("Амаду Онана","🇧🇪","CDM",81,"Rare",10000),
    ("Йохан Бакайоко","🇧🇪","RW",81,"Rare",10000),
    ("Кеннет Тейлор","🇳🇱","CM",80,"Rare",9000),
    ("Маттейс де Лигт","🇳🇱","CB",84,"Rare",18000),
    ("Натан Аке","🇳🇱","CB",83,"Rare",16000),
    ("Дензел Дюмфрис","🇳🇱","RB",84,"Rare",18000),
    ("Мемфис Депай","🇳🇱","ST",82,"Rare",12000),
    ("Коди Гакпо","🇳🇱","LW",84,"Rare",18000),
    ("Тён Копмейнерс","🇳🇱","CM",83,"Rare",16000),
    ("Райан Гравенберх","🇳🇱","CM",83,"Rare",16000),
    ("Майки Мур","🏴","RW",78,"Common",5000),
    ("Эберечи Эзе","🏴","CAM",84,"Rare",18000),
    ("Энтони Гордон","🏴","LW",83,"Rare",16000),
    ("Джеймс Мэддисон","🏴","CAM",84,"Rare",18000),
    ("Морган Гиббс-Уайт","🏴","CAM",82,"Rare",12000),
    ("Адам Уортон","🏴","CM",80,"Rare",9000),
    ("Кайл Уокер","🏴","RB",83,"Rare",16000),
    ("Джон Стоунз","🏴","CB",84,"Rare",18000),
    ("Люк Шоу","🏴","LB",81,"Rare",10000),
    ("Киран Триппьер","🏴","RB",81,"Rare",10000),
    ("Иван Перишич","🇭🇷","LW",80,"Rare",9000),
    ("Иосип Сутало","🇭🇷","CB",80,"Rare",9000),
    ("Йошко Гвардиол","🇭🇷","CB",85,"Super Rare",23000),
    ("Бруно Петкович","🇭🇷","ST",80,"Rare",9000),
    ("Андрей Крамарич","🇭🇷","ST",82,"Rare",12000),
    ("Никола Влашич","🇭🇷","CAM",80,"Rare",9000),
    ("Лука Модрич","🇭🇷","CM",85,"Super Rare",23000),
    ("Мануэль Угарте","🇺🇾","CDM",82,"Rare",12000),
    ("Факундо Пельистри","🇺🇾","RW",79,"Common",6000),
    ("Максимилиано Араухо","🇺🇾","LW",81,"Rare",10000),
    ("Мануэль Аканжи","🇨🇭","CB",83,"Rare",16000),
    ("Гранит Джака","🇨🇭","CM",84,"Rare",18000),
    ("Ремо Фройлер","🇨🇭","CDM",78,"Common",5000),
    ("Брель Эмболо","🇨🇭","ST",80,"Rare",9000),
    ("Янн Зоммер","🇨🇭","GK",83,"Rare",16000),
    ("Рияд Марез","🇩🇿","RW",83,"Rare",16000),
    ("Саид Бенрахма","🇩🇿","LW",79,"Common",6000),
    ("Исмаэль Беннасер","🇩🇿","CM",81,"Rare",10000),
    ("Ахраф Хакими","🇲🇦","RB",88,"Epic",40000),
    ("Софьян Амрабат","🇲🇦","CDM",81,"Rare",10000),
    ("Юссеф Эн-Несири","🇲🇦","ST",81,"Rare",10000),
    ("Билал Эль-Ханнус","🇲🇦","CAM",80,"Rare",9000),
    ("Софьян Буфаль","🇲🇦","LW",79,"Common",6000),
    ("Такефуса Кубо","🇯🇵","RW",84,"Rare",18000),
    ("Каору Митома","🇯🇵","LW",82,"Rare",12000),
    ("Даити Камада","🇯🇵","CAM",80,"Rare",9000),
    ("Ватару Эндо","🇯🇵","CDM",80,"Rare",9000),
    ("Такуми Минамино","🇯🇵","CAM",81,"Rare",10000),
    ("Ким Мин Джэ","🇰🇷","CB",85,"Super Rare",23000),
    ("Ли Кан Ин","🇰🇷","CAM",83,"Rare",16000),
    ("Хван Хи Чхан","🇰🇷","ST",81,"Rare",10000),
    ("Ким Сын Гю","🇰🇷","GK",78,"Common",5000),
    ("Сердар Азмун","🇮🇷","ST",80,"Rare",9000),
    ("Мехди Тареми","🇮🇷","ST",82,"Rare",12000),
    ("Ирфан Джан Кахведжи","🇹🇷","CAM",80,"Rare",9000),
    ("Оркун Кёкчю","🇹🇷","CM",82,"Rare",12000),
    ("Керем Актюркоглу","🇹🇷","LW",82,"Rare",12000),
    ("Абдюлькерим Бардакчи","🇹🇷","CB",79,"Common",6000),
    ("Ферди Кадыоглу","🇹🇷","LB",82,"Rare",12000),
    ("Дженк Тосун","🇹🇷","ST",78,"Common",5000),
    ("Мерих Демирал","🇹🇷","CB",80,"Rare",9000),
    ("Мартин Батурина","🇭🇷","CAM",79,"Common",6000),
    ("Виктор Бонифейс","🇳🇬","ST",83,"Rare",16000),
    ("Адемола Лукман","🇳🇬","RW",84,"Rare",18000),
    ("Саму Омордион","🇪🇸","ST",81,"Rare",10000),
    ("Родриго","🇧🇷","RW",88,"Epic",40000),
    ("Габриэл Мартинелли","🇧🇷","LW",83,"Rare",16000),
    ("Бруно Гимарайнс","🇧🇷","CM",86,"Super Rare",27000),
    ("Дуглас Луис","🇧🇷","CM",82,"Rare",12000),
    ("Жоао Педро","🇧🇷","ST",82,"Rare",12000),
    ("Эдерсон","🇧🇷","GK",88,"Epic",40000),
    ("Маркиньос","🇧🇷","CB",87,"Super Rare",30000),
    ("Габриэл Магальяйнс","🇧🇷","CB",85,"Super Rare",23000),
    ("Эмерсон Роял","🇧🇷","RB",79,"Common",6000),
    ("Каземиро","🇧🇷","CDM",82,"Rare",12000),
    ("Фабиньо","🇧🇷","CDM",81,"Rare",10000),
    ("Анхель Ди Мария","🇦🇷","RW",84,"Rare",18000),
    ("Пауло Дибала","🇦🇷","CAM",85,"Super Rare",23000),
    ("Алексис Мак Аллистер","🇦🇷","CM",86,"Super Rare",27000),
    ("Эмилиано Мартинес","🇦🇷","GK",87,"Super Rare",30000),
    ("Кристиан Ромеро","🇦🇷","CB",86,"Super Rare",27000),
    ("Лисандро Мартинес","🇦🇷","CB",84,"Rare",18000),
    ("Николас Отаменди","🇦🇷","CB",80,"Rare",9000),
    ("Леандро Паредес","🇦🇷","CDM",81,"Rare",10000),
    ("Анхель Корреа","🇦🇷","RW",81,"Rare",10000),
    ("Энцо Диас","🇦🇷","LB",78,"Common",5000),
    ("Родриго Де Пауль","🇦🇷","CM",84,"Rare",18000),
    ("Николас Гонсалес","🇦🇷","LW",82,"Rare",12000),
    ("Савио","🇧🇷","RW",81,"Rare",10000),
    ("Эстевао","🇧🇷","RW",80,"Rare",9000),
    ("Витор Роке","🇧🇷","ST",79,"Common",6000),
    ("Андре Сантос","🇧🇷","CM",77,"Common",5000),
    ("Жоау Невеш","🇵🇹","CM",84,"Rare",18000),
    ("Витинья","🇵🇹","CM",87,"Super Rare",30000),
    ("Нуну Мендеш","🇵🇹","LB",85,"Super Rare",23000),
    ("Диогу Жота","🇵🇹","ST",84,"Rare",18000),
    ("Гонсалу Рамуш","🇵🇹","ST",81,"Rare",10000),
    ("Педру Нету","🇵🇹","RW",83,"Rare",16000),
    ("Диогу Кошта","🇵🇹","GK",84,"Rare",18000),
    ("Рубен Диаш","🇵🇹","CB",87,"Super Rare",30000),
    ("Вильям Карвалью","🇵🇹","CDM",80,"Rare",9000),
    ("Рикарду Орта","🇵🇹","LW",80,"Rare",9000),
    ("Матеус Нунес","🇵🇹","CM",81,"Rare",10000),
    ("Бенуа Бадьяшиль","🇫🇷","CB",80,"Rare",9000),
    ("Леви Колвилл","🏴","CB",81,"Rare",10000),
    ("Мало Гюсто","🇫🇷","RB",81,"Rare",10000),
    ("Рис Джеймс","🏴","RB",84,"Rare",18000),
    ("Николас Джексон","🇸🇳","ST",82,"Rare",12000),
    ("Мойсес Кайседо","🇪🇨","CDM",84,"Rare",18000),
    ("Ромео Лавия","🇧🇪","CDM",78,"Common",5000),
    ("Марк Гехи","🏴","CB",82,"Rare",12000),
    ("Жан-Филипп Матета","🇫🇷","ST",81,"Rare",10000),
    ("Джаррод Боуэн","🏴","RW",83,"Rare",16000),
    ("Лукас Пакета","🇧🇷","CAM",83,"Rare",16000),
    ("Мохаммед Кудус","🇬🇭","RW",82,"Rare",12000),
    ("Майкл Кайоде","🇮🇹","RB",77,"Common",5000),
    ("Пьеро Инкапье","🇪🇨","CB",80,"Rare",9000),
    ("Пьер-Эмерик Обамеянг","🇬🇦","ST",81,"Rare",10000),
    ("Садио Мане","🇸🇳","LW",84,"Rare",18000),
    ("Калиду Кулибали","🇸🇳","CB",80,"Rare",9000),
    ("Исмаила Сарр","🇸🇳","RW",80,"Rare",9000),
    ("Майрон Боаду","🇳🇱","ST",78,"Common",5000),
    ("Арно Данджума","🇳🇱","LW",79,"Common",6000),
    ("Стивен Бергвейн","🇳🇱","LW",80,"Rare",9000),
    ("Ваут Вегхорст","🇳🇱","ST",79,"Common",6000),
    ("Ноа Ланг","🇳🇱","LW",81,"Rare",10000),
    ("Мохамед Эль-Шеннави","🇪🇬","GK",78,"Common",5000),
    ("Махмуд Хассан","🇪🇬","LW",77,"Common",5000),
    ("Трезеге","🇪🇬","LW",80,"Rare",9000),
    ("Омар Мармуш","🇪🇬","ST",84,"Rare",18000),
    ("Мостафа Мохамед","🇪🇬","ST",78,"Common",5000),
    ("Андре Онана","🇨🇲","GK",82,"Rare",12000),
    ("Брайан Мбемо","🇨🇲","RW",84,"Rare",18000),
    ("Йереми Пино","🇪🇸","RW",80,"Rare",9000),
    ("Серхио Регилон","🇪🇸","LB",77,"Common",5000),
    ("Луис Суарес","🇺🇾","ST",83,"Rare",16000),
]

# =========================================================
# STARS / COIN PACKS
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
            created_at INTEGER NOT NULL
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
            activations INTEGER NOT NULL DEFAULT 1,
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
        CREATE TABLE IF NOT EXISTS events(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            multiplier REAL DEFAULT 1,
            rarity TEXT DEFAULT '',
            ends_at INTEGER NOT NULL,
            active INTEGER DEFAULT 1
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
            "SELECT coins,banned FROM users WHERE user_id=?",
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
            "UPDATE users SET coins=coins-? WHERE user_id=?",
            (amount, user_id)
        )

        await db.commit()
        return True


async def add_card(user_id, player):
    async with aiosqlite.connect(DB) as db:
        await db.execute("""
        INSERT INTO cards
        (
            user_id,
            name,
            nation,
            position,
            rating,
            rarity,
            price,
            created_at
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            user_id,
            player[0],
            player[1],
            player[2],
            player[3],
            player[4],
            player[5],
            int(time.time())
        ))

        await db.commit()


async def mission_update(user_id, field):
    if field not in ("drops", "cards"):
        return

    async with aiosqlite.connect(DB) as db:
        await db.execute(
            f"""
            UPDATE missions
            SET {field}={field}+1
            WHERE user_id=?
            """,
            (user_id,)
        )

        await db.commit()


def is_owner(user):
    username = (user.username or "").lower()

    if OWNER_ID and user.id == OWNER_ID:
        return True

    return username == OWNER.lower()


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
            "member"
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
        "После подписки нажми кнопку проверки.",
        reply_markup=subscribe_keyboard(),
        parse_mode="HTML"
    )

    return False


@DP.callback_query(F.data == "check_sub")
async def check_subscription_callback(callback: CallbackQuery):

    if await check_access(callback.from_user.id):
        await callback.answer(
            "✅ Подписка подтверждена!",
            show_alert=True
        )

        await callback.message.answer(
            "✅ Доступ открыт!\n\n"
            "Теперь можешь пользоваться Football Drop."
        )

    else:
        await callback.answer(
            "❌ Подписка не найдена.",
            show_alert=True
        )


# =========================================================
# EVENTS
# =========================================================

async def get_active_event():
    now = int(time.time())

    async with aiosqlite.connect(DB) as db:
        db.row_factory = aiosqlite.Row

        await db.execute(
            """
            UPDATE events
            SET active=0
            WHERE ends_at <= ?
            """,
            (now,)
        )

        cur = await db.execute("""
            SELECT *
            FROM events
            WHERE active=1
            AND ends_at>?
            ORDER BY id DESC
            LIMIT 1
        """, (now,))

        event = await cur.fetchone()

        await db.commit()

        return event


async def notify_all_users(text):
    async with aiosqlite.connect(DB) as db:
        cur = await db.execute(
            "SELECT user_id FROM users WHERE banned=0"
        )

        users = await cur.fetchall()

    sent = 0

    for row in users:
        try:
            await BOT.send_message(
                row[0],
                text,
                parse_mode="HTML"
            )

            sent += 1

            await asyncio.sleep(0.03)

        except Exception:
            pass

    return sent


@DP.message(Command("event"))
async def event_command(message: Message):
    if not is_owner(message.from_user):
        return

    parts = message.text.split()

    if len(parts) < 2:
        await message.answer(
            "🎪 <b>УПРАВЛЕНИЕ ИВЕНТАМИ</b>\n\n"
            "<code>/event start Название 60</code>\n"
            "<code>/event stop</code>\n"
            "<code>/event status</code>\n\n"
            "Последнее число — длительность в минутах.",
            parse_mode="HTML"
        )
        return

    action = parts[1].lower()

    if action == "start":

        if len(parts) < 4:
            await message.answer(
                "Используй:\n"
                "<code>/event start Название 60</code>",
                parse_mode="HTML"
            )
            return

        name = " ".join(parts[2:-1])

        try:
            minutes = int(parts[-1])
        except ValueError:
            await message.answer("❌ Длительность должна быть числом.")
            return

        if minutes <= 0:
            await message.answer("❌ Время должно быть больше 0.")
            return

        ends_at = int(time.time()) + minutes * 60

        async with aiosqlite.connect(DB) as db:

            await db.execute(
                "UPDATE events SET active=0 WHERE active=1"
            )

            await db.execute("""
                INSERT INTO events
                (name, multiplier, rarity, ends_at, active)
                VALUES (?, ?, ?, ?, 1)
            """, (
                name,
                1.0,
                "",
                ends_at
            ))

            await db.commit()

        text = (
            "🔥 <b>НОВЫЙ ИВЕНТ!</b>\n\n"
            f"🎪 <b>{html.escape(name)}</b>\n"
            f"⏳ Длительность: <b>{minutes} мин.</b>\n\n"
            "⚽ Ивент уже активен!"
        )

        await message.answer(text, parse_mode="HTML")

        await notify_all_users(text)

        return

    if action == "stop":

        async with aiosqlite.connect(DB) as db:
            await db.execute(
                "UPDATE events SET active=0 WHERE active=1"
            )
            await db.commit()

        await message.answer(
            "🛑 <b>Ивент остановлен.</b>",
            parse_mode="HTML"
        )

        return

    if action == "status":

        event = await get_active_event()

        if not event:
            await message.answer(
                "🎪 Сейчас активных ивентов нет."
            )
            return

        left = event["ends_at"] - int(time.time())

        await message.answer(
            "🎪 <b>АКТИВНЫЙ ИВЕНТ</b>\n\n"
            f"🔥 {html.escape(event['name'])}\n"
            f"⏳ Осталось: <b>{left // 60} мин.</b>",
            parse_mode="HTML"
        )


# =========================================================
# RARITY / DROP
# =========================================================

def choose_rarity(user=None, event=None):

    names = list(RARITIES.keys())
    weights = list(RARITIES.values())

    if user and user["lucky_until"] > int(time.time()):

        weights = [
            weight * (
                LUCKY_MULTIPLIER
                if rarity != "Common"
                else 1
            )
            for rarity, weight in zip(names, weights)
        ]

    if event:

        weights = [
            weight * (
                float(event["multiplier"])
                if rarity != "Common"
                else 1
            )
            for rarity, weight in zip(names, weights)
        ]

    return random.choices(
        names,
        weights=weights,
        k=1
    )[0]


def random_player(user=None, event=None):

    rarity = choose_rarity(
        user,
        event
    )

    pool = [
        p for p in PLAYERS
        if p[4] == rarity
    ]

    if not pool:
        pool = [
            p for p in PLAYERS
            if p[4] == "Common"
        ]

    return random.choice(pool)


# =========================================================
# KEYBOARDS
# =========================================================

def main_keyboard():

    kb = InlineKeyboardBuilder()

    buttons = [
        ("🃏 DROP", "drop"),
        ("📚 Коллекция", "collection"),
        ("👤 Профиль", "profile"),
        ("🏪 Магазин", "shop"),
        ("💰 Продать карты", "sell_menu"),
        ("🎁 Daily", "daily"),
        ("🎯 Задания", "missions"),
        ("🏆 Рейтинг", "top"),
        ("📦 Паки за 🪙", "coinpacks"),
        ("⭐ Паки за Stars", "packs"),
        ("🎟️ Промокод", "promo"),
        ("🍀 Lucky Charm", "lucky"),
        ("🎪 Ивент", "event_info"),
    ]

    for text, data in buttons:
        kb.button(
            text=text,
            callback_data=data
        )

    kb.adjust(2)

    return kb.as_markup()


# =========================================================
# START
# =========================================================

@DP.message(Command("start"))
async def start(message: Message):

    await register(message.from_user)

    if not await require_subscription(message):
        return

    user = await get_user(message.from_user.id)

    if user["banned"] and not is_owner(message.from_user):
        await message.answer("🚫 Вы заблокированы.")
        return

    await message.answer(
        f"⚽ <b>FOOTBALL DROP</b>\n\n"
        f"Привет, <b>{html.escape(message.from_user.first_name)}</b>!\n\n"
        f"🪙 Монеты: <b>{user['coins']:,}</b>\n"
        f"🃏 Карт: <b>{await count_cards(message.from_user.id)}</b>\n\n"
        "Используй кнопки ниже:",
        reply_markup=main_keyboard(),
        parse_mode="HTML"
    )


# =========================================================
# DROP
# =========================================================

async def do_drop(message: Message):

    await register(message.from_user)

    if not await require_subscription(message):
        return

    user = await get_user(message.from_user.id)

    if user["banned"] and not is_owner(message.from_user):
        await message.answer("🚫 Вы заблокированы.")
        return

    now = int(time.time())

    if not is_owner(message.from_user):

        if user["last_drop"]:

            remaining = DROP_COOLDOWN - (
                now - user["last_drop"]
            )

            if remaining > 0:
                await message.answer(
                    f"⏳ Следующий DROP через "
                    f"<b>{remaining} сек.</b>",
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
                message.from_user.id
            )
        )

        await db.commit()

    await message.answer(
        "📦 <b>ПАК ОТКРЫВАЕТСЯ...</b>",
        parse_mode="HTML"
    )

    await asyncio.sleep(0.7)

    user = await get_user(message.from_user.id)
    event = await get_active_event()

    player = random_player(
        user,
        event
    )

    await add_card(
        message.from_user.id,
        player
    )

    await mission_update(
        message.from_user.id,
        "drops"
    )

    await mission_update(
        message.from_user.id,
        "cards"
    )

    coins = random.randint(
        100,
        400
    )

    await add_coins(
        message.from_user.id,
        coins
    )

    name, nation, pos, rating, rarity, price = player

    event_text = ""

    if event:
        event_text = (
            f"\n🎪 Ивент: <b>{html.escape(event['name'])}</b>"
        )

    await message.answer(
        f"{RARITY_EMOJI[rarity]} "
        f"<b>{rarity.upper()}</b>\n\n"
        f"{nation} <b>{html.escape(name)}</b>\n"
        f"⚡ Позиция: <b>{pos}</b>\n"
        f"⭐ Рейтинг: <b>{rating}</b>\n"
        f"💰 Цена: <b>€{price:,}</b>\n"
        f"🪙 Бонус: <b>+{coins}</b>"
        f"{event_text}\n\n"
        "📚 Карта добавлена!",
        parse_mode="HTML"
    )


@DP.message(Command("drop"))
async def drop_command(message: Message):
    await do_drop(message)


@DP.callback_query(F.data == "drop")
async def drop_callback(callback: CallbackQuery):
    await callback.answer()
    await do_drop(callback.message)


# =========================================================
# PROFILE
# =========================================================

async def show_profile(message):

    await register(message.from_user)

    if not await require_subscription(message):
        return

    user = await get_user(
        message.from_user.id
    )

    lucky = (
        "активен"
        if user["lucky_until"] > int(time.time())
        else "нет"
    )

    await message.answer(
        "👤 <b>ПРОФИЛЬ</b>\n\n"
        f"👤 {html.escape(message.from_user.first_name)}\n"
        f"🪙 Монеты: <b>{user['coins']:,}</b>\n"
        f"⭐ Stars: <b>{user['stars']:,}</b>\n"
        f"🃏 Карт: <b>{await count_cards(message.from_user.id)}</b>\n"
        f"🏆 Побед: <b>{user['wins']}</b>\n"
        f"💀 Поражений: <b>{user['losses']}</b>\n"
        f"🍀 Lucky Charm: <b>{lucky}</b>",
        parse_mode="HTML"
    )


@DP.message(Command("profile"))
async def profile_command(message: Message):
    await show_profile(message)


@DP.callback_query(F.data == "profile")
async def profile_callback(callback: CallbackQuery):
    await callback.answer()
    await show_profile(callback.message)


# =========================================================
# COLLECTION
# =========================================================

async def show_collection(message):

    await register(message.from_user)

    if not await require_subscription(message):
        return

    async with aiosqlite.connect(DB) as db:

        db.row_factory = aiosqlite.Row

        cur = await db.execute("""
            SELECT *
            FROM cards
            WHERE user_id=?
            ORDER BY rating DESC, id DESC
            LIMIT 100
        """, (
            message.from_user.id,
        ))

        cards = await cur.fetchall()

    if not cards:

        await message.answer(
            "📚 <b>Коллекция пуста.</b>\n\n"
            "Открой свой первый DROP ⚽",
            parse_mode="HTML"
        )

        return

    text = "📚 <b>ТВОЯ КОЛЛЕКЦИЯ</b>\n\n"

    kb = InlineKeyboardBuilder()

    for card in cards:

        text += (
            f"ID <code>{card['id']}</code> | "
            f"{RARITY_EMOJI.get(card['rarity'], '⚪')} "
            f"<b>{html.escape(card['name'])}</b>\n"
            f"⭐ {card['rating']} | "
            f"💰 €{card['price']:,}\n\n"
        )

        kb.button(
            text=f"💰 Продать #{card['id']}",
            callback_data=f"sell:{card['id']}"
        )

    kb.button(
        text="💰 Продать ВСЕ карты",
        callback_data="sell_all"
    )

    kb.adjust(2)

    await message.answer(
        text,
        reply_markup=kb.as_markup(),
        parse_mode="HTML"
    )


@DP.message(Command("collection"))
async def collection_command(message: Message):
    await show_collection(message)


@DP.callback_query(F.data == "collection")
async def collection_callback(callback: CallbackQuery):
    await callback.answer()
    await show_collection(callback.message)


# =========================================================
# ПРОДАЖА КАРТ БОТУ
# =========================================================

@DP.callback_query(F.data == "sell_menu")
async def sell_menu_callback(callback: CallbackQuery):

    await callback.answer()

    await show_collection(
        callback.message
    )


@DP.callback_query(F.data.startswith("sell:"))
async def sell_card_callback(callback: CallbackQuery):

    await callback.answer()

    try:
        card_id = int(
            callback.data.split(":")[1]
        )
    except Exception:
        await callback.message.answer(
            "❌ Ошибка карты."
        )
        return

    async with aiosqlite.connect(DB) as db:

        db.row_factory = aiosqlite.Row

        cur = await db.execute("""
            SELECT *
            FROM cards
            WHERE id=? AND user_id=?
        """, (
            card_id,
            callback.from_user.id
        ))

        card = await cur.fetchone()

        if not card:
            await callback.message.answer(
                "❌ Карта уже продана или не принадлежит тебе."
            )
            return

        sell_price = card["price"]

        await db.execute("""
            DELETE FROM cards
            WHERE id=? AND user_id=?
        """, (
            card_id,
            callback.from_user.id
        ))

        await db.execute("""
            UPDATE users
            SET coins=coins+?
            WHERE user_id=?
        """, (
            sell_price,
            callback.from_user.id
        ))

        await db.commit()

    await callback.message.answer(
        "💰 <b>КАРТА ПРОДАНА БОТУ!</b>\n\n"
        f"👤 {html.escape(card['name'])}\n"
        f"⭐ Рейтинг: <b>{card['rating']}</b>\n"
        f"💎 Редкость: <b>{card['rarity']}</b>\n"
        f"💵 Получено: <b>€{sell_price:,}</b>",
        parse_mode="HTML"
    )


@DP.callback_query(F.data == "sell_all")
async def sell_all_callback(callback: CallbackQuery):

    await callback.answer()

    async with aiosqlite.connect(DB) as db:

        cur = await db.execute("""
            SELECT COALESCE(SUM(price),0), COUNT(*)
            FROM cards
            WHERE user_id=?
        """, (
            callback.from_user.id,
        ))

        total, count = await cur.fetchone()

        if count == 0:
            await callback.message.answer(
                "📚 У тебя нет карт."
            )
            return

        await db.execute(
            "DELETE FROM cards WHERE user_id=?",
            (callback.from_user.id,)
        )

        await db.execute("""
            UPDATE users
            SET coins=coins+?
            WHERE user_id=?
        """, (
            total,
            callback.from_user.id
        ))

        await db.commit()

    await callback.message.answer(
        "💰 <b>ВСЕ КАРТЫ ПРОДАНЫ БОТУ!</b>\n\n"
        f"🃏 Карт продано: <b>{count}</b>\n"
        f"💵 Получено: <b>€{total:,}</b>",
        parse_mode="HTML"
    )


# =========================================================
# COIN PACKS
# =========================================================

@DP.message(Command("coinpacks"))
async def coinpacks_command(message: Message):

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
        "📦 <b>ПАКИ ЗА МОНЕТЫ</b>\n\n"
        "Стоимость указана в 🪙.\n"
        "Пак открывается сразу.",
        reply_markup=kb.as_markup(),
        parse_mode="HTML"
    )


@DP.callback_query(F.data == "coinpacks")
async def coinpacks_callback(callback: CallbackQuery):

    await callback.answer()

    kb = InlineKeyboardBuilder()

    for key, (price, amount, name) in COIN_PACKS.items():

        kb.button(
            text=f"{name} — {price:,} 🪙",
            callback_data=f"coinpack:{key}"
        )

    kb.adjust(1)

    await callback.message.answer(
        "📦 <b>ПАКИ ЗА МОНЕТЫ</b>",
        reply_markup=kb.as_markup(),
        parse_mode="HTML"
    )


@DP.callback_query(F.data.startswith("coinpack:"))
async def coinpack_callback(callback: CallbackQuery):

    await callback.answer()

    key = callback.data.split(":")[1]

    if key not in COIN_PACKS:
        return

    price, amount, name = COIN_PACKS[key]

    if not is_owner(callback.from_user):

        if not await spend_coins(
            callback.from_user.id,
            price
        ):
            await callback.message.answer(
                "❌ Недостаточно 🪙."
            )
            return

    user = await get_user(
        callback.from_user.id
    )

    pulled = []

    for _ in range(amount):

        event = await get_active_event()

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
        f"📦 <b>{name}</b>\n\n"
        f"🃏 Получено карт: <b>{amount}</b>\n\n"
        f"🔥 Лучшая карта:\n"
        f"{RARITY_EMOJI[best[4]]} "
        f"<b>{html.escape(best[0])}</b>\n"
        f"⭐ {best[3]} OVR\n"
        f"💰 €{best[5]:,}",
        parse_mode="HTML"
    )


# =========================================================
# SHOP
# =========================================================

async def show_shop(message):

    kb = InlineKeyboardBuilder()

    kb.button(
        text="🍀 Lucky Charm",
        callback_data="lucky"
    )

    kb.button(
        text="📦 Паки",
        callback_data="packs"
    )

    kb.button(
        text="💰 Продать карты",
        callback_data="sell_menu"
    )

    kb.button(
        text="⬅️ Назад",
        callback_data="back_main"
    )

    kb.adjust(1)

    await message.answer(
        "🏪 <b>МАГАЗИН</b>\n\n"
        "🍀 Lucky Charm\n"
        "📦 Паки\n"
        "💰 Продажа карт боту",
        reply_markup=kb.as_markup(),
        parse_mode="HTML"
    )


@DP.message(Command("shop"))
async def shop_command(message: Message):
    await register(message.from_user)
    await show_shop(message)


@DP.callback_query(F.data == "shop")
async def shop_callback(callback: CallbackQuery):
    await callback.answer()
    await show_shop(callback.message)


# =========================================================
# LUCKY CHARM
# =========================================================

@DP.message(Command("lucky"))
async def lucky_command(message: Message):

    await register(message.from_user)

    if not await require_subscription(message):
        return

    user = await get_user(
        message.from_user.id
    )

    now = int(time.time())

    if user["lucky_until"] > now:

        left = user["lucky_until"] - now

        await message.answer(
            "🍀 <b>LUCKY CHARM АКТИВЕН</b>\n\n"
            f"⏳ Осталось: "
            f"<b>{left // 3600}ч "
            f"{(left % 3600) // 60}м</b>\n"
            "🔥 Шанс редких карт увеличен x3.",
            parse_mode="HTML"
        )

        return

    await BOT.send_invoice(
        chat_id=message.from_user.id,
        title="🍀 Lucky Charm",
        description="24 часа повышенного шанса редких карт.",
        payload=f"lucky:{message.from_user.id}",
        currency="XTR",
        prices=[
            LabeledPrice(
                label="Lucky Charm",
                amount=LUCKY_COST
            )
        ]
    )


@DP.callback_query(F.data == "lucky")
async def lucky_callback(callback: CallbackQuery):

    await callback.answer()

    user = await get_user(
        callback.from_user.id
    )

    now = int(time.time())

    if user["lucky_until"] > now:

        left = user["lucky_until"] - now

        await callback.message.answer(
            "🍀 <b>LUCKY CHARM УЖЕ АКТИВЕН</b>\n\n"
            f"⏳ Осталось: "
            f"<b>{left // 3600}ч "
            f"{(left % 3600) // 60}м</b>",
            parse_mode="HTML"
        )

        return

    await BOT.send_invoice(
        chat_id=callback.from_user.id,
        title="🍀 Lucky Charm",
        description="24 часа повышенного шанса редких карт.",
        payload=f"lucky:{callback.from_user.id}",
        currency="XTR",
        prices=[
            LabeledPrice(
                label="Lucky Charm",
                amount=LUCKY_COST
            )
        ]
    )


@DP.pre_checkout_query()
async def pre_checkout(query: PreCheckoutQuery):

    await query.answer(
        ok=True
    )


@DP.message(F.successful_payment)
async def successful_payment(message: Message):

    payment = message.successful_payment

    if not payment:
        return

    payload = payment.invoice_payload

    if payload.startswith("lucky:"):

        user_id = int(
            payload.split(":")[1]
        )

        expires = int(time.time()) + (
            LUCKY_HOURS * 60 * 60
        )

        async with aiosqlite.connect(DB) as db:

            await db.execute("""
                UPDATE users
                SET lucky_until=?
                WHERE user_id=?
            """, (
                expires,
                user_id
            ))

            await db.execute("""
                INSERT INTO payments
                (user_id,product,stars,created)
                VALUES(?,?,?,?)
            """, (
                user_id,
                "Lucky Charm",
                payment.total_amount,
                int(time.time())
            ))

            await db.commit()

        await message.answer(
            "🍀 <b>LUCKY CHARM АКТИВИРОВАН!</b>\n\n"
            "⏳ Длительность: <b>24 часа</b>\n"
            "🔥 Бонус: <b>x3</b> к шансу редких карт.",
            parse_mode="HTML"
        )


# =========================================================
# PACKS ЗА STARS
# =========================================================

@DP.message(Command("packs"))
async def packs_command(message: Message):

    await register(message.from_user)

    if not await require_subscription(message):
        return

    kb = InlineKeyboardBuilder()

    for key, (stars, amount, name) in STAR_PACKS.items():

        kb.button(
            text=f"{name} — {stars} ⭐",
            callback_data=f"starpack:{key}"
        )

    kb.adjust(1)

    await message.answer(
        "⭐ <b>ПАКИ ЗА STARS</b>",
        reply_markup=kb.as_markup(),
        parse_mode="HTML"
    )


@DP.callback_query(F.data == "packs")
async def packs_callback(callback: CallbackQuery):

    await callback.answer()

    kb = InlineKeyboardBuilder()

    for key, (stars, amount, name) in STAR_PACKS.items():

        kb.button(
            text=f"{name} — {stars} ⭐",
            callback_data=f"starpack:{key}"
        )

    kb.adjust(1)

    await callback.message.answer(
        "⭐ <b>ПАКИ ЗА STARS</b>",
        reply_markup=kb.as_markup(),
        parse_mode="HTML"
    )


@DP.callback_query(F.data.startswith("starpack:"))
async def starpack_callback(callback: CallbackQuery):

    await callback.answer()

    key = callback.data.split(":")[1]

    if key not in STAR_PACKS:
        return

    stars, amount, name = STAR_PACKS[key]

    await BOT.send_invoice(
        chat_id=callback.from_user.id,
        title=name,
        description=f"Пак с {amount} картами.",
        payload=f"pack:{key}:{callback.from_user.id}",
        currency="XTR",
        prices=[
            LabeledPrice(
                label=name,
                amount=stars
            )
        ]
    )


@DP.message(F.successful_payment)
async def successful_pack_payment(message: Message):

    payment = message.successful_payment

    if not payment:
        return

    payload = payment.invoice_payload

    if not payload.startswith("pack:"):
        return

    parts = payload.split(":")

    if len(parts) != 3:
        return

    key = parts[1]
    user_id = int(parts[2])

    if key not in STAR_PACKS:
        return

    stars, amount, name = STAR_PACKS[key]

    user = await get_user(user_id)

    pulled = []

    for _ in range(amount):

        event = await get_active_event()

        player = random_player(
            user,
            event
        )

        await add_card(
            user_id,
            player
        )

        await mission_update(
            user_id,
            "cards"
        )

        pulled.append(player)

    best = max(
        pulled,
        key=lambda p: p[3]
    )

    async with aiosqlite.connect(DB) as db:
        await db.execute("""
            INSERT INTO payments
            (user_id,product,stars,created)
            VALUES(?,?,?,?)
        """, (
            user_id,
            name,
            stars,
            int(time.time())
        ))

        await db.commit()

    await message.answer(
        f"⭐ <b>{name}</b>\n\n"
        f"🃏 Карт: <b>{amount}</b>\n\n"
        f"🔥 Лучшая:\n"
        f"{RARITY_EMOJI[best[4]]} "
        f"<b>{html.escape(best[0])}</b>\n"
        f"⭐ {best[3]} OVR",
        parse_mode="HTML"
    )


# =========================================================
# DAILY
# =========================================================

@DP.message(Command("daily"))
async def daily_command(message: Message):

    await register(message.from_user)

    if not await require_subscription(message):
        return

    user = await get_user(
        message.from_user.id
    )

    today = datetime.now(
        timezone.utc
    ).strftime("%Y-%m-%d")

    if user["daily_date"] == today:

        await message.answer(
            "🎁 <b>Daily уже получен сегодня.</b>",
            parse_mode="HTML"
        )

        return

    reward = random.randint(
        1000,
        5000
    )

    streak = user["daily_streak"] + 1

    async with aiosqlite.connect(DB) as db:

        await db.execute("""
            UPDATE users
            SET coins=coins+?,
                daily_date=?,
                daily_streak=?
            WHERE user_id=?
        """, (
            reward,
            today,
            streak,
            message.from_user.id
        ))

        await db.commit()

    await message.answer(
        "🎁 <b>DAILY</b>\n\n"
        f"🪙 Получено: <b>+{reward:,}</b>\n"
        f"🔥 Серия: <b>{streak}</b>",
        parse_mode="HTML"
    )


# =========================================================
# BALANCE
# =========================================================

@DP.message(Command("balance"))
async def balance_command(message: Message):

    await register(message.from_user)

    user = await get_user(
        message.from_user.id
    )

    await message.answer(
        "💰 <b>БАЛАНС</b>\n\n"
        f"🪙 Монеты: <b>{user['coins']:,}</b>\n"
        f"⭐ Stars: <b>{user['stars']:,}</b>",
        parse_mode="HTML"
    )


# =========================================================
# MISSIONS
# =========================================================

@DP.message(Command("missions"))
async def missions_command(message: Message):

    await register(message.from_user)

    async with aiosqlite.connect(DB) as db:

        db.row_factory = aiosqlite.Row

        cur = await db.execute(
            "SELECT * FROM missions WHERE user_id=?",
            (message.from_user.id,)
        )

        mission = await cur.fetchone()

    await message.answer(
        "🎯 <b>ЗАДАНИЯ</b>\n\n"
        f"⚽ Сделать 10 дропов: "
        f"<b>{mission['drops']}/10</b>\n"
        f"🃏 Получить 20 карт: "
        f"<b>{mission['cards']}/20</b>\n\n"
        "Награды за задания можно добавить через "
        "админ-систему.",
        parse_mode="HTML"
    )


@DP.callback_query(F.data == "missions")
async def missions_callback(callback: CallbackQuery):

    await callback.answer()

    await missions_command(
        callback.message
    )


# =========================================================
# TOP
# =========================================================

@DP.message(Command("top"))
async def top_command(message: Message):

    await register(message.from_user)

    async with aiosqlite.connect(DB) as db:

        db.row_factory = aiosqlite.Row

        cur = await db.execute("""
            SELECT user_id, first_name, coins
            FROM users
            WHERE banned=0
            ORDER BY coins DESC
            LIMIT 10
        """)

        users = await cur.fetchall()

    text = "🏆 <b>ТОП 10</b>\n\n"

    for i, user in enumerate(users, 1):

        text += (
            f"{i}. "
            f"<b>{html.escape(user['first_name'])}</b> — "
            f"🪙 {user['coins']:,}\n"
        )

    await message.answer(
        text,
        parse_mode="HTML"
    )


@DP.callback_query(F.data == "top")
async def top_callback(callback: CallbackQuery):

    await callback.answer()

    await top_command(
        callback.message
    )


# =========================================================
# PROMO
# =========================================================

@DP.message(Command("promo"))
async def promo_command(message: Message):

    await register(message.from_user)

    parts = message.text.split()

    if len(parts) < 2:
        await message.answer(
            "🎟️ Использование:\n"
            "<code>/promo CODE</code>",
            parse_mode="HTML"
        )
        return

    code = parts[1].upper()

    async with aiosqlite.connect(DB) as db:

        db.row_factory = aiosqlite.Row

        cur = await db.execute(
            "SELECT * FROM promo_codes WHERE code=?",
            (code,)
        )

        promo = await cur.fetchone()

        if not promo:
            await message.answer(
                "❌ Промокод не найден."
            )
            return

        if promo["used"] >= promo["activations"]:
            await message.answer(
                "❌ Лимит активаций исчерпан."
            )
            return

        cur = await db.execute("""
            SELECT 1
            FROM promo_uses
            WHERE code=? AND user_id=?
        """, (
            code,
            message.from_user.id
        ))

        already = await cur.fetchone()

        if already:
            await message.answer(
                "❌ Ты уже использовал этот промокод."
            )
            return

        await db.execute("""
            INSERT INTO promo_uses(code,user_id)
            VALUES(?,?)
        """, (
            code,
            message.from_user.id
        ))

        await db.execute("""
            UPDATE promo_codes
            SET used=used+1
            WHERE code=?
        """, (code,))

        await db.execute("""
            UPDATE users
            SET coins=coins+?,
                stars=stars+?
            WHERE user_id=?
        """, (
            promo["coins"],
            promo["stars"],
            message.from_user.id
        ))

        await db.commit()

    await message.answer(
        "🎟️ <b>ПРОМОКОД АКТИВИРОВАН!</b>\n\n"
        f"🪙 +{promo['coins']:,}\n"
        f"⭐ +{promo['stars']}",
        parse_mode="HTML"
    )


# =========================================================
# EVENT INFO
# =========================================================

@DP.callback_query(F.data == "event_info")
async def event_info_callback(callback: CallbackQuery):

    await callback.answer()

    event = await get_active_event()

    if not event:

        await callback.message.answer(
            "🎪 <b>ИВЕНТЫ</b>\n\n"
            "Сейчас активных ивентов нет.",
            parse_mode="HTML"
        )

        return

    left = event["ends_at"] - int(time.time())

    await callback.message.answer(
        "🎪 <b>АКТИВНЫЙ ИВЕНТ</b>\n\n"
        f"🔥 {html.escape(event['name'])}\n"
        f"⏳ Осталось: <b>{left // 60} мин.</b>\n\n"
        "⚽ Ивент влияет на дропы.",
        parse_mode="HTML"
    )


# =========================================================
# ADMIN
# =========================================================

@DP.message(Command("ban"))
async def ban_command(message: Message):

    if not is_owner(message.from_user):
        return

    parts = message.text.split()

    if len(parts) < 2:
        await message.answer(
            "Используй: /ban USER_ID"
        )
        return

    try:
        user_id = int(parts[1])
    except ValueError:
        await message.answer("❌ ID должен быть числом.")
        return

    async with aiosqlite.connect(DB) as db:

        await db.execute(
            "UPDATE users SET banned=1 WHERE user_id=?",
            (user_id,)
        )

        await db.commit()

    await message.answer(
        f"🚫 Пользователь <code>{user_id}</code> заблокирован.",
        parse_mode="HTML"
    )


@DP.message(Command("unban"))
async def unban_command(message: Message):

    if not is_owner(message.from_user):
        return

    parts = message.text.split()

    if len(parts) < 2:
        return

    try:
        user_id = int(parts[1])
    except ValueError:
        return

    async with aiosqlite.connect(DB) as db:

        await db.execute(
            "UPDATE users SET banned=0 WHERE user_id=?",
            (user_id,)
        )

        await db.commit()

    await message.answer(
        f"✅ Пользователь <code>{user_id}</code> разблокирован.",
        parse_mode="HTML"
    )


@DP.message(Command("give"))
async def give_command(message: Message):

    if not is_owner(message.from_user):
        return

    parts = message.text.split()

    if len(parts) < 3:
        await message.answer(
            "Используй:\n"
            "/give USER_ID AMOUNT"
        )
        return

    try:
        user_id = int(parts[1])
        amount = int(parts[2])
    except ValueError:
        await message.answer(
            "❌ Неверные значения."
        )
        return

    await add_coins(
        user_id,
        amount
    )

    await message.answer(
        f"✅ Выдано <b>{amount:,} 🪙</b>",
        parse_mode="HTML"
    )


@DP.message(Command("makepromo"))
async def makepromo_command(message: Message):

    if not is_owner(message.from_user):
        return

    parts = message.text.split()

    if len(parts) < 5:
        await message.answer(
            "Используй:\n"
            "/makepromo CODE COINS STARS ACTIVATIONS"
        )
        return

    code = parts[1].upper()

    try:
        coins = int(parts[2])
        stars = int(parts[3])
        activations = int(parts[4])
    except ValueError:
        await message.answer(
            "❌ Неверные значения."
        )
        return

    async with aiosqlite.connect(DB) as db:

        await db.execute("""
            INSERT OR REPLACE INTO promo_codes
            (code,coins,stars,activations,used,created)
            VALUES(?,?,?,?,0,?)
        """, (
            code,
            coins,
            stars,
            activations,
            int(time.time())
        ))

        await db.commit()

    await message.answer(
        "🎟️ <b>ПРОМОКОД СОЗДАН</b>\n\n"
        f"Код: <code>{html.escape(code)}</code>\n"
        f"🪙 {coins:,}\n"
        f"⭐ {stars}\n"
        f"👥 Активаций: {activations}",
        parse_mode="HTML"
    )


# =========================================================
# BACK
# =========================================================

@DP.callback_query(F.data == "back_main")
async def back_main_callback(callback: CallbackQuery):

    await callback.answer()

    await callback.message.answer(
        "⚽ <b>FOOTBALL DROP</b>\n\n"
        "Выбери действие:",
        reply_markup=main_keyboard(),
        parse_mode="HTML"
    )


# =========================================================
# RUN
# =========================================================

async def main():

    await init_db()

    await DP.start_polling(
        BOT
    )


if __name__ == "__main__":
    asyncio.run(main())
