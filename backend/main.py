from fastapi import FastAPI, File, UploadFile, Form
from fastapi.responses import StreamingResponse, JSONResponse
from pydantic import BaseModel
from PIL import Image
from io import BytesIO
from cryptography.fernet import Fernet, InvalidToken
import base64

app = FastAPI()

# Helper functions

def generate_key(password: str) -> bytes:
    # Derive a Fernet key from the password (simple, for demo; use PBKDF2HMAC for production)
    return base64.urlsafe_b64encode(password.encode('utf-8').ljust(32, b'0'))

def encrypt_message(message: str, key: str) -> bytes:
    f = Fernet(generate_key(key))
    return f.encrypt(message.encode('utf-8'))

def decrypt_message(token: bytes, key: str) -> str:
    f = Fernet(generate_key(key))
    return f.decrypt(token).decode('utf-8')

def hide_message_in_image(image: Image.Image, message: bytes) -> Image.Image:
    # Simple LSB steganography for demonstration
    img = image.convert('RGB')
    data = list(img.getdata())
    message += b'<<END>>'
    bits = ''.join([format(byte, '08b') for byte in message])
    if len(bits) > len(data) * 3:
        raise ValueError('Message too large for image!')
    new_data = []
    bit_idx = 0
    for pixel in data:
        r, g, b = pixel
        if bit_idx < len(bits):
            r = (r & ~1) | int(bits[bit_idx])
            bit_idx += 1
        if bit_idx < len(bits):
            g = (g & ~1) | int(bits[bit_idx])
            bit_idx += 1
        if bit_idx < len(bits):
            b = (b & ~1) | int(bits[bit_idx])
            bit_idx += 1
        new_data.append((r, g, b))
    new_img = Image.new(img.mode, img.size)
    new_img.putdata(new_data)
    return new_img

def extract_message_from_image(image: Image.Image) -> bytes:
    img = image.convert('RGB')
    data = list(img.getdata())
    bits = ''
    for pixel in data:
        for color in pixel:
            bits += str(color & 1)
    bytes_list = [bits[i:i+8] for i in range(0, len(bits), 8)]
    message_bytes = bytearray()
    for byte in bytes_list:
        b = int(byte, 2)
        message_bytes.append(b)
        if message_bytes[-7:] == b'<<END>>':
            return bytes(message_bytes[:-7])
    return bytes(message_bytes)

@app.post('/encode')
async def encode(
    image: UploadFile = File(...),
    message: str = Form(...),
    key: str = Form(...)
):
    try:
        img = Image.open(BytesIO(await image.read()))
        encrypted = encrypt_message(message, key)
        new_img = hide_message_in_image(img, encrypted)
        buf = BytesIO()
        new_img.save(buf, format='PNG')
        buf.seek(0)
        return StreamingResponse(buf, media_type='image/png')
    except Exception as e:
        return JSONResponse(status_code=400, content={'error': str(e)})

@app.post('/decode')
async def decode(
    image: UploadFile = File(...),
    key: str = Form(...)
):
    try:
        img = Image.open(BytesIO(await image.read()))
        hidden = extract_message_from_image(img)
        message = decrypt_message(hidden, key)
        return {'message': message}
    except InvalidToken:
        return JSONResponse(status_code=400, content={'error': 'Invalid key or corrupted image.'})
    except Exception as e:
        return JSONResponse(status_code=400, content={'error': str(e)})
