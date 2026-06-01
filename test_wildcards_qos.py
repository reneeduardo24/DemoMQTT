import json
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone

import paho.mqtt.client as mqtt


HOST = "localhost"
PORT = 1883


@dataclass
class Capture:
    name: str
    topic_filter: str
    qos: int
    messages: list[tuple[str, int, str]] = field(default_factory=list)


def make_client(capture: Capture) -> mqtt.Client:
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id=f"demo-{capture.name}")

    def on_connect(client: mqtt.Client, userdata, flags, reason_code, properties) -> None:
        if reason_code != 0:
            raise RuntimeError(f"{capture.name} no pudo conectarse: {reason_code}")
        client.subscribe(capture.topic_filter, qos=capture.qos)

    def on_message(client: mqtt.Client, userdata, message: mqtt.MQTTMessage) -> None:
        capture.messages.append((message.topic, message.qos, message.payload.decode("utf-8")))

    client.on_connect = on_connect
    client.on_message = on_message
    return client


def publish_messages() -> None:
    publisher = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id="demo-test-publisher")
    publisher.connect(HOST, PORT, keepalive=60)
    publisher.loop_start()

    samples = [
        ("sensores/lab1/temperatura", 0, 22.5, "C"),
        ("sensores/lab1/humedad", 1, 58.2, "%"),
        ("sensores/lab2/temperatura", 2, 24.1, "C"),
        ("sensores/lab2/presion", 1, 1012.4, "hPa"),
    ]

    for topic, qos, value, unit in samples:
        payload = json.dumps(
            {
                "sensor": topic,
                "valor": value,
                "unidad": unit,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            },
            ensure_ascii=True,
        )
        result = publisher.publish(topic, payload, qos=qos)
        result.wait_for_publish()
        print(f"Publicado en {topic} con QoS {qos}")

    publisher.loop_stop()
    publisher.disconnect()


def main() -> None:
    captures = [
        Capture("todos", "sensores/#", qos=2),
        Capture("temperatura", "sensores/+/temperatura", qos=2),
        Capture("lab1", "sensores/lab1/+", qos=1),
    ]

    clients = [make_client(capture) for capture in captures]
    for client in clients:
        client.connect(HOST, PORT, keepalive=60)
        client.loop_start()

    time.sleep(1.0)
    publish_messages()
    time.sleep(2.0)

    for client in clients:
        client.loop_stop()
        client.disconnect()

    print("\nResultados de comodines y QoS:")
    for capture in captures:
        print(f"\nSuscriptor '{capture.name}' filtro='{capture.topic_filter}' QoS suscripcion={capture.qos}")
        for topic, qos, payload in capture.messages:
            print(f"  recibido topic={topic} qos_entregado={qos} payload={payload}")

    expected_counts = {"todos": 4, "temperatura": 2, "lab1": 2}
    failures = [capture.name for capture in captures if len(capture.messages) != expected_counts[capture.name]]
    if failures:
        raise SystemExit(f"Prueba incompleta. Suscriptores con conteo incorrecto: {', '.join(failures)}")

    print("\nPrueba OK: comodines # y + recibieron los mensajes esperados con QoS 0, 1 y 2.")


if __name__ == "__main__":
    main()
