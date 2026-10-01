from datetime import date
from app.extensions import db
from app.models import Medicine, PHC, PatientFootfall, Forecast

def calculate_medicine_forecast(medicine: Medicine, phc: PHC = None, demand_multiplier: float = 1.0):
    """
    Calculate demand forecast, stockout timeline, and explainable risk for a medicine.
    Algorithm:
      Predicted Daily Demand = Baseline Daily Usage * Trend Factor * Footfall Factor * Seasonal Factor * demand_multiplier
    """
    baseline_usage = float(medicine.daily_usage) if medicine.daily_usage > 0 else 10.0

    # Trend factor based on category
    trend_factors = {
        'Analgesic': 1.23,      # Paracetamol surge
        'Antibiotic': 1.17,     # Antibiotics surge
        'Rehydration': 1.31,    # ORS surge
        'Vaccine': 1.12,        # Vaccine surge
        'Antidiabetic': 1.04,
        'Respiratory': 1.18,
        'IV Fluid': 1.09,
        'Antihistamine': 1.06,
        'Antimalarial': 1.15
    }
    cat_trend = trend_factors.get(medicine.category, 1.08)

    # Footfall factor (if PHC specified or network average)
    footfall_factor = 1.05
    if phc:
        if phc.patients_today > 250:
            footfall_factor = 1.20
        elif phc.patients_today > 180:
            footfall_factor = 1.10
        elif phc.patients_today < 140:
            footfall_factor = 0.95

    # Seasonal adjustment factor (demo factor: monsoon/post-monsoon respiratory & vector uptick)
    seasonal_factor = 1.06

    predicted_daily_rate = baseline_usage * cat_trend * footfall_factor * seasonal_factor * demand_multiplier
    predicted_7d = int(round(predicted_daily_rate * 7))
    predicted_30d = int(round(predicted_daily_rate * 30))

    current_stock = float(medicine.current_stock)
    if predicted_daily_rate > 0:
        stockout_days = round(current_stock / predicted_daily_rate, 1)
    else:
        stockout_days = 99.0

    # Severity Risk
    if stockout_days < 2.0 or current_stock < (medicine.minimum_stock * 0.4):
        risk_level = 'CRITICAL'
    elif stockout_days < 4.0 or current_stock < medicine.minimum_stock:
        risk_level = 'HIGH'
    elif stockout_days < 7.0 or current_stock < (medicine.minimum_stock * 1.5):
        risk_level = 'MEDIUM'
    else:
        risk_level = 'LOW'

    # Confidence calculation (between 88% and 96%)
    confidence = min(96, max(88, int(92 + (3 if stockout_days < 3 else -2))))

    # Explainable AI Reason (Innovation 9)
    reasons = []
    if current_stock < medicine.minimum_stock:
        reasons.append(f"Current stock ({int(current_stock)} {medicine.unit}) is below minimum safety threshold ({medicine.minimum_stock} {medicine.unit}).")
    else:
        reasons.append(f"Current buffer is {int(current_stock)} {medicine.unit}.")

    pct_change = int(round((cat_trend - 1.0) * 100))
    if pct_change > 0:
        reasons.append(f"Category demand trend shows a +{pct_change}% upward shift.")

    if demand_multiplier > 1.0:
        sim_pct = int(round((demand_multiplier - 1.0) * 100))
        reasons.append(f"What-If stress test active: +{sim_pct}% external demand surge applied.")

    reasons.append(f"Projected depletion rate is ~{int(round(predicted_daily_rate))} {medicine.unit}/day, giving {stockout_days} days of remaining runway.")

    if risk_level in ['CRITICAL', 'HIGH']:
        reasons.append("Cross-district resource redistribution review strongly recommended.")

    return {
        'medicine_id': medicine.id,
        'medicine_name': medicine.name,
        'category': medicine.category,
        'unit': medicine.unit,
        'current_stock': medicine.current_stock,
        'minimum_stock': medicine.minimum_stock,
        'daily_usage': medicine.daily_usage,
        'predicted_daily_rate': round(predicted_daily_rate, 1),
        'predicted_7d': predicted_7d,
        'predicted_30d': predicted_30d,
        'stockout_days': stockout_days,
        'risk_level': risk_level,
        'confidence': confidence,
        'reason': " ".join(reasons),
        'reasons_list': reasons
    }


def calculate_dynamic_staff_strain(phcs=None, demand_multiplier: float = 1.0) -> float:
    """
    Calculate dynamic Staff Strain percentage (0 - 100%) across the healthcare facility network.
    Synthesizes:
      1. Clinical Absenteeism / Vacancy Deficit: (staff_total - staff_present) / staff_total
      2. OPD Patient-to-Staff Workload Intensity: patients_today / staff_present vs standard ratio (12:1)
      3. Inpatient Bed-to-Staff Care Ratio: occupied_beds / staff_present vs standard ratio (3.5:1)
      4. Proportion of Facilities Operating Under Acute Staff Strain (<90% attendance or >16 patients/staff)
    """
    if phcs is None:
        phcs = PHC.query.all()

    if not phcs:
        return 65.0

    total_staff = sum(p.staff_total for p in phcs)
    present_staff = sum(p.staff_present for p in phcs)
    total_patients = sum(p.patients_today for p in phcs) * demand_multiplier
    occupied_beds = sum(p.occupied_beds for p in phcs) * (1.0 + (demand_multiplier - 1.0) * 0.4)

    if total_staff <= 0 or present_staff <= 0:
        return 75.0

    # Vector A: Absenteeism / Staffing Deficit (Weight: 25%)
    absenteeism_pct = max(0.0, (total_staff - present_staff) / total_staff * 100.0)
    absenteeism_score = min(100.0, (absenteeism_pct / 12.0) * 100.0)

    # Vector B: Outpatient Workload Pressure (Weight: 40%)
    patient_staff_ratio = total_patients / present_staff
    workload_score = min(100.0, max(20.0, (patient_staff_ratio / 22.0) * 100.0))

    # Vector C: Inpatient Bed Care Burden (Weight: 20%)
    bed_staff_ratio = occupied_beds / present_staff
    bed_care_score = min(100.0, max(20.0, (bed_staff_ratio / 7.5) * 100.0))

    # Vector D: Understaffed Facilities Ratio (Weight: 15%)
    strained_phcs = sum(
        1 for p in phcs
        if (p.staff_total > 0 and (p.staff_present / p.staff_total) < 0.90) or
           (p.staff_present > 0 and (p.patients_today * demand_multiplier / p.staff_present) > 16.0)
    )
    facility_strain_score = (strained_phcs / len(phcs)) * 100.0

    # Composite Staff Strain (0 - 100%)
    composite_strain = (
        0.25 * absenteeism_score +
        0.40 * workload_score +
        0.20 * bed_care_score +
        0.15 * facility_strain_score
    )

    return round(min(98.0, max(15.0, composite_strain)), 1)


def calculate_resource_risk_index(phcs=None, medicines=None, demand_multiplier: float = 1.0):
    """
    Calculate dynamic multi-vector Resource Risk Index for the National Command Center.
    Returns:
      overall, medicine_pressure, bed_pressure, staff_pressure, patient_surge, severity
    """
    if phcs is None:
        phcs = PHC.query.all()
    if medicines is None:
        medicines = Medicine.query.all()

    # 1. Staff Strain (Dynamic from live workforce telemetry)
    staff_pressure = calculate_dynamic_staff_strain(phcs, demand_multiplier)

    # 2. Bed Pressure (Dynamic from bed occupancy telemetry)
    total_beds = sum(p.total_beds for p in phcs)
    occupied_beds = sum(p.occupied_beds for p in phcs)
    base_bed_pct = (occupied_beds / total_beds * 100.0) if total_beds > 0 else 71.0
    bed_pressure = round(min(98.5, base_bed_pct + ((demand_multiplier - 1.0) * 28.0)), 1)

    # 3. Medicine Pressure (Dynamic based on low stock and critical runway)
    if medicines:
        low_stock_count = sum(1 for m in medicines if m.current_stock < (m.minimum_stock * 1.5))
        base_med_pressure = (low_stock_count / len(medicines)) * 100.0
        medicine_pressure = round(min(98.0, max(25.0, base_med_pressure * (1.0 + (demand_multiplier - 1.0) * 0.5))), 1)
    else:
        medicine_pressure = 82.0

    # 4. Patient Surge (Dynamic based on total patients vs baseline)
    total_patients = sum(p.patients_today for p in phcs) * demand_multiplier
    nominal_baseline = len(phcs) * 1100.0 if phcs else 30000.0
    patient_surge = round(min(98.0, max(40.0, (total_patients / (nominal_baseline * 1.35)) * 100.0)), 1)

    # 5. Composite Risk Score (0 - 100)
    composite = int(round(
        0.30 * medicine_pressure +
        0.25 * bed_pressure +
        0.25 * staff_pressure +
        0.20 * patient_surge
    ))

    severity = "CRITICAL" if composite >= 80 else "ELEVATED" if composite >= 65 else "MODERATE" if composite >= 45 else "NOMINAL"

    return {
        'overall': min(99, max(10, composite)),
        'medicine_pressure': int(round(medicine_pressure)),
        'bed_pressure': int(round(bed_pressure)),
        'staff_pressure': int(round(staff_pressure)),
        'patient_surge': int(round(patient_surge)),
        'severity': severity
    }


def run_what_if_simulation(demand_increase_pct: float = 0.0):
    """
    Simulate what happens if demand increases by 0%, 10%, 20%, 30%, 50%.
    Does NOT modify actual database values.
    Returns:
      - simulated metrics
      - affected medicines
      - bed pressure changes
      - dynamic staff strain changes
      - new alert count estimate
      - required transfers
    """
    multiplier = 1.0 + (float(demand_increase_pct) / 100.0)
    medicines = Medicine.query.all()
    phcs = PHC.query.all()

    simulated_results = []
    critical_count = 0
    high_count = 0
    total_shortage_units = 0

    for med in medicines:
        sim_data = calculate_medicine_forecast(med, demand_multiplier=multiplier)
        simulated_results.append(sim_data)
        if sim_data['risk_level'] == 'CRITICAL':
            critical_count += 1
        elif sim_data['risk_level'] == 'HIGH':
            high_count += 1

        # Calculate shortage deficit if stockout is under 7 days
        if sim_data['stockout_days'] < 7.0:
            needed = max(0, sim_data['predicted_7d'] - med.current_stock)
            total_shortage_units += needed

    # Bed pressure simulation
    base_occupancy = 84.2
    simulated_bed_occupancy = min(98.5, round(base_occupancy + (demand_increase_pct * 0.28), 1))

    # Alert count estimate
    base_alerts = 126
    simulated_alert_count = int(round(base_alerts + (demand_increase_pct * 1.8)))

    # Critical PHCs estimate
    base_crit_phcs = 34
    simulated_crit_phcs = int(round(base_crit_phcs + (demand_increase_pct * 0.45)))

    # Key highlight medicines
    key_med_names = ["Paracetamol 500mg", "Amoxicillin 500mg", "ORS Sachets 20.5g", "Covishield Vaccine"]
    key_highlights = [s for s in simulated_results if s['medicine_name'] in key_med_names]

    # Dynamic Simulated Risk Index and Staff Strain
    risk_sim = calculate_resource_risk_index(phcs, medicines, demand_multiplier=multiplier)

    return {
        'demand_increase_pct': demand_increase_pct,
        'multiplier': multiplier,
        'simulated_bed_occupancy': simulated_bed_occupancy,
        'simulated_alert_count': simulated_alert_count,
        'simulated_crit_phcs': simulated_crit_phcs,
        'simulated_staff_strain': risk_sim['staff_pressure'],
        'simulated_risk_index': risk_sim,
        'critical_medicines_count': critical_count,
        'high_risk_medicines_count': high_count,
        'total_shortage_units': total_shortage_units,
        'key_highlights': key_highlights,
        'all_medicines': simulated_results
    }
