# Shop API with Monitoring

REST API сервис магазина с мониторингом через Prometheus и Grafana.

## Требования
- Docker
- Docker Compose
- Python 3.12
- Poetry

## Релевантные файлы
```
hse-python-backend/
├── lecture_2/hw/shop_api/
└── lecture_3/hw/
    ├── Dockerfile
    ├── load_test.py
    ├── docker-compose.yml
    ├── prometheus.yml
    └── requirements.txt
```

## Запуск (из корня проекта)
```bash
poetry install
poetry run make monitoring-up
poetry run make load-test
poetry run make monitoring-down
```

## Доступ к сервисам
- API: http://localhost:8000/docs
- Prometheus: http://localhost:9090
- Grafana: http://localhost:3000 (admin/admin)

При использовании WSL2:
```bash
ip addr show eth0  # Использовать полученный IP вместо localhost
```
