import math
from pymavlink import mavutil

class Adapter:
    def __init__(self, connection_string):
        self.master = mavutil.mavlink_connection(connection_string, baud=921600)
        self.master.wait_heartbeat()

        self.data = {
            "heading": None,
            "airspeed": None,
            "attitude": {
                "roll": None,
                "pitch": None,
                "yaw": None,
            },
            "global_position": {
                "alt": None,
                "relative_alt": None,
                "vz": None,
                "vx": None,
                "vy": None,
            },
            "pressure": {
                "abs_pressure": None,
                "diff_pressure": None,
            },
            "gps": {
                "lat": None,
                "lon": None
            },
            "wind": {
                "var_horiz": 0
            }
        }
        self.arm_disarm()

    def arm_disarm(self, arm=True):
        self.master.mav.command_long_send(
            self.master.target_system,
            self.master.target_component,
            mavutil.mavlink.MAV_CMD_COMPONENT_ARM_DISARM,
            0,
            int(arm),
            0, 0, 0, 0, 0, 0
        )


    def update(self):
        message = self.master.recv_match(blocking=False)
        if not message:
            return
        
        if message.get_type() == "GPS_RAW_INT":
            #print(self.data["gps"])
            self.data["gps"]["lat"] = message.lat
            self.data["gps"]["lon"] = message.lon
        
        elif message.get_type() == "HIL_GPS":
            self.data["gps_speed"] = message.vel // 100

        elif message.get_type() == "ATTITUDE":
            self.data["attitude"] = {
                "roll": math.degrees(round(message.roll, 2)),
                "pitch": math.degrees(round(message.pitch, 2)),
                "yaw": math.degrees(round(message.yaw, 2))
            }

        elif message.get_type() == "GLOBAL_POSITION_INT":
            self.data["global_position"] = {
                "alt": round(message.alt / 1000.0, 2),
                "relative_alt": round(message.relative_alt / 1000.0, 2),
                "vx": round(message.vx / 100.0, 2),
                "vy": round(message.vy / 100.0, 2),
                "vz": round(message.vz / 100.0, 2),
            }

        elif message.get_type() == "VFR_HUD":
            self.data["airspeed"] = round(message.airspeed)
            self.data["heading"] = round(message.heading, 2)
            self.data["global_position"]["alt"] = round(message.alt, 2)

        elif message.get_type() == "SCALED_PRESSURE":
            self.data["pressure"] = {
                "abs_pressure": round(message.press_abs, 2),
                "diff_pressure": round(message.press_diff, 2),
            }

if __name__ == "__main__":
    connection_string = "udp:192.168.4.3:14550"
    adapter = Adapter(connection_string)

    while True:
        adapter.update()
