import React, { useState, useEffect, useRef } from 'react';
import { MessageSquare, Trash2, Plus, Clock, X } from 'lucide-react';
import api from '../services/api';

const ChatHistorySidebar = ({ currentSessionId, onSelectSession, onNewSession, onClose, isOpen }) => {
  const [sessions, setSessions] = useState([]);
  const [loading, setLoading] = useState(false);

 const mountedRef = useRef(false);

useEffect(() => {
  // load once on mount
  loadSessions();
  mountedRef.current = true;
}, []);

useEffect(() => {
  // if it's a subsequent open (not the initial mount), reload
  if (isOpen && mountedRef.current) {
    loadSessions();
  }
}, [isOpen]);

  const loadSessions = async () => {
    setLoading(true);
    try {
      // Avoid making unauthenticated requests from the sidebar.
      const token = localStorage.getItem('access_token');
      if (!token) {
        // No token -> nothing to load. Show empty state and stop.
        setSessions([]);
        setLoading(false);
        return;
      }
      const response = await api.get('/api/chat/sessions?limit=5');
      setSessions(response.data.sessions);
    } catch (error) {
      // Handle auth errors gracefully: if the token is invalid or missing on the server
      // side, show an empty state and prompt the user to sign in rather than spamming logs.
      if (error.response && (error.response.status === 401 || error.response.status === 403)) {
        console.warn('Chat history request unauthorized; user may be logged out.');
        // Clear stored tokens (optional) so UI reflects logged-out state
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        setSessions([]);
      } else {
        console.error('Failed to load chat history:', error);
      }
    } finally {
      setLoading(false);
    }
  };

  const handleDeleteSession = async (sessionId, e) => {
    e.stopPropagation();

    if (!confirm('Delete this conversation?')) return;

    try {
      await api.delete(`/api/chat/session/${sessionId}`);
      setSessions(prev => prev.filter(s => s.session_id !== sessionId));

      if (sessionId === currentSessionId) {
        onNewSession();
      }
    } catch (error) {
      console.error('Failed to delete session:', error);
      alert('Failed to delete conversation');
    }
  };

  const formatTimestamp = (timestamp) => {
    const date = new Date(timestamp);
    const now = new Date();
    const diffMs = now - date;
    const diffMins = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMs / 3600000);
    const diffDays = Math.floor(diffMs / 86400000);

    if (diffMins < 1) return 'Just now';
    if (diffMins < 60) return `${diffMins}m ago`;
    if (diffHours < 24) return `${diffHours}h ago`;
    if (diffDays < 7) return `${diffDays}d ago`;
    return date.toLocaleDateString();
  };

  return (
    <div className="h-full flex flex-col bg-white">
      {/* Header */}
      <div className="p-4 border-b border-gray-200 flex-shrink-0">
        <div className="flex items-center justify-between mb-3">
          <h2 className="text-lg font-bold text-gray-800">Chat History</h2>
          <button
            onClick={onClose}
            className="lg:hidden p-1 hover:bg-gray-100 rounded-lg transition-colors"
            aria-label="Close sidebar"
          >
            <X size={20} className="text-gray-600" />
          </button>
        </div>

        <button
          onClick={onNewSession}
          className="w-full bg-gradient-to-r from-blue-600 to-indigo-600 text-white py-3 rounded-lg font-semibold hover:from-blue-700 hover:to-indigo-700 transition-all flex items-center justify-center gap-2 shadow-md hover:shadow-lg"
        >
          <Plus size={20} />
          New Conversation
        </button>
      </div>

      {/* Sessions List */}
      <div className="flex-1 overflow-y-auto">
        <div className="p-4">
          <h3 className="text-xs font-semibold text-gray-500 uppercase mb-3 flex items-center gap-2">
            <MessageSquare size={14} />
            Recent Conversations
          </h3>

          {loading ? (
            <div className="text-center py-8">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto"></div>
              <p className="text-sm text-gray-500 mt-2">Loading...</p>
            </div>
          ) : sessions.length === 0 ? (
            <div className="text-center py-8 text-gray-500">
              <MessageSquare className="mx-auto mb-2 text-gray-400" size={48} />
              <p className="text-sm font-medium">No chat history yet</p>
              <p className="text-xs mt-1">Start a new conversation!</p>
            </div>
          ) : (
            <div className="space-y-2">
              {sessions.map((session) => (
                <div
                  key={session.session_id}
                  onClick={() => onSelectSession(session.session_id)}
                  className={`group p-3 rounded-lg cursor-pointer transition-all ${
                    currentSessionId === session.session_id
                      ? 'bg-blue-50 border-2 border-blue-500 shadow-sm'
                      : 'bg-gray-50 hover:bg-gray-100 border-2 border-transparent hover:border-gray-300'
                  }`}
                >
                  <div className="flex items-start justify-between gap-2">
                    <div className="flex-1 min-w-0">
                      <p className="text-sm font-medium text-gray-900 truncate">
                        {session.title || 'New Conversation'}
                      </p>
                      <div className="flex items-center gap-2 mt-1">
                        <p className="text-xs text-gray-500 flex items-center gap-1">
                          <Clock size={12} />
                          {formatTimestamp(session.last_message_at)}
                        </p>
                        <span className="text-xs text-gray-400">•</span>
                        <p className="text-xs text-gray-500">
                          {session.message_count} {session.message_count === 1 ? 'message' : 'messages'}
                        </p>
                      </div>
                    </div>

                    <button
                      onClick={(e) => handleDeleteSession(session.session_id, e)}
                      className="opacity-0 group-hover:opacity-100 transition-opacity p-1 hover:bg-red-100 rounded flex-shrink-0"
                      title="Delete conversation"
                    >
                      <Trash2 size={16} className="text-red-600" />
                    </button>
                  </div>

                  {session.first_message && (
                    <p className="text-xs text-gray-600 mt-2 line-clamp-2 leading-relaxed">
                      "{session.first_message}"
                    </p>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>
      </div>

      {/* Footer Info */}
      <div className="p-4 border-t border-gray-200 bg-gray-50 flex-shrink-0">
        <p className="text-xs text-gray-500 text-center">
          📝 Showing last 5 conversations
        </p>
        <button
          onClick={loadSessions}
          className="w-full mt-2 text-xs text-blue-600 hover:text-blue-700 font-medium"
        >
          Refresh History
        </button>
      </div>
    </div>
  );
};

export default ChatHistorySidebar;