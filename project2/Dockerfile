# Dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копируем .env, main.py и запускаем
COPY .env .
COPY main.py .

CMD ["python", "main.py"]
EOF
