# scientific.py
# Этот анализатор находит объекты на фотографии

import io
import cv2  # OpenCV - библиотека для работы с изображениями
import numpy as np  # numpy для математических операций
from PIL import Image, ImageDraw, ImageFont  # PIL для работы с картинками
from ultralytics import YOLO  # YOLO - нейросеть для поиска объектов

class ScientificAnalyzer:
    """
    Класс для научного анализа изображений.
    Умеет находить объекты, текст и анализировать цвета.
    """
    
    def __init__(self):
        """
        Конструктор - запускается при создании анализатора.
        Здесь мы загружаем нейросети.
        """
        print("🔬 Загружаю научный анализатор...")
        
        # Загружаем YOLO - нейросеть для поиска объектов
        # YOLO (You Only Look Once) - очень быстрая и точная сеть
        self.model = YOLO('yolov8n.pt')  # yolov8n - легкая версия (n = nano)
        
        # Пытаемся загрузить OCR для распознавания текста
        try:
            import easyocr
            self.reader = easyocr.Reader(['ru', 'en'])  # русский и английский
            self.has_ocr = True
        except:
            print("⚠️ OCR не загружен, продолжаем без распознавания текста")
            self.has_ocr = False
        
        print("✅ Научный анализатор готов!")
    
    def analyze(self, image_bytes):
        """
        Главный метод анализа.
        Принимает байты изображения, возвращает результаты.
        """
        # 1. Конвертируем байты в изображение, понятное OpenCV
        # Открываем изображение из байтов
        pil_image = Image.open(io.BytesIO(image_bytes))
        # Конвертируем PIL в numpy массив (так работает OpenCV)
        img_numpy = np.array(pil_image)
        # OpenCV использует BGR вместо RGB, конвертируем
        img_cv = cv2.cvtColor(img_numpy, cv2.COLOR_RGB2BGR)
        
        results = {
            'objects': [],      # найденные объекты
            'text': [],         # найденный текст
            'colors': [],       # основные цвета
            'image_with_boxes': None  # изображение с рамками
        }
        
        # 2. Ищем объекты с помощью YOLO
        yolo_results = self.model(img_cv)  # прогоняем через нейросеть
        
        # Копируем изображение, чтобы рисовать на нем рамки
        img_with_boxes = img_cv.copy()
        
        # Перебираем все найденные объекты
        for r in yolo_results:
            for box in r.boxes:
                # Получаем информацию о объекте
                class_id = int(box.cls[0])  # ID класса (например, 0 = человек)
                confidence = float(box.conf[0])  # уверенность (0.95 = 95%)
                name = self.model.names[class_id]  # название класса (переводим ID в текст)
                
                # Координаты рамки (x1,y1 - левый верхний, x2,y2 - правый нижний)
                x1, y1, x2, y2 = box.xyxy[0].tolist()
                
                # Сохраняем объект
                results['objects'].append({
                    'name': name,
                    'confidence': confidence,
                    'bbox': [x1, y1, x2, y2]  # bounding box
                })
                
                # Рисуем зеленую рамку
                cv2.rectangle(
                    img_with_boxes, 
                    (int(x1), int(y1)), 
                    (int(x2), int(y2)), 
                    (0, 255, 0),  # зеленый цвет в BGR
                    2  # толщина линии
                )
                
                # Подписываем объект
                cv2.putText(
                    img_with_boxes,
                    f"{name} {confidence:.2f}",
                    (int(x1), int(y1) - 10),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.5,
                    (0, 255, 0),
                    2
                )
        
        # Конвертируем обратно в RGB для сохранения
        img_with_boxes_rgb = cv2.cvtColor(img_with_boxes, cv2.COLOR_BGR2RGB)
        results['image_with_boxes'] = Image.fromarray(img_with_boxes_rgb)
        
        # 3. Ищем текст на фото (если есть OCR)
        if self.has_ocr:
            try:
                ocr_results = self.reader.readtext(img_cv)
                results['text'] = [
                    {
                        'text': text, 
                        'confidence': conf
                    } 
                    for (bbox, text, conf) in ocr_results
                ]
            except Exception as e:
                print(f"Ошибка OCR: {e}")
        
        # 4. Анализируем цвета (находим 5 основных цветов)
        try:
            # Уменьшаем изображение для скорости
            small_img = cv2.resize(img_cv, (100, 100))
            pixels = small_img.reshape(-1, 3)
            
            # Используем KMeans для кластеризации цветов
            from sklearn.cluster import KMeans
            kmeans = KMeans(n_clusters=5, random_state=42, n_init=10)
            kmeans.fit(pixels)
            
            # Получаем центры кластеров (основные цвета)
            colors = kmeans.cluster_centers_.astype(int)
            results['colors'] = colors.tolist()
        except:
            # Если нет sklearn, пропускаем
            pass
        
        return results