import React, { useState } from 'react';
import ChatInterface from '../components/ChatInterface';
import ChatHistorySidebar from '../components/ChatHistorySidebar';
import { Menu, X } from 'lucide-react';
import api from '../services/api';

const ChatPage = ({ patient, patientData, onDataUpdate }) => {
  const [currentSessionId, setCurrentSessionId] = useState(null);
  const [loadedMessages, setLoadedMessages] = useState([]);
  const [isSidebarOpen, setIsSidebarOpen] = useState(false); // Closed by default

  const handleSelectSession = async (sessionId) => {
    try {
      const response = await api.get(`/api/chat/session/${sessionId}/messages`);
      setLoadedMessages(response.data.messages);
      setCurrentSessionId(sessionId);
      // Don't close sidebar on desktop, only on mobile
      if (window.innerWidth < 1024) {
        setIsSidebarOpen(false);
      }
    } catch (error) {
      console.error('Failed to load session:', error);
      alert('Failed to load conversation');
    }
  };

  const handleNewSession = () => {
    setCurrentSessionId(null);
    setLoadedMessages([]);
    // Don't close sidebar on desktop, only on mobile
    if (window.innerWidth < 1024) {
      setIsSidebarOpen(false);
    }
  };

  const toggleSidebar = () => {
    setIsSidebarOpen(!isSidebarOpen);
  };

  return (
    <div className="flex h-[calc(100vh-64px)] overflow-hidden">
      {/* Mobile Overlay - only shows on mobile when sidebar is open */}
      {isSidebarOpen && (
        <div
          className="fixed inset-0 bg-black bg-opacity-50 z-40 lg:hidden"
          onClick={() => setIsSidebarOpen(false)}
        />
      )}

      {/* Chat History Sidebar - Collapsible */}
      <div
        className={`
          transition-all duration-300 ease-in-out
          bg-white border-r border-gray-200 flex-shrink-0
          ${isSidebarOpen ? 'w-80' : 'w-0'}
          overflow-hidden
          relative z-50
        `}
      >
        <div className="w-80 h-full">
          <ChatHistorySidebar
            currentSessionId={currentSessionId}
            onSelectSession={handleSelectSession}
            onNewSession={handleNewSession}
            onClose={() => setIsSidebarOpen(false)}
            isOpen={isSidebarOpen}
          />
        </div>
      </div>

      {/* Main Chat Area */}
      <div className="flex-1 flex flex-col min-w-0 overflow-hidden">
        {/* Hamburger Menu & Patient Info Header */}
        <div className="bg-gradient-to-r from-blue-50 to-indigo-50 border-b border-blue-200 shadow-sm flex-shrink-0">
          <div className="flex items-center gap-4 p-4">
            {/* Hamburger Button */}
            <button
              onClick={toggleSidebar}
              className="p-2 hover:bg-blue-100 rounded-lg transition-colors flex-shrink-0"
              aria-label="Toggle sidebar"
              title={isSidebarOpen ? "Hide chat history" : "Show chat history"}
            >
              {isSidebarOpen ? (
                <X size={24} className="text-blue-700" />
              ) : (
                <Menu size={24} className="text-blue-700" />
              )}
            </button>

            {/* Patient Info */}
            {patient && (
              <div className="flex items-center justify-between flex-1 min-w-0">
                <div className="min-w-0 flex-1">
                  <p className="text-sm text-blue-800 truncate">
                    🏥 <strong>Patient:</strong> {patient.first_name} {patient.last_name}
                  </p>
                  <p className="text-xs text-blue-600 mt-1 truncate">
                    ID: {patient.patient_id} | DOB: {patient.date_of_birth}
                  </p>
                </div>
                {patient.medical_history && (
                  <div className="hidden md:block text-xs bg-blue-100 text-blue-700 px-3 py-1 rounded-full ml-4 flex-shrink-0">
                    📋 {patient.medical_history}
                  </div>
                )}
              </div>
            )}
          </div>
        </div>

        {/* Chat Interface */}
        <div className="flex-1 overflow-hidden">
          <ChatInterface
            selectedPatient={patient}
            patientData={patientData}
            onDataUpdate={onDataUpdate}
            sessionId={currentSessionId}
            initialMessages={loadedMessages}
          />
        </div>
      </div>
    </div>
  );
};

export default ChatPage;