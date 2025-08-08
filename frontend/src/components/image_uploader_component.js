import React, { useState } from 'react';

const ImageUploader = ({ token, apiBaseUrl }) => {
  const [file, setFile] = useState(null);
  const [preview, setPreview] = useState(null);
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleFileChange = (e) => {
    const selectedFile = e.target.files[0];
    if (selectedFile) {
      if (selectedFile.type.startsWith('image/')) {
        setFile(selectedFile);
        setError('');
        
        // Create preview
        const reader = new FileReader();
        reader.onload = (e) => setPreview(e.target.result);
        reader.readAsDataURL(selectedFile);
      } else {
        setError('Please select a valid image file (JPG or PNG)');
        setFile(null);
        setPreview(null);
      }
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!file) return;

    setLoading(true);
    setError('');
    setResult(null);

    try {
      const formData = new FormData();
      formData.append('file', file);

      const response = await fetch(`${apiBaseUrl}/image/analyze`, {
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
        setError(data.detail || 'Image analysis failed');
      }
    } catch (err) {
      setError('Network error. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleReset = () => {
    setFile(null);
    setPreview(null);
    setResult(null);
    setError('');
  };

  return (
    <div className="feature-container">
      <h2>Image Analysis</h2>
      <p>Upload an image to get a detailed AI-generated description</p>
      
      <form onSubmit={handleSubmit} className="upload-form">
        <div className="file-input-container">
          <label htmlFor="image-file" className="file-input-label">
            Choose Image File
          </label>
          <input
            type="file"
            id="image-file"
            accept="image/jpeg,image/jpg,image/png"
            onChange={handleFileChange}
            className="file-input"
          />
        </div>
        
        {preview && (
          <div className="image-preview">
            <img src={preview} alt="Preview" />
          </div>
        )}
        
        {error && <div className="error-message">{error}</div>}
        
        <div className="button-group">
          <button
            type="submit"
            disabled={!file || loading}
            className="analyze-button"
          >
            {loading ? 'Analyzing...' : 'Analyze Image'}
          </button>
          
          {(file || result) && (
            <button type="button" onClick={handleReset} className="reset-button">
              Reset
            </button>
          )}
        </div>
      </form>
      
      {result && (
        <div className="result-container">
          <h3>Analysis Result</h3>
          <div className="result-content">
            <p><strong>File:</strong> {result.filename}</p>
            <p><strong>Description:</strong></p>
            <div className="description">{result.description}</div>
          </div>
        </div>
      )}
    </div>
  );
};

export default ImageUploader;