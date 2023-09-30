import random
import mesa
import seaborn as sns
import numpy as np
import pandas as pd
from copy import deepcopy

def calculateTrust(agent, partner, witness):
    """Method to calculate the trust value of trade partner (target agent) based on strategy"""
    trust_in_partner = agent.trust_per_trader[partner.unique_id]
    trust_in_witness = agent.trust_per_trader[witness.unique_id]
    witness_trust_in_partner = witness.trust_per_trader[partner.unique_id]

    tactic = agent.strategies.trust_tactic

    if  tactic == 'standard':
        trust = trust_in_partner + witness_trust_in_partner  #standaard
    elif tactic == 'not_trust_witness':
        trust = trust_in_partner
    elif tactic == 'partially_trust_witness':
        trust = ((trust_in_witness + witness_trust_in_partner) / 2) + trust_in_partner
    else:
        raise NotImplementedError
    return trust / 2

def calculateWitness(all_agents, agent_a, agent_b, used_witness = None):
    """Method to pick the used witness for agent_a, based on strategy
       @TODO revisit method later"""

    if agent_a.witness_tactic == 'standard':
        agent = random.choice([agent for agent in all_agents if (agent != agent_a and agent != agent_b and agent != used_witness)])
    return agent

# Alternative way to find witnesses
def findWitness(agent, agent_list):
    if agent.witness_tactic == "standard":
        witness = random.choice(agent_list)
    if agent.witness_tactic == "high_trust":
        raise NotImplementedError
    agent_list.remove(witness)
    return witness

def calculateOffer(agent, trust_in_target_agent):
    if agent.offer_tactic == "standard":
        return np.clip(trust_in_target_agent * agent.honesty * 100, 0, 100)
    else:
        raise NotImplementedError

# Ways to update trust:
#   standard: only update your trust in the trading partner
#   include_witness: include the witness to some extent (same as partner or less? more?)
def updateTrustValues(agent, gain_or_loss, partner, witness):
    if agent.trust_update_tactic == "standard":
        trust_update_value = gain_or_loss/5
        current_trust = agent.trust_per_trader[partner.unique_id]
    else:
        raise NotImplementedError
    agent.trust_per_trader[partner.unique_id] = max(0, min(100, current_trust+ trust_update_value))
    return


class TraderAgent(mesa.Agent):
    def __init__(self, unique_id, model, money, honesty, trust_per_trader, interactions, strategies=None):
        # Pass the parameters to the parent class.
        super().__init__(unique_id, model)
        self.id = id
        self.model = model
        self.money = money # int start 100
        self.honesty = honesty # float 0 - 1
        self.trust_per_trader = trust_per_trader # array (or list?) float for each trader start 0.5
        self.interactions = interactions
        self.trading = False
        self.witnessing = False
        self.trade_partner = None

        """tactics, should be changed later maybe"""
        self.strategies = strategies    #combined strategies
        self.strat_color = strategies.strat_color   #for visuals

        self.witness_tactic = "standard"
        self.trust_update_tactic = "standard"
        self.offer_tactic = "standard"
            
    def setTradePartner(self, partnerObj):
        self.trade_partner = partnerObj
        return

    def step(self):
        if self.trade_partner is None:
            return
        
        available_agents = self.model.schedule.agents.copy()            #check dit als iets heel raar is
        
        available_agents.remove(self)
        available_agents.remove(self.trade_partner)

        witness_agent_a = findWitness(agent=self, agent_list=available_agents)
        witness_agent_b = findWitness(agent=self.trade_partner, agent_list=available_agents)
 
        #TRADE PART
        #Trust_in_agent_b = trust_in_witness_a * trust_of_witness_a
        
        # Your trust in trade partner + your witness' trust in trade partner
        trust_in_agent_b = calculateTrust(self, self.trade_partner, witness_agent_a)
        trust_in_agent_a = calculateTrust(self.trade_partner, self, witness_agent_b)

        # Calculate trade offers
        trade_offer_agent_a = calculateOffer(self, trust_in_agent_b)
        trade_offer_agent_b = calculateOffer(self.trade_partner, trust_in_agent_a)

        # Calculate new funds
        my_money_change = (trade_offer_agent_b * 1.10) - trade_offer_agent_a
        self.money = self.money + my_money_change
        partner_money_change = (trade_offer_agent_a * 1.10) - trade_offer_agent_b
        self.trade_partner.money = self.trade_partner.money + partner_money_change

        # Function that sets trust to new value, allows different tactics
        # This sets the new trust for Agent A
        # Alternative function by Thijs
        updateTrustValues(self, my_money_change, self.trade_partner, witness_agent_a)       #update agent A
        updateTrustValues(self.trade_partner, partner_money_change, self, witness_agent_b)  #update agent B

        # # Calculate the new trusts
        # self.trust_per_trader[self.trade_partner.unique_id] = np.clip(self.trust_per_trader[self.trade_partner.unique_id] * (self.interactions[self.trade_partner.unique_id] / (self.interactions[self.trade_partner.unique_id] + 1))
        #                                                 + (trade_offer_agent_b * 1.10) * (1 / (self.interactions[self.trade_partner.unique_id] + 1)), 0, 100) / 100.0
        #
        # self.trade_partner.trust_per_trader[self.unique_id] = np.clip(self.trade_partner.trust_per_trader[self.unique_id] * (self.interactions[self.unique_id] / (self.interactions[self.unique_id] + 1))
        #                                                 + (trade_offer_agent_a * 1.10) * (1 / (self.interactions[self.unique_id] + 1)), 0, 100) / 100.0

        # print("New trust of agent ", int(self.unique_id), " in agent ", int(agent_b.unique_id), ":\t", self.trust_per_trader[agent_b.unique_id])
        # print("New trust of agent ", int(agent_b.unique_id), " in agent ", int(self.unique_id), ":\t", agent_b.trust_per_trader[self.unique_id], "\n")