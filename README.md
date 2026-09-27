# 🚗 Smart Parking Management System

**Course / Project:** Data Structures and Algorithms - Task One

**Location:** Multimedia University of Kenya (MMU) / Republic of Kenya

**Tech Stack:** Python (Flask), Jinja2 HTML, Tailwind CSS

A web-based parking management system that demonstrates the practical application of Data Structures and Algorithms (DSA). It features a live 15-bay visual grid, dynamic fee calculation, and an in-memory database utilizing O(1) constant-time operations.

## 🚀 How to Run the Project Locally

1. **Clone the repository:**

   ```
   git clone https://github.com/YOUR-USERNAME/YOUR-REPO-NAME.git
   cd YOUR-REPO-NAME
   
   ```

2. **Install required tools (Flask):**

   ```
   pip install flask
   
   ```

3. **Run the application:**

   ```
   python main.py
   
   ```

4. **Open your browser:**
   Go to `http://127.0.0.1:5000`

## 🏗️ 1. System Design (Architecture)

This project is built using a simple **Model-View-Controller (MVC)** setup:

* **Frontend (View):** Web pages built with HTML and styled with Tailwind CSS. It includes interactive pop-up modals for selecting parking spaces directly.

* **Backend (Controller):** A Python Flask server that handles all button clicks, form submissions, and data processing.

* **Database (Model):** We use fast Python Hash Maps (Dictionaries) and a List to store data in the computer's active memory (RAM). This makes reading and writing data instant.

## ⚙️ 2. The 8 System Modules

### Module 1: Live Parking Slot Display

* **Action:** When you open the home page.

* **How it works:** Reads the status of all 15 parking bays. Shows green, clickable buttons for empty bays and red, unclickable boxes for occupied bays.

### Module 2: Car Entry & Slot Assignment

* **Action:** When a car arrives at the gate.

* **How it works:** Checks if the lot is full or if the car is already parked. If a user clicks a specific green bay, it assigns that one. Otherwise, it automatically finds the first empty bay. It then saves the car's plate, bay, and exact arrival time.

### Module 3: Price Calculation

* **Action:** A background task when a car wants to leave.

* **How it works:** Calculates the hours spent (current time minus arrival time). Multiplies hours by the hourly rate, adds 16% VAT tax, and returns the final total.

### Module 4: Payment System

* **Action:** When the driver pays at the exit.

* **How it works:** Takes the final price from Module 3. Creates a unique receipt number (like `TX-A1B2C3D4`) and saves the full payment details (M-Pesa, Card, or Cash) to the permanent Audit Log.

### Module 5: Exit Gate Control

* **Action:** Happens right after the payment is successful.

* **How it works:** Confirms payment, marks the exit gate as "OPEN", empties the parking bay in the system, and deletes the car's active session.

### Module 6: Changing the Parking Price (Dynamic Rates)

* **Action:** When an admin updates the hourly fee.

* **How it works:** Validates the new price (must be greater than zero) and instantly applies it to the system memory for all future calculations without needing to restart the server.

### Module 7: Financial Records & Tax Report

* **Action:** Displaying the records table on the dashboard.

* **How it works:** Reads the list of all saved receipts and generates an HTML table showing the date, receipt ID, plate, payment method, basic fee, VAT, and total collected.

### Module 8: Admin Emergency Clear

* **Action:** If a car leaves without paying or there is a system error.

* **How it works:** The admin types in the number plate. The system locates the bay, forcefully empties it, and deletes the car's record without generating a receipt.

## 🧠 3. Data Structures & Algorithm Complexity

| Data Structure | Variable Name | Purpose | Time Complexity | Why we chose it | 
 | ----- | ----- | ----- | ----- | ----- | 
| **Hash Map (Dict)** | `slots` | Tracks 15 bays | **O(1)** | Lets us check if a specific bay is empty or full instantly using the Bay ID. | 
| **Hash Map (Dict)** | `vehicles` | Tracks parked cars | **O(1)** | Lets us find a car's exact arrival time instantly using its number plate. | 
| **List (Array)** | `audit_log` | Saves receipts | **O(1) Append** | Fast and easy to add new receipts to the bottom of the financial ledger. | 

## 🗄️ 4. In-Memory Database Schema

Even though we use computer memory instead of a standard SQL database, this is how our data structures are organized:

### 1. The Parking Bays Table (`slots`)

* **Bay ID (Key):** A number from 1 to 15.

* **Car Plate (Value):** The number plate of the car parked there (or `None` if empty).

### 2. The Active Cars Table (`vehicles`)

* **Car Plate (Key):** The unique number plate of the car.

* **Session Data (Value):** A dictionary containing the `bay` number and the `entry_time` (Unix timestamp).

### 3. The Receipts Table (`audit_log`)

* **Receipt ID:** A unique code for the payment.

* **Car Plate:** The car that paid.

* **Time Spent:** Total hours parked.

* **Payment Method:** M-Pesa, Card, or Cash.

* **Basic Cost:** Money charged before tax.

* **VAT (16%):** Government tax.

* **Total Paid:** The final amount handed over.

* **Date & Time:** When the transaction happened.
