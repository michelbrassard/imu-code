# VIDI KASNIJE JEL IMA SMISLA IMATI OVU KLASU ILI KORISTITI NUMPY?
# Mozda bolje ako treba prepisat u C++???

class IMU:
    def __init__(self, timestamp, ax: float, ay: float, az: float, gx: float, gy: float, gz: float, mx: float, my: float, mz: float):
        self.timestamp = timestamp
        self.ax = ax
        self.ay = ay
        self.az = az
        self.gx = gx
        self.gy = gy
        self.gz = gz
        self.mx = mx
        self.my = my
        self.mz = mz
    
    def to_array(self):
        return [self.timestamp, self.ax, self.ay, self.az, self.gx, self.gy, self.gz, self.mx, self.my, self.mz]
        
    def get_linear(self):
        return [self.ax, self.ay, self.az]

    def get_gyro(self):
        return [self.gx, self.gy, self.gz]
    
    def get_magnet(self):
        return [self.mx, self.my, self.mz]

    def remove_offset(self, offset):
        # timestamp se normalizira u device
        self.ax - offset.ax
        self.ay - offset.ay
        self.az - offset.az
        self.gx - offset.gx
        self.gy - offset.gy
        self.gz - offset.gz
        # zasad nema magnetometer data
        return 0
    
    def __str__(self) -> str:
        return f'{self.timestamp}, {self.ax}, {self.ay}, {self.az}, {self.gx}, {self.gy}, {self.gz}, {self.mx}, {self.my}, {self.mz} \n'