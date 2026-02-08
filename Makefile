SHELL = /bin/bash

.PHONY: all backend frontend run

all: run

run:
	@echo "Starting backend and frontend..."
	@cd backend && python manage.py runserver & \
	cd frontend && npm run dev & \
	wait
venv:
	@echo "Creating virtual environment..."
	@cd backend && python3 -m venv venv
	@echo "Installing dependencies..."
	@cd backend && source venv/bin/activate && pip install -r requirements.txt

backend:
	@echo "Starting backend..."
	@cd backend && source venv/bin/activate && python3 manage.py runserver

frontend:
	@echo "Starting frontend..."
	@cd frontend && npm run dev
