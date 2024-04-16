from flask import Flask, request, jsonify, Response, stream_with_context, make_response, send_file
import requests
import json
from pdf_processor import PDFParser

controller = PDFParser()
app = Flask(__name__)

# @app.route('/pdf_parser', methods=['POST'])
# def app_pdf_parser():
#     # 从请求体中获取 template 和 input_path
#     template = request.json.get('template', None)
#     input_path = request.json.get('input_path', None)
#     model_name = request.json.get('model_name', 'gpt-4-0125-preview')  # 使用默认值或从请求体中获取
#
#     # 检查 input_path 是否为空
#     if not input_path:
#         return jsonify({'error': 'Input path is missing'}), 400
#
#     try:
#         # 调用 pdf_parser 函数，传递所有必需的参数
#         protocol_field = controller.pdf_parser(template, input_path, model_name)
#         # 返回处理结果
#         return jsonify({'status_code': 200, 'result': protocol_field})
#     except Exception as e:
#         # 处理可能的异常情况
#         return jsonify({'error': str(e)}), 500

# @app.route('/pdf_parser', methods=['POST'])
# def app_pdf_parser():
#     # 从请求体中获取 template 和 input_path
#     template = request.json.get('template', None)
#     input_path = request.json.get('input_path', None)
#     model_name = request.json.get('model_name', 'gpt-4-0125-preview')  # 使用默认值或从请求体中获取
#
#     # 检查 input_path 是否为空
#     if not input_path:
#         return jsonify({'code': 400, 'msg': 'Input path is missing', 'data': {}})
#
#     try:
#         # 调用 pdf_parser 函数，传递所有必需的参数
#         protocol_field = controller.pdf_parser(template, input_path, model_name)
#         # 返回处理结果
#         return jsonify({'code': 0, 'msg': 'Success', 'data': protocol_field})
#     except Exception as e:
#         # 处理可能的异常情况
#         return jsonify({'code': 500, 'msg': str(e), 'data': {}})

@app.route('/pdf_parser', methods=['POST'])
def app_pdf_parser():
    # 从请求体中获取 template 和 input_path
    template = request.json.get('template', None)
    input_path = request.json.get('input_path', None)
    model_name = request.json.get('model_name', 'gpt-4-0125-preview')  # 使用默认值或从请求体中获取

    # 检查 input_path 是否为空
    if not input_path:
        return jsonify({
            'code': 1,
            'msg': 'Input path is missing',
            'data': None
        }), 400

    try:
        # 调用 pdf_parser 函数，传递所有必需的参数
        protocol_field = controller.pdf_parser(template, input_path, model_name)

        # 请求成功，返回封装后的响应
        return jsonify({
            'code': 0,
            'msg': 'Success',
            'data': {
                'result': protocol_field
            }
        })
    except Exception as e:
        # 处理可能的异常情况
        return jsonify({
            'code': 1,
            'msg': str(e),
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
