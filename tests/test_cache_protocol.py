import operator as op
from src.protocols.xrpl import XRPLProtocol
from src.analysis.cache import build_predicates, set_protocol

def test_build_predicates_xrpl_count():
    protocol = XRPLProtocol()
    predicates, by_type = build_predicates(protocol)
    # Baseline: XRPL currently generates ~4496 predicates
    assert len(predicates) > 4000

def test_build_predicates_returns_by_type_index():
    protocol = XRPLProtocol()
    _, by_type = build_predicates(protocol)
    from src.models.messages import Proposal, Validation
    assert (Proposal, Proposal) in by_type
    assert (Proposal, Validation) in by_type
    assert (Validation, Validation) in by_type

def test_set_protocol_stores_protocol():
    protocol = XRPLProtocol()
    set_protocol(protocol)
    from src.analysis import cache as c
    assert c._PROTOCOL is protocol

class MinimalProtocol(XRPLProtocol):
    """Protocol with a single field pair — generates far fewer predicates."""
    def get_fields(self):
        from src.models.messages import Proposal
        return [(Proposal, 'propose_seq', 'seq_prp')]

def test_build_predicates_respects_protocol_fields():
    protocol = MinimalProtocol()
    predicates, _ = build_predicates(protocol)
    # Only Proposal->Proposal predicates with seq_prp field
    assert len(predicates) < 100