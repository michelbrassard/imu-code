import asyncio
import contextlib
import struct
import numpy as np

from pathlib import Path
from bleak import BleakClient, BleakScanner
from bleak.backends.characteristic import BleakGATTCharacteristic

from imu import IMU

class Device:
    
    # TODO, vidjet kako će uređaji stajati
    # referenca, gyro bi trebao biti 0, accel 1 za 1 direction i tako to...
    CUSTOM_IMU_UUID = "1111"
    
    def __init__(self, directory_name: str, body_location: str, uuid: str, lock: asyncio.Lock):
        self.uuid = uuid
        self.file_path = f"data/{directory_name}/{body_location}_imu_data.csv"
        self.body_location = body_location
        
        self.lock: asyncio.Lock = lock
        self.client = None
        
        self.is_connected = False
        self.is_calibrated = False
        
        self.rest_data: list[IMU] = [] # podaci za kalibraciju
        self.data: list[IMU] = []
        
        self.initial_timestamp = 0
        self.offset: IMU = None
        
    async def connect(self) -> None:
        try:
            async with self.lock:
                device = await BleakScanner.find_device_by_address(self.uuid)
                if device is None:
                    print(f"Device on {self.body_location} not found.")
                    return
                
                self.client = BleakClient(device)
                await self.client.connect()
                self.is_connected = True
                print(f'{self.body_location} connected!')
        except Exception as e:
            # TODO add the proper exception type and handling
            print(f"Error with the device on the {self.device_body_location.lower()} ({self.uuid})")
            print(e)
    
    async def calibrate(self) -> None:
        if not self.is_connected:
            print(f"Unable to calibrate device on {self.body_location}.")
            return
        
        def callback(characteristic: BleakGATTCharacteristic, data: bytearray) -> None:
            timestamp, ax, ay, az, gx, gy, gz, mx, my, mz = struct.unpack("<Ifffffffff", data)
            measured_data = IMU(timestamp, ax, ay, az, gx, gy, gz, mx, my, mz)
            self.rest_data.append(measured_data)
        
        try: 
            await self.client.start_notify(self.CUSTOM_IMU_UUID, callback)
            print(f'Calibrating {self.body_location} device... (wait 10s)')
            await asyncio.sleep(10.0)
            await self.client.stop_notify(self.CUSTOM_IMU_UUID)
            
            # TODO calculate the offset
            # np_rest_data = np.array(self.rest_data)
            # np_average_rest_data = np_rest_data.mean(axis=1)
            
            # np_ideal_linear_angular = np_average_rest_data[:, 1:7] # linear and angular data
            
            print(f'Calibration of {self.body_location} done.')
                
        except Exception as e:
            print(e)
        return
       
    async def collect(self, duration: int) -> None:
        if not self.is_connected:
            print(f"Unable to collect data from device on {self.body_location}.")
            return
        
        def callback(characteristic: BleakGATTCharacteristic, data: bytearray) -> None:
            timestamp, ax, ay, az, gx, gy, gz, mx, my, mz = struct.unpack("<Ifffffffff", data)
            if self.initial_timestamp == 0:
                self.initial_timestamp = timestamp
            modified_timestamp = timestamp - self.initial_timestamp # kasni za jedan?
            
            measured_data = IMU(modified_timestamp, ax, ay, az, gx, gy, gz, mx, my, mz)
            #calibrated_data = self.remove_offset(raw=measured_data, offset=self.offset)
            self.data.append(measured_data)
        
        try: 
            await self.client.start_notify(self.CUSTOM_IMU_UUID, callback)
            print(f'Collecting {self.body_location} data.')
            await asyncio.sleep(duration)
            await self.client.stop_notify(self.CUSTOM_IMU_UUID)
            
            print(f'Data collection from {self.body_location} done.')
        except Exception as e:
            print(e)
    
    def remove_offset(raw: IMU, offset: IMU) -> IMU:
        # TODO mozda ce trebat zasebni calibration offset za svaki element pošto se malo drugačije računanju
        return raw # za errore


    async def save_to_file(self):
        if len(self.data) == 0:
            return
        try:
            await self.client.disconnect()
            output_file = Path(self.file_path)
            output_file.parent.mkdir(exist_ok=True, parents=True)
            output_file.write_text("Timestamp, LinearX, LinearY, LinearZ, AngularX, AngularY, AngularZ, MagnetX, MagnetY, MagnetZ")
            
            print(f'Saving {self.body_location} data to file.')

            with open(self.file_path, 'w') as file:
                file.write("Timestamp, LinearX, LinearY, LinearZ, AngularX, AngularY, AngularZ, MagnetX, MagnetY, MagnetZ")
                for entry in self.data:
                    file.write(str(entry))
                file.flush()
        except Exception as e:
            print(e)
        