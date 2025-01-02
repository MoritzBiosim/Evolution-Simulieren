import numpy as np
from PIL import Image, ImageDraw
import gc

gif_frames = []
# aufzurufen als render.render(grid0)
def render(world, circleDiameter=30, spacing=0):

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
       
        
    gif_frames.append(image)
    #image.show()

def create_gif():
    gif_frames[0].save("BS_oop3.gif", save_all=True, append_images=gif_frames[1:],duration=400, loop=0)

def clear_gif():
    "clears the gif_frames list"
    gif_frames.clear()
    gc.collect