import requests
from readability import Document
import os
from bs4 import BeautifulSoup
from markdownify import markdownify as md
from urllib.parse import urljoin
from typing import Optional
def extract_with_readability(html_content):
    """
    使用 readability-lxml 库来提取文章主要内容。
    """
    doc = Document(html_content)
    
    # doc.summary() 返回清理后的主要内容HTML
    content_html = doc.summary()
    
    # doc.title() 返回文章标题
    title = doc.title()
    
    # readability 自身不直接提供日期和作者，但我们可以从清理后的HTML中提取纯文本
    # 需要再次用BeautifulSoup解析清理后的内容来获取纯文本
    soup = BeautifulSoup(content_html, 'lxml')
    content_text = soup.get_text(separator='\n', strip=True)
    
    return {
        'title': title,
        'content_text': content_text,
        'content_html': content_html
    }

# --- 示例用法 ---
if __name__ == '__main__':
    url = "https://finance.sina.com.cn/stock/relnews/cn/2024-08-20/doc-inckhrze0294204.shtml"
    try:
        response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
        response.raise_for_status()
        response.encoding = response.apparent_encoding

        article_data = extract_with_readability(response.text)
        
        print(f"标题: {article_data['title']}")
        print("\n--- 清理后的纯文本正文 (由Readability提供) ---\n")
        print(article_data['content_text'] )
        
    except requests.exceptions.RequestException as e:
        print(f"请求失败: {e}")