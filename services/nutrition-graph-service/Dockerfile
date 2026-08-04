FROM python:3.11-slim

WORKDIR /app

# Instalar dependencias
COPY services/nutrition-graph-service/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY packages/nutrigraph-common /packages/nutrigraph-common
RUN pip install -e /packages/nutrigraph-common

# Copiar el código fuente
COPY services/nutrition-graph-service .

# Exponer el puerto
EXPOSE 8000

# Comando para ejecutar la aplicación
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
