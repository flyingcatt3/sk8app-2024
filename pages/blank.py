import flet as ft

class Blank(ft.View):
    def __init__(self, page: ft.Page):
        super(Blank,self).__init__()
        self.page = page