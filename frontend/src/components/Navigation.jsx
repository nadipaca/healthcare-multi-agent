import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import { LogOut, User, MessageSquare, LayoutDashboard } from 'lucide-react';

const Navigation = ({ patient, onLogout }) => {
  const location = useLocation();
  const isAdmin = patient?.role === 'admin';

  const isActive = (path) => {
    return location.pathname === path;
  };

  return (
    <nav className="bg-white shadow-md border-b">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between h-16">
          {/* Left side - Logo and Nav */}
          <div className="flex">
            <div className="flex-shrink-0 flex items-center">
              <h1 className="text-xl font-bold text-blue-600">🏥 Healthcare Assistant</h1>
            </div>
            <div className="flex items-center sm:ml-6 sm:flex sm:space-x-4">
              <Link
                to="/"
                className={`inline-flex items-center px-3 py-2 text-sm font-medium rounded-md ${isActive('/')
                    ? 'bg-blue-50 text-blue-700'
                    : 'text-gray-700 hover:bg-gray-50'
                  }`}
              >
                <MessageSquare size={18} className="mr-2" />
                Chat
              </Link>
              {/* Patient vs admin dashboard link */}
              {!isAdmin && (
                <Link
                  to="/dashboard"
                  className={`inline-flex items-center px-3 py-2 text-sm font-medium rounded-md ${isActive('/dashboard') ? 'bg-blue-50 text-blue-700' : 'text-gray-700 hover:bg-gray-50'
                    }`}
                >
                  <LayoutDashboard size={18} className="mr-2" />
                  My Health
                </Link>
              )}
              {isAdmin && (
                <Link
                  to="/admin"
                  className={`inline-flex items-center px-3 py-2 text-sm font-medium rounded-md ${isActive('/admin') ? 'bg-blue-50 text-blue-700' : 'text-gray-700 hover:bg-gray-50'
                    }`}
                >
                  <LayoutDashboard size={18} className="mr-2" />
                  Analytics
                </Link>
              )}
            </div>
          </div>

          {/* Right side - User info and logout */}
          <div className="flex items-center">
            {patient && (
              <div className="flex items-center gap-4">
                <div className="flex items-center gap-2 bg-blue-50 px-3 py-2 rounded-lg">
                  <User size={18} className="text-blue-600" />
                  <div className="text-sm">
                    <p className="font-medium text-gray-900">
                      {patient.first_name} {patient.last_name}
                    </p>
                    <p className="text-xs text-gray-500">{patient.patient_id}</p>
                  </div>
                </div>
                <button
                  onClick={onLogout}
                  className="flex items-center gap-2 px-4 py-2 text-sm font-medium text-red-700 hover:bg-red-50 rounded-lg transition-colors"
                >
                  <LogOut size={18} />
                  Logout
                </button>
              </div>
            )}
          </div>
        </div>
      </div>
    </nav>
  );
};

export default Navigation;
