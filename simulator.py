import requests
import time
from datetime import datetime

WEBHOOK_URL = "http://127.0.0.1:8000/webhook/cv-detection"

# --- Enterprise Security Token Header ---
HEADERS = {
    "X-API-Key": "edge-cam-prod-992-xtz"
}

scenarios = [
    {
        "name": "Water: Perfect Shelf", 
        "payload": {
            "parent_sku": "SKU-WATER-6PK", 
            "detected_quantity": 20, 
            "physical_location": "Aisle-4-Bay-2", 
            "detected_format": "SHRINK_WRAPPED_MULTIPACK", 
            "loose_units_visible": 0, 
            "timestamp": datetime.utcnow().isoformat(), 
            "confidence_score": 0.99
        }
    },
    {
        "name": "Water: Pallet Wrap Left On (Human Shortcut)", 
        "payload": {
            "parent_sku": "SKU-WATER-6PK", 
            "detected_quantity": 20, 
            "physical_location": "Aisle-4-Bay-2", 
            "detected_format": "PALLET_WRAP_LEFT_ON", 
            "loose_units_visible": 0, 
            "timestamp": datetime.utcnow().isoformat(), 
            "confidence_score": 0.95
        }
    },
    {
        "name": "Water: Torn Multipack (4 Loose Units)", 
        "payload": {
            "parent_sku": "SKU-WATER-6PK", 
            "detected_quantity": 19, 
            "physical_location": "Aisle-4-Bay-2", 
            "detected_format": "TORN_MULTIPACK", 
            "loose_units_visible": 4, 
            "timestamp": datetime.utcnow().isoformat(), 
            "confidence_score": 0.98
        }
    },
    {
        "name": "Baked Beans: Torn Multipack (2 Loose Units)", 
        "payload": {
            "parent_sku": "SKU-BEANS-4PK", 
            "detected_quantity": 29, 
            "physical_location": "Aisle-2-Bay-4", 
            "detected_format": "TORN_MULTIPACK", 
            "loose_units_visible": 2, 
            "timestamp": datetime.utcnow().isoformat(), 
            "confidence_score": 0.97
        }
    }
]

print("Starting Multi-Product Authenticated CV Edge Simulator...\n")
for idx, scenario in enumerate(scenarios):
    print(f"[{idx+1}/{len(scenarios)}] Transmitting: {scenario['name']}")
    
    # Transmitting payload with API Key Header
    response = requests.post(WEBHOOK_URL, json=scenario["payload"], headers=HEADERS)
    
    if response.status_code == 200:
        res_data = response.json()
        print(f" -> Success! Trace ID: {res_data.get('trace_id')}")
        if res_data.get('label_print_task'):
            print(f"    🖨️ PDA Print Task Dispatched for: {res_data['label_print_task']['encoded_sku']}")
    else:
        print(f" -> Failed! Status: {response.status_code} | Detail: {response.text}")
        
    time.sleep(2)

print("\nSimulation complete! View the live dashboard at http://127.0.0.1:8000/dashboard")