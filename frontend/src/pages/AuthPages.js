// ── LoginPage ────────────────────────────────────────────────────────
import React, { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import toast from "react-hot-toast";
import { BrainCircuit } from "lucide-react";

const cls = "w-full bg-slate-800 border border-slate-700 rounded-lg px-3 py-2.5 text-white text-sm focus:outline-none focus:border-primary-500";

// FastAPI sometimes returns `detail` as a string, and sometimes as an array of
// validation error objects like [{type, loc, msg, input, ctx}]. Passing that
// object straight to a toast crashes React ("Objects are not valid as a React
// child"). This helper always returns a safe, human-readable string.
function getErrorMessage(err, fallback) {
  const detail = err?.response?.data?.detail;
  if (!detail) return fallback;
  if (typeof detail === "string") return detail;
  if (Array.isArray(detail)) {
    return detail.map(d => d.msg || JSON.stringify(d)).join(", ");
  }
  if (typeof detail === "object") return detail.msg || JSON.stringify(detail);
  return fallback;
}

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
    } catch (err) { toast.error(getErrorMessage(err, "Invalid email or password")); }
    finally { setLoading(false); }
  };

  return (
    <div className="min-h-screen bg-dark-950 flex items-center justify-center p-4 relative overflow-hidden">
      <div className="absolute top-[20%] left-[20%] w-[300px] h-[300px] rounded-full bg-primary-500/15 blur-[80px] pointer-events-none animate-pulse-slow" />
      <div className="absolute bottom-[20%] right-[20%] w-[250px] h-[250px] rounded-full bg-accent-cyan/10 blur-[80px] pointer-events-none" />
      
      <div className="w-full max-w-sm relative z-10 animate-float">
        <div className="flex flex-col items-center gap-2 justify-center mb-8">
          <BrainCircuit className="text-primary-400 animate-pulse" size={40}/>
          <span className="bg-gradient-to-r from-primary-400 via-accent-purple to-accent-cyan bg-clip-text text-transparent font-extrabold text-3xl tracking-tight neon-title">FinSense AI</span>
        </div>
        <div className="bg-dark-900 border border-slate-800 rounded-2xl p-6 space-y-4 shadow-2xl backdrop-blur-xl">
          <h1 className="text-white text-xl font-semibold tracking-tight">Sign in</h1>
          <form onSubmit={handle} className="space-y-3">
            <div>
              <label className="text-slate-400 text-xs mb-1 block">Email</label>
              <input className={cls} type="email" value={form.email} onChange={e=>setForm({...form,email:e.target.value})} required placeholder="you@example.com"/>
            </div>
            <div>
              <label className="text-slate-400 text-xs mb-1 block">Password</label>
              <input className={cls} type="password" value={form.password} onChange={e=>setForm({...form,password:e.target.value})} required placeholder="••••••••"/>
            </div>
            <button type="submit" disabled={loading} className="w-full bg-primary-600 hover:bg-primary-500 hover:shadow-[0_0_15px_rgba(139,92,246,0.5)] disabled:opacity-50 text-white rounded-lg py-2.5 font-medium transition-all duration-300">
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
    } catch (err) { toast.error(getErrorMessage(err, "Registration failed")); }
    finally { setLoading(false); }
  };

  return (
    <div className="min-h-screen bg-dark-950 flex items-center justify-center p-4 relative overflow-hidden">
      <div className="absolute top-[20%] left-[20%] w-[300px] h-[300px] rounded-full bg-primary-500/15 blur-[80px] pointer-events-none animate-pulse-slow" />
      <div className="absolute bottom-[20%] right-[20%] w-[250px] h-[250px] rounded-full bg-accent-cyan/10 blur-[80px] pointer-events-none" />

      <div className="w-full max-w-sm relative z-10 animate-float">
        <div className="flex flex-col items-center gap-2 justify-center mb-8">
          <BrainCircuit className="text-primary-400 animate-pulse" size={40}/>
          <span className="bg-gradient-to-r from-primary-400 via-accent-purple to-accent-cyan bg-clip-text text-transparent font-extrabold text-3xl tracking-tight neon-title">FinSense AI</span>
        </div>
        <div className="bg-dark-900 border border-slate-800 rounded-2xl p-6 space-y-4 shadow-2xl backdrop-blur-xl">
          <h1 className="text-white text-xl font-semibold tracking-tight">Create account</h1>
          <form onSubmit={handle} className="space-y-3">
            {[["Email","email","email","you@example.com"],["Username","text","username","varish123"],["Full Name","text","full_name","Varish Gada"],["Password","password","password","Min. 8 characters"]].map(([label,type,key,ph])=>(
              <div key={key}>
                <label className="text-slate-400 text-xs mb-1 block">{label}</label>
                <input className={cls} type={type} value={form[key]} onChange={e=>setForm({...form,[key]:e.target.value})} placeholder={ph} required={key!=="full_name"}/>
              </div>
            ))}
            <button type="submit" disabled={loading} className="w-full bg-primary-600 hover:bg-primary-500 hover:shadow-[0_0_15px_rgba(139,92,246,0.5)] disabled:opacity-50 text-white rounded-lg py-2.5 font-medium transition-all duration-300">
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
