from concurrent.futures import ThreadPoolExecutor, as_completed
import random
import time
import requests
from faker import Faker

faker = Faker()

def generate_item():
    return {
        "name": f"{faker.word()} {faker.word()}",
        "price": round(random.uniform(10.0, 1000.0), 2),
        "deleted": False
    }

def create_items():
    """Create random items in the shop"""
    for _ in range(20):
        item = generate_item()
        try:
            response = requests.post(
                "http://localhost:8000/item",
                json=item
            )
            print(f"Created item: {response.status_code}")
            if response.status_code == 201:
                return response.json()["id"]
        except requests.exceptions.RequestException as e:
            print(f"Error creating item: {e}")
    return None

def get_items():
    """Get items with different filters"""
    for _ in range(30):
        params = {
            "offset": random.randint(0, 5),
            "limit": random.randint(5, 20),
            "min_price": random.uniform(0, 100) if random.random() > 0.5 else None,
            "max_price": random.uniform(100, 1000) if random.random() > 0.5 else None,
            "show_deleted": random.random() > 0.8
        }
        try:
            response = requests.get(
                "http://localhost:8000/item",
                params={k: v for k, v in params.items() if v is not None}
            )
            print(f"Get items: {response.status_code}")
            
            if random.random() > 0.7 and response.status_code == 200:
                items = response.json()
                if items:
                    item_id = items[0]["id"]
                    response = requests.get(f"http://localhost:8000/item/{item_id}")
                    print(f"Get item {item_id}: {response.status_code}")
        except requests.exceptions.RequestException as e:
            print(f"Error getting items: {e}")

def work_with_cart():
    """Create cart and add items to it"""
    try:
        response = requests.post("http://localhost:8000/cart")
        if response.status_code != 201:
            return
        
        cart_id = response.json()["id"]
        print(f"Created cart: {cart_id}")
        
        num_items = random.randint(1, 5)
        for _ in range(num_items):
            item_id = create_items()
            if item_id:
                response = requests.post(f"http://localhost:8000/cart/{cart_id}/add/{item_id}")
                print(f"Added item to cart: {response.status_code}")
        
        response = requests.get(f"http://localhost:8000/cart/{cart_id}")
        if response.status_code == 200:
            cart = response.json()
            print(f"Cart {cart_id} total price: {cart['price']}")
    except requests.exceptions.RequestException as e:
        print(f"Error in cart operations: {e}")

def main():
    """Run load testing with multiple threads"""
    print("Starting load test...")
    print("Waiting 5 seconds for services to be ready...")
    time.sleep(5)
    
    try:
        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = []
            
            for cycle in range(5):
                print(f"Starting cycle {cycle + 1}")
                for _ in range(20):
                    futures.append(executor.submit(create_items))
                    futures.append(executor.submit(get_items))
                    futures.append(executor.submit(work_with_cart))
                
                for future in as_completed(futures):
                    try:
                        future.result()
                    except Exception as e:
                        print(f"Error in task: {e}")
                
                print(f"Cycle {cycle + 1} completed")
                time.sleep(5)
        
        print("Load test completed successfully")
    except Exception as e:
        print(f"Load test failed: {e}")

if __name__ == "__main__":
    main()
