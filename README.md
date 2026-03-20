# WordPress-Projekt

This repository now contains both:
- a local WordPress stack with MariaDB, WordPress PHP-FPM, and Nginx
- a Django backend development stack with PostgreSQL, Redis, Channels, and Celery

Frontend branch additions:
- `/frontend-login` serves a custom HTML login page from the repository
- the form posts credentials to WordPress at `/wp-login.php`
- `/frontend-register` serves a registration page that sends JSON to `http://localhost:18000/api/auth/register/`

Backend additions imported from `backend-dev`:
- `docker-compose-backend-dev.yml` starts Django, PostgreSQL, Redis, Celery worker, and Celery Beat
- `backend_django_dev/` contains the Django project and API app
- `Makefile` includes helper commands for the backend and WordPress stacks
