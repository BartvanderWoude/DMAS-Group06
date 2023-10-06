import numpy as np


## This file helps implement the custom strategies (3 mechanics * 3 tactics = 9 different agent types)

# TO IMPLEMENT A NEW MECHANIC: create a class
# TODO CHECK FULL DESC - THIS (vvv) DOESNT WORK ATM - FOR NOW ADD THE IMPLEMENTATION TO THE TRADER AGENT CLASS
# TO IMPLEMENT A NEW STRATEGY: add a strat to the right class init, and implement your behavior in the correct function with "if self.strategies=='whatever': behavior X " 
class CustomStrategies():
    def __init__(self):
        self.mechanics = {
            "witness": WitnessStrategies(),
            # "offer": OfferStrategies(),
            "trust_update": TrustUpdateStrategies(),
            # "getwitness": RecruitWitnessStrategies(),

        }


# TODO: possibly a Strategy class to inherit from
# -=here=-

# TODO: Implement strategy logic here
class WitnessStrategies():
    def __init__(self):
        self.strategies = ["standard", "skeptic", "naive"]
        self.colors = {"standard": "red",
                       "skeptic": "#F88379",
                       "naive": "#A42A04"
                       }
        for i, key in enumerate(self.colors):
            if self.strategies[i] != key:
                print(self.strategies[i], key)
                raise ValueError
        # if len(self.strategies) != len(self.colors):
        # raise valueError

    def calculateTrust(agent, partner, witness):
        """Method to calculate the trust value of trade partner (target agent) based on strategy"""
        trust_in_partner = agent.trust_per_trader[partner.unique_id]
        trust_in_witness = agent.trust_per_trader[witness.unique_id]
        witness_trust_in_partner = witness.trust_per_trader[partner.unique_id]

        tactic = agent.custom_strategies['witness']
        # agent.strategies.trust_tactic # TODO: this is not implemented yet

        if tactic == 'standard':
            trust = (trust_in_partner + witness_trust_in_partner) / 2  # standaard
        elif tactic == 'not_trust_witness':
            trust = trust_in_partner
        elif tactic == 'partially_trust_witness':
            trust = (((trust_in_witness + witness_trust_in_partner) / 2) + trust_in_partner) / 2
        else:
            raise NotImplementedError
        return trust

    # Preferable method - no implemented mechanic yet (if you implement this, remove "or True" below)
    def findWitness(agent, agent_list):
        tactic = agent.custom_strategies['witness']
        if tactic == "standard" or True:
            witness = np.random.choice(agent_list)
        elif tactic == "implement here":
            raise NotImplementedError
        else:
            raise NotImplementedError
        agent_list.remove(witness)
        return witness, agent_list

class RecruitWitnessStrategies():
    def __init__(self):
        self.strategies = ["standard"] #, "highvalue"] #TODO uncomment when wanting to implement this feature
        self.shapes = {"standard": "circle"}
                       # "highvalue": "rect"}

        for i, key in enumerate(self.shapes):
            if self.strategies[i] != key:
                raise ValueError

class OfferStrategies():
    def __init__(self):
        self.strategies = ["standard", "extra1"]
        self.shapes = {"standard": "circle",
                       "extra1": "rect"}

        for i, key in enumerate(self.shapes):
            if self.strategies[i] != key:
                raise ValueError
        # if len(self.strategies) != len(self.shapes):
        #   raise valueError

    def calculateOffer(agent, trust_in_target_agent):
        tactic = agent.custom_strategies['offer']
        if agent.offer_tactic == "standard":
            return np.clip(trust_in_target_agent * agent.honesty * 100, 0, 100)
        else:
            raise NotImplementedError


class TrustUpdateStrategies():
    def __init__(self):
        self.strategies = ["standard", "witness_included", "critical"]
        self.text = {"standard": "s",
                     "witness_included": "w",
                     "critical": "c"}

        for i, key in enumerate(self.text):
            if self.strategies[i] != key:
                raise ValueError
        # if len(self.strategies) != len(self.text):
        # raise ValueError

    # Ways to update trust:
    #   standard: only update your trust in the trading partner
    #   include_witness: include the witness to some extent (same as partner or less? more?)
    def updateTrustValues(agent, gain_or_loss, partner, witness):
        tactic = agent.custom_strategies['trust_update']
        if tactic == "standard":
            trust_update_value = gain_or_loss / 5
            current_trust = agent.trust_per_trader[partner.unique_id]
            agent.trust_per_trader[partner.unique_id] = max(0, min(100, current_trust + trust_update_value))
        else:
            raise NotImplementedError
        return
