from flask import Flask, request, jsonify, Response, stream_with_context, make_response, send_file
import requests
import json
from pdf_processor import PDFParser

controller = PDFParser()
app = Flask(__name__)

@app.route('/pdf_parser', methods=['POST'])
def app_pdf_parser():
    # 从请求体中获取 template 和 input_path
    template = request.json.get('template', None)
    input_path = request.json.get('input_path', None)
    model_name = request.json.get('model_name', 'gpt-4-0125-preview')  # 使用默认值或从请求体中获取

    # 检查 input_path 是否为空
    if not input_path:
        return jsonify({
            'code': 0,
            'message': '提取失败',
            'fileUrl': input_path,
            'data': None
        }), 400

    try:
        # 调用 pdf_parser 函数，传递所有必需的参数
        protocol_field = controller.pdf_parser(template, input_path, model_name)
        """"""
        # 假设的API端点
        api_endpoint = 'http://xhd-customer-api.wiseinsightai.com/app-api/trade/agreement-doc/updateAgreementStatus'

        # 创建一个请求头，可以包含任何需要的额外信息
        headers = {
            'Content-Type': 'application/json'
        }

        # 创建一个请求体，符合后端期望的格式
        data = {
            'code': 0,
            'message': '提取成功',
            'fileUrl': input_path,
            'data': protocol_field
        }

        # 发送POST请求
        response = requests.post(api_endpoint, json=data, headers=headers)

        # 打印响应内容
        print(response.text)
        """"""
        # 请求成功，返回封装后的响应
        return jsonify({
            'code': 1,
            'message': '提取成功',
            'fileUrl': input_path,
            'data': {
                'result': protocol_field
            }
        })
    except Exception as e:
        # 处理可能的异常情况
        return jsonify({
            'code': 1,
            'message': str(e),
            'fileUrl': input_path,
            'data': None
        }), 500


@app.route('/txttest', methods=['POST'])
def txt_test():
    print('111')
    if request.method == 'POST':
        txt = request.get_json()
        print(txt)
        return 'success!'

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True, threaded=True)
    # app.run(host="0.0.0.0", port=5000, threaded=True)
