import random
import time
import pandas as pd
from utils import load_resources, preprocess_message
import logging
import getpass

# ------------------- Setup Logging -------------------
logging.basicConfig(
    filename="blocked_attacks.log",
    level=logging.INFO,
    format="%(asctime)s | %(message)s"
)

# ------------------- Load Resources -------------------
try:
    ids_model, canid_encoder, label_encoder = load_resources()
except Exception as e:
    print(f"❌ Error loading resources: {e}")
    exit()

# ------------------- Logging Helper -------------------
def log_blocked_attack(attack_type, can_id, dlc, data_str):
    logging.info(f"{attack_type} | CAN_ID={can_id} | DLC={dlc} | DATA={data_str}")
    with open("blocked_can_ids.txt", "a") as f:
        f.write(f"{attack_type} | CAN_ID={can_id} | DLC={dlc} | DATA={data_str}\n")

# ------------------- Prevention Function -------------------
def prevent(can_id, dlc, data_str):
    try:
        X = preprocess_message(can_id, dlc, data_str, canid_encoder)
        y_pred = ids_model.predict(X)[0]
        label = label_encoder.inverse_transform([y_pred])[0]
    except Exception as e:
        print(f"❌ Prediction error: {e}")
        return "Error"

    if label != "Normal":
        print(f"⚠ Attack detected! Type={label} | CAN_ID={can_id}")
        log_blocked_attack(label, can_id, dlc, data_str)
    else:
        print(f"✅ Normal packet | CAN_ID={can_id}")

    return label  # return classification result for logging

# ------------------- Synthetic Traffic Generator -------------------
def generate_can_frame(attack_type=None):
    can_id = hex(random.randint(0x000, 0x7FF))
    dlc = random.randint(0, 8)
    data = " ".join([format(random.randint(0, 255), '02X') for _ in range(dlc)])

    if not attack_type:  # Normal traffic
        return can_id, dlc, data, "Normal"

    if attack_type == "DoS":
        can_id = hex(random.randint(0x000, 0x00F))  # High priority ID
    elif attack_type == "Spoofing":
        can_id = "0x0C0"  # Pretend to be engine ECU
    elif attack_type == "Fuzzy":
        data = " ".join([format(random.randint(0, 255), '02X') for _ in range(dlc)])

    return can_id, dlc, data, attack_type

# ------------------- Authentication -------------------
def authenticate():
    valid_users = {
        "admin@example.com": "securepass123",
        "analyst@example.com": "canbus2024"
    }
    valid_token = "CAN-SECURE-TOKEN-001"

    email = input("Enter email: ").strip()
    password = getpass.getpass("Enter password: ")

    if email in valid_users and valid_users[email] == password:
        print("✅ Email/Password authentication successful!")
    else:
        print("❌ Invalid email or password.")
        return False

    token = input("Enter security token: ").strip()
    if token == valid_token:
        print("✅ Token authentication successful!")
        return True
    else:
        print("❌ Invalid token.")
        return False

# ------------------- Main Loop -------------------
if __name__ == "__main__":
    if not authenticate():
        print("🚫 Authentication failed. Exiting system...")
        exit()

    print("🚗 Starting real-time CAN traffic simulation...\n")

    traffic_log = []

    try:
        while True:
            # 80% normal, 20% attack
            if random.random() < 0.2:
                attack = random.choice(["DoS", "Fuzzy", "Spoofing"])
                can_id, dlc, data, actual_label = generate_can_frame(attack)
            else:
                can_id, dlc, data, actual_label = generate_can_frame()

            # Run through IDS/IPS
            predicted_label = prevent(can_id, dlc, data)

            # Save traffic log
            traffic_log.append({
                "Timestamp": time.time(),
                "CAN_ID": can_id,
                "DLC": dlc,
                "Data": data,
                "Actual_Label": actual_label,
                "Predicted_Label": predicted_label
            })

            # Write to CSV every 20 messages
            if len(traffic_log) % 20 == 0:
                with open("traffic_log.csv", "a") as f:
                    df = pd.DataFrame(traffic_log)
                    df.to_csv(f, index=False, header=f.tell() == 0)
                traffic_log.clear()

            time.sleep(0.5)  # simulate real-time arrival

    except KeyboardInterrupt:
        print("\n🛑 Stopped simulation. Saving remaining traffic...")
        if traffic_log:
            with open("traffic_log.csv", "a") as f:
                df = pd.DataFrame(traffic_log)
                df.to_csv(f, index=False, header=f.tell() == 0)
