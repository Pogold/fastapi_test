# Используем минимальный образ Python
FROM python:3.12.7-slim

# Устанавливаем рабочую директорию
WORKDIR /app

# Устанавливаем системные зависимости
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Обновляем pip и устанавливаем зависимости для Python
RUN pip install --upgrade pip setuptools wheel

# Копируем файл зависимостей в контейнер
COPY requirements.txt .

# Устанавливаем зависимости Python (включая uvicorn)
RUN pip install --no-cache-dir -r requirements.txt uvicorn

# Копируем весь код в контейнер
COPY . .

# Делаем исполняемый файл uvicorn доступным в PATH
RUN ln -s /usr/local/bin/uvicorn /usr/bin/uvicorn

# Указываем порт
EXPOSE 8000

# Запускаем приложение с несколькими воркерами
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
