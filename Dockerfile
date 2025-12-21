# Используем официальный slim-образ Python 3.12
FROM python:3.12-slim

# Устанавливаем рабочую директорию в контейнере
WORKDIR /app

# Устанавливаем зависимости системы
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Копируем файл зависимостей в контейнер
COPY requirements.txt ./

# Устанавливаем зависимости Python
RUN pip install --no-cache-dir -r requirements.txt

# Копируем исходный код приложения в контейнер
COPY . .

# Определяем переменные окружения
ENV SECRET_KEY="django-insecure-#%jtrt_dqg*2!7xr#qyaie*58$caz&tk&fx5*i_lv0g(kw)&5_"
ENV CELERY_BROKER_URL="redis://localhost:6379/2"
ENV CELERY_BACKEND="redis://localhost:6379/2"

# Создаем директорию для медиафайлов
RUN mkdir -p /app/media

# Пробрасываем порт, который будет использовать Django
EXPOSE 8000

# Команда для запуска приложения
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "config.wsgi:application"]