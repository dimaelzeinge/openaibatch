# OpenAI Batch Tools

Some simple tools to convert a CSV file to JSONL, split a JSONL file into multiple parts, and extract responses from JSONL files. These tools are designed to help you prepare data for OpenAI batch processing.

## Screenshot

![screenshot](https://i.postimg.cc/s2t7yDwP/Screenshot-2024-11-21-at-11-46-32-PM.png)
![screenshot2](https://i.postimg.cc/L89V0Xbn/Screenshot-2024-11-26-at-10-54-48-AM.png)
![screenshot3](https://i.postimg.cc/bJt022sF/Screenshot-2024-11-26-at-10-54-52-AM.png)
![screenshot4](https://i.postimg.cc/HLJXf74s/Screenshot-2024-11-26-at-10-54-55-AM.png)

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