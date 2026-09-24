# Data Structures and Algorithms - Task One Documentation

**System Type:** Web Application with a User Interface
**Tools Used:** Python (Flask), Jinja2 HTML, Tailwind CSS
**Kenya

---

## 1. System Design

The system uses a simple Model-View-Controller (MVC) setup:

*   **Frontend** Web pages built with HTML and styled with Tailwind CSS. It has pop-up boxes for clicking and selecting parking spaces directly.
*   **Backend** A Python Flask server that runs in the background and handles all the button clicks and data processing.
*   **Database (Data storage):** We use fast Python Hash Maps and a List to store data in the computer's active memory. This makes finding and saving data instant.

---

## 2. The 8 System Modules

### Module 1: Live Parking Slot Display
*   **Action:** When you open the home page.
*   **Steps:**
    1. Read the current status of all 15 parking bays.
    2. Show green, clickable buttons for empty bays.
    3. Show red, unclickable boxes for bays that already have a car.

### Module 2: Car Entry & Slot Assignment
*   **Action:** When a car arrives at the gate.
*   **Steps:**
    1. Take the car's number plate.
    2. Check if the parking lot is completely full (all 15 spots taken).
    3. Check if this exact car is already parked inside.
    4. **Assign a spot:** If the user clicked a specific green bay, assign that one. If not, automatically find the very first empty bay.
    5. Save the car's plate, its assigned bay, and the exact arrival time.
    6. Show a success message.

### Module 3: Price Calculation
*   **Action:** A background task when a car wants to leave.
*   **Steps:**
    1. Calculate how many hours the car stayed (current time minus arrival time).
    2. Calculate the basic cost (hours multiplied by the hourly rate).
    3. Calculate the 16% VAT tax.
    4. Add the tax to the basic cost to get the final total.

### Module 4: Payment System
*   **Action:** When the driver pays at the exit.
*   **Steps:**
    1. Take the number plate and how they want to pay (M-Pesa, Card, or Cash).
    2. Get the final price from Module 3.
    3. Create a unique receipt number (like TX-A1B2).
    4. Save the full payment details to the permanent record book (Audit Log).

### Module 5: Exit Gate Control
*   **Action:** Happens right after the payment is successful.
*   **Steps:**
    1. Confirm the payment went through.
    2. Mark the exit gate as "OPEN".
    3. Empty the parking bay so someone else can use it.
    4. Delete the car's active session from the system.

### Module 6: Changing the Parking Price
*   **Action:** When an admin wants to increase or decrease the hourly fee.
*   **Steps:**
    1. Take the new price typed by the admin.
    2. Check that the new price is a valid number greater than zero.
    3. Instantly apply the new price for all future calculations.

### Module 7: Financial Records & Tax Report
*   **Action:** Displaying the records table on the dashboard.
*   **Steps:**
    1. Read the list of all saved receipts.
    2. Create a neat table showing the date, receipt number, number plate, payment method, basic fee, VAT tax, and total money collected.

### Module 8: Admin Emergency Clear
*   **Action:** If a car leaves without paying or there is a system error.
*   **Steps:**
    1. The admin types in the number plate.
    2. The system finds which bay the car was using.
    3. The system forcefully empties that bay and deletes the car's record.

---

## 3. Data Structures Used

| Tool Used | Variable Name | Purpose | Speed | Why we chose it |
| :--- | :--- | :--- | :--- | :--- |
| **Hash Map ** | `slots` | Tracks 15 bays | Instant | Enable checking if a specific bay is empty or full immediately. |
| **Hash Map ** | `vehicles` | Tracks parked cars | Instant | Lets us find a car's arrival time instantly using its number plate. |
| **List (Array)** | `audit_log` | Saves receipts | Instant | Easy and fast to just add new receipts to the bottom of the list. |

---

## 4. How Data is Saved (Database Tables)

Even though we use computer memory instead of a real database, this is how the data is organized:

### 1. The Parking Bays Table
*   **Bay ID:** A number from 1 to 15.
*   **Car Plate:** The number plate of the car parked there (or empty).

### 2. The Active Cars Table
*   **Car Plate:** The unique number plate of the car.
*   **Bay Number:** Where the car is currently parked.
*   **Arrival Time:** The exact second the car entered.

### 3. The Receipts Table (Audit Log)
*   **Receipt ID:** A unique code for the payment.
*   **Car Plate:**
*   **Time Spent:** 
*   **Payment Method:** M-Pesa, Card, or Cash.
*   **Basic Cost:** Money charged before tax.
*   **VAT (16%):** Government tax.
*   **Total Paid:** The final amount handed over.
*   **Date & Time:** When the payment happened.
