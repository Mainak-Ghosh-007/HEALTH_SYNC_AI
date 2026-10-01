from datetime import datetime, date, timedelta
from flask import Blueprint, render_template, redirect, url_for, session
from app.extensions import db
from app.models import (
    PHC, Medicine, PatientFootfall, BedRecord,
    StaffAttendance, Forecast, Alert, Redistribution,
    FederatedRound, AuditLog
)
from app.routes.auth import login_required
from app.services.forecast import calculate_medicine_forecast, calculate_resource_risk_index, calculate_dynamic_staff_strain
from app.services.federation import get_federated_state

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('main.dashboard'))
    return redirect(url_for('auth.login'))


@main_bp.route('/dashboard')
@login_required
def dashboard():
    # Key command center metrics
    # Prompt specifies demo values:
    # PHCs Connected: 12,540, Medicine Alerts: 126, Critical PHCs: 34, Available Beds: 8,420, Staff Attendance: 91%
    phcs = PHC.query.all()
    medicines = Medicine.query.all()
    active_alerts = Alert.query.filter_by(status='ACTIVE').order_by(Alert.created_at.desc()).limit(8).all()
    pending_redist = Redistribution.query.filter_by(status='PENDING').order_by(Redistribution.confidence.desc()).limit(3).all()
    
    # Calculate demand forecasts for key showcase medicines
    forecast_paracetamol = calculate_medicine_forecast(next((m for m in medicines if 'Paracetamol' in m.name), medicines[0]))
    forecast_antibiotic = calculate_medicine_forecast(next((m for m in medicines if 'Amoxicillin' in m.name), medicines[1]))
    forecast_ors = calculate_medicine_forecast(next((m for m in medicines if 'ORS' in m.name), medicines[3]))
    forecast_vaccine = calculate_medicine_forecast(next((m for m in medicines if 'Covishield' in m.name), medicines[4]))

    # Dynamic Resource Risk Index calculation based on real-time workforce, footfall, and bed telemetry
    risk_index = calculate_resource_risk_index(phcs, medicines)

    total_staff = sum(p.staff_total for p in phcs) or 320
    present_staff = sum(p.staff_present for p in phcs) or 291
    staff_att_pct = round((present_staff / total_staff) * 100, 1) if total_staff > 0 else 91.0

    stats = {
        'phcs_connected': "12,540",
        'medicine_alerts': 126,
        'critical_phcs': 34,
        'available_beds': "8,420",
        'staff_attendance': f"{int(round(staff_att_pct))}%",
        'total_beds_national': "10,000",
        'occupied_beds_national': "8,420",
        'occupancy_rate_national': "84.2%"
    }

    return render_template(
        'dashboard.html',
        stats=stats,
        risk_index=risk_index,
        alerts=active_alerts,
        redistributions=pending_redist,
        phcs=phcs[:6],
        forecast_paracetamol=forecast_paracetamol,
        forecast_antibiotic=forecast_antibiotic,
        forecast_ors=forecast_ors,
        forecast_vaccine=forecast_vaccine,
        now=datetime.utcnow()
    )


@main_bp.route('/phcs')
@login_required
def phcs_view():
    phcs = PHC.query.order_by(PHC.phc_code.asc()).all()
    districts = sorted(list(set(p.district for p in phcs)))
    return render_template('phcs.html', phcs=phcs, districts=districts)


@main_bp.route('/medicines')
@login_required
def medicines_view():
    medicines = Medicine.query.order_by(Medicine.name.asc()).all()
    categories = sorted(list(set(m.category for m in medicines)))
    return render_template('medicines.html', medicines=medicines, categories=categories)


@main_bp.route('/patients')
@login_required
def patients_view():
    phcs = PHC.query.order_by(PHC.name.asc()).all()
    patient_records = PatientFootfall.query.order_by(PatientFootfall.date.desc()).limit(40).all()
    today_records = PatientFootfall.query.filter_by(date=date.today()).all()
    
    total_today = sum(p.patient_count for p in today_records) or 4820
    emergencies_today = sum(p.emergency_cases for p in today_records) or 412
    weekly_avg = int(total_today * 0.94)
    monthly_footfall = int(total_today * 28.5)

    return render_template(
        'patients.html',
        phcs=phcs,
        patient_records=patient_records,
        total_today=f"{total_today:,}",
        emergencies_today=f"{emergencies_today:,}",
        weekly_avg=f"{weekly_avg:,}",
        monthly_footfall=f"{monthly_footfall:,}"
    )


@main_bp.route('/beds')
@login_required
def beds_view():
    phcs = PHC.query.order_by(PHC.name.asc()).all()
    total_beds = 10000
    occupied_beds = 8420
    available_beds = total_beds - occupied_beds
    occupancy_rate = 84.2

    # High occupancy list (>90%)
    high_occupancy_phcs = [p for p in phcs if p.bed_occupancy_rate >= 90.0]
    critical_occupancy_phcs = [p for p in phcs if p.bed_occupancy_rate >= 95.0]

    return render_template(
        'beds.html',
        phcs=phcs,
        total_beds=f"{total_beds:,}",
        occupied_beds=f"{occupied_beds:,}",
        available_beds=f"{available_beds:,}",
        occupancy_rate=occupancy_rate,
        high_occupancy_phcs=high_occupancy_phcs,
        critical_occupancy_phcs=critical_occupancy_phcs
    )


@main_bp.route('/staff')
@login_required
def staff_view():
    phcs = PHC.query.order_by(PHC.name.asc()).all()
    total_staff = sum(p.staff_total for p in phcs) or 320
    present_staff = sum(p.staff_present for p in phcs) or 291
    attendance_rate = round((present_staff / total_staff) * 100, 1) if total_staff > 0 else 91.0

    doctors_est = int(present_staff * 0.22)
    nurses_est = int(present_staff * 0.44)
    techs_est = int(present_staff * 0.20)
    others_est = present_staff - doctors_est - nurses_est - techs_est

    # PHCs with attendance below 85%
    understaffed_phcs = [p for p in phcs if p.staff_attendance_rate < 85.0]

    return render_template(
        'staff.html',
        phcs=phcs,
        total_staff=total_staff,
        present_staff=present_staff,
        attendance_rate=attendance_rate,
        doctors=doctors_est,
        nurses=nurses_est,
        technicians=techs_est,
        others=others_est,
        understaffed_phcs=understaffed_phcs
    )


@main_bp.route('/forecast')
@login_required
def forecast_view():
    medicines = Medicine.query.order_by(Medicine.name.asc()).all()
    forecasts = [calculate_medicine_forecast(m) for m in medicines]
    return render_template('forecast.html', medicines=medicines, forecasts=forecasts)


@main_bp.route('/alerts')
@login_required
def alerts_view():
    active_alerts = Alert.query.filter_by(status='ACTIVE').order_by(Alert.created_at.desc()).all()
    resolved_alerts = Alert.query.filter_by(status='RESOLVED').order_by(Alert.resolved_at.desc()).limit(15).all()

    critical_count = sum(1 for a in active_alerts if a.severity == 'CRITICAL')
    high_count = sum(1 for a in active_alerts if a.severity == 'HIGH')
    medium_count = sum(1 for a in active_alerts if a.severity == 'MEDIUM')
    low_count = sum(1 for a in active_alerts if a.severity == 'LOW')

    return render_template(
        'alerts.html',
        active_alerts=active_alerts,
        resolved_alerts=resolved_alerts,
        critical_count=critical_count,
        high_count=high_count,
        medium_count=medium_count,
        low_count=low_count
    )


@main_bp.route('/redistribution')
@login_required
def redistribution_view():
    pending_redists = Redistribution.query.filter_by(status='PENDING').order_by(Redistribution.confidence.desc()).all()
    history_redists = Redistribution.query.filter(Redistribution.status.in_(['APPROVED', 'REJECTED', 'COMPLETED'])).order_by(Redistribution.created_at.desc()).limit(20).all()
    
    # Identify top surplus and deficit centers for UI matrix
    medicines = Medicine.query.all()
    surplus_items = [m for m in medicines if m.risk_level == 'LOW' and m.current_stock > 1000][:6]
    deficit_items = [m for m in medicines if m.risk_level in ['CRITICAL', 'HIGH']][:6]

    return render_template(
        'redistribution.html',
        pending_redists=pending_redists,
        history_redists=history_redists,
        surplus_items=surplus_items,
        deficit_items=deficit_items
    )


@main_bp.route('/federated')
@login_required
def federated_view():
    state = get_federated_state()
    return render_template('federated.html', state=state)


@main_bp.route('/reports')
@login_required
def reports_view():
    audit_logs = AuditLog.query.order_by(AuditLog.timestamp.desc()).limit(50).all()
    alerts = Alert.query.order_by(Alert.created_at.desc()).limit(30).all()
    redistributions = Redistribution.query.order_by(Redistribution.created_at.desc()).limit(30).all()
    medicines = Medicine.query.order_by(Medicine.name.asc()).all()
    rounds = FederatedRound.query.order_by(FederatedRound.round_number.desc()).limit(10).all()

    return render_template(
        'reports.html',
        audit_logs=audit_logs,
        alerts=alerts,
        redistributions=redistributions,
        medicines=medicines,
        rounds=rounds
    )
