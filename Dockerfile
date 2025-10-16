FROM python:3.12.12-alpine

RUN apk add --no-cache python3-dev build-base

copy backend /app

WORKDIR /app

run pip install --no-cache-dir -r requirements.txt

CMD [ "fastapi", "run", "src/main.py" ]
