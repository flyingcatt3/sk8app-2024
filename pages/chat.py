import flet as ft  # 導入 Flet 庫,用於建構 GUI 應用程式介面
import time  # 導入 time 庫,用於處理時間相關功能
import os  # 導入 os 庫,用於與作業系統互動
import random  # 導入 random 庫,用於產生隨機數值
from google import generativeai as genai  # 從 google 模組導入 generativeai 函式庫,用於訪問 Google AI 服務
from dotenv import load_dotenv  # 導入 dotenv 庫,用於從 .env 文件中載入環境變數
from langchain.vectorstores.chroma import Chroma  # 從 langchain.vectorstores.chroma 導入 Chroma 類別,用於創建向量存儲
from langchain_community.embeddings import CohereEmbeddings  # 從 langchain_community.embeddings 導入 CohereEmbeddings 類別,用於生成文本嵌入
from langchain_google_genai import ChatGoogleGenerativeAI  # 從 langchain_google_genai 導入 ChatGoogleGenerativeAI 類別,用於與 Google AI 聊天
from langchain.prompts import ChatPromptTemplate  # 從 langchain.prompts 導入 ChatPromptTemplate 類別,用於創建聊天提示模板

# 定義常量
CHROMA_PATH = "chroma"  # 向量存儲的路徑
DATA_PATH = "data/redbull"  # 數據路徑
COHERE_API_KEY = "0X7IQsghxQVYwVdnC4C2nMgpX5xx4i2yGeYsuIN6"  # Cohere API 密鑰
embeddings = CohereEmbeddings(model="embed-multilingual-v3.0", cohere_api_key=COHERE_API_KEY)  # 初始化 CohereEmbeddings 對象
PROMPT_TEMPLATE = """
你是帕魯,一位滑板AI助理。你的任務是回答滑板相關的問題,但也可以參與其他的話題。
---
Context:
{context}
Context僅做為參考,回答一般問題時無須考慮到Context是否提到與問題相關的資訊,需運用自己對於問題的理解回答。
但如果是與滑板相關的問題,盡可能運用Context提供的資訊回答,並以Markdown格式回答問題,可以視情況改變字體大小。
請注意,不要編造事實。
使用繁體中文回答問題: {question}
---
"""  # 定義提示模板

# 定義示例問題列表
pL1 = ["能介紹在台灣有哪些專業的滑板場地嗎?",
       "在台灣哪些城市有室內滑板場地？"] # 滑板場地情報
pL2 = ["最近一個月內有沒有即將舉辦的滑板活動?",
       "有沒有台灣滑板比賽的最新消息？"]# 滑板近期活動
pL3 = ["請寫一篇文章介紹滑板這個運動的歷史,陳述方式要清晰、簡潔、有條理,最好還能包含幾個有趣的小知識,這樣比較能激發讀者的好奇心。",
       "滑板這項運動的起源是什麼？",
       "哪些著名的滑板選手曾經影響了這項運動的發展？",
       "滑板文化在台灣的興起和發展史有哪些里程碑事件？",
       "滑板板材的演變史及其對滑板運動的影響是什麼？",
       "有哪些有趣的滑板迷因或流行語來自於這個社群？"]# 滑板知識
pL4 = ["有甚麼推薦的滑板招式?",
       "如何進行基本的滑板轉彎？",
       "學習滑板的哪些姿勢或技巧有助於提高平衡能力？",
       "如何在滑板上進行基本的跳躍動作？",
       "如何掌握kickflip、no comply等高級技巧？",
       "有沒有針對滑板初學者的練習技巧建議？"]# 滑板技巧
pL5 = ["我想買一個滑板,有甚麼推薦的品牌或型號?",
       "想要入門的滑板手應該選擇哪種類型的滑板？",
       "除了滑板本身，有哪些必備配件或保護裝備？",
       "在台灣購買滑板時應該注意哪些品牌或商店？"]# 滑板選購指南"

load_dotenv()  # 載入 .env 文件中的環境變數
google_api_key = os.getenv('GOOGLE_API_KEY')  # 獲取 Google API 密鑰
safety_settings_NONE = [
    {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
    {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
    {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
    {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"}
]  # 定義安全設置,不對內容進行過濾

# 定義主要樣式
def main_style() -> dict:
    return {
        "width": 800,
        "height": 600,
        "bgcolor": "#141518",
        "border_radius": 10,
        "padding": 20,
    }

# 定義提示框樣式
def prompt_style() -> dict:
    return {
        "width": 330,
        "height": 45,
        "border_color": "white",
        "content_padding": 10,
        "cursor_color": "white",
    }

# 定義主內容區域
class MainContentArea(ft.Container):
    def __init__(self) -> None:
        super().__init__(**main_style())
        self.chat = ft.ListView(
            expand=True,
            height=300,
            spacing=15,
            auto_scroll=True,
        )

        self.content = self.chat

# 定義消息創建類
class CreateMessage(ft.Column):
    def __init__(self, name: str, message: str) -> None:
        self.name: str = name
        self.message: str = message
        if name == "帕魯":
            self.text = ft.Markdown(self.message, selectable=True, on_tap_link=lambda e: self.launch_url(e.data), extension_set=ft.MarkdownExtensionSet.GITHUB_WEB,)
        else:
            self.text = ft.Text(self.message, size=20)
        super().__init__(spacing=4)
        self.controls = [ft.Text(self.name, opacity=0.6, size=16), self.text]

# 定義提示框類
class Prompt(ft.TextField):
    def __init__(self, chat: ft.ListView) -> None:
        super().__init__(**prompt_style(), on_submit=self.run_prompt)
        self.chat: ft.ListView = chat
        self.adaptive = True
        self.hint_text = "在這裡輸入提示,例如：滑板怎麼玩？"
        self.text_size = 20
        self.border_radius = 15
        self.cursor_color = ft.colors.BLUE_200
        self.multiline = True
        self.content_padding = 7
        self.min_lines = 1
        self.max_lines = 3

    # 定義動畫文本輸出方法
    def animate_text_output(self, name: str, prompt: str):
        word_list: list = []
        msg = CreateMessage(name, prompt)
        self.chat.controls.append(msg)

        for word in list(prompt):
            word_list.append(word)
            msg.text.value = "".join(word_list)
            self.chat.update()
            time.sleep(0.008)

    # 定義用戶輸出方法
    def user_output(self, prompt):
        self.animate_text_output(name="Me", prompt=prompt)

    # 定義 GPT 輸出方法
    def gpt_output(self, prompt):
        print(f"Query text: {prompt}")

        # 準備數據庫
        embedding_function = CohereEmbeddings(model="embed-multilingual-v3.0", cohere_api_key=COHERE_API_KEY)
        db = Chroma(persist_directory=CHROMA_PATH, embedding_function=embedding_function)
        #retriever_mmr = db.as_retriever(search_type="mmr",k=5)
        #docs_mmr = retriever_mmr.get_relevant_documents(query_text)

        # 搜索數據庫
        results = db.similarity_search_with_relevance_scores(prompt, k=3)

        if len(results) == 0 or results[0][1] < 0.5:
            #print(str(results[0][1]))
            print("INFO: [RAG]Unable to find matching results.")
            context_text = ""
        else:
            context_text = "\n\n---\n\n".join([doc.page_content for doc, _score in results])
        prompt_template = ChatPromptTemplate.from_template(PROMPT_TEMPLATE)
        prompt = prompt_template.format(context=context_text, question=prompt)
        #print(f"Prompt: {prompt}")

        # 初始化 ChatGoogleGenerativeAI 對象並生成回應
        model = ChatGoogleGenerativeAI(model="gemini-pro", google_api_key=google_api_key, temperature=0.5)
        model.client = genai.GenerativeModel(model_name='gemini-pro', safety_settings=safety_settings_NONE)
        response = ""
        for chunk in model.stream(prompt):
            response += chunk.content
        print(response)
        #sources = [doc.metadata.get("source", None) for doc, _score in results]
        #response += f"\n參考資料: {sources}"
        self.animate_text_output(name="帕魯", prompt=response)

    # 定義運行提示方法
    def run_prompt(self, event=None):
        text = prompt.value
        if len(text) >= 2:
            prompt.value = ""
            prompt.disabled = True
            pr.visible = True
            submitBtn.visible = False
            P.update()
            if len(prompt.chat.controls) == 0:
                P.remove_at(1)
                P.remove_at(1)
                P.remove_at(1)
                P.appbar = None
                P.add(chatList)
            prompt.user_output(prompt=text)
            prompt.gpt_output(prompt=text)
            prompt.disabled = False
            pr.visible = False
            submitBtn.visible = True
            P.update()
        else:
            P.snack_bar.open = True
            P.update()
class Chat(ft.View):
    
    def __init__(self, page: ft.Page):
        super(Chat, self).__init__()
        #self.page = page
        self.main(page)
        
# 定義主程序
    def main(self, page: ft.Page) -> None:
        def btnClick(e):
            prompt.value = randomPrompt(e.control.data)
            prompt.update()
            #print(e.control.data)

        def randomPrompt(op):
            if op == 1:
                return random.choice(pL1)
            elif op == 2:
                return random.choice(pL2)
            elif op == 3:
                return random.choice(pL3)
            elif op == 4:
                return random.choice(pL4)
            else:
                return random.choice(pL5)

        global P,chatList,pr,submitBtn,prompt

        P=page
        P.horizontal_alignment = "center"
        P.theme_mode = "dark"
        P.title = "帕魯 - 你的滑板AI助理"
        P.window_height = 1080
        P.appbar = ft.AppBar(
            title=ft.Text(value="帕魯 - 你的滑板AI助理", size=28, theme_style="BOLD"),
            center_title=True
        )
        P.snack_bar = ft.SnackBar(ft.Text("請至少輸入2個字元以上的提示", size=20))

        chatList = MainContentArea()
        prompt = Prompt(chat=chatList.chat)
        pr = ft.ProgressRing()
        submitBtn = ft.IconButton(icon=ft.icons.SEND, on_click=prompt.run_prompt, data=0)
        pr.visible = False
        input = ft.BottomAppBar(
            content=ft.Row([prompt, submitBtn, pr], alignment="CENTER", width=P.window_width),
            bgcolor=ft.colors.with_opacity(0.5, "#181818")
        )

        btn1 = ft.ElevatedButton(content=ft.Text("板點情報", size=20), width=300, height=300, style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=20)), on_click=btnClick, data=1)
        btn2 = ft.ElevatedButton(content=ft.Text("近期活動", size=20), width=300, height=300, style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=20)), on_click=btnClick, data=2)
        btn3 = ft.ElevatedButton(content=ft.Text("滑板知識", size=20), width=300, height=300, style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=20)), on_click=btnClick, data=3)
        btn4 = ft.ElevatedButton(content=ft.Text("滑板技巧", size=20), width=300, height=300, style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=20)), on_click=btnClick, data=4)
        btn5 = ft.ElevatedButton(content=ft.Text("選購指南", size=20), width=300, height=300, style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=20)), on_click=btnClick, data=5)

        listBtn = ft.ListView(expand=1, horizontal=True, spacing=10)
        listBtn.controls.append(btn1)
        listBtn.controls.append(btn2)
        listBtn.controls.append(btn3)
        listBtn.controls.append(btn4)
        listBtn.controls.append(btn5)

        P.add(
            ft.Divider(height=1, color="transparent"),
            ft.Text(spans=[
                ft.TextSpan(
                    "你好\n有什麼我可以幫上忙的嗎？",
                    ft.TextStyle(
                        size=40,
                        weight=ft.FontWeight.BOLD,
                        foreground=ft.Paint(
                            gradient=ft.PaintLinearGradient(
                                (0, 20), (400, 20), ["#4b83ef", "#d96570"]
                            )
                        ),
                    ),
                ),
            ],
            ),
            ft.Divider(height=4, color="transparent"),
            listBtn,
            ft.Divider(height=2, color="transparent"),
            input
        )

        P.update()
'''
if __name__ == "__main__":
    ft.app(target=main)
'''