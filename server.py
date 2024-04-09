from flask import Flask, request, jsonify, Response, stream_with_context, make_response, send_file
from pdf_processor import PDFParser

controller = PDFParser()
app = Flask(__name__)

@app.route('/pdf_parser', methods=['POST'])
def app_pdf_parser():
    template = request.json.get('template', None)
    ...
    input_path = request.json.get('input_path', {})
    # 检查输入路径是否为空
    if not input_path:
        return jsonify({'error': 'Input path is missing'}), 400
    try:
        # 调用自定义的 PDF 解析函数
        protocol_field = controller.pdf_parser(input_path)
        # 返回处理结果
        return jsonify({'status_code': 200, 'result': protocol_field})
    except Exception as e:
        # 处理可能的异常情况
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
    # app.run(port=5000)
