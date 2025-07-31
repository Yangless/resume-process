import os
import requests
import hashlib
from urllib.parse import urljoin
from bs4 import BeautifulSoup
from readability import Document

def save_article_with_images(url: str, output_dir: str):
    """
    下载一篇文章，并将其中的图片本地化保存。

    Args:
        url (str): 文章的URL.
        output_dir (str): 保存结果的目录.
    """
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36'
    }

    try:
        # 1. 获取原始网页内容
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        response.encoding = response.apparent_encoding
        original_html = response.text
        
        # 创建输出目录
        images_dir = os.path.join(output_dir, 'images')
        os.makedirs(images_dir, exist_ok=True)
        
        # 2. 使用 readability-lxml 提取主要内容
        doc = Document(original_html)
        clean_html = doc.summary()
        title = doc.title()

        # 3. 使用 BeautifulSoup 解析干净的HTML，准备处理图片
        soup = BeautifulSoup(clean_html, 'lxml')

        # 4. 查找所有图片标签并处理
        img_tags = soup.find_all('img')
        print(f"在文章《{title}》中找到 {len(img_tags)} 张图片。")

        for img_tag in img_tags:
            # a. 获取图片URL
            img_src = img_tag.get('src')
            if not img_src:
                continue

            # 处理 data: URI 格式的内嵌图片 (常见于一些小图标)
            if img_src.startswith('data:image'):
                print(f"跳过内嵌图片 (data URI): {img_src[:60]}...")
                continue
            
            # b. 将相对URL转换为绝对URL
            absolute_img_url = urljoin(url, img_src)
            
            try:
                # c. 生成一个唯一的本地文件名，避免冲突
                # 使用URL的MD5哈希值作为文件名主体，保留原始扩展名
                file_ext = os.path.splitext(absolute_img_url)[1].split('?')[0]
                if not file_ext: # 如果没有扩展名，默认为.jpg
                    file_ext = '.jpg'
                
                hashed_name = hashlib.md5(absolute_img_url.encode()).hexdigest()
                local_filename = f"{hashed_name}{file_ext}"
                local_image_path = os.path.join(images_dir, local_filename)

                # d. 下载图片
                print(f"正在下载图片: {absolute_img_url} ...")
                img_response = requests.get(absolute_img_url, headers=headers, stream=True, timeout=20)
                img_response.raise_for_status()

                # 以二进制模式写入文件
                with open(local_image_path, 'wb') as f:
                    for chunk in img_response.iter_content(chunk_size=8192):
                        f.write(chunk)
                
                print(f"图片已保存到: {local_image_path}")

                # e. 修改<img>标签的src，指向本地文件
                # 使用相对路径，这样整个文件夹移动时也能正常显示
                relative_image_path = os.path.join('images', local_filename)
                img_tag['src'] = relative_image_path

            except Exception as e:
                print(f"处理图片 {absolute_img_url} 时出错: {e}")
                # 如果下载失败，可以移除这个img标签或保留原始src
                # 这里选择保留，以便知道哪个图片失败了
                img_tag['src'] = f"DOWNLOAD_FAILED_{absolute_img_url}"

        # 5. 保存修改后的、包含本地图片路径的最终HTML
        final_html_path = os.path.join(output_dir, 'index.html')
        
        # 组装完整的HTML页面，包括标题和样式，使其更易于查看
        final_html_content = f"""
        <!DOCTYPE html>
        <html lang="zh-CN">
        <head>
            <meta charset="UTF-8">
            <title>{title}</title>
            <style>
                body {{ font-family: sans-serif; line-height: 1.6; max-width: 800px; margin: 20px auto; padding: 0 20px; }}
                img {{ max-width: 100%; height: auto; display: block; margin: 20px 0; }}
            </style>
        </head>
        <body>
            <h1>{title}</h1>
            {soup.prettify()}
        </body>
        </html>
        """
        
        with open(final_html_path, 'w', encoding='utf-8') as f:
            f.write(final_html_content)

        print(f"\n任务完成！本地化的文章已保存到: {final_html_path}")

    except requests.exceptions.RequestException as e:
        print(f"获取文章URL失败: {e}")


# --- 示例用法 ---
if __name__ == '__main__':
    # 使用一个包含多张图片的真实新闻链接
    target_url = "https://finance.sina.com.cn/stock/relnews/cn/2024-08-20/doc-inckhrze0294204.shtml"
    # 定义输出目录，以文章标题或URL哈希命名，避免混淆
    output_directory = "saved_article_" + hashlib.md5(target_url.encode()).hexdigest()[:8]
    
    save_article_with_images(target_url, output_directory)