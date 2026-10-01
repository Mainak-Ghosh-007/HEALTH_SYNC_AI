# HEALTHSYNC AI — National Health Command Center

> **National-scale healthcare resource intelligence, predictive demand modeling, and cross-district resource redistribution platform.**

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-3.1.0-green.svg)](https://flask.palletsprojects.com/)
[![SQLite](https://img.shields.io/badge/Database-SQLite%20%2F%20SQLAlchemy-orange.svg)](https://www.sqlalchemy.org/)
[![Status](https://img.shields.io/badge/Deployment-Operational%20Prototype-success.svg)]()
[![Federation](https://img.shields.io/badge/Protocol-BRICS%20Federated%20v1.3-purple.svg)]()

---

## 1. Problem Statement

Public healthcare systems across developing nations face chronic vulnerabilities in medicine supply chains, bed allocation, and workforce management. Conventional healthcare portals display only **historical or current snapshots** without predictive runway intelligence.

Consequently, Primary Health Centres (PHCs) experience:
- Sudden stock-outs of essential antibiotics, analgesics, ORS, and vaccines
- Severe inpatient bed shortages during acute seasonal epidemics
- Staffing imbalances with lack of situational awareness across districts
- Inefficient inter-district resource distribution where one facility experiences stock-outs while another holds surplus stock expiring in storage

---

## 2. Core Idea & Mission

**HEALTHSYNC AI** transitions public healthcare administration from **passive monitoring** to **anticipatory decision intelligence**. 

The command center integrates:
$$\text{Current Status} + \text{Historical Telemetry} + \text{Patient Footfall} + \text{Consumption Velocity} + \text{Inpatient Beds} + \text{Clinical Workforce} + \text{AI Forecasting} + \text{Early Warning} + \text{Redistribution} + \text{What-If Simulation} + \text{Federated AI}$$

It directly answers the 10 vital operational questions for health directors:
1. **What is happening now?** Live KPI dashboard across 12,540 PHCs.
2. **What is likely to happen next?** Multi-horizon demand regression (7, 30, and 90 days).
3. **Which PHCs are at risk?** Automated sorting by Composite Resource Risk Index.
4. **Which medicines may run out?** Critical runway countdowns ($<48\text{ hours}$).
5. **How many days remain before stock-out?** Exact decimal stock-out timelines ($2.7\text{ days}$).
6. **Which district has surplus resources?** Identification of donor hubs with $>21\text{ days}$ runway.
7. **Which district needs those resources?** Deficit matching without donor depletion.
8. **What redistribution does AI recommend?** Specific transfer volumes, routes, and confidence ratings.
9. **What happens if demand increases by 10%, 20%, 30%, or 50%?** Non-destructive What-If stress testing.
10. **How can distributed healthcare data contribute to shared predictive modeling?** Privacy-preserving Federated AI architecture.

---

## 3. Technology Stack

- **Backend:** Python 3, Flask, Jinja2, Werkzeug
- **Database / ORM:** SQLite 3, SQLAlchemy, Flask-SQLAlchemy
- **Frontend / UI:** HTML5, CSS3, JavaScript (Fetch API / ES6+), Bootstrap 5.3, Font Awesome 6.5
- **GIS & Mapping:** Leaflet 1.9, Google Maps Style Tiles, Geolocation API, Haversine Distance Engine
- **Data Visualization:** Chart.js 4.4
- **Testing:** Pytest

---

## 4. Folder Structure

```
healthsync_ai/
│
├── run.py                       # Main application launcher
├── requirements.txt             # Clean, lightweight dependency definitions
├── README.md                    # Project manual & documentation
├── .env.example                 # Environment configuration template
├── .gitignore                   # Version control ignore rules
│
├── app/
│   ├── __init__.py              # Application factory, Jinja filters, auto-seeder
│   ├── config.py                # Environment configurations (Dev & Testing)
│   ├── extensions.py            # SQLAlchemy database extension
│   ├── models.py                # SQLAlchemy database models (12 tables)
│   │
│   ├── routes/
│   │   ├── __init__.py          # Blueprint registrations
│   │   ├── auth.py              # Login, session auth, and logout handlers
│   │   ├── main.py              # Web page views (Dashboard, Inventory, Alerts, etc.)
│   │   └── api.py               # REST API endpoints (CRUD, What-If, Export, etc.)
│   │
│   ├── services/
│   │   ├── __init__.py          # Services package exports
│   │   ├── seed.py              # Idempotent database seeder with realistic demo data
│   │   ├── forecast.py          # Predictive demand algorithm & What-If stress engine
│   │   ├── redistribution.py    # Surplus/deficit matching & approval engine
│   │   └── federation.py        # Federated learning simulator & BRICS node topology
│   │
│   ├── templates/
│   │   ├── base.html            # Command center layout, sidebar, header, and clock
│   │   ├── login.html           # Authentication portal with demo helper box
│   │   ├── dashboard.html       # Primary command dashboard with KPIs & forecast
│   │   ├── phcs.html            # Facility registry with search and modal form
│   │   ├── medicines.html       # Inventory ledger with live stockout timelines
│   │   ├── patients.html        # Outpatient footfall & triage surveillance
│   │   ├── beds.html            # Inpatient bed occupancy & capacity alerts
│   │   ├── staff.html           # Clinical workforce attendance & cadre breakdown
│   │   ├── forecast.html        # AI demand forecaster & What-If simulator sandbox
│   │   ├── alerts.html          # Early warning system with explainable evidence
│   │   ├── redistribution.html  # Inter-district transfer proposals & review workflow
│   │   ├── federated.html       # Federated learning edge architecture & BRICS view
│   │   ├── reports.html         # Executive reporting and audit trail governance
│   │   └── 404.html             # Command center 404 error page
│   │
│   └── static/
│       ├── css/
│       │   └── style.css        # Command center dark navy & cyan styles
│       └── js/
│           └── app.js           # AJAX communication, charts, simulator & modals
│
├── instance/                    # SQLite database store (auto-generated)
│   └── .gitkeep
│
├── tests/
│   └── test_routes.py           # 15 comprehensive unit & integration tests
│
└── docs/
    └── INNOVATION.md            # Detailed 10-innovation technical specification
```

---

## 5. Quick Start & Installation

### Step 1: Create and Activate Virtual Environment
```bash
# Windows
python -m venv .venv
.venv\Scripts\activate

# macOS / Linux
python3 -m venv .venv
source .venv/bin/activate
```

### Step 2: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 3: Run the Application
```bash
python run.py
```

### Step 4: Open in Web Browser
Open your browser and navigate to:
```
http://127.0.0.1:5000
```

---

## 6. Demo Credentials

The database is automatically initialized and seeded with realistic, fictional demonstration records on the first startup:

| Role | Email | Password | Access Level |
| :--- | :--- | :--- | :--- |
| **National Director (Admin)** | `admin@healthsync.gov` | `admin2026` | Full Command & Approval Privileges |
| **District Officer** | `officer@healthsync.gov` | `officer2026` | Facility Review & Telemetry Monitoring |

*(A convenient credential pre-fill helper is provided on the `/login` portal).*

---

## 7. Key Features & Innovations

1. **Predictive Runway Evaluation:** Calculates days until depletion using consumption velocity, patient surges, and therapeutic category trends.
2. **Autonomous Early Warnings:** Categorizes alerts into `CRITICAL`, `HIGH`, `MEDIUM`, and `LOW` with complete explainable evidence.
3. **Cross-District Rebalancing:** Matches surplus storage facilities with deficit outposts; transfers are executed only upon authorized officer confirmation.
4. **What-If Simulation Sandbox:** Allows planners to test $0\%$, $10\%$, $20\%$, $30\%$, and $50\%$ epidemiological demand surges in real time without mutating database records.
5. **Federated AI Demonstration:** Simulates privacy-preserving edge learning across 5 PHC nodes using Differential Privacy ($\varepsilon=1.2$) and FedAvg aggregation.
6. **BRICS Collaborative Architecture:** Demonstrates a conceptual shared predictive layer across India, Brazil, Russia, China, and South Africa.
7. **Complete Governance & Auditability:** Immutable logging of all logins, stock changes, and redistribution approvals, with one-click CSV export.

---

## 8. REST API Reference

| Endpoint | Method | Description |
| :--- | :--- | :--- |
| `POST /api/auth/login` | POST | Authenticate user credentials and establish session |
| `POST /api/auth/logout` | POST | Terminate session and record audit logout |
| `GET /api/dashboard/stats` | GET | Top KPIs, Risk Index, and 7-day forecast trends |
| `GET /api/phcs` | GET | Filterable PHC network registry (district, status, search) |
| `POST /api/phcs` | POST | Register new Primary Health Centre (persists to SQLite) |
| `GET /api/phcs/<id>` | GET | Fetch telemetry profile for a specific PHC |
| `PUT /api/phcs/<id>` | PUT | Update facility bed/staffing parameters |
| `DELETE /api/phcs/<id>` | DELETE | Remove facility from operational network |
| `GET /api/medicines` | GET | Inventory list with calculated stockout runway & risk |
| `POST /api/medicines` | POST | Add essential medicine formulation |
| `PUT /api/medicines/<id>` | PUT | Update stock count (triggers immediate timeline re-computation) |
| `DELETE /api/medicines/<id>` | DELETE | Remove medicine from inventory |
| `GET /api/patients` | GET | Outpatient footfall logs & 14-day emergency trends |
| `GET /api/beds` | GET | National and district bed capacity & occupancy rates |
| `GET /api/staff` | GET | Clinical workforce attendance by discipline |
| `GET /api/forecast` | GET | Multi-horizon demand predictions for all medicines |
| `POST /api/forecast/run` | POST | Trigger manual national forecast recalculation |
| `POST /api/forecast/what-if`| POST | Execute stress-test simulation with custom demand surge |
| `GET /api/alerts` | GET | Query active and resolved early warning alerts |
| `POST /api/alerts/<id>/resolve`| POST | Resolve alert with audit trail entry |
| `GET /api/redistribution` | GET | Query pending and executed transfer proposals |
| `POST /api/redistribution/<id>/approve`| POST | Approve transfer (adjusts stock & logs audit) |
| `POST /api/redistribution/<id>/reject` | POST | Reject transfer proposal |
| `GET /api/federated` | GET | Fetch federated round status and node states |
| `POST /api/federated/run` | POST | Execute a federated learning training round |
| `GET /api/reports/audit` | GET | Retrieve immutable audit event history |
| `GET /api/reports/export-csv` | GET | Export CSV report (`audit`, `medicines`, `alerts`, `redistribution`) |

---

## 9. Verification & Testing

The application includes 15 automated pytest tests covering authentication, views, CRUD, forecasting, What-If simulation, alerts, redistribution, and federated learning:

```bash
pytest healthsync_ai/tests -v
```

**Expected Result:**
```
============================= 15 passed in 10.69s =============================
```

---

## 10. Prototype & Demonstration Notice

> **IMPORTANT:**  
> This software is a working prototype developed for demonstration and hackathon evaluation. All hospital names, patient volumes, medicine balances, and federated parameters are **realistic fictional representations**. The platform does not connect to live government databases or transmit real patient records.
> Deployment Link : https://healthsync-ai-vy9i.onrender.com/login
