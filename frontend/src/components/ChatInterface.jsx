import React, { useState, useRef, useEffect } from 'react';
import { Send, RefreshCw, User, Bot, AlertTriangle, Loader2, Paperclip, X } from 'lucide-react';
import { useChat } from '../hooks/useChat';
import { fileService } from '../services/api';

const ChatInterface = ({ selectedPatient, patientData }) => {
  const {
    sessionId,
    messages,
    isLoading,
    error,
    agentTrace,
    needsHumanReview,
    sendMessage,
    newSession,
  } = useChat(null, selectedPatient);

  const [inputValue, setInputValue] = useState('');
  const messagesEndRef = useRef(null);
  const [proactiveActions, setProactiveActions] = useState([]);
  const [currentFlow, setCurrentFlow] = useState(null);
   const [selectedFile, setSelectedFile] = useState(null);
  const [uploadingFile, setUploadingFile] = useState(false);
  const fileInputRef = useRef(null);

  // Auto-scroll to bottom
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  // ENHANCED: Handle response and set proactive actions
  useEffect(() => {
    if (messages.length > 0) {
      const lastMessage = messages[messages.length - 1];
      if (lastMessage.role === 'assistant') {
        const content = lastMessage.content.toLowerCase();
        
        // Detect flow state and suggest next actions
        if (content.includes("immediate relief options") || content.includes("recommended next step")) {
          setProactiveActions([
            "✅ Got it, let's schedule the appointment",
            "ℹ️ Tell me more about treatment options", 
            "📞 I need to call someone first",
            "⏰ Check my calendar availability"
          ]);
          setCurrentFlow("post-symptom");
        } else if (content.includes("booked") && content.includes("appointment")) {
          setProactiveActions([
            "💳 Yes, check my insurance coverage",
            "📋 What should I prepare for the visit?",
            "📅 Add this to my calendar",
            "🔔 Set up appointment reminders"
          ]);
          setCurrentFlow("post-appointment");
        } else if (content.includes("insurance coverage") || content.includes("coverage verified")) {
          setProactiveActions([
            "✅ Perfect, I'm all set!",
            "❓ What if I need to reschedule?",
            "💊 Will my prescriptions be covered too?",
            "👨‍⚕️ Tell me about my doctor"
          ]);
          setCurrentFlow("post-insurance");
        } else {
          setProactiveActions([]);
        }
      }
    }
  }, [messages]);

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e);
    }
  };

  const handleFileSelect = (e) => {
    const file = e.target.files[0];
    if (file) {
      // Validate file size (10MB)
      if (file.size > 10 * 1024 * 1024) {
        alert('File size must be less than 10MB');
        return;
      }
      setSelectedFile(file);
    }
  };

  const handleRemoveFile = () => {
    setSelectedFile(null);
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

   const handleSubmit = async (e) => {
    e.preventDefault();
    if ((!inputValue.trim() && !selectedFile) || isLoading) return;
    
    setProactiveActions([]);
    
    // If there's a file, upload it first
    if (selectedFile) {
      setUploadingFile(true);
      try {
        const uploadResponse = await fileService.uploadPrescription(
          selectedFile,
          null,
          inputValue || 'Uploaded from chat'
        );
        
        // Send message about the uploaded file
        await sendMessage(
          inputValue || `I've uploaded a file: ${selectedFile.name}`,
          { file_id: uploadResponse.file_id }
        );
        
        handleRemoveFile();
      } catch (error) {
        alert('File upload failed: ' + (error.response?.data?.detail || error.message));
      } finally {
        setUploadingFile(false);
      }
    } else {
      // Just send text message
      await sendMessage(inputValue);
    }
    
    setInputValue('');
  };

  const quickSuggestions = [
    { text: "I have a headache and fever", emoji: "🤕" },
    { text: "Schedule an appointment", emoji: "📅" },
    { text: "Check my insurance coverage", emoji: "💳" },
    { text: "I want to give feedback", emoji: "⭐" },
  ];

  return (
    <div className="flex flex-col h-[calc(100vh-64px)] bg-gray-50">
      {/* Header */}
      <div className="bg-gradient-to-r from-primary to-secondary text-white p-4 shadow-lg flex-shrink-0">
        <div className="max-w-4xl mx-auto flex justify-between items-center">
          <div>
            <h1 className="text-2xl font-bold">🏥 Healthcare Assistant</h1>
            <p className="text-sm opacity-90">Session: {sessionId.substring(0, 16)}...</p>
          </div>
          <button
            onClick={newSession}
            className="flex items-center gap-2 bg-white/20 hover:bg-white/30 px-4 py-2 rounded-lg transition-colors"
          >
            <RefreshCw size={18} />
            New Chat
          </button>
        </div>
      </div>

      {/* Agent Trace */}
      {agentTrace.length > 0 && (
        <div className="bg-blue-50 border-b border-blue-100 p-3 flex-shrink-0">
          <div className="max-w-4xl mx-auto flex items-center gap-2 text-sm">
            <span className="text-blue-700 font-medium">Active:</span>
            {agentTrace.map((agent, idx) => (
              <span key={idx} className="bg-blue-200 text-blue-800 px-2 py-1 rounded-full text-xs">
                {agent}
              </span>
            ))}
          </div>
        </div>
      )}

      {/* ENHANCED: Proactive Actions */}
      {proactiveActions.length > 0 && (
        <div className="bg-gradient-to-r from-green-50 to-blue-50 border-b border-green-100 p-4 flex-shrink-0">
          <div className="max-w-4xl mx-auto">
            <p className="text-sm font-medium text-green-700 mb-2">
              🤖 I can help you with next steps:
            </p>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
              {proactiveActions.map((action, idx) => (
                <button
                  key={idx}
                  onClick={() => {
                    setInputValue(action.replace(/[✅ℹ️📞⏰💳📋📅🔔❓💊👨‍⚕️] /, ''));
                    setProactiveActions([]);
                  }}
                  className="bg-white hover:bg-green-50 text-left text-green-800 px-4 py-3 rounded-lg border border-green-200 hover:border-green-300 transition-all text-sm font-medium shadow-sm hover:shadow-md"
                >
                  {action}
                </button>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* Messages Area*/}
      <div className="flex-1 overflow-y-auto p-4 min-h-0">
        <div className="max-w-4xl mx-auto">
          {/* Welcome Message */}
          {messages.length === 0 && (
            <div className="text-center py-12">
              <h2 className="text-2xl font-semibold text-gray-700 mb-4">
                Welcome to Healthcare Assistant
              </h2>
              <p className="text-gray-500 mb-6">
                I can help you with symptoms, appointments, insurance, and more.
              </p>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4 max-w-2xl mx-auto">
                {quickSuggestions.map((suggestion, idx) => (
                  <button
                    key={idx}
                    onClick={() => setInputValue(suggestion.text)}
                    className="card text-left hover:shadow-xl transition-all cursor-pointer"
                  >
                    <span className="text-2xl mb-2 block">{suggestion.emoji}</span>
                    <span className="text-sm">{suggestion.text}</span>
                  </button>
                ))}
              </div>
            </div>
          )}

          {/* Messages - keeping existing message rendering code */}
          {messages.map((msg, idx) => {
            const isUser = msg.role === 'user';
            const isSystem = msg.role === 'system';
            
            return (
              <div key={idx} className={`flex ${isUser ? 'justify-end' : 'justify-start'} mb-4`}>
                <div className={`flex max-w-[70%] ${isUser ? 'flex-row-reverse' : 'flex-row'} gap-2`}>
                  {/* Avatar */}
                  {!isSystem && (
                    <div className={`flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center ${
                      isUser ? 'bg-primary' : 'bg-gray-200'
                    }`}>
                      {isUser ? (
                        <User size={18} className="text-white" />
                      ) : (
                        <Bot size={18} className="text-gray-600" />
                      )}
                    </div>
                  )}
                  
                  {/* Message Content */}
                  <div className={`rounded-lg px-4 py-2 ${
                    isUser 
                      ? 'bg-gradient-to-r from-primary to-secondary text-white' 
                      : isSystem
                      ? 'bg-red-100 text-red-700 border border-red-300'
                      : 'bg-white shadow-md'
                  }`}>
                    <p className="text-sm whitespace-pre-wrap">{msg.content}</p>
                    
                    {needsHumanReview && !isUser && !isSystem && (
                      <div className="mt-2 flex items-center gap-2 text-orange-600 text-xs">
                        <AlertTriangle size={14} />
                        <span>Flagged for human review</span>
                      </div>
                    )}
                    
                    <div className={`text-xs mt-1 ${
                      isUser ? 'text-white/70' : isSystem ? 'text-red-600' : 'text-gray-500'
                    }`}>
                      {new Date(msg.timestamp).toLocaleTimeString([], { 
                        hour: '2-digit', 
                        minute: '2-digit' 
                      })}
                    </div>
                  </div>
                </div>
              </div>
            );
          })}

          {/* Typing Indicator */}
          {isLoading && (
            <div className="flex items-center gap-2 mb-4">
              <div className="w-8 h-8 rounded-full bg-gray-200 flex items-center justify-center">
                <Loader2 size={18} className="text-gray-600 animate-spin" />
              </div>
              <span className="text-sm text-gray-500">Agent is thinking...</span>
            </div>
          )}

          <div ref={messagesEndRef} />
        </div>
      </div>

      {/* Input Area - keeping existing code */}
   <div className="border-t bg-white p-4 shadow-lg flex-shrink-0">
        <form onSubmit={handleSubmit} className="max-w-4xl mx-auto">
          {/* File Preview */}
          {selectedFile && (
            <div className="mb-3 flex items-center gap-2 bg-blue-50 p-3 rounded-lg border border-blue-200">
              <Paperclip size={16} className="text-blue-600" />
              <span className="text-sm text-blue-800 flex-1">{selectedFile.name}</span>
              <span className="text-xs text-blue-600">
                {(selectedFile.size / 1024).toFixed(1)} KB
              </span>
              <button
                type="button"
                onClick={handleRemoveFile}
                className="text-red-600 hover:text-red-800"
              >
                <X size={16} />
              </button>
            </div>
          )}

          <div className="flex gap-2">
            {/* File Upload Button */}
            <input
              ref={fileInputRef}
              type="file"
              accept="image/*,.pdf"
              onChange={handleFileSelect}
              className="hidden"
              id="file-upload-chat"
            />
            <label
              htmlFor="file-upload-chat"
              className="flex items-center justify-center w-12 h-12 border-2 border-gray-300 rounded-lg hover:bg-gray-50 cursor-pointer transition-colors"
              title="Upload prescription or document"
            >
              <Paperclip size={20} className="text-gray-600" />
            </label>

            {/* Text Input */}
            <input
              type="text"
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder={
                selectedFile 
                  ? "Add a note about this file (optional)..." 
                  : "Type your message or attach a file..."
              }
              disabled={isLoading || uploadingFile}
              className="flex-1 px-4 py-3 border rounded-lg focus:outline-none focus:ring-2 focus:ring-primary disabled:bg-gray-100"
            />

            {/* Send Button */}
            <button
              type="submit"
              disabled={isLoading || uploadingFile || (!inputValue.trim() && !selectedFile)}
              className="btn-primary disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
            >
              {uploadingFile ? (
                <>
                  <Loader2 className="animate-spin" size={18} />
                  Uploading...
                </>
              ) : (
                <>
                  <Send size={18} />
                  Send
                </>
              )}
            </button>
          </div>

          {/* File Upload Hint */}
          <div className="mt-2 text-xs text-gray-500 text-center">
            📎 Attach prescription images or documents (JPG, PNG, PDF • Max 10MB)
          </div>
        </form>
      </div>
    </div>
  );
};

export default ChatInterface;