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
        print("CONNECTING...")
        await asyncio.gather(
            *(
                device.connect() 
                for device in self.devices
            )
        )
        
    async def calibrate_devices(self):
        print("CALIBRATING...")
        await asyncio.gather(
            *(
                device.calibrate() 
                for device in self.devices
            )
        )
    
    async def collect_data(self, duration):
        print(f"COLLECTING DATA FOR {duration}s ...")
        await asyncio.gather(
            *(
                device.collect(duration) 
                for device in self.devices
            )
        )
    
    async def write_to_file(self):
        print("SAVING TO FILE")
        await asyncio.gather(
            *(
                device.save_to_file() 
                for device in self.devices
            )
        )
    
async def main():
    runner = Runner()
    lock = asyncio.Lock()
    directory_name = datetime.now().replace(microsecond=0)
    
    right_leg_device = Device(directory_name, "right_leg", "7EFA8AE7-B4F7-2803-53D0-B65EE98ECFD5", lock)
    left_leg_device = Device(directory_name, "left_leg", "08151AAC-7425-AF47-653F-5E4D46C327F0", lock)
    chest_device = Device(directory_name, "chest", "F28584E7-DEC2-9687-B6AE-DCFB28A5157D", lock)
    
    runner.addAll([right_leg_device])
    
    await runner.connect_devices()
    await runner.calibrate_devices()
    await runner.collect_data(duration=10)
    await runner.write_to_file()

asyncio.run(main())
    