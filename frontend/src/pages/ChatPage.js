import React, { useState, useRef, useEffect } from "react";
import { analyticsAPI } from "../utils/api";
import { Send, BrainCircuit } from "lucide-react";

const SUGGESTIONS = [
  "How much did I spend on food last month?",
  "Which category is growing the fastest?",
  "Give me tips to reduce my expenses.",
  "What is my biggest expense this month?",
];

export default function ChatPage() {
  const [messages, setMessages] = useState([
    { role: "assistant", text: "Hi! I'm your FinSense AI assistant. Ask me anything about your spending, budget, or savings." }
  ]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const bottomRef = useRef();

  useEffect(() => { bottomRef.current?.scrollIntoView({ behavior: "smooth" }); }, [messages]);

  const send = async (text) => {
    const msg = text || input.trim();
    if (!msg) return;
    setInput("");
    setMessages(m => [...m, { role: "user", text: msg }]);
    setLoading(true);
    try {
      const res = await analyticsAPI.chat(msg);
      setMessages(m => [...m, { role: "assistant", text: res.data.reply }]);
    } catch {
      setMessages(m => [...m, { role: "assistant", text: "Sorry, I couldn't process that. Please try again." }]);
    }
    setLoading(false);
  };

  return (
    <div className="flex flex-col h-full max-h-[calc(100vh-7rem)]">
      <div className="mb-4">
        <h1 className="text-2xl font-bold text-white">AI Finance Assistant</h1>
        <p className="text-slate-400 text-sm">Ask anything about your spending and financial health</p>
      </div>

      {/* Conversation */}
      <div className="flex-1 overflow-y-auto space-y-4 pr-1 mb-4">
        {messages.map((m, i) => (
          <div key={i} className={`flex ${m.role === "user" ? "justify-end" : "justify-start"}`}>
            {m.role === "assistant" && (
              <div className="w-8 h-8 rounded-full bg-primary-500/15 flex items-center justify-center mr-2 flex-shrink-0 mt-0.5">
                <BrainCircuit size={16} className="text-primary-400"/>
              </div>
            )}
            <div className={`max-w-[75%] px-4 py-3 rounded-2xl text-sm leading-relaxed ${
              m.role === "user"
                ? "bg-primary-600 text-white rounded-tr-sm"
                : "bg-dark-900 border border-slate-800 text-slate-200 rounded-tl-sm"
            }`}>
              {m.text}
            </div>
          </div>
        ))}
        {loading && (
          <div className="flex justify-start">
            <div className="w-8 h-8 rounded-full bg-primary-500/15 flex items-center justify-center mr-2 flex-shrink-0">
              <BrainCircuit size={16} className="text-primary-400"/>
            </div>
            <div className="bg-dark-900 border border-slate-800 rounded-2xl rounded-tl-sm px-4 py-3">
              <div className="flex gap-1.5">
                <span className="w-2 h-2 bg-primary-400 rounded-full animate-bounce" style={{animationDelay:"0ms"}}/>
                <span className="w-2 h-2 bg-primary-400 rounded-full animate-bounce" style={{animationDelay:"150ms"}}/>
                <span className="w-2 h-2 bg-primary-400 rounded-full animate-bounce" style={{animationDelay:"300ms"}}/>
              </div>
            </div>
          </div>
        )}
        <div ref={bottomRef}/>
      </div>

      {/* Suggestions */}
      {messages.length === 1 && (
        <div className="grid grid-cols-2 gap-2 mb-4">
          {SUGGESTIONS.map(s => (
            <button
              key={s}
              onClick={() => send(s)}
              className="text-left text-xs text-slate-300 bg-dark-900 border border-slate-800 hover:border-primary-500/50 rounded-xl p-3 transition-colors"
            >
              {s}
            </button>
          ))}
        </div>
      )}

      {/* Input */}
      <div className="flex gap-2">
        <input
          value={input}
          onChange={e => setInput(e.target.value)}
          onKeyDown={e => e.key === "Enter" && !e.shiftKey && send()}
          placeholder="Ask about your finances…"
          className="flex-1 bg-dark-900 border border-slate-700 focus:border-primary-500 rounded-xl px-4 py-3 text-white text-sm outline-none transition-colors"
        />
        <button
          onClick={() => send()}
          disabled={!input.trim() || loading}
          className="bg-primary-600 hover:bg-primary-500 disabled:opacity-40 text-white rounded-xl px-4 transition-colors"
        >
          <Send size={18}/>
        </button>
      </div>
    </div>
  );
}
