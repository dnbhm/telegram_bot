import os
import asyncio
import json
from datetime import datetime
from dotenv import load_dotenv
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, BotCommand, BotCommandScopeChat
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes, MessageHandler, filters
from telegram.request import HTTPXRequest

# Загружаем переменные окружения из .env файла
load_dotenv()

# Токен бота из переменной окружения
TOKEN = os.getenv("BOT_TOKEN")

# ID администраторов
ADMIN_IDS = [994881050, 759470806, 885023976, 545988920]

# --- ПУТЬ К ФАЙЛУ В ПОСТОЯННОМ ХРАНИЛИЩЕ ---
DATA_DIR = os.getenv("DATA_DIR", "/data")
if not os.path.exists(DATA_DIR):
    DATA_DIR = "data"
    os.makedirs(DATA_DIR, exist_ok=True)

USERS_FILE = os.path.join(DATA_DIR, "users.json")

# --- Константы с текстами и ссылками ---

# Текст с уроком (после кружка)
LESSON_DESCRIPTION_TEXT = (
    "*Ты готооов с удовольствием использовать летнее время по максимуму и начать заниматься любимым делом????🛼*\n\n"
    "В этом уроке ты узнаешь:\n\n"
    "//Кто такой монтажёр? Разберём, какие задачи и вопросы решает\n\n"
    "//Изучим виды монтажа, поговорим про горизонтальный и вертикальный монтаж\n\n"
    "А также я научу рассчитывать вас свою заработную плату в месяц🤫\n\n"
    "//Самый главный вопрос🍽️\n"
    "Где искать клиентов? Разберем, какие способы работают лучше всего\n\n"
    "//Разберём, как создавать портфолио, откуда брать работы, чтобы привлекать клиентов\n\n"
    "//И один из самых важных аспектов, который поможет выделяться среди других *«КРЕАТИВ»*🪩\n\n"
    "Обсудим, что такое креатив, откуда его брать и почему за помощью обращаются именно к монтажёру\n\n"
    "🧁 *Обязательно смотри урок до конца, ведь там тебя ждёт ПОДАРОК,*\n"
    "*который поможет сдвинуться с мёртвой точки и начать расти в сфере монтажа*\n\n"
    "Жми на кнопку ниже и смотри урок 🙂‍↕️"
)

# Сообщение с подарком (через 5 минут после отправки видео)
GIFT_MESSAGE_TEXT = (
    "*Ты уже сделал первые шаги к своему росту этим летом, но это ещё не всё☕️*\n\n"
    "Я подготовила для вас подарок, который поможет продвинуться в сфере монтажа, и это……\n\n"
    "*Разбор от меня или моей команды (шок??!!?)*\n\n"
    "Сейчас ты можешь принять участие в бесплатной консультации, на которой получишь точечные решения ситуаций в работе монтажёром💻\n\n"
    "Мы поговорим обо всем: как начать работать, продолжать расти, креативить и быть востребованным специалистом\n\n"
    "А после разбора у тебя будет возможность попасть ко мне на обучение по самым вкусным условиям🧁\n\n"
    "*Заполняй анкету right nowwww* 👇"
)

# Промо-пост (через 24 часа после урока)
PROMO_POST_TEXT = (
    "*Лето создано, чтобы начать что-то новое…*🍦\n\n"
    "Всю свою осознанную жизнь я развиваюсь в медиа: от актерского мастерства и журналистики "
    "до изучения кинематографа — учеба на кинооператора, а теперь то, что дает мне энергию, "
    "бесконечный креатив, возможности & свободу — *МОНТАЖ*\n\n"
    "Если ты хочешь работать в сфере монтажа или выйти на новый уровень, креативить, "
    "наслаждаться процессом — не думай, *а беги смотреть урок*💡\n\n"
    "Потому что там ты узнаешь всё, что нужно, чтобы этим летом реально начать "
    "заниматься любимым делом⭐️"
)

# Пост Vision Summer Club (отправляется через 1 час после кейсов)
VISION_CLUB_TEXT = (
    "<b>та самая летняя неделя, когда вы точно захотите оставить свои дела и начать творить</b>🍦\n\n"
    "<b>Vision Summer Club</b>\n\n"
    "я знаю, что многие хотели бы себя попробовать в сфере монтажа, узнать новые фишки, "
    "погрузиться в атмосферу обучения и у вас есть эта возможность 🛼\n\n"
    "я создала бесплатный интенсив «Vision Summer Club», где всю неделю мы будем вдохновляться, "
    "творить, поддерживать друг друга, расти в монтаже\n\n"
    "<b>интенсив пройдёт с 8 по 13 июня, давайте посмотрим, что вас ждёт:</b>\n\n"
    "<b>// 1 день: папка монтажёра</b> – как организовать рабочее пространство, познакомлю вас с концепцией будущего проекта\n\n"
    "<b>// 2 день: кинематографический монтаж</b> – разбор кино-языка — Феллини, Соррентино и другие\n\n"
    "<b>// 3 день: вертикальный монтаж</b> – как кинокадр живёт в рилсе, работа со звуком, ритм, пространство\n\n"
    "<b>// 4 день: анимационный монтаж</b> — техника stop motion & ее интеграция в вертикальный формат\n\n"
    "<b>// 5 день: личный бренд и клиенты</b> — как через один ролик раскрывать личность в блоге & поговорим про поиск клиентов\n\n"
    "<b>// 6 день: приятный бонус от меня</b>, который поможет ещё больше расти в монтаже\n\n"
    "за 5 дней у вас будет возможность создать свой ролик с 0: от выбора кино-фрагмента до готового рилса с анимацией\n\n"
    "<b>этот интенсив я создавала с одной мыслью:</b>\n\n"
    "чтобы каждый смог уйти с новыми знаниями и желанием расти дальше: неважно, новичок ты или уже действующий монтажёр, "
    "потому что мы будем разбирать приёмы, фишки, смыслы, искать вдохновение, креативить и обязательно поговорим про клиентов\n\n"
    "<b>вы можете попасть на обучение совершенно бесплатно, присоединяйтесь по ссылке, я вас буду ждать⬇️</b>\n\n"
    "<b><a href='https://t.me/+8cSWBiyep6FiN2Ri'>Vision Summer Club</a></b>"
)

# Пост Vision Мастерская (без фото)
VISION_MASTERSKAYA_POST_TEXT = (
    "<b>Как насчёт того, чтобы провести это лето ярко и продуктивно??🪩</b>\n\n"
    "мне постоянно поступают заявки на второй поток Vision Мастерской, и я решила, что лето — реально самое лучшее время, когда можно стать крутецким монтажером⭐️\n\n"
    "Мастерская — моя любовь, 3 месяца обучения компьютерному монтажу, где мы развиваем навык насмотренности, креативности, изучаем новые программы, фишки, анализируем кино, ищем клиентов и зарабатываем на любимом деле 🛼\n\n"
    "<b>Что вас ждёт:</b>\n\n"
    "// освоишь базу в монтаже, которая поможет развиться в данной сфере\n"
    "// изучишь программы: CapCut, Final Cut, Davinci, After Effects\n"
    "// получишь инструменты, которые помогут создавать креативные и продающие ролики\n"
    "// освоишь вертикальный и горизонтальный монтаж\n"
    "// прокачаешь насмотренность и креативное мышление\n"
    "// научишься привлекать клиентов и качественно взаимодействовать с ними\n\n"
    "<b>Но ещё не всё…🤫</b>\n\n"
    "// Интенсивы по заработку и прокачке личного бренда\n"
    "// Чат с вакансиями, где я отдаю самых горячих клиентов\n"
    "// Эфир с юристом\n"
    "// Бот саморефлексии, чтобы вы могли отслеживать уровень продуктивности\n\n"
    "<b>поэтому 6 июля стартует «Vision Мастерская», но уже 29 июня начинается предобучение — знакомимся, вникаем в темы 🍦</b>"
)

# Пост Вика (кейс с pic3.jpg)
VIKA_POST_TEXT = (
    "<b>купила курс и сразу начала зарабатывать⭐️</b>\n\n"
    "моя ученица Вика (@viksiiio) уже во время обучения вышла на доход 120к в месяц и продолжает расти\n\n"
    "<b>до обучения:</b>\n"
    "> работала сценаристом рилсов\n"
    "> хотела монтировать крутые анимационные ролики\n"
    "> клиенты спрашивали про монтаж, но не хватало навыков\n"
    "> не зарабатывала на монтаже\n\n"
    "многие думают что монтаж — это что-то недосягаемое, что нужен особый талант или кинообразование, но на самом деле это навык который можно освоить с нуля и сделать из него полноценную профессию с доходом🍦\n\n"
    "<b>за время обучения:</b>\n"
    "> появилась насмотренность, теперь смотрит рилсы и раскладывает монтаж по слоям\n"
    "> скиллы растут с каждым днём\n"
    "> перестала бояться клиентов и общения с ними\n"
    "> повысила заработок, просто начав изучать новую сферу и вышла на доход 120к в месяц\n\n"
    "Многие хотят творчество и доход, монтаж — идеальный баланс, потому что спрос растёт, клиенты есть и даже с нулём опыта можно собрать портфолио, найти заказчиков и выйти в прибыль🎬"
)

# Пост "Стартуем 6 июля"
START_POST_TEXT = (
    "sooooooo, если вы хотите изучить самую востребованную профессию в 2026 году🍦\n\n"
    "То скорее занимайте местечко, ведь их остаётся совсем мало!!!\n\n"
    "стартуееем уже <b>6 июля!!!⭐️</b>"
)

# Первый кейс (Алиса)
CASE1_TEXT = (
    "<b>«Обучение стало лучшим вложением в 2026 году, потому что спустя 3 месяца я вышла на доход 130к в месяц»</b> 🪩\n\n"
    "<b>Давайте расскажу про Алису (@alisakokovina)</b>\n\n"
    "<b>До обучения:</b>\n"
    "> работала монтажёром, но делала интуитивно\n"
    "> доход 50–70к в месяц\n"
    "> не всегда понимала как создавать анимационные эффекты\n"
    "> не делала горизонтальный формат\n"
    "> творческий кризис\n\n"
    "<b>Зарабатывать на монтаже - не сложно, если понимать, как формируется твой заработок🙂‍↕️</b>\n\n"
    "<b>Из чего строился доход у Алисы:</b>\n"
    "> пакет 28к (8 роликов по 3500)\n"
    "> пакет 35к (7 роликов по 5000)\n"
    "> UGC-клиент ~30-35к\n"
    "> 3 ютуб ролика ~21к\n"
    "> посты для клиентов ~15к\n\n"
    "= ~130к\n\n"
    "<b>Правда: 2-3 постоянных клиента и это уже стабильные 50-80к в месяц, не надо каждый раз искать новых 🙌</b>\n\n"
    "<b>Во время обучения:</b>\n"
    "> научилась цветокоррекции в Davinci\n"
    "> начала анализировать фильмы, клипы\n"
    "> появился свой стиль\n"
    "> начала мыслить целостной историей вместо отдельных эффектов\n"
    "> вышла на доход 130к\n\n"
    "И вы сможете, если будете работать над навыками, не ждать и тогда всё получится🤍"
)

# Второй кейс (Лиза)
CASE2_TEXT = (
    "<b>смонтировать рилс – это одно, а перестать бояться, что ты плохой монтажёр – совсем другое</b>🙂‍↕️\n\n"
    "ко мне на обучение пришла ученица Лиза (@elzavettta)\n\n"
    "<b>До обучения:</b>\n"
    "> // работала в сфере smm за небольшие деньги, чувствовала себя обесцененной\n"
    "> // ушла в монтаж, монтировала год для клиентов, но понимала, что недостаточно навыков\n"
    "> // не могла сказать себе и другим: «Я монтажёр, я могу сделать вам классные ролики», от этого выгорание, низкие чеки\n\n"
    "<b>После обучения:</b>\n"
    "> // перестала думать, что она плохой монтажёр\n"
    "> // появились 2 стабильных клиента\n"
    "> // вырос средний чек с 1,3 т.р до 5 т.р\n"
    "> // «я когда думаю о том, за сколько я делала ролики, которые как оказалось, можно делать за 5т.р, мне становится плохо»\n\n"
    "на обучении мы прорабатываем не только технику и креатив⭐️\n\n"
    "но и то, что внутри, чтобы человек перестал бояться проявляться, называть цену, говорить «я монтажёр»\n\n"
    "потому что без этого даже самые крутые навыки не приведут к деньгам и свободе🪩"
)

# Ссылки
SURVEY_URL = "https://docs.google.com/forms/d/e/1FAIpQLSe97sBgl1xuY6THBZjw4tENB5rDZSN8IQ46fpGC7mTer_cD8g/viewform?usp=header"
VIDEO_URL = "https://www.youtube.com/watch?v=7q0tfS3NcJc&feature=youtu.be"
VISION_MASTERSKAYA_URL = "https://goo.su/6Sga6A"

# Пути к файлам
VIDEO_NOTE_PATH = "video_notes/welcome.mp4"
LESSON_IMAGE_PATH = "images/lesson_preview.jpg"
CASE1_IMAGE_PATH = "images/pic1.jpg"
CASE2_IMAGE_PATH = "images/pic2.jpg"
VIKA_IMAGE_PATH = "images/pic3.jpg"

# Настройки задержек (в секундах)
DELAY_AFTER_VIDEO_NOTE = 17  # 17 секунд до урока
DELAY_AFTER_LESSON = 1800  # 5 минут до подарка
DELAY_AFTER_GIFT = 86400  # 24 часа до промо-поста
DELAY_AFTER_PROMO = 1800  # 30 минут после промо-поста до первого кейса
DELAY_BETWEEN_CASES = 1800  # 30 минут между кейсами
DELAY_AFTER_CASE2 = 3600  # 1 час после второго кейса до поста Vision Club

user_tasks = {}


# --- Функции для работы с пользователями ---

def load_users() -> dict:
    """Загружает список пользователей из файла"""
    try:
        with open(USERS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


def save_user(user_id: int, username: str, first_name: str) -> None:
    """Сохраняет пользователя в файл (админы не сохраняются)"""
    if is_admin(user_id):
        print(f"👑 Админ {user_id} нажал /start — не сохраняем в статистику")
        return

    users = load_users()
    user_id_str = str(user_id)

    if user_id_str not in users:
        clean_username = username.replace('_', '').replace('*', '') if username else None
        clean_first_name = first_name.replace('_', '').replace('*', '') if first_name else None

        users[user_id_str] = {
            "id": user_id,
            "username": clean_username,
            "first_name": clean_first_name,
            "first_seen": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        os.makedirs(os.path.dirname(USERS_FILE), exist_ok=True)
        with open(USERS_FILE, "w", encoding="utf-8") as f:
            json.dump(users, f, ensure_ascii=False, indent=2)


def is_admin(user_id: int) -> bool:
    """Проверяет, является ли пользователь админом"""
    return user_id in ADMIN_IDS


# --- Команда для получения своего ID ---
async def myid_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Показывает ID пользователя"""
    user = update.effective_user
    await update.message.reply_text(
        f"🆔 *Твой ID:* `{user.id}`\n"
        f"👤 *Username:* @{user.username}\n"
        f"📛 *Имя:* {user.first_name}",
        parse_mode="Markdown"
    )


# --- Команда /stat (статистика) ---
async def stat_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Показывает список всех пользователей, кто нажал /start (только для админов)"""
    user_id = update.effective_user.id

    if not is_admin(user_id):
        await update.message.reply_text("⛔ *Доступ запрещён!*\nЭта команда только для администраторов.",
                                        parse_mode="Markdown")
        return

    users = load_users()

    if not users:
        await update.message.reply_text("📊 *Статистика*\n\nПока ни одного пользователя не нажало /start.",
                                        parse_mode="Markdown")
        return

    def escape_markdown(text: str) -> str:
        special_chars = ['_', '*', '[', ']', '(', ')', '~', '`', '>', '#', '+', '-', '=', '|', '{', '}', '.', '!']
        for char in special_chars:
            text = text.replace(char, f'\\{char}')
        return text

    user_list = []
    for uid, data in users.items():
        username = f"@{escape_markdown(data['username'])}" if data['username'] else "❌ нет username"
        first_name = escape_markdown(data['first_name']) if data['first_name'] else "❌ нет имени"
        first_seen = data['first_seen']
        user_list.append(f"• `{uid}` | {username} | {first_name} | с {first_seen}")

    all_users_text = "\n".join(user_list)
    total_count = len(users)
    header = f"📊 *Статистика бота*\n\n👥 *Всего пользователей:* {total_count}\n\n📋 *Список:*\n\n"

    try:
        if len(header + all_users_text) > 4000:
            await update.message.reply_text(f"📊 *Статистика бота*\n\n👥 *Всего пользователей:* {total_count}",
                                            parse_mode="Markdown")
            chunk = ""
            for line in user_list:
                if len(chunk + line + "\n") > 4000:
                    await update.message.reply_text(chunk, parse_mode="Markdown")
                    chunk = line + "\n"
                else:
                    chunk += line + "\n"
            if chunk:
                await update.message.reply_text(chunk, parse_mode="Markdown")
        else:
            await update.message.reply_text(header + all_users_text, parse_mode="Markdown")
    except Exception as e:
        print(f"Ошибка при отправке статистики: {e}")
        await update.message.reply_text(
            f"📊 Статистика бота\n\nВсего пользователей: {total_count}\n\nСписок:\n\n" +
            "\n".join([line.replace('*', '').replace('_', '') for line in user_list])
        )


async def set_commands(application: Application) -> None:
    """Устанавливает команды в меню бота"""
    commands = [
        BotCommand("start", "Начать заново"),
        BotCommand("menu", "Показать главное меню"),
        BotCommand("help", "Помощь"),
        BotCommand("myid", "Узнать свой ID"),
        BotCommand("stat", "📊 Статистика пользователей (только админы)"),
        BotCommand("testvika", "🧪 Тест поста Вика"),
        BotCommand("sendvika", "📨 Отправить пост Вика всем"),
        BotCommand("teststart", "🧪 Тест поста Старт"),
        BotCommand("sendstart", "📨 Отправить пост Старт всем"),
        BotCommand("testvm", "🧪 Тест поста Vision Мастерская"),
        BotCommand("sendvm", "📨 Отправить пост Vision Мастерская всем"),
    ]
    await application.bot.set_my_commands(commands)
    print("✅ Команды бота установлены")


# --- Функция для отправки подарка (консультация + анкета) ---
async def send_gift_with_delay(chat_id: int, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Отправляет сообщение с подарком через 5 минут"""
    await asyncio.sleep(DELAY_AFTER_LESSON)

    keyboard = [[InlineKeyboardButton("📝 Заполнить анкету", url=SURVEY_URL)]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await context.bot.send_message(
        chat_id=chat_id,
        text=GIFT_MESSAGE_TEXT,
        parse_mode="Markdown",
        reply_markup=reply_markup
    )


# --- Функции для отправки кейсов новым пользователям ---
async def send_case1_to_new_user(chat_id: int, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Отправляет первый кейс (Алиса) новому пользователю через 30 минут после промо-поста"""
    await asyncio.sleep(DELAY_AFTER_PROMO)

    try:
        with open(CASE1_IMAGE_PATH, 'rb') as photo:
            await context.bot.send_photo(
                chat_id=chat_id,
                photo=photo,
                caption=CASE1_TEXT,
                parse_mode="HTML"
            )
    except FileNotFoundError:
        await context.bot.send_message(chat_id=chat_id, text=CASE1_TEXT, parse_mode="HTML")
    except Exception as e:
        print(f"❌ Ошибка при отправке кейса Алисы пользователю {chat_id}: {e}")

    print(f"📨 Кейс Алисы отправлен новому пользователю {chat_id} через 30 минут после промо-поста")

    # Запускаем таймер для второго кейса через 30 минут
    case2_key = f"case2_{chat_id}"
    if case2_key in user_tasks:
        if not user_tasks[case2_key].done():
            user_tasks[case2_key].cancel()

    user_tasks[case2_key] = asyncio.create_task(
        send_case2_to_new_user(chat_id, context)
    )


async def send_case2_to_new_user(chat_id: int, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Отправляет второй кейс (Лиза) новому пользователю через 30 минут после первого"""
    await asyncio.sleep(DELAY_BETWEEN_CASES)

    try:
        with open(CASE2_IMAGE_PATH, 'rb') as photo:
            await context.bot.send_photo(
                chat_id=chat_id,
                photo=photo,
                caption=CASE2_TEXT,
                parse_mode="HTML"
            )
    except FileNotFoundError:
        await context.bot.send_message(chat_id=chat_id, text=CASE2_TEXT, parse_mode="HTML")
    except Exception as e:
        print(f"❌ Ошибка при отправке кейса Лизы пользователю {chat_id}: {e}")

    print(f"📨 Кейс Лизы отправлен новому пользователю {chat_id} через 30 минут после кейса Алисы")

    # Запускаем таймер для отправки поста Vision Summer Club через 1 час
    vision_key = f"vision_{chat_id}"
    if vision_key in user_tasks:
        if not user_tasks[vision_key].done():
            user_tasks[vision_key].cancel()

    user_tasks[vision_key] = asyncio.create_task(
        send_vision_to_new_user(chat_id, context)
    )


async def send_vision_to_new_user(chat_id: int, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Отправляет пост Vision Summer Club новому пользователю через 1 час после второго кейса"""
    await asyncio.sleep(DELAY_AFTER_CASE2)

    try:
        await context.bot.send_message(
            chat_id=chat_id,
            text=VISION_CLUB_TEXT,
            parse_mode="HTML",
            disable_web_page_preview=False
        )
        print(f"📨 Пост Vision Summer Club отправлен новому пользователю {chat_id} через 1 час после кейса Лизы")
    except Exception as e:
        print(f"❌ Ошибка при отправке Vision Summer Club пользователю {chat_id}: {e}")


# --- Функция для отправки промо-поста новым пользователям через 24 часа ---
async def send_promo_to_new_user(chat_id: int, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Отправляет промо-пост новому пользователю через 24 часа после урока"""
    await asyncio.sleep(DELAY_AFTER_GIFT)

    keyboard = [[InlineKeyboardButton("🎬 Смотреть урок на YouTube", url=VIDEO_URL)]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    try:
        await context.bot.send_message(
            chat_id=chat_id,
            text=PROMO_POST_TEXT,
            parse_mode="Markdown",
            reply_markup=reply_markup
        )
        print(f"📨 Промо-пост отправлен новому пользователю {chat_id} через 24 часа")

        # Запускаем таймер для отправки первого кейса через 30 минут после промо-поста
        case1_key = f"case1_{chat_id}"
        if case1_key in user_tasks:
            if not user_tasks[case1_key].done():
                user_tasks[case1_key].cancel()

        user_tasks[case1_key] = asyncio.create_task(
            send_case1_to_new_user(chat_id, context)
        )

    except Exception as e:
        print(f"❌ Ошибка при отправке промо-поста пользователю {chat_id}: {e}")


# --- Функция для отправки урока с задержкой ---
async def send_lesson_with_delay(chat_id: int, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Отправляет текст с уроком через 17 секунд"""
    await asyncio.sleep(DELAY_AFTER_VIDEO_NOTE)

    keyboard = [[InlineKeyboardButton("🎬 Смотреть урок на YouTube", url=VIDEO_URL)]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    try:
        with open(LESSON_IMAGE_PATH, 'rb') as photo:
            await context.bot.send_photo(
                chat_id=chat_id,
                photo=photo,
                caption=LESSON_DESCRIPTION_TEXT,
                parse_mode="Markdown",
                reply_markup=reply_markup
            )
    except FileNotFoundError:
        await context.bot.send_message(
            chat_id=chat_id,
            text=LESSON_DESCRIPTION_TEXT,
            parse_mode="Markdown",
            reply_markup=reply_markup
        )

    # Запускаем таймер для отправки подарка через 5 минут
    if chat_id in user_tasks:
        if not user_tasks[chat_id].done():
            user_tasks[chat_id].cancel()

    user_tasks[chat_id] = asyncio.create_task(
        send_gift_with_delay(chat_id, context)
    )

    # Запускаем таймер для отправки промо-поста через 24 часа
    promo_task_key = f"promo_{chat_id}"
    if promo_task_key in user_tasks:
        if not user_tasks[promo_task_key].done():
            user_tasks[promo_task_key].cancel()

    user_tasks[promo_task_key] = asyncio.create_task(
        send_promo_to_new_user(chat_id, context)
    )


# --- Команда /start (без приветственного сообщения) ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """После /start сразу отправляем кружок и запускаем таймер"""
    user = update.effective_user
    user_id = user.id
    chat_id = update.effective_chat.id

    # Сохраняем пользователя
    save_user(user_id, user.username, user.first_name)
    print(f"📝 Новый пользователь: {user.first_name} (@{user.username}) ID: {user_id}")

    # Отменяем предыдущие задачи
    if user_id in user_tasks:
        if not user_tasks[user_id].done():
            user_tasks[user_id].cancel()
        del user_tasks[user_id]

    promo_key = f"promo_{user_id}"
    if promo_key in user_tasks:
        if not user_tasks[promo_key].done():
            user_tasks[promo_key].cancel()
        del user_tasks[promo_key]

    case1_key = f"case1_{user_id}"
    if case1_key in user_tasks:
        if not user_tasks[case1_key].done():
            user_tasks[case1_key].cancel()
        del user_tasks[case1_key]

    case2_key = f"case2_{user_id}"
    if case2_key in user_tasks:
        if not user_tasks[case2_key].done():
            user_tasks[case2_key].cancel()
        del user_tasks[case2_key]

    vision_key = f"vision_{user_id}"
    if vision_key in user_tasks:
        if not user_tasks[vision_key].done():
            user_tasks[vision_key].cancel()
        del user_tasks[vision_key]

    context.user_data["state"] = "start"

    # Отправляем кружок сразу
    try:
        with open(VIDEO_NOTE_PATH, 'rb') as video_note:
            await update.message.reply_video_note(
                video_note=video_note,
                duration=30
            )
    except FileNotFoundError:
        print("⚠️ Кружок не найден")
        await update.message.reply_text("🎬 *Подготавливаю урок...*", parse_mode="Markdown")

    # Запускаем таймер для урока через 17 секунд
    user_tasks[user_id] = asyncio.create_task(
        send_lesson_with_delay(chat_id, context)
    )


# --- Команда /menu ---
async def menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Показывает главное меню с кнопкой-ссылкой на урок"""
    keyboard = [[InlineKeyboardButton("🎬 Смотреть урок на YouTube", url=VIDEO_URL)]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    try:
        with open(LESSON_IMAGE_PATH, 'rb') as photo:
            await update.message.reply_photo(
                photo=photo,
                caption=LESSON_DESCRIPTION_TEXT,
                parse_mode="Markdown",
                reply_markup=reply_markup
            )
    except FileNotFoundError:
        await update.message.reply_text(
            LESSON_DESCRIPTION_TEXT,
            parse_mode="Markdown",
            reply_markup=reply_markup
        )


# --- Команда /help ---
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Помощь"""
    help_text = (
        "🤖 *Команды бота:*\n\n"
        "/start - Начать заново (сразу отправит кружок)\n"
        "/menu - Показать главное меню\n"
        "/help - Показать эту справку\n"
        "/myid - Узнать свой ID\n"
        "/stat - Статистика пользователей (только админы)\n"
        "/testvika - Тест поста Вика (только админы)\n"
        "/sendvika - Отправить пост Вика всем (только админы)\n"
        "/teststart - Тест поста Старт (только админы)\n"
        "/sendstart - Отправить пост Старт всем (только админы)\n"
        "/testvm - Тест поста Vision Мастерская (только админы)\n"
        "/sendvm - Отправить пост Vision Мастерская всем (только админы)\n\n"
        "Просто нажимай на кнопки для навигации!"
    )
    await update.message.reply_text(help_text, parse_mode="Markdown")


# --- ТЕСТОВЫЕ КОМАНДЫ ДЛЯ ПРОВЕРКИ (только для админов) ---
async def test_vika(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Отправляет тестовый пост Вика только админу"""
    user_id = update.effective_user.id

    if not is_admin(user_id):
        await update.message.reply_text("⛔ Доступ запрещён!")
        return

    await update.message.reply_text("🧪 Тестовая отправка\n\nОтправляю пост Вика только вам...")

    try:
        with open(VIKA_IMAGE_PATH, 'rb') as photo:
            await update.message.reply_photo(
                photo=photo,
                caption=VIKA_POST_TEXT,
                parse_mode="HTML"
            )
    except FileNotFoundError:
        await update.message.reply_text("❌ Фото pic3.jpg не найдено")
        await update.message.reply_text(VIKA_POST_TEXT, parse_mode="HTML")
    except Exception as e:
        await update.message.reply_text(f"❌ Ошибка: {e}")

    await update.message.reply_text("✅ Готово!")


async def test_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Отправляет тестовый пост Старт только админу"""
    user_id = update.effective_user.id

    if not is_admin(user_id):
        await update.message.reply_text("⛔ Доступ запрещён!")
        return

    await update.message.reply_text("🧪 Тестовая отправка\n\nОтправляю пост Старт только вам...")

    try:
        keyboard = [[InlineKeyboardButton("⭐️ ЗАНЯТЬ МЕСТЕЧКО ⭐️", url=VISION_MASTERSKAYA_URL)]]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await update.message.reply_text(
            text=START_POST_TEXT,
            parse_mode="HTML",
            reply_markup=reply_markup,
            disable_web_page_preview=False
        )
    except Exception as e:
        await update.message.reply_text(f"❌ Ошибка: {e}")

    await update.message.reply_text("✅ Готово!")


async def test_vm(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Отправляет тестовый пост Vision Мастерская только админу (без фото)"""
    user_id = update.effective_user.id

    if not is_admin(user_id):
        await update.message.reply_text("⛔ Доступ запрещён!")
        return

    await update.message.reply_text("🧪 Тестовая отправка\n\nОтправляю пост Vision Мастерская только вам...")

    try:
        keyboard = [[InlineKeyboardButton("⭐️ ЗАНЯТЬ МЕСТЕЧКО ⭐️", url=VISION_MASTERSKAYA_URL)]]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await update.message.reply_text(
            text=VISION_MASTERSKAYA_POST_TEXT,
            parse_mode="HTML",
            reply_markup=reply_markup,
            disable_web_page_preview=False
        )
    except Exception as e:
        await update.message.reply_text(f"❌ Ошибка: {e}")

    await update.message.reply_text("✅ Готово!")


# --- КОМАНДЫ ДЛЯ РАССЫЛКИ ВСЕМ ПОЛЬЗОВАТЕЛЯМ (только для админов) ---
async def send_vika_to_existing_users(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Отправляет пост Вика всем существующим пользователям (только админы)"""
    user_id = update.effective_user.id

    if not is_admin(user_id):
        await update.message.reply_text("⛔ *Доступ запрещён!*\nЭта команда только для администраторов.",
                                        parse_mode="Markdown")
        return

    users = load_users()

    if not users:
        await update.message.reply_text("📭 Нет пользователей для рассылки")
        return

    await update.message.reply_text(f"📢 Начинаю рассылку поста Вика {len(users)} пользователям...")

    success_count = 0
    fail_count = 0

    for user_id_str, user_data in users.items():
        uid = int(user_id_str)

        if is_admin(uid):
            continue

        try:
            with open(VIKA_IMAGE_PATH, 'rb') as photo:
                await context.bot.send_photo(
                    chat_id=uid,
                    photo=photo,
                    caption=VIKA_POST_TEXT,
                    parse_mode="HTML"
                )

            success_count += 1
            print(f"✅ Пост Вика отправлен пользователю {user_data.get('first_name', uid)}")
            await asyncio.sleep(0.3)

        except FileNotFoundError:
            try:
                await context.bot.send_message(
                    chat_id=uid,
                    text=VIKA_POST_TEXT,
                    parse_mode="HTML"
                )
                success_count += 1
                print(f"✅ Пост Вика (без фото) отправлен пользователю {user_data.get('first_name', uid)}")
            except Exception as e:
                fail_count += 1
                print(f"❌ Ошибка при отправке пользователю {uid}: {e}")
            await asyncio.sleep(0.3)

        except Exception as e:
            fail_count += 1
            print(f"❌ Ошибка при отправке пользователю {uid}: {e}")

    await update.message.reply_text(
        f"✅ Рассылка поста Вика завершена!\n\n"
        f"📤 Успешно: {success_count}\n"
        f"❌ Ошибок: {fail_count}"
    )


async def send_start_to_existing_users(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Отправляет пост Старт всем существующим пользователям (только админы)"""
    user_id = update.effective_user.id

    if not is_admin(user_id):
        await update.message.reply_text("⛔ *Доступ запрещён!*\nЭта команда только для администраторов.",
                                        parse_mode="Markdown")
        return

    users = load_users()

    if not users:
        await update.message.reply_text("📭 Нет пользователей для рассылки")
        return

    await update.message.reply_text(f"📢 Начинаю рассылку поста Старт {len(users)} пользователям...")

    success_count = 0
    fail_count = 0

    keyboard = [[InlineKeyboardButton("⭐️ ЗАНЯТЬ МЕСТЕЧКО ⭐️", url=VISION_MASTERSKAYA_URL)]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    for user_id_str, user_data in users.items():
        uid = int(user_id_str)

        if is_admin(uid):
            continue

        try:
            await context.bot.send_message(
                chat_id=uid,
                text=START_POST_TEXT,
                parse_mode="HTML",
                reply_markup=reply_markup,
                disable_web_page_preview=False
            )

            success_count += 1
            print(f"✅ Пост Старт отправлен пользователю {user_data.get('first_name', uid)}")
            await asyncio.sleep(0.3)

        except Exception as e:
            fail_count += 1
            print(f"❌ Ошибка при отправке пользователю {uid}: {e}")

    await update.message.reply_text(
        f"✅ Рассылка поста Старт завершена!\n\n"
        f"📤 Успешно: {success_count}\n"
        f"❌ Ошибок: {fail_count}"
    )


async def send_vm_to_existing_users(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Отправляет пост Vision Мастерская всем существующим пользователям (только админы, без фото)"""
    user_id = update.effective_user.id

    if not is_admin(user_id):
        await update.message.reply_text("⛔ *Доступ запрещён!*\nЭта команда только для администраторов.",
                                        parse_mode="Markdown")
        return

    users = load_users()

    if not users:
        await update.message.reply_text("📭 Нет пользователей для рассылки")
        return

    await update.message.reply_text(f"📢 Начинаю рассылку поста Vision Мастерская {len(users)} пользователям...")

    success_count = 0
    fail_count = 0

    keyboard = [[InlineKeyboardButton("⭐️ ЗАНЯТЬ МЕСТЕЧКО ⭐️", url=VISION_MASTERSKAYA_URL)]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    for user_id_str, user_data in users.items():
        uid = int(user_id_str)

        if is_admin(uid):
            continue

        try:
            await context.bot.send_message(
                chat_id=uid,
                text=VISION_MASTERSKAYA_POST_TEXT,
                parse_mode="HTML",
                reply_markup=reply_markup,
                disable_web_page_preview=False
            )

            success_count += 1
            print(f"✅ Vision Мастерская отправлен пользователю {user_data.get('first_name', uid)}")
            await asyncio.sleep(0.3)

        except Exception as e:
            fail_count += 1
            print(f"❌ Ошибка при отправке пользователю {uid}: {e}")

    await update.message.reply_text(
        f"✅ Рассылка поста Vision Мастерская завершена!\n\n"
        f"📤 Успешно: {success_count}\n"
        f"❌ Ошибок: {fail_count}"
    )


# --- Обработчик для любых сообщений ---
async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Отвечает на любые текстовые сообщения, кроме команд"""
    await update.message.reply_text(
        "Пожалуйста, используй кнопки меню или команду /start"
    )


def main() -> None:
    """Запуск бота"""
    if not TOKEN:
        raise ValueError("BOT_TOKEN не найден. Создай файл .env и добавь BOT_TOKEN=твой_токен")

    # Увеличиваем таймауты
    request = HTTPXRequest(
        connect_timeout=120.0,
        read_timeout=120.0,
        write_timeout=120.0,
        pool_timeout=120.0
    )

    application = Application.builder().token(TOKEN).request(request).build()
    application.post_init = set_commands

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("menu", menu))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("myid", myid_command))
    application.add_handler(CommandHandler("stat", stat_command))
    application.add_handler(CommandHandler("testvika", test_vika))
    application.add_handler(CommandHandler("sendvika", send_vika_to_existing_users))
    application.add_handler(CommandHandler("teststart", test_start))
    application.add_handler(CommandHandler("sendstart", send_start_to_existing_users))
    application.add_handler(CommandHandler("testvm", test_vm))
    application.add_handler(CommandHandler("sendvm", send_vm_to_existing_users))

    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))

    print("🚀 Бот запущен и готов к работе!")
    print(
        "⏱️ Тайминги: кружок → 17 сек → урок → 5 мин → подарок → 24 часа → промо-пост → 30 мин → кейс Алисы → 30 мин → кейс Лизы → 1 час → Vision Summer Club")
    print(f"👑 Админы ID: {ADMIN_IDS}")
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()