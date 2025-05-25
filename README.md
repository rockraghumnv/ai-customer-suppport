# AI Support Platform

This project is a Django-based platform for managing support tickets, companies, and file uploads, with future integration for AI-powered support agents.

## Project Structure
- `ai_support_platform/`: Django project settings and configuration
- `support/`: Main app for support ticketing, companies, and file uploads
- `media/`: Uploaded files
- `requirements.txt`: Python dependencies
- `Dockerfile`: (To be completed for containerization)
- `.env`: (Environment variables, e.g., secrets, API keys)

## Setup Instructions

### 1. Clone the repository
```
git clone <your-repo-url>
cd hackthon
```

### 2. Create and activate a virtual environment
```
python -m venv venv
.\venv\Scripts\activate
```

### 3. Install dependencies
```
pip install -r requirements.txt
```

### 4. Set up environment variables
- Copy `.env.example` to `.env` and fill in required values (if any).

### 5. Apply database migrations
```
python manage.py migrate
```

### 6. Create a superuser (for admin access)
```
python manage.py createsuperuser
```

### 7. Run the development server
```
python manage.py runserver
```

Visit [http://127.0.0.1:8000/admin/](http://127.0.0.1:8000/admin/) to access the Django admin panel.

## Docker Usage (Optional)
- Complete the `Dockerfile` for containerized deployment.

## Production Deployment (Docker + Gunicorn)

1. Build and run with Docker:
```sh
docker build -t ai-support-platform .
docker run -d -p 8000:8000 --env DJANGO_SUPERUSER_PASSWORD=admin ai-support-platform
```

2. Or run with Gunicorn:
```sh
python manage.py collectstatic --noinput
python manage.py migrate
gunicorn ai_support_platform.wsgi:application --bind 0.0.0.0:8000
```

3. Serve static/media files with Nginx or similar in production.

## Windows Production Deployment (PowerShell)

1. Build Docker image:
```powershell
docker build -t ai-support-platform .
```
2. Run Docker container:
```powershell
docker run -d -p 8000:8000 --env DJANGO_SUPERUSER_PASSWORD=admin ai-support-platform
```
3. Or run locally with Gunicorn (after collecting static files):
```powershell
python manage.py collectstatic --noinput
python manage.py migrate
gunicorn ai_support_platform.wsgi:application --bind 0.0.0.0:8000
```
4. For static/media files in production, use a reverse proxy (e.g., Nginx) or cloud storage.

## Environment Variables
- Set `DJANGO_SECRET_KEY`, `DEBUG`, and database settings for production.

## API Docs
- Swagger: `/swagger/`
- ReDoc: `/redoc/`

## Notes
- Restrict `CORS_ALLOW_ALL_ORIGINS` in production.
- Use HTTPS and secure credentials.

## Security Notes
- Set `DEBUG=0` and a strong `DJANGO_SECRET_KEY` in production.
- Restrict `CORS_ALLOW_ALL_ORIGINS` to your frontend domain.
- Use HTTPS in production.

---

For more details, see Django documentation: https://docs.djangoproject.com/en/5.2/
