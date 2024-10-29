class Storage:
    def __init__(self):
        self.items_db = {}
        self.carts_db = {}
        self.next_item_id = 1
        self.next_cart_id = 1

    def create_item(self, item):
        item.id = self.next_item_id
        self.items_db[item.id] = item
        self.next_item_id += 1
        return item

    def get_item(self, item_id):
        return self.items_db.get(item_id)

    def create_cart(self):
        cart_id = self.next_cart_id
        self.next_cart_id += 1
        return cart_id

    def get_cart(self, cart_id):
        return self.carts_db.get(cart_id)

storage = Storage()
