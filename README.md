# Secret Messenger

Secret Messenger is a secure, full-stack steganography web application that allows users to embed and extract secret messages in images and audio files using multiple advanced steganography algorithms. The project features a modern React + Tailwind frontend and a FastAPI backend, with robust security, rate limiting, and optional AI-powered message summarization.

## Features
- **Multiple Steganography Algorithms:**
  - LSB (Least Significant Bit) for PNG
  - Palette LSB (GIF only)
  - DCT (JPEG only)
  - Alpha LSB (PNG with alpha channel)
  - Audio LSB (WAV)
- **Modern UI/UX:** Responsive, drag-and-drop upload, clear feedback, and algorithm selection.
- **Security:** Rate limiting, CORS, security headers, and encrypted message storage.
- **AI Integration:** Optional HuggingFace summarization for long messages.
- **Dockerized:** Easy deployment for both frontend and backend.

## How It Works
1. **Encryption:**
   - Upload an image or audio file.
   - Select the steganography algorithm.
   - Enter your secret message (optionally summarize with AI).
   - Download the stego file and save the hash key for decryption.
2. **Decryption:**
   - Upload the stego file and provide the hash key.
   - The app extracts and decrypts the hidden message.

## Project Structure
```
repo-root/
  ├── backend/    # FastAPI backend (API, algorithms, security)
  ├── frontend/   # React + Tailwind frontend (UI/UX)
  ├── docker-compose.yml
  └── README.md   # (this file)
```

## Getting Started

### Prerequisites
- Docker (recommended)
- Or: Python 3.10+, Node.js 18+

### Quick Start (Docker Compose)
1. Clone the repository:
   ```bash
   git clone <your-fork-or-repo-url>
   cd secrat-messanger
   ```
2. Start both frontend and backend:
   ```bash
   docker-compose up --build
   ```
3. Access the app at the URL shown in the output (typically `http://localhost:5173`).

### Manual Start (Dev Mode)
- **Backend:**
  ```bash
  cd backend
  pip install -r requirements.txt
  uvicorn main:app --reload --host 0.0.0.0 --port 8000
  ```
- **Frontend:**
  ```bash
  cd frontend
  npm install
  npm run dev
  ```

## Adding Features & Contributing
- **Frontend:** Add new algorithms or UI features in `frontend/src/components/`.
- **Backend:** Implement new algorithms in `backend/other_steg_algorithms.py` and update endpoints in `backend/main.py`.
- **PRs and issues are welcome!**

## Security & Limitations
- Only compatible file types are accepted for each algorithm (e.g., GIF for palette LSB, JPEG for DCT).
- All user input is validated and rate-limited.
- No user authentication or message history is stored in the current version.

## License
MIT

---

For more details, see the `README.md` files in the `frontend/` and `backend/` folders.