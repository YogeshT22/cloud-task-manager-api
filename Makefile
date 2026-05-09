SHELL := /bin/sh
COMPOSE := docker-compose
K6_SCRIPT := loadtest/k6/task-manager-load-test.js
BASE_URL ?= http://localhost:8000

.PHONY: help bootstrap up down build restart logs ps api-logs worker-logs rabbitmq-logs loadtest clean

help:
	@printf '%s\n' \
	  'Available targets:' \
	  '  make bootstrap      Start the full stack in detached mode' \
	  '  make up             Alias for bootstrap' \
	  '  make down           Stop and remove containers' \
	  '  make build          Rebuild images' \
	  '  make restart        Restart the stack' \
	  '  make logs           Follow all service logs' \
	  '  make ps             Show service status' \
	  '  make api-logs       Follow API logs' \
	  '  make worker-logs    Follow Celery worker logs' \
	  '  make rabbitmq-logs  Follow RabbitMQ logs' \
	  '  make loadtest       Run the k6 script (set ACCESS_TOKEN and TASK_ID)' \
	  '  make clean          Stop containers and remove orphans'

bootstrap up:
	$(COMPOSE) up -d --build

build:
	$(COMPOSE) build

down:
	$(COMPOSE) down

restart:
	$(COMPOSE) restart

logs:
	$(COMPOSE) logs -f

ps:
	$(COMPOSE) ps

api-logs:
	$(COMPOSE) logs -f api

worker-logs:
	$(COMPOSE) logs -f worker

rabbitmq-logs:
	$(COMPOSE) logs -f rabbitmq

loadtest:
	@if [ -z "$$ACCESS_TOKEN" ] || [ -z "$$TASK_ID" ]; then \
		echo "Set ACCESS_TOKEN and TASK_ID before running make loadtest"; \
		exit 1; \
	fi
	ACCESS_TOKEN="$$ACCESS_TOKEN" TASK_ID="$$TASK_ID" BASE_URL="$(BASE_URL)" k6 run $(K6_SCRIPT)

clean:
	$(COMPOSE) down --remove-orphans
