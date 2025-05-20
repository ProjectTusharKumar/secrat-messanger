# Secret Messenger Frontend

This is the frontend for the Secret Messenger steganography web app, built with React and Tailwind CSS.

## Features
- Modern, responsive UI for embedding and extracting secret messages in images/audio
- Supports multiple steganography algorithms: LSB, Palette LSB (GIF), DCT (JPEG), Alpha LSB (PNG w/ alpha)
- Drag-and-drop file upload, algorithm selection, and clear user feedback
- Dockerized for easy deployment

## How It Works
1. **Encryption:** Upload an image, select an algorithm, enter your secret message, and the app will embed the message using the chosen steganography method.
2. **Decryption:** Upload a stego image and provide the hash key to extract the hidden message.

## Getting Started

### Prerequisites
- Node.js (v18+ recommended)
- npm or yarn

### Development
1. Clone the repository:
   ```bash
   git clone <your-fork-or-repo-url>
   cd secrat-messanger/frontend
   ```
2. Install dependencies:
   ```bash
   npm install
   # or
   yarn install
   ```
3. Start the development server:
   ```bash
   npm run dev
   # or
   yarn dev
   ```
4. The app will be available at `http://localhost:5173` (or as configured).

### Docker
You can also run the frontend in Docker:
```bash
docker build -t secret-messenger-frontend .
docker run -p 5173:5173 secret-messenger-frontend
```

## Customization & Contribution
- The UI is built with React components in `src/components/`.
- To add new features or algorithms, update the forms and logic in the relevant components.
- PRs and feature suggestions are welcome!

## Folder Structure
- `src/components/` — React components for forms and UI
- `src/App.jsx` — Main app logic and navigation
- `public/` — Static assets

## License
MIT
