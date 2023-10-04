from mesa.visualization.ModularVisualization import ModularServer
import mesa



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

# model_params = {
#     "N": mesa.visualization.Slider(
#         "Number of agents:", 50, 1, 100, description="Initial Number of People"
#     ),
#     "Default": mesa.visualization.Checkbox("Default agents", True),
#     "LowTrust": mesa.visualization.Checkbox("Low trust agents", False),
#     "NoTrust": mesa.visualization.Checkbox("Untrustful agents", False),
#     "width":10,
#     "height":10
# }
server = ModularServer(AgentModel,
                       [grid, chart],
                       "Traders Model",
                       {"N": 50, "width": 10, "height": 10})
# {"N": 50, "width": 10, "height": 10}
server.port = 8521  # The default
server.launch()
