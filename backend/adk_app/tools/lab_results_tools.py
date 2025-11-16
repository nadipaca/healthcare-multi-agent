from typing import Dict, List
from datetime import datetime, timedelta

def get_recent_lab_results(patient_id: str, days: int = 90) -> List[Dict]:
    """Get recent lab results for patient"""
    return [
        {
            "test_name": "Hemoglobin A1C",
            "value": 6.8,
            "unit": "%",
            "reference_range": "< 5.7% (normal), 5.7-6.4% (prediabetic), > 6.5% (diabetic)",
            "status": "borderline_high",
            "date": (datetime.now() - timedelta(days=30)).isoformat(),
            "ordered_by": "Dr. Smith",
        },
        {
            "test_name": "Total Cholesterol",
            "value": 195,
            "unit": "mg/dL",
            "reference_range": "< 200 mg/dL (desirable)",
            "status": "normal",
            "date": (datetime.now() - timedelta(days=30)).isoformat(),
            "ordered_by": "Dr. Smith",
        },
        {
            "test_name": "Blood Pressure",
            "value": "138/85",
            "unit": "mmHg",
            "reference_range": "< 120/80 (normal), 120-139/80-89 (elevated)",
            "status": "elevated",
            "date": (datetime.now() - timedelta(days=7)).isoformat(),
            "ordered_by": "Dr. Smith",
        }
    ]

def explain_lab_test(test_name: str) -> Dict:
    """Provide patient-friendly explanation of lab test"""
    explanations = {
        "Hemoglobin A1C": {
            "what_it_measures": "Average blood sugar over past 2-3 months",
            "why_important": "Helps monitor diabetes control",
            "normal_range": "Below 5.7%",
            "what_affects_it": "Diet, exercise, diabetes medications",
        },
        "Total Cholesterol": {
            "what_it_measures": "Amount of cholesterol in your blood",
            "why_important": "High levels increase heart disease risk",
            "normal_range": "Below 200 mg/dL",
            "what_affects_it": "Diet (especially saturated fats), exercise, genetics",
        }
    }
    return explanations.get(test_name, {
        "explanation": "Detailed explanation not available. Consult your provider."
    })