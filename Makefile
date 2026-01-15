SHELL = /bin/bash

.PHONY: all backend frontend run

all: run

run:
	@echo "Starting backend and frontend..."
	@cd backend && python manage.py runserver & \
	cd frontend && npm run dev & \
	wait

backend:
	@echo "Starting backend..."
	@cd backend && python manage.py runserver

frontend:
	@echo "Starting frontend..."
	@cd frontend && npm run dev
