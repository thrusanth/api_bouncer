import requests
import time
from datetime import datetime

WEBHOOK_URL = "http://127.0.0.1:8000/webhook/cv-detection"

HEADERS = {
    "X-API-Key": "edge-cam-prod-992-xtz"
}

scenarios = [
    {
        "name": "1. Water 6PK: Perfect Shelf Fill (Clean Sync)", 
        "payload": {
            "store_region": "ENG",
            "parent_sku": "SKU-WATER-6PK", 
            "detected_quantity": 20, 
            "physical_location": "Aisle-4-Bay-2", 
            "detected_format": "SHRINK_WRAPPED_MULTIPACK",  # Matches central ledger exactly
            "loose_units_visible": 0, 
            "timestamp": datetime.utcnow().isoformat(), 
            "confidence_score": 0.99
        }
    },
    {
        "name": "2. Water 6PK in England (£3.00 retail -> £3.00 ÷ 6 = £0.50 per unit)", 
        "payload": {
            "store_region": "ENG",
            "parent_sku": "SKU-WATER-6PK", 
            "detected_quantity": 19, 
            "physical_location": "Aisle-4-Bay-2", 
            "detected_format": "TORN_MULTIPACK", 
            "loose_units_visible": 3,  # Varied to 3 loose units
            "timestamp": datetime.utcnow().isoformat(), 
            "confidence_score": 0.99
        }
    },
    {
        "name": "3. Baked Beans 4PK in England (£2.40 retail -> £2.40 ÷ 4 = £0.60 per unit)", 
        "payload": {
            "store_region": "ENG",
            "parent_sku": "SKU-BEANS-4PK", 
            "detected_quantity": 29, 
            "physical_location": "Aisle-2-Bay-4", 
            "detected_format": "TORN_MULTIPACK", 
            "loose_units_visible": 1,  # Varied to 1 loose unit
            "timestamp": datetime.utcnow().isoformat(), 
            "confidence_score": 0.97
        }
    },
    {
        "name": "4. Lager 4PK in England (£6.00 retail -> £6.00 ÷ 4 = £1.50 vs Duty+VAT floor)", 
        "payload": {
            "store_region": "ENG",
            "parent_sku": "SKU-LAGER-4PK", 
            "detected_quantity": 14, 
            "physical_location": "Aisle-4-Bay-1", 
            "detected_format": "TORN_MULTIPACK", 
            "loose_units_visible": 2,  # Kept as 2 loose units
            "timestamp": datetime.utcnow().isoformat(), 
            "confidence_score": 0.98
        }
    },
    {
        "name": "5. Cider 4PK in Scotland (£4.00 retail -> £4.00 ÷ 4 = £1.00 overridden by MUP floor)", 
        "payload": {
            "store_region": "SCO",
            "parent_sku": "SKU-CIDER-4PK", 
            "detected_quantity": 10, 
            "physical_location": "Aisle-4-Bay-3", 
            "detected_format": "TORN_MULTIPACK", 
            "loose_units_visible": 3,  # Varied to 3 loose units
            "timestamp": datetime.utcnow().isoformat(), 
            "confidence_score": 0.97
        }
    },
    {
        "name": "6. Beer 10PK in Wales (£11.00 retail -> £11.00 ÷ 10 = £1.10 overridden by MUP floor)", 
        "payload": {
            "store_region": "WAL",
            "parent_sku": "SKU-BEER-10PK", 
            "detected_quantity": 8, 
            "physical_location": "Aisle-4-Bay-4", 
            "detected_format": "TORN_MULTIPACK", 
            "loose_units_visible": 6,  # Varied to 6 loose units
            "timestamp": datetime.utcnow().isoformat(), 
            "confidence_score": 0.99
        }
    }
]

print("Starting Multi-Product & Compliance Math Simulation...\n")
for idx, scenario in enumerate(scenarios):
    print(f"[{idx+1}/{len(scenarios)}] Transmitting: {scenario['name']}")
    
    response = requests.post(WEBHOOK_URL, json=scenario["payload"], headers=HEADERS)
    
    if response.status_code == 200:
        res_data = response.json()
        print(f" -> Success! Trace ID: {res_data.get('trace_id')}")
        if res_data.get('label_print_task'):
            print(f"    🖨️ PDA Print Task Dispatched: {res_data['label_print_task']['price_override_instruction']}")
        else:
            print(f"    ✅ Clean Sync Verified (No action required)")
    else:
        print(f" -> Failed! Status: {response.status_code} | Detail: {response.text}")
        
    time.sleep(2)

print("\nSimulation complete! View the live dashboard at http://127.0.0.1:8000/dashboard")