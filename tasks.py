import os

from celery import Celery
import pytesseract
from PIL import Image
from database import SessionLocal
import models # Импортируйте модели и сессию БД


app = Celery('tasks', broker='pyamqp://guest@localhost//')
#связь Celery и RabbitMQ через подключение Celery к URL-адресу RabbitMQ
@app.task
def process_document(doc_id, file_path):
    try:
        # Получаем абсолютный путь к файлу
        absolute_file_path = get_document_path(file_path)

        # Используем Tesseract OCR для извлечения текста
        image = Image.open(absolute_file_path)
        text = pytesseract.image_to_string(image)
        print(text)

        # Обрезаем текст до 150 символов, если он длиннее
        if len(text) > 150:
            text = text[:150]

        # Создаем новый объект Documents_text
        document_text = models.Documents_text(id_doc=doc_id, text=text)

        # Сохраняем объект в базу данных
        db = SessionLocal()
        db.add(document_text)
        db.commit()
        db.refresh(document_text)  # Получаем объект с ID после сохранения, если нужно
        db.close()
        return {"message": "Document processed successfully", "id": document_text.id}
    except Exception as e:
        db.close()
        raise e

# Функция для получения абсолютного пути к файлу
def get_document_path(file_path):
    absolute_file_path = os.path.abspath(file_path)
    return file_path