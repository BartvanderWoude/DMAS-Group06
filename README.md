# DMAS-Group02
The effect of cronyism on a multi-agent reputation based trading game.
# Project structure
There are a number of files. Giving a short explanation on what these files contain will make understanding the implementation easier.
## server.py
This is a file meant to be run. When running it opens a browser tab with an interactive session through which you can run the model and change settings.
## model.py
This file contains the overarching model logic. The model is linked to the MESA server in server.py. 
Here, the model is created, agents are created with their specific experimental conditions (honesty/strategies).
In addition, this file contains the data colletion methods necessary for saving the data of runs for further data analysis.
## trader.py
This file contains the logic for creating an agent. Aside from its variables it also handles the logic of a trade, i.e. all stages of a trading round
as described in the report. However, the specific equations are implemented in custom_strategies.py.
## movement_techniques.py
Although it is not relevant for the paper (initial settings can be left as is to recreate the data in the report), initially there was the plan to have agents move around and find witnesses/ trading partners in their neighbourhood.
This file implements the logic of moving around the grid. In the interactive session neighbourhood can be set to true in combination with several movement 
techniques. This does work but has been left outside of the scope of the report.
## custom_strategies.py
This file contains the logic for the different implemented strategies as well as some standard implementation, i.e.:
- Find a witness
- Calculate trust
- Calculate offer
- Update trust
## plot.py
Lastly, this file can be run independently after the simulation was run. This script will create several plots that are also included in the report.

# Setup
A file called requirements.txt is included that includes all the relevant python libraries for this implementation. 
We use python 3.12. Earlier versions could not work. The required libraries can be installed using:
...
pip install -r requirements.txt
...

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
