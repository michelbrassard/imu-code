"""
    Pedestrain Dead Reckoning
    14 October 2025
    
    A simple script to simulate a server and test out the connection with the Arduino
    It will try to connect to the board and it will print the data for 10 seconds
"""

import asyncio
from bleak import BleakClient, BleakScanner, BleakError
import struct

# Hard coded address for the Arduino board
ARDUINO_ADDRESS_UUID = "7EFA8AE7-B4F7-2803-53D0-B65EE98ECFD5"

"""
    Each characteristic sends a custom descriptor that states from which sensor is the data (like below).
    But I haven't been able to make it work yet because descriptor data extractor is async and it causes problems for the
    notification_handler. 
    This is a current solution just to see which data points are streamed
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
        

async def main(address):
    
    """
        Use the commented out code below to test which devices are "seen". 
        It may be useful later on so that the Arduino UUID is not hard-coded
    """
    
    # print("Scanning for nearby devices... (wait 5 seconds)")
    # devices = await BleakScanner.discover()
    # print("Nearby devices: ")
    # for device in devices:
    #     print(f" - {device.name} ({device.address})")

    
    print("Trying to connect to Arduino...")
    
    try: 
        async with BleakClient(address) as client:
            if not client.is_connected:
                print("Failed to connect.")
                return
            print("Connected!")
            
            def notification_handler(characteristic, bytearray_data):
                timestamp, x, y, z = struct.unpack("<Ifff", bytearray_data) # < -> little endian, careful with unpack
                print(f"{get_characteristic_name_from_uuid(characteristic.uuid)} -> {f"Timestamp (millis): {timestamp}, X: {x:.2f}, Y: {y:.2f}, Z: {z:.2f}"}")
            
            try:
                print("Device name: ", client.name)
                print("Services: ", client.services)
                for service in client.services:
                    print(f" - {service.uuid} {service.description}")
                    print("Characteristcs:")
                    
                    for characteristic in service.characteristics:
                        await client.start_notify(characteristic.uuid, notification_handler)
                
                # a "timer", it is used to keep the connection open for 10 seconds
                await asyncio.sleep(10)

            except BleakError as error:
                print("Problem with extracting info:, ", error)
                
    except BleakError:
        print("Arduino not found.")
            

asyncio.run(main(ARDUINO_ADDRESS_UUID))