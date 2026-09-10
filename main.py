import time

class AutomatedParkingLot:
    def __init__(self, max_capacity=5, hourly_rate=100.0):
        self.max_capacity = max_capacity
        self.free_spaces = max_capacity
        self.active_vehicles_db = {}  # Hash map: {plate_number: arrival_timestamp}
        self.user_credentials = {}    # Hash map: {username: passkey}
        self.active_session = None
        self.rate_per_hour = hourly_rate

    def create_account(self):
        print("\n=== USER ACCOUNT REGISTRATION ===")
        user = input("Choose a username: ").strip()
        if not user:
            print("[ERROR] Username cannot be blank.")
            return
        if user in self.user_credentials:
            print(f"[ERROR] Account name '{user}' already exists.")
            return
        passkey = input("Choose a passkey: ").strip()
        if not passkey:
            print("[ERROR] Passkey cannot be blank.")
            return
        
        self.user_credentials[user] = passkey
        print(f"[SUCCESS] User account '{user}' successfully generated!")

    def authenticate_user(self):
        print("\n=== USER AUTHENTICATION ===")
        if self.active_session:
            print(f"[NOTICE] Currently logged in as '{self.active_session}'. Sign out first.")
            return
        user = input("Enter username: ").strip()
        passkey = input("Enter passkey: ").strip()
        
        if user in self.user_credentials and self.user_credentials[user] == passkey:
            self.active_session = user
            print(f"[SUCCESS] Access granted. Welcome, {user}!")
        else:
            print("[ERROR] Access denied. Invalid credentials provided.")

    def terminate_session(self):
        if not self.active_session:
            print("\n[NOTICE] No active session found.")
            return
        print(f"\n[SUCCESS] Session ended for user '{self.active_session}'.")
        self.active_session = None

    def admit_vehicle(self):
        print("\n=== VEHICLE ADMISSION (ENTRY) ===")
        if not self.active_session:
            print("[DENIED] Authentication required. Please log in to process entries.")
            return
        if self.free_spaces <= 0:
            print("[FULL] Facility reached max capacity. Admission halted.")
            return
            
        plate = input("Enter vehicle registration/plate number: ").upper().strip()
        if not plate:
            print("[ERROR] Plate number cannot be empty.")
            return
        if plate in self.active_vehicles_db:
            print(f"[ERROR] Vehicle '{plate}' is already inside the lot.")
            return

        self.active_vehicles_db[plate] = time.time()
        self.free_spaces -= 1
        print(f"[SUCCESS] Vehicle '{plate}' recorded. Free spaces remaining: {self.free_spaces}")

    def release_vehicle(self):
        print("\n=== VEHICLE DEPARTURE & BILLING ===")
        if not self.active_session:
            print("[DENIED] Authentication required. Please log in to process exits.")
            return
            
        plate = input("Enter vehicle registration/plate number: ").upper().strip()
        if plate not in self.active_vehicles_db:
            print(f"[ERROR] Record for vehicle '{plate}' not found.")
            return

        arrival_timestamp = self.active_vehicles_db.pop(plate)
        departure_timestamp = time.time()
        elapsed_seconds = departure_timestamp - arrival_timestamp
        elapsed_hours = elapsed_seconds / 3600.0
        
        # Calculate fee
        calculated_fee = max(self.rate_per_hour, elapsed_hours * self.rate_per_hour)
        self.free_spaces += 1

        print(f"[SUCCESS] Vehicle '{plate}' processed for departure.")
        print(f"  -> Total Duration: {elapsed_seconds:.2f} seconds")
        print(f"  -> Calculated Bill: KES {calculated_fee:.2f}")
        print(f"  -> Updated Available Slots: {self.free_spaces}")

    def show_occupancy(self):
        print("\n=== FACILITY OCCUPANCY STATUS ===")
        print(f"Max Capacity:      {self.max_capacity}")
        print(f"Free Spaces:       {self.free_spaces}")
        print(f"Occupied Spaces:   {self.max_capacity - self.free_spaces}")
        if self.active_vehicles_db:
            print("\n[LIST OF PARKED VEHICLES]")
            for plate in self.active_vehicles_db:
                print(f"  - Registration Plate: {plate}")
        else:
            print("No vehicles are currently parked.")

def main():
    manager = AutomatedParkingLot(max_capacity=5, hourly_rate=100.0)

    while True:
        user_status = f"Active User: {manager.active_session}" if manager.active_session else "Status: Unauthenticated"
        print(f"\n****************************************")
        print(f"  SMART PARKING CONTROL HUB")
        print(f"  ({user_status})")
        print(f"****************************************")
        print("1. Create New Account")
        print("2. System Login")
        print("3. Sign Out")
        print("4. Register Vehicle Arrival")
        print("5. Process Vehicle Exit & Payment")
        print("6. Display Facility Occupancy")
        print("7. Terminate Program")

        choice = input("\nSelect action [1-7]: ").strip()

        if choice == "1":
            manager.create_account()
        elif choice == "2":
            manager.authenticate_user()
        elif choice == "3":
            manager.terminate_session()
        elif choice == "4":
            manager.admit_vehicle()
        elif choice == "5":
            manager.release_vehicle()
        elif choice == "6":
            manager.show_occupancy()
        elif choice == "7":
            print("\nShutting down Smart Parking Control Hub. Goodbye!")
            break
        else:
            print("\n[ERROR] Invalid option selected. Enter a number between 1 and 7.")

if __name__ == "__main__":
    main()