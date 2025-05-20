import React, { useState, useRef } from "react";

export default function SecretMessageForm() {
  const [image, setImage] = useState(null);
  const [imagePreview, setImagePreview] = useState(null);
  const [message, setMessage] = useState("");
  const [hashKey, setHashKey] = useState("");
  const [algorithm, setAlgorithm] = useState("lsb");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const fileInputRef = useRef();

  const supportedExtensions = {
    lsb: ["png"],
    palette_lsb: ["gif"], // GIF only for palette_lsb
    dct: ["jpg", "jpeg"],
    alpha_lsb: ["png"]
  };

  const checkImageExtension = (file, algo) => {
    if (!file) return true;
    const ext = file.name.split('.').pop().toLowerCase();
    // Palette LSB: only allow GIF
    if (algo === "palette_lsb") {
      return ext === "gif";
    }
    return supportedExtensions[algo]?.includes(ext);
  };

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

  const handleCopyHashKey = () => {
    if (hashKey) navigator.clipboard.writeText(hashKey);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError("");
    setHashKey("");
    if (!checkImageExtension(image, algorithm)) {
      setLoading(false);
      setError("Selected algorithm only supports: " + supportedExtensions[algorithm].join(", ").toUpperCase() + " files.");
      return;
    }
    try {
      const formData = new FormData();
      formData.append("image", image);
      formData.append("message", message);
      formData.append("algorithm", algorithm);
      const res = await fetch("https://secrat-messanger-1.onrender.com/api/embed", {
        method: "POST",
        body: formData,
      });
      if (!res.ok) throw new Error("Failed to embed message");
      const data = await res.json();
      setHashKey(data.hashKey);
      // Download the returned image
      const link = document.createElement("a");
      link.href = `data:${data.contentType};base64,${data.image}`;
      link.download = data.filename || "secret_image.png";
      link.click();
      // Generate shareable link
      const params = new URLSearchParams({
        hashKey: data.hashKey,
        algorithm: algorithm
      });
      window.history.replaceState({}, '', `?${params.toString()}`);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-blue-200 flex flex-col">
      <div className="flex-1 flex flex-col justify-center">
        <div className="max-w-md w-full mx-auto p-6 bg-white/90 rounded-xl shadow-2xl mt-12 mb-8 border border-blue-100">
          <h2 className="text-3xl font-extrabold mb-6 text-center text-blue-700 drop-shadow">Secret Message Creator</h2>
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
              <label className="block font-semibold mb-1 text-blue-700">Secret Message</label>
              <textarea
                value={message}
                onChange={(e) => setMessage(e.target.value)}
                className="w-full border border-blue-200 rounded p-2 focus:ring-2 focus:ring-blue-400"
                rows={3}
                required
                placeholder="Type your secret message..."
              />
            </div>
            <div>
              <label className="block font-semibold mb-1 text-blue-700">Algorithm</label>
              <select
                value={algorithm}
                onChange={e => setAlgorithm(e.target.value)}
                className="w-full border border-blue-200 rounded p-2 focus:ring-2 focus:ring-blue-400"
              >
                <option value="lsb">LSB Only(PNG)</option>
                <option value="palette_lsb">Palette LSB Only (GIF)</option>
                <option value="dct">DCT Only (JPEG)</option>
                <option value="alpha_lsb">Alpha LSB Only (PNG w/ alpha)</option>
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
                  Embedding...
                </span>
              ) : "Create Secret Image"}
            </button>
            {error && <p className="text-red-600 text-sm text-center font-semibold">{error}</p>}
            {hashKey && (
              <div className="mt-4 p-3 bg-green-50 border border-green-200 rounded-lg shadow">
                <p className="font-semibold text-green-700">Your Hash Key:</p>
                <div className="flex items-center space-x-2 mt-1">
                  <code className="break-all text-green-700 text-base">{hashKey}</code>
                  <button
                    type="button"
                    className="ml-2 px-2 py-1 text-xs bg-green-200 rounded hover:bg-green-300 font-semibold"
                    onClick={handleCopyHashKey}
                  >
                    Copy
                  </button>
                </div>
                <p className="text-xs mt-2 text-gray-600">Save this key to decrypt your message later.</p>
                <div className="mt-2">
                  <label className="block text-xs font-semibold text-blue-700 mb-1">Shareable Link:</label>
                  <input
                    type="text"
                    readOnly
                    value={window.location.href}
                    className="w-full border border-blue-200 rounded p-1 text-xs bg-blue-50"
                    onFocus={e => e.target.select()}
                  />
                </div>
              </div>
            )}
          </form>
        </div>
      </div>
      <footer className="text-center text-xs text-blue-500 mb-2">&copy; {new Date().getFullYear()} Secret Messenger</footer>
    </div>
  );
}
