# from flask import Flask, request, jsonify
# from azure.core.credentials import AzureKeyCredential
# from azure.ai.formrecognizer import DocumentAnalysisClient

# app = Flask(__name__)

# # Azure Form Recognizer endpoint and API key
# endpoint = "https://resumedocumentref.cognitiveservices.azure.com/"
# key = "1b48e06c5b94480ca36afe65140d98ee"
# model_id = "prebuilt-layout"  # Prebuilt layout model ID

# @app.route('/analyze', methods=['POST'])
# def analyze_document():
#     # Check if a file was uploaded
#     if 'file' not in request.files:
#         return jsonify({'error': 'No file part in the request'}), 400

#     file = request.files['file']

#     if file.filename == '':
#         return jsonify({'error': 'No file selected for uploading'}), 400

#     if file:
#         try:
#             # Initialize DocumentAnalysisClient with Azure credentials
#             document_analysis_client = DocumentAnalysisClient(endpoint=endpoint, credential=AzureKeyCredential(key))

#             # Analyze the document from the uploaded file
#             poller = document_analysis_client.begin_analyze_document(model_id, file)
#             result = poller.result()

#             # Prepare JSON response
#             response_data = {
#                 'styles': [],
#                 'pages': [],
#                 'tables': []
#             }

#             # Process the analysis results
#             for style in result.styles:
#                 response_data['styles'].append({
#                     'content': 'handwritten' if style.is_handwritten else 'no handwritten'
#                 })

#             for page in result.pages:
#                 page_data = {
#                     'lines': [{'content': line.content} for line in page.lines],
#                     'selection_marks': [{'state': selection_mark.state, 'confidence': selection_mark.confidence} for selection_mark in page.selection_marks]
#                 }
#                 response_data['pages'].append(page_data)

#                 for table in page.tables:
#                     table_data = {
#                         'row_count': table.row_count,
#                         'column_count': table.column_count,
#                         'cells': [{'content': cell.content} for cell in table.cells]
#                     }
#                     response_data['tables'].append(table_data)

#             return jsonify(response_data), 200

#         except Exception as e:
#             return jsonify({'error': str(e)}), 500

# if __name__ == '__main__':
#     app.run(debug=True)

from flask import Flask, request, jsonify
from azure.core.credentials import AzureKeyCredential
from azure.ai.formrecognizer import DocumentAnalysisClient
from flask_cors import CORS

app = Flask(__name__)
CORS(app)
# Azure Form Recognizer endpoint and API key
endpoint = "https://resumedocumentref.cognitiveservices.azure.com/"
key = "1b48e06c5b94480ca36afe65140d98ee"
model_id = "prebuilt-layout"  # Prebuilt layout model ID

@app.route('/analyze', methods=['POST'])
def analyze_document():
    # Check if a file was uploaded
    if 'file' not in request.files:
        return jsonify({'error': 'No file part in the request'}), 400

    file = request.files['file']

    if file.filename == '':
        return jsonify({'error': 'No file selected for uploading'}), 400

    if file:
        try:
            # Initialize DocumentAnalysisClient with Azure credentials
            document_analysis_client = DocumentAnalysisClient(endpoint=endpoint, credential=AzureKeyCredential(key))

            # Analyze the document from the uploaded file
            poller = document_analysis_client.begin_analyze_document(model_id, file)
            result = poller.result()

            # Prepare JSON response
            response_data = {
                'styles': [],
                'pages': []
            }

            # Process the analysis results
            for style in result.styles:
                response_data['styles'].append({
                    'content': 'handwritten' if style.is_handwritten else 'no handwritten'
                })

            for page in result.pages:
                page_data = {
                    'lines': [{'content': line.content} for line in page.lines],
                    'selection_marks': [{'state': selection_mark.state, 'confidence': selection_mark.confidence} for selection_mark in page.selection_marks]
                }
                response_data['pages'].append(page_data)

                if hasattr(page, 'tables'):
                    tables_data = []
                    for table in page.tables:
                        table_data = {
                            'row_count': table.row_count,
                            'column_count': table.column_count,
                            'cells': [{'content': cell.content} for cell in table.cells]
                        }
                        tables_data.append(table_data)
                    page_data['tables'] = tables_data

            return jsonify(response_data), 200

        except Exception as e:
            return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0',debug=True)

