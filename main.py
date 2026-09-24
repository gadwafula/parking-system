
import time  
import uuid  
from flask import (
    Flask,
    flash,
    redirect,
    render_template_string,
    request,
    url_for,
)

# Initialize Flask web application
app = Flask(__name__)
app.secret_key = "universal_smart_parking_key"


# =============================================================================
# 2. BACKEND LOGIC - Smart Parking System Brain
# =============================================================================
class SmartParkingSystem:
    def __init__(self, total_slots=15, hourly_rate=100.0, vat_rate=0.16):
        # Configuration Settings
        self.total_slots = total_slots  # Total physical parking spaces (15 slots)
        self.hourly_rate = hourly_rate  # Base rate per hour in KES
        self.vat_rate = vat_rate        # Government Tax rate (16% VAT)

        # --- DYNAMIC IN-MEMORY DATABASES ---
        # 1. HASH MAP:  Bay ID
        self.slots = {i: None for i in range(1, total_slots + 1)}

        # 2. HASH MAP:  License Plate 
        self.vehicles = {}

        # 3. LIST: Saves all completed payment receipts
        self.audit_log = []

        # 4. Physical exit gate indicator
        self.barrier_status = "LOCKED"

    def record_arrival(self, plate, target_bay=None):
        """Allocates a parking bay (either a specific chosen bay or the first available one)

        and records entry timestamp.
        """
        occupied = len(self.vehicles)

        # Rule 1: Reject if the parking lot is full
        if occupied >= self.total_slots:
            return False, "Parking lot is full! No vacant bays available."

        # Rule 2: Prevent duplicate entries for a car already parked inside
        if plate in self.vehicles:
            return False, f"Vehicle '{plate}' is already inside the parking lot."

        # Rule 3: If user clicked a specific vacant bay, validate it and then use it if available
        if target_bay is not None:
            if target_bay not in self.slots:
                return False, f"Invalid Bay number: {target_bay}."
            if self.slots[target_bay] is not None:
                return False, f"BAY {target_bay} is already occupied by '{self.slots[target_bay]}'."
            assigned_bay = target_bay
        else:
            # Auto-assign the first vacant bay available
            assigned_bay = next(
                bay for bay, owner in self.slots.items() if owner is None
            )

        # Save entry details in memory
        self.slots[assigned_bay] = plate
        self.vehicles[plate] = {
            "bay": assigned_bay,
            "entry_time": time.time(), # Capture arrival time in seconds
        }

        return True, f"Vehicle '{plate}' assigned to BAY {assigned_bay}. Entry barrier raised!"

    def compute_fee(self, plate):
        """Calculates parking duration, net fee, 16% VAT, and gross bill."""
        if plate not in self.vehicles:
            return None

        record = self.vehicles[plate]
        duration_seconds = time.time() - record["entry_time"]
        duration_hours = max(0.01, duration_seconds / 3600.0)

        subtotal = max(self.hourly_rate, duration_hours * self.hourly_rate)
        vat_amount = subtotal * self.vat_rate
        total_payable = subtotal + vat_amount

        return {
            "bay": record["bay"],
            "duration_hrs": duration_hours,
            "subtotal": subtotal,
            "vat": vat_amount,
            "total": total_payable,
        }

    def process_payment(self, plate, method):
        """Processes payment receipt, frees the bay, and releases exit gate."""
        billing = self.compute_fee(plate)
        if not billing:
            return False, "Vehicle not found in active parking records."

        tx_id = f"TX-{uuid.uuid4().hex[:8].upper()}"

        # Record receipt into audit log
        self.audit_log.append({
            "tx_id": tx_id,
            "plate": plate,
            "method": method,
            "duration": billing["duration_hrs"],
            "subtotal": billing["subtotal"],
            "vat": billing["vat"],
            "total": billing["total"],
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        })

        # Free the slot
        bay_id = billing["bay"]
        self.slots[bay_id] = None
        del self.vehicles[plate]

        self.barrier_status = "OPEN (PAID)"
        return True, f"Payment of KES {billing['total']:.2f} confirmed via {method}. Exit barrier opened!"


# Assigns parking lot with 15 available slots
parking_system = SmartParkingSystem(total_slots=15, hourly_rate=100.0)


# =============================================================================
# 3. FRONTEND INTERFACE - Responsive Web Graphical Dashboard
# =============================================================================
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Smart Parking Management System</title>
    <!-- Tailwind CSS library for modern styling -->
    <script src="https://cdn.tailwindcss.com"></script>
</head>

<body class="bg-slate-100 text-slate-800 font-sans min-h-screen p-6">
    <div class="max-w-6xl mx-auto space-y-6">
        
        <!-- HEADER -->
        <header class="bg-slate-900 text-white rounded-xl p-6 shadow-lg flex justify-between items-center">
            <div>
                <h1 class="text-2xl font-bold text-blue-400">Smart Parking Management System</h1>
                <p class="text-slate-300 text-sm mt-1">Automated Vehicle Tracking & Billing Interface</p>
            </div>
            <div class="text-right">
                <span class="text-xs text-slate-400 block uppercase tracking-wider">Currency</span>
                <span class="text-lg font-bold text-white">KES</span>
            </div>
        </header>

        <!-- REAL-TIME STATISTICS DASHBOARD -->
        <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div class="bg-white border border-slate-200 rounded-xl p-4 shadow-sm flex flex-col justify-center items-center">
                <span class="text-slate-500 text-xs font-bold uppercase tracking-wider mb-1">Total Capacity</span>
                <span class="text-3xl font-extrabold text-slate-700">{{ system.total_slots }}</span>
            </div>
            <div class="bg-emerald-50 border border-emerald-200 rounded-xl p-4 shadow-sm flex flex-col justify-center items-center">
                <span class="text-emerald-600 text-xs font-bold uppercase tracking-wider mb-1">Available Slots</span>
                <span class="text-3xl font-extrabold text-emerald-600">{{ system.total_slots - system.vehicles|length }}</span>
            </div>
            <div class="bg-red-50 border border-red-200 rounded-xl p-4 shadow-sm flex flex-col justify-center items-center">
                <span class="text-red-600 text-xs font-bold uppercase tracking-wider mb-1">Occupied Slots</span>
                <span class="text-3xl font-extrabold text-red-600">{{ system.vehicles|length }}</span>
            </div>
            <div class="bg-blue-50 border border-blue-200 rounded-xl p-4 shadow-sm flex flex-col justify-center items-center">
                <span class="text-blue-600 text-xs font-bold uppercase tracking-wider mb-1">Current Hourly Rate</span>
                <span class="text-3xl font-extrabold text-blue-600"><span class="text-lg">KES</span> {{ system.hourly_rate }}</span>
            </div>
        </div>

        <!-- POP-UP ALERT NOTIFICATIONS -->
        {% with messages = get_flashed_messages(with_categories=true) %}
          {% if messages %}
            {% for category, message in messages %}
              <div class="p-4 rounded-lg text-white font-medium shadow {{ 'bg-emerald-600' if category == 'success' else 'bg-red-600' }}">
                {{ message }}
              </div>
            {% endfor %}
          {% endif %}
        {% endwith %}

        <!-- MODULE 1: Live Interactive Parking Grid -->
        <section class="bg-white rounded-xl p-6 shadow-sm border border-slate-200">
            <div class="flex justify-between items-center mb-4">
                <h2 class="text-lg font-bold text-slate-700">Live Parking Bay Status</h2>
                <span class="text-xs text-slate-400 font-medium italic">💡 Tip: Click any green VACANT bay to park directly</span>
            </div>
            
            <div class="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-5 lg:grid-cols-5 gap-4">
                {% for bay_id, plate in system.slots.items() %}
                    {% if plate %}
                        <!-- OCCUPIED BAY (Red - Non-clickable) -->
                        <div class="p-4 rounded-xl text-center border-2 bg-red-50 border-red-300 text-red-700 shadow-inner">
                            <span class="text-xs font-bold uppercase tracking-wider block opacity-75">Bay {{ bay_id }}</span>
                            <span class="text-base font-black tracking-widest block mt-1">{{ plate }}</span>
                        </div>
                    {% else %}
                        <!-- VACANT BAY (Green - CLICKABLE BUTTON) -->
                        <button onclick="openBayModal({{ bay_id }})" class="p-4 rounded-xl text-center border-2 bg-emerald-50 border-emerald-300 text-emerald-700 shadow-sm hover:shadow-md hover:bg-emerald-100 hover:scale-105 transition-all w-full cursor-pointer group">
                            <span class="text-xs font-bold uppercase tracking-wider block opacity-75">Bay {{ bay_id }}</span>
                            <span class="text-base font-black tracking-widest block mt-1 group-hover:underline">VACANT</span>
                            <span class="text-[10px] font-semibold text-emerald-600 block mt-1 opacity-80">+ Click to Park</span>
                        </button>
                    {% endif %}
                {% endfor %}
            </div>
        </section>

        <!-- ENTRY & EXIT FORMS -->
        <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
            
            <!-- MODULE 2: Auto-Allocation Entry Form -->
            <section class="bg-white rounded-xl p-6 shadow-sm border border-slate-200">
                <h2 class="text-lg font-bold text-slate-700 mb-3">Vehicle Entry (Auto-Assign)</h2>
                <form action="/entry" method="POST" class="space-y-3">
                    <div>
                        <label class="block text-sm font-medium text-slate-600">License Plate Number</label>
                        <input type="text" name="plate" placeholder="e.g. KAA 123A" required class="w-full mt-1 p-2 border border-slate-300 rounded-lg uppercase bg-slate-50 focus:bg-white focus:ring-2 focus:ring-blue-500 outline-none transition">
                    </div>
                    <button type="submit" class="w-full bg-blue-600 hover:bg-blue-700 text-white font-bold py-2 rounded-lg transition shadow-sm">Auto-Assign Bay & Enter</button>
                </form>
            </section>

            <!-- MODULES 3-5: Exit & Payment Form -->
            <section class="bg-white rounded-xl p-6 shadow-sm border border-slate-200">
                <h2 class="text-lg font-bold text-slate-700 mb-3">Vehicle Exit & Billing</h2>
                <form action="/payment" method="POST" class="space-y-3">
                    <div class="grid grid-cols-2 gap-3">
                        <div>
                            <label class="block text-sm font-medium text-slate-600">License Plate</label>
                            <input type="text" name="plate" placeholder="e.g. KAA 123A" required class="w-full mt-1 p-2 border border-slate-300 rounded-lg uppercase bg-slate-50 focus:bg-white focus:ring-2 focus:ring-emerald-500 outline-none transition">
                        </div>
                        <div>
                            <label class="block text-sm font-medium text-slate-600">Payment Method</label>
                            <select name="method" class="w-full mt-1 p-2 border border-slate-300 rounded-lg bg-slate-50 focus:bg-white focus:ring-2 focus:ring-emerald-500 outline-none transition cursor-pointer">
                                <option value="Mobile Money">Mobile Money (e.g., M-Pesa)</option>
                                <option value="Bank Card">Credit / Debit Card</option>
                                <option value="Cash">Cash</option>
                            </select>
                        </div>
                    </div>
                    <button type="submit" class="w-full bg-emerald-600 hover:bg-emerald-700 text-white font-bold py-2 rounded-lg transition shadow-sm">Process Payment & Open Barrier</button>
                </form>
            </section>
        </div>

        <!-- ADMIN CONTROLS -->
        <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
            
            <!-- TARIFF SETTINGS -->
            <section class="bg-white rounded-xl p-6 shadow-sm border border-slate-200">
                <h2 class="text-lg font-bold text-slate-700 mb-3">System Tariffs</h2>
                <form action="/rate" method="POST" class="flex gap-3">
                    <input type="number" step="0.1" name="rate" placeholder="New Base Rate" required class="flex-1 p-2 border border-slate-300 rounded-lg bg-slate-50 outline-none focus:ring-2 focus:ring-amber-500">
                    <button type="submit" class="bg-amber-600 hover:bg-amber-700 text-white font-bold px-4 py-2 rounded-lg transition shadow-sm">Update Rate</button>
                </form>
            </section>

            <!-- OVERRIDE -->
            <section class="bg-white rounded-xl p-6 shadow-sm border border-slate-200">
                <h2 class="text-lg font-bold text-slate-700 mb-3">Emergency Override</h2>
                <form action="/override" method="POST" class="flex gap-3">
                    <input type="text" name="plate" placeholder="Target Plate Number" class="flex-1 p-2 border border-slate-300 rounded-lg uppercase bg-slate-50 outline-none focus:ring-2 focus:ring-rose-500">
                    <button type="submit" class="bg-rose-600 hover:bg-rose-700 text-white font-bold px-4 py-2 rounded-lg transition shadow-sm">Force Clear Bay</button>
                </form>
            </section>
        </div>

        <!-- AUDIT LEDGER TABLE -->
        <section class="bg-white rounded-xl p-6 shadow-sm border border-slate-200">
            <h2 class="text-lg font-bold text-slate-700 mb-3">Financial Audit Log</h2>
            <div class="overflow-x-auto rounded-lg border border-slate-200">
                <table class="w-full text-left text-sm text-slate-600 border-collapse">
                    <thead class="bg-slate-50 text-slate-700 uppercase font-semibold text-xs border-b border-slate-200">
                        <tr>
                            <th class="p-3">Timestamp</th>
                            <th class="p-3">TX ID</th>
                            <th class="p-3">Plate</th>
                            <th class="p-3">Duration</th>
                            <th class="p-3">Method</th>
                            <th class="p-3 text-right">Net Fee</th>
                            <th class="p-3 text-right">VAT (16%)</th>
                            <th class="p-3 text-right">Total Paid</th>
                        </tr>
                    </thead>
                    <tbody class="divide-y divide-slate-100">
                        {% for tx in system.audit_log %}
                        <tr class="hover:bg-slate-50 transition">
                            <td class="p-3 whitespace-nowrap">{{ tx.timestamp }}</td>
                            <td class="p-3 font-mono text-xs text-slate-400">{{ tx.tx_id }}</td>
                            <td class="p-3 font-bold text-slate-800">{{ tx.plate }}</td>
                            <td class="p-3 text-slate-500">{{ "%.2f"|format(tx.duration) }} Hrs</td>
                            <td class="p-3">
                                <span class="px-2 py-1 bg-slate-100 text-slate-600 rounded text-xs font-semibold">{{ tx.method }}</span>
                            </td>
                            <td class="p-3 text-right">KES {{ "%.2f"|format(tx.subtotal) }}</td>
                            <td class="p-3 text-right">KES {{ "%.2f"|format(tx.vat) }}</td>
                            <td class="p-3 font-extrabold text-emerald-600 text-right">KES {{ "%.2f"|format(tx.total) }}</td>
                        </tr>
                        {% else %}
                        <tr>
                            <td colspan="8" class="p-8 text-center text-slate-400 font-medium">No transactions recorded yet. Data will appear here after the first payment.</td>
                        </tr>
                        {% endfor %}
                    </tbody>
                </table>
            </div>
        </section>

    </div>

    <!-- QUICK BAY ASSIGNMENT POP-UP MODAL -->
    <div id="bayModal" class="fixed inset-0 bg-slate-900/60 backdrop-blur-sm hidden flex items-center justify-center p-4 z-50">
        <div class="bg-white rounded-2xl shadow-2xl max-w-md w-full p-6 border border-slate-200">
            <div class="flex justify-between items-center mb-4">
                <h3 class="text-xl font-bold text-slate-800" id="modalTitle">Park in Bay</h3>
                <button onclick="closeModal()" class="text-slate-400 hover:text-slate-600 font-bold text-2xl leading-none">&times;</button>
            </div>
            <form action="/entry" method="POST" class="space-y-4">
                <input type="hidden" name="bay_id" id="modalBayId" value="">
                <div>
                    <label class="block text-sm font-medium text-slate-600 mb-1">License Plate Number</label>
                    <input type="text" name="plate" id="modalPlateInput" placeholder="e.g. KAA 123A" required class="w-full p-3 border border-slate-300 rounded-xl uppercase bg-slate-50 focus:bg-white focus:ring-2 focus:ring-blue-500 outline-none transition font-bold text-slate-800">
                </div>
                <div class="flex gap-3 pt-2">
                    <button type="button" onclick="closeModal()" class="flex-1 bg-slate-100 hover:bg-slate-200 text-slate-700 font-bold py-2.5 rounded-xl transition">Cancel</button>
                    <button type="submit" class="flex-1 bg-blue-600 hover:bg-blue-700 text-white font-bold py-2.5 rounded-xl transition shadow-md">Assign & Open Gate</button>
                </div>
            </form>
        </div>
    </div>

    <!-- JAVASCRIPT FOR MODAL CONTROLS -->
    <script>
        function openBayModal(bayId) {
            document.getElementById('modalBayId').value = bayId;
            document.getElementById('modalTitle').innerText = 'Park Vehicle in BAY ' + bayId;
            document.getElementById('bayModal').classList.remove('hidden');
            setTimeout(() => document.getElementById('modalPlateInput').focus(), 100);
        }
        function closeModal() {
            document.getElementById('bayModal').classList.add('hidden');
        }
    </script>
</body>
</html>
"""


# =============================================================================
# 4. CONTROLLER ROUTES
# =============================================================================
@app.route("/")
def index():
    return render_template_string(HTML_TEMPLATE, system=parking_system)


@app.route("/entry", methods=["POST"])
def handle_entry():
    plate = request.form.get("plate", "").upper().strip()
    bay_id_str = request.form.get("bay_id", "").strip()
    
    # Check if a specific bay was clicked or if it should auto-assign
    target_bay = int(bay_id_str) if bay_id_str.isdigit() else None
    
    success, msg = parking_system.record_arrival(plate, target_bay=target_bay)
    flash(msg, "success" if success else "error")
    return redirect(url_for("index"))


@app.route("/payment", methods=["POST"])
def handle_payment():
    plate = request.form.get("plate", "").upper().strip()
    method = request.form.get("method", "Cash")
    success, msg = parking_system.process_payment(plate, method)
    flash(msg, "success" if success else "error")
    return redirect(url_for("index"))


@app.route("/rate", methods=["POST"])
def handle_rate():
    try:
        new_rate = float(request.form.get("rate", 100))
        parking_system.hourly_rate = new_rate
        flash(f"Base tariff successfully updated to KES {new_rate:.2f}!", "success")
    except ValueError:
        flash("Invalid rate input. Please enter a numerical value.", "error")
    return redirect(url_for("index"))


@app.route("/override", methods=["POST"])
def handle_override():
    plate = request.form.get("plate", "").upper().strip()
    if plate in parking_system.vehicles:
        bay = parking_system.vehicles[plate]["bay"]
        parking_system.slots[bay] = None
        del parking_system.vehicles[plate]
        flash(f"Vehicle '{plate}' manually force-cleared from Bay {bay}.", "success")
    else:
        flash("Vehicle record not found in active parking list.", "error")
    return redirect(url_for("index"))


if __name__ == "__main__":
    app.run(debug=True, port=5000)