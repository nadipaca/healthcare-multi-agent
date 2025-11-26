import React, { useState } from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import PatientAuth from './components/PatientAuth';
import NewPatientRegistration from './components/NewPatientRegistration';
import ChatPage from './pages/ChatPage';
import DashboardPage from './pages/DashboardPage';
import Navigation from './components/Navigation';

function App() {
  const [authenticatedPatient, setAuthenticatedPatient] = useState(null);
  const [patientData, setPatientData] = useState(null);
  const [showRegistration, setShowRegistration] = useState(false);

  const handlePatientAuthenticated = (patient, fullData) => {
    setAuthenticatedPatient(patient);
    setPatientData(fullData);
    setShowRegistration(false);
  };

  const handleLogout = () => {
    setAuthenticatedPatient(null);
    setPatientData(null);
    setShowRegistration(false);
  };

  // Show registration screen
  if (!authenticatedPatient && showRegistration) {
    return (
      <NewPatientRegistration 
        onComplete={handlePatientAuthenticated}
        onBackToLogin={() => setShowRegistration(false)}
      />
    );
  }

  // Show login screen
  if (!authenticatedPatient) {
    return (
      <PatientAuth 
        onPatientAuthenticated={handlePatientAuthenticated}
        onSwitchToRegister={() => setShowRegistration(true)}
      />
    );
  }

  // Main app for authenticated patients
  return (
    <BrowserRouter>
      <div className="min-h-screen bg-gray-50">
        <Navigation patient={authenticatedPatient} onLogout={handleLogout} />
        <Routes>
          <Route 
            path="/" 
            element={
              <ChatPage 
                patient={authenticatedPatient} 
                patientData={patientData}
                onDataUpdate={setPatientData}
              />
            } 
          />
          <Route path="/dashboard" element={<DashboardPage />} />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </div>
    </BrowserRouter>
  );
}

export default App;