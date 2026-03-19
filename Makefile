.DEFAULT_GOAL := help

COMPOSE_BACKEND := docker compose -f docker-compose-backend-dev.yml
COMPOSE_WP := docker compose -f docker-compose.yml
DJANGO_SERVICE := django

.PHONY: help
help:
	@echo "Dostepne komendy:"
	@echo "  make up              - uruchom backend (django, celery, postgres, redis)"
	@echo "  make down            - zatrzymaj backend"
	@echo "  make restart         - restart backend"
	@echo "  make build           - przebuduj obrazy backendu"
	@echo "  make logs            - podglad logow backendu"
	@echo "  make ps              - lista kontenerow backendu"
	@echo "  make shell           - shell w kontenerze django"
	@echo "  make migrate         - wykonaj migracje"
	@echo "  make makemigrations  - utworz migracje"
	@echo "  make superuser       - utworz superusera"
	@echo "  make test            - uruchom testy django"
	@echo "  make wp-up           - uruchom stack WordPress"
	@echo "  make wp-down         - zatrzymaj stack WordPress"
	@echo "  make all-up          - uruchom backend i WordPress"
	@echo "  make all-down        - zatrzymaj backend i WordPress"

.PHONY: up
up:
	$(COMPOSE_BACKEND) up -d --build

.PHONY: down
down:
	$(COMPOSE_BACKEND) down

.PHONY: restart
restart: down up

.PHONY: build
build:
	$(COMPOSE_BACKEND) build

.PHONY: logs
logs:
	$(COMPOSE_BACKEND) logs -f --tail=200

.PHONY: ps
ps:
	$(COMPOSE_BACKEND) ps

.PHONY: shell
shell:
	$(COMPOSE_BACKEND) exec $(DJANGO_SERVICE) sh

.PHONY: migrate
migrate:
	$(COMPOSE_BACKEND) exec $(DJANGO_SERVICE) python manage.py migrate

.PHONY: makemigrations
makemigrations:
	$(COMPOSE_BACKEND) exec $(DJANGO_SERVICE) python manage.py makemigrations

.PHONY: superuser
superuser:
	$(COMPOSE_BACKEND) exec $(DJANGO_SERVICE) python manage.py createsuperuser

.PHONY: test
test:
	$(COMPOSE_BACKEND) exec $(DJANGO_SERVICE) python manage.py test

.PHONY: wp-up
wp-up:
	$(COMPOSE_WP) up -d

.PHONY: wp-down
wp-down:
	$(COMPOSE_WP) down

.PHONY: all-up
all-up: up wp-up

.PHONY: all-down
all-down: down wp-down
