from random import sample

from Deferred_Acceptance_Market import Market

male_participants = ['m1', 'm2', 'm3']
male_preferences = {
    'm1': ['w1', 'w2', 'w3'],
    'm2': ['w3', 'w2', 'w1'],
    'm3': ['w3', 'w1', 'w2']
}
female_participants = ['w1', 'w2', 'w3']
female_preference = {
    'w1': ['m2', 'm3', 'm1'],
    'w2': ['m2', 'm3', 'm1'],
    'w3': ['m2', 'm1', 'm3']
}

test_Market = Market()
male_uuid_lookup = dict()
female_uuid_lookup = dict()
for male_name in male_participants:
    male_uuid = test_Market.register_proposer(male_name)
    male_uuid_lookup[male_name] = male_uuid
for female_name in female_participants:
    female_uuid = test_Market.register_responder(female_name)
    female_uuid_lookup[female_name] = female_uuid

for male_name, male_proposal_order in male_preferences.items():
    test_Market.register_proposer_proposal_order(male_uuid_lookup[male_name],
                                                 [female_uuid_lookup[female_name]
                                                  for female_name in male_proposal_order])
for female_name, female_preference_order in female_preference.items():
    test_Market.register_responder_strict_preference(female_uuid_lookup[female_name],
                                                     [male_uuid_lookup[male_name]
                                                      for male_name in female_preference_order])
bool_market, bool_proposer, bool_responder, error_message = test_Market.test_valid_market_setup()
assert bool_market and bool_proposer and bool_responder and error_message is None

round_outcome = test_Market.one_round_simultaneous_proposals()
for proposal_outcome in round_outcome:
    print(test_Market.interpret_proposal_outcome(proposal_outcome))
proposal_count, market_snapshot = test_Market.market_snapshot_sentences()
print("After %d proposals" % proposal_count)
print(market_snapshot)

while test_Market.has_more_proposal():
    proposer_id = sample(test_Market.unmatched_proposer_uuid, 1)[0]
    proposal_outcome = test_Market.proposer_make_move(proposer_id)
    print(test_Market.interpret_proposal_outcome(proposal_outcome))

proposal_count, market_snapshot = test_Market.market_snapshot_sentences()
print("After %d proposals" % proposal_count)
print(market_snapshot)

assert test_Market.proposer_make_move(1) == (None, 1, None, None)
assert test_Market.interpret_proposal_outcome((None, 1, None, None)) == []
assert test_Market.proposer_make_move(2) == (None, 2, None, None)
assert test_Market.interpret_proposal_outcome((None, 2, None, None)) == []
proposal_count, market_snapshot = test_Market.market_snapshot_sentences()
print("After %d proposals" % proposal_count)
print(market_snapshot)
