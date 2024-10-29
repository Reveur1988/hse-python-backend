from fastapi import APIRouter, HTTPException, Query, Response, status
from typing import Optional
from lecture_2.hw.shop_api.models import Cart, CartItem
from lecture_2.hw.shop_api.storage import storage

router = APIRouter()

@router.post("/cart", status_code=status.HTTP_201_CREATED)
def create_cart(response: Response):
    cart_id = storage.create_cart()
    cart = Cart(id=cart_id, items=[], price=0)
    storage.carts_db[cart.id] = cart
    
    response.headers["location"] = f"/cart/{cart.id}"
    return {"id": cart.id}

@router.get("/cart/{cart_id}")
def get_cart(cart_id: int):
    cart = storage.get_cart(cart_id)
    if not cart:
        raise HTTPException(status_code=404, detail="Cart not found")
    return cart

@router.get("/cart")
def get_carts(
    offset: int = Query(0, ge=0),
    limit: int = Query(10, gt=0),
    min_price: Optional[float] = Query(None, ge=0),
    max_price: Optional[float] = Query(None, ge=0),
    min_quantity: Optional[int] = Query(None, ge=0),
    max_quantity: Optional[int] = Query(None, ge=0)
):
    filtered_carts = list(storage.carts_db.values())
    
    if min_price is not None:
        filtered_carts = [cart for cart in filtered_carts if cart.price >= min_price]
    
    if max_price is not None:
        filtered_carts = [cart for cart in filtered_carts if cart.price <= max_price]
    
    if min_quantity is not None or max_quantity is not None:
        def total_quantity(cart):
            return sum(item.quantity for item in cart.items)
        
        if min_quantity is not None:
            filtered_carts = [cart for cart in filtered_carts if total_quantity(cart) >= min_quantity]
        
        if max_quantity is not None:
            filtered_carts = [cart for cart in filtered_carts if total_quantity(cart) <= max_quantity]
    
    return filtered_carts[offset:offset + limit]

@router.post("/cart/{cart_id}/add/{item_id}")
def add_item_to_cart(cart_id: int, item_id: int):
    cart = storage.get_cart(cart_id)
    if not cart:
        raise HTTPException(status_code=404, detail="Cart not found")
    
    item = storage.get_item(item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    
    existing_item = next((cart_item for cart_item in cart.items if cart_item.id == item_id), None)
    
    if existing_item:
        existing_item.quantity += 1
    else:
        cart_item = CartItem(
            id=item.id,
            name=item.name,
            quantity=1,
            available=not item.deleted
        )
        cart.items.append(cart_item)
    
    cart.price = sum(
        storage.items_db[cart_item.id].price * cart_item.quantity 
        for cart_item in cart.items
    )
    
    return cart
