import os
import asyncio
import json
from datetime import datetime
from dotenv import load_dotenv
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, BotCommand
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes, MessageHandler, filters

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
CASE1_TEXT = (
    "«Обучение стало лучшим вложением в 2026 году, потому что спустя 3 месяца я вышла на доход 130к в месяц» 🪩\n\n"
    "Моя ученица Алиса уже во время обучения начала зарабатывать больше 100к\n\n"
    "<b>До обучения:</b>\n"
    "<code>▸ полноценно работала монтажёром, но делала интуитивно\n"
    "▸ доход 50–70к в месяц\n"
    "▸ не всегда понимала как создавать анимационные эффекты\n"
    "▸ не делала горизонтальный формат\n"
    "▸ творческий кризис</code>\n\n"
)

CASE_TEXT = (
    "«Обучение стало лучшим вложением в 2026 году, потому что спустя 3 месяца я вышла на доход 130к в месяц» 🪩\n\n"
    "Моя ученица Алиса уже во время обучения начала зарабатывать больше 100к\n\n"
    "<b>До обучения:</b>\n"
    "<code>▸ полноценно работала монтажёром, но делала интуитивно\n"
    "▸ доход 50–70к в месяц\n"
    "▸ не всегда понимала как создавать анимационные эффекты\n"
    "▸ не делала горизонтальный формат\n"
    "▸ творческий кризис</code>\n\n"
    "Зарабатывать на монтаже - не сложно, если понимать, как формируется твой заработок🙂‍↕️\n\n"
    "<b>Из чего строился доход у Алисы:</b>\n"
    "<code>▸ пакет 28к (8 роликов по 3500)\n"
    "▸ пакет 35к (7 роликов по 5000)\n"
    "▸ UGC-клиент ~30-35к\n"
    "▸ 3 ютуб ролика ~21к\n"
    "▸ посты для клиентов ~15к\n\n"
    "= ~130к</code>\n\n"
    "Правда: два-три постоянных клиента и это уже стабильные 50-80к в месяц, не надо каждый раз искать новых 🙌\n\n"
    "<b>Во время обучения:</b>\n"
    "<code>▸ научилась цветокоррекции в Davinci\n"
    "▸ начала анализировать фильмы, клипы\n"
    "▸ появился свой стиль\n"
    "▸ начала мыслить целостной историей вместо отдельных эффектов\n"
    "▸ перестала бояться сложных проектов\n"
    "▸ вышла на доход 130к</code>\n\n"
    "И вы сможете, если будете работать над навыками, не ждать и тогда всё получится🤍"
)

CASE2_TEXT = (
    "<b>смонтировать рилс – это одно, а перестать бояться, что ты плохой монтажёр – совсем другое</b>🙂‍↕️\n\n"
    "ко мне на обучение пришла ученица Лиза (@elzavettta)\n\n"
    "<b>До обучения:</b>\n"
    "> • работала в сфере smm за небольшие деньги, чувствовала себя обесцененной\n"
    "> • ушла в монтаж, монтировала год для клиентов, но понимала, что недостаточно навыков\n"
    "> • не могла сказать себе и другим: «Я монтажёр, я могу сделать вам классные ролики», от этого выгорание, низкие чеки\n\n"
    "<b>После обучения:</b>\n"
    "> • перестала думать, что она плохой монтажёр\n"
    "> • появились 2 стабильных клиента\n"
    "> • вырос средний чек с 1,3 т.р до 5 т.р\n"
    "> • «я когда думаю о том, за сколько я делала ролики, которые как оказалось, можно делать за 5т.р, мне становится плохо»\n\n"
    "на обучении мы прорабатываем не только технику и креатив⭐️\n\n"
    "но и то, что внутри, чтобы человек перестал бояться проявляться, называть цену, говорить «я монтажёр»\n\n"
    "потому что без этого даже самые крутые навыки не приведут к деньгам и свободе🙌"
)
# Ссылки
SURVEY_URL = "https://docs.google.com/forms/d/e/1FAIpQLSeV3hbxukt2k-_9JVf0OyPPJf68ySNcsoB-kZF6NjdeBRDOgQ/viewform?usp=publish-editor"
VIDEO_URL = "https://www.youtube.com/watch?v=7q0tfS3NcJc&feature=youtu.be"

# Пути к файлам
VIDEO_NOTE_PATH = "video_notes/welcome.mp4"
LESSON_IMAGE_PATH = "images/lesson_preview.jpg"
GIFT_IMAGE_PATH = "images/gift_preview.jpg"
CASE1_IMAGE_PATH = "images/pic1.jpg"
CASE2_IMAGE_PATH = "images/pic2.jpg"

# Настройки задержек (в секундах)
DELAY_AFTER_VIDEO_NOTE = 17  # 17 секунд до урока
DELAY_AFTER_LESSON = 1800  # 5 минут до подарка
DELAY_AFTER_GIFT = 86400  # 24 часа до промо-поста
DELAY_AFTER_PROMO = 1800  # 30 минут после промо-поста до первого кейса
DELAY_BETWEEN_CASES = 1800  # 30 минут между кейсами

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
        BotCommand("stat", "Статистика (только админы)"),
        #BotCommand("sendcases", "📨 Рассылка кейсов всем пользователям (только админы)"),
        BotCommand("testcases", "🧪 Тестовая отправка кейсов (только админу)"),
    ]
    await application.bot.set_my_commands(commands)
    print("✅ Команды бота установлены")


# --- Функция для отправки подарка (консультация + анкета) ---
async def send_gift_with_delay(chat_id: int, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Отправляет сообщение с подарком через 5 минут"""
    await asyncio.sleep(DELAY_AFTER_LESSON)

    keyboard = [[InlineKeyboardButton("📝 Заполнить анкету", url=SURVEY_URL)]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    try:
        with open(GIFT_IMAGE_PATH, 'rb') as photo:
            await context.bot.send_photo(
                chat_id=chat_id,
                photo=photo,
                caption=GIFT_MESSAGE_TEXT,
                parse_mode="Markdown",
                reply_markup=reply_markup
            )
    except FileNotFoundError:
        await context.bot.send_message(
            chat_id=chat_id,
            text=GIFT_MESSAGE_TEXT,
            parse_mode="Markdown",
            reply_markup=reply_markup
        )


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

        # После промо-поста запускаем цепочку кейсов
        # Первый кейс через 30 минут
        case1_task_key = f"case1_{chat_id}"
        if case1_task_key in user_tasks:
            if not user_tasks[case1_task_key].done():
                user_tasks[case1_task_key].cancel()

        user_tasks[case1_task_key] = asyncio.create_task(
            send_case1_to_user(chat_id, context)
        )

    except Exception as e:
        print(f"❌ Ошибка при отправке промо-поста пользователю {chat_id}: {e}")


async def send_case1_to_user(chat_id: int, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Отправляет первый кейс через 30 минут после промо-поста"""
    await asyncio.sleep(DELAY_AFTER_PROMO)

    try:
        # Разбиваем текст на части
        case1_parts = split_long_text(CASE1_TEXT, 1024)

        # Отправляем картинку с первой частью
        with open(CASE1_IMAGE_PATH, 'rb') as photo:
            await context.bot.send_photo(
                chat_id=chat_id,
                photo=photo,
                caption=case1_parts[0],
                parse_mode="Markdown"
            )

        # Отправляем остальные части
        for part in case1_parts[1:]:
            await context.bot.send_message(chat_id=chat_id, text=part, parse_mode="Markdown")
            await asyncio.sleep(0.3)

    except FileNotFoundError:
        await context.bot.send_message(chat_id=chat_id, text=CASE1_TEXT, parse_mode="Markdown")

    print(f"📨 Первый кейс отправлен пользователю {chat_id}")

    # Запускаем таймер для второго кейса через 30 минут
    case2_task_key = f"case2_{chat_id}"
    if case2_task_key in user_tasks:
        if not user_tasks[case2_task_key].done():
            user_tasks[case2_task_key].cancel()

    user_tasks[case2_task_key] = asyncio.create_task(
        send_case2_to_user(chat_id, context)
    )


async def send_case2_to_user(chat_id: int, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Отправляет второй кейс через 30 минут после первого"""
    await asyncio.sleep(DELAY_BETWEEN_CASES)

    try:
        case2_parts = split_long_text(CASE2_TEXT, 1024)

        with open(CASE2_IMAGE_PATH, 'rb') as photo:
            await context.bot.send_photo(
                chat_id=chat_id,
                photo=photo,
                caption=case2_parts[0],
                parse_mode="Markdown"
            )

        for part in case2_parts[1:]:
            await context.bot.send_message(chat_id=chat_id, text=part, parse_mode="Markdown")
            await asyncio.sleep(0.3)

    except FileNotFoundError:
        await context.bot.send_message(chat_id=chat_id, text=CASE2_TEXT, parse_mode="Markdown")

    print(f"📨 Второй кейс отправлен пользователю {chat_id}")


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
        "/stat - Статистика пользователей (только админы)\n\n"
        "Просто нажимай на кнопки для навигации!"
    )
    await update.message.reply_text(help_text, parse_mode="Markdown")


async def send_cases_to_all(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Отправляет первый кейс сразу всем, второй через 30 минут (только админы)"""
    user_id = update.effective_user.id

    if not is_admin(user_id):
        await update.message.reply_text("⛔ *Доступ запрещён!*\nЭта команда только для администраторов.",
                                        parse_mode="Markdown")
        return

    users = load_users()

    if not users:
        await update.message.reply_text("📭 Нет пользователей для рассылки")
        return

    await update.message.reply_text(f"📢 Начинаю рассылку кейсов {len(users)} пользователям...\n"
                                    f"📤 Первый кейс отправляется сейчас\n"
                                    f"⏰ Второй кейс отправится через 30 минут")

    success_count = 0
    fail_count = 0

    for user_id_str, user_data in users.items():
        uid = int(user_id_str)

        if is_admin(uid):
            continue

        try:
            case1_parts = split_long_text(CASE1_TEXT, 1024)

            # Отправляем картинку с первой частью
            try:
                with open(CASE1_IMAGE_PATH, 'rb') as photo:
                    await context.bot.send_photo(
                        chat_id=uid,
                        photo=photo,
                        caption=case1_parts[0],
                        parse_mode="Markdown"
                    )

                # Отправляем остальные части
                for part in case1_parts[1:]:
                    await context.bot.send_message(chat_id=uid, text=part, parse_mode="Markdown")
                    await asyncio.sleep(0.2)

            except FileNotFoundError:
                await context.bot.send_message(chat_id=uid, text=CASE1_TEXT, parse_mode="Markdown")

            success_count += 1
            print(f"✅ Первый кейс отправлен пользователю {user_data.get('first_name', uid)}")
            await asyncio.sleep(0.3)

        except Exception as e:
            fail_count += 1
            print(f"❌ Ошибка при отправке первого кейса пользователю {uid}: {e}")

    await update.message.reply_text(
        f"✅ Первая часть рассылки завершена!\n\n"
        f"📤 Успешно: {success_count}\n"
        f"❌ Ошибок: {fail_count}\n\n"
        f"⏰ Через 30 минут начнётся отправка второго кейса..."
    )

    # Запускаем таймер для второго кейса через 30 минут
    asyncio.create_task(send_case2_to_all(context, users, success_count, fail_count, update.message.chat_id))


async def test_cases(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Отправляет тестовые кейсы только админу"""
    user_id = update.effective_user.id

    if not is_admin(user_id):
        await update.message.reply_text("⛔ Доступ запрещён!")
        return

    await update.message.reply_text("🧪 Тестовая рассылка\n\nОтправляю кейсы только вам...")

    # Первый кейс
    try:
        with open(CASE1_IMAGE_PATH, 'rb') as photo:
            await update.message.reply_photo(
                photo=photo,
                caption=CASE1_TEXT,
                parse_mode="HTML"  # <-- ИСПОЛЬЗУЕМ HTML
            )
    except FileNotFoundError:
        await update.message.reply_text("❌ Фото pic1.jpg не найдено")
        await update.message.reply_text(CASE1_TEXT, parse_mode="HTML")

    await asyncio.sleep(1)

    # Второй кейс
    try:
        with open(CASE2_IMAGE_PATH, 'rb') as photo:
            await update.message.reply_photo(
                photo=photo,
                caption=CASE2_TEXT,
                parse_mode="HTML"  # <-- ИСПОЛЬЗУЕМ HTML
            )
    except FileNotFoundError:
        await update.message.reply_text("❌ Фото pic2.jpg не найдено")
        await update.message.reply_text(CASE2_TEXT, parse_mode="HTML")

    await update.message.reply_text("✅ Готово!")


def split_long_text(text: str, max_length: int = 1024) -> list:
    """Разбивает длинный текст на части, не разрывая слова"""
    if len(text) <= max_length:
        return [text]

    parts = []
    lines = text.split('\n')
    current_part = ""

    for line in lines:
        if len(current_part) + len(line) + 1 <= max_length:
            if current_part:
                current_part += '\n' + line
            else:
                current_part = line
        else:
            if current_part:
                parts.append(current_part)
            current_part = line

    if current_part:
        parts.append(current_part)

    return parts

async def send_case2_to_all(context: ContextTypes.DEFAULT_TYPE, users: dict, success_count: int, fail_count: int,
                            admin_chat_id: int) -> None:
    """Отправляет второй кейс всем пользователям через 30 минут"""
    await asyncio.sleep(DELAY_BETWEEN_CASES)

    success2_count = 0
    fail2_count = 0

    for user_id_str, user_data in users.items():
        uid = int(user_id_str)

        if is_admin(uid):
            continue

        try:
            # Отправляем второй кейс: сначала картинка, потом текст
            try:
                with open(CASE2_IMAGE_PATH, 'rb') as photo:
                    await context.bot.send_photo(chat_id=uid, photo=photo)
                await context.bot.send_message(chat_id=uid, text=CASE2_TEXT, parse_mode="Markdown")
            except FileNotFoundError:
                await context.bot.send_message(chat_id=uid, text=CASE2_TEXT, parse_mode="Markdown")

            success2_count += 1
            print(f"✅ Второй кейс отправлен пользователю {user_data.get('first_name', uid)}")
            await asyncio.sleep(0.3)

        except Exception as e:
            fail2_count += 1
            print(f"❌ Ошибка при отправке второго кейса пользователю {uid}: {e}")

    # Отправляем отчёт админу
    await context.bot.send_message(
        chat_id=admin_chat_id,
        text=f"✅ *Вторая часть рассылки завершена!*\n\n"
             f"📤 Успешно: {success2_count}\n"
             f"❌ Ошибок: {fail2_count}\n\n"
             f"📊 *Итого:*\n"
             f"Первый кейс: +{success_count} / -{fail_count}\n"
             f"Второй кейс: +{success2_count} / -{fail2_count}",
        parse_mode="Markdown"
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

    application = Application.builder().token(TOKEN).build()
    application.post_init = set_commands

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("menu", menu))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("myid", myid_command))
    application.add_handler(CommandHandler("stat", stat_command))
    application.add_handler(CommandHandler("sendcases", send_cases_to_all))
    application.add_handler(CommandHandler("testcases", test_cases))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))

    print("🚀 Бот запущен и готов к работе!")
    print("⏱️ Тайминги: кружок → 17 сек → урок → 5 мин → подарок → 24 часа → промо-пост")
    print("⏱️ → 30 мин → первый кейс → 30 мин → второй кейс")
    print(f"👑 Админы ID: {ADMIN_IDS}")
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()