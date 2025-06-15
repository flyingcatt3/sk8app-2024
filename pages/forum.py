import flet as ft
from datetime import datetime
from utils.extras import current_user_instance as _user
from service.auth import connect_db
from firebase_admin import storage

#implement a function to get username from uid
def get_username(uid):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM usr WHERE id = %s", (uid,))
    username = cursor.fetchone()
    cursor.close()
    conn.close()
    return username[0] if username else None

def time_ago(time_str: str):
    # 解析時間字串為 datetime 對象
    time = datetime.fromisoformat(time_str.replace("+00", "+08"))
    
    # 獲取當前時間
    now = datetime.now().astimezone()
    
    # 計算時間差
    delta = now - time
    
    # 獲取時間差的總秒數
    seconds = delta.total_seconds()
    
    # 計算分鐘、小時和天數
    minutes = seconds // 60
    hours = minutes // 60
    days = hours // 24
    
    # 根據時間差返回相應的格式
    if days > 7:
        return time.strftime('%Y-%m-%d')
    elif days >= 1:
        return f"{int(days)}天前"
    elif hours >= 1:
        return f"{int(hours)}小時前"
    elif minutes >= 1:
        return f"{int(minutes)}分鐘前"
    else:
        return "剛剛"

class ForumPage(ft.View):
    def __init__(self, page: ft.Page):
        super(ForumPage,self).__init__()
        self.page = page
        self.board_mapping = {
            "全部": 1,
            "Hardware": 2,
            "Lifestyle": 3,
            "奧運": 4,
            "Skater相關": 5,
        }
        self.current_board = "全部"
        self.conn = connect_db()
        self.cur = self.conn.cursor()
        self.main()

    def main(self):
        #self.page.title = "論壇"

        # 看板選單
        self.board_dropdown = ft.Dropdown(
            label="選擇看板",
            value=self.current_board,
            options=[ft.dropdown.Option(board) for board in self.board_mapping.keys()],
            on_change=self.change_board
        )

        self.page.appbar = ft.AppBar(
            title=ft.Text("論壇"),
            actions=[self.board_dropdown]
        )
        self.page.appbar.visible = False

        self.page.floating_action_button=ft.FloatingActionButton(
            icon=ft.icons.UPLOAD, on_click=self.open_publish_page, bgcolor=ft.colors.BLACK38)
        self.page.floating_action_button.visible = False

        self.article_list=ft.ListView(expand=1,spacing=10, padding=20)

        self.ads=ft.Container(
            content=ft.Image("https://firebasestorage.googleapis.com/v0/b/backend2023mis.appspot.com/o/329941721_190054193711213_8528955829475625135_n.jpg?alt=media&token=6a4dd22c-e130-4a47-b68c-2ec6e5b5aa61"),
            url="https://www.instagram.com/9ceskateshop/p/CobUCemv0Xk/",
            image_fit=ft.ImageFit.CONTAIN,
            width=self.article_list.width,
            height=200,
            expand=1)
        #self.article_list.controls.append(self.ads)
        self.controls = [self.page.appbar,self.article_list,self.page.floating_action_button]
        
        self.view_posts()

    def view_posts(self):
        if not _user.isloggedin:
            return 1
        board_type = self.board_mapping[self.current_board]
        self.cur.execute("SELECT * FROM post WHERE type=%s ORDER BY time DESC", (board_type,))
        posts = self.cur.fetchall()
        for post in posts:
            # 檢查 post[7] 是否為 None，並將其設為空列表如果是 None
            likes = post[7] if post[7] is not None else []
            current_user_uid = _user.id
            user_liked = current_user_uid in likes
            #print(user_liked)
            post_control = ft.Column(controls=[
                ft.Text(f"{post[2]}",size=20,weight=ft.FontWeight.BOLD),
                ft.Text(f"{post[3]}"),#Article
                ft.Image(
                    src=f"{post[6]}",  # 圖片 URL
                    width=self.page.window_width-100,
                    fit=ft.ImageFit.CONTAIN,
                    border_radius=ft.border_radius.all(10)
                ),
                ft.Row(controls=[
                    ft.TextButton("Reply", on_click=lambda e, post_id=post[8]: self.reply_post(e, post_id)),
                    ft.TextButton("Unlike" if user_liked else "Like", on_click=lambda e, post_id=post[8]: self.toggle_like_post(e, post_id)),
                    # 顯示文章的讚數
                    ft.Text(f"{len(likes) if likes else ""}"),
                    # 顯示文章發布時間
                    ft.Text(f"{time_ago(str(post[4]))}"),
                    # 顯示文章作者
                    ft.Text(f" 由 {get_username(post[0])}", weight=ft.FontWeight.BOLD),
                ]),
            ])
            if post[6]=="":
                post_control.controls.pop(-2)

            replies = self.get_replies(post[8])
            for reply in replies:
                reply_control1 = ft.Row(controls=[
                    ft.Text(f"{get_username(reply[0])}", size=16, weight=ft.FontWeight.BOLD, color=ft.colors.WHITE),
                    ft.Text(f"{time_ago(str(reply[4]))}", size=12, color=ft.colors.WHITE)
                ])
                reply_control2 = ft.Row([ft.Text(f"{reply[3]}",color=ft.colors.WHITE)])
                reply_stack=ft.Column(
                    [
                        ft.Container(content=reply_control1,bgcolor="#292628",border_radius=ft.border_radius.only(5,5,0,0),margin=ft.margin.only(left=20),padding=ft.padding.only(10,10,10,0)),
                        ft.Container(content=reply_control2,bgcolor="#292628",border_radius=ft.border_radius.only(0,0,5,5),margin=ft.margin.only(left=20),padding=ft.padding.only(10,0,10,10))
                    ],spacing=0
                )
                post_control.controls.append(reply_stack)
            self.article_list.controls.append(post_control)
            self.article_list.controls.append(ft.Divider(color=ft.colors.GREY_300,thickness=2,opacity=0.5))
            self.page.appbar.visible = True
            self.page.floating_action_button.visible = True

    def get_replies(self, post_id):
        self.cur.execute("SELECT * FROM post WHERE type = %s ORDER BY time DESC", (-post_id,))
        replies = self.cur.fetchall()
        return replies

    def update_post_control(self):
        self.article_list.controls.clear()
        self.article_list.controls.append(self.ads)
        self.article_list.controls.append(ft.Divider(color=ft.colors.GREY_300,thickness=2,opacity=0.5))
        self.view_posts()
        self.page.update()

    def change_board(self, e):
        print(self.board_dropdown.value)
        if self.current_board != self.board_dropdown.value:
            self.current_board = self.board_dropdown.value
            self.update_post_control()

    def reply_post(self, e, post_id):
        def close_bs(e):
            current_user_uid = _user.id
            article=reply_content.value
            type=-post_id

            try:
                self.cur.execute(
                "INSERT INTO post (uid, type, title, article, time) VALUES (%s, %s, %s, %s, %s)",
                (current_user_uid, type, '', article, datetime.now())
                #datetime.now().astimezone(timezone(timedelta(hours=8), 'Taiwan'))
            )
                self.conn.commit()
            except Exception as ex:
                self.conn.rollback()
                print(f"An error occurred: {ex}")

            reply_sheet.open = False
            reply_sheet.update()
            self.update_post_control()

        # Create a Buttomsheet for reply
        reply_sheet = ft.BottomSheet(open=True)

        # Add fields for reply content
        reply_content = ft.TextField(label="Reply", max_lines=5, multiline=True)

        # Add a button to submit the reply
        submit_button = ft.ElevatedButton('送出', on_click=close_bs)

        reply_sheet.content=ft.Row([reply_content,submit_button])

        self.page.overlay.append(reply_sheet) # Add the bottom sheet to the overlay
        self.page.update()

    def toggle_like_post(self, e, post_id):
        current_user_uid = _user.id  # 此處替換為實際的使用者UID
        try:
            # 檢查當前的讚狀態
            self.cur.execute("SELECT like_uid FROM post WHERE id=%s", (post_id,))
            likes = self.cur.fetchone()[0] or []
            
            if current_user_uid in likes:
                # 使用者已經按下讚，執行取消讚操作
                self.cur.execute("UPDATE post SET like_uid = array_remove(like_uid, %s) WHERE id=%s", (current_user_uid, post_id))
            else:
                # 使用者未按下讚，執行按讚操作
                self.cur.execute("UPDATE post SET like_uid = array_append(like_uid, %s) WHERE id=%s", (current_user_uid, post_id))
            
            self.conn.commit()
        except Exception as ex:
            self.conn.rollback()  # 發生錯誤時回滾交易
            print(f"An error occurred: {ex}")
        finally:
            self.update_post_control()

    def open_publish_page(self, e):
        self.page.go("/publish")

class PublishPage(ft.View):
    def __init__(self, page: ft.Page):
        super(PublishPage,self).__init__()
        self.page = page
        self.board_mapping = {
            "全部": 1,
            "Hardware": 2,
            "Lifestyle": 3,
            "奧運": 4,
            "Skater相關": 5,
        }
        self.conn = connect_db()
        self.cur = self.conn.cursor()
        self.horizontal_alignment = "center"
        self.main()

    def main(self):
        #self.page.title = "發布文章"
        
        self.title_input = ft.TextField(label="標題")
        self.article_input = ft.TextField(label="文章內容",max_lines=10,multiline=True)
        self.board_dropdown = ft.Dropdown(
            label="選擇看板",
            options=[ft.dropdown.Option(board) for board in self.board_mapping.keys()]
        )
        self.uploaded_image=""

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
                self.uploaded_image = upload_image(file.path, f"forum/{file.name}")
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
        self.image_input = ft.Column(
                [
                ft.ElevatedButton(
                    text="上傳圖片",
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
                        on_click=lambda e: self.page.go("/forum"),
                        icon_size=16,
                    )
                ],
                alignment="spaceBetween",
            ),
            ft.Text("發布文章", size=32),
            ft.Column(
                controls=[
                    self.title_input,
                    self.article_input,
                    self.board_dropdown,
                ]
            ),
            self.image_input,
            ft.ElevatedButton(content=ft.Text("發布", size=20), width=self.page.window_width-100, height=100, style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=20)), on_click=self.publish_article, data=1)
        ]

    def publish_article(self, e):
        title = self.title_input.value
        article = self.article_input.value
        board = self.board_dropdown.value
        board_type = self.board_mapping.get(board)  # 將看板名稱轉換為對應的整數值
        image = self.uploaded_image
        current_user_uid = _user.id  # 此處替換為實際的使用者UID
        try:
            self.cur.execute(
                "INSERT INTO post (uid, type, title, article, time, img) VALUES (%s, %s, %s, %s, %s, %s)",
                (current_user_uid, board_type, title, article, datetime.now(), image)
                #datetime.now().astimezone(timezone(timedelta(hours=8), 'Taiwan'))
            )
            self.conn.commit()
            self.page.go("/forum")
        except Exception as ex:
            self.conn.rollback()  # 發生錯誤時回滾交易
            print(f"An error occurred: {ex}")

