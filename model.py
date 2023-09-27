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

        # Create agents
        for i in range(self.num_agents):
            a = TraderAgent(i, self, 100, np.random.uniform(0,1), {i: np.random.uniform(0.5, 1.0) for i in range(self.num_agents)}, {i: 0 for i in range(self.num_agents)})
            # Add the agent to the scheduler
            self.schedule.add(a)

            x = self.random.randrange(self.grid.width)
            y = self.random.randrange(self.grid.height)
            self.grid.place_agent(a, (x,y))

    def step(self):
        self.schedule.step()

# model = AgentModel(10, 10, 10)
# model.step()