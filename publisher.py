import argparse
import json
import random
import time
from datetime import datetime, timezone

import paho.mqtt.client as mqtt


TOPICS = (
    "sensores/lab1/temperatura",
    "sensores/lab1/humedad",
    "sensores/lab2/temperatura",
    "sensores/lab2/presion",
)


def build_payload(topic: str) -> str:

    # Divide el topico tomando el ultimo elemento
    sensor_type = topic.rsplit("/", 1)[-1]
    if sensor_type == "temperatura":
        value = round(random.uniform(18.0, 32.0), 2)
        unit = "C"
    elif sensor_type == "humedad":
        value = round(random.uniform(35.0, 80.0), 2)
        unit = "%"
    else:
        value = round(random.uniform(990.0, 1030.0), 2)
        unit = "hPa"

# Inicia la conversion de un diccionario Python a una cadena JSON y la retorna
    return json.dumps(
        {
            "sensor": topic,
            "valor": value,
            "unidad": unit,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        },
        ensure_ascii=True,
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Publicador MQTT que simula datos de sensores.")
    parser.add_argument("--host", default="localhost", help="Servidor MQTT. Por defecto: localhost")
    parser.add_argument("--port", type=int, default=1883, help="Puerto MQTT. Por defecto: 1883")
    parser.add_argument("--qos", type=int, choices=(0, 1, 2), default=1, help="Calidad de servicio MQTT")
    parser.add_argument("--count", type=int, default=10, help="Cantidad de mensajes a enviar")
    parser.add_argument("--interval", type=float, default=1.0, help="Segundos entre mensajes")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id="demo-sensor-publisher")

    print(f"Conectando a MQTT en {args.host}:{args.port}...")
    client.connect(args.host, args.port, keepalive=60)
    client.loop_start()

    try:
        for index in range(1, args.count + 1):
            topic = random.choice(TOPICS)
            payload = build_payload(topic)
            result = client.publish(topic, payload, qos=args.qos)
            result.wait_for_publish()
            print(f"[{index}/{args.count}] Publicado QoS {args.qos} en {topic}: {payload}")
            time.sleep(args.interval)
    finally:
        client.loop_stop()
        client.disconnect()


if __name__ == "__main__":
    main()
