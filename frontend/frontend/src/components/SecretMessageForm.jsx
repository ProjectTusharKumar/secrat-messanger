import React, { useState } from "react";

export default function SecretMessageForm() {
  const [image, setImage] = useState(null);
  const [message, setMessage] = useState("");
  const [hashKey, setHashKey] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const handleImageChange = (e) => {
    if (e.target.files && e.target.files[0]) {
      setImage(e.target.files[0]);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError("");
    setHashKey("");
    try {
      const formData = new FormData();
      formData.append("image", image);
      formData.append("message", message);
      // TODO: Replace with your backend endpoint
      const res = await fetch("/api/embed", {
        method: "POST",
        body: formData,
      });
      if (!res.ok) throw new Error("Failed to embed message");
      const data = await res.json();
      setHashKey(data.hashKey);
      // Optionally, handle updated image download
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-md mx-auto p-6 bg-white rounded-lg shadow mt-8">
      <h2 className="text-2xl font-bold mb-4 text-center">Secret Message Creator</h2>
      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label className="block font-medium mb-1">Upload Image</label>
          <input
            type="file"
            accept="image/*"
            onChange={handleImageChange}
            className="block w-full text-sm text-gray-700 border border-gray-300 rounded p-2"
            required
          />
        </div>
        <div>
          <label className="block font-medium mb-1">Secret Message</label>
          <textarea
            value={message}
            onChange={(e) => setMessage(e.target.value)}
            className="w-full border border-gray-300 rounded p-2"
            rows={3}
            required
            placeholder="Type your secret message..."
          />
        </div>
        <button
          type="submit"
          className="w-full bg-blue-600 text-white py-2 rounded hover:bg-blue-700 transition"
          disabled={loading}
        >
          {loading ? "Embedding..." : "Create Secret Image"}
        </button>
        {error && <p className="text-red-600 text-sm">{error}</p>}
        {hashKey && (
          <div className="mt-4 p-3 bg-green-100 rounded">
            <p className="font-semibold">Your Hash Key:</p>
            <code className="break-all text-green-700">{hashKey}</code>
            <p className="text-xs mt-2 text-gray-600">Save this key to decrypt your message later.</p>
          </div>
        )}
      </form>
    </div>
  );
}
