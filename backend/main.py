import os
import io
import secrets
from fastapi import FastAPI, File, UploadFile, Form, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, JSONResponse
from PIL import Image
from stegano import lsb
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend
import base64
from dotenv import load_dotenv
from slowapi import Limiter
from slowapi.util import get_remote_address
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.middleware.httpsredirect import HTTPSRedirectMiddleware
from starlette.middleware.trustedhost import TrustedHostMiddleware
from starlette.middleware.cors import CORSMiddleware as StarletteCORSMiddleware
from slowapi.errors import RateLimitExceeded
from fastapi.responses import PlainTextResponse
from slowapi.extension import Limiter as LimiterExtension
import requests
from datetime import datetime
from pymongo import MongoClient
from other_steg_algorithms import (
    palette_lsb_hide, palette_lsb_reveal,
    dct_hide, dct_reveal,
    alpha_lsb_hide, alpha_lsb_reveal,
    audio_lsb_hide, audio_lsb_reveal
)

app = FastAPI()

# Load environment variables
load_dotenv()

# CORS and frontend configuration
FRONTEND_ORIGIN = os.getenv("FRONTEND_ORIGIN", "")

# Rate limiter
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter

# Secure CORS for frontend integration
app.add_middleware(
    StarletteCORSMiddleware,
    allow_origins=[FRONTEND_ORIGIN ,"https://secrat-messanger.vercel.app/"],
    allow_credentials=True,
    allow_methods=["POST", "GET"],
    allow_headers=["*"],
)

# Security headers middleware
class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=63072000; includeSubDomains; preload"
        return response

app.add_middleware(SecurityHeadersMiddleware)

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

@app.exception_handler(RateLimitExceeded)
def rate_limit_handler(request, exc):
    return PlainTextResponse("Rate limit exceeded. Please try again later.", status_code=429)

@app.post("/api/embed", summary="Embed a secret message in an image or audio using steganography.")
@limiter.limit("5/minute")
async def embed_message(
    request: Request,
    image: UploadFile = File(None),
    audio: UploadFile = File(None),
    message: str = Form(...),
    summarize: bool = Form(False),
    algorithm: str = Form("lsb")
):
    # Validate input
    if not image and not audio:
        raise HTTPException(status_code=400, detail="No file uploaded.")
    if image and not image.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Invalid image file.")
    if audio and not audio.content_type.startswith("audio/"):
        raise HTTPException(status_code=400, detail="Invalid audio file.")
    # Optionally summarize message with external API
    if summarize and len(message) > 100:
        try:
            # Example: Use HuggingFace Inference API (replace YOUR_API_KEY)
            api_url = "https://api-inference.huggingface.co/models/facebook/bart-large-cnn"
            headers = {"Authorization": f"Bearer {os.getenv('HF_API_KEY', '')}"}
            payload = {"inputs": message, "parameters": {"max_length": 60, "min_length": 20, "do_sample": False}}
            resp = requests.post(api_url, headers=headers, json=payload, timeout=10)
            if resp.ok:
                summary = resp.json()
                if isinstance(summary, list) and 'summary_text' in summary[0]:
                    message = summary[0]['summary_text']
        except Exception:
            pass  # Fallback to original message if API fails
    # Generate hash key and salt
    hash_key = generate_hash_key()
    salt = secrets.token_bytes(16)
    key = derive_key(hash_key, salt)
    enc_msg = base64.urlsafe_b64encode(bytes([b ^ key[i % len(key)] for i, b in enumerate(message.encode())]))
    payload = base64.urlsafe_b64encode(salt + enc_msg).decode()
    # Handle image algorithms
    if image:
        img_bytes = await image.read()
        img_path = f"/tmp/in_{secrets.token_hex(8)}.png"
        out_path = f"/tmp/out_{secrets.token_hex(8)}.png"
        with open(img_path, "wb") as f:
            f.write(img_bytes)
        # --- Steganography algorithms unified block ---
        img_base64 = None
        try:
            if algorithm == "lsb":
                img = Image.open(img_path)
                secret_img = lsb.hide(img, payload)
                buf = io.BytesIO()
                secret_img.save(buf, format=img.format or "PNG")
                buf.seek(0)
                img_base64 = base64.b64encode(buf.getvalue()).decode()
            elif algorithm == "palette_lsb":
                img = Image.open(img_path)
                if img.mode != 'P':
                    raise HTTPException(status_code=400, detail="Palette LSB only works with palette-based images (mode 'P', e.g. GIF or 8-bit PNG). Please upload a suitable image.")
                palette_lsb_hide(img_path, payload, out_path)
                with open(out_path, "rb") as f:
                    img_base64 = base64.b64encode(f.read()).decode()
            elif algorithm == "dct":
                img = Image.open(img_path)
                if img.format not in ["JPEG", "JPG"]:
                    raise HTTPException(status_code=400, detail="DCT steganography only works with JPEG images.")
                dct_hide(img_path, payload, out_path)
                with open(out_path, "rb") as f:
                    img_base64 = base64.b64encode(f.read()).decode()
            elif algorithm == "alpha_lsb":
                img = Image.open(img_path)
                if img.mode != 'RGBA':
                    raise HTTPException(status_code=400, detail="Alpha LSB only works with PNG images with transparency (mode 'RGBA'). Please upload a suitable image.")
                alpha_lsb_hide(img_path, payload, out_path)
                with open(out_path, "rb") as f:
                    img_base64 = base64.b64encode(f.read()).decode()
            else:
                raise HTTPException(status_code=400, detail="Unsupported steganography algorithm.")
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"{algorithm} embedding failed: {str(e)}")
        return JSONResponse({
            "image": img_base64,
            "hashKey": hash_key,
            "filename": f"secret_{image.filename}",
            "contentType": image.content_type
        })
        # --- End unified block ---
    # Handle audio algorithm
    elif audio:
        audio_bytes = await audio.read()
        wav_in = f"/tmp/in_{secrets.token_hex(8)}.wav"
        wav_out = f"/tmp/out_{secrets.token_hex(8)}.wav"
        with open(wav_in, "wb") as f:
            f.write(audio_bytes)
        if algorithm == "audio_lsb":
            audio_lsb_hide(wav_in, payload, wav_out)
            with open(wav_out, "rb") as f:
                audio_base64 = base64.b64encode(f.read()).decode()
            return JSONResponse({
                "audio": audio_base64,
                "hashKey": hash_key,
                "filename": f"secret_{audio.filename}",
                "contentType": audio.content_type
            })
        else:
            raise HTTPException(status_code=400, detail="Unsupported steganography algorithm for audio.")

@app.post("/api/extract", summary="Extract and decrypt a secret message from an image or audio using steganography.")
@limiter.limit("10/minute")
async def extract_message(
    request: Request,
    image: UploadFile = File(None),
    audio: UploadFile = File(None),
    hash_key: str = Form(...),
    algorithm: str = Form("lsb")
):
    if not image and not audio:
        raise HTTPException(status_code=400, detail="No file uploaded.")
    if image and not image.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Invalid image file.")
    if audio and not audio.content_type.startswith("audio/"):
        raise HTTPException(status_code=400, detail="Invalid audio file.")
    # Handle image algorithms
    if image:
        img_bytes = await image.read()
        img_path = f"/tmp/in_{secrets.token_hex(8)}.png"
        with open(img_path, "wb") as f:
            f.write(img_bytes)
        if algorithm == "lsb":
            img = Image.open(img_path)
            payload = lsb.reveal(img)
        elif algorithm == "palette_lsb":
            payload = palette_lsb_reveal(img_path)
        elif algorithm == "dct":
            payload = dct_reveal(img_path)
        elif algorithm == "alpha_lsb":
            payload = alpha_lsb_reveal(img_path)
        else:
            raise HTTPException(status_code=400, detail="Unsupported steganography algorithm.")
    # Handle audio algorithm
    elif audio:
        audio_bytes = await audio.read()
        wav_in = f"/tmp/in_{secrets.token_hex(8)}.wav"
        with open(wav_in, "wb") as f:
            f.write(audio_bytes)
        if algorithm == "audio_lsb":
            payload = audio_lsb_reveal(wav_in)
        else:
            raise HTTPException(status_code=400, detail="Unsupported steganography algorithm for audio.")
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
