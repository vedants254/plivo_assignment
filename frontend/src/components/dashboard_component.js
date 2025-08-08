import React, { useState } from 'react';
import ImageUploader from './ImageUploader';
import Summarizer from './Summarizer';
import HistoryList from './HistoryList';

const Dashboard = ({ token, onLogout, apiBaseUrl }) => {
  const [activeTab, setActiveTab] = useState('image');

  return (
    <div className="dashboard">
      <div className="dashboard-header">
        <h1>Multi-Modal AI Dashboard</h1>
        <button onClick={onLogout} className="logout-button">
          Logout
        </button>
      </div>
      
      <div className="dashboard-tabs">
        <button
          className={activeTab === 'image' ? 'active' : ''}
          onClick={() => setActiveTab('image')}
        >
          Image Analysis
        </button>
        <button
          className={activeTab === 'summarize' ? 'active' : ''}
          onClick={() => setActiveTab('summarize')}
        >
          Document/URL Summarization
        </button>
        <button
          className={activeTab === 'history' ? 'active' : ''}
          onClick={() => setActiveTab('history')}
        >
          History
        </button>
      </div>
      
      <div className="dashboard-content">
        {activeTab === 'image' && (
          <ImageUploader token={token} apiBaseUrl={apiBaseUrl} />
        )}
        {activeTab === 'summarize' && (
          <Summarizer token={token} apiBaseUrl={apiBaseUrl} />
        )}
        {activeTab === 'history' && (
          <HistoryList token={token} apiBaseUrl={apiBaseUrl} />
        )}
      </div>
    </div>
  );
};

export default Dashboard;