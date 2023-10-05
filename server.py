from mesa import DataCollector
from mesa.visualization.ModularVisualization import ModularServer
import mesa
import math
from custom_strategies import CustomStrategies
import numpy as np
from model import AgentModel
from mesa.visualization.modules import CanvasGrid, ChartModule

from trader import TraderAgent


def agent_portrayal(agent: TraderAgent):
    portrayal = {"Filled": "true"}
    # Can only do 2 shapes properly
    portrayal["Shape"] = agent.cs.mechanics["offer"].shapes[agent.custom_strategies["offer"]]
    # portrayal["Shape"] = "circle"
    # Can do infinetely many colors
    portrayal["Color"] = agent.cs.mechanics["witness"].colors[agent.custom_strategies["witness"]]
    # Can do infinitely many texts, though it doesnt show properly (on the plotted shape)
    portrayal["Text"] = agent.cs.mechanics["trust_update"].text[agent.custom_strategies["trust_update"]]
    # portrayal["Text"] = "x"
    # portrayal["Text_color"] = "blue"
    portrayal["Layer"] = 0

    # if portrayal["Shape"] == "arrowHead":
    for dimension in ["w", "h", "r"]:
        portrayal[dimension] = np.clip(agent.proportional_funds, 0.1, 0.99) * 0.3   #scale based on funds compared to others

    return portrayal


if __name__ == '__main__':
    grid = CanvasGrid(agent_portrayal, 10, 10, 500, 500)
    chart = ChartModule([
        {"Label": "total_money", "Color": "black"},
        {"Label": "default", "Color": "green"},
        {"Label": "notrust", "Color": "red"},
        {"Label": "lowtrust", "Color": "blue"}], data_collector_name="datacollector"
    )

# Model visuals
model_params = {
    "N": mesa.visualization.Slider(
        "Number of agents:", 50, 1, 100, description="Initial Number of People"
    ),
    "Default": mesa.visualization.Checkbox("Default agents", True),
    "LowTrust": mesa.visualization.Checkbox("Low trust agents", True),
    "NoTrust": mesa.visualization.Checkbox("Untrustful agents", True),
    "width": 10,
    "height": 10,
    "n_steps": mesa.visualization.Slider(
        "trading rounds per step:", 1, 1, 30, description="trading rounds per step")
}

server = ModularServer(AgentModel,
                       [grid, chart],
                       "Traders Model",
                       model_params)
# {"N": 50, "width": 10, "height": 10}
server.port = 8521  # The default
server.launch()

# Attempt at implementing the distribution calculation here (because you have the model params available here)

# cs = CustomStrategies() # comment this in order to use the older (preset) strategies system
# # cs = {} # comment this to use the newer (customizable) strategies system

# if cs:
#     # Number of agents divided by number of classes - to create even distributions per stratety         
#     ####### TODO CHANGE THIS TO IMPLEMENT CUSTOM STRATEGY-DISTRIBUTIONS

#     # This creates an even distribution of strategies over all the agents
#     strat_distributions = []
#     # A mechanic = offer, witness, trust_update
#     for i, mechanic in enumerate(cs.mechanics):
#         # Strategies can be "standard", "lowball", "dont_trust_witness"
#         strats_of_this_mechanic = cs.mechanics[mechanic].strategies
#         # Calculate the number of agents that will get each strategy (THIS DETERMINES THE EVEN DISTRIBUTION)
#         n_agents_per_mechanic_strategy = model_params["N"].value / len(strats_of_this_mechanic) # 
#         # This creates the distribution: 50 agents, 3 strategies --> [17, 16, 16]
#         strat_distribution = [math.ceil(n_agents_per_mechanic_strategy) if strat == 0 else math.floor(n_agents_per_mechanic_strategy) for strat in range(len(strats_of_this_mechanic))]
#         strat_distributions.append(strat_distribution)


#         ##  Earlier version, calculate how many agents should get a certain strategy
#     # w = model_params["N"].value / len(cs.witness_strategies)
#     # o = model_params["N"].value / len(cs.offer_strategies)
#     # t = model_params["N"].value / len(cs.trust_update_strategies)
#     # strats = [w, o, t]

#     # # Ceil & floor ensure that 1/3 of 50 (16.33) = [17 (ceil), 16 (floor), 16 (floor)]
#     # w_even_distribution = [math.ceil(w) if strat == 0 else math.floor(w) for strat in range(len(cs.witness_strategies))]
#     # o_even_distribution = [math.ceil(o) if strat == 0 else math.floor(o) for strat in range(len(cs.offer_strategies))]
#     # t_even_distribution =  [math.ceil(t) if strat == 0 else math.floor(t) for strat in range(len(cs.trust_update_strategies))]

#     ####### TODO-END

#     # This converts the distributions into a dictionary. The dictionary contains the mechanics (trade offer, update trust, etc) and for each of those, how many agents will get whatever mechanic
#     distributions_per_mechanic = {}
#     for i, mechanic in enumerate(cs.mechanics):
#         distributions_per_mechanic[mechanic] = strat_distributions[i]

#     agent_model =  AgentModel()
#     # agent_model.set_distribution(strategy_distribution=distributions_per_mechanic, custom_strategies=cs)
