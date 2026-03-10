# energy.py
# Этот анализатор создает "энергетическую" карту изображения

import numpy as np
from PIL import Image, ImageFilter
import io
import cv2

class EnergyAnalyzer:
    """
    Анализатор энергетического поля (игровой, не воспринимайте всерьез!)
    Создает красивые градиенты на основе цветов изображения.
    """
    
    def __init__(self):
        print("🌟 Загружаю энергетический анализатор...")
        print("✅ Энергетический анализатор готов!")
    
    def analyze(self, image_bytes):
        """
        Создает "энергетическую" карту изображения
        """
        # Открываем изображение
        pil_image = Image.open(io.BytesIO(image_bytes))
        
        # Конвертируем в массив numpy
        img_array = np.array(pil_image)
        
        # Применяем размытие для создания эффекта "свечения"
        blurred = cv2.GaussianBlur(img_array, (25, 25), 0)
        
        # Анализируем доминирующие цвета
        avg_color = np.mean(img_array, axis=(0, 1))
        
        # Создаем "энергетическое" изображение
        h, w = img_array.shape[:2]
        
        # Создаем градиент от центра к краям
        y, x = np.ogrid[:h, :w]
        center_y, center_x = h // 2, w // 2
        
        # Расстояние от центра
        distance_from_center = np.sqrt((x - center_x)**2 + (y - center_y)**2)
        max_distance = np.sqrt(center_x**2 + center_y**2)
        
        # Нормализуем расстояние
        gradient = 1 - (distance_from_center / max_distance)
        gradient = np.stack([gradient] * 3, axis=-1)
        
        # Создаем "ауру" - смешиваем размытое изображение с градиентом
        aura = np.ones_like(img_array) * avg_color * gradient
        aura = aura.astype(np.uint8)
        
        # Смешиваем оригинал с аурой
        result = cv2.addWeighted(img_array, 0.5, aura, 0.5, 0)
        
        # Интерпретация
        avg_r, avg_g, avg_b = avg_color
        
        # Определяем преобладающий цвет
        if avg_r > avg_g and avg_r > avg_b:
            dominant = "красный"
            meaning = "активность, энергия, страсть"
        elif avg_g > avg_r and avg_g > avg_b:
            dominant = "зеленый"
            meaning = "гармония, рост, исцеление"
        elif avg_b > avg_r and avg_b > avg_g:
            dominant = "синий"
            meaning = "спокойствие, интуиция, мудрость"
        else:
            dominant = "смешанный"
            meaning = "баланс и многогранность"
        
        return {
            'aura_image': Image.fromarray(result),
            'dominant_color': dominant,
            'meaning': meaning,
            'energy_level': np.random.uniform(0.5, 1.0)  # случайно для демо
        }