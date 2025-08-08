import os
import uvicorn
from fastapi import FastAPI, HTTPException, Depends, File, UploadFile, Form
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
from collections import deque
import jwt
import bcrypt
import requests
from datetime import datetime, timedelta
import fitz  # PyMuPDF
from docx import Document
from bs4 import BeautifulSoup
import base64
from io import BytesIO
from PIL import Image

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

app = FastAPI(title="Multi-Modal AI API", version="2.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security
security = HTTPBearer()
JWT_SECRET = os.getenv("JWT_SECRET", "your-secret-key")
HF_TOKEN = os.getenv("HF_TOKEN")

# Hugging Face Inference Endpoints
MISTRAL_API_URL = "https://api-inference.huggingface.co/models/mistralai/Mistral-7B-Instruct-v0.3"
DEEPSEEK_VL_API_URL = "https://api-inference.huggingface.co/models/deepseek-ai/deepseek-vl-1.3b-chat"

# In-memory storage
users_db = {}
user_history = {}

# Models
class UserCreate(BaseModel):
    username: str
    password: str

class UserLogin(BaseModel):
    username: str
    password: str

# Utility functions
def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def verify_password(password: str, hashed: str) -> bool:
    return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))

def create_jwt_token(username: str) -> str:
    payload = {
        "username": username,
        "exp": datetime.utcnow() + timedelta(hours=24)
    }
    return jwt.encode(payload, JWT_SECRET, algorithm="HS256")

def verify_jwt_token(token: str) -> str:
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
        return payload["username"]
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> str:
    return verify_jwt_token(credentials.credentials)

async def analyze_image_api(image: Image.Image, prompt: str = None) -> str:
    """Analyze image using DeepSeek-VL via Hugging Face API"""
    try:
        # Convert image to base64
        buffered = BytesIO()
        image.save(buffered, format="PNG")
        img_base64 = base64.b64encode(buffered.getvalue()).decode()
        
        headers = {"Authorization": f"Bearer {HF_TOKEN}"}
        
        if not prompt:
            prompt = "Describe this image in detail, including objects, people, colors, setting, activities, and overall atmosphere."
        
        payload = {
            "inputs": {
                "text": prompt,
                "image": img_base64
            },
            "parameters": {
                "max_new_tokens": 512,
                "temperature": 0.7,
                "do_sample": True
            }
        }
        
        response = requests.post(DEEPSEEK_VL_API_URL, headers=headers, json=payload, timeout=30)
        response.raise_for_status()
        result = response.json()
        
        if isinstance(result, list) and len(result) > 0:
            return result[0].get("generated_text", "Analysis completed via DeepSeek-VL API")
        elif isinstance(result, dict) and "generated_text" in result:
            return result["generated_text"]
        
        return "Image analysis completed via DeepSeek-VL API."
        
    except Exception as e:
        return f"Image analysis failed: {str(e)}"

async def summarize_text_api(text: str, max_length: int = 300) -> str:
    """Summarize text using Mistral 7B Instruct via Hugging Face API"""
    try:
        headers = {"Authorization": f"Bearer {HF_TOKEN}"}
        prompt = f"""<s>[INST] Please provide a concise summary of the following text. Focus on the main points, key information, and important details:

{text[:2000]}

Provide a clear, informative summary in 2-3 paragraphs. [/INST]"""
        
        payload = {
            "inputs": prompt,
            "parameters": {
                "max_new_tokens": max_length,
                "temperature": 0.7,
                "top_p": 0.9,
                "return_full_text": False
            }
        }
        
        response = requests.post(MISTRAL_API_URL, headers=headers, json=payload, timeout=30)
        response.raise_for_status()
        result = response.json()
        
        if isinstance(result, list) and len(result) > 0:
            return result[0].get("generated_text", "Summary generated via Mistral 7B API").strip()
        elif isinstance(result, dict) and "generated_text" in result:
            return result["generated_text"].strip()
        
        return "Summary generated via Mistral 7B API."
        
    except Exception as e:
        return f"Summarization failed: {str(e)}"

def extract_text_from_pdf(file_content: bytes) -> str:
    doc = fitz.open(stream=file_content, filetype="pdf")
    text = ""
    for page in doc:
        text += page.get_text()
    doc.close()
    return text

def extract_text_from_docx(file_content: bytes) -> str:
    doc = Document(BytesIO(file_content))
    text = ""
    for paragraph in doc.paragraphs:
        text += paragraph.text + "\n"
    return text

def scrape_url_content(url: str) -> str:
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Remove script and style elements
        for script in soup(["script", "style"]):
            script.decompose()
        
        text = soup.get_text()
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        text = ' '.join(chunk for chunk in chunks if chunk)
        return text[:8000]
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to scrape URL: {str(e)}")

def add_to_history(username: str, item_type: str, input_data: str, output: str):
    if username not in user_history:
        user_history[username] = deque(maxlen=20)
    
    history_item = {
        "type": item_type,
        "input_data": input_data,
        "output": output,
        "timestamp": datetime.utcnow().isoformat()
    }
    user_history[username].append(history_item)

# Auth endpoints
@app.post("/auth/signup")
async def signup(user: UserCreate):
    if user.username in users_db:
        raise HTTPException(status_code=400, detail="Username already exists")
    
    users_db[user.username] = {
        "username": user.username,
        "password": hash_password(user.password)
    }
    
    token = create_jwt_token(user.username)
    return {"message": "User created successfully", "token": token}

@app.post("/auth/login")
async def login(user: UserLogin):
    if user.username not in users_db:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    if not verify_password(user.password, users_db[user.username]["password"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    token = create_jwt_token(user.username)
    return {"message": "Login successful", "token": token}

# Image analysis endpoint
@app.post("/image/analyze")
async def analyze_image(
    file: UploadFile = File(...),
    prompt: Optional[str] = Form(None),
    current_user: str = Depends(get_current_user)
):
    if file.content_type not in ["image/jpeg", "image/jpg", "image/png", "image/webp"]:
        raise HTTPException(status_code=400, detail="Only JPG, PNG, and WebP images are supported")
    
    try:
        # Read and process image
        image_content = await file.read()
        image = Image.open(BytesIO(image_content)).convert('RGB')
        
        # Resize if too large
        if image.size[0] > 768 or image.size[1] > 768:
            image.thumbnail((768, 768), Image.Resampling.LANCZOS)
        
        # Analyze image using DeepSeek-VL API
        description = await analyze_image_api(image, prompt)
        
        # Add to history
        add_to_history(current_user, "image_analysis", file.filename, description)
        
        return {
            "description": description, 
            "filename": file.filename,
            "image_size": image.size,
            "model_used": "DeepSeek-VL (API)"
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to analyze image: {str(e)}")

# Document/URL summarization endpoint
@app.post("/doc/summarize")
async def summarize_document(
    file: Optional[UploadFile] = File(None),
    url: Optional[str] = Form(None),
    max_length: Optional[int] = Form(300),
    current_user: str = Depends(get_current_user)
):
    if not file and not url:
        raise HTTPException(status_code=400, detail="Either file or URL must be provided")
    
    if file and url:
        raise HTTPException(status_code=400, detail="Provide either file or URL, not both")
    
    try:
        text_content = ""
        input_source = ""
        
        if file:
            file_content = await file.read()
            input_source = file.filename
            
            if file.content_type == "application/pdf":
                text_content = extract_text_from_pdf(file_content)
            elif file.content_type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
                text_content = extract_text_from_docx(file_content)
            elif file.content_type == "text/plain":
                text_content = file_content.decode('utf-8')
            else:
                raise HTTPException(status_code=400, detail="Only PDF, DOCX, and TXT files are supported")
        
        elif url:
            text_content = scrape_url_content(url)
            input_source = url
        
        if not text_content.strip():
            raise HTTPException(status_code=400, detail="No text content found")
        
        # Summarize using Mistral 7B Instruct API
        summary = await summarize_text_api(text_content, max_length)
        
        # Add to history
        add_to_history(current_user, "document_summary", input_source, summary)
        
        return {
            "summary": summary, 
            "source": input_source,
            "original_length": len(text_content),
            "summary_length": len(summary),
            "compression_ratio": round(len(summary) / len(text_content) * 100, 2),
            "model_used": "Mistral-7B-Instruct-v0.3 (API)"
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to summarize: {str(e)}")

# History endpoint
@app.get("/history")
async def get_history(
    limit: int = 20,
    item_type: Optional[str] = None,
    current_user: str = Depends(get_current_user)
):
    if current_user not in user_history:
        return {"history": []}
    
    history_list = list(user_history[current_user])
    
    # Filter by type if specified
    if item_type:
        history_list = [item for item in history_list if item["type"] == item_type]
    
    # Apply limit
    history_list = history_list[-limit:]
    
    return {"history": history_list, "total": len(history_list)}

# Health check
@app.get("/")
async def root():
    return {
        "message": "Multi-Modal AI API is running",
        "version": "2.0.0",
        "features": ["image_analysis", "document_summarization", "url_scraping"],
        "models": {
            "vision": "DeepSeek-VL-1.3B-Chat (API)",
            "text": "Mistral-7B-Instruct-v0.3 (API)",
            "deployment": "Vercel Serverless"
        }
    }

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)