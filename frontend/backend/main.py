import os
import io
import secrets
from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, JSONResponse
from PIL import Image
from stegano import lsb
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend
import base64
from transformers import pipeline

app = FastAPI()

# CORS for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load AI pipelines (NLP and image enhancement)
nlp_summarizer = pipeline("summarization", model="facebook/bart-large-cnn")
# Optionally, add more AI models for image enhancement or steganalysis

# Helper: Generate a strong hash key
def generate_hash_key():
    return secrets.token_urlsafe(32)

# Helper: Derive a key from hash key
def derive_key(hash_key: str, salt: bytes):
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100_000,
        backend=default_backend()
    )
    return kdf.derive(hash_key.encode())

@app.post("/api/embed")
async def embed_message(
    image: UploadFile = File(...),
    message: str = Form(...),
    summarize: bool = Form(False)
):
    # Validate file type
    if not image.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Invalid image file.")
    # Optionally summarize message with AI
    if summarize and len(message) > 100:
        try:
            summary = nlp_summarizer(message, max_length=60, min_length=20, do_sample=False)
            message = summary[0]['summary_text']
        except Exception:
            pass  # Fallback to original message if AI fails
    # Read image
    img_bytes = await image.read()
    img = Image.open(io.BytesIO(img_bytes))
    # Generate hash key and salt
    hash_key = generate_hash_key()
    salt = secrets.token_bytes(16)
    # Encrypt message with derived key (simple XOR for demo, use strong encryption in prod)
    key = derive_key(hash_key, salt)
    enc_msg = base64.urlsafe_b64encode(bytes([b ^ key[i % len(key)] for i, b in enumerate(message.encode())]))
    # Hide salt + encrypted message
    payload = base64.urlsafe_b64encode(salt + enc_msg).decode()
    secret_img = lsb.hide(img, payload)
    # Save to buffer
    buf = io.BytesIO()
    secret_img.save(buf, format=img.format or "PNG")
    buf.seek(0)
    # Return image and hash key
    return StreamingResponse(
        buf,
        media_type=image.content_type,
        headers={
            "Content-Disposition": f"attachment; filename=secret_{image.filename}",
            "X-Hash-Key": hash_key
        }
    )

@app.post("/api/extract")
async def extract_message(
    image: UploadFile = File(...),
    hash_key: str = Form(...)
):
    if not image.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Invalid image file.")
    img_bytes = await image.read()
    img = Image.open(io.BytesIO(img_bytes))
    payload = lsb.reveal(img)
    if not payload:
        raise HTTPException(status_code=404, detail="No hidden message found.")
    try:
        data = base64.urlsafe_b64decode(payload)
        salt, enc_msg = data[:16], data[16:]
        key = derive_key(hash_key, salt)
        dec_msg = bytes([b ^ key[i % len(key)] for i, b in enumerate(base64.urlsafe_b64decode(enc_msg))]).decode()
    except Exception:
        raise HTTPException(status_code=400, detail="Failed to decrypt message. Check your hash key.")
    return JSONResponse({"message": dec_msg})

@app.get("/")
def root():
    return {"status": "Secret Message API running"}
