from rapidocr_pdf import RapidOCRPDF

pdf_extracter = RapidOCRPDF()

pdf_path = "C:/Users/biela/Desktop/IDC：2024年度IDC中国金融科技榜单揭晓.pdf"

# page_num_list=[1]:
texts = pdf_extracter(pdf_path, force_ocr=True, page_num_list=[0,1,2,3,4,5,6,7])
print(texts)