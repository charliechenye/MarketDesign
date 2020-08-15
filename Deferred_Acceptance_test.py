from Deferred_Acceptance_Entity import Proposer

test_proposer = Proposer(1, 'a')
test_preference = [10, 2, 3, 9, 11]
test_proposer.set_strict_preference(test_preference)
assert test_proposer.validate([1], [2, 3, 9, 10, 11])
for i in test_preference:
    assert test_proposer.propose_next() == i
for _ in range(5):
    assert test_proposer.propose_next() == Proposer.NO_NEXT_PROPOSAL


test_proposer.set_strict_preference(test_preference + [2])
assert not test_proposer.validate([1], [2, 3, 9, 10, 11])
