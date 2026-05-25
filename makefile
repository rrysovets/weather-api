
COMPOSE = docker-compose --file docker_compose.yaml

.PHONY: up down build logs help exec-web

up:  ## Запустить сервисы
	$(COMPOSE) up -d

down:  ## Остановить сервисы
	$(COMPOSE) down

build:  ## Пересобрать контейнеры
	$(COMPOSE) build

logs:  ## Показать логи
	$(COMPOSE) logs -f


main-app:  ## Зайти в веб-контейнер
	$(COMPOSE) exec main-app sh

db:  ## Зайти в контейнер БД
	$(COMPOSE) exec postgres sh

cache:  ## Зайти в контейнер кэша
	$(COMPOSE) exec redis sh


migrate:  ## Применить миграции
	$(COMPOSE) exec main-app python manage.py migrate

makemigrations:  ## Создать миграции
	$(COMPOSE) exec main-app python manage.py makemigrations

test:  ## Запустить все тесты
	$(COMPOSE) exec main-app python manage.py test