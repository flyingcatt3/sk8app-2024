from flet import *
import pickle
from utils.extras import *
from pages.mainpage import MainPage
from pages.login import LoginPage
from pages.signup import SignupPage
from pages.market import Product,Cart
from pages.forum import ForumPage
from pages.chat import Chat
from pages.addproduct import AddProduct
from pages.forum import PublishPage
from pages.blank import Blank
from service.auth import get_user,authenticate, verify_token, register_user, is_valid_email, connect_db
from utils.extras import current_user_instance as _user
from page_instance import pageinstance
import asyncio

def get_user_id(email):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM usr WHERE acc = %s", (email,))
    user_id = cursor.fetchone()
    cursor.close()
    conn.close()
    return user_id[0] if user_id else None

def register_user_pg(name, email, password):
    user_id = get_user_id(email)
    if user_id:
        _user.id = user_id
        return user_id  # 用戶已存在，返回該用戶的 ID

    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO usr (name, acc, pwd) VALUES (%s, %s, %s)
    """, (name, email, password))
    conn.commit()
    cursor.close()
    conn.close()
    user_id = get_user_id(email)
    _user.id = user_id
    return user_id

async def save_token(token):
  try:
    with open("token.pkl", "wb") as f:
      pickle.dump(token, f)
    return 'Saved'
  except:
    return None 

async def load_token():
  try:
    with open("token.pkl", "rb") as f:
      stored_token = pickle.load(f)
    return stored_token
  except:
    return None

class App(UserControl):
  def __init__(self,pg:Page):
    super().__init__()

    #pg.window_title_bar_hidden = True
    #pg.window_frameless = True
    #pg.window_title_bar_buttons_hidden = True
    #pg.bgcolor = colors.TRANSPARENT
    #pg.window_bgcolor = colors.TRANSPARENT
    pg.vertical_alignment = MainAxisAlignment.CENTER
    pg.horizontal_alignment = "center"
    pg.fonts = {
    "SF Pro Bold":"fonts/SFProText-Bold.ttf",
    "SF Pro Heavy":"fonts/SFProText-Heavy.ttf",
    "SF Pro HeavyItalic":"fonts/SFProText-HeavyItalic.ttf",
    "SF Pro Light":"fonts/SFProText-Light.ttf",
    "SF Pro Medium":"fonts/SFProText-Medium.ttf",
    "SF Pro Regular":"fonts/SFProText-Regular.ttf",
    "SF Pro Semibold":"fonts/SFProText-Semibold.ttf",
    "SF Pro SemiboldItalic":"fonts/SFProText-SemiboldItalic.ttf",
    
    
    "Poppins ThinItalic":"fonts/poppins/Poppins-ThinItalic.ttf",
    "Poppins Thin":"fonts/poppins/Poppins-Thin.ttf",
    "Poppins Semibold":"fonts/poppins/Poppins-Semibold.ttf",
    "Poppins SemiboldItalic":"fonts/poppins/Poppins-SemiboldItalic.ttf",
    "Poppins Regular":"fonts/poppins/Poppins-Regular.ttf",
    "Poppins MediumItalic":"fonts/poppins/Poppins-MediumItalic.ttf",
    "Poppins Medium":"fonts/poppins/Poppins-Medium.ttf",
    "Poppins LightItalic":"fonts/poppins/Poppins-LightItalic.ttf",
    "Poppins Light":"fonts/poppins/Poppins-Light.ttf",
    "Poppins Italic":"fonts/poppins/Poppins-Italic.ttf",
    "Poppins ExtraLightItalic":"fonts/poppins/Poppins-ExtraLightItalic.ttf",
    "Poppins ExtraLight":"fonts/poppins/Poppins-ExtraLight.ttf",
    "Poppins ExtraBold":"fonts/poppins/Poppins-ExtraBold.ttf",
    "Poppins ExtraBoldItalic":"fonts/poppins/Poppins-ExtraBoldItalic.ttf",
    "Poppins BoldItalic":"fonts/poppins/Poppins-BoldItalic.ttf",
    "Poppins Bold":"fonts/poppins/Poppins-Bold.ttf",
    "Poppins BlackItalic":"fonts/poppins/Poppins-BlackItalic.ttf",
    "Poppins Black":"fonts/poppins/Poppins-Black.ttf",
  }
    pg.window_width = base_width
    pg.window_height = base_height

    #pg.go("/")

    auth = asyncio.run(verify_token(asyncio.run(load_token())))
    self.pg  = pg
    self.pg.spacing = 0
    self.delay = 0.1
    self.anim = animation.Animation(300,AnimationCurve.EASE_IN_OUT_CUBIC)

    self.main_page = MainPage(self.switch_page)
    
    self.screen_views = Stack(
        expand=True,
        controls=[
          self.main_page
        ]
      )

    self.init_helper()

    def displayNavigationBar():
      def navigate(e):
          # Get the index of the selected destination
          i = e.control.selected_index
          print(i)
          if i==0:
              #self.page.route = "/products"
              pg.go("/products")
          elif i==1:
              #self.Page.route = "/chat"
              pg.go("/chat")
          else:
              #self.Page.route = "/forum"
              pg.go("/forum")
          return
      
      return NavigationBar(
          destinations=[
              NavigationDestination(icon=icons.SHOP, label="賣場"),
              NavigationDestination(icon=icons.CHAT, label="Chat"),
              NavigationDestination(
                  icon=icons.BOOK_ONLINE_SHARP,
                  selected_icon=icons.BOOK_ONLINE_OUTLINED,
                  label="論壇",
              ),
          ],
          on_change=navigate
      )
    self.pg.navigation_bar = displayNavigationBar()
    self.pg.navigation_bar.visible = False

    products = Product(self.pg)
    chat = Chat(self.pg)
    forum = ForumPage(self.pg)
    publish_page = PublishPage(self.pg)
    add_product = AddProduct(self.pg)
    pageinstance.instance=[products,chat,forum,publish_page,add_product]
    
    def router(e: RouteChangeEvent) -> None:
      self.pg.views.clear()

      if self.pg.route == "/cart":
        cart = Cart(self.pg)
        self.pg.views.append(cart)
        cart.navigation_bar = self.pg.navigation_bar

      elif self.pg.route == "/products":
        self.pg.views.append(products)

      elif self.pg.route == "/chat":
        #pg.views.append(chat)
        self.pg.views.append(chat)
        chat.navigation_bar = self.pg.navigation_bar
      
      elif self.pg.route == "/forum":
        forum.navigation_bar = self.pg.navigation_bar
        self.pg.views.append(forum)

      elif self.pg.route == "/publish":
        publish_page.navigation_bar = self.pg.navigation_bar
        self.pg.views.append(publish_page)

      elif self.pg.route == "/addProduct":
        add_product.navigation_bar = self.pg.navigation_bar
        self.pg.views.append(add_product)

      elif self.pg.route == "/updateForumPosts":
        forum.view_posts()
        self.pg.route="/products"
        self.pg.navigation_bar.visible = True

      self.pg.update()
      
      print(self.pg.route)
      print(self.pg.views)
      print(self.pg.controls)

    pg.on_route_change = router

  def switch_page(self,e):
    if e.control.data == 'register':
      self.pg.add(ProgressBar(width=400, color="amber", bgcolor="#eeeeee"))
      name = self.signup_page.name_box.value
      password = self.signup_page.password_box.value
      email = self.main_page.email_input.content.value
      if len(password) < 6:
        print('Password must be at least 6 characters')
        #self.signup_page.password_box.bgcolor = input_error_bg
        self.signup_page.password_box.border=border.all(width=2, color=input_error_outline)
        self.signup_page.password_error.visible = True 
      else:
        self.signup_page.password_error.visible = False
        user = register_user(name, email, password)
        register_user_pg(name,email,password)
        self.screen_views.controls.clear()
        _user.name=name
        print(_user.name)
        print(_user.id)
        self.pg.route="/updateForumPosts"
        self.pg.update()

      self.pg.controls.pop()
      self.pg.update()
    elif e.control.data == 'process_login':
      email = self.main_page.email_input.content.value
      if is_valid_email(email):
        user = get_user(email)
        if user:
          id = user[0]
          self._name = user[1]
          _user.name = user[1]
          self._email = user[2]
          self.screen_views.controls.clear()
          self.login_page = LoginPage(self.switch_page,name=self._name,email=self._email,dp='')
          # self.login_page.content.on_focus = self.hide_error
          self.screen_views.controls.append(self.login_page)
          self.screen_views.update()
        else:
          self.screen_views.controls.clear()  
          self.signup_page = SignupPage(self.switch_page,email)
          self.screen_views.controls.append(self.signup_page)
          self.screen_views.update()
      else:
        self.main_page.email_input.bgcolor = input_error_bg
        self.main_page.email_input.border = border.all(width=2,color=input_error_outline)
        
        self.main_page.main_content.controls.insert(1,self.main_page.error)

        self.main_page.update()
        # self.main_page.email_input.update()
        
    elif e.control.data == 'main_page':
      self.screen_views.controls.clear()
      self.screen_views.controls.append(self.main_page)
      self.screen_views.update()
      
    elif e.control.data == 'login_clicked':
      self.pg.add(ProgressBar(width=400, color="amber", bgcolor="#eeeeee"))
      self.login_page.pwd_input.disabled = True
      password = self.login_page.pwd_input.content.value
      email = self.login_page.email

      auth = authenticate(email,password)
      
      if auth:
        asyncio.run(save_token(auth))
        #self.screen_views.controls.clear()
        _user.id=get_user_id(email)
        _user.isloggedin = True
        print(_user.name)
        print(_user.id)
        self.pg.route="/updateForumPosts"
        self.pg.update()

      else:
        self.login_page.pwd_input.disabled = False
        self.pg.controls.pop()
        self.pg.update()
        self.login_page.login_box.controls.insert(4,self.login_page.error)  
        self.login_page.pwd_input.bgcolor = input_error_bg
        self.login_page.pwd_input.border=border.all(width=2, color=input_error_outline)
        self.login_page.pwd_input.update()
        self.login_page.login_box.update()

    elif e.control.data == 'logout':
      try:
        os.remove('token.pkl')  
      except:
        pass
      self.screen_views.controls.clear()
      self.screen_views.controls.append(self.main_page)
      self.screen_views.update()

  def init_helper(self):
    self.pg.add(
      self.screen_views 
    )

app(target=App,assets_dir='assets')