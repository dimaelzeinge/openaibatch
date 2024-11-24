# OpenAI Batch Tools

Some simple tools to convert a CSV file to JSONL, split a JSONL file into multiple parts, and extract responses from JSONL files. These tools are designed to help you prepare data for OpenAI batch processing.

## Screenshot

![screenshot](https://i.postimg.cc/KvHHGSBK/Screenshot-2024-11-24-at-3-35-44-AM.png)

## Features

1. **CSV to JSONL Converter**
   - Convert CSV files to JSONL format for OpenAI batch processing
   - Customize system prompts and model parameters

2. **JSONL File Splitter**
   - Split large JSONL files into smaller parts
   - Specify the number of splits needed

3. **JSONL Response Extractor**
   - Convert JSONL files to CSV format

## Installation

1. Clone the repository: 
```
git clone https://github.com/yourusername/openai-batch-tools.git
```
2. Install dependencies: 
```
cd openai-batch-tools
pip install -r requirements.txt
```
3. Run the application: 
```
python app.py
```