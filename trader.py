import mesa
import numpy as np
import math
from movement_techniques import *
import custom_strategies as cusStrat


def findWitness(agent, agent_list, id_trader):
    return agent.cs.mechanics['getwitness'].findWitness(agent,
                                                        agent_list,
                                                        id_trader)


def calculateOffer(agent, trust_in_target_agent):
    return agent.cs.mechanics['offer'].calculateOffer(agent,
                                                      trust_in_target_agent)


def updateTrustValues(agent, gain_or_loss, partner, witness):
    agent.cs.mechanics['trust_update'].updateTrustValues(agent,
                                                         gain_or_loss,
                                                         partner,
                                                         witness)


def calculateTrust(agent, partner, witness):
    return agent.cs.mechanics['witness'].calculateTrust(agent=agent,
                                                        partner=partner,
                                                        witness=witness)


class TraderAgent(mesa.Agent):
    def __init__(self, unique_id, model, money, honesty, trust_per_trader, interactions, customizedStrategies,
                 strat_name, strategies=None):
        # Pass the parameters to the parent class.
        super().__init__(unique_id, model)
        self.model = model
        self.money = money  # int start 100
        self.honesty = honesty  # float 0 - 1
        self.trust_per_trader = trust_per_trader  # array (or list?) float for each trader start 0.5
        self.interactions = interactions
        self.radius = 3
        self.trade_partner = None

        self.proportional_funds = 1

        self.custom_strategies = customizedStrategies  # TODO: remove double var allocation once done implementing
        self.cs = cusStrat.CustomStrategies()
        self.strat_name = strat_name

    def setTradePartner(self, partnerObj):
        self.trade_partner = partnerObj

    def get_agents_within_radius(self, agent_list=None):
        agents_within = []

        for other_agent in agent_list:
            distance = math.sqrt((self.pos[0] - other_agent.pos[0]) ** 2 + (self.pos[1] - other_agent.pos[1]) ** 2)
            # print("id\t", self.unique_id, "dist\t", distance, "radius\t", self.radius)
            if distance <= self.radius:
                agents_within.append(other_agent)

        return agents_within

    def step(self):
        """Method which gets called for each agent at each timestep/iteration"""
        if self.trade_partner is None:
            return

        available_agents = self.model.schedule.agents.copy()

        available_agents.remove(self)
        available_agents.remove(self.trade_partner)

        """Witness selection, for now neighbourhood is not used"""
        if self.model.neighbourhood:
            agents_within_a = self.get_agents_within_radius(agent_list=available_agents)
            agents_within_b = self.trade_partner.get_agents_within_radius(agent_list=available_agents)
            witness_agent_a = findWitness(agent=self, agent_list=agents_within_a,
                                          id_trader=self.trade_partner.unique_id)
            witness_agent_b = findWitness(agent=self.trade_partner, agent_list=agents_within_b,
                                          id_trader=self.unique_id)
        else:
            # witness_agent_a = self.cs.mechanics['witness'].findWitness(agent=self, agent_list=available_agents) # TODO: fix or switch to implementing all strategies in this file
            witness_agent_a = findWitness(agent=self, agent_list=available_agents,
                                          id_trader=self.trade_partner.unique_id)
            witness_agent_b = findWitness(agent=self.trade_partner, agent_list=available_agents,
                                          id_trader=self.unique_id)

        "Calculate trust in target trader"
        trust_in_agent_b = calculateTrust(self, self.trade_partner, witness_agent_a)
        trust_in_agent_a = calculateTrust(self.trade_partner, self, witness_agent_b)

        """Calculate trade offers"""
        trade_offer_agent_a = calculateOffer(self, trust_in_agent_b)
        trade_offer_agent_b = calculateOffer(self.trade_partner, trust_in_agent_a)

        """Update fund"""
        my_money_change = (trade_offer_agent_b * 1.10) - trade_offer_agent_a
        self.money = self.money + my_money_change

        partner_money_change = (trade_offer_agent_a * 1.10) - trade_offer_agent_b
        self.trade_partner.money = self.trade_partner.money + partner_money_change

        """Update trust values"""
        updateTrustValues(self, my_money_change, self.trade_partner, witness_agent_a)  # update agent A
        updateTrustValues(self.trade_partner, partner_money_change, self, witness_agent_b)  # update agent B

        # Moving an agent makes only makes sense if the agent has a neighbourhood.
        if self.model.neighbourhood:
            movement_techniques(self, self.model, self.radius, self.model.movement_type)
