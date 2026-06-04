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

# Только второй кейс (Лиза)
CASE2_TEXT = (
    "<b>смонтировать рилс – это одно, а перестать бояться, что ты плохой монтажёр – совсем другое</b>🙂‍↕️\n\n"
    "ко мне на обучение пришла ученица Лиза (@elzavettta)\n\n"
    "<b>До обучения:</b>\n"
    "> // работала в сфере smm за небольшие деньги, чувствовала себя обесцененной\n"
    "> // ушла в монтаж, монтировала год для клиентов, но понимала, что недостаточно навыков\n"
    "> // не могла сказать себе и другим: «Я монтажёр, я могу сделать вам классные ролики», от этого выгорание, низкие чеки\n\n"
    "*🏁 до обучения:*\n"
    "▸ // уже полноценно работала монтажёром\n"
    "▸ // многие решения делала интуитивно\n"
    "▸ // доход был 50–70к в месяц\n"
    "▸ // не всегда понимала, как создаются анимационные эффекты\n"
    "▸ // не было уверенности в своих работах\n"
    "▸ // не делала горизонтальный формат\n"
    "▸ // потеря вдохновения и творческий кризис\n\n"
    "_зарабатывать на монтаже — не сложно, если понимать, как вообще формируется твой заработок_\n\n"
)

# Ссылки
SURVEY_URL = "https://docs.google.com/forms/d/e/1FAIpQLSeV3hbxukt2k-_9JVf0OyPPJf68ySNcsoB-kZF6NjdeBRDOgQ/viewform?usp=publish-editor"
VIDEO_URL = "https://www.youtube.com/watch?v=7q0tfS3NcJc&feature=youtu.be"

# Пути к файлам
VIDEO_NOTE_PATH = "video_notes/welcome.mp4"
LESSON_IMAGE_PATH = "images/lesson_preview.jpg"
GIFT_IMAGE_PATH = "images/gift_preview.jpg"
CASE2_IMAGE_PATH = "images/pic2.jpg"

# Настройки задержек (в секундах)
DELAY_AFTER_VIDEO_NOTE = 17  # 17 секунд до урока
DELAY_AFTER_LESSON = 1800  # 5 минут до подарка
DELAY_AFTER_GIFT = 86400  # 24 часа до промо-поста
DELAY_AFTER_GIFT_FOR_CASE2 = 1800  # 30 минут после подарка для второго кейса

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
        BotCommand("testcases", "🧪 Тестовая отправка кейса (только админу)"),
        BotCommand("sendcase2", "📨 Отправить второй кейс всем пользователям"),
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

    # Запускаем таймер для отправки второго кейса через 30 минут
    case2_key = f"case2_{chat_id}"
    if case2_key in user_tasks:
        if not user_tasks[case2_key].done():
            user_tasks[case2_key].cancel()

    user_tasks[case2_key] = asyncio.create_task(
        send_case2_to_new_user(chat_id, context)
    )


# --- Функция для отправки второго кейса новым пользователям ---
async def send_case2_to_new_user(chat_id: int, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Отправляет второй кейс новому пользователю через 30 минут после подарка"""
    await asyncio.sleep(DELAY_AFTER_GIFT_FOR_CASE2)

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

    print(f"📨 Второй кейс отправлен новому пользователю {chat_id} через 30 минут после подарка")


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


# --- ТЕСТОВАЯ КОМАНДА ДЛЯ ПРОВЕРКИ ---
async def test_cases(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Отправляет тестовый кейс только админу"""
    user_id = update.effective_user.id

    if not is_admin(user_id):
        await update.message.reply_text("⛔ Доступ запрещён!")
        return

    await update.message.reply_text("🧪 Тестовая отправка\n\nОтправляю второй кейс только вам...")

    try:
        with open(CASE2_IMAGE_PATH, 'rb') as photo:
            await update.message.reply_photo(
                photo=photo,
                caption=CASE2_TEXT,
                parse_mode="HTML"
            )
    except FileNotFoundError:
        await update.message.reply_text("❌ Фото pic2.jpg не найдено")
        await update.message.reply_text(CASE2_TEXT, parse_mode="HTML")

    await update.message.reply_text("✅ Готово!")


# --- КОМАНДА ДЛЯ РАССЫЛКИ ВТОРОГО КЕЙСА ВСЕМ ПОЛЬЗОВАТЕЛЯМ ---
async def send_case2_to_existing_users(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Отправляет второй кейс всем существующим пользователям (только админы)"""
    user_id = update.effective_user.id

    if not is_admin(user_id):
        await update.message.reply_text("⛔ *Доступ запрещён!*\nЭта команда только для администраторов.",
                                        parse_mode="Markdown")
        return

    users = load_users()

    if not users:
        await update.message.reply_text("📭 Нет пользователей для рассылки")
        return

    await update.message.reply_text(f"📢 Начинаю рассылку второго кейса {len(users)} пользователям...")

    success_count = 0
    fail_count = 0

    for user_id_str, user_data in users.items():
        uid = int(user_id_str)

        if is_admin(uid):
            continue

        try:
            with open(CASE2_IMAGE_PATH, 'rb') as photo:
                await context.bot.send_photo(
                    chat_id=uid,
                    photo=photo,
                    caption=CASE2_TEXT,
                    parse_mode="HTML"
                )

            success_count += 1
            print(f"✅ Второй кейс отправлен пользователю {user_data.get('first_name', uid)}")
            await asyncio.sleep(0.3)

        except Exception as e:
            fail_count += 1
            print(f"❌ Ошибка при отправке пользователю {uid}: {e}")

    await update.message.reply_text(
        f"✅ Рассылка второго кейса завершена!\n\n"
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

    application = Application.builder().token(TOKEN).build()
    application.post_init = set_commands

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("menu", menu))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("myid", myid_command))
    application.add_handler(CommandHandler("stat", stat_command))
    application.add_handler(CommandHandler("testcases", test_cases))
    application.add_handler(CommandHandler("sendcase2", send_case2_to_existing_users))

    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))

    print("🚀 Бот запущен и готов к работе!")
    print("⏱️ Тайминги: кружок → 17 сек → урок → 5 мин → подарок → 30 мин → второй кейс → 24 часа → промо-пост")
    print(f"👑 Админы ID: {ADMIN_IDS}")
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()