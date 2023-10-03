from typing import Dict

from mesa import Model
from trader import TraderAgent
from mesa.time import RandomActivation
from mesa.space import MultiGrid, SingleGrid
import numpy as np
from strategies import DefaultStrat, NoTrustStrat, LowTrustStrat
from mesa.datacollection import DataCollector
from collections import defaultdict


class AgentModel(Model):
    """A model with some number of agents."""

    def __init__(self, N, width, height, strategies: Dict[str, int] = None):
        super(AgentModel, self).__init__()
        self.num_agents = N
        self.agent_distribution = strategies  #create distribution of agents with certain strategies

        self.grid = SingleGrid(width, height,
                               True)  # changed this from multigrid to singlegrid, as 2 agents could spawn at similar locations
        self.schedule = RandomActivation(self)
        self.agent_list = []

        self.strategies = [DefaultStrat, NoTrustStrat, LowTrustStrat]
        self.strategy_dict = {"default": DefaultStrat, "lowtrust": LowTrustStrat, "notrust": NoTrustStrat}
        """for visualization"""
        self.strat_names = ["default", "lowtrust", "notrust", "funds_in_world"]  # hardcoded @TODO should be changed
        self.agent_dict = defaultdict(list)  # for "sorting" agents by strategy.name
        self.datacollector = self.data_collector()

        # Create agents

        if self.agent_distribution:
            self.setup_agents()
            return

        for i in range(self.num_agents):  # self.num_
            idx = np.random.randint(0, len(self.strategies))
            strat = self.strategies[idx]()  # pick random strategy

            a = TraderAgent(unique_id=i,
                            model=self,
                            money=100,
                            honesty=np.random.uniform(0, 1),
                            trust_per_trader={i: 0.5 for i in range(self.num_agents)},
                            interactions={i: 0 for i in range(self.num_agents)},
                            strategies=strat)

            self.agent_dict[strat.name].append(a)  # sort agent by strategy for plotting later
            # Add the agent to the scheduler
            self.schedule.add(a)

            self.agent_list.append(a)
            self.grid.move_to_empty(a)

    def setup_agents(self):
        """method to setup agents based on pre-made distribution: see experimental_setup.py"""
        agent_idx = 0
        for key, value in self.agent_distribution.items():
            for idx in range(value):
                strat = self.strategy_dict[key]()  # pick strategy and create instance

                a = TraderAgent(unique_id=agent_idx,
                                model=self,
                                money=100,
                                honesty=np.random.uniform(0, 1),
                                trust_per_trader={i: 0.5 for i in range(self.num_agents)},
                                interactions={i: 0 for i in range(self.num_agents)},
                                strategies=strat)

                self.agent_dict[strat.name].append(a)  # sort agent by strategy for plotting later
                self.schedule.add(a)
                self.agent_list.append(a)
                self.grid.move_to_empty(a)
                agent_idx += 1


    def assignTradePartners(self):
        np.random.shuffle(self.agent_list)  # shuffle the agents
        half = int(self.num_agents / 2)
        for pair_idx in range(half):
            a1 = self.agent_list[pair_idx]
            a2 = self.agent_list[pair_idx + half]

            a1.setTradePartner(a2)
            a2.setTradePartner(None)
        return

    def data_collector(self):
        """method to pass data (per step) to mesa interface, currently showing the sum, and summed money based on strategy"""
        return DataCollector(
            {"total_money": lambda m: sum([agent.money for agent in self.agent_list]),
             "default": lambda m: sum([agent.money for agent in self.agent_dict["default"]]),
             "lowtrust": lambda m: sum([agent.money for agent in self.agent_dict["lowtrust"]]),
             "notrust": lambda m: sum([agent.money for agent in self.agent_dict["notrust"]])}
        )

    def collect_data(self):
        """method to collect data to visualize later"""
        data_dictionary = defaultdict(int, {"funds_in_world": 0})
        for key in self.agent_dict.keys():
            for agent in self.agent_dict[key]:
                data_dictionary["funds_in_world"] += agent.money
                data_dictionary[key] += agent.money

        self.datacollector.add_table_row(table_name="growth_over_time", row=data_dictionary, ignore_missing=True)

    # Iteration
    def step(self):
        self.assignTradePartners()  # Set up duo's
        self.schedule.step()  # perform agent actions
        self.datacollector.collect(self)
