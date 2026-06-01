import argparse

import paho.mqtt.client as mqtt


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Suscriptor MQTT para ver datos de sensores.")
    parser.add_argument("--host", default="localhost", help="Servidor MQTT. Por defecto: localhost")
    parser.add_argument("--port", type=int, default=1883, help="Puerto MQTT. Por defecto: 1883")
    parser.add_argument("--topic", default="sensores/#", help="Topico o comodin MQTT. Ejemplo: sensores/+/temperatura")
    parser.add_argument("--qos", type=int, choices=(0, 1, 2), default=1, help="Calidad de servicio MQTT")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id="demo-sensor-subscriber")

    def on_connect(client: mqtt.Client, userdata, flags, reason_code, properties) -> None:
        if reason_code == 0:
            print(f"Conectado a {args.host}:{args.port}")
            print(f"Suscrito a '{args.topic}' con QoS {args.qos}. Presiona Ctrl+C para salir.")
            client.subscribe(args.topic, qos=args.qos)
        else:
            print(f"No se pudo conectar. Codigo: {reason_code}")

    def on_message(client: mqtt.Client, userdata, message: mqtt.MQTTMessage) -> None:
        payload = message.payload.decode("utf-8", errors="replace")
        print(f"Topico={message.topic} QoS={message.qos} Mensaje={payload}")

    client.on_connect = on_connect
    client.on_message = on_message

    client.connect(args.host, args.port, keepalive=60)
    try:
        client.loop_forever()
    except KeyboardInterrupt:
        print("\nSuscriptor detenido.")
    finally:
        client.disconnect()


if __name__ == "__main__":
    main()
