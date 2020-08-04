"""
Gale-Shapley algorithm for Stable Matching Problem (SMP) between two equally sized sets of elements, Proposers and
Responders
"""
from itertools import count
from typing import List, Dict, Tuple, Optional

from Deferred_Acceptance_Entity import Responder, Proposer, Proposal


class Market:
    def __init__(self):
        self.uuid_proposer = count(1)
        self.uuid_responder = count(1001)
        self.proposer_uuid_dict = dict()
        self.responder_uuid_dict = dict()
        self.unmatched_proposer_uuid = set()
        self.count_proposer = 0
        self.count_responder = 0
        self.proposal_count = 0

    def register_proposer(self, name: str = None, uuid: int = None) -> int:
        """
        :param name: name of the proposer; if None name set to "Proposer proposer_uuid"
        :param uuid: override randomly generated system proposer_uuid with customer supplied proposer_uuid.
        :return: proposer_uuid of the proposer
        """
        new_uuid = uuid if uuid else next(self.uuid_proposer)
        new_proposer = Proposer(new_uuid, name)
        self.proposer_uuid_dict[new_uuid] = new_proposer
        self.unmatched_proposer_uuid.add(new_uuid)
        self.count_proposer += 1
        return new_uuid

    def register_proposer_proposal_order(self, uuid: int, proposal_order: List[int]) -> None:
        """
        Register proposal order of Proposer proposer_uuid
        :param uuid: proposer_uuid
        :param proposal_order: list of Acceptor proposer_uuid stating proposal order
        """
        self.proposer_uuid_dict[uuid].set_propose_order(proposal_order)

    def proposer_name_lookup_from_uuid(self) -> Dict[str, int]:
        """
        :return: a look up map from Proposer Name to Proposer proposer_uuid
        """
        return {proposer.uuid: proposer.name for proposer in self.proposer_uuid_dict.values()}

    def register_responder(self, name: str = None, uuid: int = None) -> int:
        """
        :param name: name of the responder; if None name set to "Responder proposer_uuid"
        :param uuid: override randomly generated system proposer_uuid with customer supplied proposer_uuid.
        :return: proposer_uuid of the responder
        """
        new_uuid = uuid if uuid else next(self.uuid_responder)
        new_responder = Responder(new_uuid, name)
        self.responder_uuid_dict[new_uuid] = new_responder
        self.count_responder += 1
        return new_uuid

    def register_responder_strict_preference(self, uuid: int, strict_preference: List[int]) -> None:
        """
        :param uuid: proposer_uuid for Responder
        :param strict_preference: list of Proposer uuids representing strict preference over them
        """
        self.responder_uuid_dict[uuid].set_strict_preference(strict_preference)

    def responder_name_lookup_from_uuid(self) -> Dict[str, int]:
        """
        :return: a look up map from Proposer Name to Proposer proposer_uuid
        """
        return {responder.uuid: responder.name for responder in self.responder_uuid_dict.values()}

    def test_valid_market_setup(self) -> Tuple[bool, bool, bool, Optional[str]]:
        """
        :return: 3 booleans and a string
            (1) whether proposer_uuid were assigned correctly
            (2) proposal orders for all Proposers are set properly
            (3) preference orders for all Responder set properly
            (4) first error message encountered, in case of error, or None
        """
        error_message = None
        if len(self.proposer_uuid_dict) != self.count_proposer:
            bool_market = False
            error_message = error_message if error_message else "Proposer proposer_uuid assigned incorrectly"
        elif len(self.responder_uuid_dict) != self.count_responder:
            bool_market = False
            error_message = error_message if error_message else "Responder proposer_uuid assigned incorrectly"
        else:
            bool_market = True

        bool_proposer = True
        for uuid, proposer in self.proposer_uuid_dict.items():
            if not proposer.validate(self.proposer_uuid_dict, self.responder_uuid_dict):
                bool_proposer = False
                error_message = error_message if error_message else "Proposer %s is incorrect" % proposer.name
                break

        bool_responder = True
        for uuid, responder in self.responder_uuid_dict.items():
            if not responder.validate(self.proposer_uuid_dict, self.responder_uuid_dict):
                bool_responder = False
                error_message = error_message if error_message else "Responder %s is incorrect" % responder.name
                break

        return bool_market, bool_proposer, bool_responder, error_message

    def has_more_proposal(self) -> bool:
        """
        :return: whether more proposer wants to makes offer
        """
        return len(self.unmatched_proposer_uuid) > 0

    def proposer_make_move(self, proposer_uuid: int) -> Proposal:
        """
        :param proposer_uuid: proposer proposer_uuid makes next proposal if he is currently unmatched
        :return: None, proposer_uuid, None, None if proposer is currently matched or proposer doesn't want to propose to
                    any one else
                else (proposal_id, proposer_uuid, responder_proposed_to, responder_rejected_proposer_uuid)
        """
        want_to_propose = self.proposer_uuid_dict[proposer_uuid]
        
        if want_to_propose.matched_to is not None:
            return None, proposer_uuid, None, None
        next_propose_to = want_to_propose.propose_next()
        if next_propose_to == Proposer.NO_NEXT_PROPOSAL:
            return None, proposer_uuid, None, None

        self.proposal_count += 1
        rejection_uuid = self.responder_uuid_dict[next_propose_to].respond_to_proposal(proposer_uuid)
        if rejection_uuid is None:
            want_to_propose.register_response(is_acceptance=True)
            self.unmatched_proposer_uuid.remove(proposer_uuid)
        elif rejection_uuid == proposer_uuid:
            pass
        else:
            want_to_propose.register_response(is_acceptance=True)
            rejected_proposer = self.proposer_uuid_dict[rejection_uuid]
            rejected_proposer.register_response(is_acceptance=False)
            self.unmatched_proposer_uuid.remove(proposer_uuid)
            self.unmatched_proposer_uuid.add(rejection_uuid)
        return Proposal(self.proposal_count, proposer_uuid, next_propose_to, rejection_uuid)

    def one_round_simultaneous_proposals(self):
        """
        every currently unmatched proposer simultaneously make their next proposal
        :return: list of (self.proposal_count, want_to_propose_uuid, next_propose_to, rejection_uuid) describing current
                round proposals, use interpret_proposal_outcome() to translate the output
        """
        proposals_in_current_round = []
        next_round_proposer_uuid = set()

        for want_to_propose_uuid in self.unmatched_proposer_uuid:
            want_to_propose = self.proposer_uuid_dict[want_to_propose_uuid]
            next_propose_to = want_to_propose.propose_next()
            if next_propose_to != Proposer.NO_NEXT_PROPOSAL:
                self.proposal_count += 1
                rejection_uuid = self.responder_uuid_dict[next_propose_to].respond_to_proposal(want_to_propose_uuid)
                if rejection_uuid is None:
                    want_to_propose.register_response(is_acceptance=True)
                elif rejection_uuid == want_to_propose_uuid:
                    next_round_proposer_uuid.add(want_to_propose_uuid)
                else:
                    want_to_propose.register_response(is_acceptance=True)
                    rejected_proposer = self.proposer_uuid_dict[rejection_uuid]
                    rejected_proposer.register_response(is_acceptance=False)
                    next_round_proposer_uuid.add(rejection_uuid)

                proposals_in_current_round.append(Proposal(self.proposal_count, want_to_propose_uuid,
                                                           next_propose_to, rejection_uuid))

        self.unmatched_proposer_uuid = next_round_proposer_uuid
        return proposals_in_current_round

    def interpret_proposal_outcome(self, proposal_outcome: Proposal) -> List[str]:
        """
        used to interpret proposal outcome of proposer_make_move(proposer_uuid)
        :param proposal_outcome: one Proposal named tuple, return value from proposer_make_move()
        :return: list of string describing the proposal and its outcome
        """
        proposal_outcome_description = []
        proposal_id, proposer_uuid, prosed_to_uuid, rejection_uuid = proposal_outcome
        if proposal_id:
            proposal_outcome_description.append('Proposal No. %d' % proposal_id)
            proposer_name = self.proposer_uuid_dict[proposer_uuid].name
            responder_name = self.responder_uuid_dict[prosed_to_uuid].name
            proposal_outcome_description.append('%s proposed to %s' % (proposer_name, responder_name))
            if rejection_uuid:
                if rejection_uuid == proposer_uuid:
                    proposal_outcome_description.append('%s rejected %s' % (responder_name, proposer_name))
                else:
                    proposal_outcome_description.append(
                        '%s rejected %s' % (responder_name, self.proposer_uuid_dict[rejection_uuid].name)
                    )
        return proposal_outcome_description

    def market_snapshot_uuid(self) -> Tuple[int, List[Tuple[Optional[int], Optional[int]]]]:
        """
        using uuid, describe matching situations among proposers and responders under current snapshot
        :return: (1) number of proposals that have been made
                (2) pairs of (proposer_uuid, responder_uuid) representing matching in current snapshot;
                    None stood in for unmatched proposer or responder
        """
        market_description = []
        for _, proposer in self.proposer_uuid_dict.items():
            market_description.append((proposer.uuid, proposer.matched_to))
        for _, responder in self.responder_uuid_dict.items():
            if responder.matched_to is None:
                market_description.append((None, responder.uuid))
        return self.proposal_count, market_description

    def market_snapshot_sentences(self) -> Tuple[int, List[str]]:
        """
        sentences describe matching situations among proposers and responders under current snapshot
        :return: (1) number of proposals that have been made (2) str describing matches made so far
        """
        market_description = []
        for _, proposer in self.proposer_uuid_dict.items():
            if proposer.matched_to:
                market_description.append('%s matched to %s' % (proposer.name,
                                                                self.responder_uuid_dict[proposer.matched_to].name))
            else:
                market_description.append('%s matched to %s' % (proposer.name, None))
        for _, responder in self.responder_uuid_dict.items():
            if responder.matched_to is None:
                market_description.append(('%s matched to %s' % (None, responder.name)))
        return self.proposal_count, market_description
