from flet import padding
base_height = 900
base_width = 420
btn_width = 350
btn_height = 50
br = 30
bnt_size = 9
base_color = '#1b1517'
input_fill_color = "#ffffff"
base_green = "#01c38e"
light_green = "#e5f8f2"
input_hint_color = '#75797c'
content_padding = padding.only(left=20,top=10,right=10,bottom=10)
input_error_bg = "#f8c1bc"
input_error_outline = "#cb1a2a"
img_src ='https://pbs.twimg.com/profile_images/1767397257286971392/QZ6esgMQ_400x400.jpg'

class current_user:
   def __init__(self):
      self.isloggedin = False
      self.name = None
      self.id = None

current_user_instance = current_user()