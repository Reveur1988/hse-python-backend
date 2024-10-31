.PHONY: hw1 monitoring-up monitoring-down load-test monitoring-clean

hw1:
	uvicorn homework_1.main:app --reload

monitoring-up:
	docker compose -f lecture_3/hw/docker-compose.yml up --build -d

monitoring-down:
	docker compose -f lecture_3/hw/docker-compose.yml down

monitoring-clean:
	docker compose -f lecture_3/hw/docker-compose.yml down -v
	docker rmi shop-api-local:latest

load-test:
	python lecture_3/hw/load_test.py
