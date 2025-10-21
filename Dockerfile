FROM python:3.12.12-alpine

# Instalar pacotes para compilação e Tesseract OCR
RUN apk add --no-cache python3-dev build-base tesseract-ocr tesseract-ocr-dev tesseract-ocr-data-por

COPY backend/requirements.txt /app

WORKDIR /app

# Instalar dependências do Python
run pip install --no-cache-dir -r requirements.txt

# Limpar pacotes de build para reduzir o tamanho final da imagem
RUN apk del --no-cache build-base

COPY backend .

CMD [ "fastapi", "run", "src/main.py" ]
