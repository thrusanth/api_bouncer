# Realogram API Bouncer 🛡️📦

> An edge-to-cloud computer vision (CV) interceptor and reconciliation middleware designed to bridge automated shelf monitoring with core retail inventory management systems.

## Overview

In modern retail store execution, computer vision cameras monitor shelves in real time. However, a major architectural friction point arises when physical reality diverges from digital stock ledgers—such as human shortcuts (e.g., leaving pallet wrap on multipacks) or damaged inventory (e.g., torn multipacks exposing loose units). 

**Realogram API Bouncer** acts as an event-driven validation layer sitting between edge cameras and core enterprise systems. It intercepts non-compliant shelf states, executes dynamic **BOM (Bill of Materials) decompositions**, dynamically calculates proportional markdown prices, enforces strict regional UK alcohol compliance laws, and dispatches handheld PDA / thermal printer tasks for instant shop-floor intervention.

---



## Key Features

- **Edge API Key Authentication**: Secures ingress webhook traffic from edge compute nodes using token-based header validation (`X-API-Key`).
- **Universal EAN Standards**: Maps internal SKUs directly to global 13-digit GS1 EAN barcodes for universal supply chain interoperability.
- **Audit Trace ID Generation**: Assigns immutable, unique UUID trace IDs to every single shelf scan for end-to-end idempotency and event auditing.
- **Dynamic BOM Decomposition**: Automatically decomposes compromised parent multipacks into loose single-unit waste adjustments when packaging integrity fails.
- **Universal Proportional Pricing**: Dynamically derives the correct single-unit markdown price by calculating mathematical proportional splits (`Parent Retail Price ÷ Pack Quantity`).
- **Multi-Region Alcohol Compliance**: Enforces statutory legal pricing floors using strict `max()` boundary logic to prevent non-compliant markdowns:
  - **England**: Enforces the commercial **Duty + VAT** minimum floor.
  - **Scotland & Wales**: Enforces statutory **Minimum Unit Pricing (MUP)** floors based on product ABV strength and liquid volume.
- **PDA Markdown Task Dispatch**: Generates automated thermal printer and handheld PDA tasks to guide store colleagues on rapid price overrides and legally compliant markdown placements.
- **Live SaaS Dashboard**: Features a mobile-friendly, real-time web dashboard rendering audit logs, format alerts, compliance rule applications, and live pricing derivations.

---



## Tech Stack

- **Backend / Middleware**: FastAPI (Python)
- **Data Validation**: Pydantic models with strict type enforcement
- **Server**: Uvicorn (ASGI)
- **Simulation Client**: Python `requests` (emulating multi-product, multi-region edge camera telemetry)

---



## Project Structure

```text
realogram-api-bouncer/
├── main.py          # FastAPI application, bouncer logic, central ledger, and live dashboard
├── simulator.py     # Edge camera telemetry simulator sending authenticated multi-region webhooks
└── README.md        # Project documentation
```

