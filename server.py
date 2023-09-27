from mesa.visualization.ModularVisualization import ModularServer
from mesa.visualization.UserParam import NumberInput

from model import AgentModel
from mesa.visualization.modules import CanvasGrid, ChartModule


def agent_portrayal(agent):
    portrayal = {"Shape": "circle", "Filled": "true"}
    portrayal["Color"] = "green"
    portrayal["Layer"] = 0
    
    portrayal["r"] = max(0.01, min(1, (agent.money / 1000)) )


    if agent.trading:
        portrayal["Color"] = "red"
        portrayal["Layer"] = 0

    return portrayal


grid = CanvasGrid(agent_portrayal, 10, 10, 500, 500)
server = ModularServer(AgentModel, 
                       [grid], 
                       "Traders Model", 
                       {"N":50, "width":10, "height":10})
server.port = 8521  # The default
server.launch()