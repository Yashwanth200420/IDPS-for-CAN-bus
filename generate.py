import random
import pandas as pd
import time

# Generate random CAN frame
def generate_can_frame(attack_type=None):
    timestamp = round(time.time() + random.random(), 6)
    can_id = random.choice([hex(random.randint(0x000, 0x7FF))])
    dlc = random.randint(0, 8)
    data = " ".join([format(random.randint(0, 255), '02X') for _ in range(dlc)])

    label = "Normal"
    if attack_type:
        label = attack_type
        if attack_type == "DoS":
            can_id = hex(random.randint(0x000, 0x00F))  # Very high priority
        elif attack_type == "Fuzzy":
            data = " ".join([format(random.randint(0, 255), '02X') for _ in range(dlc)])
        elif attack_type == "Spoofing":
            can_id = "0x0C0"  # Pretend to be engine ECU

    return [timestamp, can_id, dlc, data, label]


# Create dataset
dataset = []
for _ in range(50):
    if random.random() < 0.1:  # 10% attack traffic
        attack_type = random.choice(["DoS", "Fuzzy", "Spoofing"])
        dataset.append(generate_can_frame(attack_type))
    else:
        dataset.append(generate_can_frame())

# Save to CSV
df = pd.DataFrame(dataset, columns=["Timestamp", "CAN_ID", "DLC", "Data", "Label"])
df.to_csv("synthetic_car_hacking_dataset.csv", index=False)
print("✅ Dataset saved as synthetic_car_hacking_dataset.csv")
