# DMAS-Group02
The effect of cronyism on a multi-agent reputation based trading game.


# How to use the model?

To run the model the server.py file should be used.
This python file will open a web browser with a simple mesa interface.

```
python server.py
```

It contains a step button on the top right to iterate through the simulation.

On the left some parameters can be changed. In the current version you are able to change the number of agents A, the trading rounds per step slider as well as whether agents will only trade with agents
in their neighbourhood (you can also specify type if movement if neighbourhood is set to true).
When changed the reset button on the top right should be used before the model is updated.

# Generate results
When iterating through the simulation 2 files will be created every 20 iterations containing data about the different strategies and agents.
The file plot.py will show the growth over time as well as the honesty vs iteraion plot.
In order to obtain plots of the data, run:
```
python plot.py
```

For questions don't hestitate to contact us.
