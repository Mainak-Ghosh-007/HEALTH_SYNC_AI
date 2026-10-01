from datetime import datetime
import random
from app.extensions import db
from app.models import FederatedRound, AuditLog

# Simulated Local Edge Nodes (West Bengal Hospitals & PHCs in Federated Learning)
FEDERATED_NODES = [
    {
        "node_id": "PHC-WB-001",
        "name": "SSKM Hospital & IPGMER",
        "location": "Bhowanipore, Kolkata",
        "data_samples": 3850,
        "local_accuracy": 93.8,
        "local_loss": 0.074,
        "privacy_status": "Differential Privacy (ε=1.2, δ=10⁻⁵)",
        "gradient_updates": 480,
        "status": "Ready / Synced"
    },
    {
        "node_id": "PHC-WB-026",
        "name": "Burdwan Medical College & Hospital",
        "location": "Purba Bardhaman, WB",
        "data_samples": 2950,
        "local_accuracy": 92.6,
        "local_loss": 0.081,
        "privacy_status": "Differential Privacy (ε=1.2, δ=10⁻⁵)",
        "gradient_updates": 390,
        "status": "Ready / Synced"
    },
    {
        "node_id": "PHC-WB-011",
        "name": "Howrah District Hospital",
        "location": "Mallick Phatak, Howrah",
        "data_samples": 1450,
        "local_accuracy": 91.9,
        "local_loss": 0.088,
        "privacy_status": "Differential Privacy (ε=1.2, δ=10⁻⁵)",
        "gradient_updates": 310,
        "status": "Ready / Synced"
    },
    {
        "node_id": "PHC-WB-016",
        "name": "Chinsurah Imambara Sadar Hospital",
        "location": "Chinsurah, Hooghly",
        "data_samples": 1320,
        "local_accuracy": 91.5,
        "local_loss": 0.091,
        "privacy_status": "Differential Privacy (ε=1.2, δ=10⁻⁵)",
        "gradient_updates": 295,
        "status": "Ready / Synced"
    },
    {
        "node_id": "PHC-WB-021",
        "name": "College of Medicine & JNM Hospital",
        "location": "Kalyani, Nadia",
        "data_samples": 1820,
        "local_accuracy": 92.9,
        "local_loss": 0.079,
        "privacy_status": "Differential Privacy (ε=1.2, δ=10⁻⁵)",
        "gradient_updates": 360,
        "status": "Ready / Synced"
    }
]

# Conceptual BRICS Federated Collaboration Nodes
BRICS_NODES = [
    {
        "country": "India",
        "flag": "🇮🇳",
        "system_name": "NDHM / ICMR Health Intelligence Network",
        "participating_centres": "12,540 PHCs",
        "data_modality": "Epidemiological Trends & Cold-Chain Inventory",
        "privacy_protocol": "Homomorphic Encryption + DP-FedAvg",
        "status": "Active Demonstration Node"
    },
    {
        "country": "Brazil",
        "flag": "🇧🇷",
        "system_name": "SUS / DataSUS Unified Health Grid",
        "participating_centres": "9,800 UBS (Primary Units)",
        "data_modality": "Tropical Disease Outbreaks & Antiviral Buffer",
        "privacy_protocol": "Secure Multi-Party Computation (SMPC)",
        "status": "Conceptual Peer Node"
    },
    {
        "country": "Russia",
        "flag": "🇷🇺",
        "system_name": "EMIAS National Medical Coordination",
        "participating_centres": "7,400 Polyclinics",
        "data_modality": "Seasonal Respiratory & Antibiotic Reserves",
        "privacy_protocol": "Zero-Knowledge Proofs + FedAvg",
        "status": "Conceptual Peer Node"
    },
    {
        "country": "China",
        "flag": "🇨🇳",
        "system_name": "NHC National Primary Care Cloud",
        "participating_centres": "15,200 Township Health Centers",
        "data_modality": "Syndromic Surveillance & Regional Logistics",
        "privacy_protocol": "Secure Aggregator Protocol (SAP)",
        "status": "Conceptual Peer Node"
    },
    {
        "country": "South Africa",
        "flag": "🇿🇦",
        "system_name": "NHI District Health Information System",
        "participating_centres": "3,900 Primary Clinics",
        "data_modality": "Infectious Disease Surge & Essential Meds",
        "privacy_protocol": "Differential Privacy + Encrypted Gradients",
        "status": "Conceptual Peer Node"
    }
]

def get_federated_state():
    """Retrieve current federated rounds and node statuses."""
    rounds = FederatedRound.query.order_by(FederatedRound.round_number.desc()).all()
    latest_round = rounds[0] if rounds else None

    # Calculate aggregate metrics
    current_round_num = latest_round.round_number if latest_round else 4
    current_version = latest_round.model_version if latest_round else "v1.3.0"
    current_accuracy = latest_round.accuracy if latest_round else 92.5

    return {
        "current_round": current_round_num,
        "model_version": current_version,
        "global_accuracy": current_accuracy,
        "participating_nodes_count": len(FEDERATED_NODES),
        "total_data_samples": sum(n['data_samples'] for n in FEDERATED_NODES),
        "local_nodes": FEDERATED_NODES,
        "brics_nodes": BRICS_NODES,
        "history": [r.to_dict() for r in reversed(rounds)]
    }

def trigger_federated_round(user_id=None, ip_address="127.0.0.1"):
    """
    Simulate execution of a new Federated Training Round:
    1. Local edge models train on local PHC synthetic registries.
    2. Model weights / gradients are encrypted and aggregated using FedAvg.
    3. Global model accuracy is updated and version bumped.
    4. Persists into SQLite FederatedRound and AuditLog.
    """
    latest = FederatedRound.query.order_by(FederatedRound.round_number.desc()).first()
    next_round_num = (latest.round_number + 1) if latest else 5

    # Incremental accuracy improvement with diminishing returns
    prev_acc = latest.accuracy if latest else 92.5
    improvement = round(random.uniform(0.35, 0.75) * max(0.2, (100.0 - prev_acc) / 10.0), 2)
    new_acc = min(98.8, round(prev_acc + improvement, 2))

    major = 1
    minor = next_round_num
    patch = 0
    new_version = f"v{major}.{minor}.{patch}"

    # Update simulated node states
    for node in FEDERATED_NODES:
        node['data_samples'] += random.randint(30, 80)
        node['gradient_updates'] += random.randint(25, 45)
        node['local_accuracy'] = min(98.5, round(node['local_accuracy'] + random.uniform(0.1, 0.5), 2))
        node['local_loss'] = max(0.02, round(node['local_loss'] - 0.005, 3))
        node['status'] = f"Round {next_round_num} Aggregated"

    new_round = FederatedRound(
        round_number=next_round_num,
        participating_nodes=len(FEDERATED_NODES),
        model_version=new_version,
        accuracy=new_acc,
        status="COMPLETED",
        created_at=datetime.utcnow()
    )
    db.session.add(new_round)

    audit = AuditLog(
        user_id=user_id,
        action="FEDERATED_ROUND_COMPLETED",
        description=f"Completed Federated Learning Round {next_round_num}. Aggregated 5 local PHC edge nodes using FedAvg. Model version updated to {new_version} with Global Accuracy {new_acc}%.",
        timestamp=datetime.utcnow(),
        ip_address=ip_address
    )
    db.session.add(audit)
    db.session.commit()

    return {
        "success": True,
        "round_number": next_round_num,
        "model_version": new_version,
        "accuracy": new_acc,
        "accuracy_gain": improvement,
        "participating_nodes": len(FEDERATED_NODES)
    }
