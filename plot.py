import matplotlib.pyplot as plt
import pandas as pd
import json
import numpy as np

font = {
    'family': 'Times',
    'color':  'black',
    'weight': 'normal',
    'size': 20,
}

def growth_line_plot():
    file_path = "money_over_time.csv"
    df = pd.read_csv(file_path)

    plt.figure(figsize=(20, 10))  # Adjust the figure size if needed

    for column in df.columns[2:]:
        plt.plot(df.index, df[column], label=column)

    plt.xlabel('Iteration (global step)',fontdict=font)
    plt.ylabel('Average Funds', fontdict=font)
    plt.title('Funds gain due to Strategy/Mechanics', fontdict=font)
    plt.legend(loc='upper left', bbox_to_anchor=(1.02, 1), fontsize=14)
    plt.subplots_adjust(right=0.75)
    plt.savefig("strategies.jpg")

    plt.show()

colors = ["red","green","blue","purple", "orange", "magenta", "lime", "darkred", "darkblue", "yellow"]
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
    plt.savefig("honestyfunds.jpg")
    plt.show()

def proportional_line():
    file_path = "money_over_time.csv"
    df = pd.read_csv(file_path)

    plt.figure(figsize=(20, 10))  # Adjust the figure size if needed

    for column in df.columns[2:]:
        plt.plot(df.index, df[column]/(df["avg_money"]*9)*100, label=column) #*100 percent

    plt.xlabel('Iteration (global step)', fontdict=font)
    plt.ylabel('% of total funds', fontdict=font)
    plt.title('Funds percentage due to Strategy/Mechanics', fontdict=font)
    plt.legend(loc='upper left', bbox_to_anchor=(1.02, 1), fontsize=14)
    plt.subplots_adjust(right=0.75)
    plt.savefig("strategies_proportional.jpg")

    plt.show()


if __name__ == '__main__':
    growth_line_plot()
    plot_scatter()
    proportional_line()