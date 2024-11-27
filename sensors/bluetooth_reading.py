from bleak import BleakScanner
import asyncio


def decode_bthome_payload(payload):
    # https://bthome.io/format/

    measurement_types = {
        0x01: ("battery", "uint8", 1),
        0x02: ("temperature", "sint16", 0.01),
        0x03: ("humidity", "uint16", 0.01),
    }
    measurements = {}
    payload = payload[3:]  # remove unused payload flags

    i = 0

    while i < len(payload):
        obj_id = payload[i]
        i += 1

        try:
            name, data_type, factor = measurement_types[obj_id]
        except KeyError:
            break

        if data_type == "sint16":
            value = int.from_bytes(payload[i : i + 2], byteorder="little", signed=True)
            i += 2
        elif data_type == "uint16":
            value = int.from_bytes(payload[i : i + 2], byteorder="little", signed=False)
            i += 2
        elif data_type == "uint8":
            value = payload[i]
            i += 1
        else:
            continue

        measurements[name] = value * factor

    return measurements


async def scan_bthome_devices(scan_duration=10):
    """
    Scanne les appareils Bluetooth et retourne un dictionnaire des capteurs détectés.
    Les capteurs non pertinents sont ignorés.
    """
    sensors = {}

    def detection_callback(device, advertisement_data):
        for _, payload in advertisement_data.service_data.items():
            measurements = decode_bthome_payload(payload)
            if measurements:
                sensors[device.address] = {
                    "mac_address": device.address,
                    "name": device.name or "Unknown",
                    "rssi": advertisement_data.rssi,
                    **measurements,
                }

    scanner = BleakScanner(detection_callback=detection_callback)

    await scanner.start()
    await asyncio.sleep(scan_duration)
    await scanner.stop()

    return sensors


def get_bluetooth_bthome_th_sensors_data(scan_duration=10):
    return asyncio.run(scan_bthome_devices(scan_duration))
