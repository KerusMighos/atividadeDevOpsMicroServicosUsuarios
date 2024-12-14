FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY user-service.py /app/user-service.py

CMD ["python", "user-service.py"]