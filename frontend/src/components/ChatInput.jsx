/**
 * Chat input component
 */
import React, { useState } from 'react';
import '../styles/Chat.css';

export function ChatInput({ onSend, disabled }) {
  const [input, setInput] = useState('');

  const handleSubmit = (e) => {
    e.preventDefault();
    if (input.trim() && !disabled) {
      onSend(input.trim());
      setInput('');
    }
  };

  return (
    <div className="input-container">
      <form onSubmit={handleSubmit} className="input-form">
        <div className="input-wrapper">
          <input
            type="text"
            className="message-input"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Type your message..."
            disabled={disabled}
          />
        </div>
        <button
          type="submit"
          className="send-button"
          disabled={disabled || !input.trim()}
        >
          Send
        </button>
      </form>
    </div>
  );
}
