import numpy as np
import joblib
import multiprocessing
from collections import deque
from pyomyo import Myo, emg_mode

# ===========================================================
# LOAD MODEL
# ===========================================================
MODEL_PATH = "30_features/db/knn_model_30_features.joblib"
model = joblib.load(MODEL_PATH)
print(f"✔ Loaded model from {MODEL_PATH}")

# ===========================================================
# SELECTED FEATURES (ORDER MUST MATCH TRAINING)
# ===========================================================
selected_features = [
    'CH_1_RMS', 'CH_1_MAV', 'CH_1_WL',
    'CH_2_RMS', 'CH_2_MAV', 'CH_2_WL',
    'CH_3_RMS', 'CH_3_MAV', 'CH_3_WL', 'CH_3_VAR',
    'CH_4_RMS', 'CH_4_MAV', 'CH_4_WL', 'CH_4_VAR',
    'CH_5_RMS', 'CH_5_MAV', 'CH_5_WL', 'CH_5_VAR',
    'CH_6_RMS', 'CH_6_MAV', 'CH_6_WL', 'CH_6_VAR',
    'CH_7_RMS', 'CH_7_MAV', 'CH_7_WL', 'CH_7_VAR',
    'CH_8_RMS', 'CH_8_MAV', 'CH_8_WL', 'CH_8_VAR'
]

# ===========================================================
# FEATURE FUNCTIONS
# ===========================================================
def waveform_length(x):
    return np.sum(np.abs(np.diff(x)))


def normalize_window(window, eps=1e-8):
    """
    Online z-score normalization per channel
    window shape: (WINDOW_SIZE, 8)
    """
    mean = np.mean(window, axis=0)
    std = np.std(window, axis=0)
    return (window - mean) / (std + eps)


def extract_features(window):
    """
    window shape: (WINDOW_SIZE, 8)
    return shape: (1, 30)
    """

    # ✅ NORMALIZAÇÃO ONLINE (POR JANELA)
    window = normalize_window(window)

    feats = []

    for feat in selected_features:
        prefix, ch, feat_type = feat.split("_")
        ch_idx = int(ch) - 1  # CH_1 -> 0
        x = window[:, ch_idx]

        if feat_type == "RMS":
            feats.append(np.sqrt(np.mean(x ** 2)))

        elif feat_type == "MAV":
            feats.append(np.mean(np.abs(x)))

        elif feat_type == "WL":
            feats.append(waveform_length(x))

        elif feat_type == "VAR":
            feats.append(np.var(x))

        else:
            raise ValueError(f"Unknown feature: {feat_type}")

    return np.array(feats).reshape(1, -1)

# ===========================================================
# WORKER PROCESS (MYO)
# ===========================================================
def worker(conn):
    m = Myo(mode=emg_mode.FILTERED)
    m.connect()

    def emg_handler(emg, movement):
        conn.send(emg)

    m.add_emg_handler(emg_handler)
    m.vibrate(1)

    print(">>> Myo connected, streaming EMG...")

    while True:
        try:
            m.run()
        except KeyboardInterrupt:
            break

# ===========================================================
# MAIN PROCESS
# ===========================================================
if __name__ == "__main__":

    parent_conn, child_conn = multiprocessing.Pipe()
    p = multiprocessing.Process(target=worker, args=(child_conn,))
    p.start()

    WINDOW_SIZE = 15  # MUST match training
    buffer = deque(maxlen=WINDOW_SIZE)

    gesture_names = [
        "LATERAL",
        "OPEN",
        "POINTER",
        "POWER",
        "REST",
        "TRIPOD"
    ]

    print("\n>>> REALTIME CLASSIFICATION READY")
    print(">>> Listening...\n")

    while True:
        if parent_conn.poll():
            emg = parent_conn.recv()  # shape (8,)
            buffer.append(emg)

            if len(buffer) == WINDOW_SIZE:
                window = np.array(buffer)

                features = extract_features(window)

                pred = model.predict(features)[0]
                print("Detected gesture:", gesture_names[pred])
