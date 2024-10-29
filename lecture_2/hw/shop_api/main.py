from fastapi import FastAPI
from lecture_2.hw.shop_api.routes.items import router as items_router
from lecture_2.hw.shop_api.routes.carts import router as carts_router

app = FastAPI()

app.include_router(items_router)
app.include_router(carts_router)
