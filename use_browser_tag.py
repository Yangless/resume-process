import os
import asyncio
from playwright.async_api import async_playwright
# from pdf2image import convert_from_path
# import pytesseract
from openai import OpenAI
import time
from rapidocr_pdf import RapidOCRPDF


# Ollama API 配置
LLM_API_BASE = "http://localhost:11434/v1"
LLM_MODEL_NAME = "Qwen3-8B-BF16.gguf" # 确保这个模型正在Ollama中运行

# 输入的榜单列表
RANKING_LIST = [
    {
        "name": "中国数字金融独角兽",
        "url": "https://finance.sina.com.cn/jjxw/2024-10-21/doc-incthwvv2272216.shtml"
    },
    {
        "name": "中国金融科技榜单揭晓",
        "url": "https://my.idc.com/getdoc.jsp?containerId=prCHC52515324"
    },
    {
        "name": "中国金融科技Top企业",
        "url": "https://my.idc.com/getdoc.jsp?containerId=prCHC52515324"
    }
]

# 输出文件的根目录
OUTPUT_DIR = "web_rankings_pdf_output"
os.environ["OPENAI_API_KEY"] = "sk-no-key-required"

# --- 核心功能函数 ---
pdf_extracter = RapidOCRPDF()
async def save_page_as_pdf(url, output_path):
    """使用Playwright将网页完整保存为PDF。"""
    print(f"  [+] 正在将网页保存为PDF: {url}")
    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch()
            page = await browser.new_page()
            # 增加超时时间，并等待网络空闲，确保动态内容加载完成
            await page.goto(url, wait_until='networkidle', timeout=60000)
            # 等待一小段时间，让最后的渲染完成
            await page.wait_for_timeout(3000) 
            
            await page.pdf(path=output_path, format='A4', print_background=True)
            await browser.close()
        print(f"  [+] PDF已保存至: {output_path}")
        return True
    except Exception as e:
        print(f"  [!] 保存PDF失败: {e}")
        return False

def ocr_pdf_to_text(pdf_path, poppler_path=None):
    """
    将PDF使用OCR提取所有文本。
    这可以被视为调用一个本地的“OCR处理流程接口”。
    """
    print(f"  [+] 正在对PDF进行OCR处理: {pdf_path}")
    if not os.path.exists(pdf_path):
        print("  [!] PDF文件不存在，跳过OCR。")
        return ""
        
    try:
        texts = pdf_extracter(pdf_path, force_ocr=True)
        return texts
    except Exception as e:
        print(f"  [!] PDF OCR处理失败: {e}")
        print("  [!] 请确保Poppler和Tesseract已正确安装并配置。")
        return ""

def get_companies_from_llm(context):
    """调用本地LLM模型分析文本并提取公司名称（与之前版本相同）。"""
    print("  [+] 正在调用本地LLM进行内容分析...")
    client = OpenAI(base_url=LLM_API_BASE)

    prompt = f"""

请你通过阅读全文，输出存在的榜单，和榜单上的所有公司

以下是需要分析的OCR内容：
---
{context}
---
请开始提取公司列表：
"""
    try:
        response = client.chat.completions.create(
            model=LLM_MODEL_NAME,
            messages=[
                {"role": "system", "content": "你是一个精确的信息提取助手。"},
                {"role": "user", "content": prompt}
            ],
            temperature=0.0,
        )
        result_text = response.choices[0].message.content
        print("  [*] LLM分析完成。")
        return result_text
    except Exception as e:
        print(f"  [!] 调用本地LLM失败: {e}")
        return None

# --- 主执行流程 ---

async def main():
    """主函数（异步）"""
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)

    for item in RANKING_LIST:
        name = item["name"]
        url = item["url"]
        print(f"\n{'='*20} 开始处理榜单: {name} {'='*20}")
        
        safe_name = "".join(x for x in name if x.isalnum())
        item_dir = os.path.join(OUTPUT_DIR, safe_name)
        os.makedirs(item_dir, exist_ok=True)
        
        # 1. 将网页保存为PDF
        pdf_path = os.path.join(item_dir, f"{safe_name}.pdf")
        pdf_saved = await save_page_as_pdf(url, pdf_path)
        
        if not pdf_saved:
            continue
            
        # 2. 调用本地OCR接口处理PDF
        ocr_text = ocr_pdf_to_text(pdf_path)
        # print(ocr_text)
        extracted_texts = []

        # 遍历主列表中的每个子列表
        for item in ocr_text:
            # 检查子列表的长度，确保它至少有2个元素，避免索引错误
            if len(item) > 1:
                # 提取第二个元素（索引为1）
                text = item[1]
                extracted_texts.append(text)
        # 将OCR结果保存到文件，方便调试
        combined_text = "".join(extracted_texts)
       
        ocr_file_path = os.path.join(item_dir, "ocr_text.txt")
        # ocr_file_path = os.path.join(item_dir, "ocr_text.txt")
        with open(ocr_file_path, "w", encoding='utf-8') as f:
            f.write(combined_text)
        print(f"  [+] OCR文本已保存至: {ocr_file_path}")
        
        # 3. 将文本输入本地Llama模型API
        llm_response = get_companies_from_llm(combined_text)
        print(llm_response)
        # 4. 清理和输出结果
        print(f"\n--- 最终结果: {name} ---")
        if llm_response:
            companies = [line.strip() for line in llm_response.strip().split('\n') if line.strip()]
            if companies:
                print(f"LLM成功识别出 {len(companies)} 家企业：")
                sorted_companies = sorted(list(set(companies)))
                for company in sorted_companies:
                    print(f"  - {company}")
                
                result_file = os.path.join(item_dir, "company_list_final.txt")
                with open(result_file, 'w', encoding='utf-8') as f:
                    f.write(f"# {name} - 榜单企业列表 (由PDF->OCR->LLM分析得出)\n")
                    f.write(f"# 来源URL: {url}\n\n")
                    f.write("\n".join(sorted_companies))
                print(f"\n[+] 最终企业列表已保存至: {result_file}")
            else:
                print("LLM分析了内容，但未能提取出符合要求的公司列表。")
        else:
            print("未能从LLM获取分析结果。")
            
        print(f"{'='*20} {name} 处理完成 {'='*20}\n")


if __name__ == "__main__":
    # 使用asyncio运行异步主函数
    asyncio.run(main())