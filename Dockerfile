# Используем официальный Python образ версии 3.11
FROM python:3.12-slim

# Устанавливаем рабочую директорию внутри контейнера
WORKDIR /app

COPY . /app/

# Устанавливаем зависимости
RUN pip install --no-cache-dir -r requirements.txt

# Указываем переменные окружения (если нужно)
ENV PYTHONUNBUFFERED=1

# Команда для запуска приложения
CMD ["python", "main.py"]
