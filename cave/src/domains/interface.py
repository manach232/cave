from ..networks.network.network import Network
from dataclasses import dataclass
@dataclass
class Interface:
    mac: str
    network: Network
    ipv4: str
    prefix_length: int
    is_mngmt: bool

