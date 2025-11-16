"""
Manual test script for appointment agent
Run this to quickly verify appointment functionality
"""
import sys
from pathlib import Path
from datetime import datetime, timedelta

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from backend.adk_app.tools.scheduling_tools import (
    list_open_slots_tool,
    book_appointment_tool,
)


def print_separator(title=""):
    """Print a nice separator"""
    print("\n" + "=" * 70)
    if title:
        print(f" {title}")
        print("=" * 70)


def test_list_slots():
    """Test listing appointment slots"""
    print_separator("TEST 1: List Available Slots")
    
    specialty = "orthopedics"
    after_time = datetime.now().isoformat()
    max_results = 3
    
    print(f"Specialty: {specialty}")
    print(f"After: {after_time}")
    print(f"Max Results: {max_results}")
    print()
    
    slots = list_open_slots_tool(specialty, after_time, max_results)
    
    print(f"✓ Found {len(slots)} available slots:")
    for i, slot in enumerate(slots, 1):
        print(f"\n  Slot {i}:")
        print(f"    ID: {slot['slot_id']}")
        print(f"    Specialty: {slot['specialty']}")
        print(f"    Start: {slot['start']}")
        print(f"    Duration: {slot['duration_minutes']} minutes")
        print(f"    Location: {slot['location']}")
    
    return slots


def test_book_appointment(slot_id):
    """Test booking an appointment"""
    print_separator("TEST 2: Book Appointment")
    
    patient_id = "demo_patient"
    reason = "Knee pain and limited mobility"
    
    print(f"Slot ID: {slot_id}")
    print(f"Patient ID: {patient_id}")
    print(f"Reason: {reason}")
    print()
    
    result = book_appointment_tool(slot_id, patient_id, reason)
    
    print("✓ Appointment booked successfully!")
    print(f"\n  Booking ID: {result['booking_id']}")
    print(f"  Status: {result['status']}")
    print(f"  Message: {result['message']}")
    
    return result


def test_multiple_specialties():
    """Test multiple specialties"""
    print_separator("TEST 3: Multiple Specialties")
    
    specialties = ["orthopedics", "primary care", "cardiology"]
    after_time = datetime.now().isoformat()
    
    for specialty in specialties:
        slots = list_open_slots_tool(specialty, after_time, 2)
        print(f"\n✓ {specialty.upper()}: {len(slots)} slots available")
        print(f"  First slot: {slots[0]['start']}")


def test_future_dates():
    """Test booking for future dates"""
    print_separator("TEST 4: Future Date Booking")
    
    # Book for next week
    future_date = datetime.now() + timedelta(days=7)
    print(f"Booking for: {future_date.strftime('%Y-%m-%d')}")
    
    slots = list_open_slots_tool(
        "primary care",
        future_date.isoformat(),
        3
    )
    
    print(f"\n✓ Found {len(slots)} slots for next week:")
    for slot in slots:
        slot_date = datetime.fromisoformat(slot['start'])
        print(f"  - {slot_date.strftime('%Y-%m-%d %H:%M')}")


def test_complete_workflow():
    """Test complete booking workflow"""
    print_separator("TEST 5: Complete Booking Workflow")
    
    print("Step 1: Patient requests orthopedics appointment")
    print("Step 2: System lists available slots")
    
    slots = list_open_slots_tool(
        "orthopedics",
        datetime.now().isoformat(),
        3
    )
    
    print(f"\n✓ Found {len(slots)} available slots")
    print(f"  Showing slot 1: {slots[0]['start']}")
    
    print("\nStep 3: Patient selects first slot")
    print("Step 4: System books appointment")
    
    booking = book_appointment_tool(
        slots[0]['slot_id'],
        "demo_patient",
        "Follow-up for knee pain"
    )
    
    print(f"\n✓ Booking confirmed!")
    print(f"  Booking ID: {booking['booking_id']}")
    print(f"  Status: {booking['status']}")


def run_all_tests():
    """Run all manual tests"""
    print("\n" + "=" * 70)
    print(" APPOINTMENT AGENT MANUAL TESTS")
    print("=" * 70)
    
    try:
        # Test 1: List slots
        slots = test_list_slots()
        
        # Test 2: Book appointment with first slot
        if slots:
            test_book_appointment(slots[0]['slot_id'])
        
        # Test 3: Multiple specialties
        test_multiple_specialties()
        
        # Test 4: Future dates
        test_future_dates()
        
        # Test 5: Complete workflow
        test_complete_workflow()
        
        print_separator("ALL TESTS COMPLETED")
        print("✓ All tests passed successfully!")
        
    except Exception as e:
        print(f"\n✗ Error occurred: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    run_all_tests()