from dataclasses import dataclass, field


@dataclass
class Environment:
    hostname: str = field(default=None)
    location: str = field(default=None)
    ip_address: str = field(default=None)
