import numpy as np
import math
from PIL import Image, ImageDraw
import gc
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, FancyArrowPatch, Arc
import inspect
import random
import Biosim_sandbox_neurons as n

gif_frames = []
mullerplot_dicts = []
color_dict = {}
genefrqs = []
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

        # attach color to genotype
        col = indiv.color
        rgb_color = tuple(int(col[i:i+2], 16)/255 for i in (0, 2, 4))
        color_dict[tuple(dna)] = rgb_color
    
    # sort genotypes into a dict, track the number of occurrences
    lineages = {}
    for gt in allGenotypes:
        if gt not in lineages.keys():
            lineages[gt] = 1
        elif gt in lineages.keys():
            lineages[gt] += 1

    mullerplot_dicts.append(lineages)
  
def generateMullerPlot(filename="mullerplot.png", directory=None, realColors=False):
    "generate a stackplot that resembles a Muller Plot by grouping identical individuals"
    "and thus show the lineages making up the population."
    # This muller plot cannot track which mutations arise in which lineages
    # Note: The consistency of colors may only be guaranteed when mutationRate = 0

    # extract all unique genomes from mullerplot_dicts
    genome_tracker = {}
    gen_counter = []
    unique_genomes = []
    colores = []
    for i, generation_dict in enumerate(mullerplot_dicts):
        gen_dict_keys = generation_dict.keys()
        for genome in gen_dict_keys:
            if genome not in genome_tracker:
                genome_tracker[genome] = []

                unique_genomes.append(genome)

    # add frequencies for each generation
    for i, generation_dict in enumerate(mullerplot_dicts):
        gen_counter.append(i+1)
        
        # assign current frequency to the corresponding element in genome_tracker
        for genome in generation_dict.keys():
            genome_tracker[genome].append(generation_dict[genome])
        # all genomes that don't occur in that generation get a 0 assigned
        for genome in genome_tracker.keys():
            if genome not in generation_dict.keys():
                genome_tracker[genome].append(0)

    # compile the genome keys and frequencies into a list of tuples which can be sorted
    lineages = [(genome, genome_tracker[genome]) for genome in unique_genomes]
    lineages.sort(key=lambda x: x[0])
    lineagesToPlot = [i[1] for i in lineages]

    # sort the colors into a list with the same sorting as lineages
    if realColors:
        colores = [color_dict[elem[0]] for elem in lineages]
    else:
        colores = None

    fig, ax = plt.subplots()
    #ax.stackplot(gen_counter, genome_tracker.values(), colors=colores) # deactivate colors=colores if mutations make graph unclear
    ax.stackplot(gen_counter, lineagesToPlot, colors=colores) # deactivate colors=colores if mutations make graph unclear

    ax.set_title('Muller Plot')
    ax.set_xlabel('Generation')
    if directory:
        save_dir = directory / "mullerplot.png"
        plt.savefig(save_dir)
        save_dir2 = directory / "mullerplot.pdf"
        plt.savefig(save_dir2)
    else:
        plt.show()


def getGeneFrqs(inhabitants):
    "count the gene frequencies of the current generation"
    # extract the genes of every individual and add them to genefrqs_dict
    # count how many of the inhabitants have that gene and divide that number by the total number of inhabitants
    # append that number to the list attached to the gene=key of genefrqs_dict

    genefrqs_dict = {}
    for indiv in inhabitants:
        dna = [hex(int(neurolink.DNA, 2))[2:] for neurolink in indiv.genome.genes] # this is a list of hexcode strings
        for gene in dna:
            genefrqs_dict[gene] = None

    for gene in genefrqs_dict.keys():
        i = 0
        for individual in inhabitants:
            dna = [hex(int(neurolink.DNA, 2))[2:] for neurolink in individual.genome.genes]
            if any(g == gene for g in dna):
                i +=1
        frq = i / len(inhabitants)
        genefrqs_dict[gene] = frq
    
    # append genefrqs_dict to genefrqs
    genefrqs.append(genefrqs_dict)

def plotGeneFrqs(filename="gene_frequencies.png", directory=None):
    "compile all gene frequencies and plot them over all generations"

    unique_genes = []
    gene_tracker = {}
    gen_counter = []
    # get all unique genes
    for generation in genefrqs:
        keys = generation.keys()
        for gene in keys:
            if gene not in gene_tracker:
                gene_tracker[gene] = []

                unique_genes.append(gene)
    
    # add frequencies for each generation
    for i, generation in enumerate(genefrqs):
        gen_counter.append(i+1)

        # assign current frequency to the corresponding element in genome_tracker
        for gene in generation.keys():
            gene_tracker[gene].append(generation[gene])
        # all genomes that don't occur in that generation get a 0 assigned
        for gene in gene_tracker.keys():
            if gene not in generation.keys():
                gene_tracker[gene].append(0)

    fig, ax = plt.subplots()
    for label, values in gene_tracker.items():
        ax.plot(gen_counter, values, label=label)
    ax.set_title("Gene Frequencies")
    ax.set_xlabel('Generation')
    if directory:
        save_dir = directory / filename
        plt.savefig(save_dir)
    else:
        plt.show()


## mostly chatGPT:
def visualizePixieBrain(pixie, directory=None, filename=None):
    def neuron_level(neuron):
        bases = inspect.getmro(neuron.__class__)
        if n.sensorN in bases:
            return 'sensor'
        elif n.internalN in bases:
            return 'internal'
        elif n.actionN in bases:
            return 'action'
        else:
            return 'unknown'

    neurons = list(pixie.genome.allNeurons)
    for i in neurons:
        if i not in pixie.genome.sourceNeurons and i not in pixie.genome.sinkNeurons:
            neurons.remove(i)          
    
    # Neuronen nach Ebenen sortieren
    layers = {'sensor': [], 'internal': [], 'action': []}
    for neuron in neurons:
        level = neuron_level(neuron)
        if level in layers:
            layers[level].append(neuron)
    for layer in layers.keys():
        layers[layer].sort(key=lambda x: str(x.__class__))

    # Positionen vorbereiten
    positions = {}
    radius = 0.5
    y_spacing = 2
    layer_y = {'sensor': y_spacing * 2, 'internal': y_spacing, 'action': 0}

    plt.figure(figsize=(12, 8))
    ax = plt.gca()

    for layer_name, neuron_list in layers.items():
        y = layer_y[layer_name]
        count = len(neuron_list)
        if count == 0:
            continue
        spacing = 1.5
        x_start = - (count - 1) * spacing / 2
        for i, neuron in enumerate(neuron_list):
            x = x_start + i * spacing
            positions[neuron.__class__] = (x, y)
            circle = Circle((x, y), radius, color='lightblue', ec='black', zorder=2)
            ax.add_patch(circle)
            ax.text(x, y, neuron.__class__.__name__, ha='center', va='center', fontsize=9, zorder=3)

    connection_count = {}

    for gene in pixie.genome.genes:
        src_id = gene.source
        sink_id = gene.sink
        weight = gene.weight
        color = 'green' if weight >= 0 else 'red'
        width = max(0.5, min(abs(weight) * 2, 6))

        if src_id not in positions or sink_id not in positions:
            continue

        x1, y1 = positions[src_id]
        x2, y2 = positions[sink_id]

        if src_id == sink_id:
            # Selbstverbindung als Bogen
            loop_offset = 1 + random.random() / 2
            arc = Arc((x1, y1 + 0.3 * loop_offset), 1.2*loop_offset, 0.8*loop_offset, theta1=300, theta2=240,
                      color=color, linewidth=width, zorder=1)
            ax.add_patch(arc)
            continue

        dx, dy = x2 - x1, y2 - y1
        length = (dx**2 + dy**2)**0.5
        if length < 1e-6:
            continue

        shrink_ratio = radius / length
        x1s = x1 + dx * shrink_ratio
        y1s = y1 + dy * shrink_ratio
        x2s = x2 - dx * shrink_ratio
        y2s = y2 - dy * shrink_ratio

        # Offset für Mehrfachverbindungen
        key = (src_id, sink_id)
        offset_count = connection_count.get(key, 0)
        connection_count[key] = offset_count + 1

        offset_magnitude = 0.1 * offset_count
        perp_dx = -dy / length
        perp_dy = dx / length

        rand_offset = 0.03 # control the amount of "jitter" in the arrows
        x1s += perp_dx * offset_magnitude + random.uniform(-rand_offset, rand_offset)
        y1s += perp_dy * offset_magnitude + random.uniform(-rand_offset, rand_offset)
        x2s += perp_dx * offset_magnitude + random.uniform(-rand_offset, rand_offset)
        y2s += perp_dy * offset_magnitude + random.uniform(-rand_offset, rand_offset)

        arrow = FancyArrowPatch(
            (x1s, y1s), (x2s, y2s),
            arrowstyle='-|>',
            mutation_scale=20,
            linewidth=width,
            color=color,
            zorder=1,
            alpha=0.9
        )
        ax.add_patch(arrow)

    ax.relim()
    ax.autoscale_view()
    ax.axis('off')
    ax.set_aspect('equal')
    plt.title("Pixie Brain Visualization")
    plt.tight_layout()
    if filename:
        file_name = filename 
    else:
        file_name = "sample_brain.png"
    if directory:
        save_dir = directory / file_name
        plt.savefig(save_dir)
    else:
        plt.show()
    plt.close()
