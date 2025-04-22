from Modules import classes
import math

def get_current_ratio() -> classes.QVector3:
    return classes.QVector3()

def rotate_point(center, point, angle):
    cx, cy = center
    px, py = point

    s = math.sin(math.radians(angle))
    c = math.cos(math.radians(angle))

    x_new = c * (px - cx) - s * (py - cy) + cx
    y_new = s * (px - cx) + c * (py - cy) + cy

    return x_new, y_new

def count_speed_module(vx, vy):
    return round(abs(math.sqrt(vx**2 + vy**2)), 2)



def calculate_height_from_pressure(P_ground, P_height, T=288.15, L=0.0065, R=8.31447, g=9.80665, M=0.0289644):
    # Преобразуем давление из гПа в Па
    P_ground = P_ground * 100
    P_height = P_height * 100
    
    # Вычисляем высоту по барометрической формуле
    exponent = (R * L) / (g * M)
    height = (T / L) * (1 - (P_height / P_ground) ** exponent)
    
    return round(height, 2)

def calculate_bearing(lat1, lon1, lat2, lon2):
    lat1_rad = math.radians(lat1)
    lon1_rad = math.radians(lon1)
    lat2_rad = math.radians(lat2)
    lon2_rad = math.radians(lon2)

    delta_lon = lon2_rad - lon1_rad

    x = math.sin(delta_lon) * math.cos(lat2_rad)
    y = math.cos(lat1_rad) * math.sin(lat2_rad) - math.sin(lat1_rad) * math.cos(lat2_rad) * math.cos(delta_lon)

    initial_bearing = math.atan2(x, y)
    bearing_degrees = (math.degrees(initial_bearing) + 360) % 360
    return bearing_degrees