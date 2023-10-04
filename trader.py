import random
import mesa
import seaborn as sns
import numpy as np
import pandas as pd
from copy import deepcopy
import math
from movement_techniques import *
import custom_strategies as cs


def get_agents_within_radius(agent, agent_list):
    agents_within = []

    for other_agent in agent_list:
            distance = math.sqrt((agent.pos[0] - other_agent.pos[0])**2 + (agent.pos[1] - other_agent.pos[1])**2)
            # print("id\t", self.unique_id, "dist\t", distance, "radius\t", self.radius)
            if distance <= agent.radius:
                agents_within.append(other_agent)

    return agents_within

# Alternative way to find witnesses
def findWitness(agent, agent_list):
    if agent.witness_tactic == "standard":
        witness = random.choice(agent_list)
    if agent.witness_tactic == "high_trust":
        raise NotImplementedError
    agent_list.remove(witness)
    return witness


class TraderAgent(mesa.Agent):
    def __init__(self, unique_id, model, money, honesty, trust_per_trader, interactions, strategies=None, customizedStrategies = {}):
        # Pass the parameters to the parent class.
        super().__init__(unique_id, model)
        self.model = model
        self.money = money # int start 100
        self.honesty = honesty # float 0 - 1
        self.trust_per_trader = trust_per_trader # array (or list?) float for each trader start 0.5
        self.interactions = interactions
        self.move = True
        self.radius = 3
        self.trade_partner = None

        self.custom_strategies = {} # TODO: remove double var allocation once done implementing
        self.cs = cs.CustomStrategies()

        """tactics, should be changed later maybe"""
        self.strategies = strategies    #combined strategies
        self.strat_color = strategies.strat_color   #for visuals

        if customizedStrategies:
            print("A")
            self.custom_strategies = customizedStrategies

            # Outdated technique below                                      # Can be deleted when done with updated strategies
            self.witness_tactic = customizedStrategies["witness"]           # Can be deleted when done with updated strategies
            self.trust_update_tactic = customizedStrategies["trust_update"] # Can be deleted when done with updated strategies
            self.offer_tactic = customizedStrategies["offer"]               # Can be deleted when done with updated strategies
        else:
            print("B")
            self.witness_tactic = "standard"
            self.trust_update_tactic = "standard"
            self.offer_tactic = "standard"
            
    def setTradePartner(self, partnerObj):
        self.trade_partner = partnerObj
        return

    def move_to_random_spot(self):
        while True:
            new_x = random.randint(0, self.model.grid.width - 1)
            new_y = random.randint(0, self.model.grid.height - 1)

            # Check if the cell is occupied by any agent
            is_occupied = any(agent.pos == (new_x, new_y) for agent in self.model.schedule.agents)

            if not is_occupied:
                self.model.grid.move_agent(self, (new_x, new_y))
                break

    def random_walk(self):
        dx, dy = random.choice([(1, 0), (-1, 0), (0, 1), (0, -1)])
        new_x = max(0, min(self.model.grid.width - 1, self.pos[0] + dx))
        new_y = max(0, min(self.model.grid.height - 1, self.pos[0] + dy))

        # Check if the cell is occupied by any agent
        is_occupied = any(agent.pos == (new_x, new_y) for agent in self.model.schedule.agents)

        if not is_occupied:
            self.model.grid.move_agent(self, (new_x, new_y))

    
    def step(self):
        if self.trade_partner is None:
            return
        
        available_agents = self.model.schedule.agents.copy()            #check dit als iets heel raar is
        
        available_agents.remove(self)
        available_agents.remove(self.trade_partner)

        #If neighbourhood is True, the agent has a specific radius in which it can choose its witnesses
        if self.model.neighbourhood:
            agents_within_a = get_agents_within_radius(agent=self, agent_list=available_agents)
            agents_within_b = get_agents_within_radius(agent=self.trade_partner, agent_list=available_agents)
            witness_agent_a = findWitness(agent=self, agent_list=agents_within_a)
            witness_agent_b = findWitness(agent=self.trade_partner, agent_list=agents_within_b)

        else:
            witness_agent_a = findWitness(agent=self, agent_list=available_agents)
            witness_agent_b = findWitness(agent=self.trade_partner, agent_list=available_agents)

        #TRADE PART
        #Trust_in_agent_b = trust_in_witness_a * trust_of_witness_a
        
        # Your trust in trade partner + your witness' trust in trade partner
        trust_in_agent_b = self.cs['trust_update'].calculateTrust(self, self.trade_partner, witness_agent_a)
        trust_in_agent_a = self.cs['trust_update'].calculateTrust(self.trade_partner, self, witness_agent_b)

        # Calculate trade offers
        trade_offer_agent_a = self.cs['offer'].calculateOffer(self, trust_in_agent_b)
        trade_offer_agent_b = self.cs['offer'].calculateOffer(self.trade_partner, trust_in_agent_a)

        # Calculate new funds
        my_money_change = (trade_offer_agent_b * 1.10) - trade_offer_agent_a
        self.money = self.money + my_money_change
        partner_money_change = (trade_offer_agent_a * 1.10) - trade_offer_agent_b
        self.trade_partner.money = self.trade_partner.money + partner_money_change

        # Function that sets trust to new value, allows different tactics
        # This sets the new trust for Agent A
        # Alternative function by Thijs
        self.cs['trust_update'].updateTrustValues(self, my_money_change, self.trade_partner, witness_agent_a)       #update agent A
        self.cs['trust_update'].updateTrustValues(self.trade_partner, partner_money_change, self, witness_agent_b)  #update agent B

        # # Calculate the new trusts
        # self.trust_per_trader[self.trade_partner.unique_id] = np.clip(self.trust_per_trader[self.trade_partner.unique_id] * (self.interactions[self.trade_partner.unique_id] / (self.interactions[self.trade_partner.unique_id] + 1))
        #                                                 + (trade_offer_agent_b * 1.10) * (1 / (self.interactions[self.trade_partner.unique_id] + 1)), 0, 100) / 100.0
        #
        # self.trade_partner.trust_per_trader[self.unique_id] = np.clip(self.trade_partner.trust_per_trader[self.unique_id] * (self.interactions[self.unique_id] / (self.interactions[self.unique_id] + 1))
        #                                                 + (trade_offer_agent_a * 1.10) * (1 / (self.interactions[self.unique_id] + 1)), 0, 100) / 100.0

        # print("New trust of agent ", int(self.unique_id), " in agent ", int(agent_b.unique_id), ":\t", self.trust_per_trader[agent_b.unique_id])
        # print("New trust of agent ", int(agent_b.unique_id), " in agent ", int(self.unique_id), ":\t", agent_b.trust_per_trader[self.unique_id], "\n")

        #Moving an agent makes only makes sense if the agent has a neighbourhood.
        if self.model.neighbourhood:
            movement_techniques(self, self.model, self.radius)