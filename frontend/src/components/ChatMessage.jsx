/**
 * Individual chat message component
 */
import React from 'react';
import '../styles/Chat.css';

export function ChatMessage({ message }) {
  const { role, content } = message;

  return (
    <div className={`message ${role}`}>
      <div className="message-avatar">
        {role === 'user' ? '👤' : '🤖'}
      </div>
      <div className="message-content">
        {content}
      </div>
    </div>
  );
}
