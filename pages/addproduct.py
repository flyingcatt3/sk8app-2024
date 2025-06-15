import flet as ft
from firebase_admin import storage
from service.auth import connect_db
from datetime import datetime
from utils.extras import current_user_instance as _user
from page_instance import pageinstance

class AddProduct(ft.View):
    def __init__(self, page: ft.Page):
        super(AddProduct,self).__init__(route="/addProduct")
        self.page = page
        self.horizontal_alignment = "center"
        self.uploaded_image=""
        self.conn = connect_db()
        self.cur = self.conn.cursor()
        self.main()

    def main(self):
        def add_product(e):
            print("AddProduct: Button clicked")
            
            # 取得商品名稱、價格和描述
            product_name = self.product_name_input.value
            product_price = self.product_price_input.value
            product_description = self.product_description_input.value

            product_uid = _user.id
            product_time = datetime.now()
            product_status = 'True'
            
            # 構建商品資料
            new_product = {
                "uid": product_uid,
                "name": product_name,
                "description": product_description,
                "price": product_price,
                "time": product_time,
                "status": product_status,
                "img_src": self.uploaded_image,
            }
            
            # 將商品資料插入資料庫
            try:
                query = """
                INSERT INTO product (uid, name, description, price, time, status, img)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                RETURNING id
                """
                self.cur.execute(query, (
                    new_product["uid"], new_product["name"], new_product["description"],
                    new_product["price"], new_product["time"], new_product["status"],
                    [new_product["img_src"]]
                ))
                self.conn.commit()
            
                # 提示商品已新增
                print("商品已新增！")

                self.page.go("/products")
                
            except Exception as ex:
                self.conn.rollback()  # 發生錯誤時回滾交易
                print(f"An error occurred: {ex}")

        def upload_image(image_path, storage_path):
            # 取得 Firebase 存儲桶
            bucket = storage.bucket()

            # 創建一個 Blob 物件，指定存儲路徑
            blob = bucket.blob(storage_path)

            # 上傳圖片
            blob.upload_from_filename(image_path)

            # 設置 Blob 的存取權限為公開
            blob.make_public()

            # 返回圖片的公開 URL
            return blob.public_url

        def pick_files_result(e: ft.FilePickerResultEvent):
            if e.files:
                file = e.files[0]
                # 將圖片上傳到 Firebase 並取得圖片 URL
                self.uploaded_image = upload_image(file.path, f"market/{file.name}")
                print(self.uploaded_image)
                selected_files.value = file.name
                selected_files.update()
                
            else:
                self.uploaded_image = ""

        pick_files_dialog = ft.FilePicker(on_result=pick_files_result)
        #pick_files_dialog.get_directory_path()
        pick_files_dialog.file_type=ft.FilePickerFileType.IMAGE
        selected_files = ft.Text()

        self.page.overlay.append(pick_files_dialog)

        self.product_name_input=ft.TextField(label="商品名稱", width=self.page.window_width-100, height=100)
        self.product_price_input=ft.TextField(label="商品價格", width=self.page.window_width-100, height=100)
        self.product_description_input=ft.TextField(label="商品描述", width=self.page.window_width-100, height=100,max_lines=10,multiline=True)
        self.image_input=ft.Row(
            [
            ft.ElevatedButton(
                text="上傳商品圖片",
                icon=ft.icons.UPLOAD_FILE,
                on_click=lambda _: pick_files_dialog.pick_files(
                    #allow_multiple=True
                ),
                width=self.page.window_width-100,
            ),
            selected_files,
            ],alignment="center"
        )

        self.controls=[
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
            ft.Text("上架商品申請表單", size=32),
            ft.Text("填寫表單後，我們會盡快審核您的商品資訊。", size=16),
            self.product_name_input,
            self.product_price_input,
            self.product_description_input,
            ft.Divider(height=4, color="transparent"),
            self.image_input,
            ft.ElevatedButton(content=ft.Text("提交", size=20), width=self.page.window_width-100, height=100, style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=20)), on_click=add_product, data=1)
            ]
    