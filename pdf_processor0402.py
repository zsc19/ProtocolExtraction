# coding=utf-8
import fitz  # PyMuPDF
import easyocr
import openai
from docx import Document
import pandas as pd
from flask import Flask, jsonify
import json
import os
import glob

class PDFParser:
    def __init__(self):
        self.model = "gpt-4-0125-preview"
        self.template = self.load_template()
        self.prompt = """你是一个聪明而且有百年经验的命名实体识别（NER）识别器。你的任务是提取字段。你的回答务必使用完全的json格式！不要包含多的字段，你要提取的字段有:"""
        # todo prompt需读取Excel获取完整版【yeah】

    def load_template(self):
        # load from file
        template = pd.read_excel("template.xlsx")
        return template

    def view_template(self):
        return self.template.to_records()

    def update_template(self, new_template):
        # 格式检查，检查前端传过来的是否符合要求
        self.template = pd.DataFrame(new_template)
        # 返回状态码，是否成功
        return 200

    def view_prompt(self):
        return self.prompt

    def update_prompt(self, prompt):
        self.prompt = prompt

    def view_model(self):
        return self.model

    def update_model(self, model_name):
        self.model = model_name

    def pdf_parser(self, input):
        # parse the pdf file
        if isinstance(input, bytes):
            # 处理字节流
            json_string = {}  # 创建一个空的字典用于存储JSON数据
            # todo
        elif isinstance(input, str):
            # 读取excel，更新prompt
            prompt = self.prompt
            for i in range(len(self.template)):
                item = self.template.iloc[i]
                prompt += f"field: {item['field']}\n"
                prompt += f"\tdescription: {item['description']}\n"
                prompt += f"\tunit: {item['unit']}\n"
                prompt += f"\texample: {item['example value']}\n"

            # 处理文件路径
            pdf_path = input
            output_folder = "temp_folder"   # 需要一个零时文件夹放置多页图片
            # 将PDF转换为图像
            self.convert_pdf_to_images(pdf_path, temp_folder)
            # 获取所有图像的路径
            image_paths = glob.glob(f"{output_folder}/*.jpg")
            # 使用OCR识别文本
            recognized_texts = self.recognize_text_from_images(image_paths)
            # 使用嵌套的列表推导式将所有字符串合并成一个列表
            flattened_texts = [text for sublist in recognized_texts for text in sublist]
            # 现在 flattened_texts 是一个字符串列表，可以使用 join 方法合并成一个长字符串
            long_string = "\n".join(flattened_texts)
            # 加上协议内容
            prompt += long_string
            # 更新prompt
            self.update_prompt(prompt)

            # word版本
            # docx_content = self.read_docx_to_string(input)
            # prompt += f"\t你需要提取的文件内容为: {docx_content}\n"

            openai.api_base = "https://openkey.cloud/v1"  # 换成代理，一定要加v1
            openai.api_key = os.getenv("OPENAI_API_KEY")

            response = openai.ChatCompletion.create(
                model = self.view_model(),
                messages = [
                    # {"role": "system",
                    #  "content": "你是一个聪明而且有百年经验的命名实体识别（NER）识别器。"},
                    {"role": "user",
                     "content": self.view_prompt()}]
            )

            res = response.choices[0].message.content
            print(res)
            # todo 后处理为json
            # 假设res是一个JSON格式的字符串
            try:
                parsed_res = json.loads(res)
                # 如果没有抛出异常，说明res是一个有效的JSON字符串
                # 现在parsed_res是一个Python对象（如字典或列表）
                json_string = json.dumps(parsed_res)
            except json.JSONDecodeError:
                # 如果抛出异常，说明res不是一个有效的JSON字符串
                # 处理错误情况，例如设置默认值或抛出异常
                json_string = "{}"  # 创建一个空的JSON对象

        return json_string

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

### server.py
app = Flask(__name__)
controller = PDFParser()


@app.route('/view_prompt', methods=['GET'])
def app_view_prompt():
    return jsonify(controller.view_prompt())

# @app.route('/')
# def index():
#     return 'Hello, World!'

if __name__ == '__main__':
    app.run(port=5000)
