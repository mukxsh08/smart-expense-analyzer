// frontend/src/pages/Dashboard.js

import React, { useEffect, useState } from 'react';
import { PieChart, Pie, Cell, Tooltip, BarChart, Bar, XAxis, YAxis, CartesianGrid, ResponsiveContainer } from 'recharts';
import { getDashboard, getCategorySpending, getMonthlyData } from '../api';

const COLORS = ['#3b82f6', '#f59e0b', '#10b981', '#ec4899', '#8b5cf6', '#f97316', '#06b6d4', '#84cc16'];

export default function Dashboard() {
  const [summary, setSummary] = useState(null);
  const [categories, setCategories] = useState([]);
  const [monthly, setMonthly] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([
      getDashboard(),
      getCategorySpending(),
      getMonthlyData()
    ]).then(([dashRes, catRes, monRes]) => {
      setSummary(dashRes.data);
      setCategories(catRes.data);
      setMonthly(monRes.data.slice(0, 6).reverse());
    }).catch(err => console.error(err))
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <div className="loading">⏳ Loading dashboard...</div>;
  if (!summary) return <div className="alert alert-error">Failed to load dashboard data.</div>;

  const trend = summary.month_over_month_pct;

  return (
    <div>
      <div className="page-header">
        <h1>📊 Dashboard</h1>
        <p>Your spending overview at a glance</p>
      </div>

      {/* Stats Cards */}
      <div className="stats-grid">
        <div className="card">
          <h2>This Month</h2>
          <div className="amount">₹{(summary.this_month_total || 0).toLocaleString()}</div>
          <p style={{color: trend > 0 ? '#ef4444' : '#10b981', marginTop: '0.5rem'}}>
            {trend > 0 ? '↑' : '↓'} {Math.abs(trend)}% vs last month
          </p>
        </div>
        <div className="card">
          <h2>Transactions</h2>
          <div className="amount">{summary.this_month_count}</div>
          <p style={{color:'#64748b', marginTop:'0.5rem'}}>this month</p>
        </div>
        <div className="card">
          <h2>Avg per Transaction</h2>
          <div className="amount">₹{(summary.this_month_avg || 0).toLocaleString()}</div>
        </div>
        <div className="card">
          <h2>🚨 Anomalies</h2>
          <div className="amount" style={{color: summary.anomaly_count_this_month > 0 ? '#ef4444' : '#10b981'}}>
            {summary.anomaly_count_this_month}
          </div>
          <p style={{color:'#64748b', marginTop:'0.5rem'}}>flagged this month</p>
        </div>
      </div>

      {/* Charts Row */}
      <div style={{display:'grid', gridTemplateColumns:'1fr 1fr', gap:'1.5rem'}}>

        {/* Pie Chart - Category breakdown */}
        <div className="card">
          <h2 style={{fontSize:'1rem', fontWeight:'600', color:'#1e293b', marginBottom:'1rem'}}>
            Spending by Category
          </h2>
          {categories.length > 0 ? (
            <ResponsiveContainer width="100%" height={280}>
              <PieChart>
                <Pie
                  data={categories}
                  dataKey="total_amount"
                  nameKey="category"
                  cx="50%"
                  cy="50%"
                  outerRadius={90}
                  label={({category, percentage}) => `${category} ${percentage}%`}
                >
                  {categories.map((_, index) => (
                    <Cell key={index} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip formatter={(val) => `₹${val.toLocaleString()}`} />
              </PieChart>
            </ResponsiveContainer>
          ) : (
            <p style={{color:'#94a3b8', textAlign:'center', padding:'2rem'}}>No data yet. Add some expenses!</p>
          )}
        </div>

        {/* Bar Chart - Monthly trend */}
        <div className="card">
          <h2 style={{fontSize:'1rem', fontWeight:'600', color:'#1e293b', marginBottom:'1rem'}}>
            Monthly Spending Trend
          </h2>
          {monthly.length > 0 ? (
            <ResponsiveContainer width="100%" height={280}>
              <BarChart data={monthly}>
                <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
                <XAxis dataKey="month_name" tick={{fontSize:12}} />
                <YAxis tick={{fontSize:12}} />
                <Tooltip formatter={(val) => `₹${val.toLocaleString()}`} />
                <Bar dataKey="total_amount" fill="#3b82f6" radius={[4,4,0,0]} />
              </BarChart>
            </ResponsiveContainer>
          ) : (
            <p style={{color:'#94a3b8', textAlign:'center', padding:'2rem'}}>No data yet.</p>
          )}
        </div>
      </div>
    </div>
  );
}