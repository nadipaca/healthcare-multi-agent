import React, { useState } from 'react';
import axios from 'axios';
import { User, Mail, Phone, Loader2 } from 'lucide-react';

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const PatientAuth = ({ onPatientAuthenticated }) => {
  const [authMethod, setAuthMethod] = useState('email'); // email, phone, or patient_id
  const [inputValue, setInputValue] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleAuthenticate = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      const response = await axios.post(`${API_BASE}/api/patient/authenticate`, {
        auth_method: authMethod,
        identifier: inputValue
      });

      if (response.data.status === 'success') {
        onPatientAuthenticated(response.data.patient, response.data.full_data);
      } else if (response.data.status === 'new_patient') {
        // New patient - trigger registration flow
        onPatientAuthenticated(null, null, { 
          isNew: true, 
          identifier: inputValue,
          method: authMethod 
        });
      }
    } catch (err) {
      setError(err.response?.data?.detail || 'Authentication failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center p-4">
      <div className="bg-white rounded-2xl shadow-2xl p-8 w-full max-w-md">
        <div className="text-center mb-8">
          <div className="bg-gradient-to-r from-blue-600 to-indigo-600 w-16 h-16 rounded-full flex items-center justify-center mx-auto mb-4">
            <User className="text-white" size={32} />
          </div>
          <h1 className="text-3xl font-bold text-gray-800">Healthcare Assistant</h1>
          <p className="text-gray-600 mt-2">Sign in to access your medical records</p>
        </div>

        <form onSubmit={handleAuthenticate} className="space-y-6">
          {/* Auth Method Selector */}
          <div className="flex gap-2 mb-4">
            <button
              type="button"
              onClick={() => setAuthMethod('email')}
              className={`flex-1 py-2 px-4 rounded-lg font-medium transition-colors ${
                authMethod === 'email'
                  ? 'bg-blue-600 text-white'
                  : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
              }`}
            >
              <Mail size={18} className="inline mr-2" />
              Email
            </button>
            <button
              type="button"
              onClick={() => setAuthMethod('phone')}
              className={`flex-1 py-2 px-4 rounded-lg font-medium transition-colors ${
                authMethod === 'phone'
                  ? 'bg-blue-600 text-white'
                  : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
              }`}
            >
              <Phone size={18} className="inline mr-2" />
              Phone
            </button>
            <button
              type="button"
              onClick={() => setAuthMethod('patient_id')}
              className={`flex-1 py-2 px-4 rounded-lg font-medium transition-colors ${
                authMethod === 'patient_id'
                  ? 'bg-blue-600 text-white'
                  : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
              }`}
            >
              <User size={18} className="inline mr-2" />
              ID
            </button>
          </div>

          {/* Input Field */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              {authMethod === 'email' && 'Email Address'}
              {authMethod === 'phone' && 'Phone Number'}
              {authMethod === 'patient_id' && 'Patient ID'}
            </label>
            <input
              type={authMethod === 'email' ? 'email' : 'text'}
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
              placeholder={
                authMethod === 'email' ? 'john.doe@email.com' :
                authMethod === 'phone' ? '555-0101' :
                'PAT001'
              }
              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              required
            />
          </div>

          {error && (
            <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg">
              {error}
            </div>
          )}

          <button
            type="submit"
            disabled={loading || !inputValue.trim()}
            className="w-full bg-gradient-to-r from-blue-600 to-indigo-600 text-white py-3 rounded-lg font-semibold hover:from-blue-700 hover:to-indigo-700 transition-all disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
          >
            {loading ? (
              <>
                <Loader2 className="animate-spin" size={20} />
                Authenticating...
              </>
            ) : (
              'Continue'
            )}
          </button>
        </form>

        <div className="mt-6 text-center text-sm text-gray-600">
          <p>New patient? Don't worry, we'll create your record automatically.</p>
        </div>
      </div>
    </div>
  );
};

export default PatientAuth;