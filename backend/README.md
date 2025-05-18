# Secret Message App Backend

This is a secure Python FastAPI backend for a steganography-based secret message app.

## Features
- Embed secret messages in images using steganography and a hash key
- Extract hidden messages from images using the hash key
- Secure cryptography and file handling
- CORS enabled for frontend integration

## Endpoints
- `POST /api/embed`: Upload image + message, returns updated image + hash key
- `POST /api/extract`: Upload image + hash key, returns extracted message

## Setup
1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Run the server:
   ```bash
   uvicorn main:app --reload
   ```

## Security
- Uses strong cryptography for hash key
- Validates and sanitizes all file uploads
- CORS enabled for frontend

---

Replace `.env.example` with your own `.env` for production secrets.
