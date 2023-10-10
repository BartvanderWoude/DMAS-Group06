from typing import Dict
import pandas
from functools import partial
from mesa import Model
from mesa.time import RandomActivation
from mesa.space import SingleGrid
import numpy as np
from mesa.datacollection import DataCollector
from collections import defaultdict
from scipy.special import softmax
import math

# from strategies import DefaultStrat, NoTrustStrat, LowTrustStrat
from trader import TraderAgent
import custom_strategies as CS


class AgentModel(Model):
    """Our main model for the Multi-agent systems model. Using a Mesa implementation"""

    def __init__(self, N=50,
                 neighbourhood=False,
                 movement_type="random_spot",
                 width=10, height=10,
                 strategies: Dict[str, int] = None,
                 strategyDistribution={},
                 customStrategies=None,
                 n_steps=1):

        super(AgentModel, self).__init__()
        self.num_agents = N
        self.initial_money = 100
        self.agent_distribution = strategies  # create distribution of agents with certain strategies

        self.grid = SingleGrid(width, height,
                               True)  # changed this from multigrid to singlegrid, as 2 agents could spawn at similar locations
        self.schedule = RandomActivation(self)
        self.n_steps = n_steps
        self.agent_list = []

        if not strategyDistribution:
            self.manually_set_distribution()
        else:
            self.strategy_distribution = strategyDistribution
            self.custom_strategies = customStrategies

        # Adjust this parameter when you want to have limited vision for each agent
        self.neighbourhood = neighbourhood
        self.movement_type = movement_type
        self.agents_finished_trading = []

        """for visualization"""
        self.iteration = 0
        self.agent_id_dict = defaultdict(TraderAgent)
        self.agent_dict = defaultdict(list)  # for "sorting" agents by strategy.name

        """datasets for plotting later"""
        self.df: pandas.DataFrame = None
        self.agent_df: pandas.DataFrame = None

        """call setup methods"""
        self.setup_agents()
        self.agentcollector = self.agent_data_collector()
        self.datacollector = self.data_collector()  # make sure to call after setup_agents()

    def get_agent_by_id(self, unique_id):
        """helper method to get agent instance by id"""
        try:
            return self.agent_id_dict[unique_id]
        except Exception as e:
            raise KeyError

    def manually_set_distribution(self):
        """Create agents according to self.strategy_distribution"""
        cs = CS.CustomStrategies()  # comment this in order to use the older (preset) strategies system

        # Number of agents divided by number of classes - to create even distributions per stratety         
        ####### TODO CHANGE THIS TO IMPLEMENT CUSTOM STRATEGY-DISTRIBUTIONS

        # This creates an even distribution of strategies over all the agents
        strat_distributions = []
        for i, mechanic in enumerate(cs.mechanics):
            # Strategies can be "standard", "lowball", "dont_trust_witness"
            strats_of_this_mechanic = cs.mechanics[mechanic].strategies
            # Calculate the number of agents that will get each strategy (THIS DETERMINES THE EVEN DISTRIBUTION)
            n_agents_per_mechanic_strategy = self.num_agents / len(strats_of_this_mechanic)  #
            # This creates the distribution: 50 agents, 3 strategies --> [17, 16, 16]
            strat_distribution = [
                math.ceil(n_agents_per_mechanic_strategy) if strat == 0 else math.floor(n_agents_per_mechanic_strategy)
                for strat in range(len(strats_of_this_mechanic))]
            strat_distributions.append(strat_distribution)

        ####### TODO-END

        # This converts the distributions into a dictionary. The dictionary contains the mechanics (trade offer, update trust, etc) and for each of those, how many agents will get whatever mechanic
        distributions_per_mechanic = {}
        for i, mechanic in enumerate(cs.mechanics):
            distributions_per_mechanic[mechanic] = strat_distributions[i]

        self.strategy_distribution = distributions_per_mechanic  # DICT with << strategy topic""": distribution per strategy of that topic [] >>

        self.custom_strategies = cs  # OBJ     # Contains all strategies and their (unused) methods

    def setup_agents(self):
        print("SETUP AGENTS")
        """method to setup agents with their respected strategies (evenly distributed)"""
        if self.strategy_distribution and self.custom_strategies:
            for agent_n in range(self.num_agents):
                strat = self.pickAgentStrats()
                strat_name = '_'.join(strat.values())
                a = TraderAgent(unique_id=agent_n,
                                model=self,
                                honesty=np.clip(np.random.normal(0.5, 0.2), 0.1, 0.9),
                                money=self.initial_money,
                                trust_per_trader={i: 0.5 for i in range(self.num_agents)},
                                interactions={i: 0 for i in range(self.num_agents)},
                                customizedStrategies=strat,
                                strat_name=strat_name)

                self.agent_id_dict[agent_n] = a
                self.agent_dict[strat_name].append(a)  # sort agent by strategy for plotting later
                self.schedule.add(a)
                self.agent_list.append(a)
                self.grid.move_to_empty(a)
        return

    # Works, output is a DICT of mechanics and their strategies --> {'witness': 'standard', ...}
    def pickAgentStrats(self):
        stats = {}
        for mechanic in self.custom_strategies.mechanics:
            distribution = np.asarray(self.strategy_distribution[mechanic])
            probability = softmax(distribution)

            # Picks a strategy by psuedo-randomly choosing an index, with the softmax (probablility) of the given distribution
            index_pick = np.random.choice(range(len(distribution)), p=probability)
            stats[mechanic] = self.custom_strategies.mechanics[mechanic].strategies[index_pick]

            # Lowers distribution counter of the selected strategy
            self.strategy_distribution[mechanic][index_pick] -= 1
        return stats

    def assignTradePartners(self):
        """method to pair agents"""
        np.random.shuffle(self.agent_list)  # shuffle the agents
        half = int(self.num_agents / 2)
        for pair_idx in range(half):
            a1 = self.agent_list[pair_idx]
            a2 = self.agent_list[pair_idx + half]

            a1.setTradePartner(a2)
            a2.setTradePartner(a1)
        return

    def data_collector(self):
        """method to collect data (per step) to mesa interface, currently showing the sum, and summed money based on strategy"""

        def strat_avg_money(key):
            return round(sum(agent.money for agent in self.agent_dict[key]) / len(self.agent_dict[key]), 2)

        strategy_dict = {
            "total_money": lambda m: round(sum(agent.money for agent in self.agent_list), 2),
            "avg_money": lambda m: round(sum(agent.money for agent in self.agent_list) / len(self.agent_list), 2)
        }

        for strat_key in self.agent_dict.keys():  # equal to strat names
            strategy_dict[strat_key] = partial(strat_avg_money,
                                               strat_key)  # partial is used to not mess up lambda expressions

        return DataCollector(strategy_dict)

    def agent_data_collector(self):
        """method to collect data from individual agents"""
        agent_dict = {}

        def honesty_money(agent):
            return [agent.proportional_funds, agent.honesty]

        for agent in self.agent_list:
            agent_dict[f"{agent.unique_id}_{agent.strat_name}"] = partial(honesty_money, agent)

        return DataCollector(agent_dict)

    def collect_data(self):
        """method to collect data into pandas dataframe"""
        self.df = self.datacollector.get_model_vars_dataframe()  # for agent in self.agent_list:
        self.agent_df = self.agentcollector.get_model_vars_dataframe()

        funds_in_world = self.df['total_money'].iloc[self.df['total_money'].idxmax()]
        average_funds = funds_in_world / self.num_agents

        for agent in self.agent_list:
            agent.proportional_funds = agent.money / average_funds

        if self.iteration % 20 == 0:
            print("saved df")
            self.df.to_csv("money_over_time.csv")
            self.agent_df.to_csv("agent.csv")

    # Iteration
    def step(self):
        """Method that will call every step click, each call is a new iterations"""
        for _ in range(self.n_steps):  # to speed up datacollection (this should be possible with the FPS slider but doesnt work)
            self.agents_finished_trading = []
            self.assignTradePartners()  # Set up duo's
            self.schedule.step()  # perform agent actions

            self.datacollector.collect(self)
            self.agentcollector.collect(self)
            self.collect_data()

            self.iteration += 1
