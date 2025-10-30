"""
    Pedestrain Dead Reckoning
    30 October 2025
    
    Simulates a central device for connecting to 3 arduino devices
"""

import asyncio
import struct
import contextlib
from pathlib import Path
from datetime import datetime

from bleak import BleakClient, BleakScanner
from bleak.backends.characteristic import BleakGATTCharacteristic

CUSTOM_ACCELERATION_UUID = "2D77"
CUSTOM_GYRO_UUID = "2D76"
MAGNETOMETER_UUID = "2AA1"

# Manually defined devices
DEVICES = [
    ("Right leg", "7EFA8AE7-B4F7-2803-53D0-B65EE98ECFD5"),
    ("Left leg", "7EFA8AE7-B4F7-2803-53D0-B65EE98ECFD1"), # dummy UUIDs
    ("Chest", "7EFA8AE7-B4F7-2803-53D0-B65EE98ECFD0") # dummy UUIDS
]

"""
   Script for connecting 3 BLE arduinos and fetching their data
    
    Used: GPT + https://github.com/hbldh/bleak/blob/develop/examples/two_devices.py
"""
def get_characteristic_name_from_uuid(uuid): 
    extracted_uuid_segment = uuid[4:8]
    match extracted_uuid_segment:
        case "2d77": 
            return "Acceleration (m/s^2)"
        case "2d76": 
            return "Gyroscope (deg/s)"
        case "2aa1": 
            return "Magnetometer (µT)"

# TODO vidi jel bolje da je to jedan file pa da je sve sinkronizirano ili 3 fiela s standardiziranim timestampom
def store_files_to_directory(device_body_location, data):
    output_file = Path(f"../data/{datetime.now().replace(microsecond=0)}/{device_body_location}/_imu_data.csv")
    output_file.parent.mkdir(exist_ok=True, parents=True)
    output_file.write_text("FOOBAR")
        
async def connect_to_device(uuid_address: str, device_body_location: str, lock: asyncio.Lock):
    try:
        async with contextlib.AsyncExitStack() as stack:
            
            # used because establishing a connection to multiple devices can cause errors (github, TODO read more)
            async with lock:
                print(f"Looking for a device on the {device_body_location.lower()} ({uuid_address})...")
                
                device = await BleakScanner.find_device_by_address(uuid_address)
                if device is None:
                    print(f"Device on the {device_body_location.lower()} ({uuid_address}) was not found.")
                    return
                    
                client = await stack.enter_async_context(BleakClient(device))
            # release lock
                
            def callback(characteristic: BleakGATTCharacteristic, data: bytearray) -> None:
                timestamp, x, y, z = struct.unpack("<Ifff", data) # < -> little endian, careful with unpack
                print(f"{device_body_location}: {get_characteristic_name_from_uuid(characteristic.uuid)} -> {f"Timestamp (millis): {timestamp}, X: {x:.2f}, Y: {y:.2f}, Z: {z:.2f}"}")

            await client.start_notify(CUSTOM_ACCELERATION_UUID, callback)
            await client.start_notify(CUSTOM_GYRO_UUID, callback)
            await client.start_notify(MAGNETOMETER_UUID, callback)
                
            # TODO Make it so that it listens until interrupt
            await asyncio.sleep(10.0)
               
    except Exception as e:
        print(f"Error with the device on the {device_body_location.lower()} ({uuid_address})")
        print(e)
        
async def main():
    lock = asyncio.Lock()
    
    # start multiple async functions concurrently 
    await asyncio.gather(
        *(
            connect_to_device(uuid_address, device_body_position, lock) 
            for device_body_position, uuid_address in DEVICES
        )
    )

asyncio.run(main())