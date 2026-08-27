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
from keep_alive import keep_alive

keep_alive()

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
if not TOKEN:
    raise RuntimeError("TELEGRAM_BOT_TOKEN is not set")

BOT = Bot(token=TOKEN)
DP = Dispatcher()

DB = "football_drop.db"
OWNER = "foqlu"

REQUIRED_CHANNEL = os.getenv("REQUIRED_CHANNEL", "")
CHANNEL_LINK = "https://t.me/+MHTPcaFy2j5lOWMy"

DROP_COOLDOWN = 60 * 60
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

# name, nation, position, rating, rarity, price
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

    # Объединённые игроки из EXTRA_PLAYERS
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
    ("Мурад Мустапха","🇩🇿","ST",78,"Common",5000),
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
    ("Сардар Дурсун","🇹🇷","ST",77,"Common",5000),
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
    ("Идрисса Гейе","🇸🇳","CDM",78,"Common",5000),
    ("Исмаила Сарр","🇸🇳","RW",80,"Rare",9000),
    ("Майрон Боаду","🇳🇱","ST",78,"Common",5000),
    ("Арно Данджума","🇳🇱","LW",79,"Common",6000),
    ("Стивен Бергвейн","🇳🇱","LW",80,"Rare",9000),
    ("Ваут Вегхорст","🇳🇱","ST",79,"Common",6000),
    ("Ноа Ланг","🇳🇱","LW",81,"Rare",10000),
    ("Ибрагим Сангари","🇨🇮","CDM",79,"Common",6000),
    ("Секу Койта","🇲🇱","ST",78,"Common",5000),
    ("Мохамед Эль-Шеннави","🇪🇬","GK",78,"Common",5000),
    ("Махмуд Хассан","🇪🇬","LW",77,"Common",5000),
    ("Трезеге","🇪🇬","LW",80,"Rare",9000),
    ("Омар Мармуш","🇪🇬","ST",84,"Rare",18000),
    ("Мостафа Мохамед","🇪🇬","ST",78,"Common",5000),
    ("Андре Онана","🇨🇲","GK",82,"Rare",12000),
    ("Брайан Мбемо","🇨🇲","RW",84,"Rare",18000),
    ("Карл Токо Экамби","🇨🇲","LW",78,"Common",5000),
    ("Йереми Пино","🇪🇸","RW",80,"Rare",9000),
    ("Микель Весга","🇪🇸","CM",78,"Common",5000),
    ("Серхио Регилон","🇪🇸","LB",77,"Common",5000),
    ("Тьяско Сеговия","🇻🇪","CM",76,"Common",4500),
    ("Тадео Альенде","🇦🇷","RW",76,"Common",4500),
    ("Луис Суарес","🇺🇾","ST",83,"Rare",16000),
]

STAR_PACKS = {
    "basic": (10, 1, "🥉 Basic Pack"),
    "pro": (25, 3, "🥈 Pro Pack"),
    "elite": (50, 6, "🥇 Elite Pack"),
    "legend": (100, 12, "💎 Legendary Pack"),
    "icon": (250, 20, "🔥 Icon Pack"),
    "ultimate": (500, 35, "🌈 Ultimate Pack"),
}

STAR_PLAYERS = [
    ("Мбаппе Premium","🇫🇷","ST",94,"Premium",125),
    ("Винисиус Premium","🇧🇷","LW",94,"Premium",125),
    ("Месси Premium","🇦🇷","RW",96,"Premium",250),
    ("Роналду Premium","🇵🇹","ST",96,"Premium",250),
    ("Роналдиньо Premium","🇧🇷","LW",97,"Premium",300),
]

COIN_PACKS = {
    "c1": (15000, 1, "📦 Bronze Coin Pack"),
    "c2": (40000, 3, "📦 Silver Coin Pack"),
    "c3": (90000, 7, "📦 Gold Coin Pack"),
    "c4": (200000, 18, "💎 Diamond Coin Pack"),
}


async def init_db():
    async with aiosqlite.connect(DB) as db:
        await db.execute("""CREATE TABLE IF NOT EXISTS users(
            user_id INTEGER PRIMARY KEY,
            username TEXT DEFAULT '',
            first_name TEXT DEFAULT '',
            coins INTEGER DEFAULT 0,
            last_drop INTEGER DEFAULT 0,
            daily_date TEXT DEFAULT '',
            daily_streak INTEGER DEFAULT 0,
            wins INTEGER DEFAULT 0,
            losses INTEGER DEFAULT 0,
            lucky_until INTEGER DEFAULT 0,
            banned INTEGER DEFAULT 0)""")

        await db.execute("""CREATE TABLE IF NOT EXISTS cards(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            name TEXT NOT NULL,
            nation TEXT NOT NULL,
            position TEXT NOT NULL,
            rating INTEGER NOT NULL,
            rarity TEXT NOT NULL,
            price INTEGER NOT NULL)""")

        await db.execute("""CREATE TABLE IF NOT EXISTS market(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            seller_id INTEGER NOT NULL,
            card_id INTEGER NOT NULL,
            price INTEGER NOT NULL)""")

        await db.execute("""CREATE TABLE IF NOT EXISTS payments(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            product TEXT NOT NULL,
            stars INTEGER NOT NULL,
            created INTEGER NOT NULL)""")

        await db.execute("""CREATE TABLE IF NOT EXISTS missions(
            user_id INTEGER PRIMARY KEY,
            drops INTEGER DEFAULT 0,
            cards INTEGER DEFAULT 0,
            claimed INTEGER DEFAULT 0)""")

        await db.execute("""CREATE TABLE IF NOT EXISTS promo_codes(
            code TEXT PRIMARY KEY,
            coins INTEGER DEFAULT 0,
            stars INTEGER DEFAULT 0,
            activations INTEGER NOT NULL,
            used INTEGER DEFAULT 0,
            created INTEGER NOT NULL)""")

        await db.execute("""CREATE TABLE IF NOT EXISTS promo_uses(
            code TEXT NOT NULL,
            user_id INTEGER NOT NULL,
            PRIMARY KEY(code,user_id))""")

        await db.commit()


async def register(user):
    async with aiosqlite.connect(DB) as db:
        await db.execute(
            "INSERT OR IGNORE INTO users(user_id,username,first_name) VALUES(?,?,?)",
            (user.id, user.username or "", user.first_name or "")
        )

        await db.execute(
            "UPDATE users SET username=?,first_name=? WHERE user_id=?",
            (user.username or "", user.first_name or "", user.id)
        )

        await db.execute(
            "INSERT OR IGNORE INTO missions(user_id) VALUES(?)",
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

        if not row or row[1] or row[0] < amount:
            return False

        await db.execute(
            "UPDATE users SET coins=coins-? WHERE user_id=?",
            (amount, user_id)
        )
        await db.commit()
        return True


async def add_card(user_id, player):
    async with aiosqlite.connect(DB) as db:
        await db.execute(
            """INSERT INTO cards
            (user_id,name,nation,position,rating,rarity,price)
            VALUES(?,?,?,?,?,?,?)""",
            (user_id, *player)
        )
        await db.commit()


async def mission_update(user_id, field):
    if field not in ("drops", "cards"):
        return

    async with aiosqlite.connect(DB) as db:
        await db.execute(
            f"UPDATE missions SET {field}={field}+1 WHERE user_id=?",
            (user_id,)
        )
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
    if is_owner(message.from_user) or await check_access(message.from_user.id):
        return True

    await message.answer(
        "🔒 <b>СНАЧАЛА ПОДПИШИСЬ НА КАНАЛ</b>\n\n"
        "После подписки нажми «Проверить подписку».",
        reply_markup=subscribe_keyboard(),
        parse_mode="HTML"
    )
    return False


def choose_rarity(user=None):
    names = list(RARITIES)
    weights = list(RARITIES.values())

    if user and user["lucky_until"] > int(time.time()):
        weights = [
            weights[i] * (1 if names[i] == "Common" else LUCKY_MULTIPLIER)
            for i in range(len(names))
        ]

    return random.choices(names, weights=weights, k=1)[0]


def random_player(user=None, forced_rarity=None):
    rarity = forced_rarity or choose_rarity(user)

    pool = [p for p in PLAYERS if p[4] == rarity]

    if not pool:
        pool = [p for p in PLAYERS if p[4] == "Common"]

    return random.choice(pool)


def main_keyboard():
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

    for text, data in buttons:
        kb.button(text=text, callback_data=data)

    kb.adjust(2)
    return kb.as_markup()


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
        f"Привет, <b>{html.escape(message.from_user.first_name)}</b>!\n"
        f"🪙 Монеты: <b>{user['coins']:,}</b>\n"
        f"🃏 Карт: <b>{await count_cards(message.from_user.id)}</b>\n\n"
        "🃏 /drop — дроп\n"
        "📦 /coinpacks — паки за монеты\n"
        "⭐ /packs — паки за Stars\n"
        "🍀 /lucky — Lucky Charm\n"
        "🎟️ /promo CODE — промокод\n"
        "🏪 /market — рынок\n"
        "🎁 /daily — ежедневная награда\n"
        "🎯 /missions — задания\n"
        "🏆 /top — рейтинг",
        reply_markup=main_keyboard(),
        parse_mode="HTML"
    )


async def do_drop(message):
    await register(message.from_user)

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
            await message.answer(
                f"⏳ Следующий DROP через "
                f"<b>{remaining // 60} мин. {remaining % 60} сек.</b>",
                parse_mode="HTML"
            )
            return

    async with aiosqlite.connect(DB) as db:
        await db.execute(
            "UPDATE users SET last_drop=? WHERE user_id=?",
            (now, message.from_user.id)
        )
        await db.commit()

    coins = random.randint(100, 400)

    await add_coins(message.from_user.id, coins)
    await mission_update(message.from_user.id, "drops")

    await message.answer(
        "📦 <b>ПАК ОТКРЫВАЕТСЯ...</b>",
        parse_mode="HTML"
    )

    await asyncio.sleep(0.7)

    player = random_player(user)

    await add_card(message.from_user.id, player)
    await mission_update(message.from_user.id, "cards")

    name, nation, pos, rating, rarity, price = player

    await message.answer(
        f"{RARITY_EMOJI[rarity]} <b>{rarity.upper()}</b>\n\n"
        f"{nation} <b>{html.escape(name)}</b>\n"
        f"⚡ Позиция: <b>{pos}</b>\n"
        f"⭐ Рейтинг: <b>{rating}</b>\n"
        f"💰 Цена: <b>{price:,} 🪙</b>\n"
        f"🪙 Бонус: +{coins}\n"
        "📚 Карта добавлена!",
        parse_mode="HTML"
    )


@DP.message(Command("drop"))
async def drop(message):
    await do_drop(message)


@DP.message(Command("profile"))
async def profile(message):
    await register(message.from_user)

    if not await require_subscription(message):
        return

    u = await get_user(message.from_user.id)

    lucky = (
        "активен"
        if u["lucky_until"] > int(time.time())
        else "нет"
    )

    await message.answer(
        f"👤 <b>ПРОФИЛЬ</b>\n\n"
        f"👤 {html.escape(message.from_user.first_name)}\n"
        f"🪙 Монеты: <b>{u['coins']:,}</b>\n"
        f"🃏 Карт: <b>{await count_cards(message.from_user.id)}</b>\n"
        f"🏆 Побед: <b>{u['wins']}</b>\n"
        f"💀 Поражений: <b>{u['losses']}</b>\n"
        f"🍀 Lucky Charm: <b>{lucky}</b>",
        parse_mode="HTML"
    )


@DP.message(Command("collection"))
async def collection(message):
    await register(message.from_user)

    if not await require_subscription(message):
        return

    async with aiosqlite.connect(DB) as db:
        cur = await db.execute(
            """SELECT id,name,nation,position,rating,rarity
            FROM cards
            WHERE user_id=?
            ORDER BY rating DESC
            LIMIT 100""",
            (message.from_user.id,)
        )

        cards = await cur.fetchall()

    if not cards:
        await message.answer(
            "📚 Коллекция пустая. Используй /drop."
        )
        return

    text = "📚 <b>КОЛЛЕКЦИЯ</b>\n\n"

    for c in cards:
        text += (
            f"ID <code>{c[0]}</code> | "
            f"{RARITY_EMOJI[c[5]]} {c[2]} "
            f"<b>{html.escape(c[1])}</b> — {c[4]} OVR\n"
        )

    await message.answer(text, parse_mode="HTML")


@DP.message(Command("mycards"))
async def mycards(message):
    await collection(message)


@DP.message(Command("coinpacks"))
async def coinpacks(message):
    await register(message.from_user)

    if not await require_subscription(message):
        return

    kb = InlineKeyboardBuilder()

    for k, (price, amount, name) in COIN_PACKS.items():
        kb.button(
            text=f"{name} — {price:,} 🪙",
            callback_data=f"coinpack:{k}"
        )

    kb.adjust(1)

    await message.answer(
        "📦 <b>ПАКИ ЗА МОНЕТЫ</b>\n\n"
        "Паки открываются сразу после покупки.",
        reply_markup=kb.as_markup(),
        parse_mode="HTML"
    )


@DP.callback_query(F.data.startswith("coinpack:"))
async def coinpack_callback(c):
    await register(c.from_user)

    if not await check_access(c.from_user.id) and not is_owner(c.from_user):
        await c.message.answer(
            "🔒 Подпишись на канал.",
            reply_markup=subscribe_keyboard()
        )
        await c.answer()
        return

    k = c.data.split(":")[1]

    if k not in COIN_PACKS:
        await c.answer("Ошибка", show_alert=True)
        return

    price, amount, name = COIN_PACKS[k]

    if not is_owner(c.from_user):
        if not await spend_coins(c.from_user.id, price):
            await c.answer(
                "❌ Недостаточно монет.",
                show_alert=True
            )
            return

    u = await get_user(c.from_user.id)
    pulled = []

    for _ in range(amount):
        p = random_player(u)
        await add_card(c.from_user.id, p)
        await mission_update(c.from_user.id, "cards")
        pulled.append(p)

    await c.answer("📦 Пак открыт!")

    rare = max(pulled, key=lambda x: x[3])

    await c.message.answer(
        f"📦 <b>{name}</b>\n"
        f"🃏 Карт: <b>{amount}</b>\n\n"
        f"🔥 Лучшая карта: "
        f"{RARITY_EMOJI[rare[4]]} "
        f"{rare[1]} <b>{rare[0]}</b> — "
        f"{rare[3]} OVR",
        parse_mode="HTML"
    )


@DP.message(Command("lucky"))
async def lucky(message):
    await register(message.from_user)

    if not await require_subscription(message):
        return

    u = await get_user(message.from_user.id)
    now = int(time.time())

    if u["lucky_until"] > now:
        left = u["lucky_until"] - now

        await message.answer(
            f"🍀 Lucky Charm уже активен ещё примерно "
            f"<b>{left // 3600}ч {(left % 3600) // 60}м</b>.",
            parse_mode="HTML"
        )
        return

    await BOT.send_invoice(
        chat_id=message.from_user.id,
        title="🍀 Lucky Charm",
        description="24 часа и x3 к шансам редких карт.",
        payload=f"lucky:{message.from_user.id}",
        currency="XTR",
        prices=[
            LabeledPrice(
                label="Lucky Charm",
                amount=LUCKY_COST
            )
        ]
    )


@DP.message(Command("promo"))
async def promo(message):
    await register(message.from_user)

    if not await require_subscription(message):
        return

    args = message.text.split()

    if len(args) != 2:
        await message.answer(
            "Используй: <code>/promo КОД</code>",
            parse_mode="HTML"
        )
        return

    code = args[1].upper()

    async with aiosqlite.connect(DB) as db:
        cur = await db.execute(
            "SELECT coins,stars,activations,used "
            "FROM promo_codes WHERE code=?",
            (code,)
        )

        p = await cur.fetchone()

        if not p:
            await message.answer("❌ Промокод не найден.")
            return

        if p[3] >= p[2]:
            await message.answer(
                "❌ Лимит активаций исчерпан."
            )
            return

        cur = await db.execute(
            "SELECT 1 FROM promo_uses "
            "WHERE code=? AND user_id=?",
            (code, message.from_user.id)
        )

        if await cur.fetchone():
            await message.answer(
                "❌ Ты уже использовал этот промокод."
            )
            return

        await db.execute(
            "INSERT INTO promo_uses(code,user_id) VALUES(?,?)",
            (code, message.from_user.id)
        )

        await db.execute(
            "UPDATE promo_codes SET used=used+1 WHERE code=?",
            (code,)
        )

        await db.execute(
            "UPDATE users SET coins=coins+? WHERE user_id=?",
            (p[0], message.from_user.id)
        )

        await db.commit()

    await message.answer(
        f"🎟️ Промокод активирован! 🪙 +{p[0]:,}"
        + (
            f"\n⭐ Бонус: {p[1]} Stars"
            if p[1]
            else ""
        )
    )


@DP.message(Command("shop"))
async def shop(message):
    await register(message.from_user)

    if not await require_subscription(message):
        return

    kb = InlineKeyboardBuilder()

    for i, p in enumerate(PLAYERS):
        if p[3] >= 80:
            kb.button(
                text=f"{p[1]} {p[0]} — {p[5]:,} 🪙",
                callback_data=f"buy:{i}"
            )

    kb.adjust(1)

    await message.answer(
        "🛒 <b>МАГАЗИН</b>\n\n"
        "Покупка игроков за монеты.",
        reply_markup=kb.as_markup(),
        parse_mode="HTML"
    )


@DP.callback_query(F.data.startswith("buy:"))
async def buy(c):
    await register(c.from_user)

    if not await check_access(c.from_user.id) and not is_owner(c.from_user):
        await c.message.answer(
            "🔒 Подпишись на канал.",
            reply_markup=subscribe_keyboard()
        )
        await c.answer()
        return

    i = int(c.data.split(":")[1])

    if i < 0 or i >= len(PLAYERS):
        await c.answer("Ошибка.", show_alert=True)
        return

    p = PLAYERS[i]

    if not is_owner(c.from_user):
        if not await spend_coins(c.from_user.id, p[5]):
            await c.answer(
                "❌ Недостаточно монет.",
                show_alert=True
            )
            return

    await add_card(c.from_user.id, p)

    await c.answer("✅ Игрок куплен!")

    await c.message.answer(
        f"✅ {p[1]} <b>{html.escape(p[0])}</b> — {p[3]} OVR",
        parse_mode="HTML"
    )


@DP.message(Command("sellbot"))
async def sellbot(message):
    await register(message.from_user)

    if not await require_subscription(message):
        return

    a = message.text.split()

    if len(a) != 2:
        await message.answer("Используй: /sellbot ID")
        return

    try:
        cid = int(a[1])
    except:
        await message.answer("❌ Неверный ID.")
        return

    async with aiosqlite.connect(DB) as db:
        cur = await db.execute(
            """SELECT id,name,rating,rarity,price
            FROM cards
            WHERE id=? AND user_id=?""",
            (cid, message.from_user.id)
        )

        card = await cur.fetchone()

        if not card:
            await message.answer("❌ Карта не найдена.")
            return

        cur = await db.execute(
            "SELECT id FROM market WHERE card_id=?",
            (cid,)
        )

        if await cur.fetchone():
            await message.answer(
                "❌ Карта уже на рынке."
            )
            return

        val = max(100, card[4] // 2)

        await db.execute(
            "DELETE FROM cards WHERE id=?",
            (cid,)
        )

        await db.execute(
            "UPDATE users SET coins=coins+? WHERE user_id=?",
            (val, message.from_user.id)
        )

        await db.commit()

    await message.answer(
        f"🤖 Бот выкупил {html.escape(card[1])}. "
        f"🪙 +{val:,}",
        parse_mode="HTML"
    )


@DP.message(Command("sell"))
async def sell(message):
    await register(message.from_user)

    if not await require_subscription(message):
        return

    a = message.text.split()

    if len(a) != 3:
        await message.answer(
            "Формат: /sell ID цена"
        )
        return

    try:
        cid = int(a[1])
        price = int(a[2])
    except:
        await message.answer(
            "❌ ID и цена — числа."
        )
        return

    if price <= 0:
        await message.answer(
            "❌ Цена должна быть больше 0."
        )
        return

    async with aiosqlite.connect(DB) as db:
        cur = await db.execute(
            """SELECT id,name,rating,rarity
            FROM cards
            WHERE id=? AND user_id=?""",
            (cid, message.from_user.id)
        )

        card = await cur.fetchone()

        if not card:
            await message.answer(
                "❌ Карта не найдена."
            )
            return

        cur = await db.execute(
            "SELECT id FROM market WHERE card_id=?",
            (cid,)
        )

        if await cur.fetchone():
            await message.answer(
                "❌ Уже на рынке."
            )
            return

        await db.execute(
            "INSERT INTO market(seller_id,card_id,price) "
            "VALUES(?,?,?)",
            (message.from_user.id, cid, price)
        )

        await db.commit()

    await message.answer(
        f"🏪 Карта <b>{html.escape(card[1])}</b> "
        f"выставлена за {price:,} 🪙.",
        parse_mode="HTML"
    )


@DP.message(Command("market"))
async def market(message):
    await register(message.from_user)

    if not await require_subscription(message):
        return

    async with aiosqlite.connect(DB) as db:
        db.row_factory = aiosqlite.Row

        cur = await db.execute(
            """SELECT market.id,market.seller_id,market.card_id,
            market.price,cards.name,cards.nation,cards.rating,
            cards.rarity,users.username
            FROM market
            JOIN cards ON cards.id=market.card_id
            JOIN users ON users.user_id=market.seller_id
            ORDER BY market.id DESC
            LIMIT 30"""
        )

        rows = await cur.fetchall()

    if not rows:
        await message.answer(
            "🏪 Рынок пуст. /sell ID цена"
        )
        return

    kb = InlineKeyboardBuilder()
    text = "🏪 <b>РЫНОК</b>\n\n"

    for x in rows:
        text += (
            f"{RARITY_EMOJI[x['rarity']]} "
            f"{x['nation']} "
            f"<b>{html.escape(x['name'])}</b> — "
            f"⭐{x['rating']} — "
            f"🪙{x['price']:,}\n"
            f"👤 @{html.escape(x['username'] or 'player')}\n\n"
        )

        kb.button(
            text=f"🛒 Купить {x['name']}",
            callback_data=f"marketbuy:{x['id']}"
        )

    kb.adjust(1)

    await message.answer(
        text,
        reply_markup=kb.as_markup(),
        parse_mode="HTML"
    )


@DP.callback_query(F.data.startswith("marketbuy:"))
async def marketbuy(c):
    await register(c.from_user)

    if not await check_access(c.from_user.id) and not is_owner(c.from_user):
        await c.message.answer(
            "🔒 Подпишись на канал.",
            reply_markup=subscribe_keyboard()
        )
        await c.answer()
        return

    lid = int(c.data.split(":")[1])

    async with aiosqlite.connect(DB) as db:
        db.row_factory = aiosqlite.Row

        cur = await db.execute(
            """SELECT market.id,market.seller_id,market.card_id,
            market.price,cards.name,cards.nation,cards.rating,
            cards.rarity
            FROM market
            JOIN cards ON cards.id=market.card_id
            WHERE market.id=?""",
            (lid,)
        )

        item = await cur.fetchone()

        if not item:
            await c.answer(
                "❌ Лот уже продан.",
                show_alert=True
            )
            return

        if item["seller_id"] == c.from_user.id:
            await c.answer(
                "❌ Это твоя карта.",
                show_alert=True
            )
            return

        if not await spend_coins(
            c.from_user.id,
            item["price"]
        ):
            await c.answer(
                "❌ Недостаточно монет.",
                show_alert=True
            )
            return

        await db.execute(
            "UPDATE cards SET user_id=? WHERE id=?",
            (c.from_user.id, item["card_id"])
        )

        await db.execute(
            "UPDATE users SET coins=coins+? WHERE user_id=?",
            (item["price"], item["seller_id"])
        )

        await db.execute(
            "DELETE FROM market WHERE id=?",
            (lid,)
        )

        await db.commit()

    await c.answer("✅ Куплено!")

    await c.message.answer(
        f"✅ {item['nation']} "
        f"<b>{html.escape(item['name'])}</b> — "
        f"⭐{item['rating']} — "
        f"🪙{item['price']:,}",
        parse_mode="HTML"
    )


@DP.message(Command("daily"))
async def daily(message):
    await register(message.from_user)

    if not await require_subscription(message):
        return

    today = datetime.now(
        timezone.utc
    ).strftime("%Y-%m-%d")

    async with aiosqlite.connect(DB) as db:
        cur = await db.execute(
            "SELECT daily_date,daily_streak "
            "FROM users WHERE user_id=?",
            (message.from_user.id,)
        )

        u = await cur.fetchone()

        if u[0] == today:
            await message.answer(
                "🎁 Daily уже забран сегодня."
            )
            return

        streak = u[1] + 1
        reward = min(400 + streak * 100, 2000)

        await db.execute(
            """UPDATE users
            SET daily_date=?,daily_streak=?,coins=coins+?
            WHERE user_id=?""",
            (
                today,
                streak,
                reward,
                message.from_user.id
            )
        )

        await db.commit()

    await message.answer(
        f"🎁 <b>DAILY</b>\n"
        f"🔥 Серия: {streak}\n"
        f"🪙 +{reward:,}",
        parse_mode="HTML"
    )


@DP.message(Command("missions"))
async def missions(message):
    await register(message.from_user)

    if not await require_subscription(message):
        return

    async with aiosqlite.connect(DB) as db:
        cur = await db.execute(
            "SELECT drops,cards,claimed "
            "FROM missions WHERE user_id=?",
            (message.from_user.id,)
        )

        m = await cur.fetchone()

    await message.answer(
        f"🎯 <b>ЗАДАНИЯ</b>\n\n"
        f"🃏 DROP: {m[0]}/3\n"
        f"📚 Карты: {m[1]}/5\n\n"
        f"🎁 Награда: <b>3000 🪙</b>\n"
        f"Статус: "
        f"{'✅ Выполнено' if m[0] >= 3 and m[1] >= 5 else '⏳ В процессе'}",
        parse_mode="HTML"
    )


@DP.message(Command("claim"))
async def claim(message):
    await register(message.from_user)

    if not await require_subscription(message):
        return

    async with aiosqlite.connect(DB) as db:
        cur = await db.execute(
            "SELECT drops,cards,claimed "
            "FROM missions WHERE user_id=?",
            (message.from_user.id,)
        )

        m = await cur.fetchone()

        if m[2]:
            await message.answer(
                "❌ Награда уже получена."
            )
            return

        if m[0] < 3 or m[1] < 5:
            await message.answer(
                "❌ Задания ещё не выполнены."
            )
            return

        await db.execute(
            "UPDATE missions SET claimed=1 WHERE user_id=?",
            (message.from_user.id,)
        )

        await db.execute(
            "UPDATE users SET coins=coins+3000 WHERE user_id=?",
            (message.from_user.id,)
        )

        await db.commit()

    await message.answer(
        "🎉 ЗАДАНИЯ ВЫПОЛНЕНЫ! 🪙 +3000"
    )


@DP.message(Command("top"))
@DP.message(Command("leaderboard"))
async def top(message):
    await register(message.from_user)

    if not await require_subscription(message):
        return

    async with aiosqlite.connect(DB) as db:
        cur = await db.execute(
            """SELECT username,wins,coins
            FROM users
            WHERE banned=0
            ORDER BY wins DESC,coins DESC
            LIMIT 10"""
        )

        rows = await cur.fetchall()

    text = "🏆 <b>ТОП ИГРОКОВ</b>\n\n"

    for i, r in enumerate(rows, 1):
        text += (
            f"{i}. @{html.escape(r[0] or 'player')} — "
            f"🏆{r[1]} | 🪙{r[2]:,}\n"
        )

    await message.answer(
        text,
        parse_mode="HTML"
    )


@DP.message(Command("packs"))
async def packs(message):
    await register(message.from_user)

    if not await require_subscription(message):
        return

    kb = InlineKeyboardBuilder()

    for k, (stars, amount, name) in STAR_PACKS.items():
        kb.button(
            text=f"{name} — {stars} ⭐",
            callback_data=f"pack:{k}"
        )

    kb.adjust(1)

    await message.answer(
        "⭐ <b>ПАКИ ЗА STARS</b>",
        reply_markup=kb.as_markup(),
        parse_mode="HTML"
    )


@DP.callback_query(F.data.startswith("pack:"))
async def pack_callback(c):
    k = c.data.split(":")[1]

    if k not in STAR_PACKS:
        await c.answer(
            "Ошибка",
            show_alert=True
        )
        return

    stars, amount, name = STAR_PACKS[k]

    await BOT.send_invoice(
        chat_id=c.from_user.id,
        title=name,
        description=f"Футбольный пак. Карт: {amount}",
        payload=f"pack:{k}:{c.from_user.id}",
        currency="XTR",
        prices=[
            LabeledPrice(
                label=name,
                amount=stars
            )
        ]
    )

    await c.answer()


@DP.message(Command("starplayers"))
async def starplayers(message):
    await register(message.from_user)

    if not await require_subscription(message):
        return

    kb = InlineKeyboardBuilder()

    for i, p in enumerate(STAR_PLAYERS):
        kb.button(
            text=f"{p[1]} {p[0]} — {p[5]} ⭐",
            callback_data=f"starplayer:{i}"
        )

    kb.adjust(1)

    await message.answer(
        "⭐ <b>ЭКСКЛЮЗИВНЫЕ КАРТЫ</b>",
        reply_markup=kb.as_markup(),
        parse_mode="HTML"
    )


@DP.callback_query(F.data.startswith("starplayer:"))
async def starplayer_callback(c):
    i = int(c.data.split(":")[1])
    p = STAR_PLAYERS[i]

    await BOT.send_invoice(
        chat_id=c.from_user.id,
        title=p[0],
        description=f"Эксклюзивная карта {p[0]}",
        payload=f"starplayer:{i}:{c.from_user.id}",
        currency="XTR",
        prices=[
            LabeledPrice(
                label=p[0],
                amount=p[5]
            )
        ]
    )

    await c.answer()


@DP.pre_checkout_query()
async def pre_checkout(q: PreCheckoutQuery):
    await q.answer(ok=True)


@DP.message(F.successful_payment)
async def successful_payment(message):
    payment = message.successful_payment
    payload = payment.invoice_payload

    if payload.startswith("lucky:"):
        async with aiosqlite.connect(DB) as db:
            await db.execute(
                "UPDATE users SET lucky_until=? WHERE user_id=?",
                (
                    int(time.time()) + LUCKY_HOURS * 3600,
                    message.from_user.id
                )
            )

            await db.execute(
                """INSERT INTO payments
                (user_id,product,stars,created)
                VALUES(?,?,?,?)""",
                (
                    message.from_user.id,
                    "lucky",
                    LUCKY_COST,
                    int(time.time())
                )
            )

            await db.commit()

        await message.answer(
            "🍀 <b>LUCKY CHARM АКТИВИРОВАН!</b>\n"
            "24 часа • x3 к шансам редких карт.",
            parse_mode="HTML"
        )

    elif payload.startswith("pack:"):
        key = payload.split(":")[1]

        if key not in STAR_PACKS:
            return

        stars, amount, name = STAR_PACKS[key]
        u = await get_user(message.from_user.id)

        for _ in range(amount):
            await add_card(
                message.from_user.id,
                random_player(u)
            )

        async with aiosqlite.connect(DB) as db:
            await db.execute(
                """INSERT INTO payments
                (user_id,product,stars,created)
                VALUES(?,?,?,?)""",
                (
                    message.from_user.id,
                    key,
                    stars,
                    int(time.time())
                )
            )

            await db.commit()

        await message.answer(
            f"✅ {name} куплен! 🃏 {amount} карт.\n"
            "/collection"
        )

    elif payload.startswith("starplayer:"):
        i = int(payload.split(":")[1])

        if i < 0 or i >= len(STAR_PLAYERS):
            return

        p = STAR_PLAYERS[i]

        await add_card(
            message.from_user.id,
            p
        )

        await message.answer(
            f"🔥 <b>ЭКСКЛЮЗИВНАЯ КАРТА!</b>\n"
            f"{p[1]} <b>{p[0]}</b> — ⭐{p[3]}",
            parse_mode="HTML"
        )


async def notify_all(text):
    async with aiosqlite.connect(DB) as db:
        cur = await db.execute(
            "SELECT user_id FROM users WHERE banned=0"
        )

        ids = [
            r[0]
            for r in await cur.fetchall()
        ]

    sent = 0

    for uid in ids:
        try:
            await BOT.send_message(
                uid,
                text,
                parse_mode="HTML"
            )
            sent += 1
        except Exception:
            pass

        await asyncio.sleep(0.03)

    return sent


@DP.message(Command("owner"))
async def owner_panel(message):
    if not is_owner(message.from_user):
        await message.answer("❌ Нет доступа.")
        return

    await message.answer(
        "👑 <b>OWNER</b>\n\n"
        "/give ID количество — выдать монеты\n"
        "/take ID количество — забрать монеты\n"
        "/givecard ID индекс — выдать карту\n"
        "/ban ID — бан\n"
        "/unban ID — разбан\n"
        "/promocreate КОД монеты активации — создать промокод\n"
        "/promolist — список промокодов\n"
        "/superdrop on|off — Super Drop\n"
        "/stats — статистика\n"
        "/players — количество игроков",
        parse_mode="HTML"
    )


@DP.message(Command("give"))
async def give(message):
    if not is_owner(message.from_user):
        return

    a = message.text.split()

    if len(a) != 3:
        await message.answer(
            "Формат: /give ID количество"
        )
        return

    try:
        uid = int(a[1])
        amount = int(a[2])
    except:
        await message.answer("❌ Числа.")
        return

    await add_coins(uid, amount)

    await message.answer(
        f"👑 Выдано 🪙 {amount:,} игроку "
        f"<code>{uid}</code>.",
        parse_mode="HTML"
    )


@DP.message(Command("take"))
async def take(message):
    if not is_owner(message.from_user):
        return

    a = message.text.split()

    if len(a) != 3:
        await message.answer(
            "Формат: /take ID количество"
        )
        return

    try:
        uid = int(a[1])
        amount = int(a[2])
    except:
        await message.answer("❌ Числа.")
        return

    await add_coins(
        uid,
        -abs(amount)
    )

    await message.answer(
        f"👑 Забрано 🪙 {abs(amount):,} "
        f"у <code>{uid}</code>.",
        parse_mode="HTML"
    )


@DP.message(Command("givecard"))
async def givecard(message):
    if not is_owner(message.from_user):
        return

    a = message.text.split()

    if len(a) != 3:
        await message.answer(
            "Формат: /givecard ID индекс"
        )
        return

    try:
        uid = int(a[1])
        i = int(a[2])
    except:
        await message.answer("❌ Числа.")
        return

    if i < 0 or i >= len(PLAYERS):
        await message.answer(
            f"❌ Индекс от 0 до {len(PLAYERS)-1}."
        )
        return

    await add_card(
        uid,
        PLAYERS[i]
    )

    await message.answer(
        f"🎴 Выдана карта: {PLAYERS[i][0]}"
    )


@DP.message(Command("ban"))
async def ban(message):
    if not is_owner(message.from_user):
        return

    a = message.text.split()

    if len(a) != 2:
        await message.answer(
            "Формат: /ban ID"
        )
        return

    uid = int(a[1])

    async with aiosqlite.connect(DB) as db:
        await db.execute(
            "UPDATE users SET banned=1 WHERE user_id=?",
            (uid,)
        )
        await db.commit()

    await message.answer(
        f"🚫 <code>{uid}</code> заблокирован.",
        parse_mode="HTML"
    )


@DP.message(Command("unban"))
async def unban(message):
    if not is_owner(message.from_user):
        return

    a = message.text.split()

    if len(a) != 2:
        await message.answer(
            "Формат: /unban ID"
        )
        return

    uid = int(a[1])

    async with aiosqlite.connect(DB) as db:
        await db.execute(
            "UPDATE users SET banned=0 WHERE user_id=?",
            (uid,)
        )
        await db.commit()

    await message.answer(
        f"✅ <code>{uid}</code> разблокирован.",
        parse_mode="HTML"
    )


@DP.message(Command("promocreate"))
async def promocreate(message):
    if not is_owner(message.from_user):
        return

    a = message.text.split()

    if len(a) != 4:
        await message.answer(
            "Формат: /promocreate КОД монеты активации"
        )
        return

    code = a[1].upper()

    try:
        coins = int(a[2])
        acts = int(a[3])
    except:
        await message.answer(
            "❌ Монеты и активации — числа."
        )
        return

    if acts < 1:
        await message.answer(
            "❌ Активаций должно быть больше 0."
        )
        return

    async with aiosqlite.connect(DB) as db:
        await db.execute(
            """INSERT OR REPLACE INTO promo_codes
            (code,coins,stars,activations,used,created)
            VALUES(?,?,?,?,0,?)""",
            (
                code,
                coins,
                0,
                acts,
                int(time.time())
            )
        )

        await db.commit()

    await message.answer(
        f"🎟️ Промокод <b>{code}</b> создан. "
        f"🪙{coins:,}, активаций: {acts}.",
        parse_mode="HTML"
    )


@DP.message(Command("promolist"))
async def promolist(message):
    if not is_owner(message.from_user):
        return

    async with aiosqlite.connect(DB) as db:
        cur = await db.execute(
            """SELECT code,coins,activations,used
            FROM promo_codes
            ORDER BY created DESC"""
        )

        rows = await cur.fetchall()

    if not rows:
        await message.answer(
            "Промокодов нет."
        )
        return

    text = "🎟️ <b>ПРОМОКОДЫ</b>\n\n"

    for r in rows:
        text += (
            f"<code>{r[0]}</code> — "
            f"🪙{r[1]:,} | {r[3]}/{r[2]}\n"
        )

    await message.answer(
        text,
        parse_mode="HTML"
    )


SUPER_DROP = False


@DP.message(Command("superdrop"))
async def superdrop(message):
    global SUPER_DROP

    if not is_owner(message.from_user):
        return

    a = message.text.split()

    if (
        len(a) != 2
        or a[1].lower() not in ("on", "off")
    ):
        await message.answer(
            "Формат: /superdrop on или /superdrop off"
        )
        return

    SUPER_DROP = a[1].lower() == "on"

    if SUPER_DROP:
        await message.answer(
            "🔥 <b>SUPER DROP ВКЛЮЧЁН!</b>\n"
            "Все получили уведомление.",
            parse_mode="HTML"
        )

        await notify_all(
            "🔥 <b>SUPER DROP!</b>\n"
            "Сейчас действует особый дроп! "
            "Успей открыть карту."
        )

    else:
        await message.answer(
            "❌ SUPER DROP выключен."
        )


@DP.message(Command("stats"))
async def stats(message):
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
            "SELECT COUNT(*) FROM market"
        )
        market_count = (await cur.fetchone())[0]

    await message.answer(
        f"📊 Пользователей: {users}\n"
        f"🃏 Карт: {cards}\n"
        f"🏪 На рынке: {market_count}\n"
        f"👥 Игроков в пуле: {len(PLAYERS)}"
    )


@DP.message(Command("players"))
async def players_count(message):
    if not is_owner(message.from_user):
        return

    await message.answer(
        f"🃏 Сейчас в пуле: "
        f"<b>{len(PLAYERS)}</b> игроков.",
        parse_mode="HTML"
    )


@DP.callback_query(F.data == "check_sub")
async def check_sub(c):
    if await check_access(c.from_user.id) or is_owner(c.from_user):
        await c.answer(
            "✅ Подписка подтверждена!",
            show_alert=True
        )

        await c.message.answer(
            "⚽ Доступ открыт!",
            reply_markup=main_keyboard()
        )
    else:
        await c.answer(
            "❌ Подписка не найдена.",
            show_alert=True
        )


@DP.callback_query(F.data == "drop")
async def bdrop(c):
    await c.answer()
    await do_drop(c.message)


@DP.callback_query(F.data == "profile")
async def bprofile(c):
    await c.answer()
    await profile(c.message)


@DP.callback_query(F.data == "collection")
async def bcollection(c):
    await c.answer()
    await collection(c.message)


@DP.callback_query(F.data == "shop")
async def bshop(c):
    await c.answer()
    await shop(c.message)


@DP.callback_query(F.data == "market")
async def bmarket(c):
    await c.answer()
    await market(c.message)


@DP.callback_query(F.data == "daily")
async def bdaily(c):
    await c.answer()
    await daily(c.message)


@DP.callback_query(F.data == "missions")
async def bmissions(c):
    await c.answer()
    await missions(c.message)


@DP.callback_query(F.data == "top")
async def btop(c):
    await c.answer()
    await top(c.message)


@DP.callback_query(F.data == "coinpacks")
async def bcoinpacks(c):
    await c.answer()
    await coinpacks(c.message)


@DP.callback_query(F.data == "packs")
async def bpacks(c):
    await c.answer()
    await packs(c.message)


@DP.callback_query(F.data == "lucky")
async def blucky(c):
    await c.answer()
    await lucky(c.message)


@DP.callback_query(F.data == "promo")
async def bpromo(c):
    await c.answer(
        "Введи /promo КОД в чате.",
        show_alert=True
    )


async def main():
    await init_db()

    print("================================")
    print("FOOTBALL DROP BOT STARTED")
    print(f"PLAYERS: {len(PLAYERS)}")
    print("TOKEN: Render Environment")
    print("================================")

    await DP.start_polling(BOT)


if __name__ == "__main__":
    asyncio.run(main())
