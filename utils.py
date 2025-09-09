import joblib
import pandas as pd

# ------------------- Load model and encoders -------------------
def load_resources():
    try:
        ids_model = joblib.load("ids_model.pkl")
        canid_encoder = joblib.load("canid_encoder.pkl")
        label_encoder = joblib.load("label_encoder.pkl")
        return ids_model, canid_encoder, label_encoder
    except Exception as e:
        print(f"❌ Error loading resources: {e}")
        raise

# ------------------- Preprocess CAN message -------------------
def preprocess_message(can_id, dlc, data_str, canid_encoder):
    try:
        # Encode CAN ID using the same encoder as training
        encoded_canid = canid_encoder.transform([can_id])[0]

        # Split data string into bytes
        data_bytes = data_str.split(" ")
        data_bytes = [int(b, 16) for b in data_bytes if b.strip() != ""]

        # Pad to max length (8 bytes for CAN)
        while len(data_bytes) < 8:
            data_bytes.append(0)

        # Build feature row (just like training)
        features = {
            "CAN_ID": encoded_canid,
            "DLC": dlc,
            "Byte0": data_bytes[0],
            "Byte1": data_bytes[1],
            "Byte2": data_bytes[2],
            "Byte3": data_bytes[3],
            "Byte4": data_bytes[4],
            "Byte5": data_bytes[5],
            "Byte6": data_bytes[6],
            "Byte7": data_bytes[7],
        }

        X = pd.DataFrame([features])
        return X

    except Exception as e:
        print(f"❌ Error preprocessing message: {e}")
        raise
