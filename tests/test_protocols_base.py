from src.protocols.base import ConsensusProtocol
import inspect

def test_is_abstract():
    assert inspect.isabstract(ConsensusProtocol)

def test_required_methods():
    required = {
        'get_fields', 'parse_log', 'get_num_nodes',
        'filter_messages', 'is_successful', 'classify_run',
        'get_bug_types', 'wrap_observations'
    }
    abstract_methods = ConsensusProtocol.__abstractmethods__
    assert required == abstract_methods

def test_filter_aggregation_default_is_noop():
    """filter_aggregation has a default implementation so subclasses need not override it."""
    class MinimalProtocol(ConsensusProtocol):
        def get_fields(self): return []
        def parse_log(self, path): return []
        def get_num_nodes(self): return 1
        def filter_messages(self, msgs, node_id): return msgs
        def is_successful(self, run_dir): return True
        def classify_run(self, run_dir): return set()
        def get_bug_types(self): return []
        def wrap_observations(self, pred, observed_nodes): return {}
    p = MinimalProtocol()
    d = {'key': 'value'}
    assert p.filter_aggregation(d) is d  # default returns same dict unchanged