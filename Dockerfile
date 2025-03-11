# Usa una imagen ligera de Python
FROM python:3.9-slim

# Define el directorio de trabajo
WORKDIR /app

# Copia los archivos de la aplicación
COPY . /app

# Instala las dependencias
RUN pip install --no-cache-dir -r requirements.txt

# Expone el puerto 5000
EXPOSE 5000

# Usa Gunicorn en lugar de `flask run`
CMD sh -c "gunicorn -b 0.0.0.0:5000 src.app:app --workers=$(expr $(nproc) \* 2 + 1) --threads=8 --keep-alive=5 --timeout=500 --log-level=info --access-logfile=- --error-logfile=-"
