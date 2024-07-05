from flask import Flask, request, jsonify
from azure.core.credentials import AzureKeyCredential
from azure.ai.formrecognizer import DocumentAnalysisClient
from flask_cors import CORS
import io

app = Flask(__name__)
CORS(app)
# Azure Form Recognizer endpoint and API key
endpoint = "https://babithdocument.cognitiveservices.azure.com/"
key = "1520cd9775ee4d51ba5dff5d1d40b73d"
 # Prebuilt layout model ID

@app.route('/analyze', methods=['POST'])
def analyze_document():
    model_id = "skillextractionmodel"
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
    
@app.route('/analyze1', methods=['POST'])
def analyze_document1():
    model_id = "resumemodel" 
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

            # Read file content into bytes
            file_bytes = file.read()

            # Analyze the document from the byte stream
            poller = document_analysis_client.begin_analyze_document(model_id, io.BytesIO(file_bytes))
            result = poller.result()

            # Prepare JSON response
            response_data = {
                'documents': [],
                'pages': [],
                'tables': []
            }

            # Process the analysis results
            for idx, document in enumerate(result.documents):
                document_data = {
                    'doc_type': document.doc_type,
                    'confidence': document.confidence,
                    'fields': {name: field.value if field.value else field.content for name, field in document.fields.items()}
                }
                response_data['documents'].append(document_data)

            for page in result.pages:
                page_data = {
                    'page_number': page.page_number,
                    'lines': [line.content for line in page.lines],
                    'words': [(word.content, word.confidence) for word in page.words],
                    'selection_marks': [{'state': selection_mark.state, 'confidence': selection_mark.confidence} for selection_mark in page.selection_marks]
                }
                response_data['pages'].append(page_data)

            for table in result.tables:
                table_data = {
                    'bounding_regions': [region.page_number for region in table.bounding_regions],
                    'cells': [{'row_index': cell.row_index, 'column_index': cell.column_index, 'content': cell.content} for cell in table.cells]
                }
                response_data['tables'].append(table_data)

            return jsonify(response_data), 200

        except Exception as e:
            return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0',debug=True)

