import os
import logging
from typing import Dict, Any
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command, CommandObject
from aiogram.types import (
    KeyboardButton, 
    ReplyKeyboardMarkup, 
    InlineKeyboardButton, 
    InlineKeyboardMarkup,
    Message,
    FSInputFile,
    KeyboardButtonPollType,
    ReplyKeyboardRemove
)
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.enums import ParseMode
from dotenv import load_dotenv

# Загрузка переменных окружения
load_dotenv()
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

if not TOKEN:
    raise ValueError("Не задан токен бота. Создайте файл .env и добавьте в него TELEGRAM_BOT_TOKEN=your_token_here")

# Инициализация бота и диспетчера
bot = Bot(token=TOKEN)
dp = Dispatcher()

# Данные о городах (в реальном приложении лучше хранить в БД)
cities_data = {
    "moscow": {
        "name": "Москва",
        "description": "Столица России, город федерального значения",
        "attractions": ["Красная площадь", "Третьяковская галерея", "Парк Горького"],
        "food": ["Московские пончики", "Селёдка под шубой", "Бефстроганов"],
    },
    "spb": {
        "name": "Санкт-Петербург",
        "description": "Культурная столица России",
        "attractions": ["Эрмитаж", "Петергоф", "Исаакиевский собор"],
        "food": ["Корюшка", "Пышки", "Ленинградский рассольник"],
    },
}

def get_main_keyboard() -> ReplyKeyboardMarkup:
    """Создаёт расширенную основную клавиатуру"""
    keyboard = [
        [KeyboardButton(text="🏰 Выбрать город")],
        [
            KeyboardButton(text="📍 Отправить локацию", request_location=True),
            KeyboardButton(text="📱 Отправить контакт", request_contact=True)
        ],
        [KeyboardButton(text="📊 Создать опрос", request_poll=KeyboardButtonPollType())],
        [KeyboardButton(text="ℹ️ О боте")],
    ]
    return ReplyKeyboardMarkup(
        keyboard=keyboard,
        resize_keyboard=True,
        input_field_placeholder="Выберите действие"
    )

def get_cities_keyboard() -> InlineKeyboardMarkup:
    """Создаёт клавиатуру с городами и дополнительными действиями"""
    builder = InlineKeyboardBuilder()
    for city_id, city_data in cities_data.items():
        builder.button(
            text=city_data["name"], 
            callback_data=f"city_{city_id}"
        )
    # Добавляем кнопку со ссылкой
    builder.button(
        text="🔍 Подробнее о городах", 
        url="https://ru.wikipedia.org/wiki/Города_России"
    )
    builder.button(
        text="📱 Поделиться ботом",
        switch_inline_query="Классный бот-гид по городам!"
    )
    builder.adjust(1)
    return builder.as_markup()

def get_city_keyboard(city_id: str) -> InlineKeyboardMarkup:
    """Создаёт расширенную клавиатуру для конкретного города"""
    builder = InlineKeyboardBuilder()
    builder.button(text="🏛 Достопримечательности", callback_data=f"attractions_{city_id}")
    builder.button(text="🍽 Местная кухня", callback_data=f"food_{city_id}")
    builder.button(text="📸 Фото города", callback_data=f"photo_{city_id}")
    builder.button(text="📝 Оставить отзыв", callback_data=f"review_{city_id}")
    builder.button(text="◀️ Назад к списку городов", callback_data="show_cities")
    builder.adjust(1)
    return builder.as_markup()

@dp.message(Command("start"))
async def cmd_start(message: Message):
    await message.answer(
        "👋 Привет! Я бот-гид по городам России. Для показа основных возможностей telegram\n"
        "Выберите город, чтобы узнать о нём подробнее:",
        reply_markup=get_main_keyboard()
    )

@dp.message(Command("help"))
async def cmd_help(message: Message):
    help_text = """
*Доступные команды:*
/start - Начать работу с ботом
/help - Показать это сообщение
/cities - Список городов
/hide - Скрыть клавиатуру
/format - Примеры форматирования

*Дополнительные возможности:*
• Отправка локации
• Создание опросов
• Веб-приложение
• Отправка контакта
• Форматированные сообщения
    """
    await message.answer(help_text, parse_mode=ParseMode.MARKDOWN)

@dp.message(Command("format"))
async def cmd_format(message: Message):
    format_text = """
*Как форматировать текст в Telegram:*

1️⃣ *Жирный текст*
Используйте: `*текст*`

2️⃣ _Курсивный текст_
Используйте: `_текст_`

3️⃣ __Подчёркнутый текст__
Используйте: `__текст__`

4️⃣ ~Зачёркнутый текст~
Используйте: `~текст~`

5️⃣ ||Спойлер||
Используйте: `||текст||`

6️⃣ `Моноширинный текст`
Используйте: \\`текст\\`

7️⃣ Блок кода:
```python
def hello():
    print('Hello!')
```
Используйте: \\`\\`\\`язык
ваш код
\\`\\`\\`

8️⃣ [Ссылка](https://telegram.org)
Используйте: `[текст ссылки](url)`

💡 *Комбинирование стилей:*
Можно *_комбинировать_* разные __*стили*__ форматирования

⚠️ *Важно:*
• Если нужно показать символ форматирования как текст, используйте \\ перед ним
• Некоторые символы нужно экранировать: \\. , ! [ ] ( ) { } > # + - = | { } ~ $
    """
    await message.answer(format_text, parse_mode=ParseMode.MARKDOWN_V2)

@dp.message(Command("hide"))
async def cmd_hide_keyboard(message: Message):
    await message.answer(
        "Клавиатура скрыта. Используйте /start чтобы показать её снова.",
        reply_markup=ReplyKeyboardRemove()
    )

@dp.message(F.location)
async def handle_location(message: Message):
    await message.answer(
        f"📍 Получены координаты:\nШирота: {message.location.latitude}\nДолгота: {message.location.longitude}"
    )

@dp.message(F.contact)
async def handle_contact(message: Message):
    await message.answer(
        f"📱 Получен контакт:\nИмя: {message.contact.first_name}\nТелефон: {message.contact.phone_number}"
    )

@dp.message(F.poll)
async def handle_poll(message: Message):
    await message.answer("📊 Опрос создан!")

@dp.callback_query(F.data.startswith("photo_"))
async def show_city_photo(callback: types.CallbackQuery):
    city_id = callback.data.split("_")[1]
    city = cities_data[city_id]
    
    # Здесь можно отправить реальное фото города
    await callback.message.answer_photo(
        FSInputFile("path_to_photo.jpg") if os.path.exists("path_to_photo.jpg") else "https://via.placeholder.com/400x300",
        caption=f"📸 Фото города {city['name']}"
    )

@dp.callback_query(F.data.startswith("review_"))
async def start_review(callback: types.CallbackQuery):
    city_id = callback.data.split("_")[1]
    city = cities_data[city_id]
    
    await callback.message.answer(
        f"📝 Оставьте свой отзыв о городе {city['name']}.\n"
        "Просто отправьте сообщение в ответ.",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[[
            InlineKeyboardButton(text="❌ Отменить", callback_data="cancel_review")
        ]])
    )

@dp.message(F.text == "🏰 Выбрать город")
async def show_cities(message: Message):
    await message.answer(
        "Выберите город для просмотра информации:",
        reply_markup=get_cities_keyboard()
    )

@dp.message(F.text == "ℹ️ О боте")
async def about_bot(message: Message):
    await message.answer(
        "🤖 Я бот-гид по городам России.\n"
        "Я могу рассказать вам о разных городах, их достопримечательностях и местной кухне.\n"
        "Используйте кнопки меню для навигации.",
        reply_markup=get_main_keyboard()
    )

@dp.callback_query(F.data.startswith("city_"))
async def show_city_info(callback: types.CallbackQuery):
    city_id = callback.data.split("_")[1]
    city = cities_data[city_id]
    
    await callback.message.edit_text(
        f"🏰 {city['name']}\n\n"
        f"{city['description']}\n\n"
        "Выберите, что вас интересует:",
        reply_markup=get_city_keyboard(city_id)
    )

@dp.callback_query(F.data.startswith("attractions_"))
async def show_attractions(callback: types.CallbackQuery):
    city_id = callback.data.split("_")[1]
    city = cities_data[city_id]
    
    attractions_text = "\n• ".join([""] + city["attractions"])
    await callback.message.edit_text(
        f"🏛 Достопримечательности {city['name']}:{attractions_text}\n\n"
        "Выберите другой раздел:",
        reply_markup=get_city_keyboard(city_id)
    )

@dp.callback_query(F.data.startswith("food_"))
async def show_food(callback: types.CallbackQuery):
    city_id = callback.data.split("_")[1]
    city = cities_data[city_id]
    
    food_text = "\n• ".join([""] + city["food"])
    await callback.message.edit_text(
        f"🍽 Местная кухня {city['name']}:{food_text}\n\n"
        "Выберите другой раздел:",
        reply_markup=get_city_keyboard(city_id)
    )

@dp.callback_query(F.data == "show_cities")
async def back_to_cities(callback: types.CallbackQuery):
    await callback.message.edit_text(
        "Выберите город для просмотра информации:",
        reply_markup=get_cities_keyboard()
    )

@dp.message(Command("cities"))
async def cmd_cities(message: Message):
    await message.answer(
        "🏰 Список доступных городов:",
        reply_markup=get_cities_keyboard()
    )

async def main():
    logging.basicConfig(level=logging.INFO)
    
    # Установка команд бота
    await bot.set_my_commands([
        types.BotCommand(command="start", description="Запустить бота"),
        types.BotCommand(command="help", description="Показать справку"),
        types.BotCommand(command="cities", description="Список городов"),
        types.BotCommand(command="hide", description="Скрыть клавиатуру"),
        types.BotCommand(command="format", description="Примеры форматирования")
    ])
    
    await dp.start_polling(bot)

if __name__ == "__main__":
    import asyncio
    asyncio.run(main()) 