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

CUSTOM_IMU_UUID = "1111"

# Manually defined devices
DEVICES = [
    ("right_leg", "7EFA8AE7-B4F7-2803-53D0-B65EE98ECFD5"),
    ("left_leg", "7EFA8AE7-B4F7-2803-53D0-B65EE98ECFD1"), # dummy UUIDs
    ("chest", "7EFA8AE7-B4F7-2803-53D0-B65EE98ECFD0") # dummy UUIDS
]

"""
    Script for connecting 3 BLE arduinos and fetching their data
    Used: GPT + https://github.com/hbldh/bleak/blob/develop/examples/two_devices.py
""" 
async def connect_to_device(uuid_address: str, device_body_location: str, lock: asyncio.Lock, directory_name: str):
    try:
        async with contextlib.AsyncExitStack() as stack:
            # used because establishing a connection to multiple devices can cause errors (github)
            async with lock:
                print(f"Looking for a device on the {device_body_location.lower()} ({uuid_address})...")
                  
                device = await BleakScanner.find_device_by_address(uuid_address)
                if device is None:
                    print(f"Device on the {device_body_location.lower()} ({uuid_address}) not found.")
                    return
                    
                client = await stack.enter_async_context(BleakClient(device))
                
                # create files use with open later on...
                output_file = Path(f"data/{directory_name}/{device_body_location}_imu_data.csv")
                output_file.parent.mkdir(exist_ok=True, parents=True)
                output_file.write_text("Timestamp, LinearX, LinearY, LinearZ, AngularX, AngularY, AngularZ, MagnetX, MagnetY, MagnetZ")
            # release lock
            
            initial_timestamp = 0
            sensor_data = [] 
            
            def callback(characteristic: BleakGATTCharacteristic, data: bytearray) -> None:
                timestamp, ax, ay, az, gx, gy, gz, mx, my, mz = struct.unpack("<Ifffffffff", data) # < -> little endian, careful with unpack
                if initial_timestamp == 0:
                    initial_timestamp = timestamp
                
                # TODO: Calibration
                timestamp = timestamp - initial_timestamp
                sensor_data.append(f"{timestamp}, {ax}, {ay}, {az}, {gx}, {gy}, {gz}, {mx}, {my}, {mz}")
                
            await client.start_notify(CUSTOM_IMU_UUID, callback)
            await asyncio.sleep(10.0) # TODO listen until interrupted?
            
            with open(f"./data/{directory_name}/{device_body_location}_imu_data.csv", 'w') as file:
                for line in sensor_data:
                    file.write(line)
                file.flush()
               
    except Exception as e:
        print(f"Error with the device on the {device_body_location.lower()} ({uuid_address})")
        print(e)
        
async def main():
    lock = asyncio.Lock()
    
    directory_name = datetime.now().replace(microsecond=0)
    
    # start multiple async functions concurrently 
    await asyncio.gather(
        *(
            connect_to_device(uuid_address, device_body_position, lock, directory_name) 
            for device_body_position, uuid_address in DEVICES
        )
    )

asyncio.run(main())