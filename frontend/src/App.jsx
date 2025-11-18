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
  const [isNewPatient, setIsNewPatient] = useState(false);

  const handlePatientAuthenticated = (patient, fullData, newPatientInfo) => {
    if (newPatientInfo?.isNew) {
      // Handle new patient registration
      setIsNewPatient(true);
      // You could show a registration form here
    } else {
      setAuthenticatedPatient(patient);
      setPatientData(fullData);
      setIsNewPatient(false);
    }
  };

  const handleLogout = () => {
    setAuthenticatedPatient(null);
    setPatientData(null);
    setIsNewPatient(false);
  };

  // Show authentication screen if not logged in
  if (!authenticatedPatient && !isNewPatient) {
    return <PatientAuth onPatientAuthenticated={handlePatientAuthenticated} />;
  }

  // Show registration flow for new patients
  if (isNewPatient) {
    return (
      <NewPatientRegistration 
        onComplete={(patient, data) => {
          setAuthenticatedPatient(patient);
          setPatientData(data);
          setIsNewPatient(false);
        }}
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