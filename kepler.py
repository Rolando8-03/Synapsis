"""Modelo físico y muestras de los experimentos de Kepler de Synapsis."""
from dataclasses import dataclass
from functools import cached_property, lru_cache
from math import cos, floor, hypot, isfinite, pi, remainder, sin, sqrt, tau

CENTER_X, CENTER_Y = 300, 174
MAJOR, REFERENCE = 154, 48
WINDOW = tau * .08
MAX_TIME = 12
SAMPLES = 1200

@dataclass(frozen=True)
class Orbit:
    """Órbita ligada alrededor de un cuerpo dominante, en UA y años."""

    a: float
    e: float
    mu: float
    units: str = 'UA, año'

    def __post_init__(self):
        if self.units != 'UA, año':
            raise ValueError('Usá a en UA, t en años y μ en UA³/año².')
        if not isfinite(self.a) or self.a <= 0:
            raise ValueError('El semieje mayor debe ser positivo y finito.')
        if not isfinite(self.e) or not 0 <= self.e < 1:
            raise ValueError('La excentricidad debe ser mayor o igual a cero y menor que uno.')
        if not isfinite(self.mu) or self.mu <= 0:
            raise ValueError('El parámetro gravitacional debe ser positivo y finito.')
        if not isfinite(self.period) or self.period <= 0 or self.b <= 0:
            raise ValueError('Las dimensiones o el período exceden el rango de cálculo.')

    @cached_property
    def b(self):
        return self.a*sqrt((1-self.e)*(1+self.e))

    @cached_property
    def period(self):
        return tau*(self.a*sqrt(self.a/self.mu))



def eccentric_anomaly(mean, e):
    """Resolver M = E − e sen E en una vuelta mediante Newton acotado."""
    signed_mean = remainder(mean, tau)
    if not signed_mean or not e:
        return signed_mean % tau
    target = abs(signed_mean)
    lo, hi = 0.0, pi
    angle = target if e < .76 else pi
    for _ in range(80):
        if angle < .1:
            z = angle*angle
            # E − sen E sin cancelación cerca del perihelio.
            difference = angle*z*(1/6-z*(1/120-z*(1/5040-z/362880)))
        else:
            difference = angle-sin(angle)
        residual = (1-e)*angle + e*difference - target
        if residual == 0:
            break
        if residual > 0:
            hi = angle
        else:
            lo = angle
        slope = 1-e+2*e*sin(angle/2)**2
        candidate = angle-residual/slope
        if candidate == angle:
            break
        if not lo < candidate < hi:
            candidate = (lo+hi)/2
        if hi-lo <= 4e-15*max(hi,1e-15):
            angle = candidate
            break
        angle = candidate
    return (angle if signed_mean > 0 else -angle) % tau


@dataclass(frozen=True)
class Position:
    turns: int
    mean: float
    anomaly: float
    x: float
    y: float
    radius: float
    speed: float


def position(orbit, time):
    """Posición heliocéntrica y rapidez en el tiempo físico, sin escala gráfica."""
    cycles = time/orbit.period
    if not isfinite(cycles):
        raise ValueError('El tiempo debe representar un número finito de vueltas.')
    turns = floor(cycles)
    mean = tau*(cycles-turns)
    E = eccentric_anomaly(mean,orbit.e)
    deviation = 2*sin(E/2)**2
    x = orbit.a*((1-orbit.e)-deviation)
    y = orbit.b*sin(E)
    radius = hypot(x,y)
    speed = sqrt(orbit.mu/orbit.a)*sqrt(2/(radius/orbit.a)-1)
    return Position(turns,mean,E,x,y,radius,speed)


def planet_positions(first, second, time):
    if first.mu != second.mu or first.units != second.units:
        raise ValueError('Las dos órbitas deben compartir el cuerpo dominante y las unidades.')
    return position(first,time), position(second,time)


@dataclass(frozen=True)
class SweptSector:
    start_time: float
    end_time: float
    start: Position
    end: Position
    delta_anomaly: float
    area: float


def _measure_sector(orbit, start_time, end_time, end):
    start = position(orbit,start_time)
    delta = tau*(end.turns-start.turns)+(end.anomaly-start.anomaly)
    angle = delta-orbit.e*(sin(end.anomaly)-sin(start.anomaly))
    return SweptSector(start_time,end_time,start,end,delta,orbit.a*orbit.b*angle/2)


def measure_sector(orbit, start_time, end_time):
    if not start_time < end_time:
        raise ValueError('El final del sector debe seguir al inicio.')
    return _measure_sector(orbit,start_time,end_time,position(orbit,end_time))


def equal_sectors(orbit, time, current_position):
    duration = orbit.period*.08
    reference = time-orbit.period/2
    return (_measure_sector(orbit,time-duration,time,current_position),
            measure_sector(orbit,reference-duration,reference))


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


SOLAR_MU = tau**2  # Unidades normalizadas para que a = 1 UA tenga T = 1 año.


def orbital_readout(orbit):
    return {
        'a':orbit.a, 'b':orbit.b, 'e':orbit.e,
        'centro':-orbit.a*orbit.e, 'otro_foco':-2*orbit.a*orbit.e,
        'periodo':orbit.period, 'cociente':(orbit.period/orbit.a)**2/orbit.a,
    }


def position_readout(state):
    return {'p':[state.x,state.y], 'r':state.radius, 'v':state.speed,
            'M':state.mean, 'E':state.anomaly, 'vueltas':state.turns}


def sector_readout(section):
    return {'inicio_t':section.start_time, 'fin_t':section.end_time, 'area':section.area,
            'inicio':[section.start.x,section.start.y], 'fin':[section.end.x,section.end.y],
            'E_inicial':section.start.anomaly, 'E_final':section.end.anomaly,
            'delta_E':section.delta_anomaly, 'v':section.end.speed}


@lru_cache(maxsize=6)
def scene_frames(eccentricity, outer_a, outer_e):
    """Muestras sincronizadas de las dos órbitas y de los sectores de A."""
    if not .60 <= outer_a <= 3:
        raise ValueError('El semieje mayor de B debe estar entre 0,60 y 3 UA.')
    first, second = Orbit(1.0,eccentricity,SOLAR_MU), Orbit(outer_a,outer_e,SOLAR_MU)
    frames = []
    for i in range(SAMPLES+1):
        time = i*MAX_TIME/SAMPLES
        a, b = planet_positions(first,second,time)
        live, reference = equal_sectors(first,time,a)
        frames.append({'t':time, 'A':position_readout(a), 'B':position_readout(b),
                       'actual':sector_readout(live), 'referencia':sector_readout(reference)})
    return {'mu':first.mu, 'A':orbital_readout(first), 'B':orbital_readout(second),
            'cociente_teorico':tau**2/first.mu, 'duracion_sector':first.period*.08,
            'frames':frames}
