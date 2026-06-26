import React, { useEffect, useState } from "react";
import { budgetsAPI } from "../utils/api";
import toast from "react-hot-toast";
import { Plus, Trash2 } from "lucide-react";

const CATEGORIES = ["Food","Transport","Healthcare","Entertainment","Education","Shopping","Utilities","Investments","Travel","Miscellaneous"];
const THIS_MONTH = new Date().toISOString().slice(0,7);

export default function BudgetsPage() {
  const [budgets, setBudgets] = useState([]);
  const [month, setMonth] = useState(THIS_MONTH);
  const [form, setForm] = useState({ category: "Food", allocated_amount: "" });
  const [adding, setAdding] = useState(false);

  const load = () => budgetsAPI.list(month).then(r => setBudgets(r.data)).catch(() => toast.error("Failed to load"));
  useEffect(() => { load(); }, [month]);

  const handleAdd = async () => {
    if (!form.allocated_amount) return toast.error("Enter an amount");
    setAdding(true);
    try {
      await budgetsAPI.create({ ...form, month, allocated_amount: parseFloat(form.allocated_amount) });
      toast.success("Budget set");
      setForm({ category: "Food", allocated_amount: "" });
      load();
    } catch { toast.error("Failed to save"); }
    finally { setAdding(false); }
  };

  const handleDelete = async (id) => {
    await budgetsAPI.delete(id);
    toast.success("Removed");
    load();
  };

  return (
    <div className="space-y-5 max-w-2xl">
      <div>
        <h1 className="text-2xl font-bold text-white">Budgets</h1>
        <p className="text-slate-400 text-sm">Set monthly spending limits per category</p>
      </div>

      {/* Month selector */}
      <div className="flex items-center gap-3">
        <label className="text-slate-400 text-sm">Month:</label>
        <input type="month" value={month} onChange={e=>setMonth(e.target.value)}
          className="bg-slate-800 border border-slate-700 rounded-lg px-3 py-1.5 text-white text-sm focus:outline-none focus:border-primary-500"/>
      </div>

      {/* Add form */}
      <div className="bg-dark-900 border border-slate-800 rounded-xl p-5 space-y-3">
        <h2 className="text-white font-medium">Add Budget Limit</h2>
        <div className="flex gap-3">
          <select value={form.category} onChange={e=>setForm({...form,category:e.target.value})}
            className="flex-1 bg-slate-800 border border-slate-700 rounded-lg px-3 py-2 text-white text-sm focus:outline-none focus:border-primary-500">
            {CATEGORIES.map(c=><option key={c}>{c}</option>)}
          </select>
          <input type="number" value={form.allocated_amount} onChange={e=>setForm({...form,allocated_amount:e.target.value})}
            placeholder="₹ Amount" className="flex-1 bg-slate-800 border border-slate-700 rounded-lg px-3 py-2 text-white text-sm focus:outline-none focus:border-primary-500"/>
          <button onClick={handleAdd} disabled={adding}
            className="flex items-center gap-2 px-4 py-2 bg-primary-600 hover:bg-primary-500 hover:shadow-[0_0_15px_rgba(139,92,246,0.5)] disabled:opacity-50 text-white rounded-lg text-sm font-medium transition-all duration-300">
            <Plus size={16}/> Add
          </button>
        </div>
      </div>

      {/* Budget list */}
      {budgets.length === 0 ? (
        <p className="text-slate-400 text-sm text-center py-8">No budgets for {month}. Add one above.</p>
      ) : (
        <div className="space-y-2">
          {budgets.map(b => {
            const pct = b.allocated_amount > 0 ? Math.min((b.spent_amount/b.allocated_amount)*100, 100) : 0;
            const color = pct > 90 ? "bg-gradient-to-r from-accent-pink to-red-500 shadow-[0_0_8px_rgba(255,0,127,0.5)]" : pct > 70 ? "bg-gradient-to-r from-yellow-400 to-orange-500 shadow-[0_0_8px_rgba(245,158,11,0.5)]" : "bg-gradient-to-r from-primary-400 to-primary-600 shadow-[0_0_8px_rgba(139,92,246,0.5)]";
            return (
              <div key={b.id} className="bg-dark-900 border border-slate-800 rounded-xl p-4 hover:shadow-lg hover:shadow-primary-500/5 transition-all duration-300">
                <div className="flex items-center justify-between mb-2">
                  <div>
                    <span className="text-white font-medium">{b.category}</span>
                    <span className="text-slate-400 text-sm ml-3">₹{b.spent_amount.toLocaleString()} / ₹{b.allocated_amount.toLocaleString()}</span>
                  </div>
                  <button onClick={() => handleDelete(b.id)} className="text-slate-500 hover:text-red-400 transition-colors"><Trash2 size={15}/></button>
                </div>
                <div className="h-1.5 bg-slate-800 rounded-full overflow-hidden">
                  <div className={`h-full ${color} rounded-full transition-all`} style={{width:`${pct}%`}}/>
                </div>
                <p className="text-xs text-slate-500 mt-1">{pct.toFixed(0)}% used</p>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
