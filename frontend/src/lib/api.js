/**
 * API client for chatbot backend
 */

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export class ChatAPI {
  /**
   * Send a chat message (non-streaming)
   */
  static async sendMessage(messages, regexGuardrailsEnabled = true, nemoGuardrailsEnabled = true, department = 'hr') {
    const response = await fetch(`${API_BASE_URL}/api/chat`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        messages,
        guardrails_enabled: regexGuardrailsEnabled,
        nemo_guardrails_enabled: nemoGuardrailsEnabled,
        department,
        stream: false,
      }),
    });

    if (!response.ok) {
      throw new Error(`API error: ${response.statusText}`);
    }

    return response.json();
  }

  /**
   * Send a chat message (streaming)
   */
  static async *streamMessage(messages, regexGuardrailsEnabled = true, nemoGuardrailsEnabled = true, department = 'hr') {
    const response = await fetch(`${API_BASE_URL}/api/chat/stream`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        messages,
        guardrails_enabled: regexGuardrailsEnabled,
        nemo_guardrails_enabled: nemoGuardrailsEnabled,
        department,
        stream: true,
      }),
    });

    if (!response.ok) {
      throw new Error(`API error: ${response.statusText}`);
    }

    const reader = response.body.getReader();
    const decoder = new TextDecoder();

    while (true) {
      const { done, value } = await reader.read();
      if (done) break;

      const chunk = decoder.decode(value);
      const lines = chunk.split('\n');

      for (const line of lines) {
        if (line.startsWith('data: ')) {
          const data = line.slice(6);
          try {
            const parsed = JSON.parse(data);
            yield parsed;
          } catch (e) {
            console.error('Error parsing SSE data:', e);
          }
        }
      }
    }
  }

  /**
   * Check API health
   */
  static async checkHealth() {
    const response = await fetch(`${API_BASE_URL}/health`);
    return response.json();
  }
}
