import pygame
import math
import random
from pygame.locals import *
import vector

#defines a camera which can move and render walls/objects around the map
class Camera():
    def __init__(self,px,py,dx,dy,pnx,pny):
        self.pos = [px,py]
        self.dir = [dx,dy]
        self.plane = [pnx,pny]

#defines an object that can be seen by the camera
class Entity():
    def __init__(self,px,py,typ):
        self.pos = [px,py]
        self.type = typ

    #basically an override function
    def update(self,dt,playerPos,level):
        pass

    def damage(self,amount):
        pass

#stores world data and performs useful functions such as rendering the world/entities

class World:
    def __init__(self,mapIn,entities):
        self.map = mapIn
        self.images = [pygame.image.load("images/background.bmp"),
                       load_image(pygame.image.load("images/wall/bricks.png").convert(),(0,0,0),255),
                       load_image(pygame.image.load("images/wall/grey_bricks.png").convert(),(0,0,0),255),
                       load_image(pygame.image.load("images/wall/bluestone.png").convert(),(0,0,0),255),
                       load_image(pygame.image.load("images/wall/purplestone.png").convert(),(0,0,0),255),
                       load_image(pygame.image.load("images/wall/mossy.png").convert(),(0,0,0),255),
                       load_image(pygame.image.load("images/wall/wood.png").convert(),(0,0,0),255),
                       load_image(pygame.image.load("images/wall/cobble.png").convert(),(0,0,0),255),
                       load_image(pygame.image.load("images/wall/bricks.png").convert(),(0,0,0),127),
                       load_image(pygame.image.load("images/wall/grey_bricks.png").convert(),(0,0,0),127),
                       load_image(pygame.image.load("images/wall/bluestone.png").convert(),(0,0,0),127),
                       load_image(pygame.image.load("images/wall/purplestone.png").convert(),(0,0,0),127),
                       load_image(pygame.image.load("images/wall/mossy.png").convert(),(0,0,0),127),
                       load_image(pygame.image.load("images/wall/wood.png").convert(),(0,0,0),127),
                       load_image(pygame.image.load("images/wall/cobble.png").convert(),(0,0,0),127),]
        self.objects = [load_image(pygame.image.load("images/object/barrel.png"),(0,0,0),255),
                        load_image(pygame.image.load("images/object/greenlight.png"),(0,0,0),255),
                        load_image(pygame.image.load("images/object/pillar.png"),(0,0,0),255),
                        load_image(pygame.image.load("images/object/shop.png"),(0,0,0),255),                        
                        load_image(pygame.image.load("images/object/enemy11.png"),(0,0,0),255),
                        load_image(pygame.image.load("images/object/enemy21.png"),(0,0,0),255),
                        load_image(pygame.image.load("images/object/enemy31.png"),(0,0,0),255),
                        load_image(pygame.image.load("images/object/kailemface.png"),(0,0,0),255)]

        self.explosives = [load_image(pygame.image.load("images/object/explosion1.png"),(0,0,0),255),
                           load_image(pygame.image.load("images/object/explosion2.png"),(0,0,0),255),
                           load_image(pygame.image.load("images/object/explosion3.png"),(0,0,0),255)]
                           
        self.entities = entities

    def spawn_enemy(self,playerPos,typ):
        #attempts to spawn an enemy away from the player 10 times, returns a position if
        #the algorithm finds a spot and returns False if it fails to find a position

        for i in range(10):
            angle = random.randint(0,360)
            sn = math.sin(angle)
            cs = math.cos(angle)

            direction = [cs * 12,sn * 12]

            direction = vector.add(direction,playerPos)

            #check that the vector is inside the map boundaries to avoid index errors
            if int(direction[1]) > 0 and int(direction[1]) < len(self.map) and int(direction[0]) > 0 and int(direction[0]) < len(self.map[0]):
                if self.map[int(direction[1])][int(direction[0])] == 0:
                    return [int(direction[0]),int(direction[1]),typ]
        return False
        

        
        
    def draw(self,camx,camy,dirx,diry,planex,planey,surface):

        #get the dimensions of the surface to draw on
        w = surface.get_width()
        h = surface.get_height()

        offx,offy = surface.get_abs_offset()
        
        surface.blit(pygame.transform.scale(self.images[0],(w,h)),(0,0))

        #stores the distance to all pixels, is used to see if objects can be drawn
        zbuffer = []
        
        #cast a ray for every horizontal column on the surface
        for x in range(w):
            camspaceX = float(2 * x / float(w) - 1) #find the offset of the ray
           
            rayx = camx
            rayy = camy

            #the rays will move along the edges of two grid squares, they will
            #never be inside a grid square

            #dx and dy mean direction x and y
            raydx = dirx + planex * camspaceX
            raydy = diry + planey * camspaceX

            #grid coordinate of the ray
            gridx = int(rayx)
            gridy = int(rayy)

            #distance from the rays current (float) coordinate to the
            #next interger coordinate on a certain axis
            ddistx = math.sqrt(1 + (raydy * raydy) / (raydx * raydx))

            #since the y direction may be 0, set it to a very small number
            #to avoid a division by zero error
            if raydy == 0:
                raydy = 0.00001

            ddisty = math.sqrt(1 + (raydx * raydx) / (raydy * raydy))

            #which way to step towards on each axis (-1 or 1)
            stepx = 0
            stepy = 0

            #has the fay hit a wall?
            hit = False

            #was the wall that was hit vertical or horizontal? 0 = horizontal, 1 = vertical
            side = 0

            sidedistx = 0.
            sidedisty = 0.

            #caculate the step direction and how far the ray has travelled in each direcition
            if raydx < 0:
                stepx = -1
                sidedistx = (rayx - gridx) * ddistx
            else:
                stepx = 1
                sidedistx = (gridx + 1.0 - rayx) * ddistx
                
            if raydy < 0:
                stepy = -1
                sidedisty = (rayy - gridy) * ddisty
            else:
                stepy = 1
                sidedisty = (gridy + 1.0 - rayy) * ddisty

            #move the ray until it hits a wall
            while hit == False:
                if sidedistx < sidedisty:
                    sidedistx += ddistx
                    gridx += stepx
                    side = 0
                else:
                    sidedisty += ddisty
                    gridy += stepy
                    side = 1

                #check if the current square is not free space
                if self.map[gridx][gridy] > 0:
                    hit = True

            #how far the ray's intersection point is away from the camera
            wallDist = 0.
            if side == 0:
                wallDist = abs((gridx - rayx + (1 - stepx) / 2) / raydx)
            else:
                wallDist = abs((gridy - rayy + (1 - stepy) / 2) / raydy)

            if wallDist == 0:
                wallDist = 0.000001

            #add the distance to the zbuffer array
            zbuffer.append(wallDist)
                
            lineHeight = abs(int(300 / wallDist))

            drawStart = -lineHeight / 2 + (h / 2)
            drawEnd = lineHeight / 2 + (h / 2)

            #background uses the 1st spot (entry 0) in the image array
            texid = self.map[gridx][gridy]

            #use a darker texture for y-axis walls
            if side == 0:
                texid += 7

            #find the exact intersection point
            wallx = 0
            if side == 1:
                wallx = rayx + ((gridy - rayy + (1 - stepy) / 2) / raydy) * raydx
            else:
                wallx = rayy + ((gridx - rayx + (1 - stepx) / 2) / raydx) * raydy
            wallx -= math.floor(wallx)

            #find the coloumn of the texture to render
            texX = int(wallx * 64.0)
            if side == 0 and raydx > 0:
                texX = 64 - texX - 1
            if side == 1 and raydy < 0:
                texX = 64 - texX - 1

            #stop pygame from rendering ridiculously tall textures
            if lineHeight > 10000:
                lineHeight = 10000
                drawStart = -10000 / 2 + 300 / 2

            #grab the coloumn of the texture to render and draw it to the screen
            surface.blit(pygame.transform.scale(self.images[texid][texX], (1, lineHeight)), (x, drawStart))

        #objects need to be rendered in order of from closest to furthest
        #tuples are always sorted by their first items
            
        entity_tuple = []
        for entity in self.entities:
            entity_tuple.append([vector.distance([camx,camy],[entity.pos[1],entity.pos[0]]),entity])
        entity_tuple = reversed(sorted(entity_tuple))

        hitboxes = []
        
        for tup in entity_tuple:
            entity = tup[1]

            #translate the sprite relatve to the camera
            #camx = 64, object x = 66, relative x = 2
            objectX = entity.pos[1] - camx
            objectY = entity.pos[0] - camy

            #inverse camera matrix
            #----------------------------------------------
            inv = 1.0 / (planex * diry - dirx * planey)

            transformX = inv * (diry * objectX - dirx * objectY)
            transformY = inv * (-planey * objectX + planex * objectY)
            #----------------------------------------------

            if transformY == 0:
                transformY = 0.0001

            #x centre of the sprite projected onto the surface
            spriteX = int((w / 2) * (1 + transformX / transformY))

            #using the distance on the y-axis,  caculate the width and height
            width = abs(int(h / (transformY)))
            height = abs(int(h / (transformY)))

            #find the min/max width/height of the sprite being drawn
            drawsx = -width / 2 + spriteX
            drawex = width / 2 + spriteX
            
            drawsy = -height / 2 + h / 2
            drawey = height / 2 + h / 2 

            seeable = False

            #don't render ridiculous tall sprites
            if height < 1000:
                if entity.__class__.__name__ == "Explosion":
                    texture = self.explosives[entity.life]
                else:
                    texture = self.objects[entity.type]
                    
                for stripe in range(drawsx, drawex):
                    #find the exact coloumn of the texture array to draw
                    texX = int(256 * (stripe - (-width / 2 + spriteX)) * 64 / width) / 256
                          
                    #if the stripe is on the screen, and the stripe is not behind a wall
                    #and the stripe isn't behind the camera, draw the stripe to the surface
                    if (transformY > 0 and stripe > 0 and stripe < w and transformY < zbuffer[stripe]):
                        seeable = True
                        surface.blit(pygame.transform.scale(texture[texX], (1,height)), (stripe, drawsy))
                if seeable:
                    hitboxes.append([spriteX - width / 4,spriteX + width / 4,entity])
        #return all the hitboxes of sprites that can be seen
        return hitboxes    
                     
                
def load_image(image,color,alpha):
    #turn a image into a surface to get the columns from it
    ret_array = []

    #if the colour of a pixel is equal to the color key, it becomes invisible
    if color is not None:
        image.set_colorkey(color)
    image.set_alpha(alpha)

    #add grab columns from the image and add them to the surface
    for i in range(image.get_width()):
        surface = pygame.Surface((1, image.get_height())).convert()
        surface.blit(image, (- i, 0))
        if color is not None:
            surface.set_colorkey(color)
        ret_array.append(surface)
    return ret_array
