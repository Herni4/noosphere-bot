import asyncio
import os
import io
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import BufferedInputFile
from dotenv import load_dotenv
import logging

# Настраиваем логирование (чтобы видеть ошибки)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Загружаем токен
load_dotenv()
TOKEN = os.getenv('BOT_TOKEN')

# Создаем бота
bot = Bot(token=TOKEN)
dp = Dispatcher()

# ИМПОРТИРУЕМ АНАЛИЗАТОРЫ
from analyzers.scientific import ScientificAnalyzer
from analyzers.energy import EnergyAnalyzer

# СОЗДАЕМ АНАЛИЗАТОРЫ (один раз при запуске)
print("🚀 Запуск NOOSPHERE бота...")
scientific = ScientificAnalyzer()
energy = EnergyAnalyzer()
print("✅ Все анализаторы загружены!")

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    """Приветствие"""
    await message.answer(
        "🌌 **Добро пожаловать в NOOSPHERE!**\n\n"
        "Я бот, который видит скрытые слои реальности.\n\n"
        "📸 **Отправь мне любое фото, и я проанализирую его через:**\n"
        "🔬 Научный слой (объекты, текст, цвета)\n"
        "🌟 Энергетический слой (аура, биополе)\n\n"
        "_Другие слои скоро добавятся..._",
        parse_mode="Markdown"
    )

@dp.message(lambda message: message.photo)
async def handle_photo(message: types.Message):
    """Обработка фотографий"""
    
    # Сообщаем о начале анализа
    status_msg = await message.answer("🔄 **Анализирую изображение...**\n\n🔬 Научный слой: обработка")
    
    try:
        # Скачиваем фото
        photo = message.photo[-1]  # берем самое качественное
        photo_file = await bot.download(photo)
        photo_bytes = photo_file.getvalue()
        
        # ШАГ 1: Научный анализ
        await status_msg.edit_text("🔄 **Анализирую изображение...**\n\n🔬 Научный слой: найдено объектов...")
        
        # Запускаем научный анализ
        loop = asyncio.get_event_loop()
        scientific_results = await loop.run_in_executor(
            None, 
            scientific.analyze, 
            photo_bytes
        )
        
        # ШАГ 2: Энергетический анализ
        await status_msg.edit_text("🔄 **Анализирую изображение...**\n\n🌟 Энергетический слой: создание ауры...")
        
        energy_results = await loop.run_in_executor(
            None,
            energy.analyze,
            photo_bytes
        )
        
        # Удаляем сообщение о прогрессе
        await status_msg.delete()
        
        # Формируем текстовый отчет
        report = "🔬 **НАУЧНЫЙ СЛОЙ:**\n"
        
        if scientific_results['objects']:
            report += "Найденные объекты:\n"
            # Показываем только первые 5 объектов
            for obj in scientific_results['objects'][:5]:
                report += f"• {obj['name']} ({obj['confidence']:.2%})\n"
        else:
            report += "Объекты не найдены\n"
        
        if scientific_results['text']:
            report += f"\n📝 Текст на фото:\n"
            for txt in scientific_results['text'][:3]:
                report += f"• {txt['text']}\n"
        
        report += f"\n🌟 **ЭНЕРГЕТИЧЕСКИЙ СЛОЙ:**\n"
        report += f"• Доминирующий цвет: {energy_results['dominant_color']}\n"
        report += f"• Значение: {energy_results['meaning']}\n"
        report += f"• Уровень энергии: {energy_results['energy_level']:.1%}\n"
        
        # Отправляем изображение с рамками
        if scientific_results['image_with_boxes']:
            img_byte_arr = io.BytesIO()
            scientific_results['image_with_boxes'].save(img_byte_arr, format='PNG')
            img_byte_arr.seek(0)
            
            await message.answer_photo(
                BufferedInputFile(img_byte_arr.getvalue(), filename="analysis.png"),
                caption=report,
                parse_mode="Markdown"
            )
        
        # Отправляем "энергетическое" изображение
        if energy_results['aura_image']:
            aura_byte_arr = io.BytesIO()
            energy_results['aura_image'].save(aura_byte_arr, format='PNG')
            aura_byte_arr.seek(0)
            
            await message.answer_photo(
                BufferedInputFile(aura_byte_arr.getvalue(), filename="aura.png"),
                caption="🌟 **Энергетическое поле (аура)**",
                parse_mode="Markdown"
            )
            
    except Exception as e:
        logger.error(f"Ошибка: {e}")
        await status_msg.delete()
        await message.answer(
            f"❌ Произошла ошибка при анализе.\n"
            f"Попробуйте другое фото или повторите позже."
        )

@dp.message()
async def handle_other(message: types.Message):
    """Обработка не-фото"""
    await message.answer("📸 Пожалуйста, отправьте фотографию для анализа!")

async def main():
    """Запуск бота"""
    print("🚀 Бот NOOSPHERE запущен и готов к работе!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())