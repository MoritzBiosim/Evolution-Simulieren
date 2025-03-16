import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

def data_analysis():
    energylevels_df = pd.read_csv("energylevels_database.txt", sep="\t")

    energylevels_df.info()

    abcabc = energylevels_df.groupby(by="numPrey")[["mean_energy"]].mean().reset_index()
    print(abcabc)

    x = abcabc["numPrey"]
    y = abcabc["mean_energy"]

    plt.plot(x, y)
    plt.title("mean energy values after 7 simsteps\n for one predator with increasing prey numbers")
    plt.xlabel("number of prey")
    plt.ylabel("mean energy value [a.u.]")
    plt.show()