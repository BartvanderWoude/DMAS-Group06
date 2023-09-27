import random
import mesa
import seaborn as sns
import numpy as np
import pandas as pd


class TraderAgent(mesa.Agent):
    def __init__(self, unique_id, model, money, honesty, trust_per_trader, interactions):
        # Pass the parameters to the parent class.
        super().__init__(unique_id, model)
        self.id = id
        self.model = model
        self.money = money
        self.honesty = honesty
        self.trust_per_trader = trust_per_trader       
        self.interactions = interactions 
        self.trading = False
        self.witnessing = False

    def step(self):
        print("\n\n Interaction between two new agents:\n")
        #WITNESS PART
        witness_agent_a = random.choice([agent for agent in self.model.schedule.agents if agent != self]) 
        agent_b = max([agent for agent in self.model.schedule.agents if agent != self], key=lambda agent: self.trust_per_trader[agent.unique_id])    
        witness_agent_b = random.choice([agent for agent in self.model.schedule.agents if (agent != self and agent != agent_b)]) 

        #TRADE PART
        #Trust_in_agent_b = trust_in_witness_a * trust_of_witness_a
        trust_in_agent_b = (self.trust_per_trader[witness_agent_a.unique_id] + witness_agent_a.trust_per_trader[agent_b.unique_id]) / 2.0

        #Trust_in_agent_a = trust_in_witness_b * trist_of_witness_b
        trust_in_agent_a = (agent_b.trust_per_trader[witness_agent_b.unique_id] + witness_agent_b.trust_per_trader[self.unique_id]) / 2.0

        print("trust of agent ", int(self.unique_id),  " in agent ", int(agent_b.unique_id), ":\t", trust_in_agent_b)
        print("trust of agent ", int(agent_b.unique_id), " in agent ", int(self.unique_id), ":\t", trust_in_agent_a, "\n")

        # Calculate trade offers
        trade_offer_agent_a = trust_in_agent_b * self.honesty * self.money
        trade_offer_agent_b = trust_in_agent_a * agent_b.honesty * agent_b.money

        print("Trade offer agent ", int(self.unique_id), ":\t", trade_offer_agent_a)
        print("Trade offer agent ", int(agent_b.unique_id), ":\t", trade_offer_agent_b, "\n")
        
        # Calculate new funds
        self.money = self.money - trade_offer_agent_a + (trade_offer_agent_b * 1.10)
        agent_b.money = agent_b.money - trade_offer_agent_b + (trade_offer_agent_a * 1.10)

        print("Money of agent ", int(self.unique_id), ":\t", self.money)
        print("Money of agent ", int(agent_b.unique_id), "", agent_b.money, "\n")

        # Calculate the new trusts
        self.trust_per_trader[agent_b.unique_id] = np.clip(self.trust_per_trader[agent_b.unique_id] * (self.interactions[agent_b.unique_id] / (self.interactions[agent_b.unique_id] + 1)) 
                                                           + (trade_offer_agent_b * 1.10) * (1 / (self.interactions[agent_b.unique_id] + 1)), 0, 100) / 100.0

        agent_b.trust_per_trader[self.unique_id] = np.clip(agent_b.trust_per_trader[self.unique_id] * (self.interactions[self.unique_id] / (self.interactions[self.unique_id] + 1)) 
                                                           + (trade_offer_agent_a * 1.10) * (1 / (self.interactions[self.unique_id] + 1)), 0, 100) / 100.0

        print("New trust of agent ", int(self.unique_id), " in agent ", int(agent_b.unique_id), ":\t", self.trust_per_trader[agent_b.unique_id])
        print("New trust of agent ", int(agent_b.unique_id), " in agent ", int(self.unique_id), ":\t", agent_b.trust_per_trader[self.unique_id], "\n")

