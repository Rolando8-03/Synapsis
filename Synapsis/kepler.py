"""Coordinate samples and readouts for the three interactive Kepler experiments."""
from functools import lru_cache
from math import cos, isfinite, pi, sin, sqrt, tau

CENTER_X, CENTER_Y = 300, 174
MAJOR, REFERENCE = 154, 48
WINDOW = tau * .08
MAX_TIME = 12
SAMPLES = 1200

def eccentric_anomaly(mean, e):
    mean %= tau
    angle = mean if e < .76 else pi
    for _ in range(16):
        correction = (angle - e*sin(angle) - mean) / (1 - e*cos(angle))
        angle -= correction
        if abs(correction) < 1e-12:
            break
    return angle

def point(angle, major, minor):
    return round(CENTER_X + major*cos(angle), 4), round(CENTER_Y - minor*sin(angle), 4)

def sector(mean, e, minor, focus):
    start = eccentric_anomaly(mean - WINDOW, e)
    stop = eccentric_anomaly(mean, e)
    x0,y0 = point(start, MAJOR, minor)
    x1,y1 = point(stop, MAJOR, minor)
    arc = int((stop-start) % tau > pi)
    return f"M{focus:.3f} {CENTER_Y}L{x0} {y0}A{MAJOR} {minor:.3f} 0 {arc} 0 {x1} {y1}Z"

@lru_cache(maxsize=24)
def orbital_frames(law, shape):
    if not isfinite(shape) or not (law in (1, 2) and 0 <= shape <= .88 or law == 3 and .60 <= shape <= 3):
        raise ValueError("El parámetro orbital está fuera del intervalo.")
    frames = []
    if law == 3:
        radius = shape * REFERENCE
        period = shape**1.5
        for i in range(SAMPLES + 1):
            time = i * MAX_TIME / SAMPLES
            frames.append([*point(tau*time, REFERENCE, REFERENCE),
                           *point(tau*time/period + .72, radius, radius)])
        return {"duration":MAX_TIME,"radius":radius,"period":period,"ratio":period**2 / shape**3,
                "frames":frames}
    minor, offset = MAJOR * sqrt(1-shape**2), MAJOR * shape
    focus, other = CENTER_X + offset, CENTER_X - offset
    for i in range(SAMPLES + 1):
        mean = tau*i / SAMPLES
        angle = eccentric_anomaly(mean, shape)
        radius = 1-shape*cos(angle)
        frame = [*point(angle, MAJOR, minor), round(radius,8)]
        if law == 1:
            other_radius = 1+shape*cos(angle)
            frame.extend([round(other_radius,8),round(radius+other_radius,8)])
        else:
            frame.extend([round(sqrt(2/radius-1),8),sector(mean,shape,minor,focus),sector(mean-pi,shape,minor,focus)])
        frames.append(frame)
    return {"duration":1,"minor":minor,"focus":focus,"other":other,"area_percent":round(100*WINDOW/tau),
            "frames":frames}
