import os
import asyncio
import json
from datetime import datetime
from dotenv import load_dotenv
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, BotCommand
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

# Пост Вебинар
WEBINAR_TEXT = (
    "<b>ВЕБИНАР ЭТИМ ЛЕТНИМ ДНЁМ 🛼</b>\n\n"
    "Вас ждёт эфир на тему: <b>«Как стать востребованным монтажёром уже этим летом»</b>🍦\n\n"
    "<b>Что разберём на вебинаре:</b>\n\n"
    "<i>// кто такой монтажёр?</i>\n"
    "разберём, какие задачи решает монтажёр, куда можно расти и на что делать упор\n\n"
    "<i>// виды монтажа: поговорим про горизонтальный и вертикальный монтаж</i>\n\n"
    "<i>// расскажу, как рассчитать свою заработную плату и выйти на 100-150к в месяц</i>\n\n"
    "<i>// как создавать портфолио: откуда брать работы, если нет ещё клиентов? как оформить портфолио, чтобы оно продавало</i>\n\n"
    "<i>// где брать вдохновение и креатив? Обсудим, что такое креатив монтажа и как вдохновляться не только на Pinterest</i>\n\n"
    "<i>// открытие продаж на моё обучение «Vision Мастерская»</i>\n\n"
    "<b>РАЗБОР ВАШИХ РАБОТ ОТ МЕНЯ🪩</b>\n\n"
    "я выберу несколько ваших работ из анкеты и разберу в прямом эфире, где поделюсь своим мнением🍦\n\n"
    "<b>Встречаемся уже в СЕГОДНЯ в 18:00 по МСК</b>\n\n"
    "Переходи по ссылке, чтобы участвовать на вебинаре и не забудь заполнить анкету на разбор, если хочешь получить комментарии от меня\n\n"
    "<b>⭐️⭐️⭐️ССЫЛОЧКА⭐️⭐️⭐️</b>"
)

# Пост Гранты
GRANTS_TEXT = (
    "<b>И САМОЕ ВКУСНОЕ - ГРАНТЫ НА ОБУЧЕНИЕ</b>\n\n"
    "3 места - вы сможете получить место в «Vision Мастерской» со скидкой 30%\n\n"
    "Чтобы участвовать в разборе и в грантах - заполняйте анкету\n\n"
    "*работу можно прикрепить, которую вы сделали на интенсиве или уже смонтированный ролик для себя / клиента\n\n"
    "*условие участия в грантах - присутствие на вебинаре\n\n"
    "<b>🫥ССЫЛОЧКА НА РЕГИСТРАЦИЮ🫥</b>"
)

# Ссылка на вебинар и анкету
WEBINAR_URL = "https://t.me/+l2NfnQhCgrA2NDhi"  # ЗАМЕНИТЕ НА РЕАЛЬНУЮ ССЫЛКУ
SURVEY_URL = "https://docs.google.com/forms/d/e/1FAIpQLSe97sBgl1xuY6THBZjw4tENB5rDZSN8IQ46fpGC7mTer_cD8g/viewform?usp=header"
VIDEO_URL = "https://www.youtube.com/watch?v=7q0tfS3NcJc&feature=youtu.be"

# Пути к файлам
VIDEO_NOTE_PATH = "video_notes/welcome.mp4"
LESSON_IMAGE_PATH = "images/lesson_preview.jpg"
CASE1_IMAGE_PATH = "images/pic1.jpg"
CASE2_IMAGE_PATH = "images/pic2.jpg"

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
    """Устанавливает команды в меню бота (только для админов видны админские команды)"""
    # Обычные команды для всех
    commands = [
        BotCommand("start", "Начать заново"),
        BotCommand("menu", "Показать главное меню"),
        BotCommand("help", "Помощь"),
        BotCommand("myid", "Узнать свой ID"),
    ]
    await application.bot.set_my_commands(commands)

    # Админские команды устанавливаются отдельно для админов
    admin_commands = [
        BotCommand("stat", "Статистика (только админы)"),
        BotCommand("testwebinar", "🧪 Тест поста Вебинар"),
        BotCommand("sendwebinar", "📨 Отправить пост Вебинар всем"),
        BotCommand("testgrants", "🧪 Тест поста Гранты"),
        BotCommand("sendgrants", "📨 Отправить пост Гранты всем"),
    ]

    for admin_id in ADMIN_IDS:
        try:
            await application.bot.set_my_commands(commands, scope=telegram.BotCommandScopeChat(admin_id))
            await application.bot.set_my_commands(admin_commands, scope=telegram.BotCommandScopeChat(admin_id))
        except Exception as e:
            print(f"⚠️ Не удалось установить команды для админа {admin_id}: {e}")

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
        "/myid - Узнать свой ID\n\n"
        "👑 *Администраторам:*\n"
        "Команды /stat, /testwebinar, /sendwebinar, /testgrants, /sendgrants доступны только администраторам"
    )
    await update.message.reply_text(help_text, parse_mode="Markdown")


# --- ТЕСТОВЫЕ КОМАНДЫ ДЛЯ ПРОВЕРКИ (только для админов) ---
async def test_webinar(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Отправляет тестовый пост Вебинар только админу"""
    user_id = update.effective_user.id

    if not is_admin(user_id):
        await update.message.reply_text("⛔ Доступ запрещён!")
        return

    await update.message.reply_text("🧪 Тестовая отправка\n\nОтправляю пост Вебинар только вам...")

    try:
        keyboard = [[InlineKeyboardButton("⭐️ ПЕРЕЙТИ НА ВЕБИНАР ⭐️", url=WEBINAR_URL)]]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await update.message.reply_text(
            text=WEBINAR_TEXT,
            parse_mode="HTML",
            disable_web_page_preview=False,
            reply_markup=reply_markup
        )
    except Exception as e:
        await update.message.reply_text(f"❌ Ошибка: {e}")

    await update.message.reply_text("✅ Готово!")


async def test_grants(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Отправляет тестовый пост Гранты только админу"""
    user_id = update.effective_user.id

    if not is_admin(user_id):
        await update.message.reply_text("⛔ Доступ запрещён!")
        return

    await update.message.reply_text("🧪 Тестовая отправка\n\nОтправляю пост Гранты только вам...")

    try:
        keyboard = [[InlineKeyboardButton("🫥 ЗАПОЛНИТЬ АНКЕТУ 🫥", url=SURVEY_URL)]]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await update.message.reply_text(
            text=GRANTS_TEXT,
            parse_mode="HTML",
            disable_web_page_preview=False,
            reply_markup=reply_markup
        )
    except Exception as e:
        await update.message.reply_text(f"❌ Ошибка: {e}")

    await update.message.reply_text("✅ Готово!")


# --- КОМАНДЫ ДЛЯ РАССЫЛКИ (только для админов) ---
async def send_webinar_to_existing_users(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Отправляет пост Вебинар всем существующим пользователям (только админы)"""
    user_id = update.effective_user.id

    if not is_admin(user_id):
        await update.message.reply_text("⛔ *Доступ запрещён!*\nЭта команда только для администраторов.",
                                        parse_mode="Markdown")
        return

    users = load_users()

    if not users:
        await update.message.reply_text("📭 Нет пользователей для рассылки")
        return

    await update.message.reply_text(f"📢 Начинаю рассылку поста Вебинар {len(users)} пользователям...")

    success_count = 0
    fail_count = 0

    keyboard = [[InlineKeyboardButton("⭐️ ПЕРЕЙТИ НА ВЕБИНАР ⭐️", url=WEBINAR_URL)]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    for user_id_str, user_data in users.items():
        uid = int(user_id_str)

        if is_admin(uid):
            continue

        try:
            await context.bot.send_message(
                chat_id=uid,
                text=WEBINAR_TEXT,
                parse_mode="HTML",
                disable_web_page_preview=False,
                reply_markup=reply_markup
            )

            success_count += 1
            print(f"✅ Вебинар отправлен пользователю {user_data.get('first_name', uid)}")
            await asyncio.sleep(0.3)

        except Exception as e:
            fail_count += 1
            print(f"❌ Ошибка при отправке пользователю {uid}: {e}")

    await update.message.reply_text(
        f"✅ Рассылка поста Вебинар завершена!\n\n"
        f"📤 Успешно: {success_count}\n"
        f"❌ Ошибок: {fail_count}"
    )


async def send_grants_to_existing_users(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Отправляет пост Гранты всем существующим пользователям (только админы)"""
    user_id = update.effective_user.id

    if not is_admin(user_id):
        await update.message.reply_text("⛔ *Доступ запрещён!*\nЭта команда только для администраторов.",
                                        parse_mode="Markdown")
        return

    users = load_users()

    if not users:
        await update.message.reply_text("📭 Нет пользователей для рассылки")
        return

    await update.message.reply_text(f"📢 Начинаю рассылку поста Гранты {len(users)} пользователям...")

    success_count = 0
    fail_count = 0

    keyboard = [[InlineKeyboardButton("🫥 ЗАПОЛНИТЬ АНКЕТУ 🫥", url=SURVEY_URL)]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    for user_id_str, user_data in users.items():
        uid = int(user_id_str)

        if is_admin(uid):
            continue

        try:
            await context.bot.send_message(
                chat_id=uid,
                text=GRANTS_TEXT,
                parse_mode="HTML",
                disable_web_page_preview=False,
                reply_markup=reply_markup
            )

            success_count += 1
            print(f"✅ Гранты отправлены пользователю {user_data.get('first_name', uid)}")
            await asyncio.sleep(0.3)

        except Exception as e:
            fail_count += 1
            print(f"❌ Ошибка при отправке пользователю {uid}: {e}")

    await update.message.reply_text(
        f"✅ Рассылка поста Гранты завершена!\n\n"
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

    # Увеличиваем таймауты для избежания ConnectTimeout
    request = HTTPXRequest(
        connect_timeout=30.0,
        read_timeout=30.0,
        write_timeout=30.0,
        pool_timeout=30.0
    )

    application = Application.builder().token(TOKEN).request(request).build()
    application.post_init = set_commands

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("menu", menu))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("myid", myid_command))
    application.add_handler(CommandHandler("stat", stat_command))
    application.add_handler(CommandHandler("testwebinar", test_webinar))
    application.add_handler(CommandHandler("sendwebinar", send_webinar_to_existing_users))
    application.add_handler(CommandHandler("testgrants", test_grants))
    application.add_handler(CommandHandler("sendgrants", send_grants_to_existing_users))

    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))

    print("🚀 Бот запущен и готов к работе!")
    print(
        "⏱️ Тайминги: кружок → 17 сек → урок → 5 мин → подарок → 24 часа → промо-пост → 30 мин → кейс Алисы → 30 мин → кейс Лизы → 1 час → Vision Summer Club")
    print(f"👑 Админы ID: {ADMIN_IDS}")
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()