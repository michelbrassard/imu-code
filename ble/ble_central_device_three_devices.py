"""
    Pedestrain Dead Reckoning
    30 October 2025
    
    Simulates a central device for connecting to 3 arduino devices
"""

import asyncio
from bleak import BleakClient, BleakScanner, BleakError
import struct