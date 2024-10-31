FROM python:3.12 AS base

ARG PYTHONFAULTHANDLER=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONHASHSEED=random \
    PIP_NO_CACHE_DIR=on \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    PIP_DEFAULT_TIMEOUT=500

RUN apt-get update && \
    apt-get install -y gcc && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

RUN python -m pip install --upgrade pip

WORKDIR /app
COPY lecture_2/hw/shop_api ./shop_api
COPY lecture_3/hw/requirements.txt .

RUN pip install -r requirements.txt

FROM base as dev
CMD ["bash", "-c", "while true; do sleep 1; done"]

FROM base as local
CMD ["uvicorn", "shop_api.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
