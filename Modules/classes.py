

class QVector3:
    roll:float
    pitch:float
    yaw:float

    def __init__(self, roll=0.0, pitch=0.0, yaw=0.0):
        self.roll, self.pitch, self.yaw = roll, pitch, yaw

class Global_Position:
    alt: int
    relative_alt: int
    vz: int
    vx: int
    vy: int

    def __init__(self, alt=0, relative_alt=0, vz=0, vx=0, vy=0):
        self.alt, self.relative_alt, self.vz, self.vx, self.vy = alt, relative_alt, vz, vy, vz
        
