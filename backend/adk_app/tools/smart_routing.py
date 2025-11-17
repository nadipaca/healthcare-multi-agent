from typing import Dict, Tuple, Optional

def determine_specialty_and_urgency(symptoms: str, medical_history: Optional[Dict] = None) -> Tuple[str, str, str]:
    """
    Smart routing based on symptoms and medical history.
    
    Args:
        symptoms: User's symptom description
        medical_history: Optional medical history dict
        
    Returns:
        Tuple of (specialty, urgency, reason)
    """
    
    symptoms_lower = symptoms.lower()
    history = medical_history or {}
    history_str = str(history).lower()
    
    # Emergency/Critical symptoms - immediate care needed
    if any(kw in symptoms_lower for kw in [
        "chest pain", "difficulty breathing", "can't breathe",
        "severe bleeding", "unconscious", "stroke", "heart attack"
    ]):
        return "emergency", "immediate", "Critical symptoms require immediate emergency care"
    
    # Cardiac concerns
    if any(kw in symptoms_lower for kw in ["chest pain", "heart", "palpitations", "cardiac"]):
        if "cardiac" in history_str or "heart" in history_str:
            return "cardiology", "urgent", "Given your cardiac history, urgent evaluation needed"
        return "emergency", "immediate", "Chest symptoms require immediate evaluation"
    
    # Neurological concerns  
    if any(kw in symptoms_lower for kw in ["headache", "migraine", "vision", "dizziness", "seizure"]):
        if "migraine" in history_str or "neurological" in history_str:
            return "neurology", "routine", "Based on your migraine/neurological history"
        if any(severe in symptoms_lower for severe in ["severe", "worst", "sudden", "vision loss"]):
            return "neurology", "urgent", "Severe neurological symptoms need prompt evaluation"
        return "primary_care", "routine", "For headache evaluation and management"
    
    # Orthopedic/Joint concerns
    if any(kw in symptoms_lower for kw in ["knee", "joint", "back pain", "arthritis", "fracture"]):
        if "orthopedic" in history_str or "arthritis" in history_str:
            return "orthopedics", "routine", "Follow-up for your orthopedic condition"
        if any(severe in symptoms_lower for severe in ["severe", "can't walk", "can't move"]):
            return "orthopedics", "urgent", "Severe joint/mobility issues need prompt care"
        return "orthopedics", "routine", "For joint and mobility evaluation"
    
    # Dermatological concerns
    if any(kw in symptoms_lower for kw in ["skin", "rash", "mole", "dermatology"]):
        if any(concerning in symptoms_lower for concerning in ["changing mole", "suspicious", "cancer"]):
            return "dermatology", "urgent", "Skin changes need prompt evaluation"
        return "dermatology", "routine", "For skin condition evaluation"
    
    # Gastrointestinal concerns
    if any(kw in symptoms_lower for kw in ["stomach", "nausea", "vomiting", "diarrhea", "abdominal"]):
        if any(severe in symptoms_lower for severe in ["severe", "blood", "can't keep down"]):
            return "gastroenterology", "urgent", "Severe GI symptoms need prompt evaluation"
        return "primary_care", "routine", "For digestive symptom evaluation"
    
    # General symptoms or unclear
    if any(kw in symptoms_lower for kw in ["fever", "fatigue", "general", "checkup"]):
        return "primary_care", "routine", "For general symptom assessment and care"
    
    # Default to primary care
    return "primary_care", "routine", "For comprehensive evaluation of your symptoms"


def get_immediate_relief_by_specialty(specialty: str, symptoms: str) -> str:
    """Get specialty-specific immediate relief recommendations"""
    
    relief_options = {
        "cardiology": (
            "🚨 **CARDIAC SYMPTOMS - SEEK IMMEDIATE CARE**\n"
            "• Call 911 if chest pain is severe or worsening\n"
            "• Sit upright and stay calm\n"
            "• Take prescribed nitroglycerin if you have it\n"
            "• Do NOT drive yourself to the hospital"
        ),
        "neurology": (
            "🧠 **NEUROLOGICAL RELIEF:**\n"
            "• Rest in a dark, quiet environment\n"
            "• Apply cold compress to head/neck\n"
            "• Stay hydrated\n"
            "• Avoid bright lights and loud sounds\n"
            "• Take prescribed migraine medication if available"
        ),
        "orthopedics": (
            "🦴 **JOINT/MUSCLE RELIEF:**\n"
            "• Rest and avoid aggravating movements\n"
            "• Apply ice for acute injuries (first 24-48 hours)\n"
            "• Apply heat for chronic pain/stiffness\n"
            "• Elevate injured area if possible\n"
            "• Take anti-inflammatory medication as directed"
        ),
        "dermatology": (
            "👨‍⚕️ **SKIN CARE:**\n"
            "• Keep affected area clean and dry\n"
            "• Avoid scratching or picking\n"
            "• Apply cool, damp cloth for itching\n"
            "• Use gentle, fragrance-free moisturizer\n"
            "• Avoid known irritants or allergens"
        ),
        "gastroenterology": (
            "🍯 **DIGESTIVE RELIEF:**\n"
            "• BRAT diet: bananas, rice, applesauce, toast\n"
            "• Clear liquids: water, broth, ginger tea\n"
            "• Rest in comfortable position\n"
            "• Avoid dairy, fatty foods, alcohol\n"
            "• Small, frequent meals when ready"
        ),
        "primary_care": (
            "🏥 **GENERAL COMFORT MEASURES:**\n"
            "• Rest and monitor symptoms\n"
            "• Stay well hydrated\n"
            "• Take over-the-counter pain relievers as needed\n"
            "• Apply heat or cold as feels comfortable\n"
            "• Avoid strenuous activity"
        )
    }
    
    return relief_options.get(specialty, relief_options["primary_care"])


def get_preparation_instructions(specialty: str, symptoms: str) -> str:
    """Get specialty-specific appointment preparation instructions"""
    
    prep_instructions = {
        "cardiology": (
            "**CARDIOLOGY APPOINTMENT PREP:**\n"
            "• Bring: EKGs, stress test results, list of heart medications\n"
            "• Note: When symptoms started, triggers, family cardiac history\n"
            "• Prepare: Questions about lifestyle modifications\n"
            "• Expect: EKG, possibly stress test or echocardiogram"
        ),
        "neurology": (
            "**NEUROLOGY APPOINTMENT PREP:**\n"
            "• Track: Headache diary with triggers, frequency, severity\n"
            "• Bring: Previous brain scans (MRI/CT), neurological medications\n"
            "• Note: Any vision changes, numbness, weakness\n"
            "• Expect: Neurological examination, possibly imaging orders"
        ),
        "orthopedics": (
            "**ORTHOPEDICS APPOINTMENT PREP:**\n"
            "• Bring: X-rays, MRIs, physical therapy records\n"
            "• Note: How injury occurred, what makes it better/worse\n"
            "• Wear: Comfortable clothes, avoid tight-fitting around affected area\n"
            "• Expect: Physical examination, possibly imaging, treatment plan"
        ),
        "dermatology": (
            "**DERMATOLOGY APPOINTMENT PREP:**\n"
            "• Don't use: Makeup or lotions on affected areas day of visit\n"
            "• Bring: Photos of how condition has changed over time\n"
            "• Note: When it started, what triggers it, family history\n"
            "• Expect: Full skin examination, possibly biopsy"
        ),
        "gastroenterology": (
            "**GASTROENTEROLOGY APPOINTMENT PREP:**\n"
            "• Track: Food diary, symptom patterns, bowel movements\n"
            "• Note: Family history of GI conditions, dietary triggers\n"
            "• Bring: List of medications, supplements, previous test results\n"
            "• Expect: Detailed history, possibly lab work or imaging orders"
        ),
        "primary_care": (
            "**PRIMARY CARE APPOINTMENT PREP:**\n"
            "• Bring: Complete medication list, insurance card, ID\n"
            "• Note: All symptoms, when they started, severity\n"
            "• Prepare: Questions about your health concerns\n"
            "• Expect: Comprehensive examination, possibly lab work"
        )
    }
    
    return prep_instructions.get(specialty, prep_instructions["primary_care"])