/**
 * Alert component for guardrail triggers
 */
import React from 'react';
import '../styles/App.css';

export function GuardrailAlert({ triggered, injectionDetected }) {
  if (!triggered && !injectionDetected) {
    return null;
  }

  return (
    <div className={`alert ${injectionDetected ? 'danger' : 'warning'}`}>
      <div className="alert-icon">
        {injectionDetected ? '🛡️' : '⚠️'}
      </div>
      <div className="alert-content">
        <h4>
          {injectionDetected ? 'Injection Detected!' : 'Guardrail Triggered'}
        </h4>
        <p>
          {injectionDetected
            ? 'Potential prompt injection detected and blocked by guardrails.'
            : 'The guardrail system flagged this content for review.'}
        </p>
      </div>
    </div>
  );
}
