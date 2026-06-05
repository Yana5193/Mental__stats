FROM python:3.11-slim

WORKDIR /app

RUN pip install --no-cache-dir fastapi==0.136.1 uvicorn==0.46.0 sqlalchemy==2.0.49

COPY . /app

EXPOSE 8002
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8002"]