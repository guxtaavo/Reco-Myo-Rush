import multiprocessing
import numpy as np
import pandas as pd
import time
from pyomyo import Myo, emg_mode
from collections import deque
import joblib
import paho.mqtt.client as mqtt
import os

# ----- CONFIGURAÇÕES -----
PATH = os.path.abspath(os.getcwd())
MODEL_PATH = os.path.join(PATH, "db", "best_RF.joblib")
MQTT_BROKER = "localhost"
MQTT_PORT = 1883
MQTT_TOPIC_PREDICTION = "myo/prediction"
ROLLING_WINDOW_SIZE = 15

# ----- FUNÇÃO DE EXTRAÇÃO DE FEATURES -----
def extract_features(window):
    window = np.array(window)
    mean = np.mean(window, axis=0)
    std = np.std(window, axis=0)
    maximum = np.max(window, axis=0)
    minimum = np.min(window, axis=0)
    return np.concatenate([mean, std, maximum, minimum])

# ----- PROCESSO DE COLETA DE DADOS -----
def worker(conn):
    m = Myo(mode=emg_mode.FILTERED)
    m.connect()

    def add_to_pipe(emg, movement):
        conn.send((time.time(), emg))

    m.set_leds([128, 0, 0], [128, 0, 0])
    m.vibrate(1)
    m.add_emg_handler(add_to_pipe)

    print("Myo conectado. Coletando dados EMG...")
    while True:
        try:
            m.run()
        except Exception as e:
            print("Worker parado:", e)
            break

# ----- PROGRAMA PRINCIPAL -----
if __name__ == '__main__':
    # Iniciar subprocesso
    parent_conn, child_conn = multiprocessing.Pipe()
    p = multiprocessing.Process(target=worker, args=(child_conn,))
    p.start()

    # Carregar modelo
    print("Carregando modelo de 3 classes...")
    model = joblib.load(MODEL_PATH)

    # MQTT
    mqtt_client = mqtt.Client()
    try:
        mqtt_client.connect(MQTT_BROKER, MQTT_PORT, 60)
        mqtt_client.loop_start()
        mqtt_connected = True
        print(f"MQTT conectado em {MQTT_BROKER}:{MQTT_PORT}")
    except:
        mqtt_connected = False
        print("Falha ao conectar no broker MQTT.")

    rolling_window = deque(maxlen=ROLLING_WINDOW_SIZE)
    monitor = deque(maxlen=100)
    fixed_sample_rate = None
    CALIBRATION_DURATION = 5
    last_stored_time = None
    print("Pressione Ctrl+C para parar a coleta")

    try:
        start_time = time.time()

        while True:
            if parent_conn.poll():
                timestamp, emg = parent_conn.recv()

                # Calibração inicial
                if fixed_sample_rate is None:
                    monitor.append(timestamp)
                    if time.time() - start_time >= CALIBRATION_DURATION:
                        duration = monitor[-1] - monitor[0]
                        rate = len(monitor) / duration if duration > 0 else 0
                        fixed_sample_rate = rate
                        print(f"Sample rate estimado: {rate:.2f} Hz")
                        storage_interval = 1.0 / rate
                        last_stored_time = timestamp
                    continue

                # Coleta no intervalo certo
                if last_stored_time is None or timestamp - last_stored_time >= storage_interval:
                    last_stored_time = timestamp
                    rolling_window.append(emg)

                    # Se o buffer estiver cheio, classifica
                    if len(rolling_window) == ROLLING_WINDOW_SIZE:
                        features = extract_features(rolling_window).reshape(1, -1)
                        prediction = model.predict(features)[0]

                        label_map = {0: "Left", 1: "Center", 2: "Right"}
                        print(f"Predição: {label_map.get(prediction, prediction)} ({prediction})")

                        if mqtt_connected:
                            mqtt_client.publish(MQTT_TOPIC_PREDICTION, str(prediction))
                        else:
                            print("Warning: MQTT não conectado.")

    except KeyboardInterrupt:
        print("\nEncerrando...")
        p.terminate()
        p.join()
        if mqtt_connected:
            mqtt_client.loop_stop()
            mqtt_client.disconnect()
        print("Encerrado com sucesso.")
