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
CMD ["gunicorn", "-b", "0.0.0.0:5000", "app:app", "--workers=4", "--threads=4", "--log-level=debug", "--access-logfile=-", "--error-logfile=-"]
