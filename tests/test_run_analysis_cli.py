import subprocess, sys

def test_help_flag():
    result = subprocess.run(
        [sys.executable, 'scripts/run_analysis.py', '--help'],
        cwd='/Users/addacarutasu/thesis/consensus-bug-isolation',
        capture_output=True, text=True
    )
    assert result.returncode == 0
    assert '--protocol' in result.stdout

def test_unknown_protocol_exits():
    result = subprocess.run(
        [sys.executable, 'scripts/run_analysis.py', '--protocol', 'unknown'],
        cwd='/Users/addacarutasu/thesis/consensus-bug-isolation',
        capture_output=True, text=True
    )
    assert result.returncode != 0