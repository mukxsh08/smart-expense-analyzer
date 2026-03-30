// frontend/src/pages/ExpensesPage.js

import React, { useEffect, useState } from 'react';
import { getExpenses, createExpense, deleteExpense, getCategories } from '../api';

const today = new Date().toISOString().split('T')[0];

export default function ExpensesPage() {
  const [expenses, setExpenses] = useState([]);
  const [categories, setCategories] = useState([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(true);
  const [message, setMessage] = useState(null);
  const [showForm, setShowForm] = useState(false);
  const [form, setForm] = useState({
    title: '', amount: '', date: today, merchant: '', description: ''
  });

  const loadExpenses = () => {
    setLoading(true);
    getExpenses({ limit: 50 })
      .then(res => {
        setExpenses(res.data.expenses);
        setTotal(res.data.total);
      })
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    loadExpenses();
    getCategories().then(res => setCategories(res.data));
  }, []);

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      await createExpense({
        ...form,
        amount: parseFloat(form.amount)
      });
      setMessage({ type: 'success', text: '✅ Expense added and auto-categorized!' });
      setForm({ title: '', amount: '', date: today, merchant: '', description: '' });
      setShowForm(false);
      loadExpenses();
    } catch (err) {
      const detail = err.response?.data?.detail;
      setMessage({ type: 'error', text: `❌ Error: ${JSON.stringify(detail)}` });
    }
    setTimeout(() => setMessage(null), 5000);
  };

  const handleDelete = async (id) => {
    if (!window.confirm('Delete this expense?')) return;
    await deleteExpense(id);
    loadExpenses();
  };

  const getCategoryName = (id) => {
    const cat = categories.find(c => c.id === id);
    return cat ? `${cat.icon} ${cat.name}` : '📦 Uncategorized';
  };

  return (
    <div>
      <div className="page-header" style={{display:'flex', justifyContent:'space-between', alignItems:'center'}}>
        <div>
          <h1>📋 Expenses</h1>
          <p>{total} total expenses</p>
        </div>
        <button className="btn btn-primary" onClick={() => setShowForm(!showForm)}>
          {showForm ? '✕ Cancel' : '+ Add Expense'}
        </button>
      </div>

      {message && <div className={`alert alert-${message.type}`}>{message.text}</div>}

      {/* Add Expense Form */}
      {showForm && (
        <div className="card">
          <h3 style={{marginBottom:'1rem'}}>New Expense</h3>
          <form onSubmit={handleSubmit}>
            <div style={{display:'grid', gridTemplateColumns:'1fr 1fr', gap:'1rem'}}>
              <div className="form-group">
                <label>Title *</label>
                <input value={form.title} onChange={e => setForm({...form, title: e.target.value})}
                  placeholder="e.g. Lunch at Swiggy" required />
              </div>
              <div className="form-group">
                <label>Amount (₹) *</label>
                <input type="number" step="0.01" value={form.amount}
                  onChange={e => setForm({...form, amount: e.target.value})}
                  placeholder="e.g. 350" required />
              </div>
              <div className="form-group">
                <label>Date *</label>
                <input type="date" value={form.date}
                  onChange={e => setForm({...form, date: e.target.value})} required />
              </div>
              <div className="form-group">
                <label>Merchant</label>
                <input value={form.merchant} onChange={e => setForm({...form, merchant: e.target.value})}
                  placeholder="e.g. Swiggy" />
              </div>
              <div className="form-group" style={{gridColumn:'span 2'}}>
                <label>Description (optional)</label>
                <input value={form.description} onChange={e => setForm({...form, description: e.target.value})} />
              </div>
            </div>
            <button type="submit" className="btn btn-success">Save Expense</button>
          </form>
        </div>
      )}

      {/* Expenses Table */}
      <div className="card" style={{padding:0}}>
        {loading ? (
          <div className="loading">Loading expenses...</div>
        ) : expenses.length === 0 ? (
          <div style={{padding:'3rem', textAlign:'center', color:'#94a3b8'}}>
            No expenses yet. Add one above or upload a CSV!
          </div>
        ) : (
          <table className="expense-table">
            <thead>
              <tr>
                <th>Title</th>
                <th>Amount</th>
                <th>Date</th>
                <th>Merchant</th>
                <th>Category</th>
                <th>Flag</th>
                <th>Action</th>
              </tr>
            </thead>
            <tbody>
              {expenses.map(exp => (
                <tr key={exp.id}>
                  <td>{exp.title}</td>
                  <td><strong>₹{exp.amount.toLocaleString()}</strong></td>
                  <td>{exp.date}</td>
                  <td>{exp.merchant || '—'}</td>
                  <td>{getCategoryName(exp.category_id)}</td>
                  <td>
                    {exp.is_anomaly
                      ? <span className="badge-anomaly" title={exp.anomaly_reason}>🚨 Anomaly</span>
                      : <span style={{color:'#10b981'}}>✓ Normal</span>
                    }
                  </td>
                  <td>
                    <button className="btn btn-danger" style={{padding:'0.3rem 0.7rem', fontSize:'0.8rem'}}
                      onClick={() => handleDelete(exp.id)}>
                      Delete
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  );
}