# coding=utf-8
import fitz  # PyMuPDF
import easyocr
import openai
from docx import Document
import pandas as pd
import json
import os

def convert_pdf_to_images(pdf_path, output_folder):
    # 打开PDF文件
    pdf = fitz.open(pdf_path)

    # 遍历PDF的每一页
    for page_num in range(len(pdf)):
        page = pdf[page_num]

        # 将PDF页转换为图像
        pix = page.get_pixmap()

        # 定义输出图像的路径
        output_path = f"{output_folder}/page_{page_num + 1}.jpg"

        # 保存图像
        pix.save(output_path)

    # 关闭PDF文件
    pdf.close()

def recognize_text_from_images(image_paths):
    # 初始化EasyOCR的Reader对象
    reader = easyocr.Reader(['ch_sim','en'])  # 这里使用中文模型，根据需要可以更改

    # 存储所有识别结果的列表
    results = []

    # 遍历所有图像路径
    for image_path in image_paths:
        # 读取图像并进行文字识别
        result = reader.readtext(image_path, detail = 0)

        # 将结果添加到列表中
        results.append(result)

    return results

def truncate_text(text, max_tokens):
    tokens = text.split()  # 假设每个词是一个令牌
    if len(tokens) > max_tokens:
        return ' '.join(tokens[-max_tokens:])  # 保留最后的max_tokens个令牌
    return text

def read_docx_to_string(file_path):
    # 加载Word文档
    doc = Document(file_path)
    full_text = []

    # 遍历文档中的段落并读取内容
    for para in doc.paragraphs:
        full_text.append(para.text)

    # 将所有段落连接成一个字符串
    return '\n'.join(full_text)

# 按装订区域中的绿色按钮以运行脚本。
if __name__ == '__main__':
    import pandas as pd

    prompt ="""    你是一个xxx，你的任务是提取字段
    你要提取的字段要:
    冷却方式，xxxx
    电压。xxXx"""

    df = pd.read_excel('text.xlsx')
    prompt = """你是一个聪明而且有百年经验的命名实体识别（NER）识别器。你的任务是提取字段。
    你要提取的字段有:
    """

    for i in range(len(df)):
        item = df.iloc[i]
        prompt += f" field: {item['field']}\n"
        prompt += f"\tdescription: {item['description']}\n"
        prompt += f"\tunit: {item['unit']}\n"
        prompt += f"\texample: {item['example value']}\n"

    file_path = '技术协议提取/历史评审单/3/中冶赛迪电气15000kVA技术协议20240220.docx'
    docx_content = read_docx_to_string(file_path)
    prompt += f"\t你需要提取的文件内容为: {docx_content}\n"

    openai.api_base = "https://openkey.cloud/v1"  # 换成代理，一定要加v1
    openai.api_key = os.getenv("OPENAI_API_KEY")

    response = openai.ChatCompletion.create(
        model="gpt-4-0125-preview",
        messages=[
            {"role": "system",
             "content": "你是一个聪明而且有百年经验的命名实体识别（NER）识别器。"},
            {"role": "user",
             "content": prompt}]
    )
    print(response)
