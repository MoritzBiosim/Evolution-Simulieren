import numpy as np
import math
from PIL import Image, ImageDraw
import gc
import matplotlib.pyplot as plt

gif_frames = []
mullerplot_dicts = []
# aufzurufen als render.render(grid0)
def render(world, circleDiameter=30, spacing=0, show_image=False):

    matrixSize = np.size(world.grid, 0)
    cellSize = circleDiameter + spacing
    imgSize = cellSize * matrixSize

    # create a blank canvas
    image = Image.new("RGB", (imgSize, imgSize), color="white")
    draw = ImageDraw.Draw(image)

    # for each object, draw a circle
    allObjects = [world.getInhabitants(), world.getEnvironment()]
    for objectClass in allObjects:
        for object in objectClass:
            #print(object.color)

            #get hexcolors and convert them to RGB
            if object.color:
                hex_color = object.color
                rgb_color = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

            # Berechne die Position des Kreises
            top_left = (object.yxPos[1] * cellSize + spacing // 2, object.yxPos[0] * cellSize + spacing // 2)
            bottom_right = (top_left[0] + circleDiameter, top_left[1] + circleDiameter)

            if object.shape == "round":
                draw.ellipse([top_left, bottom_right], fill=rgb_color)
            elif object.shape == "square":
                draw.rectangle([top_left, bottom_right], fill=rgb_color)
            elif object.shape == "food":
                draw.polygon(((top_left[0] + cellSize/2, top_left[1] + cellSize/10), (bottom_right[0],bottom_right[1]), (bottom_right[0] - cellSize, bottom_right[1])), fill=rgb_color, outline="black")                
                #sticker = Image.open("flower30x30.jpg")
                #image.paste(sticker, (top_left[0], top_left[1]))
            
            # if facing, calculate position of facing-point
            if hasattr(object, "facing"):
                facing_y = math.sin(object.facing) * (circleDiameter/2)
                facing_x = math.cos(object.facing) * (circleDiameter/2)
                x_point = object.yxPos[1] * cellSize + spacing + circleDiameter/2 + facing_x
                y_point = object.yxPos[0] * cellSize + spacing + circleDiameter/2 + facing_y

                draw.circle(xy=(x_point, y_point), radius=circleDiameter/7, fill=rgb_color) 
       
        
    gif_frames.append(image)
    if show_image:
        image.show()

def create_gif(filename="sandbox.gif", directory=None):
    if directory:
        img_dir = directory / filename
    else: 
        img_dir = filename
    gif_frames[0].save(img_dir, save_all=True, append_images=gif_frames[1:],duration=200, loop=0)
    clear_gif()

def clear_gif():
    "clears the gif_frames list"
    gif_frames.clear()
    gc.collect

def calcSurvivalAndDiversity(selCrit, list_survival=None, list_diversity=None, directory=None):
    if list_survival:
        plt.plot(list_survival, label="survival rate")
        # print(list_survival)
    if list_diversity:
        plt.plot(list_diversity, label="diversity")
    
    plt.suptitle("survival rates and diversity in the population over time")
    plt.title(f"selection criterium: {selCrit}")
    plt.xlabel("generation")
    plt.ylim(0,1)
    plt.legend()
    if directory:
        save_dir = directory / "survival_diversity_plot.png"
        plt.savefig(save_dir)
    else:
        plt.show()

def countLineages(inhabitants):
    "sort the unique genotpyes of each generation into a dictionary with genotype as key and occurrence as value"

    allGenotypes = []
    for indiv in inhabitants:
        dna = [hex(int(neurolink.DNA, 2))[2:] for neurolink in indiv.genome.genes] # this is a list of hexcode strings
        
        allGenotypes.append(tuple(dna))
    
    # sort genotypes into a dict, track the number of occurrences
    lineages = {}
    for gt in allGenotypes:
        if gt not in lineages.keys():
            lineages[gt] = 1
        elif gt in lineages.keys():
            lineages[gt] += 1

    mullerplot_dicts.append(lineages)

    
def generateMullerPlot(filename="mullerplot.png", directory=None):
    "generate a stackplot that resembles a Muller Plot by grouping identical individuals"
    "and thus show the lineages making up the population."
    # This muller plot cannot track which mutations arise in which lineages
    # Note: The consistency of colors may only be guaranteed when mutationRate = 0

    # extract all unique genomes from mullerplot_dicts
    genome_tracker = {}
    gen_counter = []
    for dicty in mullerplot_dicts:
        for genome in dicty.keys():
            genome_tracker[genome] = []

    # add frequencies for each generation
    for i, generation_dict in enumerate(mullerplot_dicts):
        gen_counter.append(i)
        
        # assign current frequency to the corresponding element in genome_tracker
        for genome in generation_dict.keys():
            genome_tracker[genome].append(generation_dict[genome])
        # all genomes that don't occur in that generation get a 0 assigned
        for genome in genome_tracker.keys():
            if genome not in generation_dict.keys():
                genome_tracker[genome].append(0)

    fig, ax = plt.subplots()
    ax.stackplot(gen_counter, genome_tracker.values())
    # ax.legend(loc='upper left')
    ax.set_title('Muller Plot')
    ax.set_xlabel('Generation')
    if directory:
        save_dir = directory / "mullerplot.png"
        plt.savefig(save_dir)
    else:
        plt.show()
