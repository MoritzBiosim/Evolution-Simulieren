import numpy as np
import math
from PIL import Image, ImageDraw
import gc
import matplotlib.pyplot as plt

gif_frames = []
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
                x_point = object.yxPos[1] * cellSize + spacing +15 + facing_x
                y_point = object.yxPos[0] * cellSize + spacing +15 + facing_y

                draw.circle(xy=(x_point, y_point), radius=4, fill=rgb_color)
       
        
    gif_frames.append(image)
    if show_image:
        image.show()

def create_gif(filename="sandbox.gif"):
    gif_frames[0].save(filename, save_all=True, append_images=gif_frames[1:],duration=200, loop=0)
    clear_gif()

def clear_gif():
    "clears the gif_frames list"
    gif_frames.clear()
    gc.collect

def calcSurvivalAndDiversity(selCrit, list_survival=None, list_diversity=None):
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
    plt.show()