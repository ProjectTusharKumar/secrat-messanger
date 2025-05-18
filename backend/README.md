# Backend for Secret Messaging App with Steganography

This backend uses FastAPI, Pillow, and cryptography to encode and decode secret messages in images using a secret key.

## Setup

1. Install dependencies:
   pip install fastapi uvicorn pillow cryptography python-multipart

2. Run the server:
   uvicorn main:app --reload

## Endpoints

- POST /encode: Hide an encrypted message in an image.
- POST /decode: Extract and decrypt a message from an image.

Place your backend code in this folder.
