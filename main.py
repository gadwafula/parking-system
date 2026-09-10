import time

class SmartParkingSystem:
    def __init__(self, total_slots=5, hourly_rate=100.0):
        self.total_slots = total_slots
        self.hourly_rate = hourly_rate
        # Dynamic Database tables initialized in memory
        self.slots = {i: None for i in range(1, total_slots + 1)}  # Hash Map: Slot ID -> Vehicle Plate
        self.vehicles = {}  # Hash Map: Vehicle Plate -> {slot, entry_time}

    def visual_display(self):
        """MODULE 1: Live Visual Display of Available Parking Slots"""
        occupied = sum(1 for plate in self.slots.values() if plate is not None)
        available = self.total_slots - occupied
        
        print("\n========================================================")
        print("          LIVE PARKING SLOT VISUAL DISPLAY BOARD        ")
        print("========================================================")
        print(f" Total Capacity: {self.total_slots} | Available Slots: {available} | Occupied: {occupied}\n")
        
        grid_display = " "
        for slot_id, plate in self.slots.items():
            if plate:
                grid_display += f"[ SLOT {slot_id}: OCCUPIED ({plate}) ]  "
            else:
                grid_display += f"[ SLOT {slot_id}: VACANT ]  "
        print(grid_display)
        print("========================================================\n")

    def record_arrival(self):
        """MODULE 2: Vehicle Arrival & Entry Recording"""
        self.visual_display()
        occupied = sum(1 for plate in self.slots.values() if plate is not None)
        
        if occupied >= self.total_slots:
            print("[!] ENTRY DENIED: Parking Lot is Full!")
            return

        plate = input("Enter vehicle license plate (e.g., KAA 123A): ").upper().strip()
        if not plate:
            print("[!] Error: License plate cannot be empty.")
            return
        if plate in self.vehicles:
            print(f"[!] Error: Vehicle '{plate}' is already inside the lot.")
            return

        # Automatically assign the first vacant slot
        assigned_slot = next(slot for slot, owner in self.slots.items() if owner is None)
        
        # Save arrival record into dynamic database structure
        self.slots[assigned_slot] = plate
        self.vehicles[plate] = {
            "slot": assigned_slot,
            "entry_time": time.time()
        }
        
        print(f"\n[+] ARRIVAL RECORDED: Vehicle '{plate}' assigned to SLOT {assigned_slot}.")
        print("[+] ENTRY BARRIER: Opening barrier -> Vehicle entered -> Barrier closed.")

    def process_exit(self):
        """MODULE 3 & 4: Time Calculation, Billing & Barrier Gate Control"""
        print("\n--- VEHICLE EXIT & AUTOMATED BILLING ---")
        plate = input("Enter vehicle license plate for exit: ").upper().strip()
        
        if plate not in self.vehicles:
            print(f"[!] Error: Vehicle '{plate}' is not registered inside the lot.")
            return

        record = self.vehicles[plate]
        slot_id = record["slot"]
        entry_time = record["entry_time"]
        exit_time = time.time()

        # Calculate duration and fees
        duration_seconds = exit_time - entry_time
        duration_hours = max(0.01, duration_seconds / 3600.0)
        total_fee = max(self.hourly_rate, duration_hours * self.hourly_rate)

        print(f"\n==========================================")
        print(f"             PARKING INVOICE              ")
        print(f"==========================================")
        print(f" Vehicle Plate : {plate}")
        print(f" Assigned Slot : Slot {slot_id}")
        print(f" Stay Duration : {duration_seconds:.2f} seconds")
        print(f" Total Fee     : KES {total_fee:.2f}")
        print(f"==========================================")

        # Barrier release contingent on payment
        pay_confirm = input(f"Confirm payment receipt of KES {total_fee:.2f}? (y/n): ").lower().strip()
        if pay_confirm == 'y':
            print("\n[+] PAYMENT CONFIRMED: Payment processed successfully.")
            print("[+] EXIT BARRIER: Barrier opening to allow exit...")
            print("    ====================================")
            print("    |  [==== EXIT BARRIER OPEN ====]   |")
            print("    ====================================")
            print("[+] Vehicle safely cleared the gate.")
            print("[+] EXIT BARRIER: Barrier closed.")

            # Update dynamic database tables
            self.slots[slot_id] = None
            del self.vehicles[plate]
            print(f"[+] DATABASE UPDATED: Slot {slot_id} is now VACANT.")
        else:
            print("\n[!] PAYMENT FAILED / CANCELLED: Exit barrier remains CLOSED.")

def main():
    system = SmartParkingSystem(total_slots=5, hourly_rate=100.0)

    while True:
        print("\n==============================================")
        print("  KENYA AUTOMATED PARKING MANAGEMENT SYSTEM   ")
        print("==============================================")
        print("1. Visual Display of Parking Slots")
        print("2. Record Vehicle Arrival (Entry Gate)")
        print("3. Process Exit, Calculate Billing & Open Barrier")
        print("4. Terminate System")

        choice = input("\nSelect Option (1-4): ").strip()

        if choice == "1":
            system.visual_display()
        elif choice == "2":
            system.record_arrival()
        elif choice == "3":
            system.process_exit()
        elif choice == "4":
            print("\nShutting down Automated Parking System. Goodbye!")
            break
        else:
            print("\n[!] Invalid selection. Please choose an option between 1 and 4.")

if __name__ == "__main__":
    main()