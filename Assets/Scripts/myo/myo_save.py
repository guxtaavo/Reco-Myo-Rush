import multiprocessing
import pandas as pd
import time
from time import perf_counter
from pyomyo import Myo, emg_mode
from collections import deque
import os
import winsound
import cv2
import random

# =========================================
# GESTURES + IMAGES
# =========================================
gestures = {
    "POWER": "img/power.png",
    "LATERAL": "img/lateral.png",
    "POINTER": "img/point.png",
    "OPEN": "img/open.png",
    "TRIPOD": "img/tripod.png"
}

REST_IMAGE = "img/rest.png"

# =========================================
# WORKER → Myo reader process
# =========================================
def worker(conn):
    m = Myo(mode=emg_mode.FILTERED)
    m.connect()

    def add_to_pipe(emg, movement):
        conn.send((time.time(), emg))

    m.set_leds([128, 0, 0], [128, 0, 0])
    m.vibrate(1)
    m.add_emg_handler(add_to_pipe)

    print("Myo connected. Collecting...")

    while True:
        try:
            m.run()
        except Exception as e:
            print("Worker stopped:", e)
            break


# =========================================
# SHOW IMAGE
# =========================================
def show_image(image_path, window_name="Gesture", width=500, height=500):
    img = cv2.imread(image_path)
    if img is not None:
        img = cv2.resize(img, (width, height))
        cv2.imshow(window_name, img)
        cv2.waitKey(1)
    else:
        print(f"⚠ ERROR: Could not load {image_path}")


# =========================================
# MAIN
# =========================================
if __name__ == "__main__":

    parent_conn, child_conn = multiprocessing.Pipe()
    p = multiprocessing.Process(target=worker, args=(child_conn,))
    p.start()

    emg_data = []

    print("Estimating sample rate...")
    monitor = deque(maxlen=200)

    start_time = time.time()
    fixed_sample_rate = None

    # Estimate sample rate 2–3 seconds
    while fixed_sample_rate is None:
        if parent_conn.poll():
            t, _ = parent_conn.recv()
            monitor.append(t)

            if time.time() - start_time >= 3:
                duration = monitor[-1] - monitor[0]
                fixed_sample_rate = len(monitor) / duration
                print(f"✔ Estimated Sample Rate: {fixed_sample_rate:.2f} Hz")
                storage_interval = 1.0 / fixed_sample_rate
                last_save = t

    # Protocol parameters
    GRASP_TIME = 5.0
    REST_TIME = 3.0
    REPEAT_CYCLES = 5

    gesture_list = list(gestures.keys())

    print("\n===============================")
    print("     PROTOCOL STARTED")
    print("===============================\n")

    try:
        for cycle in range(REPEAT_CYCLES):
            print(f"\n======== CYCLE {cycle+1}/{REPEAT_CYCLES} ========\n")

            # randomize order
            random_order = random.sample(gesture_list, len(gesture_list))
            print("Random order:", random_order)

            for current_gesture in random_order:

                # --------------------------------------------------
                # REST PHASE — EXACT 3.000 s
                # --------------------------------------------------
                show_image(REST_IMAGE)
                print(f"\n🟦 REST ({REST_TIME}s)")
                
                t_start = perf_counter()
                t_rest_end = t_start + REST_TIME

                winsound.Beep(700, 150)  # beep at rest start (optional)

                while perf_counter() < t_rest_end:
                    if parent_conn.poll():
                        timestamp, emg = parent_conn.recv()
                        if timestamp - last_save >= storage_interval:
                            emg_data.append([timestamp] + list(emg) + ["REST"])
                            last_save = timestamp

                # --------------------------------------------------
                # GESTURE PHASE — EXACT 5.000 s
                # --------------------------------------------------
                show_image(gestures[current_gesture])
                print(f"✊ PERFORM {current_gesture} ({GRASP_TIME}s)")

                winsound.Beep(1000, 150)  # EXACT TIME BEEP (gesture start)

                t_grasp_end = t_rest_end + GRASP_TIME

                while perf_counter() < t_grasp_end:
                    if parent_conn.poll():
                        timestamp, emg = parent_conn.recv()
                        if timestamp - last_save >= storage_interval:
                            emg_data.append([timestamp] + list(emg) + [current_gesture])
                            last_save = timestamp

                winsound.Beep(600, 150)  # EXACT TIME BEEP (gesture end)

        print("\n🎉 ALL CYCLES COMPLETED SUCCESSFULLY!")

    except KeyboardInterrupt:
        print("\nInterrupted by user.")

    finally:
        print("\nShutting down Myo...")
        p.terminate()
        p.join()

        df = pd.DataFrame(
            emg_data,
            columns=["Timestamp"] + [f"CH_{i+1}" for i in range(8)] + ["State"]
        )

        os.makedirs("db", exist_ok=True)
        # out_path = "db/TESTE0000.csv"
        out_path = "db/voluntary_010_right.csv"
        df.to_csv(out_path, index=False)

        print(f"✔ File saved to: {out_path}")

        cv2.destroyAllWindows()