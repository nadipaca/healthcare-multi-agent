import React from 'react';
import ChatInterface from '../components/ChatInterface';

const ChatPage = ({ patient, patientData, onDataUpdate }) => {
  return (
    <div className="max-w-7xl mx-auto px-4 py-6">
      {patient && (
        <div className="bg-gradient-to-r from-blue-50 to-indigo-50 border border-blue-200 rounded-lg p-4 mb-4 shadow-sm">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-blue-800">
                🏥 <strong>Patient:</strong> {patient.first_name} {patient.last_name}
              </p>
              <p className="text-xs text-blue-600 mt-1">
                ID: {patient.patient_id} | DOB: {patient.date_of_birth}
              </p>
            </div>
            {patient.medical_history && (
              <div className="text-xs bg-blue-100 text-blue-700 px-3 py-1 rounded-full">
                📋 {patient.medical_history}
              </div>
            )}
          </div>
        </div>
      )}
      
      <ChatInterface 
        selectedPatient={patient} 
        patientData={patientData}
        onDataUpdate={onDataUpdate}
      />
    </div>
  );
};

export default ChatPage;
