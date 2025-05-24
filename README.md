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

## Next Steps
- Implement views, serializers, and API endpoints in the `support` app.
- Register models in `support/admin.py`.
- Add tests in `support/tests.py`.
- Integrate AI/ML features as needed.

---

For more details, see Django documentation: https://docs.djangoproject.com/en/5.2/
