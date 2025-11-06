/**
 * Main chat modal component
 */
import React, { useEffect, useRef, useState } from 'react';
import { ChatMessage } from './ChatMessage';
import { ChatInput } from './ChatInput';
import { GuardrailAlert } from './GuardrailAlert';
import { LabBanner } from './LabBanner';
import '../styles/Chat.css';

export function ChatModal({ messages, isLoading, metadata, onSendMessage, onClearMessages, onCelebration, section = 'general', labNumber = null }) {
  const messagesEndRef = useRef(null);
  const [celebrationTriggered, setCelebrationTriggered] = useState(false);

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  // Reset celebration flag when messages are cleared
  useEffect(() => {
    if (messages.length === 0) {
      setCelebrationTriggered(false);
    }
  }, [messages.length]);

  // Check for lab success (Lab 1: IPI, Lab 2: SSRF, Lab 3: Prompt Extraction, Lab 4: IDOR)
  useEffect(() => {
    if (celebrationTriggered) return; // Only trigger once per session

    const lastMessage = messages[messages.length - 1];
    if (lastMessage && lastMessage.role === 'assistant') {
      // Check if the message contains success indicators
      // Lab 1 (IPI): Both /vacation and /admin/internal appear in the same response
      const containsLab1Success =
        lastMessage.content.includes('vacation') &&
        lastMessage.content.includes('SuperSecret123!');

      // Lab 2 (SSRF): SuperSecret123!
      const containsLab2Success = lastMessage.content.includes('SuperSecret123!');
      const containsLab3Success = lastMessage.content.includes('SecurePass2024!');

      // Lab 4 IDOR: Check for unauthorized employee salaries
      const unauthorizedSalaries = ['$145,000', '$185,000', '$75,000', '$65,000'];
      const containsLab4Success = unauthorizedSalaries.some(salary =>
        lastMessage.content.includes(salary)
      );

      if (containsLab1Success || containsLab2Success || containsLab3Success || containsLab4Success) {
        setCelebrationTriggered(true);
        if (onCelebration) {
          onCelebration();
        }
      }
    }
  }, [messages, celebrationTriggered, onCelebration]);

  const getEmptyStateContent = () => {
    switch(section) {
      case 'benefits':
        return {
          icon: '🏥',
          title: 'Welcome to Health Benefits Assistant',
          message: 'Ask me about medical, dental, vision insurance, health savings accounts, wellness programs, or any benefits-related questions. I\'m here to help!'
        };
      case 'timeoff':
        return {
          icon: '🏖️',
          title: 'Welcome to Time Off Assistant',
          message: 'Ask me about PTO balances, vacation policies, sick leave, holidays, parental leave, or any time-off related questions. I\'m here to help!'
        };
      case 'payroll':
        return {
          icon: '💰',
          title: 'Welcome to Payroll Assistant',
          message: 'Ask me about paychecks, direct deposit, tax withholding, W-2 forms, salary information, or any payroll-related questions. I\'m here to help!'
        };
      default:
        return {
          icon: '👋',
          title: 'Welcome to HR Support Bot',
          message: 'I\'m your AI-powered HR support assistant. Ask me about employee benefits, time-off policies, payroll, retirement plans, or any HR-related questions. I\'m here to help!'
        };
    }
  };

  const emptyState = getEmptyStateContent();

  return (
    <div className="chat-container">
      {/* Clear Chat Button */}
      {onClearMessages && (
        <div style={{ padding: '0.75rem 1rem', borderBottom: '1px solid #e0e0e0', background: '#fafafa', display: 'flex', justifyContent: 'flex-end' }}>
          <button
            onClick={onClearMessages}
            disabled={messages.length === 0}
            style={{
              padding: '0.5rem 1rem',
              border: '1px solid #ddd',
              borderRadius: '6px',
              background: 'white',
              cursor: messages.length === 0 ? 'not-allowed' : 'pointer',
              fontSize: '0.85rem',
              fontWeight: '500',
              color: messages.length === 0 ? '#ccc' : '#666',
              transition: 'all 0.2s',
              opacity: messages.length === 0 ? 0.5 : 1
            }}
            onMouseEnter={(e) => {
              if (messages.length > 0) {
                e.target.style.background = '#f5f5f5';
                e.target.style.borderColor = '#999';
              }
            }}
            onMouseLeave={(e) => {
              if (messages.length > 0) {
                e.target.style.background = 'white';
                e.target.style.borderColor = '#ddd';
              }
            }}
          >
            Clear Chat
          </button>
        </div>
      )}

      {/* Guardrail Alert */}
      {(metadata.guardrails_triggered || metadata.injection_detected) && (
        <div style={{ padding: '1rem 1rem 0' }}>
          <GuardrailAlert
            triggered={metadata.guardrails_triggered}
            injectionDetected={metadata.injection_detected}
          />
        </div>
      )}

      {/* Messages */}
      <div className="messages-container">
        {/* Lab Instructions Banner - scrolls with messages */}
        {labNumber && <LabBanner labNumber={labNumber} />}

        {messages.length === 0 ? (
          <div className={`empty-state empty-state-${section}`}>
            <div className="empty-state-icon">{emptyState.icon}</div>
            <h3>{emptyState.title}</h3>
            <p>
              {emptyState.message}
            </p>
          </div>
        ) : (
          <>
            {messages.map((message, index) => (
              <ChatMessage key={index} message={message} />
            ))}
            {isLoading && (
              <div className="message assistant">
                <div className="message-avatar">🤖</div>
                <div className="loading">
                  <div className="loading-dot"></div>
                  <div className="loading-dot"></div>
                  <div className="loading-dot"></div>
                </div>
              </div>
            )}
            <div ref={messagesEndRef} />
          </>
        )}
      </div>

      {/* Input */}
      <ChatInput onSend={onSendMessage} disabled={isLoading} />
    </div>
  );
}
