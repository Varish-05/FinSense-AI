// ── LoginPage ────────────────────────────────────────────────────────
import React, { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import toast from "react-hot-toast";
import { BrainCircuit } from "lucide-react";

const cls = "w-full bg-slate-800 border border-slate-700 rounded-lg px-3 py-2.5 text-white text-sm focus:outline-none focus:border-primary-500";

export function LoginPage() {
  const { login } = useAuth();
  const navigate = useNavigate();
  const [form, setForm] = useState({ email: "", password: "" });
  const [loading, setLoading] = useState(false);

  const handle = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      await login(form.email, form.password);
      navigate("/dashboard");
    } catch { toast.error("Invalid email or password"); }
    finally { setLoading(false); }
  };

  return (
    <div className="min-h-screen bg-dark-950 flex items-center justify-center p-4">
      <div className="w-full max-w-sm">
        <div className="flex items-center gap-2 justify-center mb-8">
          <BrainCircuit className="text-primary-500" size={32}/>
          <span className="text-white text-2xl font-bold">FinSense <span className="text-primary-500">AI</span></span>
        </div>
        <div className="bg-dark-900 border border-slate-800 rounded-2xl p-6 space-y-4">
          <h1 className="text-white text-xl font-semibold">Sign in</h1>
          <form onSubmit={handle} className="space-y-3">
            <div>
              <label className="text-slate-400 text-xs mb-1 block">Email</label>
              <input className={cls} type="email" value={form.email} onChange={e=>setForm({...form,email:e.target.value})} required placeholder="you@example.com"/>
            </div>
            <div>
              <label className="text-slate-400 text-xs mb-1 block">Password</label>
              <input className={cls} type="password" value={form.password} onChange={e=>setForm({...form,password:e.target.value})} required placeholder="••••••••"/>
            </div>
            <button type="submit" disabled={loading} className="w-full bg-primary-600 hover:bg-primary-500 disabled:opacity-50 text-white rounded-lg py-2.5 font-medium transition-colors">
              {loading ? "Signing in…" : "Sign in"}
            </button>
          </form>
          <p className="text-slate-400 text-sm text-center">
            New here? <Link to="/register" className="text-primary-400 hover:underline">Create account</Link>
          </p>
        </div>
      </div>
    </div>
  );
}

// ── RegisterPage ──────────────────────────────────────────────────────
export function RegisterPage() {
  const { register } = useAuth();
  const navigate = useNavigate();
  const [form, setForm] = useState({ email: "", username: "", full_name: "", password: "" });
  const [loading, setLoading] = useState(false);

  const handle = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      await register(form);
      navigate("/dashboard");
    } catch (err) { toast.error(err.response?.data?.detail || "Registration failed"); }
    finally { setLoading(false); }
  };

  return (
    <div className="min-h-screen bg-dark-950 flex items-center justify-center p-4">
      <div className="w-full max-w-sm">
        <div className="flex items-center gap-2 justify-center mb-8">
          <BrainCircuit className="text-primary-500" size={32}/>
          <span className="text-white text-2xl font-bold">FinSense <span className="text-primary-500">AI</span></span>
        </div>
        <div className="bg-dark-900 border border-slate-800 rounded-2xl p-6 space-y-4">
          <h1 className="text-white text-xl font-semibold">Create account</h1>
          <form onSubmit={handle} className="space-y-3">
            {[["Email","email","email","you@example.com"],["Username","text","username","varish123"],["Full Name","text","full_name","Varish Gada"],["Password","password","password","Min. 8 characters"]].map(([label,type,key,ph])=>(
              <div key={key}>
                <label className="text-slate-400 text-xs mb-1 block">{label}</label>
                <input className={cls} type={type} value={form[key]} onChange={e=>setForm({...form,[key]:e.target.value})} placeholder={ph} required={key!=="full_name"}/>
              </div>
            ))}
            <button type="submit" disabled={loading} className="w-full bg-primary-600 hover:bg-primary-500 disabled:opacity-50 text-white rounded-lg py-2.5 font-medium transition-colors">
              {loading ? "Creating…" : "Create account"}
            </button>
          </form>
          <p className="text-slate-400 text-sm text-center">
            Already have an account? <Link to="/login" className="text-primary-400 hover:underline">Sign in</Link>
          </p>
        </div>
      </div>
    </div>
  );
}
