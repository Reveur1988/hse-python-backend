from fastapi import APIRouter, HTTPException, Query, Response, status
from typing import Optional
from lecture_2.hw.shop_api.models import Item
from lecture_2.hw.shop_api.storage import storage

router = APIRouter()

@router.post("/item", status_code=status.HTTP_201_CREATED)
def create_item(item: Item):
    return storage.create_item(item)

@router.get("/item/{item_id}")
def get_item(item_id: int):
    item = storage.get_item(item_id)
    if not item or item.deleted:
        raise HTTPException(status_code=404, detail="Item not found")
    return item

@router.get("/item")
def get_items(
    offset: int = Query(0, ge=0),
    limit: int = Query(10, gt=0),
    min_price: Optional[float] = Query(None, ge=0),
    max_price: Optional[float] = Query(None, ge=0),
    show_deleted: bool = False
):
    filtered_items = list(storage.items_db.values())
    
    if not show_deleted:
        filtered_items = [item for item in filtered_items if not item.deleted]
    
    if min_price is not None:
        filtered_items = [item for item in filtered_items if item.price >= min_price]
    
    if max_price is not None:
        filtered_items = [item for item in filtered_items if item.price <= max_price]
    
    return filtered_items[offset:offset + limit]

@router.put("/item/{item_id}")
def update_item(item_id: int, item: Item):
    if item_id not in storage.items_db:
        raise HTTPException(status_code=404, detail="Item not found")
    
    current_item = storage.items_db[item_id]
    current_item.name = item.name
    current_item.price = item.price
    
    return current_item

@router.patch("/item/{item_id}")
def patch_item(item_id: int, item_update: dict):
    if item_id not in storage.items_db:
        raise HTTPException(status_code=404, detail="Item not found")
    
    current_item = storage.items_db[item_id]
    
    if current_item.deleted:
        return Response(status_code=status.HTTP_304_NOT_MODIFIED)
    
    valid_fields = {"name", "price"}
    if not set(item_update.keys()).issubset(valid_fields):
        raise HTTPException(status_code=422, detail="Invalid fields in update")
    
    if "name" in item_update:
        current_item.name = item_update["name"]
    if "price" in item_update:
        current_item.price = item_update["price"]
    
    return current_item

@router.delete("/item/{item_id}")
def delete_item(item_id: int):
    if item_id not in storage.items_db:
        raise HTTPException(status_code=404, detail="Item not found")
    storage.items_db[item_id].deleted = True
    return {"status": "deleted"}
