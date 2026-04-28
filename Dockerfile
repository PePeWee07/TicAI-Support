FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt /app/requirements.txt

RUN pip install --no-cache-dir -r requirements.txt \
    && pip install --no-cache-dir gunicorn

COPY . /app

ENV PYTHONPATH=/app
ENV FLASK_APP=src/app.py

EXPOSE 5000

# Usa Gunicorn en lugar de `flask run`
CMD sh -c "gunicorn -b 0.0.0.0:5000 src.app:app --workers=$(expr $(nproc) \* 2 + 1) --threads=8 --keep-alive=5 --timeout=500 --log-level=info --access-logfile=- --error-logfile=-"
