FROM python:3.11-slim

WORKDIR /app

# Скопіювати залежності
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Скопіювати проект
COPY . .

# Відкрити порт
EXPOSE 8080

# Стандартна команда (можна перевизначати в docker-compose)
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]
