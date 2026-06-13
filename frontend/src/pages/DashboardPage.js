import React, { useEffect, useState } from "react";
import { analyticsAPI } from "../utils/api";
import { Doughnut, Bar } from "react-chartjs-2";
import {
  Chart as ChartJS, ArcElement, Tooltip, Legend,
  CategoryScale, LinearScale, BarElement
} from "chart.js";
import { TrendingUp, TrendingDown, Wallet, Activity } from "lucide-react";
import toast from "react-hot-toast";

ChartJS.register(ArcElement, Tooltip, Legend, CategoryScale, LinearScale, BarElement);

const COLORS = ["#22c55e","#3b82f6","#f59e0b","#ef4444","#8b5cf6","#06b6d4","#f97316","#ec4899","#10b981","#6366f1"];

function StatCard({ title, value, sub, icon: Icon, trend }) {
  return (
    <div className="bg-dark-900 border border-slate-800 rounded-xl p-5">
      <div className="flex items-start justify-between mb-3">
        <div className="w-10 h-10 rounded-lg bg-primary-500/10 flex items-center justify-center">
          <Icon size={20} className="text-primary-400" />
        </div>
        {trend !== undefined && (
          <span className={`text-xs font-medium flex items-center gap-1 ${trend >= 0 ? "text-red-400" : "text-primary-400"}`}>
            {trend >= 0 ? <TrendingUp size={14}/> : <TrendingDown size={14}/>}
            {Math.abs(trend).toFixed(1)}%
          </span>
        )}
      </div>
      <p className="text-slate-400 text-sm">{title}</p>
      <p className="text-white text-2xl font-bold mt-1">{value}</p>
      {sub && <p className="text-slate-500 text-xs mt-1">{sub}</p>}
    </div>
  );
}

export default function DashboardPage() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    analyticsAPI.dashboard()
      .then(res => setData(res.data))
      .catch(() => toast.error("Failed to load dashboard"))
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <p className="text-slate-400 text-center mt-20">Loading dashboard…</p>;
  if (!data) return <p className="text-slate-400 text-center mt-20">No data yet. Add some expenses to get started!</p>;

  const cats = Object.keys(data.category_breakdown);
  const vals = Object.values(data.category_breakdown);

  const donutData = {
    labels: cats,
    datasets: [{ data: vals, backgroundColor: COLORS, borderWidth: 0 }],
  };

  const budgetCats = Object.keys(data.budget_utilization);
  const budgetVals = Object.values(data.budget_utilization);
  const barData = {
    labels: budgetCats,
    datasets: [{
      label: "Budget Used (%)",
      data: budgetVals,
      backgroundColor: budgetVals.map(v => v > 90 ? "#ef4444" : v > 70 ? "#f59e0b" : "#22c55e"),
      borderRadius: 6,
    }],
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-white">Dashboard</h1>
        <p className="text-slate-400 text-sm mt-1">Your financial overview for this month</p>
      </div>

      {/* Stat cards */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard
          title="This Month"
          value={`₹${data.total_expenses_this_month.toLocaleString("en-IN")}`}
          icon={Wallet}
          trend={data.month_over_month_change_pct}
          sub="vs last month"
        />
        <StatCard
          title="Last Month"
          value={`₹${data.total_expenses_last_month.toLocaleString("en-IN")}`}
          icon={Activity}
        />
        <StatCard
          title="Health Score"
          value={data.financial_health_score != null ? `${data.financial_health_score}/100` : "—"}
          icon={Activity}
          sub="Overall financial health"
        />
        <StatCard
          title="Top Category"
          value={data.top_spending_categories[0] || "—"}
          icon={TrendingUp}
          sub="Highest spending this month"
        />
      </div>

      {/* Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-dark-900 border border-slate-800 rounded-xl p-5">
          <h2 className="text-white font-semibold mb-4">Spending by Category</h2>
          {cats.length > 0 ? (
            <Doughnut data={donutData} options={{ plugins: { legend: { labels: { color: "#94a3b8", font: { size: 12 } } } } }} />
          ) : (
            <p className="text-slate-500 text-sm">No expenses recorded this month.</p>
          )}
        </div>

        <div className="bg-dark-900 border border-slate-800 rounded-xl p-5">
          <h2 className="text-white font-semibold mb-4">Budget Utilisation</h2>
          {budgetCats.length > 0 ? (
            <Bar
              data={barData}
              options={{
                plugins: { legend: { display: false } },
                scales: {
                  x: { ticks: { color: "#94a3b8" }, grid: { color: "#1e293b" } },
                  y: { ticks: { color: "#94a3b8" }, grid: { color: "#1e293b" }, max: 120 },
                },
              }}
            />
          ) : (
            <p className="text-slate-500 text-sm">No budgets set. Go to Budgets to set limits.</p>
          )}
        </div>
      </div>
    </div>
  );
}
