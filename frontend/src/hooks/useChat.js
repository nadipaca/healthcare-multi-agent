import { useState, useCallback } from 'react';
import { chatService } from '../services/api';

export const useChat = (initialSessionId = null, patientContext = null) => {
  const [sessionId, setSessionId] = useState(
    initialSessionId || `session-${Date.now()}`
  );
  const [messages, setMessages] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const [agentTrace, setAgentTrace] = useState([]);
  const [needsHumanReview, setNeedsHumanReview] = useState(false);

  const sendMessage = useCallback(async (text) => {
    if (!text.trim()) return;

    // Add user message immediately
    const userMessage = {
      role: 'user',
      content: text,
      timestamp: new Date().toISOString(),
    };
    setMessages(prev => [...prev, userMessage]);
    setIsLoading(true);
    setError(null);

    try {
      // Include patient context if available
      const messagePayload = {
        session_id: sessionId,
        message: text,
      };
      
      if (patientContext) {
        messagePayload.patient_id = patientContext.patient_id;
      }
      
      const response = await chatService.sendMessage(messagePayload.session_id, messagePayload.message, patientContext);
      
      // Handle backend response format: response.messages is an array of strings
      const responseContent = response.messages && response.messages.length > 0 
        ? response.messages.join('\n') 
        : response.response || response.message || 'No response';
      
      // Add agent response
      const agentMessage = {
        role: 'assistant',
        content: responseContent,
        timestamp: new Date().toISOString(),
      };
      
      setMessages(prev => [...prev, agentMessage]);
      setAgentTrace(response.agent_trace || []);
      setNeedsHumanReview(response.needs_human_review || false);
      
    } catch (err) {
      const errorMessage = err.response?.data?.detail || err.message || 'Failed to send message';
      setError(errorMessage);
      console.error('Chat error:', err);
      
      // Add error message to chat
      const errorMsg = {
        role: 'system',
        content: `Error: ${errorMessage}`,
        timestamp: new Date().toISOString(),
      };
      setMessages(prev => [...prev, errorMsg]);
    } finally {
      setIsLoading(false);
    }
  }, [sessionId, patientContext]);

  const clearChat = useCallback(() => {
    setMessages([]);
    setAgentTrace([]);
    setNeedsHumanReview(false);
    setError(null);
  }, []);

  const newSession = useCallback(() => {
    const newId = `session-${Date.now()}`;
    setSessionId(newId);
    clearChat();
  }, [clearChat]);

  return {
    sessionId,
    messages,
    isLoading,
    error,
    agentTrace,
    needsHumanReview,
    sendMessage,
    clearChat,
    newSession,
  };
};
