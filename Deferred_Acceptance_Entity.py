"""
Gale-Shapley algorithm for Stable Matching Problem (SMP) between two equally sized sets of elements, Proposers and
Responders
"""
from collections import namedtuple
from typing import List, Optional


class Proposer:
    NO_NEXT_PROPOSAL = -1

    def __init__(self, uuid: int, name: str = None):
        """
        :param uuid: universally unique identifier for proposer
        :param name: name of current proposer; if None name set to "Proposer proposer_uuid"
        """
        self.uuid = uuid
        self.name = name if name else "Proposer " + str(uuid)
        self.matched_to = None
        self.proposal_order = []
        self.last_proposed_to = -1

    def set_strict_preference(self, strict_preference: List[int]) -> None:
        """
        :param strict_preference: proposer make offer from most preferred to least preferred
        """
        self.proposal_order = strict_preference

    def set_weak_preference(self, weak_preference: List[List[int]]) -> bool:
        """
        :param weak_preference: list of sets of uuids, indifferent among uuids in the same rank_set, randomly break ties
        :return: return True if proposer shows strict preference among Responders
        """
        self.proposal_order = [responder_uuid for rank_set in weak_preference for responder_uuid in rank_set]
        return all(len(rank_set) <= 1 for rank_set in weak_preference)

    def validate(self, proposer_list: List[int], responder_list: List[int]) -> bool:
        """
        :param proposer_list: set of proposer_uuid of Proposers
        :param responder_list: set of proposer_uuid of Responders
        :return: whether the proposal order contains only valid responder proposer_uuid and contains no duplicates
        """
        return self.uuid in proposer_list and \
               len(set(responder_list).intersection(set(self.proposal_order))) == len(self.proposal_order)

    def propose_next(self) -> int:
        """
        :return: proposer_uuid for next Responder to propose to
        """
        if not self.proposal_order or self.last_proposed_to >= len(self.proposal_order) - 1:
            return self.NO_NEXT_PROPOSAL
        else:
            self.last_proposed_to += 1
            return self.proposal_order[self.last_proposed_to]

    def register_response(self, is_acceptance: bool = True):
        if is_acceptance:
            self.matched_to = self.proposal_order[self.last_proposed_to]
        else:
            self.matched_to = None


class Responder:
    def __init__(self, uuid: int, name: str = None):
        """
        :param uuid: universally unique identifier for responder
        :param name: name of current responder; if None name set to "Responder proposer_uuid"
        """
        self.uuid = uuid
        self.name = name if name else "Responder " + str(uuid)
        self.matched_to = None
        self.preference_order = dict()

    def set_strict_preference(self, strict_preference: List[int]) -> None:
        """
        :param strict_preference: strict preference over Proposers, list of uuids
        """
        self.preference_order = {uuid: preference_rank
                                 for preference_rank, uuid in enumerate(reversed(strict_preference))}

    def set_weak_preference(self, weak_preference: List[List[int]]) -> bool:
        """
        :param weak_preference: list of sets of uuids, indifferent among uuids in the same rank_set
        :return: return True if proposer shows strict preference among Responders
        """
        self.preference_order = {uuid: preference_rank
                                 for preference_rank, rank_set in enumerate(reversed(weak_preference))
                                 for uuid in rank_set}
        return all(len(rank_set) <= 1 for rank_set in weak_preference)

    def validate(self, proposer_list: List[int], responder_list: List[int]) -> bool:
        """
        :param proposer_list: set of proposer_uuid of Proposers
        :param responder_list: set of proposer_uuid of Responders
        :return: whether the preference order contains only valid proposer proposer_uuid and contains no duplicates
        """
        return self.uuid in responder_list and \
               len(set(proposer_list).intersection(set(self.preference_order))) == len(self.preference_order)

    def respond_to_proposal(self, proposer_uuid: int) -> Optional[int]:
        """
        only accepts the proposal if it is a strict improvement over existing self.matched_to
        :param proposer_uuid: proposer_uuid for current proposer
        :return: rejection sent to either new proposer or previously matched to
        """
        if self.preference_order.get(self.matched_to, -1) < self.preference_order.get(proposer_uuid, -1):
            previously_matched_to = self.matched_to
            self.matched_to = proposer_uuid
            return previously_matched_to
        else:
            return proposer_uuid


Proposal = namedtuple("Proposal", "proposal_id proposer_uuid responder_uuid rejected_uuid")
