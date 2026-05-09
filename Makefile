SHELL := /bin/sh
COMPOSE := docker-compose
K6_SCRIPT := loadtest/k6/task-manager-load-test.js
BASE_URL ?= http://localhost:8000
LOADTEST_USER_EMAIL ?= loadtest@example.com
LOADTEST_USER_PASSWORD ?= pass123

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
	  '  make loadtest       Run k6 (auto-creates token/task if not provided)' \
	  '                     Optional: ACCESS_TOKEN=... TASK_ID=... make loadtest' \
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
	@command -v k6 >/dev/null 2>&1 || { echo "k6 is not installed. Install k6 first."; exit 1; }
	@ACCESS_TOKEN_INPUT="$$ACCESS_TOKEN"; \
	TASK_ID_INPUT="$$TASK_ID"; \
	if [ -z "$$ACCESS_TOKEN_INPUT" ] || [ -z "$$TASK_ID_INPUT" ]; then \
		echo "No ACCESS_TOKEN/TASK_ID provided. Auto-provisioning load test user and task..."; \
		curl -sS -X POST "$(BASE_URL)/users/" \
		  -H "Content-Type: application/json" \
		  -d '{"email":"$(LOADTEST_USER_EMAIL)","password":"$(LOADTEST_USER_PASSWORD)"}' >/dev/null || true; \
		LOGIN_RESPONSE=$$(curl -sS -X POST "$(BASE_URL)/login" \
		  -H "Content-Type: application/x-www-form-urlencoded" \
		  -d 'username=$(LOADTEST_USER_EMAIL)&password=$(LOADTEST_USER_PASSWORD)'); \
		ACCESS_TOKEN_INPUT=$$(printf '%s' "$$LOGIN_RESPONSE" | sed -n 's/.*"access_token"[[:space:]]*:[[:space:]]*"\([^"]*\)".*/\1/p'); \
		if [ -z "$$ACCESS_TOKEN_INPUT" ]; then \
			echo "Failed to login and retrieve access token."; \
			echo "Response: $$LOGIN_RESPONSE"; \
			exit 1; \
		fi; \
		TASK_RESPONSE=$$(curl -sS -X POST "$(BASE_URL)/tasks/" \
		  -H "Authorization: Bearer $$ACCESS_TOKEN_INPUT" \
		  -H "Content-Type: application/json" \
		  -d '{"title":"Load test seed task","content":"Auto-generated for k6"}'); \
		TASK_ID_INPUT=$$(printf '%s' "$$TASK_RESPONSE" | sed -n 's/.*"id"[[:space:]]*:[[:space:]]*\([0-9][0-9]*\).*/\1/p'); \
		if [ -z "$$TASK_ID_INPUT" ]; then \
			echo "Failed to create task and retrieve task id."; \
			echo "Response: $$TASK_RESPONSE"; \
			exit 1; \
		fi; \
		echo "Auto-generated ACCESS_TOKEN and TASK_ID=$$TASK_ID_INPUT"; \
	fi; \
	ACCESS_TOKEN="$$ACCESS_TOKEN_INPUT" TASK_ID="$$TASK_ID_INPUT" BASE_URL="$(BASE_URL)" k6 run $(K6_SCRIPT)

clean:
	$(COMPOSE) down --remove-orphans
