import os
import requests
from bs4 import BeautifulSoup
from markdownify import markdownify as md
from urllib.parse import urljoin
from typing import Optional

# --- 新的、被包装的核心功能函数 ---
def url_to_markdown_file(url: str, output_dir: str, name: str) -> Optional[str]:
    """
    抓取网页URL，将其主要内容转换为Markdown文件，并返回生成的文件路径。
    如果操作失败，则返回 None。

    Args:
        url (str): 目标网页的URL.
        output_dir (str): 保存Markdown文件的目录.
        name (str): 用于命名的安全字符串（不含扩展名）.

    Returns:
        Optional[str]: 成功时返回Markdown文件的绝对路径，失败时返回None.
    """
    try:
        # 1. 发送网络请求
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36'
        }
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        response.encoding = response.apparent_encoding

        # 2. 解析HTML
        soup = BeautifulSoup(response.text, 'lxml')

        # 3. 提取主要内容区域
        content_selectors = ['article', 'main', 'div#main-content', 'div.main-content', 'div#content', 'div.content', 'div.article-body']
        content_html = None
        for selector in content_selectors:
            if soup.select_one(selector):
                content_html = soup.select_one(selector)
                break
        
        if not content_html:
            content_html = soup.body

        # 4. 转换相对URL为绝对URL
        for tag in content_html.find_all(['a', 'img']):
            attr = 'href' if tag.name == 'a' else 'src'
            if tag.has_attr(attr) and tag[attr]:
                absolute_url = urljoin(url, tag[attr])
                tag[attr] = absolute_url

        # 5. 转换为Markdown
        markdown_text = md(str(content_html), heading_style="ATX")

        # 6. 准备路径并保存文件
        os.makedirs(output_dir, exist_ok=True)
        output_path = os.path.join(output_dir, f"{name}.md")
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(markdown_text)
        
        # 7. 成功后返回文件路径
        return output_path

    except requests.exceptions.RequestException as e:
        # 在调用处处理打印信息，这里只负责失败
        print(f"  [!] 网络请求失败 ({url}): {e}")
        return None
    except Exception as e:
        print(f"  [!] 处理过程中发生未知错误 ({url}): {e}")
        return None

# --- 主程序逻辑（调用新函数） ---
def main():
    """主函数示例"""
    # 假设这是你的榜单列表
    RANKING_LIST = [
        {
            "name": "中国金融科技Top企业",
            "url": "https://www.stcn.com/article/detail/1271379.html"
        },
        {
            "name": "中国银行业100强",
            "url": "https://finance.sina.com.cn/stock/relnews/cn/2024-08-20/doc-inckhrze0294204.shtml"
        },
        {
            "name": "无效链接示例",
            "url": "https://thissitedoesnotexist.com/page"
        }
    ]
    
    OUTPUT_DIR = "markdown_output"
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)

    for item in RANKING_LIST:
        name = item["name"]
        url = item["url"]
        
        print(f"\n{'='*20} 开始处理: {name} {'='*20}")

        # 创建一个对文件名安全的名字
        safe_name = "".join(x for x in name if x.isalnum())
        item_dir = os.path.join(OUTPUT_DIR, safe_name)
        
        # 调用核心函数，并接收返回的路径
        markdown_file_path = url_to_markdown_file(url, item_dir, safe_name)
        
        # 根据返回值判断成功或失败，并打印相应信息
        if markdown_file_path:
            print(f"  [✔] 成功！Markdown文件已保存至: {markdown_file_path}")
        else:
            print(f"  [❌] 失败！未能为 {name} 创建Markdown文件。")

if __name__ == "__main__":
    main()