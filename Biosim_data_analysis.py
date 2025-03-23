import pandas as pd
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import numpy as np
from scipy.interpolate import griddata

def data_analysis():
    energylevels_df = pd.read_csv("energylevels_database.txt", sep="\t")

    energylevels_df.info()

    abcabc = energylevels_df.groupby(by="numPrey")[["mean_energy"]].mean().reset_index()
    print(abcabc)

    x = abcabc["numPrey"]
    y = abcabc["mean_energy"]

    plt.plot(x, y)
    plt.title("mean energy values after 10 simsteps\n for n predators with increasing prey numbers")
    plt.xlabel("number of prey")
    plt.ylabel("mean energy value [a.u.]")
    plt.show()

def data_analysis3d():
    energylevels_df = pd.read_csv("energylevels_database.txt", sep="\t")

    energylevels_df.info()

    abcabc = energylevels_df.groupby(by=["numPrey", "numPredators"])[["mean_energy"]].mean().reset_index()
    print(abcabc)

    x = abcabc["numPrey"]
    y = abcabc["numPredators"]
    z = abcabc["mean_energy"]

    xi = np.linspace(x.min(), x.max(), 100)  # 100 Punkte entlang der x-Achse
    yi = np.linspace(y.min(), y.max(), 100)  # 100 Punkte entlang der y-Achse
    xi, yi = np.meshgrid(xi, yi)
    zi = griddata((x, y), z, (xi, yi), method="cubic")

    fig = plt.figure()
    ax = fig.add_subplot(111, projection="3d")
    ax.set_xlabel("number of prey")
    ax.set_ylabel("number of predators")
    ax.set_zlabel("mean energy")

    # ax.bar3d(x, y, z, dx, dy, dz, shade=True, cmap = "viridis")
    contour = plt.contourf(xi, yi, zi, levels=200, cmap="viridis")  # 20 Farb-Level
    plt.colorbar(contour, label="Mean Energy")

    #plt.scatter(x, y, z)
    plt.title("mean energy values after 10 simsteps\n for n predators with increasing prey numbers")
    # plt.xlabel("number of prey")
    # plt.ylabel("mean energy value [a.u.]")
    plt.show()

def optimality_graph(maxThickness, simSteps):
    energylevels = pd.read_csv("optimality.txt", sep="\t")
    bins = []
    labels = []

    bins_steps = range(0, maxThickness+1, 4)
    for i in bins_steps:
        bins.append(i)
        if i>0:
            labels.append(str(i))

    energylevels["sorted thickness"] = pd.cut(energylevels["preferred thickness"], bins=bins, labels=labels)
    output = energylevels.groupby("sorted thickness")["Energy"].mean().reset_index()


    plt.plot(output["sorted thickness"], output["Energy"], label="energy values")

    plt.title("mean energy levels by preferred prey thickness")
    plt.xlabel("preferred thickness")
    plt.ylabel(f"energy after {simSteps} sim steps")
    plt.legend()

    plt.show()

#optimality_graph()