import asyncio
from datetime import datetime
from device import Device


class Runner:
    def __init__(self):
        self.devices: list[Device] = []
        self.directory_name = datetime.now().replace(microsecond=0)
    
    def add(self, device: Device):
        self.devices.append(device)
    
    def addAll(self, devices: list[Device]):
        self.devices.extend(devices)
    
    async def connect_devices(self):
        await asyncio.gather(
            *(
                device.connect() 
                for device in self.devices
            )
        )
        
    async def calibrate_devices(self):
        await asyncio.gather(
            *(
                device.calibrate() 
                for device in self.devices
            )
        )
    
    async def collect_data(self, duration):
        await asyncio.gather(
            *(
                device.collect(duration) 
                for device in self.devices
            )
        )
    
    async def write_to_file(self):
        await asyncio.gather(
            *(
                device.save_to_file() 
                for device in self.devices
            )
        )
    