import asyncio
import os
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from dotenv import load_dotenv


load_dotenv()
TOKEN = os.getenv('BOT_TOKEN')
print(f"Токен: {TOKEN}")

bot = Bot(token=TOKEN)
dp = Dispatcher()



@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    """
    Это приветствие. Когда пользователь пишет /start,
    бот отвечает этим сообщением.
    """
    await message.answer(
        "🌟 **Добро пожаловать в NOOSPHERE!**\n\n"
        "Я бот, который видит скрытые слои реальности.\n"
        "Отправь мне фото, и я проанализирую его!\n\n"
        "_Пока я в разработке, но скоро научусь всему!_",
        parse_mode="Markdown"
    )



@dp.message(lambda message: message.photo)
async def handle_photo(message: types.Message):
    """
    Когда приходит фото, бот говорит, что обрабатывает,
    и через 3 секунды присылает заглушку.
    """

    processing_msg = await message.answer("🔄 **Анализирую изображение...**")
    
  
    await asyncio.sleep(3)
    

    await processing_msg.delete()
    

    await message.answer(
        "✅ **Анализ завершен!**\n\n"
        "🔬 Научный слой: найдено 5 объектов\n"
        "🌟 Энергетический слой: аура сине-зеленая\n"
        "🧠 Психологический слой: вы фокусируетесь на деталях\n\n"
        "_Полная версия будет доступна скоро!_"
    )


@dp.message()
async def handle_other(message: types.Message):
    """
    Если прислали не фото, говорим, что нужна фотография.
    """
    await message.answer("📸 Пожалуйста, отправьте фотографию для анализа!")



async def main():
    """
    Запускаем бота и выводим сообщение в консоль.
    """
    print("🚀 Бот NOOSPHERE запущен и готов к работе!")
    print("📸 Отправьте фото своему боту в Telegram!")
    
  
    await dp.start_polling(bot)



if __name__ == "__main__":
    asyncio.run(main())