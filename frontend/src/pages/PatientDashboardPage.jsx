// frontend/src/pages/PatientDashboardPage.jsx
import React, { useEffect, useState } from 'react';
import { patientService } from '../services/api';
import { Activity, Calendar, FileText, Shield } from 'lucide-react';

const PatientDashboardPage = () => {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const load = async () => {
      try {
        setLoading(true);
        setError(null);
        const res = await patientService.getCurrentUser(); // /api/patient/me
        setData(res.data); // backend returns { status, data }
      } catch (e) {
        console.error('Failed to load patient dashboard', e);
        setError('Unable to load your health data.');
      } finally {
        setLoading(false);
      }
    };
    load();
  }, []);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-[calc(100vh-64px)] bg-gray-50">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary" />
      </div>
    );
  }

  if (error || !data) {
    return (
      <div className="flex items-center justify-center h-[calc(100vh-64px)] bg-gray-50">
        <p className="text-red-600 text-sm">{error || 'No data available'}</p>
      </div>
    );
  }

  const { patient, prescriptions, appointments, insurance, medical_history, lab_results } = data;

  const nextAppt = appointments && appointments[0];
  const labsCount = lab_results?.length || 0;
  const rxCount = prescriptions?.length || 0;

  return (
    <div className="min-h-[calc(100vh-64px)] bg-gray-50 p-6">
      <div className="max-w-6xl mx-auto space-y-6">
        {/* Header */}
        <div className="bg-gradient-to-r from-primary to-secondary text-white p-6 rounded-lg shadow-lg">
          <h1 className="text-2xl font-bold mb-1">My Health Overview</h1>
          <p className="text-sm opacity-90">
            {patient.first_name} {patient.last_name} &middot; ID: {patient.patient_id}
          </p>
        </div>

        {/* Summary cards */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="card border-l-4 border-primary">
            <div className="flex justify-between items-center">
              <div>
                <p className="text-xs text-gray-500 uppercase mb-1">Active Prescriptions</p>
                <p className="text-2xl font-bold">{rxCount}</p>
              </div>
              <Activity className="text-primary" size={32} />
            </div>
          </div>
          <div className="card border-l-4 border-green-500">
            <div className="flex justify-between items-center">
              <div>
                <p className="text-xs text-gray-500 uppercase mb-1">Upcoming Appointment</p>
                <p className="text-sm font-semibold">
                  {nextAppt
                    ? `${nextAppt.appointment_date.split(' ')[0]} · ${nextAppt.specialty}`
                    : 'None scheduled'}
                </p>
              </div>
              <Calendar className="text-green-500" size={32} />
            </div>
          </div>
          <div className="card border-l-4 border-blue-500">
            <div className="flex justify-between items-center">
              <div>
                <p className="text-xs text-gray-500 uppercase mb-1">Lab Results</p>
                <p className="text-2xl font-bold">{labsCount}</p>
              </div>
              <FileText className="text-blue-500" size={32} />
            </div>
          </div>
        </div>

        {/* Insurance + history */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="card">
            <div className="flex items-center gap-2 mb-3">
              <Shield className="text-primary" size={18} />
              <h2 className="text-sm font-semibold">Insurance</h2>
            </div>
            {insurance ? (
              <div className="text-sm space-y-1">
                <p className="font-medium">{insurance.provider}</p>
                <p>Policy: {insurance.policy_number}</p>
                <p>Status: <span className="font-semibold">{insurance.coverage_status}</span></p>
                <p>Copay (Primary): ${insurance.copay_primary}</p>
                <p>Deductible: ${insurance.deductible} (met: ${insurance.deductible_met})</p>
              </div>
            ) : (
              <p className="text-sm text-gray-500">No insurance on file.</p>
            )}
          </div>

          <div className="card">
            <h2 className="text-sm font-semibold mb-3">Medical Conditions</h2>
            {medical_history && medical_history.length > 0 ? (
              <ul className="text-sm space-y-1 max-h-40 overflow-auto">
                {medical_history.map((h) => (
                  <li key={h.history_id}>
                    <span className="font-medium">{h.condition}</span> &middot; {h.status}
                    {h.diagnosed_date && ` · since ${h.diagnosed_date}`}
                  </li>
                ))}
              </ul>
            ) : (
              <p className="text-sm text-gray-500">No medical history recorded.</p>
            )}
          </div>
        </div>

        {/* Lab results table (compact) */}
        <div className="card">
          <div className="flex justify-between items-center mb-3">
            <h2 className="text-sm font-semibold">Recent Lab Results</h2>
          </div>
          {lab_results && lab_results.length > 0 ? (
            <table className="w-full text-sm">
              <thead className="text-xs text-gray-500 border-b">
                <tr>
                  <th className="text-left py-2">Test</th>
                  <th className="text-left py-2">Result</th>
                  <th className="text-left py-2">Reference</th>
                  <th className="text-left py-2">Date</th>
                </tr>
              </thead>
              <tbody>
                {lab_results.slice(0, 5).map((lab) => (
                  <tr key={lab.lab_id} className="border-b last:border-0">
                    <td className="py-2">{lab.test_name}</td>
                    <td className="py-2">
                      {lab.result_value} {lab.unit}
                    </td>
                    <td className="py-2">{lab.reference_range}</td>
                    <td className="py-2">{lab.test_date}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          ) : (
            <p className="text-sm text-gray-500">No lab results yet.</p>
          )}
        </div>
      </div>
    </div>
  );
};

export default PatientDashboardPage;
