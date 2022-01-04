from dataclasses import dataclass, field


@dataclass
class Climate:
    """ Dataclass to store climate data"""
    temperature: float = field(default=-999.0)
    humidity: float = field(default=-999.0)
