import React, { useState } from "react";
import SecretMessageForm from "./components/SecretMessageForm";
import DecryptMessageForm from "./components/DecryptMessageForm";
import './App.css'

const NAV = [
  { label: "Encryption", view: "encrypt" },
  { label: "Decryption", view: "decrypt" },
];

export default function App() {
  const [view, setView] = useState("encrypt");

  return (
    <div id="app-root" className="min-h-screen bg-gray-100">
      <header>
        <nav className="bg-blue-700 text-white px-4 py-3 flex justify-center space-x-6 shadow">
          {NAV.map((item) => (
            <a
              key={item.view}
              href="#"
              className={`font-semibold px-3 py-1 rounded ${view === item.view ? "bg-blue-900" : "hover:bg-blue-800"}`}
              onClick={e => {
                e.preventDefault();
                setView(item.view);
              }}
            >
              {item.label}
            </a>
          ))}
        </nav>
      </header>
      <main className="py-8">
        {view === "encrypt" ? <SecretMessageForm /> : <DecryptMessageForm />}
      </main>
    </div>
  );
}
