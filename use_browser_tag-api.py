import os
import sys
import asyncio
from playwright.async_api import async_playwright
from openai import OpenAI
import time
from rapidocr_pdf import RapidOCRPDF
import requests
import json
import re
from readability import Document
from bs4 import BeautifulSoup
from markdownify import markdownify as md
from urllib.parse import urljoin
from typing import Optional
import hashlib
from urllib.parse import urljoin
import pdfkit


# Ollama API 配置
GET_TOKEN_URL='https://aitest.wintalent.cn/chat/getAccessToken'
pyload={ "appId":"test_max_propmpt",
        "securityKey":"WipDbZs8eHwWiawPM1nQiYSw1Rsf7RGW", 
        "corpCode":"testcorp",
        "userId":"testcorp-10001"
       }
LLM_API_BASE = "http://localhost:11434/v1"
LLM_MODEL_NAME = "Qwen3-8B-BF16.gguf" 
os.environ["OPENAI_API_KEY"] = "sk-no-key-required"

#服务器token
response=requests.post(GET_TOKEN_URL,json=pyload)
if response.status_code==200:
    print(response.json())
accesstoken=response.json()['data']['token']
CHAT_API_URL ="https://aitest.wintalent.cn/chat/completions/synchMsg"
headers = {"wintalentaiToken": accesstoken}


# 输入的榜单列表
RANKING_LIST = [
   {
    "name": "中国证券公司百强",
    "url": [
      "http://www.360doc.com/content/25/0308/12/76659663_1148438950.shtml",
      "https://finance.sina.com.cn/stock/quanshang/2025-07-22/doc-infhiuqq7221953.shtml",
      "https://finance.sina.com.cn/stock/observe/2025-07-23/doc-infhmxpq6263220.shtml"
    ]
  },
  {
    "name": "中国房地产百强企业成长性TOP10",
    "url": [
      "https://fdc.fang.com/news/zt/wap/202203/2022bq.html"
    ]
  },
  {
    "name": "中国房地产百强企业盈利性TOP10",
    "url": [
      "https://fdc.fang.com/news/zt/wap/202203/2022bq.html"
    ]
  },
  {
    "name": "中国房地产百强企业融资能力TOP10",
    "url": [
      "https://fdc.fang.com/news/zt/wap/202203/2022bq.html"
    ]
  },
  {
    "name": "中国房地产百强企业百强之星",
    "url": [
      "https://www.10guoying.com/bangdan/8808.html"
    ]
  }
]

def load_ranking_list_from_json(filename: str = "tag.json") -> list:
    """
    从指定的JSON文件加载榜单列表。
    
    Args:
        filename (str): JSON文件的路径.

    Returns:
        list: 包含榜单信息的字典列表.
    """
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            data = json.load(f)
            print(f"成功从 {filename} 加载了 {len(data)} 个榜单。")
            return data
    except FileNotFoundError:
        print(f"错误: JSON文件未找到 -> '{filename}'")
        print("请确保该文件与Python脚本在同一目录下。")
        sys.exit(1) # 退出程序，因为没有数据无法继续
    except json.JSONDecodeError as e:
        print(f"错误: JSON文件格式无效 -> '{filename}'")
        print(f"详细错误信息: {e}")
        sys.exit(1) # 退出程序

# 输出文件的根目录
OUTPUT_DIR = "web_rankings_pdf_output2"

# 自动滚动到底，触发懒加载或异步加载
async def auto_scroll(page):
    await page.evaluate("""
        async () => {
            await new Promise((resolve) => {
                let totalHeight = 0;
                const distance = 100;
                const timer = setInterval(() => {
                    const scrollHeight = document.body.scrollHeight;
                    window.scrollBy(0, distance);
                    totalHeight += distance;

                    if (totalHeight >= scrollHeight - window.innerHeight) {
                        clearInterval(timer);
                        resolve();
                    }
                }, 100);
            });
        }
    """)

async def save_page_as_pdf_later(url, output_path):
    print(f"  [+] 正在将网页保存为PDF: {url}")
    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context(
                user_agent=(
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/114.0.0.0 Safari/537.36"
                ),
                viewport={"width": 1920, "height": 1080},
                device_scale_factor=1,
                is_mobile=False,
                has_touch=False,
                locale="zh-CN"
            )

            # 注入脚本：去除 webdriver 特征
            await context.add_init_script(
                """Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"""
            )

            page = await context.new_page()
            await page.goto(url, wait_until='networkidle', timeout=90000)

            # 隐藏固定表头和导航栏，避免遮挡
            await page.add_style_tag(content="""
                header, nav, .navbar, .fixed-header {
                    display: none !important;
                }
            """)

            # 注入 CSS 隐藏固定的 header、nav、footer、悬浮按钮等
            await page.add_style_tag(content="""

                /* 屏蔽常见固定布局元素 */
                header, nav, footer,
                .fixed, .sticky, .float, .floating, .affix,
                .navbar, .sidebar, .topbar, .bottombar, .menu, .toolbar,
                .ad, .ads, .advert, .advertisement, .popup, .pop, .overlay,
                .modal, .banner, .cookie, .cookies, .subscribe, .newsletter,
                [class*="header"], [class*="footer"], [class*="nav"], [class*="bar"],
                [class*="menu"], [class*="popup"], [class*="overlay"], [class*="modal"],
                [class*="subscribe"], [class*="banner"], [class*="ad"], [class*="ads"],
                [class*="sticky"], [class*="float"], [class*="fixed"],
                [id*="header"], [id*="footer"], [id*="nav"], [id*="bar"],
                [id*="menu"], [id*="popup"], [id*="overlay"], [id*="modal"],
                [id*="subscribe"], [id*="banner"], [id*="ad"], [id*="ads"],
                [id*="sticky"], [id*="float"], [id*="fixed"],
                [class*="顶部"], [class*="底部"], [class*="导航"], [class*="菜单"],
                [id*="顶部"], [id*="底部"], [id*="导航"], [id*="菜单"],
                [style*="z-index: 999"], [style*="position: fixed"], [style*="position: sticky"]

            """)
            # await page.evaluate("""
            #     document.querySelectorAll('[class*="header"], [id*="popup"], .fixed, .sticky').forEach(el => el.remove());
            # """)


            # 滚动加载所有懒加载内容
            await auto_scroll(page)
            await page.pdf(
            path=output_path,
            format="A4",
            print_background=True,
            margin={"top": "1cm", "bottom": "1cm", "left": "1cm", "right": "1cm"}
            )
            await browser.close()
            print(f"  [+] PDF已保存至: {output_path}")
            return True

    except Exception as e:
        print(f"  [!] 保存PDF失败: {e}")
        return False


async def save_page_as_pdf(url, output_path):
    # 将wkhtmltopdf.exe程序绝对路径传入config对象
    path_wkthmltopdf = r'D:/Program Files/wkhtmltopdf/bin/wkhtmltopdf.exe'
    config = pdfkit.configuration(wkhtmltopdf=path_wkthmltopdf)
    print('url:',url)
    # 生成pdf文件，to_file为文件路径
    pdfkit.from_url(url, output_path, configuration=config) 
    return True


# from rapidocr import EngineType, LangDet, ModelType, OCRVersion, RapidOCR
# # ---params={"EngineConfig.onnxruntime.use_dml": True}
# pdf_extracter = RapidOCRPDF(ocr_params={
#         "EngineConfig.onnxruntime.use_dml": True,
#         # "Det.engine_type": EngineType.TORCH, 
#         "Det.lang_type": LangDet.CH,
#         "Det.model_type": ModelType.MOBILE,
#         "Det.ocr_version": OCRVersion.PPOCRV5})
# def ocr_pdf_to_text(pdf_path, poppler_path=None):
#     """
#     将PDF使用OCR提取所有文本。
#     这可以被视为调用一个本地的“OCR处理流程接口”。
#     """
#     print(f"  [+] 正在对PDF进行OCR处理: {pdf_path}")
#     if not os.path.exists(pdf_path):
#         print("  [!] PDF文件不存在，跳过OCR。")
#         return ""
        
#     try:
#         texts = pdf_extracter(pdf_path,force_ocr = True)
#         return texts
#     except Exception as e:
#         print(f"  [!] PDF OCR处理失败: {e}")
#         return ""

# def save_article_with_images(url: str, output_dir: str):
#     """
#     下载一篇文章，并将其中的图片本地化保存。

#     Args:
#         url (str): 文章的URL.
#         output_dir (str): 保存结果的目录.
#     """
#     headers = {
#         'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36'
#     }

#     try:
#         # 1. 获取原始网页内容
#         response = requests.get(url, headers=headers, timeout=30)
#         response.raise_for_status()
#         response.encoding = response.apparent_encoding
#         original_html = response.text
        
#         # 创建输出目录
#         images_dir = os.path.join(output_dir, 'images')
#         os.makedirs(images_dir, exist_ok=True)
        
#         # 2. 使用 readability-lxml 提取主要内容
#         doc = Document(original_html)
#         clean_html = doc.summary()
#         title = doc.title()

#         # 3. 使用 BeautifulSoup 解析干净的HTML，准备处理图片
#         soup = BeautifulSoup(clean_html, 'lxml')

#         # 4. 查找所有图片标签并处理
#         img_tags = soup.find_all('img')
#         print(f"在文章《{title}》中找到 {len(img_tags)} 张图片。")

#         for img_tag in img_tags:
#             # a. 获取图片URL
#             img_src = img_tag.get('src')
#             if not img_src:
#                 continue

#             # 处理 data: URI 格式的内嵌图片 (常见于一些小图标)
#             if img_src.startswith('data:image'):
#                 print(f"跳过内嵌图片 (data URI): {img_src[:60]}...")
#                 continue
            
#             # b. 将相对URL转换为绝对URL
#             absolute_img_url = urljoin(url, img_src)
            
#             try:
#                 # c. 生成一个唯一的本地文件名，避免冲突
#                 # 使用URL的MD5哈希值作为文件名主体，保留原始扩展名
#                 file_ext = os.path.splitext(absolute_img_url)[1].split('?')[0]
#                 if not file_ext: # 如果没有扩展名，默认为.jpg
#                     file_ext = '.jpg'
                
#                 hashed_name = hashlib.md5(absolute_img_url.encode()).hexdigest()
#                 local_filename = f"{hashed_name}{file_ext}"
#                 local_image_path = os.path.join(images_dir, local_filename)

#                 # d. 下载图片
#                 print(f"正在下载图片: {absolute_img_url} ...")
#                 img_response = requests.get(absolute_img_url, headers=headers, stream=True, timeout=20)
#                 img_response.raise_for_status()

#                 # 以二进制模式写入文件
#                 with open(local_image_path, 'wb') as f:
#                     for chunk in img_response.iter_content(chunk_size=8192):
#                         f.write(chunk)
                
#                 print(f"图片已保存到: {local_image_path}")

#                 # e. 修改<img>标签的src，指向本地文件
#                 # 使用相对路径，这样整个文件夹移动时也能正常显示
#                 relative_image_path = os.path.join('images', local_filename)
#                 img_tag['src'] = relative_image_path

#             except Exception as e:
#                 print(f"处理图片 {absolute_img_url} 时出错: {e}")
#                 # 如果下载失败，可以移除这个img标签或保留原始src
#                 # 这里选择保留，以便知道哪个图片失败了
#                 img_tag['src'] = f"DOWNLOAD_FAILED_{absolute_img_url}"

#         # 5. 保存修改后的、包含本地图片路径的最终HTML
#         final_html_path = os.path.join(output_dir, 'index.html')
        
#         # 组装完整的HTML页面，包括标题和样式，使其更易于查看
#         final_html_content = f"""
#         <!DOCTYPE html>
#         <html lang="zh-CN">
#         <head>
#             <meta charset="UTF-8">
#             <title>{title}</title>
#             <style>
#                 body {{ font-family: sans-serif; line-height: 1.6; max-width: 800px; margin: 20px auto; padding: 0 20px; }}
#                 img {{ max-width: 100%; height: auto; display: block; margin: 20px 0; }}
#             </style>
#         </head>
#         <body>
#             <h1>{title}</h1>
#             {soup.prettify()}
#         </body>
#         </html>
#         """
        
#         with open(final_html_path, 'w', encoding='utf-8') as f:
#             f.write(final_html_content)

#         print(f"\n任务完成！本地化的文章已保存到: {final_html_path}")
#         return final_html_path

#     except requests.exceptions.RequestException as e:
#         print(f"获取文章URL失败: {e}")
# from readability import Document
# import tempfile # 用于创建临时目录，自动清理


def save_html_as_pdf(html_path: str, output_pdf_path: str) -> bool:
    """
    将一个本地的HTML文件转换为PDF。
    （这是你修改后的 save_page_as_pdf 函数）

    Args:
        html_path (str): 本地HTML文件的路径.
        output_pdf_path (str): 最终生成的PDF文件路径.

    Returns:
        bool: 成功返回True，失败返回False.
    """
    try:
        path_wkthmltopdf = r'D:/Program Files/wkhtmltopdf/bin/wkhtmltopdf.exe'
        config = pdfkit.configuration(wkhtmltopdf=path_wkthmltopdf)
        
        print(f"正在将本地文件 {html_path} 转换为 PDF...")
        
        # 使用 from_file 而不是 from_url
        options = {
            'page-size': 'A4',
            'margin-top': '0.75in',
            'margin-right': '0.75in',
            'margin-bottom': '0.75in',
            'margin-left': '0.75in',
            'encoding': "UTF-8",
            'enable-local-file-access': None # **关键：允许wkhtmltopdf访问本地文件（图片）**
        }
        
        pdfkit.from_file(html_path, output_pdf_path, configuration=config, options=options)
        
        print(f"PDF已成功保存到: {output_pdf_path}")
        return True
    except Exception as e:
        print(f"使用pdfkit将HTML转换为PDF时失败: {e}")
        return False


# ----------------- 新增：使用Playwright获取完全加载的HTML -----------------
async def fetch_fully_loaded_html(url: str, timeout_seconds: int = 60) -> str | None:
    """
    使用Playwright启动浏览器，访问URL，等待页面完全加载，然后返回最终的HTML。
    
    Args:
        url (str): 要访问的网址.
        timeout_seconds (int): 最大等待时间（秒）.

    Returns:
        str | None: 成功则返回HTML字符串，失败则返回None.
    """
    print(f"使用Playwright加载URL: {url}")
    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch()
            page = await browser.new_page()
            
            # 'networkidle' 意味着等待直到网络在500毫秒内没有新的连接，
            await page.goto(url, wait_until='networkidle', timeout=timeout_seconds * 1000)

            # 有些“懒加载”的图片或内容可能在网络空闲后才触发，额外等待一小段时间
            await page.wait_for_timeout(3000)

            content = await page.content()
            await browser.close()
            print("页面内容已完全加载并获取。")
            return content
    except Exception as e:
        print(f"使用Playwright加载页面时出错: {e}")
        return None
from readability import Document
import tempfile # 用于创建临时目录，自动清理
# ----------------- 修改：处理HTML并保存本地文件 -----------------
def process_and_save_article(original_html: str, base_url: str, output_dir: str) -> str | None:
    """
    处理给定的HTML，提取正文，下载图片，并保存为本地化的HTML文件。
    (这是你原来的 save_article_with_images 函数的核心部分)

    Args:
        original_html (str): 已经完全加载的HTML内容.
        base_url (str): 原始URL，用于解析相对路径.
        output_dir (str): 保存结果的目录.

    Returns:
        str | None: 成功则返回本地HTML文件的路径，失败则返回None.
    """
    try:
        images_dir = os.path.join(output_dir, 'images')
        os.makedirs(images_dir, exist_ok=True)
        
        doc = Document(original_html,keepClasses = "True",classesToPreserve = "True")
        clean_html = doc.summary()
        title = doc.title()
        soup = BeautifulSoup(clean_html, 'lxml')
        
        print(f"在文章《{title}》中找到 {len(soup.find_all('img'))} 张图片进行处理。")
        for img_tag in soup.find_all('img'):
            # (图片处理逻辑与之前相同)
            img_src = img_tag.get('src')
            if not img_src or img_src.startswith('data:image'): continue
            
            absolute_img_url = urljoin(base_url, img_src)
            try:
                # (文件名生成和下载逻辑与之前相同)
                file_ext = os.path.splitext(absolute_img_url)[1].split('?')[0] or '.jpg'
                hashed_name = hashlib.md5(absolute_img_url.encode()).hexdigest()
                local_filename = f"{hashed_name}{file_ext}"
                local_image_path = os.path.join(images_dir, local_filename)

                img_response = requests.get(absolute_img_url, stream=True, timeout=20)
                img_response.raise_for_status()
                with open(local_image_path, 'wb') as f:
                    f.write(img_response.content)
                
                # 使用绝对路径，这对于pdfkit转换本地文件更可靠
                img_tag['src'] = os.path.abspath(local_image_path)
            except Exception as e:
                print(f"处理图片 {absolute_img_url} 时出错: {e}")
                img_tag['src'] = ""

        final_html_path = os.path.join(output_dir, 'index.html')
        final_html_content = f"""
        <!DOCTYPE html><html lang="zh-CN"><head><meta charset="UTF-8"><title>{title}</title>
        <style>body{{font-family:sans-serif;max-width:800px;margin:auto;}} img{{max-width:100%;height:auto;}}</style>
        </head><body><h1>{title}</h1>{soup.prettify()}</body></html>
        """
        with open(final_html_path, 'w', encoding='utf-8') as f:
            f.write(final_html_content)
        
        print(f"本地化的文章已保存到: {final_html_path}")
        return final_html_path
    except Exception as e:
        print(f"处理和保存文章时出错: {e}")
        return None

# async def process_url_to_pdf(url: str, final_pdf_path: str):
#     """
#     完整的处理流程：从URL到最终的PDF文件。
#     """
#     # 使用临时目录来存放中间的HTML和图片文件，程序结束时会自动删除
#     with tempfile.TemporaryDirectory() as temp_dir:
#         print(f"为URL {url} 创建临时工作目录: {temp_dir}")

#         # 步骤 1: 下载和净化网页，生成本地HTML
#         local_html_file = save_article_with_images(url, temp_dir)

#         # 步骤 2: 如果HTML成功生成，则将其转换为PDF
#         if local_html_file:
#             save_html_as_pdf(local_html_file, final_pdf_path)
#             return final_pdf_path
#         else:
#             print("因无法生成本地HTML文件，PDF转换任务已取消。")
#             return False
            
#     print("临时文件已清理。")
async def process_url_to_pdf_timeout(url: str, final_pdf_path: str):
    """从URL到PDF"""
    # 步骤1: 使用Playwright获取完全加载的HTML
    fully_loaded_html = await fetch_fully_loaded_html(url)
    
    if not fully_loaded_html:
        print("无法获取网页内容，任务中止。")
        return

    # 使用临时目录来存放中间文件
    with tempfile.TemporaryDirectory() as temp_dir:
        print(f"创建临时工作目录: {temp_dir}")

        # 步骤2: 处理HTML，下载图片，生成本地化的index.html
        local_html_file = process_and_save_article(
            original_html=fully_loaded_html,
            base_url=url,
            output_dir=temp_dir
        )
        
        # 步骤3: 如果本地HTML成功生成，则转换为PDF
        if local_html_file:
            save_html_as_pdf(local_html_file, final_pdf_path)
            return final_pdf_path
        else:
            print("无法生成本地HTML文件，PDF转换任务已取消。")
            return False
            
    print("任务完成，临时文件已清理。")

def get_companies_from_llm(context):
    """调用本地LLM模型分析文本并提取公司名称（与之前版本相同）。"""
    print("  [+] 正在调用本地LLM进行内容分析...")
#     client = OpenAI(base_url=LLM_API_BASE)

    prompt = f"""

你将收到一份从 PDF OCR 中提取出的文本，内容可能存在换行符混乱、表格结构丢失、格式不规范等问题。

请你从这份文本中识别出所有出现的“榜单”（如：XX百强榜、最具价值公司榜、创新企业TOP50等），并提取出每个榜单中列出的公司名称。

要求输出为 JSON 格式，结构如下：
{{
  "榜单名称1": ["公司1", "公司2", ...],
  "榜单名称2": ["公司A", "公司B", ...]
}}

注意：
- 榜单名称可能出现在标题、粗体文字、特殊格式或段落开头。
- 公司名称通常为中文公司全称（可包含“股份有限公司”、“科技有限公司”等字样）。
- 如果某个榜单下的公司没有显式编号（如1. 2. 3.），也请尽力提取。
- 可能存在多个榜单混杂，务必区分清楚。
- 输出时不得遗漏任何榜单及其下属公司。
- 多个榜单输出多个，不要嵌套。
- 按照顺序输出公司或者企业
json格式：
<json>
{{
  "中国银行业100强榜单": [
上海浦东发展银行
江苏银行
广东南粤银行
重庆三峡银行
浙江网商银行]}}
</json>

以下是OCR识别的PDF文本内容：
<ocr>
{context}
</ocr>

"""
#     try:
#         response = client.chat.completions.create(
#             model=LLM_MODEL_NAME,
#             messages=[
#                 {"role": "system", "content": "你是一个精确的信息提取助手。"},
#                 {"role": "user", "content": prompt}
#             ],
#             temperature=0.0,
#         )
#         result_text = response.choices[0].message.content
#         print("  [*] LLM分析完成。")


    body={"corpCode":"testcorp",
                    "userId":"testcorp-10001",
                    "sessionId":"testcorp-10001-20001", 
                    "bizType":5101,
                    "prompt": prompt
            }
    # print("prompt:",prompt)
    session=requests.session()
    response= session.post(CHAT_API_URL,json=body,headers=headers,timeout=300)
    # print("response:",response)
    data= response.json()['data']
    return data
    # except Exception as e:
        # print(f"  [!] 调用本地LLM失败: {e}")
        # return None
        # 
# from typing import List
# from PyPDF2 import PdfMerger
# def merge_pdfs(pdf_paths: List[str], output_path: str) -> bool:
#     """合并多个PDF为一个"""
#     merger = PdfMerger()
#     for path in pdf_paths:
#         print("path:",path)
#         if os.path.exists(path):
#             merger.append(path)
#     merger.write(output_path)
#     merger.close()
#     print(f"[完成] 合并PDF -> {output_path}")
#     return True
def is_valid_ocr_text(text: str) -> bool:
    """
    检查OCR识别出的文本是否为有效内容，过滤掉整体无意义的文本。
    不再负责移除关键词，只判断是否为“垃圾行”。

    Args:
        text (str): 单行OCR文本。

    Returns:
        bool: 如果文本有效（非纯空白、非高度重复等）则返回True, 否则返回False。
    """
    if not isinstance(text, str) or not text.strip():
        return False # 跳过非字符串或纯空白内容

    text = text.strip()

    # 规则1: 过滤掉高度重复的、无意义的文本 (这对应"无限文本"的引申义)
    # 例如：'---------' 或 'AAAAAAAAA'
    # 策略：如果字符串很长（例如超过10个字符），但独立字符种类非常少（例如例如只有1或2种），则认为是垃圾
    if len(text) > 10 and len(set(text)) <= 2:
        return False

    # 规则2: 过滤掉太短的无意义文本 (可选，根据实际需求决定是否启用)
    # if len(text) < 2:
    #     return False

    # 所有检查都通过了，说明是有效文本（但可能包含需要清理的关键词）
    return True

async def main():
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)

    ranking_list = load_ranking_list_from_json("tag2.json")
    for item in ranking_list:
    # for item in RANKING_LIST:
        name = item["name"]
        urls = item["url"] if isinstance(item["url"], list) else [item["url"]]

        print(f"\n{'='*20} 开始处理榜单: {name} {'='*20}")
        safe_name = "".join(x for x in name if x.isalnum())
        item_dir = os.path.join(OUTPUT_DIR, safe_name)
        os.makedirs(item_dir, exist_ok=True)

        # 步骤 1：下载并保存每个 URL 对应的 PDF
        ocr_texts = []
        for idx, single_url in enumerate(urls):
            
            pdf_path = os.path.join(item_dir, f"{safe_name}_{idx+1}.pdf")
            saved_path = await process_url_to_pdf_timeout(single_url, pdf_path)
            if not saved_path:
                print(f"  [×] PDF保存失败: {single_url}")
                continue
            print(f"  [+] PDF已保存: {pdf_path}")

            # 步骤 2：执行 OCR 并提取文本
            data = {
                "ali_ocr": "False"
            }

            with open(pdf_path, 'rb') as f:
                files = {
                    'file': (pdf_path, f, 'application/pdf')
                }
                ocr_result = requests.post("http://172.16.2.35:8001/layout", data=data, files=files)

            # 提取第二列文字信息,判断是否为有效OCR
            
            ocr_result = json.loads(ocr_result.text)["data"]
            # print(ocr_result)
            
            # print(ocr_result)
            # filtered_texts = [
            #     line for line in ocr_result  
            #     if len(line) > 1 and is_valid_ocr_text(line[1])
            # ]

            # print(filtered_texts)
            # if not filtered_texts:
            #     print(f"[跳过] 无有效OCR文本: {name}")
            #     continue 
            # else:
            #     # 将所有通过过滤的有效文本一次性添加到 ocr_texts 列表中
            #     ocr_texts.extend(filtered_texts)
                # print(f"成功提取并添加 {len(filtered_texts)} 条有效OCR文本。")

            # ocr_result = [line[1] for line in ocr_result if len(line) > 1]
            # if not ocr_result:
            #     print(f"[跳过] 无有效OCR文本: {name}")
            #     continue
            # ocr_texts.extend(ocr_result)
            ocr_texts.extend(ocr_result)


        # 步骤 3：保存所有 OCR 文本到文件
        combined_text = "".join(ocr_texts)
        # print("combined_text",combined_text)
        ocr_file_path = os.path.join(item_dir, "ocr_text.txt")
        with open(ocr_file_path, "w", encoding='utf-8') as f:
            f.write(combined_text)
        print(f"  [+] OCR文本已保存至: {ocr_file_path}")

        # 步骤 4：调用LLM接口进行信息提取
        llm_response = get_companies_from_llm(combined_text)

        print(f"\n--- 最终结果: {name} ---")

        if llm_response:
            try:
                # 提取llm_response中的JSON内容
                match = re.search(r'\{[\s\S]*\}', llm_response)
                if match:
                    json_str = match.group(0)
                    data = json.loads(json_str)

                    for list_name, companies in data.items():
                        print(f"\n榜单名称: {list_name}")
                        print(f"公司数量: {len(companies)}")
                        for company in sorted(set(companies)):
                            print(f"  - {company}")

                    # 保存为公司列表文件
                    result_file = os.path.join(item_dir, "company_list_final.txt")
                    with open(result_file, 'w', encoding='utf-8') as f:
                        f.write(f"# {name} - 榜单企业列表 (由PDF->OCR->LLM分析得出)\n")
                        f.write(f"# 来源URL: {urls}\n\n")
                        for list_name, companies in data.items():
                            f.write(f"## {list_name}\n")
                            for company in sorted(set(companies)):
                                f.write(f"{company}\n")
                            f.write("\n")
                    print(f"\n[+] 最终企业列表已保存至: {result_file}")

                    # 可选：保存为结构化json
                    json_file = os.path.join(item_dir, "company_list.json")
                    with open(json_file, 'w', encoding='utf-8') as f_json:
                        json.dump(data, f_json, ensure_ascii=False, indent=2)
                    print(f"[+] JSON结构化信息已保存至: {json_file}")

                else:
                    print("未能在llm_response中找到合法的JSON结构。")
            except json.JSONDecodeError as e:
                print(f"[!] JSON解析失败: {e}")
        else:
            print("未能从LLM获取分析结果。")


if __name__ == "__main__":
    asyncio.run(main())