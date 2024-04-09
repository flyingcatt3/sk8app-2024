import flet as ft 
import psycopg2
from psycopg2 import sql

def main(page: ft.Page) -> None:
    page.title="Login"    
    page.horizontal_alignment="center"
    page.vertical_alignment="center"
    page.theme_mode="dark"
    page.window_width=600
    page.window_height=1080
    page.snack_bar = ft.SnackBar(ft.Text("你輸入的帳號已存在", size=20))

    def validate(e) -> None:
        if all([user_name.value, account.value, password.value, checkboxsignup.value]):
            button_submit.disabled=False
        else:
            button_submit.disabled=True
        page.update()
        
    def submit(e) -> None:
        print("submit 函數被觸發")
        print('User Name:', user_name.value)
        print('Account:', account.value)
        print('Password:', password.value)
        
        # 將資料寫入PostgreSQL資料庫
        conn = psycopg2.connect(
            dbname='root', 
            user='lazzicat', 
            password='84ZI9ICIbfflZU3DZF9i', 
            host='sk8app-2024.ch2aea0k4vpx.ap-northeast-1.rds.amazonaws.com',
            port='2024'
        )   
        cur = conn.cursor()
        try:
            # 檢查帳號是否已存在
            cur.execute(
                sql.SQL("SELECT * FROM usr WHERE acc = %s"),
                (account.value,)
            )
            if cur.fetchone():
                # 如果帳號已存在，顯示錯誤訊息
                page.snack_bar.open = True
            else:
                # 如果帳號不存在，進行資料插入
                cur.execute(
                    sql.SQL("INSERT INTO usr(acc, pwd, name) VALUES (%s, %s, %s)"),
                    (account.value, password.value, user_name.value)
                )
                conn.commit()
                # 清理頁面並顯示歡迎訊息
                page.clean()
                page.add(
                    ft.Row(
                        controls=[
                            ft.Text(value=f'Welcome: {user_name.value}!', width=20), 
                        ],
                        alignment=ft.MainAxisAlignment.CENTER
                    )
                )
        except Exception as e:
            print("發生錯誤:", e)
        finally:
            cur.close()
            conn.close()
        
    user_name = ft.TextField(label="使用者名稱", text_align=ft.TextAlign.LEFT, width=200)
    account = ft.TextField(label="帳號", text_align=ft.TextAlign.LEFT, width=200)
    password = ft.TextField(label="密碼", text_align=ft.TextAlign.LEFT, width=200, password=True)
    checkboxsignup = ft.Checkbox(label="我同意使用條款", value=False)
    button_submit = ft.ElevatedButton(text='註冊', width=200, disabled=True,on_click=submit)
        
    checkboxsignup.on_change=validate
    user_name.on_change=validate
    account.on_change=validate
    password.on_change=validate
    
    page.add(
        ft.Row(
            controls=[
                ft.Column(
                    [user_name, account, password, checkboxsignup, button_submit]
                )
            ],
            alignment=ft.MainAxisAlignment.CENTER
        )
    )

ft.app(target=main)