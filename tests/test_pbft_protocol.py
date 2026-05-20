import pytest
from src.protocols.pbft import PBFTProtocol, PrePrepare, Prepare, Commit, ViewChange

protocol = PBFTProtocol()

# Group A: PRE-PREPARE operation mutation, validity+agreement violation
OPERATION_CORRUPTION_FILE = 'out/tests-D0-C1-ss/out95.txt'
# Group B: PRE-PREPARE seq-number mutation (also Operation Corruption in 5-class)
OPERATION_CORRUPTION_SEQ_FILE = 'out/tests-D1-C2-ss/out7.txt'
# Group C: VC/NV mutation, termination
VIEW_CHANGE_FAULT_FILE = 'out/tests-D1-C2-ss/out49.txt'
# Group D: pure partition stall, termination, no Byzantine mutation
PARTITION_TIMEOUT_FILE = 'out/tests-D1-C0/out115.txt'
# Group F: COMMIT/PREPARE/REPLY mutation + partition, termination
NON_PP_MUTATION_FILE = 'out/tests-D1-C1-as/out57.txt'
# Group E: split-brain, agreement at view ≥ 2
SPLIT_BRAIN_FILE = 'out/tests-D2-C0/out87.txt'
# correct run (no violation)
CORRECT_FILE = 'out/tests-D1-C0/out1.txt'

def _skip_if_absent(path):
    import os
    if not os.path.exists(path):
        pytest.skip(f'{path} not present')

def test_get_num_nodes():
    assert protocol.get_num_nodes() == 4

def test_get_bug_types():
    assert set(protocol.get_bug_types()) == {
        'Operation Corruption', 'View-Change Fault',
        'Partition Timeout', 'Non-PP Mutation', 'Split Brain',
    }

def test_get_fields_covers_root_causes():
    fields = protocol.get_fields()
    field_names = [f[1] for f in fields]
    # Operation Corruption requires PRE-PREPARE fields
    assert 'operation_first' in field_names
    assert 'seq_no' in field_names
    # View-Change Fault requires VIEW-CHANGE
    assert 'new_view_no' in field_names

def test_classify_run_operation_corruption_op():
    _skip_if_absent(OPERATION_CORRUPTION_FILE)
    result = protocol.classify_run(OPERATION_CORRUPTION_FILE)
    assert 'Operation Corruption' in result

def test_classify_run_operation_corruption_seq():
    _skip_if_absent(OPERATION_CORRUPTION_SEQ_FILE)
    result = protocol.classify_run(OPERATION_CORRUPTION_SEQ_FILE)
    assert 'Operation Corruption' in result

def test_classify_run_view_change_fault():
    _skip_if_absent(VIEW_CHANGE_FAULT_FILE)
    result = protocol.classify_run(VIEW_CHANGE_FAULT_FILE)
    assert 'View-Change Fault' in result

def test_classify_run_partition_timeout():
    _skip_if_absent(PARTITION_TIMEOUT_FILE)
    result = protocol.classify_run(PARTITION_TIMEOUT_FILE)
    assert 'Partition Timeout' in result

def test_classify_run_non_pp_mutation():
    _skip_if_absent(NON_PP_MUTATION_FILE)
    result = protocol.classify_run(NON_PP_MUTATION_FILE)
    assert 'Non-PP Mutation' in result

def test_classify_run_split_brain():
    _skip_if_absent(SPLIT_BRAIN_FILE)
    result = protocol.classify_run(SPLIT_BRAIN_FILE)
    assert 'Split Brain' in result

def test_is_successful_on_non_violation():
    _skip_if_absent(CORRECT_FILE)
    assert protocol.is_successful(CORRECT_FILE) is True

def test_parse_log_returns_preprepare():
    _skip_if_absent(OPERATION_CORRUPTION_FILE)
    messages = protocol.parse_log(OPERATION_CORRUPTION_FILE)
    assert any(isinstance(m, PrePrepare) for m in messages)

def test_filter_messages_is_noop():
    class Msg: pass
    msgs = [Msg(), Msg()]
    assert protocol.filter_messages(msgs, node_id=0) is msgs

def test_wrap_observations_single_entry():
    obs = protocol.wrap_observations('some_pred', observed_nodes={0})
    # PBFT: one threshold entry (observed by >= 1 replica)
    assert '"some_pred" > 0' in obs
    assert obs['"some_pred" > 0'] is True