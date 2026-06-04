FROM python:3.11-slim

WORKDIR /project

RUN pip install --no-cache-dir fastapi uvicorn sqlalchemy httpx

RUN pip install --no-cache-dir \
    --index-url https://test.pypi.org/simple/ \
    --extra-index-url https://pypi.org/simple/ \
    psych_analyzer==0.1.3

COPY backend/app/ /project/app/

EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]