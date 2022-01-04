from dataclasses import dataclass


@dataclass
class InfluxSettings:
    url: str
    token: str
    org: str
    bucket: str
