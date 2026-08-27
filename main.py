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
        "📚 /collection — коллекция\n"
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


async def do_drop(message, user=None):
    target = user or message.from_user

    await register(target)

    if not await check_access(target.id) and not is_owner(target):
        await message.answer(
            "🔒 Подпишись на канал.",
            reply_markup=subscribe_keyboard()
        )
        return

    user_data = await get_user(target.id)

    if user_data["banned"] and not is_owner(target):
        await message.answer("🚫 Вы заблокированы.")
        return

    now = int(time.time())

    if not is_owner(target):
        remaining = DROP_COOLDOWN - (now - user_data["last_drop"])

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
            (now, target.id)
        )
        await db.commit()

    coins = random.randint(100, 400)

    await add_coins(target.id, coins)
    await mission_update(target.id, "drops")

    await message.answer(
        "📦 <b>ПАК ОТКРЫВАЕТСЯ...</b>",
        parse_mode="HTML"
    )

    await asyncio.sleep(0.7)

    user_data = await get_user(target.id)
    player = random_player(user_data)

    await add_card(target.id, player)
    await mission_update(target.id, "cards")

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
async def collection(message, target=None):
    user = target or message.from_user

    await register(user)

    if not await check_access(user.id) and not is_owner(user):
        await message.answer(
            "🔒 Подпишись на канал.",
            reply_markup=subscribe_keyboard()
        )
        return

    async with aiosqlite.connect(DB) as db:
        cur = await db.execute(
            """SELECT id,name,nation,position,rating,rarity
            FROM cards
            WHERE user_id=?
            ORDER BY rating DESC, id DESC
            LIMIT 100""",
            (user.id,)
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
            f"{RARITY_EMOJI.get(c[5], '⚪')} "
            f"{c[2]} <b>{html.escape(c[1])}</b> — "
            f"{c[4]} OVR\n"
        )

    await message.answer(
        text,
        parse_mode="HTML"
    )


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

async def do_drop(message):
    await register(message.from_user)
    if not await require_subscription(message):
        return

    user = await get_user(message.from_user.id)
    if not user:
        return

    now = int(time.time())
    cooldown = 60

    if user["last_drop"] and now - user["last_drop"] < cooldown:
        left = cooldown - (now - user["last_drop"])
        await message.answer(
            f"⏳ Следующий дроп через <b>{left} сек.</b>"
        )
        return

    await update_user(message.from_user.id, last_drop=now)

    player = random_player()

    # Lucky Charm
    charm = await get_lucky_charm(message.from_user.id)

    # Базовый шанс редкости
    rarity = get_rarity(player["rating"])

    # Lucky Charm x3
    if charm and charm["expires_at"] > now:
        if random.random() < 0.35:
            rarity = improve_rarity(rarity)

    player["rarity"] = rarity

    price = get_player_price(player)

    await add_card(
        message.from_user.id,
        player["name"],
        player["nation"],
        player["rating"],
        player["rarity"],
        price
    )

    text = (
        "⚽ <b>FOOTBALL DROP!</b>\n\n"
        f"👤 <b>{html.escape(player['name'])}</b>\n"
        f"🌍 {html.escape(player['nation'])}\n"
        f"⭐ Рейтинг: <b>{player['rating']}</b>\n"
        f"💎 Редкость: <b>{player['rarity']}</b>\n"
        f"💰 Цена: <b>€{price:,}</b>"
    )

    kb = InlineKeyboardBuilder()
    kb.button(text="📚 Коллекция", callback_data="collection")
    kb.button(text="💰 Продать", callback_data=f"sell_{player['id']}")
    kb.button(text="⚽ Ещё дроп", callback_data="drop")
    kb.adjust(2, 1)

    await message.answer(text, reply_markup=kb.as_markup())


def get_rarity(rating):
    roll = random.random()

    if rating >= 90:
        if roll < 0.05:
            return "🔥 Легендарная"
        elif roll < 0.20:
            return "💎 Эпическая"
        elif roll < 0.50:
            return "🟣 Очень редкая"
        return "🔵 Редкая"

    if rating >= 85:
        if roll < 0.03:
            return "🔥 Легендарная"
        elif roll < 0.12:
            return "💎 Эпическая"
        elif roll < 0.35:
            return "🟣 Очень редкая"
        return "🔵 Редкая"

    if rating >= 80:
        if roll < 0.01:
            return "🔥 Легендарная"
        elif roll < 0.06:
            return "💎 Эпическая"
        elif roll < 0.20:
            return "🟣 Очень редкая"
        return "🔵 Редкая"

    if roll < 0.03:
        return "🟣 Очень редкая"
    elif roll < 0.15:
        return "🔵 Редкая"

    return "⚪ Обычная"


def improve_rarity(rarity):
    order = [
        "⚪ Обычная",
        "🔵 Редкая",
        "🟣 Очень редкая",
        "💎 Эпическая",
        "🔥 Легендарная"
    ]

    if rarity not in order:
        return rarity

    index = order.index(rarity)

    if index >= len(order) - 1:
        return rarity

    return order[index + 1]


async def get_lucky_charm(user_id):
    async with aiosqlite.connect(DB_NAME) as db:
        db.row_factory = aiosqlite.Row

        cur = await db.execute(
            """
            SELECT *
            FROM lucky_charms
            WHERE user_id = ?
            LIMIT 1
            """,
            (user_id,)
        )

        row = await cur.fetchone()
        return row


async def add_card(
    user_id,
    name,
    nation,
    rating,
    rarity,
    price
):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute(
            """
            INSERT INTO cards
            (
                user_id,
                player_name,
                nation,
                rating,
                rarity,
                price,
                created_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                user_id,
                name,
                nation,
                rating,
                rarity,
                price,
                int(time.time())
            )
        )

        await db.commit()


def get_player_price(player):
    rating = player["rating"]

    base = rating * 100000

    if rating >= 90:
        multiplier = 5
    elif rating >= 85:
        multiplier = 3
    elif rating >= 80:
        multiplier = 2
    else:
        multiplier = 1

    return int(base * multiplier)


async def show_collection(message):
    await register(message.from_user)

    async with aiosqlite.connect(DB_NAME) as db:
        db.row_factory = aiosqlite.Row

        cur = await db.execute(
            """
            SELECT *
            FROM cards
            WHERE user_id = ?
            ORDER BY rating DESC
            """,
            (message.from_user.id,)
        )

        cards = await cur.fetchall()

    if not cards:
        await message.answer(
            "📚 <b>Твоя коллекция пуста.</b>\n\n"
            "Открой первый дроп ⚽"
        )
        return

    text = "📚 <b>ТВОЯ КОЛЛЕКЦИЯ</b>\n\n"

    for i, card in enumerate(cards, 1):
        text += (
            f"{i}. {card['rarity']} "
            f"<b>{html.escape(card['player_name'])}</b>\n"
            f"   ⭐ {card['rating']} | "
            f"💰 €{card['price']:,}\n\n"
        )

    kb = InlineKeyboardBuilder()
    kb.button(text="⚽ Дроп", callback_data="drop")
    kb.button(text="🏪 Магазин", callback_data="shop")
    kb.adjust(2)

    await message.answer(
        text,
        reply_markup=kb.as_markup()
    )


@dp.callback_query(F.data == "collection")
async def collection_callback(callback: CallbackQuery):
    await callback.answer()

    await show_collection(callback.message)


@dp.callback_query(F.data == "drop")
async def drop_callback(callback: CallbackQuery):
    await callback.answer()

    await do_drop(callback.message)


@dp.callback_query(F.data == "shop")
async def shop_callback(callback: CallbackQuery):
    await callback.answer()

    kb = InlineKeyboardBuilder()

    kb.button(
        text="🍀 Lucky Charm",
        callback_data="buy_charm"
    )

    kb.button(
        text="📦 Паки",
        callback_data="packs"
    )

    kb.button(
        text="💰 Рынок",
        callback_data="market"
    )

    kb.button(
        text="⬅️ Назад",
        callback_data="back_main"
    )

    kb.adjust(1)

    await callback.message.answer(
        "🏪 <b>МАГАЗИН</b>\n\n"
        "🍀 Lucky Charm — увеличивает шанс получить "
        "более редкую карту.\n\n"
        "📦 Паки — специальные наборы игроков.\n\n"
        "💰 Рынок — покупка и продажа карт.",
        reply_markup=kb.as_markup()
    )


@dp.callback_query(F.data == "buy_charm")
async def buy_charm_callback(callback: CallbackQuery):
    await callback.answer()

    user = await get_user(callback.from_user.id)

    if not user:
        return

    price = 500

    if user["stars"] < price:
        await callback.message.answer(
            "❌ Недостаточно ⭐ Stars.\n\n"
            f"Стоимость Lucky Charm: <b>{price} ⭐</b>"
        )
        return

    now = int(time.time())
    expires = now + 24 * 60 * 60

    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute(
            "UPDATE users SET stars = stars - ? WHERE user_id = ?",
            (price, callback.from_user.id)
        )

        await db.execute(
            """
            INSERT INTO lucky_charms
            (user_id, expires_at)
            VALUES (?, ?)
            ON CONFLICT(user_id)
            DO UPDATE SET expires_at = excluded.expires_at
            """,
            (callback.from_user.id, expires)
        )

        await db.commit()

    await callback.message.answer(
        "🍀 <b>LUCKY CHARM АКТИВИРОВАН!</b>\n\n"
        "✨ Длительность: <b>24 часа</b>\n"
        "🔥 Бонус: <b>x3 к шансу редкой карты</b>\n\n"
        "Теперь твои дропы имеют повышенный шанс "
        "на получение редких карт."
    )

@dp.callback_query(F.data == "packs")
async def packs_callback(callback: CallbackQuery):
    await callback.answer()

    kb = InlineKeyboardBuilder()

    kb.button(
        text="📦 Обычный пак — 300 ⭐",
        callback_data="buy_pack"
    )
    kb.button(
        text="⬅️ Назад",
        callback_data="shop"
    )

    kb.adjust(1)

    await callback.message.answer(
        "📦 <b>ПАКИ</b>\n\n"
        "Открой пак и получи случайного игрока!\n\n"
        "💰 Стоимость: <b>300 ⭐</b>",
        reply_markup=kb.as_markup()
    )


@dp.callback_query(F.data == "buy_pack")
async def buy_pack_callback(callback: CallbackQuery):
    await callback.answer()

    user = await get_user(callback.from_user.id)

    if not user:
        return

    price = 300

    if user["stars"] < price:
        await callback.message.answer(
            "❌ Недостаточно ⭐ Stars.\n\n"
            f"Стоимость пака: <b>{price} ⭐</b>"
        )
        return

    player = random_player()

    rarity = get_rarity(player["rating"])

    charm = await get_lucky_charm(callback.from_user.id)
    now = int(time.time())

    if charm and charm["expires_at"] > now:
        if random.random() < 0.35:
            rarity = improve_rarity(rarity)

    player["rarity"] = rarity

    card_price = get_player_price(player)

    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute(
            "UPDATE users SET stars = stars - ? WHERE user_id = ?",
            (price, callback.from_user.id)
        )

        await db.commit()

    await add_card(
        callback.from_user.id,
        player["name"],
        player["nation"],
        player["rating"],
        player["rarity"],
        card_price
    )

    text = (
        "📦 <b>ПАК ОТКРЫТ!</b>\n\n"
        f"👤 <b>{html.escape(player['name'])}</b>\n"
        f"🌍 {html.escape(player['nation'])}\n"
        f"⭐ Рейтинг: <b>{player['rating']}</b>\n"
        f"💎 Редкость: <b>{player['rarity']}</b>\n"
        f"💰 Цена: <b>€{card_price:,}</b>"
    )

    kb = InlineKeyboardBuilder()

    kb.button(
        text="📚 Коллекция",
        callback_data="collection"
    )

    kb.button(
        text="📦 Ещё пак",
        callback_data="packs"
    )

    kb.button(
        text="🏪 Магазин",
        callback_data="shop"
    )

    kb.adjust(2, 1)

    await callback.message.answer(
        text,
        reply_markup=kb.as_markup()
    )


@dp.callback_query(F.data == "market")
async def market_callback(callback: CallbackQuery):
    await callback.answer()

    async with aiosqlite.connect(DB_NAME) as db:
        db.row_factory = aiosqlite.Row

        cur = await db.execute(
            """
            SELECT *
            FROM cards
            WHERE user_id = ?
            ORDER BY rating DESC
            LIMIT 20
            """,
            (callback.from_user.id,)
        )

        cards = await cur.fetchall()

    if not cards:
        await callback.message.answer(
            "💰 <b>РЫНОК</b>\n\n"
            "У тебя пока нет карт для продажи.\n\n"
            "Сначала открой несколько дропов ⚽"
        )
        return

    text = "💰 <b>ТВОИ КАРТЫ НА РЫНКЕ</b>\n\n"

    kb = InlineKeyboardBuilder()

    for card in cards:
        text += (
            f"{card['rarity']} "
            f"<b>{html.escape(card['player_name'])}</b>\n"
            f"⭐ {card['rating']} | "
            f"💰 €{card['price']:,}\n\n"
        )

        kb.button(
            text=f"💰 Продать {card['player_name']}",
            callback_data=f"sell_{card['id']}"
        )

    kb.button(
        text="⬅️ Назад",
        callback_data="shop"
    )

    kb.adjust(1)

    await callback.message.answer(
        text,
        reply_markup=kb.as_markup()
    )


@dp.callback_query(F.data.startswith("sell_"))
async def sell_card_callback(callback: CallbackQuery):
    await callback.answer()

    try:
        card_id = int(callback.data.split("_")[1])
    except (ValueError, IndexError):
        await callback.message.answer("❌ Ошибка карты.")
        return

    async with aiosqlite.connect(DB_NAME) as db:
        db.row_factory = aiosqlite.Row

        cur = await db.execute(
            """
            SELECT *
            FROM cards
            WHERE id = ? AND user_id = ?
            """,
            (
                card_id,
                callback.from_user.id
            )
        )

        card = await cur.fetchone()

        if not card:
            await callback.message.answer(
                "❌ Эта карта не найдена в твоей коллекции."
            )
            return

        sell_price = card["price"]

        await db.execute(
            """
            DELETE FROM cards
            WHERE id = ? AND user_id = ?
            """,
            (
                card_id,
                callback.from_user.id
            )
        )

        await db.execute(
            """
            UPDATE users
            SET balance = balance + ?
            WHERE user_id = ?
            """,
            (
                sell_price,
                callback.from_user.id
            )
        )

        await db.commit()

    await callback.message.answer(
        "💰 <b>КАРТА ПРОДАНА!</b>\n\n"
        f"👤 {html.escape(card['player_name'])}\n"
        f"⭐ Рейтинг: <b>{card['rating']}</b>\n"
        f"💵 Получено: <b>€{sell_price:,}</b>"
    )


@dp.callback_query(F.data == "back_main")
async def back_main_callback(callback: CallbackQuery):
    await callback.answer()

    kb = InlineKeyboardBuilder()

    kb.button(
        text="⚽ Дроп",
        callback_data="drop"
    )

    kb.button(
        text="📚 Коллекция",
        callback_data="collection"
    )

    kb.button(
        text="🏪 Магазин",
        callback_data="shop"
    )

    kb.adjust(2, 1)

    await callback.message.answer(
        "⚽ <b>FOOTBALL DROP</b>\n\n"
        "Выбери действие:",
        reply_markup=kb.as_markup()
    )


@dp.message(Command("collection"))
async def collection_command(message: Message):
    await show_collection(message)


@dp.message(Command("drop"))
async def drop_command(message: Message):
    await do_drop(message)


@dp.message(Command("shop"))
async def shop_command(message: Message):
    await register(message.from_user)

    kb = InlineKeyboardBuilder()

    kb.button(
        text="🍀 Lucky Charm",
        callback_data="buy_charm"
    )

    kb.button(
        text="📦 Паки",
        callback_data="packs"
    )

    kb.button(
        text="💰 Рынок",
        callback_data="market"
    )

    kb.adjust(1)

    await message.answer(
        "🏪 <b>МАГАЗИН</b>",
        reply_markup=kb.as_markup()
    )


@dp.message(Command("balance"))
async def balance_command(message: Message):
    await register(message.from_user)

    user = await get_user(message.from_user.id)

    if not user:
        return

    await message.answer(
        "💰 <b>ТВОЙ БАЛАНС</b>\n\n"
        f"💵 Монеты: <b>€{user['balance']:,}</b>\n"
        f"⭐ Stars: <b>{user['stars']}</b>"
    )


@dp.message(Command("charm"))
async def charm_command(message: Message):
    await register(message.from_user)

    charm = await get_lucky_charm(message.from_user.id)

    if not charm:
        await message.answer(
            "🍀 <b>LUCKY CHARM</b>\n\n"
            "У тебя нет активного Lucky Charm.\n\n"
            "Купить его можно в 🏪 магазине."
        )
        return

    now = int(time.time())
    expires = charm["expires_at"]

    if expires <= now:
        await message.answer(
            "🍀 <b>LUCKY CHARM</b>\n\n"
            "❌ Lucky Charm закончился.\n\n"
            "Купить новый можно в магазине."
        )
        return

    left = expires - now

    hours = left // 3600
    minutes = (left % 3600) // 60

    await message.answer(
        "🍀 <b>LUCKY CHARM АКТИВЕН</b>\n\n"
        "🔥 Бонус: <b>x3 к шансу редкой карты</b>\n"
        f"⏳ Осталось: <b>{hours} ч. {minutes} мин.</b>"
    )


async def main():
    await init_db()

    bot = Bot(token=TOKEN)

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
