// frontend/src/pages/RulesPage.js

import React, { useEffect, useState } from 'react';
import { getRules, testRule } from '../api';

export default function RulesPage() {
  const [rules, setRules] = useState([]);
  const [loading, setLoading] = useState(true);
  const [testForm, setTestForm] = useState({ title: '', amount: '', date: new Date().toISOString().split('T')[0], merchant: '' });
  const [testResult, setTestResult] = useState(null);

  useEffect(() => {
    getRules()
      .then(res => setRules(res.data))
      .finally(() => setLoading(false));
  }, []);

  const handleTest = async (e) => {
    e.preventDefault();
    try {
      const res = await testRule({
        ...testForm,
        amount: parseFloat(testForm.amount) || 0
      });
      setTestResult(res.data);
    } catch (err) {
      setTestResult({ error: err.response?.data?.detail || 'Test failed' });
    }
  };

  const RULE_TYPE_COLOR = {
    keyword: '#3b82f6',
    merchant: '#8b5cf6',
    amount_range: '#f59e0b'
  };

  return (
    <div>
      <div className="page-header">
        <h1>⚙️ Rule Engine</h1>
        <p>Rules auto-categorize your expenses. Higher priority rules are checked first.</p>
      </div>

      {/* Test Rule Engine */}
      <div className="card">
        <h3 style={{marginBottom:'1rem'}}>🧪 Test Rule Engine</h3>
        <p style={{color:'#64748b', fontSize:'0.9rem', marginBottom:'1rem'}}>
          Enter a fake expense below to see which category the rule engine would assign (without saving).
        </p>
        <form onSubmit={handleTest}>
          <div style={{display:'grid', gridTemplateColumns:'1fr 1fr 1fr', gap:'1rem'}}>
            <div className="form-group">
              <label>Title</label>
              <input value={testForm.title} onChange={e => setTestForm({...testForm, title: e.target.value})}
                placeholder="e.g. Uber to airport" required />
            </div>
            <div className="form-group">
              <label>Amount</label>
              <input type="number" value={testForm.amount} onChange={e => setTestForm({...testForm, amount: e.target.value})}
                placeholder="e.g. 250" required />
            </div>
            <div className="form-group">
              <label>Merchant (optional)</label>
              <input value={testForm.merchant} onChange={e => setTestForm({...testForm, merchant: e.target.value})}
                placeholder="e.g. Uber" />
            </div>
          </div>
          <button type="submit" className="btn btn-primary">🔍 Test Categorization</button>
        </form>

        {testResult && (
          <div style={{marginTop:'1rem'}}>
            {testResult.error ? (
              <div className="alert alert-error">❌ {JSON.stringify(testResult.error)}</div>
            ) : (
              <div className="alert alert-success">
                <strong>Assigned Category:</strong> {testResult.assigned_category}
                {testResult.rule_explanations?.length > 0 && (
                  <p style={{marginTop:'0.5rem', fontSize:'0.85rem'}}>
                    Matched by rule: "{testResult.rule_explanations[0].rule_name}"
                  </p>
                )}
              </div>
            )}
          </div>
        )}
      </div>

      {/* Rules Table */}
      <div className="card" style={{padding:0}}>
        <div style={{padding:'1.5rem 1.5rem 0'}}>
          <h3>{rules.length} Active Rules</h3>
        </div>
        {loading ? (
          <div className="loading">Loading rules...</div>
        ) : (
          <table className="expense-table">
            <thead>
              <tr>
                <th>#</th>
                <th>Rule Name</th>
                <th>Type</th>
                <th>Condition</th>
                <th>→ Category</th>
                <th>Priority</th>
                <th>Active</th>
              </tr>
            </thead>
            <tbody>
              {rules.map(rule => (
                <tr key={rule.id}>
                  <td style={{color:'#94a3b8'}}>{rule.id}</td>
                  <td>{rule.name}</td>
                  <td>
                    <span style={{
                      background: RULE_TYPE_COLOR[rule.rule_type] + '20',
                      color: RULE_TYPE_COLOR[rule.rule_type],
                      padding:'2px 8px', borderRadius:'4px', fontSize:'0.8rem', fontWeight:600
                    }}>
                      {rule.rule_type}
                    </span>
                  </td>
                  <td style={{maxWidth:'250px', overflow:'hidden', textOverflow:'ellipsis', whiteSpace:'nowrap', fontSize:'0.85rem', color:'#475569'}}>
                    {rule.condition}
                  </td>
                  <td><strong>{rule.category_name}</strong></td>
                  <td>{rule.priority}</td>
                  <td>{rule.is_active ? '✅' : '❌'}</td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  );
}