"""Protocol adapter registry.

`make_protocol(name)` is the single entry point used by the analysis CLIs
to instantiate a `ConsensusProtocol` from a string identifier.
"""

from .base import ConsensusProtocol


def make_protocol(name: str) -> ConsensusProtocol:
    """Instantiate a protocol adapter by name.

    Recognised names: 'xrpl', 'pbft', 'redisraft'.
    """
    name = (name or '').lower()
    if name == 'xrpl':
        from .xrpl import XRPLProtocol
        return XRPLProtocol()
    if name == 'pbft':
        from .pbft import PBFTProtocol
        return PBFTProtocol()
    if name == 'redisraft':
        from .redisraft import RedisRaftProtocol
        return RedisRaftProtocol()
    raise ValueError(f'unknown protocol: {name!r}')


PROTOCOL_CHOICES = ('xrpl', 'pbft', 'redisraft')
