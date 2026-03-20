# WordPress-Projekt

This repository now contains both:
- a local WordPress stack with MariaDB, WordPress PHP-FPM, and Nginx
- a Django backend development stack with PostgreSQL, Redis, Channels, and Celery

Frontend branch additions:
- `frontend/` now contains a Next.js app
- auth views: `/login` and `/register`
- ecommerce views: `/dashboard`, `/products`, `/products/[id]`
- the frontend integrates with backend auth and ecommerce endpoints exposed by Django
- run it with Node.js from `frontend/` using `npm install` and `npm run dev`
- the Next.js app is separate from the WordPress Nginx container
- or run it with Docker from `docker-compose-backend-dev.yml` on `http://localhost:3000`

Backend additions imported from `backend-dev`:
- `docker-compose-backend-dev.yml` starts Django, PostgreSQL, Redis, Celery worker, and Celery Beat
- `backend_django_dev/` contains the Django project and API app
- `Makefile` includes helper commands for the backend and WordPress stacks
