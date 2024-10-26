DC = docker compose
ENV = --env-file .env

.PHONY: up
up:
	${DC} up -d --build --remove-orphans

.PHONY: down
down:
	${DC} down --remove-orphans
