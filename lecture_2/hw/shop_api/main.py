from fastapi import FastAPI
from prometheus_fastapi_instrumentator import Instrumentator
from .routes.items import router as items_router
from .routes.carts import router as carts_router

app = FastAPI()

Instrumentator().instrument(app).expose(app)

app.include_router(items_router)
app.include_router(carts_router)
