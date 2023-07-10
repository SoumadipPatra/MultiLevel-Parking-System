import hashlib

PARKING_RATE = 20  # Rs per hour
NUM_FLOORS = 5
SLOTS_PER_FLOOR = 15

parking_lot = {}
for floor in range(1, NUM_FLOORS + 1):
    parking_lot[str(floor)] = { str(slot): None for slot in range(1, SLOTS_PER_FLOOR + 1) }

parking_lot['1']['1'] =  {'car_number': 'PQR', 'entry_time': 1688987205, 'token': '5cdc323434'}

# Function to check the availability of parking slots on a floor
def check_availability(floor):
    for slot, car in parking_lot[floor].items():
        if car is None:
            return slot
    return None

def generate_token(entry_time):
    md5_hash = hashlib.md5(str(entry_time).encode()).hexdigest()
    token = md5_hash[:8]
    return token

def calculate_bill(entry_time, exit_time):
    parking_duration = exit_time - entry_time
    bill = (parking_duration // 3600 + 1) * PARKING_RATE
    return bill

