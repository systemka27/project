from datetime import datetime
from fastapi import FastAPI, File, UploadFile, HTTPException
from database import SessionLocal, engine
import models
import uvicorn
import os
from fastapi.responses import JSONResponse
from werkzeug.utils import secure_filename
import shutil
from config import DOC_PATH
from tasks import process_document

app = FastAPI()

models.Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/")
def root():
    return {"message": "Hello World"}

UPLOAD_FOLDER = 'documents'

@app.post("/upload_doc")
async def upload_doc(file: UploadFile = File(...)):
    filename = secure_filename(file.filename)
    file_path = os.path.join(UPLOAD_FOLDER, filename)

    # Сохранение файла
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Добавление записи в базу данных
    db = SessionLocal()
    try:
        new_doc = models.Documents(path=DOC_PATH + file.filename, date=datetime.now())
        db.add(new_doc)
        db.commit()
        db.refresh(new_doc)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        db.close()

    return JSONResponse(status_code=200, content={"message": "Document uploaded successfully", "filename": filename})

@app.delete("/doc_delete")
async def doc_delete(id):
    db = SessionLocal()
    try:
        pic = db.get(models.Documents, id)
        print(f"{pic.id} - {pic.date}")

        db.delete(pic)  # удаляем объект
        db.commit()  # сохраняем изменения
    except AttributeError as a:
        raise HTTPException(status_code=500, detail=str(a))
    finally:
        db.close()

def get_document_path(relative_path):
    # Получаем абсолютный путь к каталогу, где находится файл main.py
    directory_of_main = os.path.dirname(os.path.abspath(__file__))
    # Соединяем путь к каталогу с относительным путем файла
    absolute_file_path = os.path.join(directory_of_main, relative_path)
    return absolute_file_path

@app.post("/doc_analyse")
async def doc_analyse(id_doc: int, file_path: str):
    try:
        # Вызываем задачу Celery асинхронно
        task = process_document.delay(id_doc, file_path)
        return {"message": "Document processing started", "task_id": task.id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/get_text")
def get_text(doc_id: int):
    db = SessionLocal()
    document_text = db.query(models.Documents_text).filter(models.Documents_text.id == doc_id).first()
    db.close()

    if document_text:
        return {"text": document_text.text}
    else:
        return {"message": "Document not found"}


if __name__ == '__main__':
    uvicorn.run(app)



