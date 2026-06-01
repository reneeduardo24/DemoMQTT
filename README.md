# Demo MQTT con Mosquitto

## Requisitos

- Python 3.9 o superior
- Eclipse Mosquitto ejecutandose en `localhost:1883`

## Instalacion

```powershell
pip install -r requirements.txt
```

## Suscriptor

```powershell
python subscriber.py --topic sensores/# --qos 1
```

Para recibir solo lecturas de temperatura:

```powershell
python subscriber.py --topic sensores/+/temperatura --qos 2
```

## Publicador

```powershell
python publisher.py --qos 1 --count 10 --interval 1
```

## Prueba de comodines y QoS

```powershell
python test_wildcards_qos.py
```
