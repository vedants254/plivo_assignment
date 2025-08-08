import React, { useState, useEffect } from 'react';
import './App.css';
import Login from './components/login_component.js';
import Signup from './components/signup_component.js';
import Dashboard from './components/dashboard_component.js';

// Use Vercel deployment URL for production, localhost for development
const API_BASE_URL = process.env.REACT_APP_API_URL || 
  (process.env.NODE_ENV === 'production' 
    ? ''
    : 'http://localhost:8000'
  );

function App() {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [currentView, setCurrentView] = useState('login');
  const [token, setToken] = useState(null);

  useEffect(() => {
    const savedToken = localStorage.getItem('token');
    if (savedToken) {
      setToken(savedToken);
      setIsAuthenticated(true);
    }
  }, []);

  const handleLogin = (newToken) => {
    localStorage.setItem('token', newToken);
    setToken(newToken);
    setIsAuthenticated(true);
  };

  const handleLogout = () => {
    localStorage.removeItem('token');
    setToken(null);
    setIsAuthenticated(false);
    setCurrentView('login');
  };

  if (isAuthenticated) {
    return (
      <div className="App">
        <Dashboard token={token} onLogout={handleLogout} apiBaseUrl={API_BASE_URL} />
      </div>
    );
  }

  return (
    <div className="App">
      <div className="auth-container">
        <div className="auth-header">
          <h1>Multi-Modal AI App</h1>
          <div className="auth-tabs">
            <button 
              className={currentView === 'login' ? 'active' : ''} 
              onClick={() => setCurrentView('login')}
            >
              Login
            </button>
            <button 
              className={currentView === 'signup' ? 'active' : ''} 
              onClick={() => setCurrentView('signup')}
            >
              Sign Up
            </button>
          </div>
        </div>
        
        {currentView === 'login' ? (
          <Login onLogin={handleLogin} apiBaseUrl={API_BASE_URL} />
        ) : (
          <Signup onLogin={handleLogin} apiBaseUrl={API_BASE_URL} />
        )}
      </div>
    </div>
  );
}

export default App;