HERE = $(shell pwd)

.PHONY: all

all: 
	@echo Please run make dev or make prod

dev:
	docker-compose -f docker-compose.yml up --build

format-code:
	docker-compose run api black api/

lint:
	# docker-compose build
	docker-compose run api flake8

test:
	# docker-compose build
	docker-compose run api pytest -vvv -s

