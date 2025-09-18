from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Appointment, MedicalRecord, VideoSession, PatientMedicalHistory, Prescription
from hospitals.models import Doctor

# Create your views here.

# Appointment management
@login_required
def appointment_list(request):
    """Display list of appointments for a patient."""
    appointments = []  # This would fetch real appointments in a real app
    context = {
        'appointments': appointments,
    }
    return render(request, 'appointments/appointment_list.html', context)

@login_required
def create_appointment(request, doctor_id):
    """Create a new appointment with a doctor."""
    doctor = get_object_or_404(Doctor, id=doctor_id)
    
    if request.method == 'POST':
        date = request.POST.get('date')
        time = request.POST.get('time')
        reason = request.POST.get('reason')
        
        # Basic validation
        if not all([date, time]):
            messages.error(request, 'Please select both date and time for the appointment.')
            return redirect('appointments:create_appointment', doctor_id=doctor_id)
        
        # Create appointment
        appointment = Appointment.objects.create(
            patient=request.user,
            doctor=doctor,
            appointment_date=date,
            appointment_time=time,
            reason=reason,
            status='PENDING'
        )
        
        messages.success(request, 'Appointment request created successfully. Waiting for confirmation.')
        return redirect('appointments:appointment_detail', appointment_id=appointment.id)
        
    context = {
        'doctor': doctor,
        'available_days': doctor.get_available_days_list(),
        'available_from': doctor.available_from,
        'available_to': doctor.available_to
    }
    return render(request, 'appointments/create_appointment.html', context)

@login_required
def appointment_detail(request, appointment_id):
    """Display details of a specific appointment."""
    appointment = {}  # This would fetch a real appointment in a real app
    context = {
        'appointment': appointment,
    }
    return render(request, 'appointments/appointment_detail.html', context)

@login_required
def cancel_appointment(request, appointment_id):
    """Cancel an appointment."""
    # This would cancel the appointment in a real app
    return redirect('appointments:appointment_list')

@login_required
def reschedule_appointment(request, appointment_id):
    """Reschedule an appointment."""
    if request.method == 'POST':
        # This would reschedule the appointment in a real app
        pass
    
    appointment = {}  # This would fetch a real appointment in a real app
    context = {
        'appointment': appointment,
    }
    return render(request, 'appointments/reschedule_appointment.html', context)

# Video consultations
@login_required
def video_consultation(request, meeting_id):
    """Display video consultation interface."""
    # This would fetch the video session in a real app
    context = {
        'meeting_id': meeting_id,
    }
    return render(request, 'appointments/video_consultation.html', context)

@login_required
def start_video_session(request, meeting_id):
    """Start a video consultation session."""
    # This would start the video session in a real app
    return redirect('appointments:video_consultation', meeting_id=meeting_id)

@login_required
def end_video_session(request, meeting_id):
    """End a video consultation session."""
    # This would end the video session in a real app
    return redirect('appointments:appointment_detail', appointment_id=1)  # Placeholder ID

# Medical records
@login_required
def medical_record_list(request):
    """Display list of medical records for a patient."""
    records = []  # This would fetch real records in a real app
    context = {
        'records': records,
    }
    return render(request, 'appointments/medical_record_list.html', context)

@login_required
def medical_record_detail(request, record_id):
    """Display details of a specific medical record."""
    record = {}  # This would fetch a real record in a real app
    context = {
        'record': record,
    }
    return render(request, 'appointments/medical_record_detail.html', context)

# For doctors/hospitals
@login_required
def manage_appointments(request):
    """Display appointments for a doctor or hospital to manage."""
    appointments = []  # This would fetch real appointments in a real app
    context = {
        'appointments': appointments,
    }
    return render(request, 'appointments/manage_appointments.html', context)

@login_required
def confirm_appointment(request, appointment_id):
    """Confirm an appointment."""
    # This would confirm the appointment in a real app
    return redirect('appointments:manage_appointments')

@login_required
def complete_appointment(request, appointment_id):
    """Mark an appointment as completed."""
    # This would complete the appointment in a real app
    return redirect('appointments:manage_appointments')

@login_required
def mark_no_show(request, appointment_id):
    """Mark an appointment as no-show."""
    # This would mark the appointment in a real app
    return redirect('appointments:manage_appointments')

# Medical records management (for doctors)
@login_required
def create_medical_record(request, appointment_id):
    """Create a medical record for an appointment."""
    if request.method == 'POST':
        # This would create a record in a real app
        pass
    
    appointment = {}  # This would fetch a real appointment in a real app
    context = {
        'appointment': appointment,
    }
    return render(request, 'appointments/create_medical_record.html', context)

@login_required
def update_medical_record(request, appointment_id):
    """Update a medical record."""
    if request.method == 'POST':
        # This would update the record in a real app
        pass
    
    appointment = {}  # This would fetch a real appointment in a real app
    record = {}  # This would fetch a real record in a real app
    context = {
        'appointment': appointment,
        'record': record,
    }
    return render(request, 'appointments/update_medical_record.html', context)

# Prescriptions
@login_required
def add_prescription(request, record_id):
    """Add a prescription to a medical record."""
    if request.method == 'POST':
        # This would add a prescription in a real app
        pass
    
    record = {}  # This would fetch a real record in a real app
    context = {
        'record': record,
    }
    return render(request, 'appointments/add_prescription.html', context)

@login_required
def edit_prescription(request, record_id, prescription_id):
    """Edit a prescription."""
    if request.method == 'POST':
        # This would edit the prescription in a real app
        pass
    
    prescription = {}  # This would fetch a real prescription in a real app
    context = {
        'prescription': prescription,
    }
    return render(request, 'appointments/edit_prescription.html', context)

@login_required
def delete_prescription(request, record_id, prescription_id):
    """Delete a prescription."""
    # This would delete the prescription in a real app
    return redirect('appointments:medical_record_detail', record_id=record_id)

# Medical history
@login_required
def medical_history(request):
    """Display medical history for a patient."""
    # This would fetch the history in a real app
    # For now, creating sample data to demonstrate the functionality
    history = {
        'chronic_diseases': 'Diabetes\nHypertension\nAsthma',
        'allergies': 'Peanuts\nDairy\nShellfish',
        'surgeries': 'Appendectomy (2018)\nTonsillectomy (2015)',
        'family_medical_history': 'Heart disease\nDiabetes\nCancer',
        'current_medications': 'Metformin 500mg\nLisinopril 10mg\nAlbuterol inhaler'
    }
    
    # Preprocess the data to split strings into lists
    if history.get('chronic_diseases'):
        history['chronic_diseases_list'] = [disease.strip() for disease in history['chronic_diseases'].split('\n') if disease.strip()]
    else:
        history['chronic_diseases_list'] = []
        
    if history.get('allergies'):
        history['allergies_list'] = [allergy.strip() for allergy in history['allergies'].split('\n') if allergy.strip()]
    else:
        history['allergies_list'] = []
        
    if history.get('surgeries'):
        history['surgeries_list'] = [surgery.strip() for surgery in history['surgeries'].split('\n') if surgery.strip()]
    else:
        history['surgeries_list'] = []
        
    if history.get('family_medical_history'):
        history['family_medical_history_list'] = [item.strip() for item in history['family_medical_history'].split('\n') if item.strip()]
    else:
        history['family_medical_history_list'] = []
        
    if history.get('current_medications'):
        history['current_medications_list'] = [medication.strip() for medication in history['current_medications'].split('\n') if medication.strip()]
    else:
        history['current_medications_list'] = []
    
    context = {
        'history': history,
    }
    return render(request, 'appointments/medical_history.html', context)

@login_required
def update_medical_history(request):
    """Update medical history."""
    if request.method == 'POST':
        # This would update the history in a real app
        pass
    
    history = {}  # This would fetch the history in a real app
    context = {
        'history': history,
    }
    return render(request, 'appointments/update_medical_history.html', context)
