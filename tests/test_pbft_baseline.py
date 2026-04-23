import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.protocols.pbft import PBFTProtocol


def test_parse_baseline_observations_successful_run(tmp_path):
    log = tmp_path / "out1.txt"
    log.write_text(
        "PRED BRANCH DefaultReplica.java:282 R0 0\n"
        "PRED BRANCH DefaultReplica.java:282 R1 1\n"
        "PRED BRANCH DefaultReplica.java:393 R0 1\n"
        "PRED WHILE PropertyChecker.java:119 R2 0\n"
        "Task completed.\n"
    )
    proto = PBFTProtocol()
    result = proto.parse_baseline_observations(str(log))
    assert result is not None
    success, obs, name = result
    assert success is True
    assert obs["BRANCH DefaultReplica.java:282 is true"] is True
    assert obs["BRANCH DefaultReplica.java:282 is false"] is True
    assert obs["BRANCH DefaultReplica.java:393 is true"] is True
    assert obs["BRANCH DefaultReplica.java:393 is false"] is False
    assert "out1.txt" in name  # run_name is full path


def test_parse_baseline_observations_failing_run(tmp_path):
    log = tmp_path / "out42.txt"
    log.write_text(
        "PRED BRANCH DefaultReplica.java:282 R0 1\n"
        "Violation of AGREEMENT at Replica: 0 viewNo: 0 seqNo: 1\n"
        "Task completed.\n"
    )
    proto = PBFTProtocol()
    result = proto.parse_baseline_observations(str(log))
    assert result is not None
    success, obs, name = result
    assert success is False
    assert "out42.txt" in name  # run_name is full path


def test_parse_baseline_observations_timeout_run(tmp_path):
    log = tmp_path / "out99.txt"
    log.write_text(
        "PRED BRANCH DefaultReplica.java:282 R0 0\n"
        "Reached test duration\n"
    )
    proto = PBFTProtocol()
    result = proto.parse_baseline_observations(str(log))
    success, obs, name = result
    assert success is False


def test_parse_baseline_or_aggregation_across_replicas(tmp_path):
    log = tmp_path / "out1.txt"
    log.write_text(
        "PRED BRANCH DefaultReplica.java:100 R0 0\n"
        "PRED BRANCH DefaultReplica.java:100 R1 0\n"
        "PRED BRANCH DefaultReplica.java:100 R2 0\n"
        "PRED BRANCH DefaultReplica.java:100 R3 1\n"
        "Task completed.\n"
    )
    proto = PBFTProtocol()
    success, obs, name = proto.parse_baseline_observations(str(log))
    assert obs["BRANCH DefaultReplica.java:100 is true"] is True
    assert obs["BRANCH DefaultReplica.java:100 is false"] is True
