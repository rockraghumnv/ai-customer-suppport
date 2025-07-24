# Production-ready Dockerfile for Django + Gunicorn
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV DJANGO_SETTINGS_MODULE=ai_support_platform.settings
ENV PYTHONUNBUFFERED=1

RUN python manage.py collectstatic --noinput

EXPOSE 8000

CMD ["gunicorn", "ai_support_platform.wsgi:application", "--bind", "0.0.0.0:8000"]
