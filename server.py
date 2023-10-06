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
    # portrayal["Shape"] = agent.cs.mechanics["offer"].shapes[agent.custom_strategies["offer"]]
    portrayal["Shape"] = "circle"
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
    "neighbourhood": mesa.visualization.Checkbox("Neighbourhood", value=False),
    "movement_type": mesa.visualization.Choice(
        "Movement type",
        value="random_spot",
        choices=list(["random_spot", "random_walk", "move_within_radius"]),
    ),
    "width": 10,
    "height": 10,
    "n_steps": mesa.visualization.Slider(
        "trading rounds per step:", 1, 1, 30, description="trading rounds per step")
}

server = ModularServer(AgentModel,
                       [grid],  #TODO revist chart
                       "Traders Model",
                       model_params)

server.port = 8521  # The default
server.launch()

