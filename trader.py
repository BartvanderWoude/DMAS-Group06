import random
import mesa
import seaborn as sns
import numpy as np
import pandas as pd
from strategies import Strategy
from copy import deepcopy

def calculateTrust(agent, partner, witness):
    """Method to calculate the trust value of trade partner (target agent) based on strategy"""
    trust_in_partner = agent.trust_per_trader[partner.unique_id]
    trust_in_witness = agent.trust_per_trader[witness.unique_id]
    witness_trust_in_partner = witness.trust_per_trader[partner.unique_id]

    if agent.trust_tactic == 'standard':
        trust = trust_in_partner + witness_trust_in_partner  #standaard
    if agent.trust_tactic == 'trust_witness':
        trust = ((trust_in_witness + witness_trust_in_partner) / 2) + trust_in_partner
    if agent.trust_tactic == '-':
        pass
    return trust / 2

def calculateWitness(all_agents, agent_a, agent_b, used_witness = None):
    """Method to pick the used witness for agent_a, based on strategy
       @TODO revisit method later"""

    if agent_a.witness_tactic == 'standard':
        agent = random.choice([agent for agent in all_agents if (agent != agent_a and agent != agent_b and agent != used_witness)])
    return agent

def findWitness(agent, agent_list):
    if agent.witness_tactic == "standard":
        witness = random.choice(agent_list)
    if agent.witness_tactic == "high_trust":
        raise NotImplementedError
    agent_list.remove(witness)
    return witness

def calculateOffer(agent, trust_target_agent):
    raise NotImplementedError

def calculateNewTrustValues(target_agent, outcome_offer, witness):
    raise NotImplementedError
    

class TraderAgent(mesa.Agent):
    def __init__(self, unique_id, model, money, honesty, trust_per_trader, interactions):
        # Pass the parameters to the parent class.
        super().__init__(unique_id, model)
        self.id = id
        self.model = model
        self.money = money # int
        self.honesty = honesty # int
        self.trust_per_trader = trust_per_trader # array (or list?) 
        self.interactions = interactions 
        self.trading = False
        self.witnessing = False
        self.trade_partner = None
        self.trust_tactic = "standard"
        self.witness_tactic = "standard"
            
    
    def setTradePartner(self, partnerObj):
        self.trade_partner = partnerObj
        return

    def step(self):
        if self.trade_partner is None:
            # pass
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
        trade_offer_agent_a = trust_in_agent_b * self.honesty * self.money
        trade_offer_agent_b = trust_in_agent_a * self.trade_partner.honesty * self.trade_partner.money

        # print("Trade offer agent ", int(self.unique_id), ":\t", trade_offer_agent_a)
        # print("Trade offer agent ", int(agent_b.unique_id), ":\t", trade_offer_agent_b, "\n")
        
        # Calculate new funds
        my_money_change =  (trade_offer_agent_b * 1.10) - trade_offer_agent_a
        self.money = self.money + my_money_change
        partner_money_change = (trade_offer_agent_a * 1.10) - trade_offer_agent_b
        self.trade_partner.money = self.trade_partner.money + partner_money_change

        # print("Money of agent ", int(self.unique_id), ":\t", self.money)
        # print("Money of agent ", int(agent_b.unique_id), "", agent_b.money, "\n")

        # Calculate the new trusts
        self.trust_per_trader[self.trade_partner.unique_id] = np.clip(self.trust_per_trader[self.trade_partner.unique_id] * (self.interactions[self.trade_partner.unique_id] / (self.interactions[self.trade_partner.unique_id] + 1)) 
                                                        + (trade_offer_agent_b * 1.10) * (1 / (self.interactions[self.trade_partner.unique_id] + 1)), 0, 100) / 100.0

        self.trade_partner.trust_per_trader[self.unique_id] = np.clip(self.trade_partner.trust_per_trader[self.unique_id] * (self.interactions[self.unique_id] / (self.interactions[self.unique_id] + 1)) 
                                                        + (trade_offer_agent_a * 1.10) * (1 / (self.interactions[self.unique_id] + 1)), 0, 100) / 100.0

        # print("New trust of agent ", int(self.unique_id), " in agent ", int(agent_b.unique_id), ":\t", self.trust_per_trader[agent_b.unique_id])
        # print("New trust of agent ", int(agent_b.unique_id), " in agent ", int(self.unique_id), ":\t", agent_b.trust_per_trader[self.unique_id], "\n")

