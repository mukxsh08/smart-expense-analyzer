// frontend/src/App.js

import React from 'react';
import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom';
import Dashboard from './pages/Dashboard';
import ExpensesPage from './pages/ExpensesPage';
import UploadPage from './pages/UploadPage';
import RulesPage from './pages/RulesPage';
import './App.css';

function App() {
  return (
    <Router>
      <div className="app">
        {/* Navigation Bar */}
        <nav className="navbar">
          <div className="nav-brand">💰 Smart Expense Analyzer</div>
          <div className="nav-links">
            <Link to="/">📊 Dashboard</Link>
            <Link to="/expenses">📋 Expenses</Link>
            <Link to="/upload">📁 Upload CSV</Link>
            <Link to="/rules">⚙️ Rules</Link>
          </div>
        </nav>

        {/* Page Content */}
        <main className="main-content">
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/expenses" element={<ExpensesPage />} />
            <Route path="/upload" element={<UploadPage />} />
            <Route path="/rules" element={<RulesPage />} />
          </Routes>
        </main>
      </div>
    </Router>
  );
}

export default App;
