class IMU:
    def __init__(self, timestamp, ax, ay, az, gx, gy, gz, mx, my, mz):
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
    
    def __str__(self) -> str:
        return f'{self.timestamp}, {self.ax}, {self.ay}, {self.az}, {self.gx}, {self.gy}, {self.gz}, {self.mx}, {self.my}, {self.mz} \n'