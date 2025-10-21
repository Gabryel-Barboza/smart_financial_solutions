FROM python:3.12.12-slim-bookworm

# Instalar pacotes para Tesseract OCR
RUN apt-get update && apt-get install -y tesseract-ocr tesseract-ocr-por

WORKDIR /app

COPY backend/requirements.txt .

# Instalar dependências do Python
RUN pip install --no-cache-dir -r requirements.txt 

COPY backend .

CMD [ "fastapi", "run", "src/main.py" ]
