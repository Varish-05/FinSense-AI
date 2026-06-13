import React, { useEffect, useState, useRef } from "react";
import { expensesAPI } from "../utils/api";
import toast from "react-hot-toast";
import { Plus, Trash2, Upload, Edit3 } from "lucide-react";

const CATEGORIES = ["Food","Transport","Healthcare","Entertainment","Education","Shopping","Utilities","Investments","Travel","Miscellaneous"];
const PAYMENT_MODES = ["UPI","Credit Card","Debit Card","Cash","Net Banking","Wallet"];

const EMPTY_FORM = { amount: "", date: new Date().toISOString().slice(0,10), merchant_name: "", description: "", payment_mode: "UPI", category: "", notes: "" };

function Modal({ title, onClose, children }) {
  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 p-4">
      <div className="bg-dark-900 border border-slate-700 rounded-2xl w-full max-w-lg p-6 space-y-4">
        <div className="flex items-center justify-between">
          <h2 className="text-white font-semibold text-lg">{title}</h2>
          <button onClick={onClose} className="text-slate-400 hover:text-white">✕</button>
        </div>
        {children}
      </div>
    </div>
  );
}

function Field({ label, children }) {
  return <div><label className="text-slate-400 text-xs mb-1 block">{label}</label>{children}</div>;
}

const inputCls = "w-full bg-slate-800 border border-slate-700 rounded-lg px-3 py-2 text-white text-sm focus:outline-none focus:border-primary-500";

export default function ExpensesPage() {
  const [expenses, setExpenses] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showModal, setShowModal] = useState(false);
  const [editTarget, setEditTarget] = useState(null);
  const [form, setForm] = useState(EMPTY_FORM);
  const [saving, setSaving] = useState(false);
  const fileRef = useRef();

  const load = () => {
    expensesAPI.list({ limit: 100 })
      .then(r => setExpenses(r.data))
      .catch(() => toast.error("Failed to load expenses"))
      .finally(() => setLoading(false));
  };

  useEffect(load, []);

  const openAdd = () => { setEditTarget(null); setForm(EMPTY_FORM); setShowModal(true); };
  const openEdit = (e) => {
    setEditTarget(e);
    setForm({ amount: e.amount, date: e.date, merchant_name: e.merchant_name, description: e.description||"", payment_mode: e.payment_mode, category: e.category, notes: e.notes||"" });
    setShowModal(true);
  };

  const handleSubmit = async () => {
    if (!form.amount || !form.date || !form.merchant_name) return toast.error("Amount, date and merchant are required.");
    setSaving(true);
    try {
      if (editTarget) {
        await expensesAPI.update(editTarget.id, form);
        toast.success("Expense updated");
      } else {
        await expensesAPI.create(form);
        toast.success("Expense added");
      }
      setShowModal(false);
      load();
    } catch { toast.error("Failed to save"); }
    finally { setSaving(false); }
  };

  const handleDelete = async (id) => {
    if (!window.confirm("Delete this expense?")) return;
    await expensesAPI.delete(id);
    toast.success("Deleted");
    load();
  };

  const handleCSV = async (e) => {
    const file = e.target.files[0];
    if (!file) return;
    const t = toast.loading("Uploading CSV…");
    try {
      const r = await expensesAPI.uploadCSV(file);
      toast.success(`Imported ${r.data.length} transactions`, { id: t });
      load();
    } catch { toast.error("CSV import failed", { id: t }); }
    e.target.value = "";
  };

  return (
    <div className="space-y-5">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-white">Expenses</h1>
          <p className="text-slate-400 text-sm">{expenses.length} transactions</p>
        </div>
        <div className="flex gap-2">
          <button onClick={() => fileRef.current.click()} className="flex items-center gap-2 px-3 py-2 rounded-lg border border-slate-700 text-slate-300 hover:border-primary-500 hover:text-primary-400 text-sm transition-colors">
            <Upload size={16}/> CSV
          </button>
          <input ref={fileRef} type="file" accept=".csv" className="hidden" onChange={handleCSV}/>
          <button onClick={openAdd} className="flex items-center gap-2 px-4 py-2 bg-primary-600 hover:bg-primary-500 text-white rounded-lg text-sm font-medium transition-colors">
            <Plus size={16}/> Add Expense
          </button>
        </div>
      </div>

      {loading ? (
        <p className="text-slate-400 text-center py-12">Loading…</p>
      ) : expenses.length === 0 ? (
        <div className="text-center py-16 border border-dashed border-slate-700 rounded-xl">
          <p className="text-slate-400 mb-2">No expenses yet.</p>
          <button onClick={openAdd} className="text-primary-400 hover:underline text-sm">Add your first expense</button>
        </div>
      ) : (
        <div className="bg-dark-900 border border-slate-800 rounded-xl overflow-hidden">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-slate-800">
                {["Date","Merchant","Category","Amount","Mode",""].map(h => (
                  <th key={h} className="text-left text-slate-400 font-medium px-4 py-3 text-xs">{h}</th>
                ))}
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/50">
              {expenses.map(e => (
                <tr key={e.id} className="hover:bg-slate-800/30 transition-colors">
                  <td className="px-4 py-3 text-slate-300">{e.date}</td>
                  <td className="px-4 py-3 text-white font-medium">{e.merchant_name}</td>
                  <td className="px-4 py-3">
                    <span className="px-2 py-0.5 bg-primary-500/10 text-primary-400 rounded text-xs">{e.category}</span>
                  </td>
                  <td className="px-4 py-3 text-white">₹{e.amount.toLocaleString("en-IN")}</td>
                  <td className="px-4 py-3 text-slate-400">{e.payment_mode}</td>
                  <td className="px-4 py-3">
                    <div className="flex gap-2">
                      <button onClick={() => openEdit(e)} className="text-slate-400 hover:text-white"><Edit3 size={15}/></button>
                      <button onClick={() => handleDelete(e.id)} className="text-slate-400 hover:text-red-400"><Trash2 size={15}/></button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {showModal && (
        <Modal title={editTarget ? "Edit Expense" : "Add Expense"} onClose={() => setShowModal(false)}>
          <div className="grid grid-cols-2 gap-3">
            <Field label="Amount (₹)">
              <input className={inputCls} type="number" value={form.amount} onChange={e => setForm({...form, amount: e.target.value})} placeholder="500"/>
            </Field>
            <Field label="Date">
              <input className={inputCls} type="date" value={form.date} onChange={e => setForm({...form, date: e.target.value})}/>
            </Field>
            <Field label="Merchant Name">
              <input className={inputCls} value={form.merchant_name} onChange={e => setForm({...form, merchant_name: e.target.value})} placeholder="Swiggy, Amazon…"/>
            </Field>
            <Field label="Category (auto if blank)">
              <select className={inputCls} value={form.category} onChange={e => setForm({...form, category: e.target.value})}>
                <option value="">Auto-detect</option>
                {CATEGORIES.map(c => <option key={c}>{c}</option>)}
              </select>
            </Field>
            <Field label="Payment Mode">
              <select className={inputCls} value={form.payment_mode} onChange={e => setForm({...form, payment_mode: e.target.value})}>
                {PAYMENT_MODES.map(m => <option key={m}>{m}</option>)}
              </select>
            </Field>
            <Field label="Description">
              <input className={inputCls} value={form.description} onChange={e => setForm({...form, description: e.target.value})} placeholder="Optional details"/>
            </Field>
          </div>
          <Field label="Notes">
            <textarea className={`${inputCls} resize-none`} rows={2} value={form.notes} onChange={e => setForm({...form, notes: e.target.value})}/>
          </Field>
          <button
            onClick={handleSubmit}
            disabled={saving}
            className="w-full bg-primary-600 hover:bg-primary-500 disabled:opacity-50 text-white rounded-lg py-2.5 font-medium transition-colors"
          >
            {saving ? "Saving…" : editTarget ? "Update Expense" : "Add Expense"}
          </button>
        </Modal>
      )}
    </div>
  );
}
