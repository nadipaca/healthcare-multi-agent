"""
Test suite for the Appointment Scheduler Agent
Tests appointment scheduling functionality including slot listing and booking
"""
import pytest
import sys
from pathlib import Path
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, patch, MagicMock

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from adk_app.tools.scheduling_tools import (
    list_open_slots_tool,
    book_appointment_tool,
)
from adk_app.appointment_agent import appointment_agent


class TestSchedulingTools:
    """Test the scheduling tool functions directly"""
    
    def test_list_open_slots_basic(self):
        """Test basic slot listing functionality"""
        specialty = "orthopedics"
        after_datetime = datetime.now().isoformat()
        max_results = 3
        
        slots = list_open_slots_tool(specialty, after_datetime, max_results)
        
        assert len(slots) == max_results
        assert all("slot_id" in slot for slot in slots)
        assert all(slot["specialty"] == specialty for slot in slots)
        assert all(slot["duration_minutes"] == 30 for slot in slots)
        assert all("start" in slot for slot in slots)
        assert all("location" in slot for slot in slots)
    
    def test_list_open_slots_specialty(self):
        """Test slot listing for different specialties"""
        specialties = ["orthopedics", "primary care", "cardiology"]
        after_datetime = datetime.now().isoformat()
        
        for specialty in specialties:
            slots = list_open_slots_tool(specialty, after_datetime, 2)
            assert all(slot["specialty"] == specialty for slot in slots)
    
    def test_list_open_slots_date_progression(self):
        """Test that slots progress correctly over days"""
        after_datetime = datetime.now().isoformat()
        slots = list_open_slots_tool("primary care", after_datetime, 5)
        
        # Check that dates are increasing
        dates = [datetime.fromisoformat(slot["start"]) for slot in slots]
        for i in range(len(dates) - 1):
            assert dates[i] < dates[i + 1]
    
    def test_book_appointment_basic(self):
        """Test basic appointment booking"""
        slot_id = "test-slot-123"
        patient_id = "demo_patient"
        reason = "Knee pain follow-up"
        
        result = book_appointment_tool(slot_id, patient_id, reason)
        
        assert result["status"] == "BOOKED"
        assert result["slot_id"] == slot_id
        assert result["patient_id"] == patient_id
        assert result["reason"] == reason
        assert "booking_id" in result
        assert "message" in result
    
    def test_book_appointment_different_reasons(self):
        """Test booking with different reasons"""
        reasons = [
            "Annual checkup",
            "Headache and dizziness",
            "Follow-up after surgery",
        ]
        
        for reason in reasons:
            result = book_appointment_tool("slot-1", "patient-1", reason)
            assert result["reason"] == reason
            assert result["status"] == "BOOKED"


class TestAppointmentAgentConfiguration:
    """Test the appointment agent configuration"""
    
    def test_agent_name(self):
        """Test agent has correct name"""
        assert appointment_agent.name == "appointment_scheduler"
    
    def test_agent_model(self):
        """Test agent uses correct model"""
        assert appointment_agent.model == "gemini-2.5-flash-lite"
    
    def test_agent_has_tools(self):
        """Test agent has necessary tools configured"""
        assert appointment_agent.tools is not None
        assert len(appointment_agent.tools) == 2
    
    def test_agent_has_description(self):
        """Test agent has description"""
        assert appointment_agent.description is not None
        assert "schedule" in appointment_agent.description.lower()
    
    def test_agent_has_instructions(self):
        """Test agent has proper instructions"""
        assert appointment_agent.instruction is not None
        instructions_lower = appointment_agent.instruction.lower()
        assert "book" in instructions_lower or "appointment" in instructions_lower
    
    def test_agent_output_key(self):
        """Test agent has output key configured"""
        assert appointment_agent.output_key == "appointment_summary"


@pytest.mark.asyncio
class TestAppointmentAgentIntegration:
    """Integration tests for appointment agent (requires API key)"""
    
    async def test_agent_slot_listing_flow(self):
        """Test that agent can list available slots"""
        # Note: This is a simplified test - full test would require mocking
        # the entire ADK context and event streaming
        
        # Verify tools are callable
        slots = list_open_slots_tool(
            "orthopedics",
            datetime.now().isoformat(),
            3
        )
        assert len(slots) == 3
    
    async def test_agent_booking_flow(self):
        """Test that agent can complete booking"""
        # First get a slot
        slots = list_open_slots_tool(
            "primary care",
            datetime.now().isoformat(),
            1
        )
        slot_id = slots[0]["slot_id"]
        
        # Book the appointment
        result = book_appointment_tool(
            slot_id,
            "demo_patient",
            "Test booking"
        )
        
        assert result["status"] == "BOOKED"
        assert result["slot_id"] == slot_id


class TestAppointmentWorkflow:
    """Test complete appointment scheduling workflows"""
    
    def test_complete_booking_workflow(self):
        """Test end-to-end booking workflow"""
        # 1. List available slots
        specialty = "orthopedics"
        after_time = (datetime.now() + timedelta(days=1)).isoformat()
        
        slots = list_open_slots_tool(specialty, after_time, 3)
        assert len(slots) > 0
        
        # 2. Select a slot (first one)
        selected_slot = slots[0]
        
        # 3. Book the appointment
        booking = book_appointment_tool(
            slot_id=selected_slot["slot_id"],
            patient_id="demo_patient",
            reason="Knee pain consultation"
        )
        
        # 4. Verify booking
        assert booking["status"] == "BOOKED"
        assert booking["slot_id"] == selected_slot["slot_id"]
        assert "booking_id" in booking
    
    def test_weekend_booking_workflow(self):
        """Test booking for weekend appointments"""
        # Get a date that's definitely in the future
        future_date = datetime.now() + timedelta(days=7)
        
        slots = list_open_slots_tool(
            "primary care",
            future_date.isoformat(),
            5
        )
        
        assert len(slots) == 5
        # Verify dates are after requested time
        for slot in slots:
            slot_time = datetime.fromisoformat(slot["start"])
            assert slot_time >= future_date
    
    def test_multiple_specialty_bookings(self):
        """Test booking across different specialties"""
        specialties = ["orthopedics", "cardiology", "primary care"]
        after_time = datetime.now().isoformat()
        
        for specialty in specialties:
            slots = list_open_slots_tool(specialty, after_time, 2)
            assert len(slots) == 2
            
            booking = book_appointment_tool(
                slots[0]["slot_id"],
                "demo_patient",
                f"Consultation for {specialty}"
            )
            assert booking["status"] == "BOOKED"


class TestEdgeCases:
    """Test edge cases and error scenarios"""
    
    def test_zero_slots_requested(self):
        """Test requesting zero slots"""
        slots = list_open_slots_tool(
            "primary care",
            datetime.now().isoformat(),
            0
        )
        assert len(slots) == 0
    
    def test_large_number_of_slots(self):
        """Test requesting many slots"""
        slots = list_open_slots_tool(
            "orthopedics",
            datetime.now().isoformat(),
            50
        )
        assert len(slots) == 50
    
    def test_past_datetime(self):
        """Test with past datetime (should still work, mock doesn't validate)"""
        past_time = (datetime.now() - timedelta(days=1)).isoformat()
        slots = list_open_slots_tool("primary care", past_time, 3)
        # Mock doesn't validate dates, so this should still return slots
        assert len(slots) == 3
    
    def test_empty_reason(self):
        """Test booking with empty reason"""
        result = book_appointment_tool("slot-1", "patient-1", "")
        assert result["status"] == "BOOKED"
        assert result["reason"] == ""
    
    def test_special_characters_in_reason(self):
        """Test booking with special characters in reason"""
        reason = "Follow-up: knee pain (post-surgery) & rehab"
        result = book_appointment_tool("slot-1", "patient-1", reason)
        assert result["reason"] == reason
        assert result["status"] == "BOOKED"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])