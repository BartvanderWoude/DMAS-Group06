from mesa.visualization.ModularVisualization import ModularServer

from model import AgentModel
from mesa.visualization.modules import CanvasGrid, ChartModule


def agent_portrayal(agent):
    portrayal = {"Shape": "circle", "Filled": "true"}
    portrayal["Color"] = agent.strat_color
    portrayal["Layer"] = 0

    portrayal["r"] = max(0.01, min(1, (agent.money / 1000)))
    return portrayal


if __name__ == '__main__':
    grid = CanvasGrid(agent_portrayal, 10, 10, 500, 500)
    chart = ChartModule([
        {"Label": "total_money", "Color": "black"},
        {"Label": "default", "Color": "green"},
        {"Label": "notrust", "Color": "red"},
        {"Label": "lowtrust", "Color": "blue"}], data_collector_name="datacollector"
    )

    server = ModularServer(AgentModel,
                           [grid, chart],
                           "Traders Model",
                           {"N": 50, "width": 10, "height": 10})
    server.port = 8521  # The default
    server.launch()
