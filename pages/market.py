import flet as ft
import psycopg2 as pg
from utils.extras import *
from service.auth import connect_db

# Define a QuantitySelector class that allows users to increase or decrease the quantity of an item in the cart

class QuantitySelector(ft.Row):
    def __init__(self,n):
        super(QuantitySelector, self).__init__()

        self.cartItem = n
        self.quantity = Model.cart[self.cartItem]["quantity"]

        self.decrease_button = ft.ElevatedButton(
            "-",
            on_click=self.decrease_quantity,
            style=ft.ButtonStyle(bgcolor={"": "#202020"}),
        )

        self.increase_button = ft.ElevatedButton(
            "+",
            on_click=self.increase_quantity,
            style=ft.ButtonStyle(bgcolor={"": "#202020"}),
        )

        self.remove_button = ft.ElevatedButton(
            "移除商品",
            on_click=self.remove_item,
            style=ft.ButtonStyle(bgcolor={"": "#202020"}),
        )

        self.quantity_text = ft.Text(str(self.quantity), size=28, weight="bold")

        self.controls = [self.decrease_button, self.quantity_text, self.increase_button, self.remove_button]

    def decrease_quantity(self, e):
        if self.quantity > 1:
            self.quantity -= 1
            self.quantity_text.value = str(self.quantity)
            # Update the cart quantity in the Model class
            Model.cart[self.cartItem]["quantity"] = self.quantity
            Model.update_cart_quantity(self.cartItem, self.quantity)  # 通知Model更新購物車
            self.update()

    def increase_quantity(self, e):
        self.quantity += 1
        self.quantity_text.value = str(self.quantity)
        Model.cart[self.cartItem]["quantity"] = self.quantity
        Model.update_cart_quantity(self.cartItem, self.quantity)  # 通知Model更新購物車
        self.update()

    def remove_item(self, e):
        del Model.cart[self.cartItem]
        Model._notify_listeners()
        self.update()

# Define your model class => class that stores your data
class Model(object):
    products: dict = {
        0: {
            "id": "111",
            "img_src": "638380864757770000.jpg",
            "name": "【 SOUR 】SNAPE–HOOKAHJESUS 8.25",
            "description": "無",
            "price": "NT$2,200",
        },
        1: {
            "id": "222",
            "img_src": "638424762422570000.jpg",
            "name": "【INDEPENDENT】139 STAGE 11 FORGED HOLLOW CANT BE BEAT 78 SILVER ANO BLUE",
            "description": "無",
            "price": "NT$2,600",
        },
        2: {
            "id": "333",
            "img_src": "638436857380870000.jpg",
            "name": "【OJ WHEELS】雙硬度板輪 56MM /外層101A內層95A - MILTON MARTINEZ HEAR NO EVIL DOUBLE DURO WHITE",
            "description": "無",
            "price": "NT$2,200",
        },
    }

    cart: dict = {}
    _listeners = []

    @staticmethod
    def get_products():
        return Model.products

    @staticmethod
    def get_cart():
        return Model.cart

    @staticmethod
    def add_item_to_cart(data: str):
        for _, values in Model.products.items():
            for key, value in values.items():
                if value == data:
                    if not Model.cart.get(value):
                        Model.cart[value] = {"quantity": 1, **values}

                    else:
                        Model.cart[value]["quantity"] += 1

    @staticmethod
    def calculate_total():
        total = 0
        for item in Model.cart.values():
            # Remove the currency symbol and convert the price to an integer
            price = int(item['price'].replace('NT$', '').replace(',', ''))
            quantity = item['quantity']
            total += price * quantity
        return total
    
    @staticmethod
    def add_listener(listener):
        Model._listeners.append(listener) # first element is update_total

    @staticmethod
    def _notify_listeners():
        for listener in Model._listeners:
            listener()

    @staticmethod
    def update_cart_quantity(cartItem, quantity):
        Model.cart[cartItem]["quantity"] = quantity
        Model._notify_listeners()


# Next, define the product page ...
class Product(ft.View):

    def __init__(self, page: ft.Page):
        super(Product, self).__init__()
        self.page = page

        def addClick(e):
            self.page.go("/addProduct")
            return
        
        self.page.floating_action_button = ft.FloatingActionButton(
            icon=ft.icons.ADD, on_click=addClick, bgcolor=ft.colors.BLACK38
            )
        self.conn = connect_db()
        self.cur = self.conn.cursor()

        self.initilize()

    def load_products_from_db(self):
        query = "SELECT uid, name, description, price, time, status, img, id FROM product"
        self.cur.execute(query)
        rows = self.cur.fetchall()
        
        Model.products = {}
        for row in rows:
            Model.products[row[7]] = {
                "id": row[7],
                "img_src": row[6][0],
                "name": row[1],
                "description": row[2],
                "price": f"NT${row[3]}",
            }
        #print(Model.products)
        #print(Model.get_products())
    # we break the UI compoenents into several functions for better code readability

    # a method to initilize everythong
    def initilize(self):
        # this is the main row where items apepar ,,,
        self.products = ft.Row(expand=True, scroll="auto", spacing=30)
        self.load_products_from_db()  # 加載產品資料
        self.create_products(Model.products)
        def search(e):
            # Get the search query from the event
            search_query = e.control.value
            print(search_query)
            # Construct the SQL query to search for the product in the database
            sql_query = "SELECT * FROM product WHERE name ILIKE %s"
            search_query_like = f"%{search_query}%"  # Adding wildcards for partial matching

            # Execute the SQL query
            with self.conn.cursor() as cursor:
                cursor.execute(sql_query, (search_query_like,))
                search_results = cursor.fetchall()

            # If search results are found, display them using create_products()
            if search_results:
                # Convert search results to a dictionary format similar to Model.products
                formatted_results = {}
                for row in search_results:
                    formatted_results[row[0]] = {
                        "id": row[0],
                        "img_src": row[1],  # Assuming image source is in the second column
                        "name": row[2],  # Assuming product name is in the third column
                        "description": row[3],  # Assuming description is in the fourth column
                        "price": row[4],  # Assuming price is in the fifth column
                    }
                
                # Display search results using create_products()
                self.create_products(formatted_results)
            else:
                print("No matching products found.")

        search_input=ft.TextField(icon=ft.icons.SEARCH,text_size=20,border_radius=30,content_padding=5,cursor_color = ft.colors.BLUE_200,on_submit=lambda e: search(e))

        self.controls = [
            self.display_product_page_header(),
            ft.Text("賣場", size=32),
            ft.Text("從下面的清單中選擇商品"),
            self.products,
            self.page.floating_action_button,
            self.page.navigation_bar,
            #search button
            search_input,
            self.display_product_page_footer(),
        ]

    def display_product_page_footer(self):
        return ft.Row([ft.Text("Simple Sk8 Shop", size=10)], alignment="center")

    def display_product_page_header(self):
        return ft.Container(
            content=ft.Row(
                [
                    ft.Icon("settings", size=18),
                    ft.IconButton(
                        "shopping_cart_outlined",
                        on_click=lambda e: self.page.go("/cart"),
                        icon_size=18,
                    ),
                ],
                alignment="spaceBetween",
            )
        )

    # Define a method that creates the product UI items from the Model
    def create_products(self, products):
        # loop over the data and extract the info based on keys
        #print(products)
        for _, values in products.items():
            for (
                key,
                value,
            ) in values.items():
                # values.items() has a specific key:value pairing system
                if key == "img_src":
                    img_src = self.create_product_image(img_path=value)
                elif key == "name":
                    name = values["name"]
                elif key == "description":
                    description = values["description"]
                elif key == "id":
                    idd = values["id"]
                elif key == "price":
                    price = self.create_product_event(values["price"], idd)

            texts = self.create_product_text(name, description)

            self.create_full_item_view(img_src, texts, price)

    # define a gather method that compiles everything
    def create_full_item_view(self, img_src, texts, price):
        item = ft.Column()

        item.controls.append(self.create_product_container(4, img_src))
        item.controls.append(self.create_product_container(4, texts))
        item.controls.append(self.create_product_container(1, price))

        self.products.controls.append(self.create_item_wrapper(item))

    # a final wraper method
    def create_item_wrapper(self, item: ft.Column):
        return ft.Container(
            width=250, height=450, content=item, padding=8, border_radius=6
        )

    # define am ethod for the image UI
    def create_product_image(self, img_path: str):
        return ft.Container(
            image_src=img_path, image_fit="fill", border_radius=6, padding=10
        )

    # define a method for the text UI (name + description)
    def create_product_text(self, name: str, description: str):
        return ft.Column([ft.Text(name, size=18), ft.Text(description, size=14,max_lines=6)])

    # define a method for prie and a add_to_cart button
    def create_product_event(self, price: str, idd: str):
        # we use the idd to keep track of the products being clicked
        return ft.Row(
            [
                ft.Text(price, size=14),
                ft.IconButton(
                    "add",
                    data=idd,
                    on_click=self.add_to_cart,
                ),
            ],
            alignment="spaceBetween",
        )

    # A method to wrap our product card inside a container
    def create_product_container(self, expand: bool, control: ft.control):
        return ft.Container(content=control, expand=expand, padding=5)

    # before the cart, one final method to add items to the cart
    def add_to_cart(self, e: ft.TapEvent):
        Model.add_item_to_cart(data=e.control.data)
        print(Model.cart)


# Finally, we define our cart class
class Cart(ft.View):
    def __init__(self, page: ft.Page):
        super(Cart, self).__init__(route="/cart")
        self.page = page
        self.total_text = ft.Text(f"總計: NT${Model.calculate_total()}", size=20, color=ft.colors.ORANGE_200)
        Model.add_listener(self.update_total)
        self.initilize()

    # similiar to the products page, we break down the UI cart into functions

    # a method to initilize
    def initilize(self):
        self.cart_items = ft.Column(spacing=20)
        self.create_cart()
        
        self.controls = [
            ft.Row(
                [
                    ft.IconButton(
                        "arrow_back_ios_new_outlined",
                        on_click=lambda e: self.page.go("/products"),
                        icon_size=16,
                    )
                ],
                alignment="spaceBetween",
            ),
            ft.Text("購物車", size=32),
            ft.Text("你的購物車商品"),
            self.cart_items,
            ft.Row([self.total_text], alignment=ft.alignment.bottom_center),
            ft.Row([ft.ElevatedButton(content=ft.Text("結帳", size=20), width=self.page.window_width-100, height=100, style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=20)), on_click=self.checkout)], alignment=ft.alignment.bottom_center)
        ]

    def update_total(self):
        self.total_text.value = f"總計: NT${Model.calculate_total()}"
        #self.total_text.update()

    def checkout(self, e: ft.TapEvent):
        print("Checkout")
        self.page.go("/products")
        Model.cart.clear()
        #self.page.overlay.append()

    def create_cart(self, cart: dict = Model.get_cart()):
        for n, values in cart.items():
            for key, value in values.items():
                if key == "img_src":
                    img_src = self.create_item_image(img_path=value)
                elif key == "quantity":
                    quantity = self.create_item_quantity(values["quantity"])
                elif key == "name":
                    name = self.create_item_name(values["name"])
                elif key == "price":
                    price = self.create_item_price(values["price"])

            self.compile_cart_item(n,img_src, quantity, name, price)

    # we also have a method to compile all the items
    def create_cart_item(self):
        return ft.Row(alignment="spaceBetween")

    def compile_cart_item(self, n,img_src, quantity, name, price):
        row = self.create_cart_item()

        row.controls.append(img_src)
        row.controls.append(name)
        row.controls.append(quantity)
        row.controls.append(price)
        row.controls.append(ft.IconButton("edit", data=n, on_click=self.edit_item,expand=1))

        self.cart_items.controls.append(self.create_item_wrap(row))

    # we can now create the seperate UI components for each data
    def create_item_wrap(self, control: ft.Control):
        return ft.Container(
            content=control,
            padding=10,
            border=ft.border.all(1, "white10"),
            border_radius=6,
        )

    def create_item_image(self, img_path):
        return ft.Container(width=32, height=32, image_src=img_path, bgcolor="teal",expand=1)

    def create_item_quantity(self, quantity: int):
        return ft.Text(f"  {quantity} X",color=ft.colors.BLUE_200,expand=1)

    def create_item_name(self, name: str):
        return ft.Text(name, size=16,overflow=ft.TextOverflow.CLIP,max_lines=2,expand=3)

    def create_item_price(self, price: str):
        return ft.Text("  "+price,color=ft.colors.ORANGE_200,expand=2)
    
    def edit_item(self, e: ft.TapEvent):
        print(f"Edit item: {e.control.data}")
        # Implement edit item functionality here
        # For example, you can display a dialog to edit the item quantity
        # or remove the item from the cart
        # You can also implement a separate view for editing the cart items
        
        #implement a function that display ft.Buttomsheet with quantity selector, and a confirm button that changes the quantity of the item in the cart
        #and a delete button that removes the item from the cart
        #the function should be called when the edit button is clicked
        #the function should update the cart dictionary in the Model class

        def bs_dismissed(e):
            print("Dismissed!")

        global close_bs

        def close_bs(e):
            bs.open = False
            bs.update()
            self.cart_items.controls.clear()
            self.create_cart()
            self.page.update()

        bs = ft.BottomSheet(
            ft.Container(
                ft.Row(
                    [
                        ft.Text("編輯數量"),
                        QuantitySelector(n=e.control.data),
                        ft.ElevatedButton("確認", on_click=close_bs),
                    ],
                    alignment="spaceBetween",
                ),
                padding=10,
            ),
            open=True,
            on_dismiss=bs_dismissed,
        )

        self.page.overlay.append(bs) # Add the bottom sheet to the overlay
        self.page.update()

