/**
 * Custom hook for chat functionality
 */
import { useState, useCallback } from 'react';
import { ChatAPI } from '../lib/api';

export function useChat(regexGuardrailsEnabled = true, nemoGuardrailsEnabled = true, department = 'hr') {
  const [messages, setMessages] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const [metadata, setMetadata] = useState({});

  const sendMessage = useCallback(async (content) => {
    setIsLoading(true);
    setError(null);

    // Add user message
    const userMessage = { role: 'user', content };
    setMessages(prev => [...prev, userMessage]);

    try {
      // Stream the response
      let assistantContent = '';
      const allMessages = [...messages, userMessage];

      for await (const chunk of ChatAPI.streamMessage(allMessages, regexGuardrailsEnabled, nemoGuardrailsEnabled, department)) {
        if (chunk.error) {
          throw new Error(chunk.error);
        }

        if (chunk.content) {
          assistantContent += chunk.content;
          setMessages(prev => {
            const lastMessage = prev[prev.length - 1];
            if (lastMessage && lastMessage.role === 'assistant') {
              // Update existing assistant message
              return [
                ...prev.slice(0, -1),
                { role: 'assistant', content: assistantContent }
              ];
            } else {
              // Add new assistant message
              return [...prev, { role: 'assistant', content: assistantContent }];
            }
          });
        }

        if (chunk.done) {
          // Store metadata
          setMetadata({
            guardrails_triggered: chunk.guardrails_triggered,
            injection_detected: chunk.injection_detected,
            ...chunk.metadata
          });
        }
      }
    } catch (err) {
      console.error('Chat error:', err);
      setError(err.message);
      // Remove the user message if there was an error
      setMessages(prev => prev.slice(0, -1));
    } finally {
      setIsLoading(false);
    }
  }, [messages, regexGuardrailsEnabled, nemoGuardrailsEnabled, department]);

  const clearMessages = useCallback(() => {
    setMessages([]);
    setMetadata({});
    setError(null);
  }, []);

  return {
    messages,
    isLoading,
    error,
    metadata,
    sendMessage,
    clearMessages
  };
}
