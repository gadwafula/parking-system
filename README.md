# Smart Parking Management System

**Course:** Data Structures and Algorithms - Task One  
**Institution:** Multimedia University of Kenya (MMU) / Republic of Kenya  
**Stack:** Python (Flask), Jinja2 HTML Templating, Tailwind CSS  

---

## 📋 Overview

The **Smart Parking Management System** is a locally hosted web application built to manage a 15-bay dynamic parking facility in real time. Designed using a Model-View-Controller (MVC) monolithic architecture, the system provides an interactive visual interface for bay allocation, automatic fee calculation with 16% statutory VAT, payment processing, dynamic tariff adjustments, and financial audit reporting.

---

## 🏗️ System Architecture & Data Structures

The application utilizes in-memory data structures to ensure constant-time $O(1)$ operations without database query latency:

| Data Structure | Implementation Variable | Role & Function | Time Complexity |
| :--- | :--- | :--- | :--- |
| **Hash Map** | `slots` | Maps Bay IDs (1 to 15) to parked vehicle plate numbers | $O(1)$ |
| **Hash Map** | `vehicles` | Maps License Plate to active session details `{bay, entry_time}` | $O(1)$ |
| **List / Array** | `audit_log` | Append-only chronological financial ledger for payment receipts | $O(1)$ Append |

---

## ⚙️ Core System Modules

1. **Live Visual Slot Display:** Real-time 15-bay visual grid with dynamic status cards (Green = Vacant, Red = Occupied) and interactive modal pop-ups.
2. **Dual-Mode Entry Control:** Supports both automatic first-available slot allocation and manual direct bay selection via modal clicks.
3. **Fee Computation Engine:** Automated billing module calculating time stayed, minimum 1-hour base rates, and 16% Kenya Value-Added Tax (VAT).
4. **Multi-Channel Payment Gateway:** Handles exit processing via **Mobile Money / M-Pesa**, **Credit/Debit Card**, or **Cash**, generating unique transaction receipt IDs (e.g., `TX-8F12A9C0`).
5. **Exit Barrier Gate Control:** Automated gate control that verifies payment, sets barrier status to `OPEN (PAID)`, clears the slot, and purges active session memory.
6. **Dynamic Rate Management:** Administrative controls allowing real-time adjustment of hourly rates without restarting the web server.
7. **Auditable Financial Reporting:** Generates a real-time transaction ledger rendering timestamps, net parking fees, 16% VAT breakdown, and gross revenue.
8. **Administrative Overrides:** Emergency administrative tool to force-clear occupied bays during system exceptions or emergency exits.

---

## 📂 Project Structure

```text
parking-system/
│
├── main.py              # Flask Web Server & Core Logic Controller
├── docs/
│   └── algorithm.md     # System Algorithm Specification & Pseudocode
└── README.md            # System Documentation & Execution Guide
