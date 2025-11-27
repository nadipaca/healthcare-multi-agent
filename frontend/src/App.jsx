import React, { useState, useEffect } from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import PatientAuth from './components/PatientAuth';
import NewPatientRegistration from './components/NewPatientRegistration';
import ChatPage from './pages/ChatPage';
import DashboardPage from './pages/DashboardPage';
import Navigation from './components/Navigation';       
import PatientDashboardPage from './pages/PatientDashboardPage';

function App() {
  const [authenticatedPatient, setAuthenticatedPatient] = useState(null);
  const [patientData, setPatientData] = useState(null);
  const [showRegistration, setShowRegistration] = useState(false);

  useEffect(() => {
  const patient = localStorage.getItem('patient');
  const patientData = localStorage.getItem('patientData');
  if (patient) {
    setAuthenticatedPatient(JSON.parse(patient));
  }
  if (patientData) {
    setPatientData(JSON.parse(patientData));
  }
}, []);

    const handlePatientAuthenticated = (patient, response) => {
      setAuthenticatedPatient(patient);
      setPatientData(response);
      // store tokens and patient in localStorage using the actual response object
      localStorage.setItem('access_token', response.access_token);
      localStorage.setItem('refresh_token', response.refresh_token);
      localStorage.setItem('patient', JSON.stringify(response.patient));
      setShowRegistration(false);
    };

  const handleLogout = () => {
    setAuthenticatedPatient(null);
    setPatientData(null);
    setShowRegistration(false);
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    localStorage.removeItem('patient');
    setAuthenticatedPatient(null);
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
          <Route path="/dashboard" element={<PatientDashboardPage />} />
          <Route path="/admin" element={<DashboardPage />} />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </div>
    </BrowserRouter>
  );
}

export default App;