"""
    Pedestrain Dead Reckoning
    4 November 2025
    
    Used for finding available devices
"""

import asyncio
from bleak import BleakScanner

async def main():    
    print("Scanning for nearby devices... (wait 5 seconds)")
    devices = await BleakScanner.discover()
    print("Nearby devices: ")
    for device in devices:
        print(f" - {device.name} ({device.address})")

asyncio.run(main())