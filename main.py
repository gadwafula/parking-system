
import time
from uuid import uuid4
from flask import Flask, render_template_string, request, redirect, url_for, flash

app = Flask(__name__)
app.secret_key = "mmu_parking_secret_key_gad"

class SmartParkingSystem:
    """
    Core backend logic using highly efficient O(1) Data Structures.
    """
    def __init__(self, total_slots=15):
        # 1. TOTAL CAPACITY
        self.total_slots = total_slots
        
        # 2. SLOTS (Hash Map): O(1) time complexity for instant visual display mapping.
        # Maps Bay ID (1 to 15) to License Plate (or None if vacant).
        self.slots = {i: None for i in range(1, self.total_slots + 1)}
        
        # 3. VEHICLES (Hash Map): O(1) time complexity for instant fee calculation on exit.
        # Maps License Plate -> {"bay": integer, "entry_time": float}
        self.vehicles = {}
        
        # 4. AUDIT_LOG (List): O(1) append operation. Records all transactions.
        self.audit_log = []
        
        # 5. BARRIER_STATUS: Tracks the physical barrier gate status.
        self.barrier_status = "LOCKED"

    def record_arrival(self, plate, target_bay=None):
        """
        Records a vehicle on arrival and assigns a parking slot[cite: 4].
        """
        plate = plate.strip().upper()
        
        # Guard: Check if parking is full
        if len(self.vehicles) >= self.total_slots:
            return False, "Parking lot is full! No vacant slots available."
            
        # Guard: Prevent double entry of the same vehicle
        if plate in self.vehicles:
            return False, f"Vehicle {plate} is already registered inside."
            
        # Allocation Logic: Manual Click vs Auto-Assign
        if target_bay:
            try:
                target_bay = int(target_bay)
                if target_bay not in self.slots or self.slots[target_bay] is not None:
                    return False, f"Bay {target_bay} is already occupied."
                assigned_bay = target_bay
            except ValueError:
                return False, "Invalid bay selection."
        else:
            # Auto-find the first available empty slot
            assigned_bay = next((bay for bay, occupant in self.slots.items() if occupant is None), None)

        if assigned_bay is None:
            return False, "System Error: No vacant bay found."

        # Save to memory databases
        self.slots[assigned_bay] = plate
        self.vehicles[plate] = {
            "bay": assigned_bay,
            "entry_time": time.time()
        }
        return True, f"Vehicle {plate} successfully parked in Bay {assigned_bay}."

    def compute_fee(self, plate, simulated_duration_mins=None):
        """
        Automatically calculates total time spent and amount to pay[cite: 4].
        Implements the exact official MMU tiered fee structure[cite: 4].
        """
        plate = plate.strip().upper()
        if plate not in self.vehicles:
            return None
            
        record = self.vehicles[plate]
        
        # Calculate duration
        if simulated_duration_mins:
            # For assignment testing purposes, allow simulating time passed
            duration_minutes = float(simulated_duration_mins)
        else:
            # Real-time calculation
            duration_seconds = time.time() - record["entry_time"]
            duration_minutes = duration_seconds / 60.0
            
        duration_hours = duration_minutes / 60.0
        
        # =========================================================
        # MMU TIERED PARKING FEE ALGORITHM[cite: 4]
        # =========================================================
        if duration_minutes <= 30:
            total_fee = 0.0     # Up to 30 mins: FREE
        elif duration_minutes <= 120:
            total_fee = 50.0    # Up to 2 hours: Kshs. 50
        elif duration_minutes <= 240:
            total_fee = 100.0   # Up to 4 hours: Kshs. 100
        elif duration_minutes <= 360:
            total_fee = 300.0   # Up to 6 hours: Kshs. 300
        else:
            total_fee = 500.0   # Over 6 hours: Kshs. 500
        # =========================================================
            
        return {
            "bay": record["bay"],
            "duration_minutes": round(duration_minutes, 1),
            "duration_hours": round(duration_hours, 2),
            "total_fee": total_fee
        }

    def process_payment(self, plate, method, simulated_duration_mins=None):
        """
        Processes payment, logs the transaction, and opens the barrier[cite: 4].
        """
        plate = plate.strip().upper()
        
        # 1. Calculate final bill
        billing = self.compute_fee(plate, simulated_duration_mins)
        if not billing:
            return False, "Vehicle record not found in active parking database."
            
        # 2. Generate Receipt Ledger Entry
        tx_id = f"TX-{uuid4().hex[:8].upper()}"
        receipt = {
            "tx_id": tx_id,
            "plate": plate,
            "method": method,
            "duration_mins": billing["duration_minutes"],
            "total_paid": billing["total_fee"],
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
        }
        self.audit_log.append(receipt)
        
        # 3. Open Barrier to allow exit on payment of parking fees.
        self.barrier_status = "OPEN (PAID)"
        
        # 4. Free up the slot and remove vehicle from active memory
        bay_id = billing["bay"]
        self.slots[bay_id] = None
        del self.vehicles[plate]
        
        # 5. Reset barrier (in a real hardware system, this happens after car passes)
        self.barrier_status = "LOCKED"
        
        return True, f"Success! Kshs. {billing['total_fee']} paid via {method}. Barrier Opened!"

    def force_clear(self, plate):
        """Emergency Admin function to clear a stuck vehicle."""
        plate = plate.strip().upper()
        if plate in self.vehicles:
            bay_id = self.vehicles[plate]["bay"]
            self.slots[bay_id] = None
            del self.vehicles[plate]
            return True, f"Admin Action: Bay {bay_id} forcibly cleared."
        return False, "Vehicle record not found."


# Initialize the master system monolith
system = SmartParkingSystem(total_slots=15)


# ==============================================================================
# FRONTEND TEMPLATE (HTML)
# Provides the visual display of parking slots available before entry.
# ==============================================================================
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>MMU Smart Parking - Gad Wafula</title>
    <script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="bg-gray-100 font-sans leading-normal tracking-normal text-gray-800">
    <div class="container mx-auto p-6 max-w-7xl">
        
        <!-- Header -->
        <header class="bg-blue-900 text-white p-6 rounded-lg shadow-lg mb-6 flex flex-col md:flex-row justify-between items-center border-b-4 border-yellow-500">
            <div>
                <h1 class="text-3xl font-extrabold tracking-tight">MULTIMEDIA UNIVERSITY OF KENYA</h1>
                <p class="text-blue-200 text-sm font-medium mt-1">DSA Task One: Automated Smart Parking Management System</p>
                <p class="text-yellow-400 text-xs font-bold mt-1">Developer: Gad Wafula Mulongo</p>
            </div>
            <div class="mt-4 md:mt-0">
                <span class="bg-blue-800 text-xs px-4 py-2 rounded-full border border-blue-500 font-mono shadow-inner">
                    LIVE SYSTEM ONLINE
                </span>
            </div>
        </header>

        <!-- System Alerts / Notifications -->
        {% with messages = get_flashed_messages(with_categories=true) %}
          {% if messages %}
            {% for category, message in messages %}
              <div class="mb-6 p-4 rounded-lg shadow-sm animate-pulse {% if category == 'success' %}bg-green-100 text-green-800 border-l-4 border-green-500{% else %}bg-red-100 text-red-800 border-l-4 border-red-500{% endif %}">
                <p class="font-bold">{{ message }}</p>
              </div>
            {% endfor %}
          {% endif %}
        {% endwith %}

        <!-- Live Metrics -->
        <div class="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
            <div class="bg-white p-5 rounded-lg shadow border-l-4 border-blue-500 flex flex-col justify-center">
                <p class="text-gray-500 text-xs font-bold uppercase tracking-wider">Total Capacity</p>
                <p class="text-3xl font-black text-gray-800">{{ system.total_slots }} Slots</p>
            </div>
            <div class="bg-white p-5 rounded-lg shadow border-l-4 border-green-500 flex flex-col justify-center">
                <p class="text-gray-500 text-xs font-bold uppercase tracking-wider">Available Bays</p>
                <p class="text-3xl font-black text-green-600">{{ system.total_slots - system.vehicles|length }} Vacant</p>
            </div>
            <div class="bg-white p-5 rounded-lg shadow border-l-4 border-red-500 flex flex-col justify-center">
                <p class="text-gray-500 text-xs font-bold uppercase tracking-wider">Occupied Bays</p>
                <p class="text-3xl font-black text-red-600">{{ system.vehicles|length }} Occupied</p>
            </div>
            <div class="bg-white p-5 rounded-lg shadow border-l-4 border-yellow-500 flex flex-col justify-center">
                <p class="text-gray-500 text-xs font-bold uppercase tracking-wider">Gate Barrier</p>
                <p class="text-2xl font-black text-gray-700">{{ system.barrier_status }}</p>
            </div>
        </div>

        <!-- Official Fee Structure (As requested by MMU) -->
        <div class="bg-blue-50 border border-blue-200 p-5 rounded-lg shadow-sm mb-6">
            <h3 class="text-sm font-extrabold text-blue-900 mb-3 uppercase tracking-wider">Official Tiered Parking Rates:</h3>
            <div class="grid grid-cols-2 md:grid-cols-5 gap-3 text-sm text-blue-900 text-center">
                <div class="bg-white p-3 rounded shadow-sm border border-blue-100">Up to 30 mins<br><span class="text-lg font-black text-green-600">FREE</span></div>
                <div class="bg-white p-3 rounded shadow-sm border border-blue-100">Up to 2 hours<br><span class="text-lg font-black">Kshs. 50</span></div>
                <div class="bg-white p-3 rounded shadow-sm border border-blue-100">Up to 4 hours<br><span class="text-lg font-black">Kshs. 100</span></div>
                <div class="bg-white p-3 rounded shadow-sm border border-blue-100">Up to 6 hours<br><span class="text-lg font-black">Kshs. 300</span></div>
                <div class="bg-white p-3 rounded shadow-sm border border-blue-100">Over 6 hours<br><span class="text-lg font-black text-red-600">Kshs. 500</span></div>
            </div>
        </div>

        <!-- VISUAL DISPLAY OF PARKING SLOTS -->
        <div class="bg-white p-6 rounded-lg shadow-lg mb-8">
            <h2 class="text-xl font-extrabold text-gray-800 mb-6 border-b pb-2">Live Visual Display (Select to Park)</h2>
            <div class="grid grid-cols-3 md:grid-cols-5 gap-4">
                {% for bay_id, occupant in system.slots.items() %}
                    {% if occupant %}
                        <!-- Occupied Slot UI -->
                        <div class="bg-red-50 border-2 border-red-400 p-4 rounded-xl text-center shadow-sm relative overflow-hidden">
                            <div class="absolute top-0 left-0 w-full h-1 bg-red-500"></div>
                            <span class="block text-xs text-red-600 font-black tracking-widest mb-1">BAY {{ "%02d"|format(bay_id) }}</span>
                            <span class="block text-lg font-black text-gray-800 mt-2">{{ occupant }}</span>
                            <span class="inline-block mt-3 px-3 py-1 bg-red-200 text-red-900 text-xs rounded-full font-bold">OCCUPIED</span>
                        </div>
                    {% else %}
                        <!-- Vacant Slot UI -->
                        <button onclick="openParkModal('{{ bay_id }}')" class="bg-green-50 border-2 border-green-400 p-4 rounded-xl text-center hover:bg-green-100 hover:scale-105 transition-all shadow-sm w-full cursor-pointer relative overflow-hidden group">
                            <div class="absolute top-0 left-0 w-full h-1 bg-green-500"></div>
                            <span class="block text-xs text-green-700 font-black tracking-widest mb-1">BAY {{ "%02d"|format(bay_id) }}</span>
                            <span class="block text-lg font-black text-green-800 mt-2 group-hover:text-green-900">VACANT</span>
                            <span class="inline-block mt-3 px-3 py-1 bg-green-200 text-green-900 text-xs rounded-full font-bold">CLICK TO PARK</span>
                        </button>
                    {% endif %}
                {% endfor %}
            </div>
        </div>

        <!-- System Controls -->
        <div class="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
            
            <!-- Entry Form -->
            <div class="bg-white p-6 rounded-lg shadow-lg border-t-4 border-blue-500">
                <h3 class="font-extrabold text-lg text-gray-800 mb-4">1. Vehicle Arrival</h3>
                <form action="/entry" method="POST" class="space-y-4">
                    <div>
                        <label class="block text-xs font-bold text-gray-600 mb-1">License Plate</label>
                        <input type="text" name="plate" required placeholder="e.g. KCA 123A" class="w-full border-2 border-gray-200 p-3 rounded-lg text-sm font-bold uppercase focus:border-blue-500 focus:outline-none">
                    </div>
                    <div>
                        <label class="block text-xs font-bold text-gray-600 mb-1">Preferred Bay (Optional)</label>
                        <input type="number" name="target_bay" placeholder="Auto-assign if empty" min="1" max="15" class="w-full border-2 border-gray-200 p-3 rounded-lg text-sm focus:border-blue-500 focus:outline-none">
                    </div>
                    <button type="submit" class="w-full bg-blue-600 hover:bg-blue-700 text-white font-black py-3 rounded-lg text-sm transition shadow-md">RECORD ENTRY</button>
                </form>
            </div>

            <!-- Exit & Payment Form -->
            <div class="bg-white p-6 rounded-lg shadow-lg border-t-4 border-green-500">
                <h3 class="font-extrabold text-lg text-gray-800 mb-4">2. Process Exit & Pay</h3>
                <form action="/payment" method="POST" class="space-y-4">
                    <div>
                        <label class="block text-xs font-bold text-gray-600 mb-1">License Plate</label>
                        <input type="text" name="plate" required placeholder="e.g. KCA 123A" class="w-full border-2 border-gray-200 p-3 rounded-lg text-sm font-bold uppercase focus:border-green-500 focus:outline-none">
                    </div>
                    <div>
                        <label class="block text-xs font-bold text-gray-600 mb-1">Payment Method</label>
                        <select name="method" class="w-full border-2 border-gray-200 p-3 rounded-lg text-sm font-bold focus:border-green-500 focus:outline-none">
                            <option value="M-Pesa">Mobile Money (M-Pesa)</option>
                            <option value="Card">Credit/Debit Card</option>
                            <option value="Cash">Cash</option>
                        </select>
                    </div>
                    <!-- Assignment Testing Feature -->
                    <div>
                        <label class="block text-xs font-bold text-blue-600 mb-1">Test Grading Tool: Simulate Mins Parked</label>
                        <input type="number" name="simulate_mins" placeholder="e.g. 150 (for 2.5 hrs)" class="w-full border-2 border-blue-200 bg-blue-50 p-2 rounded-lg text-xs focus:outline-none">
                    </div>
                    <button type="submit" class="w-full bg-green-600 hover:bg-green-700 text-white font-black py-3 rounded-lg text-sm transition shadow-md">PAY & OPEN BARRIER</button>
                </form>
            </div>

            <!-- Admin Form -->
            <div class="bg-white p-6 rounded-lg shadow-lg border-t-4 border-gray-800">
                <h3 class="font-extrabold text-lg text-gray-800 mb-4">3. Admin Override</h3>
                <p class="text-xs text-gray-500 mb-4">Forcefully remove a vehicle record without processing payment.</p>
                <form action="/override" method="POST" class="space-y-4">
                    <div>
                        <label class="block text-xs font-bold text-gray-600 mb-1">Target License Plate</label>
                        <input type="text" name="plate" required placeholder="e.g. KCA 123A" class="w-full border-2 border-gray-200 p-3 rounded-lg text-sm font-bold uppercase focus:border-gray-800 focus:outline-none">
                    </div>
                    <button type="submit" class="w-full bg-gray-800 hover:bg-gray-900 text-white font-black py-3 rounded-lg text-sm transition shadow-md mt-6">FORCE CLEAR SLOT</button>
                </form>
            </div>
            
        </div>

        <!-- Transactions Ledger -->
        <div class="bg-white p-6 rounded-lg shadow-lg">
            <h2 class="text-xl font-extrabold text-gray-800 mb-4 border-b pb-2">Financial Transactions Ledger</h2>
            <div class="overflow-x-auto">
                <table class="w-full text-left border-collapse text-sm">
                    <thead>
                        <tr class="bg-gray-800 text-white uppercase text-xs tracking-wider">
                            <th class="p-4 rounded-tl-lg">Date & Time</th>
                            <th class="p-4">Receipt ID</th>
                            <th class="p-4">Vehicle Plate</th>
                            <th class="p-4">Duration</th>
                            <th class="p-4">Method</th>
                            <th class="p-4 rounded-tr-lg">Total Paid</th>
                        </tr>
                    </thead>
                    <tbody>
                        {% for log in system.audit_log %}
                        <tr class="hover:bg-gray-50 border-b border-gray-200">
                            <td class="p-4 text-gray-600">{{ log.timestamp }}</td>
                            <td class="p-4 font-mono font-bold text-blue-600">{{ log.tx_id }}</td>
                            <td class="p-4 font-black text-gray-800">{{ log.plate }}</td>
                            <td class="p-4 font-medium text-gray-600">{{ log.duration_mins }} mins</td>
                            <td class="p-4 text-gray-600">{{ log.method }}</td>
                            <td class="p-4 font-black text-green-700 text-lg">Kshs. {{ log.total_paid }}</td>
                        </tr>
                        {% else %}
                        <tr>
                            <td colspan="6" class="p-8 text-center text-gray-400 italic font-medium">No transactions recorded yet. Waiting for exits.</td>
                        </tr>
                        {% endfor %}
                    </tbody>
                </table>
            </div>
        </div>
        
        <footer class="mt-8 text-center text-xs text-gray-500 font-bold">
            &copy; 2026 Gad Wafula Mulongo. Submitted for MMU DSA Task One.
        </footer>
    </div>

    <!-- Modal Form for Direct Bay Selection -->
    <div id="parkModal" class="hidden fixed inset-0 bg-gray-900 bg-opacity-75 flex items-center justify-center backdrop-blur-sm z-50 transition-opacity">
        <div class="bg-white p-8 rounded-xl shadow-2xl w-full max-w-md transform scale-100 transition-transform">
            <h3 class="text-2xl font-black mb-6 text-gray-800 text-center">Assign Bay <span id="modalBayId" class="text-green-600"></span></h3>
            <form action="/entry" method="POST">
                <input type="hidden" name="target_bay" id="modalBayInput">
                <div class="mb-6">
                    <label class="block text-sm font-bold text-gray-600 mb-2 uppercase tracking-wide">Enter License Plate</label>
                    <input type="text" name="plate" required placeholder="e.g. KCA 123A" class="w-full border-4 border-gray-100 p-4 rounded-lg text-lg font-black uppercase text-center focus:border-green-500 focus:outline-none transition">
                </div>
                <div class="flex justify-end gap-3">
                    <button type="button" onclick="closeParkModal()" class="w-1/2 py-3 bg-gray-200 hover:bg-gray-300 text-gray-800 rounded-lg text-sm font-black transition">CANCEL</button>
                    <button type="submit" class="w-1/2 py-3 bg-green-600 hover:bg-green-700 text-white rounded-lg text-sm font-black transition shadow-lg">CONFIRM PARK</button>
                </div>
            </form>
        </div>
    </div>

    <script>
        // Modal Control Functions
        function openParkModal(bayId) {
            document.getElementById('modalBayId').innerText = bayId;
            document.getElementById('modalBayInput').value = bayId;
            document.getElementById('parkModal').classList.remove('hidden');
        }
        function closeParkModal() {
            document.getElementById('parkModal').classList.add('hidden');
        }
    </script>
</body>
</html>
"""

# ==============================================================================
# FLASK ROUTING CONTROLLERS
# ==============================================================================

@app.route("/")
def dashboard():
    """Renders the main graphical user interface."""
    return render_template_string(HTML_TEMPLATE, system=system)

@app.route("/entry", methods=["POST"])
def entry():
    """Handles the vehicle arrival form submission[cite: 4]."""
    plate = request.form.get("plate", "")
    target_bay = request.form.get("target_bay", "")
    
    # Process through system algorithm
    success, message = system.record_arrival(plate, target_bay)
    flash(message, "success" if success else "error")
    return redirect(url_for("dashboard"))

@app.route("/payment", methods=["POST"])
def payment():
    """Handles the exit calculation and barrier opening[cite: 4]."""
    plate = request.form.get("plate", "")
    method = request.form.get("method", "Cash")
    simulate_mins = request.form.get("simulate_mins", "")
    
    # Parse simulated time if provided
    simulated_val = float(simulate_mins) if simulate_mins.strip() else None
    
    # Process payment and exit barrier
    success, message = system.process_payment(plate, method, simulated_duration_mins=simulated_val)
    flash(message, "success" if success else "error")
    return redirect(url_for("dashboard"))

@app.route("/override", methods=["POST"])
def override():
    """Handles emergency clear logic."""
    plate = request.form.get("plate", "")
    success, message = system.force_clear(plate)
    flash(message, "success" if success else "error")
    return redirect(url_for("dashboard"))

if __name__ == "__main__":
    # Start the local development web server on port 5000
    app.run(debug=True, port=5000)