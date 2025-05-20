import React, { useState, useRef } from "react";

export default function DecryptMessageForm() {
  const [image, setImage] = useState(null);
  const [imagePreview, setImagePreview] = useState(null);
  const [algorithm, setAlgorithm] = useState(() => {
    const params = new URLSearchParams(window.location.search);
    return params.get('algorithm') || 'lsb';
  });
  const [hashKey, setHashKey] = useState(() => {
    const params = new URLSearchParams(window.location.search);
    return params.get('hashKey') || '';
  });
  const [message, setMessage] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const fileInputRef = useRef();

  const handleImageChange = (e) => {
    const file = e.target.files && e.target.files[0];
    if (file) {
      setImage(file);
      setImagePreview(URL.createObjectURL(file));
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    const file = e.dataTransfer.files && e.dataTransfer.files[0];
    if (file) {
      setImage(file);
      setImagePreview(URL.createObjectURL(file));
    }
  };

  const handleDragOver = (e) => {
    e.preventDefault();
  };

  const handleCopyMessage = () => {
    if (message) navigator.clipboard.writeText(message);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError("");
    setMessage(null);
    try {
      const formData = new FormData();
      formData.append("image", image);
      formData.append("hash_key", hashKey);
      formData.append("algorithm", algorithm);
      const res = await fetch("https://animated-enigma-q7vvqxgvwg66hgv4-8000.app.github.dev/api/extract", {
        method: "POST",
        body: formData,
      });
      if (!res.ok) {
        const data = await res.json();
        if (res.status === 404 && res.status === 500 && data.detail === "No hidden message found or Hash key is incorrect or select the correct Algorithm.") {
          setError("No hidden message detected in the file.");
        } else {
          setError(data.detail || "No hidden message found..");
        }
        setLoading(false);
        return;
      }
      const data = await res.json();
      setMessage(data.message);
    } catch (err) {
      setError("Failed to extract message.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-50 to-blue-200">
      <div className="w-full flex flex-col items-center justify-center">
        <div className="max-w-md w-full mx-auto p-6 bg-white/90 rounded-xl shadow-2xl border border-blue-100">
          <h2 className="text-3xl font-extrabold mb-6 text-center text-blue-700 drop-shadow">Secret Message Decryptor</h2>
          <form onSubmit={handleSubmit} className="space-y-5">
            <div
              className="border-2 border-dashed border-blue-300 rounded-lg p-4 text-center cursor-pointer bg-blue-50 hover:bg-blue-100 transition"
              onDrop={handleDrop}
              onDragOver={handleDragOver}
              onClick={() => fileInputRef.current.click()}
            >
              <input
                type="file"
                accept="image/*"
                onChange={handleImageChange}
                className="hidden"
                ref={fileInputRef}
                required
              />
              {imagePreview ? (
                <img src={imagePreview} alt="Preview" className="mx-auto max-h-40 rounded shadow" />
              ) : (
                <span className="text-blue-400 font-medium">Drag & drop or click to select an image</span>
              )}
            </div>
            <div>
              <label className="block font-semibold mb-1 text-blue-700">Hash Key</label>
              <input
                type="text"
                value={hashKey}
                onChange={(e) => setHashKey(e.target.value)}
                className="w-full border border-blue-200 rounded p-2 focus:ring-2 focus:ring-blue-400"
                required
                placeholder="Enter your hash key..."
              />
            </div>
            <div>
              <label className="block font-semibold mb-1 text-blue-700">Algorithm</label>
              <select
                value={algorithm}
                onChange={e => setAlgorithm(e.target.value)}
                className="w-full border border-blue-200 rounded p-2 focus:ring-2 focus:ring-blue-400"
              >
                <option value="lsb">LSB (PNG)</option>
                <option value="palette_lsb">Palette LSB (GIF/8-bit PNG)</option>
                <option value="dct">DCT (JPEG)</option>
                <option value="alpha_lsb">Alpha LSB (PNG w/ alpha)</option>
                {/* <option value="audio_lsb">Audio LSB (WAV)</option> */}
              </select>
            </div>
            <button
              type="submit"
              className="w-full bg-gradient-to-r from-blue-600 to-blue-500 text-white py-2 rounded-lg font-bold shadow hover:from-blue-700 hover:to-blue-600 transition"
              disabled={loading}
            >
              {loading ? (
                <span className="flex items-center justify-center">
                  <svg className="animate-spin h-5 w-5 mr-2 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8z"></path>
                  </svg>
                  Decrypting...
                </span>
              ) : "Decrypt Message"}
            </button>
            {error && <p className="text-red-600 text-sm text-center font-semibold">{error}</p>}
            {message && (
              <div className="mt-4 p-3 bg-green-50 border border-green-200 rounded-lg shadow">
                <p className="font-semibold text-green-700">Decrypted Message:</p>
                <div className="flex items-center space-x-2 mt-1">
                  <code className="break-all text-green-700 text-base">{message}</code>
                  <button
                    type="button"
                    className="ml-2 px-2 py-1 text-xs bg-green-200 rounded hover:bg-green-300 font-semibold"
                    onClick={handleCopyMessage}
                  >
                    Copy
                  </button>
                </div>
              </div>
            )}
          </form>
        </div>
        <footer className="text-center text-xs text-blue-500 mt-4">&copy; {new Date().getFullYear()} Secret Messenger</footer>
      </div>
    </div>
  );
}
