import operator as op
from src.models.predicates import Assertion, Predicate

class FakeMsg:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.peers = {0}  # Predicate.eval checks len(l.peers) >= threshold

def test_assertion_on_arbitrary_message_type():
    a = Assertion('x', 'x', op.eq)
    assert a.eval(FakeMsg(1, 2), FakeMsg(1, 9)) is True
    assert a.eval(FakeMsg(1, 2), FakeMsg(3, 9)) is False

def test_predicate_on_arbitrary_message_type():
    p = Predicate(FakeMsg, FakeMsg, threshold=1, assertions=[Assertion('x', 'y', op.eq)])
    assert p.eval(FakeMsg(5, 5), FakeMsg(5, 5)) is True
    assert p.eval(FakeMsg(1, 2), FakeMsg(3, 4)) is False