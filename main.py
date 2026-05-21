import os
import asyncio
from dotenv import load_dotenv
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, BotCommand
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes, MessageHandler, filters

# Загружаем переменные окружения из .env файла
load_dotenv()

# Токен бота из переменной окружения
TOKEN = os.getenv("BOT_TOKEN")

# --- Константы с текстами и ссылками ---

# Приветственное сообщение (первое)
WELCOME_MESSAGE = (
    "*Что умеет этот бот?*\n\n"
    "Привет🤍 Меня зовут Настя, ты точно видел мой монтаж у себя в ленте! \n\n"
    "Если ты давно мечтаешь стать востребованным монтажёром или улучшить свои навыки - "
    "ты попал туда, куда нужно🪩 \n\n"
    "Здесь тебя ждёт полезный урок «5 шагов, чтобы стать востребованным монтажёром уже этим летом»\n\n"
    "Жми *«Вперед»*, чтобы быстрее начать🙂‍↕️"
)

# Текст с уроком (после кружка)
LESSON_DESCRIPTION_TEXT = (
    "*Ты готооов с удовольствием использовать летнее время по максимуму и начать заниматься любимым делом????🛼*\n\n"
    "В этом уроке ты узнаешь:\n\n"
    "📌 *Кто такой монтажёр?* Разберём, какие задачи и вопросы решает\n\n"
    "📌 *Изучим виды монтажа*, поговорим про горизонтальный и вертикальный монтаж\n\n"
    "📌 А также я научу рассчитывать вас свою заработную плату в месяц🤫\n\n"
    "📌 *Самый главный вопрос🍽️*\n"
    "Где искать клиентов? Разберем, какие способы работают лучше всего\n\n"
    "📌 *Разберём, как создавать портфолио*, откуда брать работы, чтобы привлекать клиентов\n\n"
    "📌 *И один из самых важных аспектов*, который поможет выделяться среди других *«КРЕАТИВ»*🪩\n\n"
    "Обязательно обсудим, что такое креатив, откуда его брать и почему за помощью обращаются именно к монтажёру\n\n"
    "🧁 *Обязательно смотри урок до конца, ведь там тебя ждёт ПОДАРОК*, "
    "который поможет сдвинуться с мёртвой точки и начать расти в сфере монтажа\n\n"
    "👇 *Жми на кнопку ниже и смотри урок* 🙂‍↕️"
)

# Текст "Как успехи?" (через 30 минут после урока)
HOW_ARE_YOU_TEXT = (
    "🤍 *Как успехи?*\n\n"
    "Успел посмотреть урок? Если остались вопросы — смело задавай!\n\n"
    "И помни: главное — не бояться начинать. У тебя всё получится! 💪"
)

# Ссылка на видео (YouTube)
VIDEO_URL = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"

# Путь к кружку (video note)
VIDEO_NOTE_PATH = "video_notes/welcome.mp4"

# Путь к приветственной картинке (первое сообщение)
WELCOME_IMAGE_PATH = "images/welcome.jpg"

# Путь к картинке с описанием урока
LESSON_IMAGE_PATH = "images/lesson_preview.jpg"

# Настройки задержек (в секундах)
DELAY_AFTER_VIDEO_NOTE = 60  # 1 минута до текста с уроком
DELAY_AFTER_LESSON = 1800  # 30 минут до "Как успехи?"

# Хранилище задач для отложенных сообщений
user_tasks = {}


# --- Функция для установки команд бота в меню ---
async def set_commands(application: Application) -> None:
    """Устанавливает команды в меню бота"""
    commands = [
        BotCommand("start", "Начать заново"),
        BotCommand("menu", "Показать главное меню"),
        BotCommand("help", "Помощь"),
    ]
    await application.bot.set_my_commands(commands)
    print("✅ Команды бота установлены")


# --- Функция для отправки урока с задержкой ---
async def send_lesson_with_delay(chat_id: int, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Отправляет текст с уроком через указанную задержку"""
    await asyncio.sleep(DELAY_AFTER_VIDEO_NOTE)

    # Кнопка-ссылка на YouTube (прямо ведёт на видео)
    keyboard = [[InlineKeyboardButton("🎬 Смотреть урок на YouTube", url=VIDEO_URL)]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    # Отправляем картинку с текстом и кнопкой-ссылкой
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
        # Если картинки нет — отправляем только текст с кнопкой
        await context.bot.send_message(
            chat_id=chat_id,
            text=LESSON_DESCRIPTION_TEXT,
            parse_mode="Markdown",
            reply_markup=reply_markup
        )

    # Запускаем таймер для "Как успехи?" (через 30 минут)
    if chat_id in user_tasks:
        # Отменяем старую задачу, если есть
        if not user_tasks[chat_id].done():
            user_tasks[chat_id].cancel()

    user_tasks[chat_id] = asyncio.create_task(
        send_how_are_you_with_delay(chat_id, context)
    )


# --- Функция для отправки "Как успехи?" с задержкой ---
async def send_how_are_you_with_delay(chat_id: int, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Отправляет сообщение "Как успехи?" через 30 минут"""
    await asyncio.sleep(DELAY_AFTER_LESSON)

    await context.bot.send_message(
        chat_id=chat_id,
        text=HOW_ARE_YOU_TEXT,
        parse_mode="Markdown"
    )


# --- Команда /start ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Отправляет приветственное сообщение с кнопкой «Вперед»"""
    user = update.effective_user
    user_id = user.id
    chat_id = update.effective_chat.id

    # Отменяем предыдущие задачи, если они есть
    if user_id in user_tasks:
        if not user_tasks[user_id].done():
            user_tasks[user_id].cancel()
        del user_tasks[user_id]

    # Сбрасываем состояние пользователя
    context.user_data["state"] = "start"

    # Кнопка «Вперед»
    keyboard = [[InlineKeyboardButton("👉 Вперед", callback_data=f"forward_menu")]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    # Пытаемся отправить с картинкой, если есть
    try:
        with open(WELCOME_IMAGE_PATH, 'rb') as photo:
            await update.message.reply_photo(
                photo=photo,
                caption=WELCOME_MESSAGE,
                parse_mode="Markdown",
                reply_markup=reply_markup
            )
    except FileNotFoundError:
        # Если картинки нет — отправляем только текст
        await update.message.reply_text(
            WELCOME_MESSAGE,
            parse_mode="Markdown",
            reply_markup=reply_markup
        )


# --- Обработчик нажатия на кнопку «Вперед» ---
async def forward_menu_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """После нажатия «Вперед» отправляем кружок и запускаем таймер"""
    query = update.callback_query
    user_id = query.from_user.id
    chat_id = query.message.chat_id
    await query.answer()

    context.user_data["state"] = "video_note_sent"

    # Отправляем кружок (video note)
    try:
        with open(VIDEO_NOTE_PATH, 'rb') as video_note:
            await query.message.reply_video_note(
                video_note=video_note,
                duration=30
            )
    except FileNotFoundError:
        print("⚠️ Кружок не найден, продолжаем без него")
        await query.message.reply_text("🎬 *Подготавливаю урок...*", parse_mode="Markdown")

    # Запускаем таймер для отправки урока через 1 минуту
    if user_id in user_tasks:
        if not user_tasks[user_id].done():
            user_tasks[user_id].cancel()

    user_tasks[user_id] = asyncio.create_task(
        send_lesson_with_delay(chat_id, context)
    )


# --- Команда /menu ---
async def menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Показывает главное меню с кнопкой-ссылкой на урок"""
    # Кнопка-ссылка на YouTube
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
        "/start - Начать заново\n"
        "/menu - Показать главное меню\n"
        "/help - Показать эту справку\n\n"
        "Просто нажимай на кнопки для навигации!"
    )
    await update.message.reply_text(help_text, parse_mode="Markdown")


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

    # Создаём приложение
    application = Application.builder().token(TOKEN).build()

    # Устанавливаем команды меню после запуска
    application.post_init = set_commands

    # Регистрируем команды
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("menu", menu))
    application.add_handler(CommandHandler("help", help_command))

    # Регистрируем обработчики callback-кнопок
    application.add_handler(CallbackQueryHandler(forward_menu_callback, pattern="forward_menu"))

    # Обработчик для любых других сообщений
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))

    # Запускаем бота
    print("🚀 Бот запущен и готов к работе!")
    print("📱 Проверь бота в Telegram")
    print("⏱️ Тайминги: кружок → 1 минута → урок (с кнопкой-ссылкой) → 30 минут → 'Как успехи?'")
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()