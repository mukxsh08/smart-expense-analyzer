// frontend/src/pages/UploadPage.js

import React, { useState } from 'react';
import { uploadCSV, seedCategories, seedRules } from '../api';

export default function UploadPage() {
  const [file, setFile] = useState(null);
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [seedMsg, setSeedMsg] = useState(null);

  const handleUpload = async (e) => {
    e.preventDefault();
    if (!file) return;

    setLoading(true);
    const formData = new FormData();
    formData.append('file', file);

    try {
      const res = await uploadCSV(formData);
      setResult(res.data);
    } catch (err) {
      setResult({ error: err.response?.data?.detail || 'Upload failed' });
    } finally {
      setLoading(false);
    }
  };

  const handleSeedAll = async () => {
    try {
      await seedCategories();
      await seedRules();
      setSeedMsg({ type: 'success', text: '✅ Default categories and rules seeded!' });
    } catch (err) {
      setSeedMsg({ type: 'error', text: '❌ Seeding failed: ' + err.message });
    }
    setTimeout(() => setSeedMsg(null), 4000);
  };

  return (
    <div>
      <div className="page-header">
        <h1>📁 Upload CSV</h1>
        <p>Bulk import expenses from a CSV file</p>
      </div>

      {/* Seed data button */}
      <div className="card">
        <h3 style={{marginBottom:'0.5rem'}}>🌱 First Time Setup</h3>
        <p style={{color:'#64748b', marginBottom:'1rem', fontSize:'0.9rem'}}>
          Click below to add default categories (Food, Transport, etc.) and auto-categorization rules.
          Do this once before uploading expenses.
        </p>
        {seedMsg && <div className={`alert alert-${seedMsg.type}`}>{seedMsg.text}</div>}
        <button className="btn btn-primary" onClick={handleSeedAll}>
          🌱 Seed Default Categories + Rules
        </button>
      </div>

      {/* CSV Format Info */}
      <div className="card">
        <h3 style={{marginBottom:'0.5rem'}}>📝 Required CSV Format</h3>
        <p style={{color:'#64748b', fontSize:'0.9rem', marginBottom:'1rem'}}>
          Your CSV must have these columns. The header row names must match exactly.
        </p>
        <table className="expense-table">
          <thead>
            <tr>
              <th>Column</th>
              <th>Required?</th>
              <th>Example</th>
            </tr>
          </thead>
          <tbody>
            <tr><td>title</td><td>✅ Yes</td><td>Lunch at Zomato</td></tr>
            <tr><td>amount</td><td>✅ Yes</td><td>350.00</td></tr>
            <tr><td>date</td><td>✅ Yes</td><td>2024-01-15</td></tr>
            <tr><td>merchant</td><td>❌ Optional</td><td>Zomato</td></tr>
            <tr><td>description</td><td>❌ Optional</td><td>Team lunch</td></tr>
            <tr><td>tags</td><td>❌ Optional</td><td>work,food</td></tr>
          </tbody>
        </table>

        <div style={{background:'#f8fafc', padding:'1rem', borderRadius:'8px', marginTop:'1rem'}}>
          <p style={{fontWeight:'600', marginBottom:'0.5rem'}}>Sample CSV content:</p>
          <code style={{fontSize:'0.85rem', color:'#475569'}}>
            title,amount,date,merchant<br/>
            Uber to office,180,2024-01-15,Uber<br/>
            Netflix subscription,649,2024-01-01,Netflix<br/>
            Swiggy lunch,350,2024-01-15,Swiggy
          </code>
        </div>
      </div>

      {/* Upload Form */}
      <div className="card">
        <h3 style={{marginBottom:'1rem'}}>Upload Your File</h3>
        <form onSubmit={handleUpload}>
          <div className="form-group">
            <label>Select CSV File</label>
            <input
              type="file"
              accept=".csv"
              onChange={e => setFile(e.target.files[0])}
              style={{padding:'0.4rem'}}
            />
          </div>
          <button type="submit" className="btn btn-primary" disabled={!file || loading}>
            {loading ? '⏳ Uploading...' : '📤 Upload & Process'}
          </button>
        </form>

        {/* Upload Result */}
        {result && (
          <div style={{marginTop:'1.5rem'}}>
            {result.error ? (
              <div className="alert alert-error">❌ {result.error}</div>
            ) : (
              <div>
                <div className="alert alert-success">
                  ✅ Processing complete! {result.processing_result?.success_count} of {result.processing_result?.total_rows} rows imported.
                </div>
                {result.processing_result?.error_count > 0 && (
                  <div className="alert alert-error">
                    ❌ {result.processing_result?.error_count} rows had errors:
                    <ul style={{marginTop:'0.5rem', paddingLeft:'1.5rem'}}>
                      {result.processing_result?.errors?.map((e, i) => (
                        <li key={i} style={{fontSize:'0.85rem'}}>
                          Row {e.row}: {e.error}
                        </li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}