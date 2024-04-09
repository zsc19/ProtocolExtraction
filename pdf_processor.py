# coding=utf-8
import fitz  # PyMuPDF
import easyocr
import openai
from docx import Document
import pandas as pd
import json
import os
import glob

class PDFParser:
    def __init__(self):
        self.model = "gpt-4-0125-preview"
        self.template = self.load_template()
        self.prompt = """你是一个聪明而且有百年经验的命名实体识别（NER）识别器。你的任务是提取字段。你的回答务必使用完全的json格式！不要包含多的字段，你要提取的字段有:"""

    def load_template(self):
        # load from file
        template = pd.read_excel("./template.xlsx")
        return template

    def view_template(self):
        # 获取 DataFrame 的列名
        columns = self.template.columns.tolist()
        # 将 DataFrame 中的数据转换为 UTF-8 编码
        records = self.template.applymap(
            lambda x: str(x).encode('utf-8').decode('utf-8') if isinstance(x, str) else x
        ).to_records(index=False)
        # 使用列名和 records 创建字典列表
        template_list = [dict(zip(columns, row)) for row in records]
        # 将数据转换为 JSON，并确保不将中文转换为 Unicode 转义序列
        json_data = json.dumps(template_list, ensure_ascii=False, indent=4)
        return json_data
        """"""
        # # 获取 DataFrame 的列名
        # columns = self.template.columns.tolist()
        # records = self.template.to_records(index=False)
        # # 使用列名和 records 创建字典列表
        # template_list = [dict(zip(columns, row)) for row in records]
        # return template_list
        """"""
        # records = self.template.to_records()
        # # 将 records 转换为字典列表
        # # template_list = [dict(row) for row in records]
        # template_list = [dict(zip(row._fields, row)) for row in records]
        # # print(type(template_list))
        # return template_list
        """"""
        # return self.template.to_records()
        """"""
        # df_json = self.template.to_json(orient='records')
        # return jsonify(df_json)
        """"""


    def update_template(self, new_template):
        # 格式检查，检查前端传过来的是否符合要求
        self.template = pd.DataFrame(new_template)
        # 返回状态码，是否成功
        return 200

    def view_prompt(self):
        return self.prompt

    def update_prompt(self, prompt):
        self.prompt = prompt
        # 返回状态码，是否成功
        return 200

    def view_model(self):
        return self.model

    def update_model(self, model_name):
        self.model = model_name
        # 返回状态码，是否成功
        return 200

    def pdf_parser(self, template, input_path, model_name = 'gpt-4-0125-preview'):
        # parse the pdf file
        if isinstance(input_path, bytes):
            # 处理字节流
            json_string = {}  # 创建一个空的字典用于存储JSON数据
            # todo
        elif isinstance(input_path, str):
            # 读取excel，更新prompt
            prompt = self.prompt
            # TODO: template合法性检查
            # 要求template为一个字典，包含field, description, key, unit, examples五个键，每个键的值为一个列表
            # 例如：
            template = {
                'field': ['冷却方式', '电压'],
                'description': ['...', '...'],
                'key': [],
                'unit': [],
                'examples': []
            }


            # 根据template组装prompt
            for i in range(len(self.template)):
                item = self.template.iloc[i]
                prompt += f"field: {item['field']}\n"
                prompt += f"\tdescription: {item['description']}\n"
                prompt += f"\tunit: {item['unit']}\n"
                prompt += f"\texample: {item['example value']}\n"

            # 处理文件路径
            # 获取文件的扩展名
            file_extension = os.path.splitext(input_path)[1].lower()
            # pdf版本
            if file_extension in ['.pdf']:
                pdf_path = input_path
                output_folder = "output_folder"   # 需要一个零时输出文件夹放置多页图片
                # 将PDF转换为图像
                self.convert_pdf_to_images(pdf_path, output_folder)
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
            if file_extension in ['.doc', '.docx']:
                docx_content = self.read_docx_to_string(file_extension)
                prompt += f"\t你需要提取的文件内容为: {docx_content}\n"
                self.update_prompt(prompt)
            # todo word融合pdf

            # api
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

    @classmethod
    def convert_pdf_to_images(cls, pdf_path, output_folder):
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

    @classmethod
    def recognize_text_from_images(cls, image_paths):
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

    def read_docx_to_string(self, file_path):
        # 加载Word文档
        doc = Document(file_path)
        full_text = []

        # 遍历文档中的段落并读取内容
        for para in doc.paragraphs:
            full_text.append(para.text)

        # 将所有段落连接成一个字符串
        return '\n'.join(full_text)
