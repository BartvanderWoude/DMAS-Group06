from mesa import Model
from trader import TraderAgent
from mesa.time import RandomActivation
from mesa.space import MultiGrid
import numpy as np

class AgentModel(Model):
    """A model with some number of agents."""

    def __init__(self, N, width, height):
        self.num_agents = N
        self.grid = MultiGrid(width, height, True)
        self.schedule = RandomActivation(self)
        
        self.agent_list = []

        # Create agents
        for i in range(self.num_agents):    #self.num_
            a = TraderAgent(i, self, 100, np.random.uniform(0,1), {i: np.random.uniform(0.5, 1.0) for i in range(self.num_agents)}, {i: 0 for i in range(self.num_agents)})
            # Add the agent to the scheduler
            self.schedule.add(a)

            self.agent_list.append(a)

            x = self.random.randrange(self.grid.width)
            y = self.random.randrange(self.grid.height)
            self.grid.place_agent(a, (x,y))

    def assignTradePartners(self):
        np.random.shuffle(self.agent_list)  #shuffle the agents
        half = int(self.num_agents/2)
        for pair_idx in range(half):
            a1 = self.agent_list[pair_idx]
            a2 = self.agent_list[pair_idx+half]

            a1.setTradePartner(a2)
            a2.setTradePartner(None)
        return
    
    
    # Iteration
    def step(self):
        
        self.assignTradePartners() # Set up duo's
        
        self.schedule.step()    #perform agent actions


        
        

# model = AgentModel(10, 10, 10)
# model.step()