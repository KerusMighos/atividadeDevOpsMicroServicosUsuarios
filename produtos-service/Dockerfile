FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY produtos-service.py /app/produtos-service.py

CMD ["python", "produtos-service.py"]