# Secret Messenger Backend

This is the backend for the Secret Messenger steganography web app, built with FastAPI.

## Features
- REST API for embedding and extracting secret messages in images/audio
- Supports LSB, Palette LSB (GIF), DCT (JPEG), Alpha LSB (PNG w/ alpha), and Audio LSB (WAV)
- Rate limiting, security headers, and CORS for secure operation
- Optional HuggingFace API integration for message summarization
- Dockerized for easy deployment

## How It Works
1. **/api/embed:** Accepts an image/audio file, secret message, and algorithm. Returns a stego file with the message embedded.
2. **/api/extract:** Accepts a stego image/audio and hash key. Returns the extracted secret message.

## Getting Started

### Prerequisites
- Python 3.10+
- pip
- (Optional) Docker

### Development
1. Clone the repository:
   ```bash
   git clone <your-fork-or-repo-url>
   cd secrat-messanger/backend
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Start the FastAPI server:
   ```bash
   uvicorn main:app --reload --host 0.0.0.0 --port 8000
   ```
4. The API will be available at `http://localhost:8000`.

### Docker
You can also run the backend in Docker:
```bash
docker build -t secret-messenger-backend .
docker run -p 8000:8000 secret-messenger-backend
```

## Customization & Contribution
- Steganography algorithms are in `other_steg_algorithms.py`.
- To add new algorithms, implement them and update the `/api/embed` and `/api/extract` endpoints in `main.py`.
- PRs and feature suggestions are welcome!

## Folder Structure
- `main.py` — FastAPI app and endpoints
- `other_steg_algorithms.py` — Steganography algorithms
- `requirements.txt` — Python dependencies

## License
MIT
