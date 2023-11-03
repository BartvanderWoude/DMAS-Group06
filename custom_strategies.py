import numpy as np


## This file helps implement the custom strategies (3 mechanics * 3 tactics = 9 different agent types)

# TO IMPLEMENT A NEW MECHANIC: create a class
class CustomStrategies():
    def __init__(self):
        self.mechanics = {
            "witness": WitnessStrategies(),
            "offer": OfferStrategies(),
            "trust_update": TrustUpdateStrategies(),
            "getwitness": RecruitWitnessStrategies()
        }

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

    def calculateTrust(self, agent, partner, witness):
        """Method to calculate the trust value of trade partner (target agent) based on strategy"""
        trust_in_partner = agent.trust_per_trader[partner.unique_id]
        trust_in_witness = agent.trust_per_trader[witness.unique_id]
        witness_trust_in_partner = witness.trust_per_trader[partner.unique_id]

        tactic = agent.custom_strategies['witness']

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
        self.strategies = ["standard"]  # , "highvalue"]
        self.shapes = {"standard": "circle"}
        # "highvalue": "rect"}

        for i, key in enumerate(self.shapes):
            if self.strategies[i] != key:
                raise ValueError

    def findWitness(self, agent, agent_list, id_trader):
        tactic = agent.custom_strategies['getwitness']
        if tactic == "standard":
            witness = np.random.choice(agent_list)
        elif tactic == "highvalue":
            temp_dict = {index: value for index, value in enumerate(agent.trust_per_trader)}
            temp_dict.pop(agent.unique_id, None)
            temp_dict.pop(id_trader, None)
            witness_id = max(temp_dict, key=temp_dict.get)
            witness = agent.model.get_agent_by_id(witness_id)
            print(witness.unique_id, agent.unique_id, id_trader)
        else:
            raise NotImplementedError
        agent_list.remove(witness)
        return witness


class OfferStrategies():
    def __init__(self):
        self.strategies = ["standard"]
        self.shapes = {"standard": "circle"}

        for i, key in enumerate(self.shapes):
            if self.strategies[i] != key:
                raise ValueError

    def calculateOffer(self, agent, trust_in_target_agent):
        tactic = agent.custom_strategies['offer']

        if tactic == "standard":
            offer = np.clip((trust_in_target_agent * agent.honesty) * 100, 0, 100)
        elif tactic == "extra1":
            offer = np.clip((trust_in_target_agent * agent.honesty) * 100, 0, 100)
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

    def updateTrustValues(self, agent, gain_or_loss, partner, witness):
        tactic = agent.custom_strategies['trust_update']
        gain_or_loss /= 100  # refactor test
        if tactic == "standard":
            trust_update_value = gain_or_loss / 5
            current_trust = agent.trust_per_trader[partner.unique_id]
            agent.trust_per_trader[partner.unique_id] = np.clip(current_trust + trust_update_value, 0, 1)
        elif tactic == "witness_included":
            trust_update_value = gain_or_loss / 5
            current_trust = agent.trust_per_trader[partner.unique_id]
            agent.trust_per_trader[partner.unique_id] = np.clip(current_trust + trust_update_value, 0, 1)
            current_witness_trust = agent.trust_per_trader[witness.unique_id]
            agent.trust_per_trader[witness.unique_id] = np.clip(current_witness_trust + trust_update_value, 0, 1)
        elif tactic == "critical":
            current_trust = agent.trust_per_trader[partner.unique_id]
            trust_update_value = (gain_or_loss / 5) * current_trust
            agent.trust_per_trader[partner.unique_id] = np.clip(current_trust + trust_update_value, 0, 1)
        else:
            raise NotImplementedError
        return
