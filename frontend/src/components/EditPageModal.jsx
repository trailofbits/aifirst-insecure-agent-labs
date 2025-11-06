/**
 * Modal for editing external page content
 */
import React, { useState, useEffect } from 'react';
import '../styles/EditPage.css';

const CONTENT_SERVER_URL = 'http://localhost:8181';

export function EditPageModal({ isOpen, onClose }) {
  const [pageName, setPageName] = useState('vacation');
  const [content, setContent] = useState('');
  const [loading, setLoading] = useState(false);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(false);
  const [copied, setCopied] = useState(false);

  useEffect(() => {
    if (isOpen && pageName) {
      loadPage();
    }
  }, [isOpen, pageName]);

  const loadPage = async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await fetch(`${CONTENT_SERVER_URL}/api/page/${pageName}`);
      const data = await response.json();

      if (response.ok) {
        setContent(data.content);
      } else {
        setError(data.error || 'Failed to load page');
      }
    } catch (err) {
      setError('Failed to connect to content server');
    } finally {
      setLoading(false);
    }
  };

  const savePage = async () => {
    setSaving(true);
    setError(null);
    setSuccess(false);
    try {
      const response = await fetch(`${CONTENT_SERVER_URL}/api/page/${pageName}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ content }),
      });

      const data = await response.json();

      if (response.ok) {
        setSuccess(true);
        setTimeout(() => setSuccess(false), 3000);
      } else {
        setError(data.error || 'Failed to save page');
      }
    } catch (err) {
      setError('Failed to connect to content server');
    } finally {
      setSaving(false);
    }
  };

  const copyUrl = () => {
    const url = `http://content-server:8181/page/${pageName}`;
    navigator.clipboard.writeText(url).then(() => {
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    });
  };

  if (!isOpen) return null;

  return (
    <div className="edit-page-overlay">
      <div className="edit-page-modal">
        <div className="edit-page-header">
          <div>
            <h2>Edit External Page</h2>
            <div className="page-selector">
              <label>Page: </label>
              <select
                value={pageName}
                onChange={(e) => setPageName(e.target.value)}
                disabled={loading || saving}
              >
                <option value="vacation">vacation</option>
                <option value="welcome">welcome</option>
                <option value="ssrf-direct">ssrf-direct</option>
                <option value="ssrf-legitimate">ssrf-legitimate</option>
              </select>
              <button
                onClick={loadPage}
                disabled={loading || saving}
                className="reload-btn"
              >
                🔄 Reload
              </button>
              <button
                onClick={copyUrl}
                className="copy-url-btn"
                title={`Copy URL: http://content-server:8181/page/${pageName}`}
              >
                {copied ? '✓ Copied!' : '📋 Copy URL'}
              </button>
            </div>
          </div>
          <button onClick={onClose} className="close-modal-btn">✕</button>
        </div>

        <div className="edit-page-body">
          {loading ? (
            <div className="loading-state">Loading page content...</div>
          ) : error ? (
            <div className="error-message">
              <strong>Error:</strong> {error}
            </div>
          ) : (
            <textarea
              className="page-editor"
              value={content}
              onChange={(e) => setContent(e.target.value)}
              disabled={saving}
              placeholder="Page content will appear here..."
            />
          )}
        </div>

        <div className="edit-page-footer">
          {success && (
            <div className="success-message">
              ✓ Page saved successfully!
            </div>
          )}
          <div className="button-group">
            <button onClick={onClose} disabled={saving}>
              Cancel
            </button>
            <button
              onClick={savePage}
              disabled={loading || saving || !content}
              className="save-btn"
            >
              {saving ? 'Saving...' : '💾 Save Changes'}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
