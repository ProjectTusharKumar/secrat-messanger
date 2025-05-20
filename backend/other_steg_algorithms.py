# Additional Steganography Algorithms (not currently used in your app)

# This file provides Python code examples for other steganography algorithms you can integrate.
# These are for educational/demo purposes and are not as secure as your current approach.

from PIL import Image
import numpy as np

# --------- 1. Simple Palette LSB (for GIF/8-bit PNG) ---------
def palette_lsb_hide(image_path, message, output_path):
    img = Image.open(image_path)
    if img.mode != 'P':
        raise ValueError('Image must be palette-based (mode P)')
    data = np.array(img)
    msg_bits = ''.join(f'{ord(c):08b}' for c in message) + '00000000'  # Null-terminate
    flat = data.flatten()
    if len(msg_bits) > len(flat):
        raise ValueError('Message too long to hide in palette image.')
    for i, bit in enumerate(msg_bits):
        # Ensure result is in uint8 range
        flat[i] = np.uint8((int(flat[i]) & ~1) | int(bit))
    data = flat.reshape(data.shape)
    out = Image.fromarray(data, 'P')
    out.putpalette(img.getpalette())
    out.save(output_path)

def palette_lsb_reveal(image_path):
    img = Image.open(image_path)
    data = np.array(img).flatten()
    bits = [str(data[i] & 1) for i in range(0, len(data), 1)]
    chars = [chr(int(''.join(bits[i:i+8]), 2)) for i in range(0, len(bits), 8)]
    msg = ''.join(chars).split('\x00')[0]
    return msg

# --------- 2. DCT (JPEG) Steganography (using cv2) ---------
# Requires: pip install opencv-python
import cv2

def dct_hide(image_path, message, output_path):
    img = cv2.imread(image_path, cv2.IMREAD_COLOR)
    if img is None:
        raise ValueError('Image not found or not readable')
    msg = message + chr(0)  # Null-terminate
    msg_bits = ''.join(f'{ord(c):08b}' for c in msg)
    h, w, _ = img.shape
    # Ensure both height and width are multiples of 8 for DCT
    h8, w8 = h - (h % 8), w - (w % 8)
    img = img[:h8, :w8, :]
    idx = 0
    for row in range(0, h8, 8):
        for col in range(0, w8, 8):
            if idx >= len(msg_bits):
                break
            block = img[row:row+8, col:col+8, 0].astype(float)
            dct = cv2.dct(block)
            # Fix: ensure dct[7, 7] is rounded and cast to int before bitwise ops
            dct77 = int(round(dct[7, 7]))
            dct77 = (dct77 & ~1) | int(msg_bits[idx])
            dct[7, 7] = float(dct77)
            img[row:row+8, col:col+8, 0] = cv2.idct(dct)
            idx += 1
    cv2.imwrite(output_path, img)

def dct_reveal(image_path):
    img = cv2.imread(image_path, cv2.IMREAD_COLOR)
    h, w, _ = img.shape
    h8, w8 = h - (h % 8), w - (w % 8)
    img = img[:h8, :w8, :]
    bits = []
    for row in range(0, h8, 8):
        for col in range(0, w8, 8):
            block = img[row:row+8, col:col+8, 0].astype(float)
            dct = cv2.dct(block)
            dct77 = int(round(dct[7, 7]))
            bits.append(str(dct77 & 1))
    chars = [chr(int(''.join(bits[i:i+8]), 2)) for i in range(0, len(bits), 8)]
    msg = ''.join(chars).split('\x00')[0]
    return msg

# --------- 3. Alpha Channel LSB (for PNG with transparency) ---------
def alpha_lsb_hide(image_path, message, output_path):
    img = Image.open(image_path).convert('RGBA')
    data = np.array(img)
    msg_bits = ''.join(f'{ord(c):08b}' for c in message) + '00000000'
    flat = data[..., 3].flatten()
    if len(msg_bits) > len(flat):
        raise ValueError('Message too long to hide in alpha channel of this image.')
    for i, bit in enumerate(msg_bits):
        # Ensure result is in uint8 range
        flat[i] = np.uint8((int(flat[i]) & ~1) | int(bit))
    data[..., 3] = flat.reshape(data[..., 3].shape)
    out = Image.fromarray(data, 'RGBA')
    out.save(output_path)

def alpha_lsb_reveal(image_path):
    img = Image.open(image_path).convert('RGBA')
    data = np.array(img)[..., 3].flatten()
    bits = [str(data[i] & 1) for i in range(0, len(data), 1)]
    chars = [chr(int(''.join(bits[i:i+8]), 2)) for i in range(0, len(bits), 8)]
    msg = ''.join(chars).split('\x00')[0]
    return msg

# --------- 4. Audio LSB (for WAV files) ---------
import wave

def audio_lsb_hide(wav_in, message, wav_out):
    with wave.open(wav_in, 'rb') as w:
        params = w.getparams()
        frames = bytearray(w.readframes(w.getnframes()))
    msg_bits = ''.join(f'{ord(c):08b}' for c in message) + '00000000'
    for i, bit in enumerate(msg_bits):
        frames[i] = (frames[i] & ~1) | int(bit)
    with wave.open(wav_out, 'wb') as w:
        w.setparams(params)
        w.writeframes(frames)

def audio_lsb_reveal(wav_in):
    with wave.open(wav_in, 'rb') as w:
        frames = bytearray(w.readframes(w.getnframes()))
    bits = [str(frames[i] & 1) for i in range(len(frames))]
    chars = [chr(int(''.join(bits[i:i+8]), 2)) for i in range(0, len(bits), 8)]
    msg = ''.join(chars).split('\x00')[0]
    return msg

# --------- End of file ---------
