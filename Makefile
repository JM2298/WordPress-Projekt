.DEFAULT_GOAL := help

COMPOSE := docker compose -f docker-compose.yml
DJANGO_SERVICE := django
BACKUP_DIR := BACKUP
BACKUP_DJANGO_DIR := $(BACKUP_DIR)/django_db
BACKUP_WP_DIR := $(BACKUP_DIR)/wordpress_db
TIMESTAMP := $(shell powershell -NoProfile -Command "Get-Date -Format yyyyMMdd_HHmmss")
POSTGRES_DB ?= app
POSTGRES_USER ?= app
MYSQL_DATABASE ?= wordpress
MYSQL_ROOT_PASSWORD ?= root_password

.PHONY: help
help:
	@echo "Dostepne komendy (jeden docker-compose.yml):"
	@echo "  make up              - uruchom caly stack (backend + WordPress)"
	@echo "  make down            - zatrzymaj caly stack"
	@echo "  make restart         - restart calego stacku"
	@echo "  make build           - przebuduj wszystkie obrazy"
	@echo "  make logs            - podglad logow calego stacku"
	@echo "  make ps              - lista kontenerow"
	@echo "  make shell           - shell w kontenerze django"
	@echo "  make migrate         - wykonaj migracje Django"
	@echo "  make makemigrations  - utworz migracje Django"
	@echo "  make superuser       - utworz superusera Django"
	@echo "  make test            - uruchom testy Django"
	@echo "  make backend-up      - uruchom tylko backend"
	@echo "  make backend-down    - zatrzymaj tylko backend"
	@echo "  make wp-up           - uruchom tylko WordPress"
	@echo "  make wp-down         - zatrzymaj tylko WordPress"
	@echo "  make backup-django-db - backup bazy Django (PostgreSQL)"
	@echo "  make backup-wp-db     - backup bazy WordPress (MariaDB)"
	@echo "  make backup-db        - backup obu baz"
	@echo "  make restore-django-db DJANGO_FILE=... - przywroc baze Django"
	@echo "  make restore-wp-db WP_FILE=...         - przywroc baze WordPress"
	@echo "  make restore-db DJANGO_FILE=... WP_FILE=... - przywroc obie bazy"
	@echo "  make all-up          - alias do make up"
	@echo "  make all-down        - alias do make down"

.PHONY: up
up:
	$(COMPOSE) up -d --build

.PHONY: down
down:
	$(COMPOSE) down

.PHONY: restart
restart: down up

.PHONY: build
build:
	$(COMPOSE) build

.PHONY: logs
logs:
	$(COMPOSE) logs -f --tail=200

.PHONY: ps
ps:
	$(COMPOSE) ps

.PHONY: shell
shell:
	$(COMPOSE) exec $(DJANGO_SERVICE) sh

.PHONY: migrate
migrate:
	$(COMPOSE) exec $(DJANGO_SERVICE) python manage.py migrate

.PHONY: makemigrations
makemigrations:
	$(COMPOSE) exec $(DJANGO_SERVICE) python manage.py makemigrations

.PHONY: superuser
superuser:
	$(COMPOSE) exec $(DJANGO_SERVICE) python manage.py createsuperuser

.PHONY: test
test:
	$(COMPOSE) exec $(DJANGO_SERVICE) python manage.py test

.PHONY: backend-up
backend-up:
	$(COMPOSE) up -d --build postgres redis django celery_worker celery_beat

.PHONY: backend-down
backend-down:
	$(COMPOSE) stop celery_beat celery_worker django redis postgres

.PHONY: wp-up
wp-up:
	$(COMPOSE) up -d db wordpress nginx

.PHONY: wp-down
wp-down:
	$(COMPOSE) stop nginx wordpress db

.PHONY: backup-django-db
backup-django-db:
	@if not exist "$(BACKUP_DJANGO_DIR)" mkdir "$(BACKUP_DJANGO_DIR)"
	$(COMPOSE) exec -T postgres sh -c "pg_dump -U $(POSTGRES_USER) -d $(POSTGRES_DB)" > "$(BACKUP_DJANGO_DIR)/django_$(TIMESTAMP).sql"
	@echo "Utworzono backup Django DB: $(BACKUP_DJANGO_DIR)/django_$(TIMESTAMP).sql"

.PHONY: backup-wp-db
backup-wp-db:
	@if not exist "$(BACKUP_WP_DIR)" mkdir "$(BACKUP_WP_DIR)"
	$(COMPOSE) exec -T db sh -c "mysqldump -uroot -p$(MYSQL_ROOT_PASSWORD) $(MYSQL_DATABASE)" > "$(BACKUP_WP_DIR)/wordpress_$(TIMESTAMP).sql"
	@echo "Utworzono backup WordPress DB: $(BACKUP_WP_DIR)/wordpress_$(TIMESTAMP).sql"

.PHONY: backup-db
backup-db: backup-django-db backup-wp-db

.PHONY: restore-django-db
restore-django-db:
	@if "$(DJANGO_FILE)"=="" (echo Podaj plik: make restore-django-db DJANGO_FILE=BACKUP/django_db/django_YYYYmmdd_HHMMSS.sql & exit /b 1)
	type "$(DJANGO_FILE)" | $(COMPOSE) exec -T postgres sh -c "psql -U $(POSTGRES_USER) -d $(POSTGRES_DB)"
	@echo "Przywrocono baze Django z: $(DJANGO_FILE)"

.PHONY: restore-wp-db
restore-wp-db:
	@if "$(WP_FILE)"=="" (echo Podaj plik: make restore-wp-db WP_FILE=BACKUP/wordpress_db/wordpress_YYYYmmdd_HHMMSS.sql & exit /b 1)
	type "$(WP_FILE)" | $(COMPOSE) exec -T db sh -c "mysql -uroot -p$(MYSQL_ROOT_PASSWORD) $(MYSQL_DATABASE)"
	@echo "Przywrocono baze WordPress z: $(WP_FILE)"

.PHONY: restore-db
restore-db:
	@if "$(DJANGO_FILE)"=="" (echo Podaj plik Django: make restore-db DJANGO_FILE=... WP_FILE=... & exit /b 1)
	@if "$(WP_FILE)"=="" (echo Podaj plik WordPress: make restore-db DJANGO_FILE=... WP_FILE=... & exit /b 1)
	$(MAKE) restore-django-db DJANGO_FILE="$(DJANGO_FILE)"
	$(MAKE) restore-wp-db WP_FILE="$(WP_FILE)"

.PHONY: all-up
all-up: up

.PHONY: all-down
all-down: down
