import mesa
import numpy as np
import math
import movement_techniques
import custom_strategies as cusStrat

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

        self.custom_strategies = customizedStrategies
        self.cs = cusStrat.CustomStrategies()
        self.strat_name = strat_name

    def setTradePartner(self, partnerObj):
        self.trade_partner = partnerObj

    def get_agents_within_radius(self, agent_list=None):
        agents_within = []

        for other_agent in agent_list:
            distance = math.sqrt((self.pos[0] - other_agent.pos[0]) ** 2 + (self.pos[1] - other_agent.pos[1]) ** 2)

            if distance <= self.radius:
                agents_within.append(other_agent)

        return agents_within
    
    def findWitness(self, agent_list, id_trader):
        return self.cs.mechanics['getwitness'].findWitness(self,
                                                        agent_list,
                                                        id_trader)
    
    def calculateTrust(self, witness):
        return self.cs.mechanics['witness'].calculateTrust(agent=self,
                                                        partner=self.trade_partner,
                                                        witness=witness)
    
    def calculateOffer(self, trust_in_target_agent):
        return self.cs.mechanics['offer'].calculateOffer(self,
                                                      trust_in_target_agent)
    
    def updateTrustValues(self, gain_or_loss, witness):
        self.cs.mechanics['trust_update'].updateTrustValues(self,
                                                         gain_or_loss,
                                                         self.trade_partner,
                                                         witness)

    def step(self):
        """Method which gets called for each agent at each timestep/iteration"""
        if self.unique_id in self.model.agents_finished_trading:
            return
        else:
            self.model.agents_finished_trading.append(self.unique_id)
            self.model.agents_finished_trading.append(self.trade_partner.unique_id)

        available_agents = self.model.schedule.agents.copy()

        available_agents.remove(self)
        available_agents.remove(self.trade_partner)

        """Witness selection, for now neighbourhood is not used"""
        if self.model.neighbourhood:
            agents_within_a = self.get_agents_within_radius(agent_list=available_agents)
            agents_within_b = self.trade_partner.get_agents_within_radius(agent_list=available_agents)
            witness_agent_a = self.findWitness(agent_list=agents_within_a,
                                               id_trader=self.trade_partner.unique_id)
            witness_agent_b = self.trade_partner.findWitness(agent_list=agents_within_b,
                                                             id_trader=self.unique_id)
        else:
            witness_agent_a = self.findWitness(agent_list=available_agents,
                                               id_trader=self.trade_partner.unique_id)
            witness_agent_b = self.trade_partner.findWitness(agent_list=available_agents,
                                                             id_trader=self.unique_id)

        "Calculate trust in target trader"
        trust_in_agent_b = self.calculateTrust(witness_agent_a)
        trust_in_agent_a = self.trade_partner.calculateTrust(witness_agent_b)

        """Calculate trade offers"""
        trade_offer_agent_a = self.calculateOffer(trust_in_agent_b)
        trade_offer_agent_b = self.trade_partner.calculateOffer(trust_in_agent_a)

        """Update fund"""
        my_money_change = (trade_offer_agent_b * 1.10) - trade_offer_agent_a
        self.money = self.money + my_money_change

        partner_money_change = (trade_offer_agent_a * 1.10) - trade_offer_agent_b
        self.trade_partner.money = self.trade_partner.money + partner_money_change

        """Update trust values"""
        self.updateTrustValues(my_money_change, witness_agent_a)  # update agent A
        self.trade_partner.updateTrustValues(partner_money_change, witness_agent_b)  # update agent B

        # Moving an agent makes only makes sense if the agent has a neighbourhood.
        if self.model.neighbourhood:
            movement_techniques.movement_techniques(self, self.model, self.radius, self.model.movement_type)
