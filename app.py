from fastapi import FastAPI, UploadFile, Form, HTTPException
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.requests import Request
import pandas as pd
import json
import io
import math
import zipfile

app = FastAPI()

# 添加CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 修改静态文件和模板配置
templates = Jinja2Templates(directory="templates")
try:
    app.mount("/static", StaticFiles(directory="static"), name="static")
except:
    pass

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/format", response_class=HTMLResponse)
async def format_page(request: Request):
    return templates.TemplateResponse("format.html", {"request": request})

@app.post("/format")
async def format_csv(
    csv_file: UploadFile,
    model: str = Form(...),
    system_prompt: str = Form(...),
    max_tokens: int = Form(...),
    temperature: float = Form(default=1.0),
    content_column: str = Form(...)
):
    try:
        if not csv_file:
            raise HTTPException(status_code=400, detail="Please select a file to upload")
            
        contents = await csv_file.read()
        df = pd.read_csv(io.BytesIO(contents))
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
                    "temperature": temperature,
                    "max_tokens": max_tokens
                }
            }
        
        results = [process_row(row) for _, row in df.iterrows()]
        for item in results:
            output.write(json.dumps(item, ensure_ascii=False).encode('utf-8') + b'\n')
                
        output.seek(0)
        return FileResponse(
            output,
            media_type='text/plain',
            filename='output.jsonl',
            headers={"Cache-Control": "no-cache, no-store, must-revalidate"}
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/split", response_class=HTMLResponse)
async def split_page(request: Request):
    return templates.TemplateResponse("split.html", {"request": request})

@app.post("/split")
async def split_jsonl(
    jsonl_file: UploadFile,
    split_number: int = Form(default=2)
):
    try:
        if not jsonl_file or not jsonl_file.filename.endswith('.jsonl'):
            raise HTTPException(status_code=400, detail="Please select a valid JSONL file")
            
        contents = await jsonl_file.read()
        lines = contents.decode('utf-8').splitlines()
        
        if not lines:
            raise HTTPException(status_code=400, detail="The file is empty")

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
        return FileResponse(
            memory_file,
            media_type='application/zip',
            filename='split_files.zip',
            headers={"Cache-Control": "no-cache, no-store, must-revalidate"}
        )
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/extract", response_class=HTMLResponse)
async def extract_page(request: Request):
    return templates.TemplateResponse("extract.html", {"request": request})

@app.post("/extract")
async def extract_jsonl(jsonl_file: UploadFile):
    try:
        if not jsonl_file or not jsonl_file.filename.endswith('.jsonl'):
            raise HTTPException(status_code=400, detail="Please select a valid JSONL file")
            
        contents = await jsonl_file.read()
        lines = contents.decode('utf-8').splitlines()
        
        if not lines:
            raise HTTPException(status_code=400, detail="The file is empty")

        data = []
        processed_ids = set()
        
        for line in lines:
            try:
                json_data = json.loads(line)
                custom_id = json_data.get('custom_id', '')
                if custom_id and custom_id not in processed_ids:
                    processed_ids.add(custom_id)
                    content = json_data.get('response', {}).get('body', {}).get('choices', [{}])[0].get('message', {}).get('content', '')
                    data.append({'custom_id': custom_id, 'content': content})
            except (json.JSONDecodeError, KeyError, IndexError):
                continue
        
        df = pd.DataFrame(data)
        output = io.BytesIO()
        df.to_csv(output, index=False, encoding='utf-8-sig')
        output.seek(0)
        
        return FileResponse(
            output,
            media_type='text/csv',
            filename='extracted_content.csv',
            headers={"Cache-Control": "no-cache, no-store, must-revalidate"}
        )
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    return {"status": "ok"}