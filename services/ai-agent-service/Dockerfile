FROM python:3.11-slim

WORKDIR /app

COPY services/ai-agent-service/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY packages/nutrigraph-common /packages/nutrigraph-common
RUN pip install -e /packages/nutrigraph-common

COPY services/ai-agent-service .

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
