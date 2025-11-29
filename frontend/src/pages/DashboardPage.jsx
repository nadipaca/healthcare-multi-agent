import React, { useState, useEffect } from 'react';
import { analyticsService } from '../services/api';
import { RefreshCw, Activity, Users, Flag, Clock } from 'lucide-react';

const DashboardPage = () => {
  const [data, setData] = useState(null);
  const [timeRange, setTimeRange] = useState(24);
  const [loading, setLoading] = useState(true);
  const [lastUpdated, setLastUpdated] = useState(null);

  const loadDashboard = async () => {
    setLoading(true);
    try {
      const result = await analyticsService.getDashboard(timeRange);
      setData(result);
      setLastUpdated(new Date());
    } catch (error) {
      console.error('Failed to load dashboard:', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadDashboard();
    const interval = setInterval(loadDashboard, 30000); // Auto-refresh every 30s
    return () => clearInterval(interval);
  }, [timeRange]);

  if (loading || !data) {
    return (
      <div className="flex items-center justify-center h-screen bg-gray-50">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary"></div>
      </div>
    );
  }

  const { overview, agent_usage, agent_performance, top_sessions, recent_hitl_flags } = data;

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="bg-gradient-to-r from-primary to-secondary text-white p-8 rounded-lg shadow-lg mb-6">
          <h1 className="text-3xl font-bold mb-2">📊 Analytics Dashboard</h1>
          <p className="opacity-90">Real-time monitoring and performance metrics</p>
        </div>

        {/* Controls */}
        <div className="bg-white p-4 rounded-lg shadow-md mb-6 flex justify-between items-center flex-wrap gap-4">
          <div className="flex items-center gap-4">
            <label className="font-semibold">Time Range:</label>
            <select
              value={timeRange}
              onChange={(e) => setTimeRange(Number(e.target.value))}
              className="px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-primary"
            >
              <option value={1}>Last Hour</option>
              <option value={6}>Last 6 Hours</option>
              <option value={24}>Last 24 Hours</option>
              <option value={168}>Last 7 Days</option>
            </select>
          </div>
          <div className="flex items-center gap-4">
            <span className="text-sm text-gray-500">
              Updated: {lastUpdated?.toLocaleTimeString()}
            </span>
            <button
              onClick={loadDashboard}
              className="flex items-center gap-2 btn-primary"
            >
              <RefreshCw size={18} />
              Refresh
            </button>
          </div>
        </div>

        {/* Overview Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-6">
          <div className="card border-l-4 border-primary">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-500 uppercase mb-1 font-semibold">Total Interactions</p>
                <p className="text-3xl font-bold">{overview.total_interactions}</p>
                <p className="text-xs text-gray-500 mt-1">Last {overview.time_period_hours}h</p>
              </div>
              <Activity className="text-primary" size={40} />
            </div>
          </div>

          <div className="card border-l-4 border-green-500">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-500 uppercase mb-1 font-semibold">Active Sessions</p>
                <p className="text-3xl font-bold">{overview.active_sessions}</p>
                <p className="text-xs text-gray-500 mt-1">Unique users</p>
              </div>
              <Users className="text-green-500" size={40} />
            </div>
          </div>

          <div className="card border-l-4 border-orange-500">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-500 uppercase mb-1 font-semibold">HITL Flags</p>
                <p className="text-3xl font-bold">{overview.hitl_flags}</p>
                <p className="text-xs text-gray-500 mt-1">Requiring review</p>
              </div>
              <Flag className="text-orange-500" size={40} />
            </div>
          </div>

          <div className="card border-l-4 border-blue-500">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-500 uppercase mb-1 font-semibold">Avg Session</p>
                <p className="text-3xl font-bold">{Math.round(overview.avg_session_duration_seconds)}s</p>
                <p className="text-xs text-gray-500 mt-1">Duration</p>
              </div>
              <Clock className="text-blue-500" size={40} />
            </div>
          </div>
        </div>

        {/* Agent Usage */}
        <div className="card mb-6">
          <h2 className="text-xl font-semibold mb-4">Agent Usage & Performance</h2>
          {Object.entries(agent_usage).length > 0 ? (
            Object.entries(agent_usage).map(([agent, calls]) => {
              const maxCalls = Math.max(...Object.values(agent_usage));
              const percentage = (calls / maxCalls) * 100;
              const perf = agent_performance[agent] || {};

              return (
                <div key={agent} className="mb-4">
                  <div className="flex justify-between mb-2">
                    <span className="font-semibold capitalize">{agent.replace(/_/g, ' ')}</span>
                    <span className="text-sm text-gray-600">
                      {calls} calls • {perf.avg_duration_ms?.toFixed(0) || 0}ms avg • ⭐ {perf.avg_rating?.toFixed(1) || 'N/A'}
                    </span>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-8">
                    <div
                      className="bg-gradient-to-r from-primary to-secondary h-8 rounded-full flex items-center px-3 text-white text-sm font-semibold transition-all"
                      style={{ width: `${percentage}%`, minWidth: calls > 0 ? '60px' : '0' }}
                    >
                      {calls} interactions
                    </div>
                  </div>
                </div>
              );
            })
          ) : (
            <p className="text-gray-500">No agent usage data yet</p>
          )}
        </div>

        {/* Top Sessions & HITL Flags */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Top Sessions */}
          <div className="card">
            <h2 className="text-xl font-semibold mb-4">Top Active Sessions</h2>
            {top_sessions && top_sessions.length > 0 ? (
              <div className="space-y-2">
                {top_sessions.map((session, idx) => (
                  <div key={idx} className="p-3 bg-gray-50 rounded-lg flex justify-between">
                    <div>
                      <p className="font-mono text-sm">{session.session_id.substring(0, 20)}...</p>
                      <p className="text-xs text-gray-500">{session.agents_used} agents used</p>
                    </div>
                    <div className="text-right">
                      <p className="font-bold">{session.total_interactions}</p>
                      <p className="text-xs text-gray-500">{session.duration_minutes} min</p>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-gray-500">No sessions yet</p>
            )}
          </div>

          {/* HITL Flags */}
          <div className="card">
            <h2 className="text-xl font-semibold mb-4">Recent HITL Flags 🚩</h2>
            {recent_hitl_flags && recent_hitl_flags.length > 0 ? (
              <div className="space-y-2">
                {recent_hitl_flags.map((flag, idx) => (
                  <div key={idx} className="p-3 bg-orange-50 border border-orange-200 rounded-lg">
                    <div className="flex justify-between items-start mb-1">
                      <span className="text-xs font-semibold text-orange-700 uppercase">{flag.agent}</span>
                      <span className="text-xs text-gray-500">
                        {new Date(flag.timestamp).toLocaleString()}
                      </span>
                    </div>
                    <p className="text-sm text-gray-700">{flag.message_preview}</p>
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-gray-500">No recent HITL flags ✅</p>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default DashboardPage;
