from fastapi import FastAPI, HTTPException, status, Header
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from typing import Dict, Optional
from datetime import datetime
import uuid

app = FastAPI(title="Realogram API Bouncer", description="Edge CV Format Violation Interceptor & Reconciliation Engine")

reconciliation_logs = []

# --- Enterprise Security Token ---
VALID_EDGE_TOKEN = "edge-cam-prod-992-xtz"

class ExpectedLedger(BaseModel):
    parent_sku: str
    ean: str
    expected_quantity: int
    planogram_location: str
    expected_format: str
    linked_child_sku: str 

class CVEdgeDetection(BaseModel):
    parent_sku: str
    detected_quantity: int
    physical_location: str
    detected_format: str 
    loose_units_visible: int 
    timestamp: datetime
    confidence_score: float

class TransactionEnginePayload(BaseModel):
    transaction_type: str
    reason_code: str
    ledger_adjustments: Dict[str, int] 

class LabelPrintPayload(BaseModel):
    printer_target: str
    barcode_format: str
    encoded_sku: str
    item_trace_id: str
    price_override_instruction: str

class ShelfReconciliation(BaseModel):
    trace_id: str
    sku: str
    ean: str
    status: str
    format_alert: str
    shop_floor_action: str
    transaction_engine_hook: Optional[TransactionEnginePayload] = None
    label_print_task: Optional[LabelPrintPayload] = None

central_ledger_db = {
    "SKU-WATER-6PK": ExpectedLedger(
        parent_sku="SKU-WATER-6PK", 
        ean="5051410987654",
        expected_quantity=20, 
        planogram_location="Aisle-4-Bay-2",
        expected_format="SHRINK_WRAPPED_MULTIPACK",
        linked_child_sku="SKU-WATER-SINGLE"
    ),
    "SKU-BEANS-4PK": ExpectedLedger(
        parent_sku="SKU-BEANS-4PK", 
        ean="5051420123456",
        expected_quantity=30, 
        planogram_location="Aisle-2-Bay-4",
        expected_format="SHRINK_WRAPPED_MULTIPACK",
        linked_child_sku="SKU-BEANS-SINGLE"
    )
}

@app.post("/webhook/cv-detection", response_model=ShelfReconciliation)
def process_edge_detection(payload: CVEdgeDetection, x_api_key: str = Header(None)):
    # 1. Edge Authentication Check (The Bouncer Gatekeeper)
    if x_api_key != VALID_EDGE_TOKEN:
        raise HTTPException(status_code=401, detail="Unauthorized: Invalid Edge Camera Token")

    if payload.confidence_score < 0.85:
        raise HTTPException(status_code=422, detail="CV confidence too low.")

    ledger_data = central_ledger_db.get(payload.parent_sku)
    if not ledger_data:
        raise HTTPException(status_code=404, detail="SKU not found.")

    format_alert = "PASS"
    status_code = "SYNCED"
    shop_floor_action = "NONE"
    transaction_payload = None
    label_task = None
    
    # 2. Generate Audit Trace ID for Idempotency & Tracking
    audit_trace_id = f"TRX-{uuid.uuid4().hex[:8].upper()}"

    if payload.detected_format != ledger_data.expected_format:
        if payload.detected_format == "TORN_MULTIPACK" and payload.loose_units_visible > 0:
            status_code = "FORMAT_VIOLATION_TORN_PACK"
            format_alert = f"Torn Multipack Detected! {payload.loose_units_visible} loose units exposed."
            shop_floor_action = "DISPATCH_COLLEAGUE: Remove loose units & attach markdown label."
            
            # Dynamic BOM Decomposition Write-off accounting for real-world variance
            transaction_payload = TransactionEnginePayload(
                transaction_type="BOM_DECOMPOSITION_WRITE_OFF",
                reason_code="DAMAGED_FORMAT_MULTIPACK_COMPROMISED",
                ledger_adjustments={
                    payload.parent_sku: -1, 
                    ledger_data.linked_child_sku + "-WASTE": payload.loose_units_visible
                }
            )
            
            # Dynamic Label Generation Task for PDA / Thermal Printing
            label_task = LabelPrintPayload(
                printer_target=f"{payload.physical_location}-ZPL-PRINTER",
                barcode_format="CODE128",
                encoded_sku=ledger_data.linked_child_sku,
                item_trace_id=audit_trace_id,
                price_override_instruction="SINGLE_UNIT_MARKDOWN_OVERRIDE"
            )
        else:
            status_code = "FORMAT_VIOLATION_GENERAL"
            format_alert = f"Expected {ledger_data.expected_format}, found {payload.detected_format}."
            shop_floor_action = "DISPATCH_COLLEAGUE: Correct presentation format."

    result = ShelfReconciliation(
        trace_id=audit_trace_id, 
        sku=payload.parent_sku, 
        ean=ledger_data.ean,
        status=status_code, 
        format_alert=format_alert,
        shop_floor_action=shop_floor_action, 
        transaction_engine_hook=transaction_payload,
        label_print_task=label_task
    )
    reconciliation_logs.append(result)
    return result

@app.get("/dashboard", response_class=HTMLResponse)
def get_dashboard():
    rows = ""
    for log in reversed(reconciliation_logs):
        tx_data = "<span class='empty-state'>N/A</span>"
        if log.transaction_engine_hook:
            tx_data = f"<div class='tx-data'><strong>TxType:</strong> {log.transaction_engine_hook.transaction_type}<br><strong>Adj:</strong> {log.transaction_engine_hook.ledger_adjustments}</div>"
        
        label_data = ""
        if log.label_print_task:
            label_data = f"<div class='label-data'>🖨️ <strong>PDA Print Task:</strong> {log.label_print_task.encoded_sku} ({log.label_print_task.price_override_instruction})</div>"
        
        status_class = "violation" if "VIOLATION" in log.status else "synced"
        status_icon = "⚠️" if "VIOLATION" in log.status else "✅"
        
        rows += f"""
        <tr>
            <td>
                <span class='trace-id'>{log.trace_id}</span><br>
                <span class='sku-label'>{log.sku}</span><br>
                <span class='ean-label'>EAN: {log.ean}</span>
            </td>
            <td><span class='badge {status_class}'>{status_icon} {log.status}</span></td>
            <td><span class='alert-text'>{log.format_alert}</span></td>
            <td><span class='action-text'>{log.shop_floor_action}</span></td>
            <td>{tx_data}{label_data}</td>
        </tr>
        """
        
    return f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Format Violation Bouncer</title>
        <style>
            :root {{ --bg: #f8fafc; --surface: #ffffff; --text: #334155; --border: #e2e8f0; --brand: #0f172a; }}
            body {{ font-family: system-ui, -apple-system, sans-serif; background: var(--bg); color: var(--text); padding: 20px; margin: 0; line-height: 1.5; }}
            .container {{ max-width: 1200px; margin: 0 auto; }}
            h2 {{ color: var(--brand); margin-bottom: 20px; font-size: 1.5rem; letter-spacing: -0.02em; }}
            .table-wrapper {{ background: var(--surface); border-radius: 10px; box-shadow: 0 4px 6px -1px rgb(0 0 0 / 0.05); overflow-x: auto; border: 1px solid var(--border); }}
            table {{ width: 100%; border-collapse: collapse; min-width: 900px; }}
            th, td {{ padding: 16px 20px; text-align: left; border-bottom: 1px solid var(--border); vertical-align: middle; }}
            th {{ background: #f8fafc; font-weight: 600; color: #64748b; text-transform: uppercase; font-size: 0.75rem; letter-spacing: 0.05em; }}
            .sku-label {{ font-weight: 700; color: #0f172a; }}
            .trace-id {{ font-family: ui-monospace, monospace; font-size: 0.7rem; color: #94a3b8; letter-spacing: 0.05em; }}
            .ean-label {{ font-family: ui-monospace, monospace; font-size: 0.75rem; color: #64748b; letter-spacing: 0.02em; }}
            .badge {{ padding: 6px 12px; border-radius: 6px; font-weight: 600; font-size: 0.75rem; display: inline-flex; align-items: center; gap: 6px; white-space: nowrap; font-family: ui-monospace, monospace; letter-spacing: -0.02em; }}
            .badge.violation {{ background: #fef2f2; color: #b91c1c; border: 1px solid #fecaca; box-shadow: 0 1px 2px rgba(185,28,28,0.05); }}
            .badge.synced {{ background: #f0fdf4; color: #15803d; border: 1px solid #bbf7d0; box-shadow: 0 1px 2px rgba(21,128,61,0.05); }}
            .alert-text {{ font-weight: 500; color: #1e293b; font-size: 0.95rem; line-height: 1.4; display: block; }}
            .action-text {{ color: #475569; font-size: 0.9rem; }}
            .tx-data {{ background: #fff7ed; border-left: 3px solid #f97316; padding: 8px 12px; font-family: ui-monospace, monospace; font-size: 0.75rem; color: #9a3412; border-radius: 0 6px 6px 0; line-height: 1.4; margin-bottom: 4px; }}
            .label-data {{ background: #f1f5f9; border-left: 3px solid #64748b; padding: 6px 12px; font-family: ui-monospace, monospace; font-size: 0.75rem; color: #334155; border-radius: 0 6px 6px 0; }}
            .empty-state {{ color: #94a3b8; font-style: italic; font-size: 0.9rem; }}
            @media (max-width: 600px) {{ body {{ padding: 10px; }} h2 {{ font-size: 1.25rem; padding-left: 5px; }} th, td {{ padding: 12px 16px; }} }}
        </style>
    </head>
    <body>
        <div class="container">
            <h2>Live Reconciliation Dashboard</h2>
            <div class="table-wrapper">
                <table>
                    <thead>
                        <tr>
                            <th>Audit Trace / Product & EAN</th>
                            <th>Intercept Status</th>
                            <th>Format Alert</th>
                            <th>Shop-Floor Action</th>
                            <th>Transaction & Label Payload</th>
                        </tr>
                    </thead>
                    <tbody>
                        {rows}
                    </tbody>
                </table>
            </div>
        </div>
    </body>
    </html>
    """