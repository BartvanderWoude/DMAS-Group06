import numpy as np


## This file helps implement the custom strategies (3 mechanics * 3 tactics = 9 different agent types)

# TO IMPLEMENT A NEW MECHANIC: create a class
# TODO CHECK FULL DESC - THIS (vvv) DOESNT WORK ATM - FOR NOW ADD THE IMPLEMENTATION TO THE TRADER AGENT CLASS
# TO IMPLEMENT A NEW STRATEGY: add a strat to the right class init, and implement your behavior in the correct function with "if self.strategies=='whatever': behavior X " 
class CustomStrategies():
    def __init__(self):
        self.mechanics = {
            "witness": WitnessStrategies(),
            "offer": OfferStrategies(),
            "trust_update": TrustUpdateStrategies(),
            "getwitness": RecruitWitnessStrategies()
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

    def calculateTrust(self, agent, partner, witness):
        """Method to calculate the trust value of trade partner (target agent) based on strategy"""
        trust_in_partner = agent.trust_per_trader[partner.unique_id]
        trust_in_witness = agent.trust_per_trader[witness.unique_id]
        witness_trust_in_partner = witness.trust_per_trader[partner.unique_id]

        tactic = agent.custom_strategies['witness']

        # agent.strategies.trust_tactic # TODO: this is not implemented yet

        if tactic == 'standard':
            trust = (trust_in_partner + witness_trust_in_partner) / 2  # standaard
        elif tactic == 'naive':
            trust = trust_in_partner
        elif tactic == 'skeptic':
            trust = (((trust_in_witness + witness_trust_in_partner) / 2) + trust_in_partner) / 2
        else:
            raise NotImplementedError

        return trust

class RecruitWitnessStrategies():
    def __init__(self):
        self.strategies = ["standard"] #, "highvalue"] #TODO uncomment when wanting to implement this feature
        self.shapes = {"standard": "circle"}
                       # "highvalue": "rect"}

        for i, key in enumerate(self.shapes):
            if self.strategies[i] != key:
                raise ValueError
            
    # Preferable method - no implemented mechanic yet (if you implement this, remove "or True" below)
    def findWitness(self, agent, agent_list, id_trader):
        tactic = agent.custom_strategies['getwitness']
        if tactic == "standard":
            witness = np.random.choice(agent_list)
        elif tactic == "highvalue": #TODO make this working, gets error when removing from the agent_list below
            temp_dict = {index: value for index, value in enumerate(agent.trust_per_trader)}
            temp_dict.pop(agent.unique_id, None)
            temp_dict.pop(id_trader, None)
            witness_id = max(temp_dict, key=temp_dict.get)          #TODO this is not random i believe (in case of tie)
            witness = agent.model.get_agent_by_id(witness_id)
            print(witness.unique_id, agent.unique_id, id_trader)
        else:
            raise NotImplementedError
        agent_list.remove(witness)
        return witness

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

    def calculateOffer(self, agent, trust_in_target_agent):
        tactic = agent.custom_strategies['offer']
        
        if tactic == "standard":
            offer = np.clip(((trust_in_target_agent + agent.honesty) / 2) * 100, 0, 100)
        elif tactic == "extra1":
            offer = np.clip(((trust_in_target_agent + agent.honesty) / 2) * 100, 0, 100)     #TODO no difference, needs change if we want this functionality
        else:
            raise NotImplementedError
        
        return offer


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
    def updateTrustValues(self, agent, gain_or_loss, partner, witness):
        tactic = agent.custom_strategies['trust_update']
        if tactic == "standard":
            trust_update_value = gain_or_loss / 5
            current_trust = agent.trust_per_trader[partner.unique_id]
            agent.trust_per_trader[partner.unique_id] = max(0, min(100, current_trust + trust_update_value))
        elif tactic == "witness_included":
            trust_update_value = gain_or_loss / 5
            current_trust = agent.trust_per_trader[partner.unique_id]
            agent.trust_per_trader[partner.unique_id] = max(0, min(100, current_trust + trust_update_value))
            current_witness_trust = agent.trust_per_trader[witness.unique_id]
            agent.trust_per_trader[witness.unique_id] = max(0, min(100, current_witness_trust + trust_update_value))
        elif tactic == "critical":
            current_trust = agent.trust_per_trader[partner.unique_id]
            trust_update_value = (gain_or_loss / 5) * (0.1 * current_trust)
            agent.trust_per_trader[partner.unique_id] = max(0, min(100, current_trust + trust_update_value))
        else:
            raise NotImplementedError
        return
