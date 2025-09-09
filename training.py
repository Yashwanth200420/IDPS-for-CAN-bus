import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import classification_report
import joblib

# 1. Load Dataset
df = pd.read_csv("synthetic_car_hacking_dataset.csv")

# 2. Encode categorical columns
le_canid = LabelEncoder()
df["CAN_ID"] = le_canid.fit_transform(df["CAN_ID"])

# Split Data column into bytes
df_data_bytes = df["Data"].str.split(" ", expand=True).fillna("00")
for col in df_data_bytes.columns:
    df_data_bytes[col] = df_data_bytes[col].apply(lambda x: int(x, 16))

# Combine features
X = pd.concat([df[["Timestamp", "CAN_ID", "DLC"]], df_data_bytes], axis=1)

# Encode labels
le_label = LabelEncoder()
y = le_label.fit_transform(df["Label"])
X.columns = X.columns.astype(str)

# 3. Train-test split
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# 4. Train model
model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X_train, y_train)

# 5. Evaluate
labels_present = np.unique(y_test)
y_pred = model.predict(X_test)

print(classification_report(
    y_test, y_pred,
    labels=labels_present,
    target_names=le_label.classes_[labels_present],
    zero_division=0
))

# 6. Save model & encoders
joblib.dump(model, "ids_model.pkl")
joblib.dump(le_canid, "canid_encoder.pkl")
joblib.dump(le_label, "label_encoder.pkl")
print("✅ Model and encoders saved.")
