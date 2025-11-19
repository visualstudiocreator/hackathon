"""
Веб-приложение на FastAPI для обработки сценариев
"""

import os
import shutil
from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.responses import HTMLResponse, FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi import Request
from typing import Optional, List
import json
import uvicorn

from screenplay_processor import ScreenplayProcessor
import config


# Инициализация приложения
app = FastAPI(
    title="Препродакшн Анализатор Сценариев",
    description="Автоматизированный анализ сценариев для подготовки препродакшн-документации",
    version="1.0.0"
)

# Создаем директории
os.makedirs('static', exist_ok=True)
os.makedirs('templates', exist_ok=True)
os.makedirs(config.UPLOAD_FOLDER, exist_ok=True)
os.makedirs(config.OUTPUT_FOLDER, exist_ok=True)

# Настройка статических файлов и шаблонов
app.mount("/static", StaticFiles(directory="static"), name="static")
app.mount("/outputs", StaticFiles(directory=config.OUTPUT_FOLDER), name="outputs")
templates = Jinja2Templates(directory="templates")

# Инициализация процессора
processor = ScreenplayProcessor()


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    """Главная страница"""
    return templates.TemplateResponse("index.html", {
        "request": request,
        "presets": config.PRESETS
    })


@app.post("/api/upload")
async def upload_file(
    file: UploadFile = File(...),
    preset: str = Form("extended"),
    custom_columns: Optional[str] = Form(None),
    export_format: str = Form("xlsx")
):
    """
    Загружает и обрабатывает файл сценария
    
    Args:
        file: загружаемый файл
        preset: выбранный пресет
        custom_columns: пользовательские колонки (JSON строка)
        export_format: формат экспорта
    """
    try:
        # Проверяем расширение файла
        file_extension = os.path.splitext(file.filename)[1].lower()
        if file_extension not in config.SUPPORTED_FORMATS:
            raise HTTPException(
                status_code=400,
                detail=f"Неподдерживаемый формат файла. Поддерживаются: {', '.join(config.SUPPORTED_FORMATS)}"
            )
        
        # Сохраняем загруженный файл
        file_path = os.path.join(config.UPLOAD_FOLDER, file.filename)
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Обрабатываем пользовательские колонки
        columns = None
        if custom_columns:
            try:
                columns = json.loads(custom_columns)
                is_valid, error_msg = processor.validate_custom_columns(columns)
                if not is_valid:
                    raise HTTPException(status_code=400, detail=error_msg)
            except json.JSONDecodeError:
                raise HTTPException(status_code=400, detail="Некорректный формат пользовательских колонок")
        
        # Обрабатываем сценарий
        result = processor.process_screenplay(
            file_path=file_path,
            preset=preset,
            custom_columns=columns,
            export_format=export_format,
            output_filename=os.path.splitext(file.filename)[0]
        )
        
        if not result['success']:
            raise HTTPException(status_code=400, detail=result['error'])
        
        # Формируем ответ
        response_data = {
            'success': True,
            'scenes_count': result['scenes_count'],
            'pages': result['pages'],
            'processing_time': result['processing_time'],
            'output_file': os.path.basename(result['output_file']),
            'summary_file': os.path.basename(result['summary_file']),
            'download_url': f"/api/download/{os.path.basename(result['output_file'])}",
            'summary_download_url': f"/api/download/{os.path.basename(result['summary_file'])}"
        }
        
        # Удаляем загруженный файл
        os.remove(file_path)
        
        return JSONResponse(content=response_data)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка обработки: {str(e)}")


@app.get("/api/download/{filename}")
async def download_file(filename: str):
    """Скачивание обработанного файла"""
    file_path = os.path.join(config.OUTPUT_FOLDER, filename)
    
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Файл не найден")
    
    return FileResponse(
        path=file_path,
        filename=filename,
        media_type='application/octet-stream'
    )


@app.post("/api/preview")
async def preview_file(file: UploadFile = File(...)):
    """
    Возвращает превью первых сцен без полной обработки
    """
    try:
        # Сохраняем файл
        file_path = os.path.join(config.UPLOAD_FOLDER, file.filename)
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Получаем превью
        result = processor.get_scenes_preview(file_path, num_scenes=3)
        
        # Удаляем файл
        os.remove(file_path)
        
        if not result['success']:
            raise HTTPException(status_code=400, detail=result['error'])
        
        return JSONResponse(content=result)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка: {str(e)}")


@app.get("/api/presets")
async def get_presets():
    """Возвращает доступные пресеты"""
    return JSONResponse(content=config.PRESETS)


@app.get("/api/columns")
async def get_columns():
    """Возвращает все доступные колонки"""
    columns = processor.get_available_columns()
    return JSONResponse(content={"columns": columns})


@app.get("/health")
async def health_check():
    """Проверка работоспособности сервиса"""
    return {"status": "ok", "version": "1.0.0"}


if __name__ == "__main__":
    print("=" * 60)
    print("Препродакшн Анализатор Сценариев")
    print("=" * 60)
    print(f"Открывайте в браузере: http://localhost:8000")
    print("=" * 60)
    
    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )

