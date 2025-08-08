import React, { useState } from 'react';

const Summarizer = ({ token, apiBaseUrl }) => {
  const [inputType, setInputType] = useState('file');
  const [file, setFile] = useState(null);
  const [url, setUrl] = useState('');
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleFileChange = (e) => {
    const selectedFile = e.target.files[0];
    if (selectedFile) {
      const validTypes = [
        'application/pdf',
        'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
      ];
      
      if (validTypes.includes(selectedFile.type)) {
        setFile(selectedFile);
        setError('');
      } else {
        setError('Please select a valid PDF or DOCX file');
        setFile(null);
      }
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (inputType === 'file' && !file) return;
    if (inputType === 'url' && !url.trim()) return;

    setLoading(true);
    setError('');
    setResult(null);

    try {
      const formData = new FormData();
      
      if (inputType === 'file') {
        formData.append('file', file);
      } else {
        formData.append('url', url.trim());
      }

      const response = await fetch(`${apiBaseUrl}/doc/summarize`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
        },
        body: formData,
      });

      const data = await response.json();

      if (response.ok) {
        setResult(data);
      } else {
        setError(data.detail || 'Summarization failed');
      }
    } catch (err) {
      setError('Network error. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleReset = () => {
    setFile(null);
    setUrl('');
    setResult(null);
    setError('');
  };

  const handleInputTypeChange = (type) => {
    setInputType(type);
    setFile(null);
    setUrl('');
    setError('');
    setResult(null);
  };

  return (
    <div className="feature-container">
      <h2>Document & URL Summarization</h2>
      <p>Upload a document or provide a URL to get an AI-generated summary</p>
      
      <div className="input-type-selector">
        <button
          type="button"
          className={inputType === 'file' ? 'active' : ''}
          