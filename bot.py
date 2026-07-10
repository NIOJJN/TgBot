import asyncio
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

# --- НАСТРОЙКИ ---
BOT_TOKEN = "8964454118:AAEINlcrfoVwdvRd64kHriaAuD9RNdavUu4"
ADMIN_ID = 5457331962

# --- Инициализация ---
logging.basicConfig(level=logging.INFO)
bot = Bot(token=BOT_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)

# --- Состояния ---
class Form(StatesGroup):
    waiting_for_message = State()

# --- Клавиатуры ---
def get_main_keyboard():
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📝 Написать", callback_data="send_anonymous")],
        [InlineKeyboardButton(text="📖 Правила", callback_data="about")]
    ])
    return keyboard

def get_cancel_keyboard():
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔙 Назад", callback_data="cancel")]
    ])
    return keyboard

# --- Команды ---
@dp.message(Command("start"))
async def cmd_start(message: Message):
    await message.answer(
        "👋 Привет!\n\nЭто бот для связи.\nНапиши сюда всё, что хочешь сказать.",
        reply_markup=get_main_keyboard()
    )

@dp.message(Command("help"))
async def cmd_help(message: Message):
    await message.answer(
        "📌 Просто нажми 'Написать' и отправь сообщение.",
        reply_markup=get_main_keyboard()
    )

# --- Callback-запросы ---
@dp.callback_query(lambda c: c.data == "send_anonymous")
async def process_send_anonymous(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.edit_text(
        "✍️ Напиши своё сообщение:\n\nМожно отменить — нажми 'Назад'.",
        reply_markup=get_cancel_keyboard()
    )
    await state.set_state(Form.waiting_for_message)
    await callback.answer()

@dp.callback_query(lambda c: c.data == "cancel")
async def process_cancel(callback: types.CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.edit_text(
        "✅ Готово. Можешь написать ещё:",
        reply_markup=get_main_keyboard()
    )
    await callback.answer()

@dp.callback_query(lambda c: c.data == "about")
async def process_about(callback: types.CallbackQuery):
    await callback.message.edit_text(
        "📖 Бот для обратной связи.\nВсе сообщения приходят администратору.",
        reply_markup=get_main_keyboard()
    )
    await callback.answer()

# --- Обработчик сообщений ---
@dp.message(Form.waiting_for_message)
async def handle_anonymous_message(message: Message, state: FSMContext):
    try:
        if not message.text:
            await message.answer("❌ Напиши текст.")
            return

        user = message.from_user
        user_id = user.id
        first_name = user.first_name or "Без имени"
        last_name = user.last_name or ""
        username = f"@{user.username}" if user.username else "Нет username"
        full_name = f"{first_name} {last_name}".strip()

        admin_message = (
            f"📩 Сообщение\n"
            f"{'─' * 25}\n"
            f"👤 {full_name}\n"
            f"🆔 {user_id}\n"
            f"🔗 {username}\n"
            f"{'─' * 25}\n"
            f"{message.text}"
        )

        await bot.send_message(chat_id=ADMIN_ID, text=admin_message)

        await message.answer(
            "✅ Отправлено!",
            reply_markup=get_main_keyboard()
        )
        
        await state.clear()

    except Exception as e:
        logging.error(f"Ошибка: {e}")
        await message.answer(
            "❌ Ошибка. Попробуй позже.",
            reply_markup=get_main_keyboard()
        )
        await state.clear()

@dp.message(Command("stats"))
async def cmd_stats(message: Message):
    if message.from_user.id == ADMIN_ID:
        await message.answer("✅ Бот работает.")
    else:
        await message.answer(
            "📌 Нажми 'Написать', чтобы отправить сообщение.",
            reply_markup=get_main_keyboard()
        )

@dp.message()
async def handle_other_messages(message: Message):
    if message.from_user.id == ADMIN_ID:
        return
    
    await message.answer(
        "📌 Используй кнопки:",
        reply_markup=get_main_keyboard()
    )

# --- Запуск ---
async def main():
    print("✅ Бот запущен!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
