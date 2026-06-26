import React, { useState } from "react";
import { analyticsAPI } from "../utils/api";
import { Line } from "react-chartjs-2";
import { Chart as ChartJS, CategoryScale, LinearScale, PointElement, LineElement, Tooltip, Legend, Filler } from "chart.js";
import toast from "react-hot-toast";

ChartJS.register(CategoryScale, LinearScale, PointElement, LineElement, Tooltip, Legend, Filler);

const CATEGORIES = ["(All)","Food","Transport","Healthcare","Entertainment","Education","Shopping","Utilities","Investments","Travel","Miscellaneous"];

export default function ForecastPage() {
  const [category, setCategory] = useState("(All)");
  const [periods, setPeriods] = useState(3);
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(false);

  const run = async () => {
    setLoading(true);
    try {
      const res = await analyticsAPI.forecast({
        category: category === "(All)" ? undefined : category,
        periods,
      });
      setData(res.data);
    } catch { toast.error("Forecast failed – not enough data yet."); }
    finally { setLoading(false); }
  };

  const chartData = data && data.forecast.length > 0 ? {
    labels: data.forecast.map(d => d.ds),
    datasets: [
      {
        label: "Predicted Spending (₹)",
        data: data.forecast.map(d => d.yhat),
        borderColor: "#00f2fe",
        backgroundColor: "rgba(0,242,254,0.08)",
        fill: true,
        tension: 0.4,
        pointRadius: 5,
        pointBackgroundColor: "#00f2fe",
      },
      {
        label: "Upper Bound",
        data: data.forecast.map(d => d.yhat_upper),
        borderColor: "#94a3b8",
        borderDash: [4,4],
        fill: false,
        tension: 0.4,
        pointRadius: 0,
      },
      {
        label: "Lower Bound",
        data: data.forecast.map(d => d.yhat_lower),
        borderColor: "#94a3b8",
        borderDash: [4,4],
        fill: false,
        tension: 0.4,
        pointRadius: 0,
      },
    ],
  } : null;

  return (
    <div className="space-y-5 max-w-3xl">
      <div>
        <h1 className="text-2xl font-bold text-white">Expense Forecast</h1>
        <p className="text-slate-400 text-sm">Predict future spending using Facebook Prophet</p>
      </div>

      <div className="bg-dark-900 border border-slate-800 rounded-xl p-5 space-y-4">
        <div className="flex flex-wrap gap-4">
          <div>
            <label className="text-slate-400 text-xs mb-1 block">Category</label>
            <select value={category} onChange={e=>setCategory(e.target.value)}
              className="bg-slate-800 border border-slate-700 rounded-lg px-3 py-2 text-white text-sm focus:outline-none focus:border-primary-500">
              {CATEGORIES.map(c=><option key={c}>{c}</option>)}
            </select>
          </div>
          <div>
            <label className="text-slate-400 text-xs mb-1 block">Months ahead</label>
            <select value={periods} onChange={e=>setPeriods(parseInt(e.target.value))}
              className="bg-slate-800 border border-slate-700 rounded-lg px-3 py-2 text-white text-sm focus:outline-none focus:border-primary-500">
              {[1,2,3,6,12].map(n=><option key={n} value={n}>{n} month{n>1?"s":""}</option>)}
            </select>
          </div>
          <div className="flex items-end">
            <button onClick={run} disabled={loading}
              className="px-5 py-2 bg-primary-600 hover:bg-primary-500 hover:shadow-[0_0_15px_rgba(139,92,246,0.5)] disabled:opacity-50 text-white rounded-lg text-sm font-medium transition-all duration-300">
              {loading ? "Running…" : "Run Forecast"}
            </button>
          </div>
        </div>

        {!data && !loading && (
          <p className="text-slate-400 text-sm text-center py-8">Configure options above and click Run Forecast. You need at least 6 months of data.</p>
        )}

        {data && data.forecast.length === 0 && (
          <div className="bg-yellow-500/10 border border-yellow-500/30 rounded-xl p-4">
            <p className="text-yellow-400 text-sm">Not enough historical data to generate a forecast. Add at least 6 months of expenses.</p>
          </div>
        )}

        {chartData && (
          <>
            <Line data={chartData} options={{
              responsive: true,
              plugins: {
                legend: { labels: { color: "#94a3b8", font: { size: 12 } } },
                tooltip: { callbacks: { label: ctx => `₹${ctx.parsed.y.toLocaleString("en-IN")}` } },
              },
              scales: {
                x: { ticks: { color: "#94a3b8" }, grid: { color: "rgba(255,255,255,0.03)" } },
                y: { ticks: { color: "#94a3b8", callback: v => `₹${v.toLocaleString()}` }, grid: { color: "rgba(255,255,255,0.03)" } },
              },
            }}/>
            <div className="grid grid-cols-3 gap-3 mt-2">
              {data.forecast.map(f => (
                <div key={f.ds} className="bg-slate-800/50 rounded-xl p-3 text-center">
                  <p className="text-slate-400 text-xs">{f.ds}</p>
                  <p className="text-white font-bold text-lg">₹{f.yhat.toLocaleString("en-IN")}</p>
                  <p className="text-slate-500 text-xs">±{((f.yhat_upper-f.yhat_lower)/2).toFixed(0)}</p>
                </div>
              ))}
            </div>
          </>
        )}
      </div>
    </div>
  );
}
