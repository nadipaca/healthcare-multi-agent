import React, { useEffect, useRef, useState } from 'react';
import { patientService, fileService } from '../services/api';
import { Activity, Calendar, FileText, Shield } from 'lucide-react';

const specialties = [
  'General Practitioner',
  'Cardiology',
  'Neurology',
  'Orthopedics',
  'Dermatology',
  'Endocrinology',
  'Gastroenterology',
  'Pulmonology',
  'Psychiatry',
  'Gynecology',
];

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const PatientDashboardPage = () => {
  const [data, setData] = useState(null);
  const [showForm, setShowForm] = useState(false);
  const [formValues, setFormValues] = useState({
    date: '',
    time: '',
    reason: '',
    specialty: specialties[0],
  });
  const [formLoading, setFormLoading] = useState(false);
  const [formError, setFormError] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [files, setFiles] = useState([]);
  const [filesLoading, setFilesLoading] = useState(true);
  const [selectedTab, setSelectedTab] = useState('prescriptions');
  const [prescripDocs, setPrescripDocs] = useState([]);

  const patientId = data?.patient?.patient_id;

  useEffect(() => {
    const load = async () => {
      try {
        setLoading(true);
        setError(null);
        const res = await patientService.getCurrentUser();
        setData(res.data);
      } catch (e) {
        setError('Unable to load your health data.');
      } finally {
        setLoading(false);
      }
    };
    load();
  }, []);

  useEffect(() => {
    const loadFiles = async () => {
      if (!patientId) return;
      try {
        setFilesLoading(true);
        const res = await fileService.getPatientFiles(patientId);
        setFiles(res.files || []);
      } finally {
        setFilesLoading(false);
      }
    };
    loadFiles();
  }, [patientId]);

  // Split files by type
  const prescriptionDocs = files.filter(
    (f) => f.category === 'prescription' || f.document_type === 'prescription'
  );
  const labDocs = files.filter(
    (f) => f.category === 'lab_result' || f.document_type === 'lab_result'
  );

  // Remove medical conditions and manual lab result forms
  // Remove mhForm, mhLoading, handleMhChange, handleMhSubmit, labForm, labLoading, handleLabChange, handleLabSubmit

  const handleFormChange = (e) => {
    const { name, value } = e.target;
    setFormValues((prev) => ({ ...prev, [name]: value }));
  };

  const handleFormSubmit = async (e) => {
    e.preventDefault();
    setFormLoading(true);
    setFormError(null);
    try {
      const payload = {
        date: `${formValues.date} ${formValues.time}`,
        reason: formValues.reason,
        specialty: formValues.specialty,
      };
      await patientService.createAppointment(payload);
      setShowForm(false);
      setFormValues({
        date: '',
        time: '',
        reason: '',
        specialty: specialties[0],
      });
      // Refresh dashboard data
      const res = await patientService.getCurrentUser();
      setData(res.data);
    } catch (err) {
      setFormError('Failed to create appointment.');
    } finally {
      setFormLoading(false);
    }
  };

  useEffect(() => {
    const loadPrescriptionDocs = async () => {
      if (!patientId) return;
      try {
        const res = await fileService.getPrescriptionFiles(patientId);
        setPrescripDocs(res.files || []);
      } catch (e) {
        console.error('Failed to load prescription docs', e);
      }
    };

    loadPrescriptionDocs();
  }, [patientId]);


  if (loading || !data) {
    return (
      <div className="flex items-center justify-center h-[calc(100vh-64px)] bg-gray-50">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary"></div>
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
  const rxCount = prescripDocs?.length || 0;
  const apptCount = appointments?.length || 0;
  const labsCount = labDocs.length || 0;

  // Filter future appointments
  const now = new Date();
  const futureAppointments = (appointments || []).filter((a) => {
    if (!a.appointment_date) return false;
    return new Date(a.appointment_date) >= now;
  });

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

        {/* Summary cards - now select tab */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div
            className={`card border-l-4 border-primary cursor-pointer hover:shadow-md transition-shadow ${selectedTab === 'prescriptions' ? 'ring-2 ring-primary' : ''
              }`}
            onClick={() => setSelectedTab('prescriptions')}
          >
            <div className="flex justify-between items-center">
              <div>
                <p className="text-xs text-gray-500 uppercase mb-1">Active Prescriptions</p>
                <p className="text-2xl font-bold">{rxCount}</p>
              </div>
              <Activity className="text-primary" size={32} />
            </div>
          </div>
          <div
            className={`card border-l-4 border-green-500 cursor-pointer hover:shadow-md transition-shadow ${selectedTab === 'appointments' ? 'ring-2 ring-green-500' : ''
              }`}
            onClick={() => setSelectedTab('appointments')}
          >
            <div className="flex justify-between items-center">
              <div>
                <p className="text-xs text-gray-500 uppercase mb-1">Appointments</p>
                <p className="text-2xl font-bold">{apptCount}</p>
              </div>
              <Calendar className="text-green-500" size={32} />
            </div>
          </div>
          <div
            className={`card border-l-4 border-blue-500 cursor-pointer hover:shadow-md transition-shadow ${selectedTab === 'labs' ? 'ring-2 ring-blue-500' : ''
              }`}
            onClick={() => setSelectedTab('labs')}
          >
            <div className="flex justify-between items-center">
              <div>
                <p className="text-xs text-gray-500 uppercase mb-1">Lab Results</p>
                <p className="text-2xl font-bold">{labsCount}</p>
              </div>
              <FileText className="text-blue-500" size={32} />
            </div>
          </div>
        </div>

        {/* Tab bar */}
        <div className="mt-4 border-b flex gap-4 text-sm">
          {['prescriptions', 'appointments', 'labs'].map((tab) => {
            const label =
              tab === 'prescriptions'
                ? 'Prescriptions'
                : tab === 'appointments'
                  ? 'Appointments'
                  : 'Lab Results';

            return (
              <button
                key={tab}
                type="button"
                onClick={() => setSelectedTab(tab)}
                className={`pb-2 border-b-2 -mb-px ${selectedTab === tab
                  ? 'border-primary text-primary font-semibold'
                  : 'border-transparent text-gray-600 hover:text-primary'
                  }`}
              >
                {label}
              </button>
            );
          })}
        </div>

        {/* Details section per tab */}
        <div className="mt-4">
          {/* Prescriptions tab */}
          {selectedTab === 'prescriptions' && (
            <div className="card">
              <div className="flex justify-between items-center mb-3">
                <h2 className="text-sm font-semibold">Prescriptions</h2>
                <label className="btn-primary text-xs px-3 py-1 rounded cursor-pointer">
                  Upload prescription
                  <input
                    type="file"
                    accept="application/pdf,image/*"
                    className="hidden"
                    onChange={async (e) => {
                      const file = e.target.files?.[0];
                      if (!file) return;
                      try {
                        await fileService.uploadPrescription(file, null, 'Uploaded from dashboard');
                        const [presRes, meRes] = await Promise.all([
                          fileService.getPrescriptionFiles(patientId),
                          patientService.getCurrentUser(),
                        ]);
                        setPrescriptionDocs(presRes.files || []);
                        setData(meRes.data);
                      } catch (err) {
                        alert('Failed to upload prescription');
                      } finally {
                        e.target.value = '';
                      }
                    }}
                  />
                </label>
              </div>

              {prescripDocs.length > 0 ? (
                <ul className="space-y-2 text-sm">
                  {prescripDocs.map((doc) => (
                    <li
                      key={doc.file_id}
                      className="flex justify-between items-center bg-gray-50 px-3 py-2 rounded"
                    >
                      <div>
                        <div className="font-medium">{doc.file_name}</div>
                        <div className="text-xs text-gray-500">
                          Uploaded {doc.uploaded_at && new Date(doc.uploaded_at).toLocaleString()}
                        </div>
                      </div>
                      <button
                        type="button"
                        className="text-xs text-blue-600 hover:underline"
                        onClick={() => fileService.downloadPrescriptionFile(doc.file_id, doc.file_name)}
                      >
                        Download
                      </button>
                    </li>
                  ))}
                </ul>
              ) : (
                <p className="text-sm text-gray-500">No prescriptions uploaded yet.</p>
              )}
            </div>
          )}


          {/* Appointments tab */}
          {selectedTab === 'appointments' && (
            <div className="card">
              <div className="flex justify-between items-center mb-3">
                <h2 className="text-sm font-semibold">Upcoming Appointments</h2>
              </div>
              {futureAppointments.length > 0 ? (
                <ul className="space-y-2 text-sm mb-4">
                  {futureAppointments.map((appt) => (
                    <li
                      key={appt.appointment_id}
                      className="flex justify-between items-center bg-gray-50 px-3 py-2 rounded"
                    >
                      <div>
                        <div className="font-medium">
                          {appt.appointment_date} · {appt.specialty}
                        </div>
                        <div className="text-xs text-gray-500">
                          {appt.doctor_name} · {appt.location}
                        </div>
                      </div>
                      <span className="text-xs capitalize text-gray-600">{appt.status}</span>
                    </li>
                  ))}
                </ul>
              ) : (
                <p className="text-sm text-gray-500 mb-4">No upcoming appointments.</p>
              )}
              {/* Booking form */}
              <form
                onSubmit={handleFormSubmit}
                className="mt-2 bg-white p-4 rounded shadow flex flex-col gap-3 max-w-md"
              >
                <div>
                  <label className="block text-sm font-medium mb-1">Date</label>
                  <input
                    type="date"
                    name="date"
                    value={formValues.date}
                    onChange={handleFormChange}
                    required
                    className="border px-3 py-2 rounded w-full"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium mb-1">Time</label>
                  <input
                    type="time"
                    name="time"
                    value={formValues.time}
                    onChange={handleFormChange}
                    required
                    className="border px-3 py-2 rounded w-full"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium mb-1">Specialty</label>
                  <select
                    name="specialty"
                    value={formValues.specialty}
                    onChange={handleFormChange}
                    className="border px-3 py-2 rounded w-full"
                  >
                    {specialties.map((s) => (
                      <option key={s} value={s}>{s}</option>
                    ))}
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-medium mb-1">Reason</label>
                  <input
                    type="text"
                    name="reason"
                    value={formValues.reason}
                    onChange={handleFormChange}
                    required
                    className="border px-3 py-2 rounded w-full"
                    placeholder="Reason for visit"
                  />
                </div>
                {formError && (
                  <div className="text-red-600 text-sm">{formError}</div>
                )}
                <button
                  type="submit"
                  className="btn-primary px-4 py-2 rounded mt-2"
                  disabled={formLoading}
                >
                  {formLoading ? 'Booking...' : 'Submit'}
                </button>
              </form>
            </div>
          )}

          {/* Lab results tab */}
          {selectedTab === 'labs' && (
            <div className="card">
              <div className="flex justify-between items-center mb-3">
                <h2 className="text-sm font-semibold">Lab Documents</h2>
                <label className="btn-primary text-xs px-3 py-1 rounded cursor-pointer">
                  Upload lab result
                  <input
                    type="file"
                    accept="application/pdf,image/*"
                    className="hidden"
                    onChange={async (e) => {
                      const file = e.target.files?.[0];
                      if (!file) return;
                      try {
                        await fileService.uploadLabResult(file, file.name, 'Uploaded from dashboard');
                        const [filesRes, meRes] = await Promise.all([
                          fileService.getPatientFiles(patientId),
                          patientService.getCurrentUser(),
                        ]);
                        setFiles(filesRes.files || []);
                        setData(meRes.data);
                      } catch (err) {
                        alert('Failed to upload lab document');
                      } finally {
                        e.target.value = '';
                      }
                    }}
                  />
                </label>
              </div>
              {labDocs.length > 0 ? (
                <ul className="space-y-2 text-sm">
                  {labDocs.map((doc) => (
                    <li
                      key={doc.document_id}
                      className="flex justify-between items-center bg-gray-50 px-3 py-2 rounded"
                    >
                      <div>
                        <div className="font-medium">{doc.file_name}</div>
                        <div className="text-xs text-gray-500">
                          Uploaded {doc.uploaded_at && new Date(doc.uploaded_at).toLocaleString()}
                        </div>
                      </div>
                      <div className="flex gap-2">
                        <button
                          type="button"
                          className="text-xs text-blue-600 hover:underline"
                          onClick={() => fileService.downloadFile(doc.document_id, doc.file_name)}
                        >
                          Download
                        </button>
                      </div>
                    </li>
                  ))}
                </ul>
              ) : (
                <p className="text-sm text-gray-500">No lab documents uploaded yet.</p>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default PatientDashboardPage;