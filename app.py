from flask import Flask, render_template, request, send_file, flash, redirect, url_for
import pandas as pd
import json
import io
import secrets
import math
import zipfile
import csv

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)

@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')

# Format routes
@app.route('/format', methods=['GET'])
def format_page():
    return render_template('format.html')

@app.route('/format', methods=['POST'])
def format_csv():
    try:
        if 'csv_file' not in request.files:
            return 'Please select a file to upload', 400
        
        csv_file = request.files['csv_file']
        if csv_file.filename == '':
            return 'No file selected', 400
            
        model = request.form.get('model')
        if not model:
            return 'Model is required', 400
            
        system_prompt = request.form['system_prompt']
        max_tokens = int(request.form['max_tokens'])
        content_column = request.form['content_column']
        
        temp_file = io.BytesIO()
        csv_file.save(temp_file)
        temp_file.seek(0)
        
        df = pd.read_csv(temp_file)
        output = io.BytesIO()
        
        def process_row(row):
            return {
                "custom_id": f"request-{row.name+1}",
                "method": "POST",
                "url": "/v1/chat/completions",
                "body": {
                    "model": model,
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": str(row[content_column])}
                    ],
                    "max_tokens": max_tokens
                }
            }
        
        results = [process_row(row) for _, row in df.iterrows()]
        for item in results:
            output.write(json.dumps(item, ensure_ascii=False).encode('utf-8') + b'\n')
                
        output.seek(0)
        response = send_file(
            output,
            mimetype='text/plain',
            as_attachment=True,
            download_name='output.jsonl'
        )
        response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
        return response
        
    except Exception as e:
        return str(e), 500

# Split routes
@app.route('/split', methods=['GET'])
def split_page():
    return render_template('split.html')

@app.route('/split', methods=['POST'])
def split_jsonl():
    try:
        if 'jsonl_file' not in request.files:
            return 'Please select a file to upload', 400
        
        file = request.files['jsonl_file']
        if file.filename == '' or not file.filename.endswith('.jsonl'):
            return 'Please select a valid JSONL file', 400
            
        split_number = int(request.form.get('split_number', 2))
        
        lines = file.read().decode('utf-8').splitlines()
        
        if not lines:
            return 'The file is empty', 400

        total_lines = len(lines)
        lines_per_file = math.ceil(total_lines / split_number)
        
        memory_file = io.BytesIO()
        with zipfile.ZipFile(memory_file, 'w', zipfile.ZIP_DEFLATED) as zf:
            for i in range(split_number):
                start_idx = i * lines_per_file
                end_idx = min((i + 1) * lines_per_file, total_lines)
                
                if start_idx >= total_lines:
                    break
                    
                content = '\n'.join(lines[start_idx:end_idx])
                if content.strip():
                    zf.writestr(f'part_{i+1}.jsonl', content)

        memory_file.seek(0)
        
        response = send_file(
            memory_file,
            mimetype='application/zip',
            as_attachment=True,
            download_name='split_files.zip'
        )
        response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
        return response
            
    except Exception as e:
        return str(e), 500

# Extract routes
@app.route('/extract', methods=['GET'])
def extract_page():
    return render_template('extract.html')

@app.route('/extract', methods=['POST'])
def extract_jsonl():
    try:
        if 'jsonl_file' not in request.files:
            return 'Please select a file to upload', 400
        
        file = request.files['jsonl_file']
        if file.filename == '' or not file.filename.endswith('.jsonl'):
            return 'Please select a valid JSONL file', 400
            
        lines = file.read().decode('utf-8').splitlines()
        
        if not lines:
            return 'The file is empty', 400

        # Create a CSV file in memory
        output = io.StringIO()
        writer = csv.writer(output, quoting=csv.QUOTE_NONE, escapechar='\\')  # Disable quoting
        writer.writerow(['custom_id', 'content'])  # CSV header
        
        # First pass: collect all custom_ids
        custom_ids = set()
        content_map = {}
        
        for line in lines:
            try:
                data = json.loads(line)
                custom_id = data.get('custom_id', '')
                if custom_id:
                    custom_ids.add(custom_id)
                    content = data.get('response', {}).get('body', {}).get('choices', [{}])[0].get('message', {}).get('content', '')
                    if content:  # Only store if content is not empty
                        content_map[custom_id] = content
            except (json.JSONDecodeError, KeyError, IndexError) as e:
                continue
        
        # Second pass: write rows in order, with empty content for missing responses
        for custom_id in sorted(custom_ids):
            content = content_map.get(custom_id, '')  # Get content or empty string if not found
            writer.writerow([custom_id, content])
        
        # Convert StringIO to BytesIO
        output_bytes = io.BytesIO()
        output_bytes.write(output.getvalue().encode('utf-8-sig'))  # Use UTF-8 with BOM for correct Chinese display in Excel
        output_bytes.seek(0)
        output.close()
        
        response = send_file(
            output_bytes,
            mimetype='text/csv',
            as_attachment=True,
            download_name='extracted_content.csv'
        )
        response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
        return response
            
    except Exception as e:
        return str(e), 500

if __name__ == '__main__':
    app.run()