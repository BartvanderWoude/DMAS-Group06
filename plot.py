import matplotlib.pyplot as plt
import pandas as pd
import json
import numpy as np
import pickle
import random
import re
import os

# colors = ["red","green","blue","purple", "orange", "magenta", "lime", "darkred", "darkblue", "yellow"]

def get_font():
    return {
        'family': 'Times',
        'color':  'black',
        'weight': 'normal',
        'size': 20,
    }

def growth_line_plot():
    file_path = "money_over_time.csv"
    df = pd.read_csv(file_path)

    plt.figure(figsize=(16, 10))  # Adjust the figure size if needed

    for column in df.columns[2:]:
        if column != "avg_money":
            name = column.split("_")
            name = f"{refactor_names(name[0], False)} + {refactor_names(name[2], True)}"
        else:
            name = "average funds"

        plt.plot(df.index, df[column], label=name)

    plt.xlabel('Iteration (global step)',fontdict=get_font())
    plt.ylabel('Average Funds', fontdict=get_font())
    plt.title('Funds gain due to Strategy/Mechanics', fontdict=get_font())
    plt.legend(loc='upper left', bbox_to_anchor=(1.02, 1), fontsize=14)
    plt.subplots_adjust(right=0.75)
    plt.savefig("images/strategies.jpg")

    plt.show()

def plot_scatter():
    file_path = "agent.csv"
    df = pd.read_csv(file_path)
    col_names = list(df.columns)
    col_names = [x.split('_', 1) for x in col_names[1:]]
    # unique_strats = list(set(col_names))

    last_row = df.iloc[-1]
    funds = []
    honesty = []
    N = len(last_row[1:])
    for col in last_row[1:]: #skips header
        value_list = json.loads(col)
        funds.append(value_list[0])
        honesty.append(value_list[1])

    slope, intercept = np.polyfit(np.array(honesty), np.array(funds), 1)    #generate line

    # Generate y values for the regression line
    regression_line = slope * np.array(honesty) + intercept
    # Create the scatter plot

    plt.scatter(x=honesty, y=funds)
    plt.plot(honesty, regression_line, color='red', label='Regression Line')

    plt.axline((0,0), slope=0, color="black", linestyle="--")
    plt.xlabel("Honesty Value")
    plt.ylabel("Funds (proportional to mean)")
    plt.title(label=f"Funds as a Function of Honesty: N={N}")
    plt.savefig("images/funds_proportional.jpg")
    plt.show()

def proportional_line():
    file_path = "money_over_time.csv"
    df = pd.read_csv(file_path)

    plt.figure(figsize=(16, 10))  # Adjust the figure size if needed

    for column in df.columns[2:]:

        if column != "avg_money":
            name = column.split("_")
            name = f"{refactor_names(name[0], False)} + {refactor_names(name[2], True)}"
        else:
            name = "average funds"
        plt.plot(df.index, df[column]/(df["avg_money"]*9)*100, label=name) #*100 percent

    plt.xlabel('Iteration (global step)', fontdict=get_font())
    plt.ylabel('% of total funds', fontdict=get_font())
    plt.title('Funds percentage due to Strategy/Mechanics', fontdict=get_font())
    plt.legend(loc='upper left', bbox_to_anchor=(1.02, 1), fontsize=14)
    plt.subplots_adjust(right=0.75)
    plt.savefig("images/strategies_proportional.jpg")

    plt.show()

def plot_real_fake_hoensty():
    a_file = open("data.pkl", "rb")
    data = pickle.load(a_file)

    real_honesty = {}
    trust_in = {}
    for unique_id in range(50):
        total_trust = []
        real_honesty[unique_id] = data[unique_id][unique_id][1]

        for id_2 in range(50):
            if id_2 == unique_id:
                continue
            total_trust.append(data[id_2][unique_id][0])

        trust_in[unique_id] = np.mean(total_trust)

    # slope, intercept = np.polyfit(np.array(list(real_honesty.values())), np.array(list(trust_in.values())), 1)    #generate line
    # regression_line = slope * np.array(list(real_honesty.values())) + intercept
    # plt.plot(real_honesty.values(), regression_line, color='red', label='Regression Line')

    plt.scatter(real_honesty.values(), trust_in.values())

    plt.title("Mean Trust as a Factor of Honesty")
    plt.xlabel("honesty of agent")
    plt.ylabel("mean trust in agent")
    plt.savefig("images/mean_trust_vs_honesty.jpg")

def refactor_names(string, trust_update):

    if not trust_update:
        string = string.replace("standard", "considerate")
    else:
        string = string.replace("standard", "adaptive")
    string = string.replace("naive", "stubborn")
    string = string.replace("critical", "calm")


    return string

def plot_cronyism():
    a_file = open("data.pkl", "rb")
    output = pickle.load(a_file)

    a_file = open("strat.pkl", "rb")
    strat = pickle.load(a_file)

    random_idx = random.randint(0, 49)

    data = output[random_idx]
    # trust in trader, honesty (constant) x-axis
    values = list(data.values())

    own_data = data[random_idx]
    data.pop(random_idx)    #pop self

    trust = [sublist[0] for sublist in values]
    honesty = [sublist[1] for sublist in values]

    plt.scatter(honesty, trust)

    plt.title(f"agent with honesty: {round(own_data[1], 2)}")
    plt.xlabel("honesty values (0-1)")
    plt.ylabel("trust values (0-1)")
    plt.savefig("images/individual_trust.jpg")
    plt.show()

def main_plot():
    if not os.path.exists("images/"):
        print("creating images folder")
        os.makedirs("images")
    plot_cronyism()
    plot_real_fake_hoensty()
    growth_line_plot()
    plot_scatter()
    proportional_line()

if __name__ == '__main__':
    main_plot()