# Smart Parking System 

## 1. System Overview
This program manages a smart parking lot using user authentication. It allows users to register accounts, log in, track arriving vehicles, automatically calculate parking fees at exit, and view real-time space availability.

---

## 2. Key Data Structures (How Data is Stored)

* **Vehicle Database (`active_vehicles_db`)**
  * **Type:** Hash Map / Dictionary `{plate_number: arrival_time}`
  * **Purpose:** Stores each parked vehicle alongside its exact entry timestamp.
  * **Efficiency:** $O(1)$ constant time for instant lookups during entry and exit.

* **User Database (`user_credentials`)**
  * **Type:** Hash Map / Dictionary `{username: passkey}`
  * **Purpose:** Stores accounts and passwords.
  * **Efficiency:** $O(1)$ constant time for instant login checks.

* **Available Spaces (`free_spaces`)**
  * **Type:** Integer counter
  * **Purpose:** Keeps track of remaining open parking spots.

---

## 3. Database Schema

### Parked Vehicles Table
| Field Name | Data Type | Key Type | Description |

| `plate_number` | String | Primary Key | Unique vehicle license plate |
| `arrival_timestamp` | Float | Value | Exact time the vehicle entered |

### User Accounts Table
| Field Name | Data Type | Key Type | Description |

| `username` | String | Primary Key | Unique user account name |
| `passkey` | String | Value | User login password |

---

## 4. Step-by-Step Feature Logic

### 1. User Account Registration
1. Ask for desired `username` and `passkey`.
2. Check if `username` already exists in `user_credentials`.
3. **If taken:** Display an error message.
4. **If unique:** Save `username` and `passkey` into `user_credentials`.

### 2. User Login
1. Ask for `username` and `passkey`.
2. Check `user_credentials` for a matching key-value pair.
3. **If match:** Set user session to active.
4. **If no match:** Display "Invalid Credentials".

### 3. Vehicle Admission (Entry)
1. Verify user is logged in (deny access if not).
2. Check if `free_spaces > 0` (if 0, display "Parking Lot Full").
3. Prompt for vehicle `plate_number`.
4. Check if vehicle is already inside `active_vehicles_db`.
5. Record entry timestamp and store `active_vehicles_db[plate_number] = entry_time`.
6. Decrease `free_spaces` by 1.

### 4. Vehicle Exit & Billing
1. Verify user is logged in.
2. Prompt for vehicle `plate_number`.
3. Retrieve `arrival_time` from `active_vehicles_db` and delete the record.
4. Calculate duration: `exit_time - arrival_time`.
5. Calculate total fee based on duration and hourly rate.
6. Increase `free_spaces` by 1.
7. Print receipt showing total time, cost, and remaining spots.