import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { User, FileText, Calendar, Shield, Activity, TestTube } from 'lucide-react';

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const PatientSelector = ({ onPatientSelect }) => {
  const [patients, setPatients] = useState([]);
  const [selectedPatient, setSelectedPatient] = useState(null);
  const [patientData, setPatientData] = useState(null);
  const [scenarios, setScenarios] = useState([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    fetchPatients();
    fetchScenarios();
  }, []);

  const fetchPatients = async () => {
    try {
      const response = await axios.get(`${API_BASE}/api/testing/patients`);
      setPatients(response.data.patients);
    } catch (error) {
      console.error('Error fetching patients:', error);
    }
  };

  const fetchScenarios = async () => {
    try {
      const response = await axios.get(`${API_BASE}/api/testing/scenarios`);
      setScenarios(response.data.scenarios);
    } catch (error) {
      console.error('Error fetching scenarios:', error);
    }
  };

  const selectPatient = async (patientId) => {
    setLoading(true);
    try {
      // Select patient for session
      const selectResponse = await axios.post(`${API_BASE}/api/testing/select-patient`, {
        patient_id: patientId
      });

      // Get full patient data
      const dataResponse = await axios.get(`${API_BASE}/api/testing/patient/${patientId}`);
      
      setSelectedPatient(selectResponse.data.patient);
      setPatientData(dataResponse.data.data);
      
      // Notify parent component
      if (onPatientSelect) {
        onPatientSelect(selectResponse.data.patient, dataResponse.data.data);
      }
    } catch (error) {
      console.error('Error selecting patient:', error);
      alert('Failed to select patient');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="bg-white rounded-lg shadow-lg p-6 mb-6">
      <h2 className="text-2xl font-bold mb-4 text-gray-800">🧪 Testing Dashboard</h2>
      
      {/* Patient Selection */}
      <div className="mb-6">
        <h3 className="text-lg font-semibold mb-3 text-gray-700">Select Test Patient:</h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {patients.map((patient) => (
            <button
              key={patient.patient_id}
              onClick={() => selectPatient(patient.patient_id)}
              disabled={loading}
              className={`p-4 border-2 rounded-lg text-left transition-all ${
                selectedPatient?.patient_id === patient.patient_id
                  ? 'border-blue-500 bg-blue-50'
                  : 'border-gray-200 hover:border-blue-300 hover:bg-gray-50'
              } ${loading ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer'}`}
            >
              <div className="flex items-center gap-3 mb-2">
                <User className="text-blue-600" size={24} />
                <div>
                  <p className="font-bold text-gray-800">
                    {patient.first_name} {patient.last_name}
                  </p>
                  <p className="text-sm text-gray-600">{patient.patient_id}</p>
                </div>
              </div>
              <p className="text-xs text-gray-500 mt-2">{patient.medical_history}</p>
            </button>
          ))}
        </div>
      </div>

      {/* Selected Patient Data */}
      {selectedPatient && patientData && (
        <div className="border-t pt-6">
          <h3 className="text-lg font-semibold mb-4 text-gray-700">
            Patient Data Overview:
          </h3>
          
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {/* Prescriptions */}
            <div className="bg-blue-50 p-4 rounded-lg">
              <div className="flex items-center gap-2 mb-2">
                <FileText className="text-blue-600" size={20} />
                <h4 className="font-semibold text-blue-900">Prescriptions</h4>
              </div>
              <p className="text-2xl font-bold text-blue-700">
                {patientData.prescriptions.length}
              </p>
              <p className="text-sm text-blue-600">
                {patientData.prescriptions.filter(p => p.needs_renewal).length} need renewal
              </p>
            </div>

            {/* Appointments */}
            <div className="bg-green-50 p-4 rounded-lg">
              <div className="flex items-center gap-2 mb-2">
                <Calendar className="text-green-600" size={20} />
                <h4 className="font-semibold text-green-900">Appointments</h4>
              </div>
              <p className="text-2xl font-bold text-green-700">
                {patientData.appointments.length}
              </p>
              <p className="text-sm text-green-600">Upcoming visits</p>
            </div>

            {/* Insurance */}
            <div className="bg-purple-50 p-4 rounded-lg">
              <div className="flex items-center gap-2 mb-2">
                <Shield className="text-purple-600" size={20} />
                <h4 className="font-semibold text-purple-900">Insurance</h4>
              </div>
              <p className="text-lg font-bold text-purple-700">
                {patientData.insurance?.provider || 'None'}
              </p>
              <p className="text-sm text-purple-600">
                ${patientData.insurance?.copay_primary || 0} copay
              </p>
            </div>

            {/* Medical History */}
            <div className="bg-orange-50 p-4 rounded-lg">
              <div className="flex items-center gap-2 mb-2">
                <Activity className="text-orange-600" size={20} />
                <h4 className="font-semibold text-orange-900">Conditions</h4>
              </div>
              <p className="text-2xl font-bold text-orange-700">
                {patientData.medical_history.length}
              </p>
              <p className="text-sm text-orange-600">Active conditions</p>
            </div>

            {/* Lab Results */}
            <div className="bg-pink-50 p-4 rounded-lg">
              <div className="flex items-center gap-2 mb-2">
                <TestTube className="text-pink-600" size={20} />
                <h4 className="font-semibold text-pink-900">Lab Results</h4>
              </div>
              <p className="text-2xl font-bold text-pink-700">
                {patientData.lab_results.length}
              </p>
              <p className="text-sm text-pink-600">Recent tests</p>
            </div>
          </div>
        </div>
      )}

      {/* Test Scenarios */}
      {selectedPatient && (
        <div className="border-t pt-6 mt-6">
          <h3 className="text-lg font-semibold mb-4 text-gray-700">
            🎯 Suggested Test Scenarios:
          </h3>
          <div className="space-y-3">
            {scenarios.map((scenario, idx) => (
              <div key={idx} className="bg-gray-50 p-4 rounded-lg border border-gray-200">
                <div className="flex justify-between items-start mb-2">
                  <h4 className="font-semibold text-gray-800">{scenario.agent}</h4>
                  <span className="text-xs bg-blue-100 text-blue-700 px-2 py-1 rounded">
                    {scenario.patient}
                  </span>
                </div>
                <p className="text-sm text-gray-600 mb-2">{scenario.scenario}</p>
                <div className="bg-white p-3 rounded border border-gray-200 mb-2">
                  <p className="text-sm font-mono text-gray-700">
                    💬 "{scenario.test_message}"
                  </p>
                </div>
                <p className="text-xs text-gray-500">
                  Expected: {scenario.expected_flow}
                </p>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default PatientSelector;
