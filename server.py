import mesa
from mesa.visualization.ModularVisualization import ModularServer
import numpy as np
from mesa.visualization.modules import CanvasGrid, ChartModule

from model import AgentModel
from trader import TraderAgent


def agent_portrayal(agent: TraderAgent):
    portrayal = {"Filled": "true"}
    portrayal["Shape"] = "circle"
    portrayal["Color"] = agent.cs.mechanics["witness"].colors[agent.custom_strategies["witness"]]
    portrayal["Text"] = agent.cs.mechanics["trust_update"].text[agent.custom_strategies["trust_update"]]
    portrayal["Layer"] = 0

    for dimension in ["w", "h", "r"]:
        portrayal[dimension] = np.clip(agent.proportional_funds, 0.1, 0.99) * 0.3   #scale based on funds compared to others

    return portrayal

def get_modelparams():
    # Interactivity
    return {
        "n_steps": mesa.visualization.Slider(
            "trading rounds per step:", 1, 1, 30, description="trading rounds per step"),
        "A": mesa.visualization.Slider(
            "Number of agents:", 50, 2, 100, description="Initial Number of agents"
        ),
        "neighbourhood": mesa.visualization.Checkbox(
            "Neighbourhood", value=False
        ),
        "movement_type": mesa.visualization.Choice(
            "Movement type",
            value="random_spot",
            choices=list(["random_spot", "random_walk", "move_within_radius"]),
        ),
        "width": 10,
        "height": 10,
    }

def setup_run_server():
    grid = CanvasGrid(agent_portrayal, 10, 10, 500, 500)
    chart = ChartModule([
        {"Label": "total_money", "Color": "black"},
        {"Label": "default", "Color": "green"},
        {"Label": "notrust", "Color": "red"},
        {"Label": "lowtrust", "Color": "blue"}], data_collector_name="datacollector"
    )

    server = ModularServer(AgentModel,
                       [grid],
                       "Traders Model",
                       get_modelparams())

    server.port = 8521  # The default
    server.launch()

if __name__ == '__main__':
    setup_run_server()