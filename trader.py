import random
import mesa
import seaborn as sns
import numpy as np
import pandas as pd
from copy import deepcopy
import math
from movement_techniques import *
import custom_strategies as cusStrat


def get_agents_within_radius(agent, agent_list):
    agents_within = []

    for other_agent in agent_list:
        distance = math.sqrt((agent.pos[0] - other_agent.pos[0]) ** 2 + (agent.pos[1] - other_agent.pos[1]) ** 2)
        # print("id\t", self.unique_id, "dist\t", distance, "radius\t", self.radius)
        if distance <= agent.radius:
            agents_within.append(other_agent)

    return agents_within


# This has no mechanic yet
def findWitness(agent, agent_list, id_trader):
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
    agent_list.remove(witness)  # Removes it from the original list, so no need to return the list
    return witness


def calculateOffer(agent, trust_in_target_agent):
    tactic = agent.custom_strategies['offer']
    if tactic == "standard":
        return np.clip(((trust_in_target_agent + agent.honesty) / 2) * 100, 0, 100)
    elif tactic == "extra1":
        return np.clip(((trust_in_target_agent + agent.honesty) / 2) * 100, 0, 100)     #TODO no difference, needs change if we want this functionality
    else:
        raise NotImplementedError


# Ways to update trust:
#   standard: only update your trust in the trading partner
#   include_witness: include the witness to some extent (same as partner or less? more?)
def updateTrustValues(agent, gain_or_loss, partner, witness):
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


def calculateTrust(agent, partner, witness):
    """Method to calculate the trust value of trade partner (target agent) based on strategy"""
    trust_in_partner = agent.trust_per_trader[partner.unique_id]
    trust_in_witness = agent.trust_per_trader[witness.unique_id]
    witness_trust_in_partner = witness.trust_per_trader[partner.unique_id]

    tactic = agent.custom_strategies['witness']
    # agent.strategies.trust_tactic # TODO: this is not implemented yet

    if tactic == 'standard':
        trust = (trust_in_partner + witness_trust_in_partner) / 2  # standaard
    elif tactic == 'skeptic':
        trust = (((trust_in_witness + witness_trust_in_partner) / 2) + trust_in_partner) / 2
    elif tactic == 'naive':
        trust = witness_trust_in_partner
    else:
        raise NotImplementedError
    return trust


class TraderAgent(mesa.Agent):
    def __init__(self, unique_id, model, money, honesty, trust_per_trader, interactions, strategies=None,
                 customizedStrategies={}):
        # Pass the parameters to the parent class.
        super().__init__(unique_id, model)
        self.model = model
        self.money = money  # int start 100
        self.honesty = honesty  # float 0 - 1
        self.trust_per_trader = trust_per_trader  # array (or list?) float for each trader start 0.5
        self.interactions = interactions
        self.move = True
        self.radius = 3
        self.trade_partner = None

        self.proportional_funds = 1

        self.custom_strategies = customizedStrategies  # TODO: remove double var allocation once done implementing
        self.cs = cusStrat.CustomStrategies()

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

        available_agents = self.model.schedule.agents.copy()  # check dit als iets heel raar is

        available_agents.remove(self)
        available_agents.remove(self.trade_partner)

        # If neighbourhood is True, the agent has a specific radius in which it can choose its witnesses
        if self.model.neighbourhood:
            agents_within_a = get_agents_within_radius(agent=self, agent_list=available_agents)
            agents_within_b = get_agents_within_radius(agent=self.trade_partner, agent_list=available_agents)
            witness_agent_a = findWitness(agent=self, agent_list=agents_within_a, id_trader=self.trade_partner.unique_id)
            witness_agent_b = findWitness(agent=self.trade_partner, agent_list=agents_within_b, id_trader=self.unique_id)

        else:
            # witness_agent_a = self.cs.mechanics['witness'].findWitness(agent=self, agent_list=available_agents) # TODO: fix or switch to implementing all strategies in this file
            witness_agent_a = findWitness(agent=self, agent_list=available_agents, id_trader=self.trade_partner.unique_id)
            witness_agent_b = findWitness(agent=self.trade_partner, agent_list=available_agents, id_trader=self.unique_id)

        # TRADE PART
        # Trust_in_agent_b = trust_in_witness_a * trust_of_witness_a

        # Your trust in trade partner + your witness' trust in trade partner
        # trust_in_agent_b = self.cs.mechanics['trust_update'].calculateTrust(agent=self.trade_partner, parner=self, witness=witness_agent_a) # TODO: fix or switch to implementing all strategies in this file
        trust_in_agent_b = calculateTrust(self, self.trade_partner, witness_agent_a)
        trust_in_agent_a = calculateTrust(self.trade_partner, self, witness_agent_b)

        # Calculate trade offers
        # trade_offer_agent_a = self.cs.mechanics['offer'].calculateOffer(self, trust_in_agent_b) # TODO: fix or switch to implementing all strategies in this file
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

        # self.cs['trust_update'].updateTrustValues(self, my_money_change, self.trade_partner, witness_agent_a) # TODO: fix or switch to implementing all strategies in this file
        updateTrustValues(self, my_money_change, self.trade_partner, witness_agent_a)  # update agent A
        updateTrustValues(self.trade_partner, partner_money_change, self, witness_agent_b)  # update agent B

        # # Calculate the new trusts
        # self.trust_per_trader[self.trade_partner.unique_id] = np.clip(self.trust_per_trader[self.trade_partner.unique_id] * (self.interactions[self.trade_partner.unique_id] / (self.interactions[self.trade_partner.unique_id] + 1))
        #                                                 + (trade_offer_agent_b * 1.10) * (1 / (self.interactions[self.trade_partner.unique_id] + 1)), 0, 100) / 100.0
        #
        # self.trade_partner.trust_per_trader[self.unique_id] = np.clip(self.trade_partner.trust_per_trader[self.unique_id] * (self.interactions[self.unique_id] / (self.interactions[self.unique_id] + 1))
        #                                                 + (trade_offer_agent_a * 1.10) * (1 / (self.interactions[self.unique_id] + 1)), 0, 100) / 100.0

        # print("New trust of agent ", int(self.unique_id), " in agent ", int(agent_b.unique_id), ":\t", self.trust_per_trader[agent_b.unique_id])
        # print("New trust of agent ", int(agent_b.unique_id), " in agent ", int(self.unique_id), ":\t", agent_b.trust_per_trader[self.unique_id], "\n")

        # Moving an agent makes only makes sense if the agent has a neighbourhood.
        if self.model.neighbourhood:
            movement_techniques(self, self.model, self.radius)
