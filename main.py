import os
import shutil
from fastapi import FastAPI, UploadFile, File, Request
from fastapi.responses import HTMLResponse, FileResponse, RedirectResponse
from jinja2 import Template

app = FastAPI(title="Global Satellite Drive")

# Isolated storage directory on the host server
STORAGE_DIR = os.path.abspath("./user_files")
os.makedirs(STORAGE_DIR, exist_ok=True)

HTML_LAYOUT = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Global Drive</title>
    <style>
        * { box-sizing: border-box; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; }
        body { background-color: #f8f9fa; margin: 0; padding: 20px; color: #333; }
        .container { max-width: 900px; margin: 0 auto; background: #ffffff; padding: 24px; border-radius: 12px; box-shadow: 0 4px 12px rgba(0,0,0,0.05); }
        h1 { margin-top: 0; color: #1a73e8; display: flex; align-items: center; gap: 10px; }
        .upload-box { border: 2px dashed #dadce0; border-radius: 8px; padding: 24px; text-align: center; background: #f8f9fa; margin: 20px 0; }
        .btn { background: #1a73e8; color: white; border: none; padding: 10px 18px; border-radius: 6px; cursor: pointer; text-decoration: none; font-weight: 500; font-size: 14px; display: inline-block; }
        .btn:hover { background: #1557b0; }
        .btn-danger { background: #d93025; }
        .btn-danger:hover { background: #b3261e; }
        table { width: 100%; border-collapse: collapse; margin-top: 20px; }
        th, td { text-align: left; padding: 12px; border-bottom: 1px solid #e8eaed; }
        th { color: #5f6368; font-weight: 500; }
        .actions { display: flex; gap: 8px; }
    </style>
</head>
<body>
    <div class="container">
        <h1>☁️ Global Satellite File Manager</h1>
        <p>Access your files from any satellite connection or device worldwide.</p>
        
        <div class="upload-box">
            <form action="/upload" method="post" enctype="multipart/form-data">
                <input type="file" name="file" required style="margin-bottom: 12px;"><br>
                <button type="submit" class="btn">Upload File</button>
            </form>
        </div>

        <table>
            <thead>
                <tr>
                    <th>File Name</th>
                    <th>Size</th>
                    <th>Actions</th>
                </tr>
            </thead>
            <tbody>
                {% for item in files %}
                <tr>
                    <td><strong>{{ item.name }}</strong></td>
                    <td>{{ item.size }} MB</td>
                    <td class="actions">
                        <a href="/download/{{ item.name }}" class="btn">Download</a>
                        <a href="/delete/{{ item.name }}" class="btn btn-danger">Delete</a>
                    </td>
                </tr>
                {% else %}
                <tr>
                    <td colspan="3" style="text-align: center; color: #70757a; padding: 24px;">No files found in your global drive.</td>
                </tr>
                {% endfor %}
            </tbody>
        </table>
    </div>
</body>
</html>
"""

@app.get("/", response_class=HTMLResponse)
def home():
    files_data = []
    for fname in os.listdir(STORAGE_DIR):
        fpath = os.path.join(STORAGE_DIR, fname)
        if os.path.isfile(fpath):
            size_mb = round(os.path.getsize(fpath) / (1024 * 1024), 2)
            files_data.append({"name": fname, "size": size_mb})
    return Template(HTML_LAYOUT).render(files=files_data)

@app.post("/upload")
async def handle_upload(file: UploadFile = File(...)):
    dest = os.path.join(STORAGE_DIR, file.filename)
    with open(dest, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    return RedirectResponse(url="/", status_code=303)

@app.get("/download/{filename}")
def handle_download(filename: str):
    fpath = os.path.join(STORAGE_DIR, filename)
    if os.path.exists(fpath):
        return FileResponse(path=fpath, filename=filename)
    return HTMLResponse("File Not Found", status_code=404)

@app.get("/delete/{filename}")
def handle_delete(filename: str):
    fpath = os.path.join(STORAGE_DIR, filename)
    if os.path.exists(fpath):
        os.remove(fpath)
    return RedirectResponse(url="/", status_code=303)