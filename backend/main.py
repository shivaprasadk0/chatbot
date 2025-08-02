from fastapi import FastAPI, File, UploadFile, Form, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from openai import OpenAI
from dotenv import load_dotenv
import os
from pathlib import Path
import shutil
import tempfile

# -------------------------------
# Load environment variables from .env
# -------------------------------
load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise ValueError("❌ OPENAI_API_KEY is not set in .env file or environment.")

client = OpenAI(api_key=api_key)

app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static and templates
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

UPLOAD_DIR = Path(tempfile.gettempdir()) / "chatbot_uploads"
UPLOAD_DIR.mkdir(exist_ok=True)

# -------------------------------
# Helper: ChatGPT call
# -------------------------------
def get_chatgpt_reply(prompt: str) -> str:
    try:
        chat_completion = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You're a helpful assistant."},
                {"role": "user", "content": prompt}
            ]
        )
        return chat_completion.choices[0].message.content.strip()
    except Exception as e:
        return f"❌ Error: {str(e)}"

# -------------------------------
# Routes
# -------------------------------
@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/favicon.ico")
async def favicon():
    return FileResponse("static/favicon.ico")

@app.post("/chat")
async def chat(text: str = Form(...), file: UploadFile = File(None)):
    file_msg = ""
    if file:
        try:
            file_location = UPLOAD_DIR / file.filename
            with open(file_location, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
            file_msg = f"\n(File '{file.filename}' uploaded successfully.)"
        except Exception as e:
            file_msg = f"\n(❌ Error saving file: {str(e)})"

    full_prompt = text
    if file:
        full_prompt += f"\n\nThe user uploaded a file named '{file.filename}'."

    reply = get_chatgpt_reply(full_prompt)
    return JSONResponse(content={"reply": reply + file_msg})
