from datetime import datetime, date
from werkzeug.security import generate_password_hash, check_password_hash
from app.extensions import db

class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), default='OFFICER', nullable=False)  # ADMIN, OFFICER
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    audit_logs = db.relationship('AuditLog', backref='user', lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'role': self.role,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else None
        }


class PHC(db.Model):
    __tablename__ = 'phcs'

    id = db.Column(db.Integer, primary_key=True)
    phc_code = db.Column(db.String(20), unique=True, nullable=False, index=True)
    name = db.Column(db.String(120), nullable=False)
    district = db.Column(db.String(80), nullable=False, index=True)
    state = db.Column(db.String(80), default='West Bengal', nullable=False)
    total_beds = db.Column(db.Integer, default=20)
    occupied_beds = db.Column(db.Integer, default=12)
    staff_total = db.Column(db.Integer, default=12)
    staff_present = db.Column(db.Integer, default=11)
    patients_today = db.Column(db.Integer, default=120)
    status = db.Column(db.String(20), default='NORMAL')  # NORMAL, WATCH, WARNING, CRITICAL
    latitude = db.Column(db.Float, nullable=True)
    longitude = db.Column(db.Float, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    usages = db.relationship('MedicineUsage', backref='phc', lazy=True, cascade='all, delete-orphan')
    patient_records = db.relationship('PatientFootfall', backref='phc', lazy=True, cascade='all, delete-orphan')
    bed_records = db.relationship('BedRecord', backref='phc', lazy=True, cascade='all, delete-orphan')
    staff_records = db.relationship('StaffAttendance', backref='phc', lazy=True, cascade='all, delete-orphan')
    alerts = db.relationship('Alert', backref='phc', lazy=True, cascade='all, delete-orphan')
    forecasts = db.relationship('Forecast', backref='phc', lazy=True, cascade='all, delete-orphan')

    @property
    def bed_occupancy_rate(self):
        if self.total_beds and self.total_beds > 0:
            return round((self.occupied_beds / self.total_beds) * 100, 1)
        return 0.0

    @property
    def staff_attendance_rate(self):
        if self.staff_total and self.staff_total > 0:
            return round((self.staff_present / self.staff_total) * 100, 1)
        return 0.0

    def to_dict(self):
        return {
            'id': self.id,
            'phc_code': self.phc_code,
            'name': self.name,
            'district': self.district,
            'state': self.state,
            'total_beds': self.total_beds,
            'occupied_beds': self.occupied_beds,
            'available_beds': max(0, self.total_beds - self.occupied_beds),
            'bed_occupancy_rate': self.bed_occupancy_rate,
            'staff_total': self.staff_total,
            'staff_present': self.staff_present,
            'staff_attendance_rate': self.staff_attendance_rate,
            'patients_today': self.patients_today,
            'status': self.status,
            'latitude': self.latitude,
            'longitude': self.longitude,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else None
        }


class Medicine(db.Model):
    __tablename__ = 'medicines'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False, index=True)
    category = db.Column(db.String(80), default='Essential')  # Analgesic, Antibiotic, Rehydration, Vaccine, etc.
    current_stock = db.Column(db.Integer, default=0)
    daily_usage = db.Column(db.Integer, default=10)
    minimum_stock = db.Column(db.Integer, default=100)
    unit = db.Column(db.String(20), default='units')  # tablets, vials, packets, doses
    expiry_date = db.Column(db.Date, nullable=True)
    status = db.Column(db.String(20), default='ADEQUATE')  # ADEQUATE, LOW, CRITICAL
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    usages = db.relationship('MedicineUsage', backref='medicine', lazy=True, cascade='all, delete-orphan')
    forecasts = db.relationship('Forecast', backref='medicine', lazy=True, cascade='all, delete-orphan')
    alerts = db.relationship('Alert', backref='medicine', lazy=True, cascade='all, delete-orphan')
    redistributions = db.relationship('Redistribution', backref='medicine', lazy=True)

    @property
    def stockout_days(self):
        if self.daily_usage and self.daily_usage > 0:
            return round(self.current_stock / float(self.daily_usage), 1)
        return 99.0

    @property
    def predicted_7d_demand(self):
        # Slightly trended usage estimate
        return int(round(self.daily_usage * 7 * 1.05))

    @property
    def predicted_30d_demand(self):
        return int(round(self.daily_usage * 30 * 1.08))

    @property
    def risk_level(self):
        days = self.stockout_days
        if days < 2.0 or self.current_stock < (self.minimum_stock * 0.4):
            return 'CRITICAL'
        elif days < 4.0 or self.current_stock < self.minimum_stock:
            return 'HIGH'
        elif days < 7.0 or self.current_stock < (self.minimum_stock * 1.5):
            return 'MEDIUM'
        return 'LOW'

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'category': self.category,
            'current_stock': self.current_stock,
            'daily_usage': self.daily_usage,
            'minimum_stock': self.minimum_stock,
            'unit': self.unit,
            'expiry_date': self.expiry_date.strftime('%Y-%m-%d') if self.expiry_date else None,
            'status': self.status,
            'stockout_days': self.stockout_days,
            'predicted_7d_demand': self.predicted_7d_demand,
            'predicted_30d_demand': self.predicted_30d_demand,
            'risk_level': self.risk_level,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else None,
            'updated_at': self.updated_at.strftime('%Y-%m-%d %H:%M:%S') if self.updated_at else None
        }


class MedicineUsage(db.Model):
    __tablename__ = 'medicine_usages'

    id = db.Column(db.Integer, primary_key=True)
    medicine_id = db.Column(db.Integer, db.ForeignKey('medicines.id'), nullable=False)
    phc_id = db.Column(db.Integer, db.ForeignKey('phcs.id'), nullable=True)
    usage_date = db.Column(db.Date, default=date.today)
    quantity_used = db.Column(db.Integer, default=0)

    def to_dict(self):
        return {
            'id': self.id,
            'medicine_id': self.medicine_id,
            'medicine_name': self.medicine.name if self.medicine else None,
            'phc_id': self.phc_id,
            'phc_name': self.phc.name if self.phc else 'Network Average',
            'usage_date': self.usage_date.strftime('%Y-%m-%d') if self.usage_date else None,
            'quantity_used': self.quantity_used
        }


class PatientFootfall(db.Model):
    __tablename__ = 'patient_footfalls'

    id = db.Column(db.Integer, primary_key=True)
    phc_id = db.Column(db.Integer, db.ForeignKey('phcs.id'), nullable=False)
    date = db.Column(db.Date, default=date.today)
    patient_count = db.Column(db.Integer, default=0)
    emergency_cases = db.Column(db.Integer, default=0)

    def to_dict(self):
        return {
            'id': self.id,
            'phc_id': self.phc_id,
            'phc_name': self.phc.name if self.phc else None,
            'district': self.phc.district if self.phc else None,
            'date': self.date.strftime('%Y-%m-%d') if self.date else None,
            'patient_count': self.patient_count,
            'emergency_cases': self.emergency_cases
        }


class BedRecord(db.Model):
    __tablename__ = 'bed_records'

    id = db.Column(db.Integer, primary_key=True)
    phc_id = db.Column(db.Integer, db.ForeignKey('phcs.id'), nullable=False)
    date = db.Column(db.Date, default=date.today)
    total_beds = db.Column(db.Integer, default=20)
    occupied_beds = db.Column(db.Integer, default=10)

    @property
    def occupancy_rate(self):
        if self.total_beds and self.total_beds > 0:
            return round((self.occupied_beds / self.total_beds) * 100, 1)
        return 0.0

    def to_dict(self):
        return {
            'id': self.id,
            'phc_id': self.phc_id,
            'phc_name': self.phc.name if self.phc else None,
            'district': self.phc.district if self.phc else None,
            'date': self.date.strftime('%Y-%m-%d') if self.date else None,
            'total_beds': self.total_beds,
            'occupied_beds': self.occupied_beds,
            'available_beds': max(0, self.total_beds - self.occupied_beds),
            'occupancy_rate': self.occupancy_rate
        }


class StaffAttendance(db.Model):
    __tablename__ = 'staff_attendances'

    id = db.Column(db.Integer, primary_key=True)
    phc_id = db.Column(db.Integer, db.ForeignKey('phcs.id'), nullable=False)
    date = db.Column(db.Date, default=date.today)
    total_staff = db.Column(db.Integer, default=10)
    present_staff = db.Column(db.Integer, default=9)
    doctors_present = db.Column(db.Integer, default=2)
    nurses_present = db.Column(db.Integer, default=4)
    technicians_present = db.Column(db.Integer, default=2)
    other_staff_present = db.Column(db.Integer, default=1)

    @property
    def attendance_rate(self):
        if self.total_staff and self.total_staff > 0:
            return round((self.present_staff / self.total_staff) * 100, 1)
        return 0.0

    def to_dict(self):
        return {
            'id': self.id,
            'phc_id': self.phc_id,
            'phc_name': self.phc.name if self.phc else None,
            'district': self.phc.district if self.phc else None,
            'date': self.date.strftime('%Y-%m-%d') if self.date else None,
            'total_staff': self.total_staff,
            'present_staff': self.present_staff,
            'absent_staff': max(0, self.total_staff - self.present_staff),
            'attendance_rate': self.attendance_rate,
            'doctors_present': self.doctors_present,
            'nurses_present': self.nurses_present,
            'technicians_present': self.technicians_present,
            'other_staff_present': self.other_staff_present
        }


class Forecast(db.Model):
    __tablename__ = 'forecasts'

    id = db.Column(db.Integer, primary_key=True)
    medicine_id = db.Column(db.Integer, db.ForeignKey('medicines.id'), nullable=False)
    phc_id = db.Column(db.Integer, db.ForeignKey('phcs.id'), nullable=True)
    forecast_date = db.Column(db.Date, default=date.today)
    predicted_demand = db.Column(db.Integer, default=0)
    stockout_days = db.Column(db.Float, default=0.0)
    risk_level = db.Column(db.String(20), default='LOW')  # LOW, MEDIUM, HIGH, CRITICAL
    confidence = db.Column(db.Integer, default=90)  # Percentage 0-100
    reason = db.Column(db.Text, nullable=True)

    def to_dict(self):
        return {
            'id': self.id,
            'medicine_id': self.medicine_id,
            'medicine_name': self.medicine.name if self.medicine else None,
            'category': self.medicine.category if self.medicine else None,
            'unit': self.medicine.unit if self.medicine else 'units',
            'current_stock': self.medicine.current_stock if self.medicine else 0,
            'phc_id': self.phc_id,
            'phc_name': self.phc.name if self.phc else 'National Network Aggregate',
            'forecast_date': self.forecast_date.strftime('%Y-%m-%d') if self.forecast_date else None,
            'predicted_demand': self.predicted_demand,
            'stockout_days': round(self.stockout_days, 1),
            'risk_level': self.risk_level,
            'confidence': self.confidence,
            'reason': self.reason
        }


class Alert(db.Model):
    __tablename__ = 'alerts'

    id = db.Column(db.Integer, primary_key=True)
    phc_id = db.Column(db.Integer, db.ForeignKey('phcs.id'), nullable=True)
    medicine_id = db.Column(db.Integer, db.ForeignKey('medicines.id'), nullable=True)
    alert_type = db.Column(db.String(50), nullable=False)  # MEDICINE_SHORTAGE, BED_PRESSURE, STAFF_SHORTAGE, PATIENT_SURGE, VACCINE_SHORTAGE
    severity = db.Column(db.String(20), nullable=False)  # LOW, MEDIUM, HIGH, CRITICAL
    message = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(20), default='ACTIVE')  # ACTIVE, RESOLVED
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    resolved_at = db.Column(db.DateTime, nullable=True)

    def to_dict(self):
        return {
            'id': self.id,
            'phc_id': self.phc_id,
            'phc_code': self.phc.phc_code if self.phc else 'NATIONAL',
            'phc_name': self.phc.name if self.phc else 'All Centres',
            'district': self.phc.district if self.phc else 'Multi-District',
            'medicine_id': self.medicine_id,
            'medicine_name': self.medicine.name if self.medicine else None,
            'alert_type': self.alert_type,
            'severity': self.severity,
            'message': self.message,
            'status': self.status,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else None,
            'resolved_at': self.resolved_at.strftime('%Y-%m-%d %H:%M:%S') if self.resolved_at else None
        }


class Redistribution(db.Model):
    __tablename__ = 'redistributions'

    id = db.Column(db.Integer, primary_key=True)
    source_phc = db.Column(db.String(100), nullable=False)
    target_phc = db.Column(db.String(100), nullable=False)
    medicine_id = db.Column(db.Integer, db.ForeignKey('medicines.id'), nullable=False)
    quantity = db.Column(db.Integer, default=0)
    confidence = db.Column(db.Integer, default=90)
    reason = db.Column(db.Text, nullable=True)
    status = db.Column(db.String(20), default='PENDING')  # PENDING, APPROVED, REJECTED, COMPLETED
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    reviewed_at = db.Column(db.DateTime, nullable=True)

    def to_dict(self):
        return {
            'id': self.id,
            'source_phc': self.source_phc,
            'target_phc': self.target_phc,
            'medicine_id': self.medicine_id,
            'medicine_name': self.medicine.name if self.medicine else None,
            'unit': self.medicine.unit if self.medicine else 'units',
            'quantity': self.quantity,
            'confidence': self.confidence,
            'reason': self.reason,
            'status': self.status,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else None,
            'reviewed_at': self.reviewed_at.strftime('%Y-%m-%d %H:%M:%S') if self.reviewed_at else None
        }


class FederatedRound(db.Model):
    __tablename__ = 'federated_rounds'

    id = db.Column(db.Integer, primary_key=True)
    round_number = db.Column(db.Integer, nullable=False)
    participating_nodes = db.Column(db.Integer, default=5)
    model_version = db.Column(db.String(50), default='v1.0.0')
    accuracy = db.Column(db.Float, default=92.5)
    status = db.Column(db.String(30), default='COMPLETED')  # TRAINING, AGGREGATING, COMPLETED
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'round_number': self.round_number,
            'participating_nodes': self.participating_nodes,
            'model_version': self.model_version,
            'accuracy': round(self.accuracy, 2),
            'status': self.status,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else None
        }


class AuditLog(db.Model):
    __tablename__ = 'audit_logs'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    action = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    ip_address = db.Column(db.String(50), default='127.0.0.1')

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'user_name': self.user.name if self.user else 'System / Autonomous Agent',
            'action': self.action,
            'description': self.description,
            'timestamp': self.timestamp.strftime('%Y-%m-%d %H:%M:%S') if self.timestamp else None,
            'ip_address': self.ip_address
        }
