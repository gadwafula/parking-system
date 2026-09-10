# Data Structures and Algorithms - Task One Solutions

## Task Overview
This document outlines the architectural analysis, system algorithms, data structure justifications, and dynamic database design for an automated parking system in Kenya based on the client terms of reference.

---

## (a) Module Algorithms

### Module 1: Live Visual Display Module
1. Iterate through the physical slot records in the `slots` Hash Map.
2. Count vacant slots where `plate == None` and occupied slots where `plate != None`.
3. Output the total capacity, number of available slots, and an ASCII grid showing slot statuses (VACANT vs. OCCUPIED).

### Module 2: Vehicle Arrival & Entry Module
1. Check if `available_slots > 0`. If equal to 0, deny entry and output "Parking Lot Full".
2. Display the live visual slot grid to the driver.
3. Capture the vehicle `plate_number`.
4. Verify `plate_number` is not currently inside `vehicles` dictionary.
5. Assign the first available `slot_id`.
6. Record system timestamp `entry_time = current_time()`.
7. Store details in dynamic state tables and open the entry barrier.

### Module 3: Exit & Automated Billing Module
1. Prompt for vehicle `plate_number`.
2. Locate record in `vehicles` Hash Map.
3. Record `exit_time = current_time()`.
4. Calculate duration: `duration = exit_time - entry_time`.
5. Compute total amount payable: `amount_due = max(HOURLY_RATE, duration_hours * HOURLY_RATE)`.
6. Generate and display receipt invoice to the user.

### Module 4: Payment Processing & Barrier Gate Control Module
1. Receive payment confirmation status.
2. IF payment is verified:
   - Trigger signal to open exit barrier gate.
   - Remove vehicle entry from `vehicles` database.
   - Set slot status in `slots` database to `VACANT`.
   - Close exit barrier gate after vehicle clears sensors.
3. ELSE:
   - Keep exit barrier gate locked/closed.

---

## (b) Data Structures and Justifications

* **Hash Map / Dictionary (`vehicles`)**
  * **Description:** Stores key-value pairs where `key = plate_number` and `value = {slot_id, entry_time}`.
  * **Justification:** Offers $O(1)$ constant time complexity for instant vehicle lookups, entry logs, and exit fee queries.

* **Hash Map / Dictionary (`slots`)**
  * **Description:** Stores slot status mappings where `key = slot_id` and `value = plate_number / None`.
  * **Justification:** Enables instant state tracking and rapid dynamic slot allocation in $O(1)$ time.

* **Floating-Point Primitive (`entry_time` / `exit_time`)**
  * **Description:** Stores high-precision Unix epoch timestamps.
  * **Justification:** Allows exact floating-point subtraction for precise parking duration calculations.

---

## (c) Dynamic Database Design

The system utilizes an in-memory dynamic relational mapping model representing key entities:

### 1. Slots Entity Table (`slots`)
| Field | Data Type | Key Type | Description |
| :--- | :--- | :--- | :--- |
| `slot_id` | Integer | Primary Key | Unique slot identifier (1 to N) |
| `assigned_plate` | String / Null | Foreign Key | License plate occupying slot (Null if vacant) |

### 2. Vehicle Session Table (`vehicles`)
| Field | Data Type | Key Type | Description |
| :--- | :--- | :--- | :--- |
| `plate_number` | String | Primary Key | Unique registration plate |
| `slot_id` | Integer | Foreign Key | Reference to occupied physical slot |
| `entry_time` | Timestamp | Attribute | Exact system arrival time |

### 3. Payment & Gate Log Transaction Schema
| Field | Data Type | Description |
| :--- | :--- | :--- |
| `transaction_id` | Auto-UUID | Unique transaction record |
| `plate_number` | String | Vehicle processed |
| `total_duration` | Float | Time spent in parking |
| `amount_paid` | Float | Parking fee paid in KES |
| `barrier_status` | Boolean | True = Gate Released upon payment |